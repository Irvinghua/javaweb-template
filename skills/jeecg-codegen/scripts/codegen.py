#!/usr/bin/env python3
"""jeecg-codegen — 用对齐版 code-template 渲染 JeecgBoot CRUD 代码（Java FreeMarker 驱动）。

读 ctx.json → normalize → FtlRunner 渲染 → 按文件类型分发到本工程目录。
模板来自 jeecg/code-template（已对齐新 UI），本脚本不修改模板内容。
"""
import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path

SKILL_DIR = Path(__file__).resolve().parent.parent
LIB_DIR = SKILL_DIR / 'lib'
TEMPLATES_DIR = SKILL_DIR / 'templates'
SCRIPTS_DIR = SKILL_DIR / 'scripts'
CACHE_DIR = SCRIPTS_DIR / '.cache'
JAR_NAMES = ['freemarker-2.3.32.jar', 'fastjson2.jar']

# 用户友好风格名 → code-template 目录名
STYLE_MAP = {
    'single':        'one',
    'onetomany':     'onetomany',
    'onetomany-tab': 'onetomany2',
}
VALID_STYLES = set(STYLE_MAP)

# 后端自动维护字段：前端表单/子表默认不显示（与 jeecg 一致）
SYSTEM_FIELD_NAMES = {'createBy', 'createTime', 'updateBy', 'updateTime', 'sysOrgCode'}

# code-template 实际用到的列字段为 fieldName/fieldType/filedComment/fieldDbType/classType；
# 其余为兜底，保证模板里偶发引用不抛 InvalidReferenceException。
COLUMN_DEFAULTS = {
    'fieldDbName': '',
    'filedComment': '',          # jeecg 模板拼写为 'filed'
    'fieldDbType': 'string',
    'fieldType': 'java.lang.String',
    'classType': 'text',
    'nullable': 'Y',
    'isShowList': 'Y',
    'isShow': 'Y',
    'isQuery': 'N',
    'dictField': '',
    'dictText': '',
    'dictTable': '',
}


def _camel_to_snake(s):
    return re.sub(r'([a-z0-9])([A-Z])', r'\1_\2', s).lower()


def _snake_to_camel(s):
    if '_' not in s:
        return s
    parts = s.split('_')
    return parts[0] + ''.join(p[:1].upper() + p[1:] for p in parts[1:])


def _enrich_column(col, primary_key=None):
    out = dict(col)
    fn = out.get('fieldName', '')
    out.setdefault('fieldDbName', _camel_to_snake(fn))
    if 'isShow' not in col and (fn in SYSTEM_FIELD_NAMES or (primary_key and fn == primary_key)):
        out['isShow'] = 'N'
    for k, v in COLUMN_DEFAULTS.items():
        out.setdefault(k, v)
    if not out.get('filedComment'):
        out['filedComment'] = fn
    return out


def _frontend_field_type(col):
    """前端 data.ts 用短类型（date/datetime/int/decimal/double）选控件；
    后端 entity 用 Java 类型（java.lang.X）。二者读同一 fieldType 但语义不同，
    故前端 columns 需把 Java 类型映射成短类型，否则数字/日期会退化成普通 Input。"""
    jt = str(col.get('fieldType', ''))
    dbt = str(col.get('fieldDbType', ''))
    if jt == 'java.util.Date':
        return 'datetime' if dbt.lower() == 'datetime' else 'date'
    if jt in ('java.lang.Integer', 'java.lang.Long', 'java.lang.Short') or dbt == 'int':
        return 'int'
    if jt == 'java.math.BigDecimal' or dbt in ('BigDecimal', 'decimal'):
        return 'decimal'
    if jt in ('java.lang.Double', 'java.lang.Float') or dbt in ('double', 'float'):
        return 'double'
    return 'string'


def _to_frontend_col(col):
    fc = dict(col)
    fc['fieldType'] = _frontend_field_type(col)
    return fc


def _enrich_tablevo(tv, ctx):
    out = dict(tv) if tv else {}
    out.setdefault('entityName', ctx.get('entityName', ''))
    out.setdefault('tableName', ctx.get('tableName', ''))
    out.setdefault('ftlDescription', ctx.get('description', ctx.get('tableName', '')))
    out.setdefault('searchFieldNum', 6)   # 高级查询折叠前显示字段数，jeecg 默认 6
    return out


