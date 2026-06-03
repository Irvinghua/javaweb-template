import sys, os
from pathlib import Path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
import codegen as cg


def test_style_map_keys():
    assert cg.STYLE_MAP == {'single': 'one', 'onetomany': 'onetomany', 'onetomany-tab': 'onetomany2'}


def test_normalize_injects_pk_and_currentdate():
    ctx = {'entityName': 'BizGoods', 'tableName': 'biz_goods', 'entityPackage': 'biz',
           'bussiPackage': 'org.jeecg.modules',
           'originalColumns': [{'fieldName': 'name', 'filedComment': '名称'}]}
    out = cg.normalize_ctx(ctx)
    assert out['currentDate']  # YYYYMMDD 注入
    assert out['entityPackagePath'] == 'biz'
    assert any(c['fieldName'] == 'id' for c in out['originalColumns'])  # 主键自动注入
    name_col = [c for c in out['originalColumns'] if c['fieldName'] == 'name'][0]
    assert name_col['fieldDbName'] == 'name'         # camel->snake 兜底
    assert name_col['classType'] == 'text'           # 默认 classType


def test_normalize_sets_searchfieldnum():
    ctx = {'entityName': 'A', 'tableName': 'a', 'entityPackage': 'b', 'bussiPackage': 'org.jeecg.modules',
           'originalColumns': []}
    out = cg.normalize_ctx(ctx)
    assert out['tableVo']['searchFieldNum'] == 6
    assert out['tableVo']['ftlDescription'] == 'a'    # 缺 description 用 tableName 兜底


def test_normalize_subtable_foreignkeys_camel():
    ctx = {'entityName': 'A', 'tableName': 'a', 'entityPackage': 'b', 'bussiPackage': 'org.jeecg.modules',
           'originalColumns': [],
           'subTables': [{'entityName': 'AItem', 'tableName': 'a_item',
                          'foreignKeys': ['order_id'], 'originalColumns': [{'fieldName': 'qty'}]}]}
    out = cg.normalize_ctx(ctx)
    sub = out['subTables'][0]
    assert sub['foreignKeys'] == ['orderId']          # snake->camel
    assert sub['colums'] == sub['originalColumns']     # jeecg 拼写别名补齐
    assert any(c['fieldName'] == 'id' for c in sub['originalColumns'])


def test_frontend_columns_use_short_fieldtype():
    ctx = {'entityName': 'A', 'tableName': 'a', 'entityPackage': 'b', 'bussiPackage': 'org.jeecg.modules',
           'originalColumns': [
               {'fieldName': 'price', 'fieldType': 'java.math.BigDecimal', 'fieldDbType': 'BigDecimal'},
               {'fieldName': 'qty', 'fieldType': 'java.lang.Integer', 'fieldDbType': 'int'},
               {'fieldName': 'createTime', 'fieldType': 'java.util.Date', 'fieldDbType': 'datetime'},
           ]}
    out = cg.normalize_ctx(ctx)
    fe = {c['fieldName']: c['fieldType'] for c in out['columns']}
    assert fe['price'] == 'decimal'        # 前端短类型 → InputNumber
    assert fe['qty'] == 'int'
    assert fe['createTime'] == 'datetime'
    be = {c['fieldName']: c['fieldType'] for c in out['originalColumns']}
    assert be['price'] == 'java.math.BigDecimal'   # 后端仍 Java 类型
    assert be['qty'] == 'java.lang.Integer'


def test_categorize_paths():
    assert cg.categorize(Path('org/jeecg/modules/biz/vue3/BizGoodsList.vue')) == 'frontend'
    assert cg.categorize(Path('org/jeecg/modules/biz/entity/BizGoods.java')) == 'backend'
    assert cg.categorize(Path('V20260603_1__menu_insert_BizGoods.sql')) == 'sql'


def test_strip_and_segment_helpers():
    assert cg.strip_template_prefix(Path('java/org/jeecg/x/entity/A.java')) == Path('org/jeecg/x/entity/A.java')
    before, after = cg.split_at_segment(Path('org/jeecg/biz/vue3/BizList.vue'), 'vue3')
    assert after == Path('BizList.vue')


def test_normalize_dst_name_dunder_to_dot():
    assert cg.normalize_dst_name(Path('BizGoods__data.ts')).name == 'BizGoods.data.ts'
    # .sql 的 __ 是 Flyway 规范，保留
    assert cg.normalize_dst_name(Path('V20260603_1__menu_insert_Biz.sql')).name == 'V20260603_1__menu_insert_Biz.sql'


if __name__ == '__main__':
    import traceback
    fns = [v for k, v in sorted(globals().items()) if k.startswith('test_') and callable(v)]
    failed = 0
    for fn in fns:
        try:
            fn(); print(f'PASS {fn.__name__}')
        except Exception:
            failed += 1; print(f'FAIL {fn.__name__}'); traceback.print_exc()
    print(f'\n{len(fns)-failed}/{len(fns)} passed')
    sys.exit(1 if failed else 0)
