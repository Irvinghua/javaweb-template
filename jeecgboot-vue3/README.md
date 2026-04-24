# vibeCRUD 前端模板（基于 JeecgBoot Vue3 裁剪）

本工程是 ToB 后台管理系统的前端脚手架模板，为**每个新项目 fork 一次独立开发**而设计（fork-and-forget）。
后端在同仓库的 `jeecg-boot/` 目录。

## 工程定位

- 70% 业务是 CRUD 后台管理，复用 JeecgBoot 的系统管理、权限、字典等内核
- 30% 业务为 dashboard / 报表 / 定制业务页，按每个项目的设计稿 AI 改造
- 每个项目 fork 后独立演化，**不回流 template**

## 技术栈

Vue 3 + Vite 6 + TypeScript + Ant Design Vue 4 + Pinia + Vue Router 4。
包管理 pnpm，Node ^18 || >=20。

## 启动

```bash
pnpm install
pnpm dev          # 端口 3100；代理 /jeecgboot → localhost:8080/jeecg-boot
```

详细环境变量见 `.env.development`。

## Fork 后的改造流程

fork 本模板后 + 拿到新项目设计稿，按以下步骤：

1. **改项目身份**
   - `package.json` 的 `name` / `version` / `author` / `repository`
   - `.env` 的 `VITE_GLOB_APP_TITLE` / `VITE_GLOB_APP_SHORT_NAME`
   - `public/favicon.ico`、`src/assets/images/logo.png`
2. **改主题 token**：修改 `src/theme/tokens.ts`（ROI 最高，让 70% 的 CRUD 页自动吃上新风格）
3. **改应用外壳**：按设计稿重写 `src/layouts/default/**`
4. **改登录 / 主页**：`src/views/login/**`、`src/views/dashboard/**`
5. **如项目不需要深色模式**：删除设置抽屉里的 dark 切换组件（位于 `src/layouts/default/setting/**`）
6. **开发业务页**：新模块建议放 `src/views/<moduleName>/**`

完整流程与给 AI 的 prompt 模板见 **[`docs/ai-redesign-workflow.md`](./docs/ai-redesign-workflow.md)**。

## 禁区（不主动改）

除非有明确理由，fork 后**不要**改以下目录：

- `src/views/system/**` — JeecgBoot 系统管理页
- `src/components/**` — 基础组件库
- `src/store/**` / `src/router/**` / `src/utils/**` / `src/api/**` / `src/hooks/**` / `src/logics/**` / `src/settings/**`
- `build/**` / `vite.config.ts`

改这些会把本模板的内核改坏，也让未来想借鉴其他 fork 的修复变困难。

## 目录结构（节选）

```
src/
├── theme/tokens.ts         # [可改区] design token 单一真源
├── layouts/default/        # [可改区] 应用外壳
├── views/
│   ├── login/              # [可改区] 登录页
│   ├── dashboard/          # [可改区] 主页 / 概览
│   ├── system/             # [禁区] JeecgBoot 系统管理页
│   └── <your-module>/      # [可改区] 业务页
├── components/             # [禁区] 基础组件库
├── store/                  # [禁区] 状态管理
├── router/                 # [禁区] 路由配置
├── api/                    # [禁区] HTTP 客户端与业务 API
└── assets/                 # [可改区] 静态资源
```

## 常用命令

```bash
pnpm dev              # 开发服务器
pnpm build            # 生产构建
pnpm clean:cache      # 清 vite 缓存
pnpm reinstall        # 重装依赖
pnpm batch:prettier   # 批量格式化 src
```

## Lint / 类型检查

- `npx eslint src/path/to/file.vue`
- `npx stylelint "src/**/*.{vue,less,css}"`
- `npx vue-tsc --noEmit`（未配全量 CI，手动跑）

## 更多

- 后端参见 `jeecg-boot/` 及其 `CLAUDE.md`
- 前端编码约定参见 `CLAUDE.md`（与本文互补：本文档面向人类与 AI 代理，CLAUDE.md 记录编码细节）

---

底层基于 [JeecgBoot](https://github.com/jeecgboot/JeecgBoot) 3.9.1 裁剪。
