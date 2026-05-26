-- =====================================================
-- 清理 AI 应用平台 / AI 应用门户 / OpenAPI / JimuReport 模块遗留的种子数据
-- 适用于从 JeecgBoot 3.9.2 升级的已有数据库
-- 上一步 V3.9.2_0 已删除 Online 模块本身的代码与表，这里负责
-- 清掉那些只剩"数据残留"的 seed 行：AI 字典、AI 角色、AI/JimuReport 公告等
-- =====================================================

-- 1. 删除 AI 模块相关的字典定义
-- ai_app_type / know_doc_type / model_type / model_provider 都是 AI 应用平台引用的字典，
-- 模块已删除后这些字典只会在"数据字典"页里挂着，对 fork 项目没意义。
DELETE FROM sys_dict_item WHERE dict_id IN (
    SELECT id FROM sys_dict WHERE dict_code IN (
        'ai_app_type', 'know_doc_type', 'model_type', 'model_provider'
    )
);
DELETE FROM sys_dict WHERE dict_code IN (
    'ai_app_type', 'know_doc_type', 'model_type', 'model_provider'
);

-- 2. 删除 "AI 应用角色"（role_code = 'aiadmin'）
DELETE FROM sys_role_permission WHERE role_id IN (
    SELECT id FROM sys_role WHERE role_code = 'aiadmin'
);
DELETE FROM sys_user_role WHERE role_id IN (
    SELECT id FROM sys_role WHERE role_code = 'aiadmin'
);
DELETE FROM sys_role WHERE role_code = 'aiadmin';

-- 3. 清理 AI / 工具箱 / OpenAPI 相关菜单权限（如果上游 SQL 漏掉了）
-- 这些 url / component 路径在前端代码中都已删除，残留菜单会跳 404。
DELETE FROM sys_role_permission WHERE permission_id IN (
    SELECT id FROM sys_permission WHERE
        url LIKE '/super/airag%'
        OR url LIKE '/dashboard/ai%'
        OR url LIKE '/super/aiapp%'
        OR url LIKE '/views/openapi%'
        OR url LIKE '/openapi%'
        OR component LIKE 'super/airag%'
        OR component LIKE 'dashboard/ai%'
        OR component LIKE 'views/openapi%'
);
DELETE FROM sys_permission WHERE
    url LIKE '/super/airag%'
    OR url LIKE '/dashboard/ai%'
    OR url LIKE '/super/aiapp%'
    OR url LIKE '/views/openapi%'
    OR url LIKE '/openapi%'
    OR component LIKE 'super/airag%'
    OR component LIKE 'dashboard/ai%'
    OR component LIKE 'views/openapi%';

-- 4. 删除 JimuReport / 积木报表 / Online 升级 相关的通告
-- 这些都是官方 demo 数据，fork 后没必要继续展示。
DELETE FROM sys_announcement_send WHERE annt_id IN (
    SELECT id FROM sys_announcement WHERE
        titile LIKE '%JimuReport%'
        OR titile LIKE '%积木报表%'
        OR titile LIKE '%Online%'
);
DELETE FROM sys_announcement WHERE
    titile LIKE '%JimuReport%'
    OR titile LIKE '%积木报表%'
    OR titile LIKE '%Online%';

-- 5. 清理白名单中残留的 AI / JimuReport 表
DELETE FROM sys_table_white_list WHERE
    table_name LIKE 'ai_%'
    OR table_name LIKE 'airag_%'
    OR table_name LIKE 'jimu_%';