def normalize_ctx(ctx):
    """补齐 code-template 模板需要、AI 不一定显式传入的派生字段。"""
    if 'entityPackage' in ctx and 'entityPackagePath' not in ctx:
        ctx['entityPackagePath'] = str(ctx['entityPackage']).replace('.', '/')
    if 'currentDate' not in ctx:
        ctx['currentDate'] = time.strftime('%Y%m%d')

    pk = ctx.get('primaryKeyField') or 'id'
    cols = ctx.get('originalColumns') or []
    if not any(c.get('fieldName') == pk for c in cols):
        cols = [{'fieldName': pk, 'filedComment': '主键', 'fieldDbName': pk,
                 'fieldDbType': 'string', 'fieldType': 'java.lang.String', 'classType': 'text',
                 'nullable': 'Y', 'isShowList': 'N', 'isShow': 'N', 'isQuery': 'N'}] + cols
    cols = [_enrich_column(c, pk) for c in cols]
    ctx['originalColumns'] = cols

    if 'columns' not in ctx:
        ctx['columns'] = [_to_frontend_col(c) for c in cols if c.get('fieldName') != pk]
    else:
        fe = [_enrich_column(c, pk) for c in ctx['columns']]
        ctx['columns'] = [_to_frontend_col(c) for c in fe if c.get('fieldName') != pk]

    ctx['tableVo'] = _enrich_tablevo(ctx.get('tableVo') or {}, ctx)
    ctx.setdefault('primaryKeyField', pk)

    subs = ctx.get('subTables') or []
    for sub in subs:
        sub_pk = sub.get('primaryKeyField') or 'id'
        sub_cols = sub.get('originalColumns') or []
        if not any(c.get('fieldName') == sub_pk for c in sub_cols):
            sub_cols = [{'fieldName': sub_pk, 'filedComment': '主键', 'fieldDbName': sub_pk,
                         'fieldDbType': 'string', 'fieldType': 'java.lang.String', 'classType': 'text',
                         'nullable': 'Y', 'isShowList': 'N', 'isShow': 'N', 'isQuery': 'N'}] + sub_cols
        sub_cols = [_enrich_column(c, sub_pk) for c in sub_cols]
        sub['originalColumns'] = sub_cols
        sub['colums'] = sub_cols       # jeecg 模板拼写别名（少一个 n）
        sub['columns'] = sub_cols
        sub.setdefault('originalForeignKeys', [])
        sub['foreignKeys'] = [_snake_to_camel(k) for k in (sub.get('foreignKeys') or [])]
        sub.setdefault('foreignRelationType', '0')
        sub.setdefault('ftlDescription', sub.get('tableName', ''))
        sub.setdefault('primaryKeyField', 'id')
    ctx['subTables'] = subs
    return ctx


def build_classpath():
    sep = ';' if os.name == 'nt' else ':'
    paths = [str(LIB_DIR / n) for n in JAR_NAMES]
    paths.append(str(CACHE_DIR))
    return sep.join(paths)


def _javac_release_flags():
    try:
        out = subprocess.run(['javac', '-version'], capture_output=True, text=True, check=True)
        ver = (out.stdout + out.stderr).strip()
    except Exception:
        return ['-source', '8', '-target', '8']
    m = re.search(r'javac\s+(\d+)(?:\.(\d+))?', ver)
    if not m:
        return ['-source', '8', '-target', '8']
    return ['-source', '8', '-target', '8'] if int(m.group(1)) == 1 else ['--release', '8']


def ensure_compiled():
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    src = SCRIPTS_DIR / 'FtlRunner.java'
    cls = CACHE_DIR / 'FtlRunner.class'
    if cls.exists() and cls.stat().st_mtime >= src.stat().st_mtime:
        return
    sep = ';' if os.name == 'nt' else ':'
    jar_cp = sep.join(str(LIB_DIR / n) for n in JAR_NAMES)
    cmd = ['javac', '-encoding', 'UTF-8', *_javac_release_flags(), '-cp', jar_cp, '-d', str(CACHE_DIR), str(src)]
    print('[codegen] compiling FtlRunner …', ' '.join(cmd))
    subprocess.run(cmd, check=True)


def run_freemarker(style_dir, ctx_path, work_dir):
    cmd = ['java', '-cp', build_classpath(), 'FtlRunner', str(TEMPLATES_DIR), style_dir, str(ctx_path), str(work_dir)]
    print('[codegen] running FtlRunner …')
    return subprocess.run(cmd, check=False).returncode


def collect_outputs(work_dir):
    return [p for p in work_dir.rglob('*') if p.is_file()]


def categorize(rel):
    """backend / frontend(vue3) / sql。"""
    if rel.name.endswith('.sql'):
        return 'sql'
    if 'vue3' in rel.parts:
        return 'frontend'
    return 'backend'


def strip_template_prefix(rel):
    parts = list(rel.parts)
    if parts and parts[0] == 'java':
        parts = parts[1:]
    return Path(*parts)


def split_at_segment(rel, segment):
    parts = list(rel.parts)
    if segment in parts:
        idx = parts.index(segment)
        return Path(*parts[:idx]), Path(*parts[idx + 1:]) if parts[idx + 1:] else Path()
    return rel, Path()


def normalize_dst_name(p):
    if p.suffix == '.sql':
        return p
    return p.with_name(p.name.replace('__', '.')) if '__' in p.name else p


def entity_module_dir(ctx):
    name = str(ctx.get('entityName', ''))
    return name[:1].lower() + name[1:] if name else ''


def dispatch(work_dir, args, ctx):
    results = []
    sql_seen = set()
    entity_path = str(ctx.get('entityPackage', '')).replace('.', '/')
    module_dir = entity_module_dir(ctx)

    for src in collect_outputs(work_dir):
        rel = strip_template_prefix(src.relative_to(work_dir))
        cat = categorize(rel)
        if cat == 'sql':
            if not args.flyway_dir or src.name in sql_seen:
                continue
            sql_seen.add(src.name)
            dst = Path(args.flyway_dir) / src.name
        elif cat == 'frontend':
            if not args.frontend_root:
                continue
            _, after = split_at_segment(rel, 'vue3')
            dst = Path(args.frontend_root) / 'src/views' / entity_path / module_dir / after
        else:  # backend
            if not args.backend_root:
                continue
            dst = Path(args.backend_root) / 'src/main/java' / rel
        results.append((src, normalize_dst_name(dst)))
    return results


def write_files(plan, dry_run, sql_rewrite=None):
    for src, dst in plan:
        print(f"[codegen] {'WOULD WRITE' if dry_run else 'WROTE'} {dst}")
        if dry_run:
            continue
        dst.parent.mkdir(parents=True, exist_ok=True)
        if dst.suffix == '.sql' and sql_rewrite:
            old, new = sql_rewrite
            dst.write_text(src.read_text(encoding='utf-8').replace(old, new), encoding='utf-8')
        else:
            shutil.copyfile(src, dst)


def parse_args():
    p = argparse.ArgumentParser(description='JeecgBoot codegen via Freemarker (code-template aligned).')
    p.add_argument('--style', required=True, choices=sorted(VALID_STYLES))
    p.add_argument('--ctx', required=True)
    p.add_argument('--backend-root')
    p.add_argument('--frontend-root')
    p.add_argument('--flyway-dir')
    p.add_argument('--out', help='[调试] 仅渲染到目录不分发')
    p.add_argument('--dry-run', action='store_true')
    return p.parse_args()


def main():
    args = parse_args()
    ctx_path = Path(args.ctx).resolve()
    if not ctx_path.is_file():
        sys.exit(f'ctx file not found: {ctx_path}')
    with ctx_path.open(encoding='utf-8') as f:
        ctx = normalize_ctx(json.load(f))
    norm_path = ctx_path.with_suffix('.normalized.json')
    with norm_path.open('w', encoding='utf-8') as f:
        json.dump(ctx, f, ensure_ascii=False, indent=2)

    ensure_compiled()
    style_dir = STYLE_MAP[args.style]

    if args.out:
        work_dir = Path(args.out).resolve()
        work_dir.mkdir(parents=True, exist_ok=True)
        rc = run_freemarker(style_dir, norm_path, work_dir)
        sys.exit(rc) if rc else print(f'[codegen] rendered to {work_dir}, skip dispatch (--out)')
        return

    with tempfile.TemporaryDirectory(prefix='jeecg-codegen-') as tmp:
        work_dir = Path(tmp)
        rc = run_freemarker(style_dir, norm_path, work_dir)
        if rc != 0:
            sys.exit(rc)
        plan = dispatch(work_dir, args, ctx)
        entity_path = str(ctx.get('entityPackage', '')).replace('.', '/')
        module_dir = entity_module_dir(ctx)
        entity_name = ctx.get('entityName', '')
        sql_rewrite = (f"'{entity_path}/{entity_name}", f"'{entity_path}/{module_dir}/{entity_name}") \
            if module_dir and entity_path and entity_name else None
        write_files(plan, args.dry_run, sql_rewrite)
        print(f'[codegen] {len(plan)} files dispatched.')


if __name__ == '__main__':
    main()
