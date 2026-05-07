-- =====================================================
-- 移除 Online表单开发、Online报表开发、数据可视化 模块
-- 适用于从 JeecgBoot 3.9.1 升级的已有数据库
-- =====================================================

-- 删除 Online/可视化 菜单权限
DELETE FROM sys_permission WHERE url LIKE '/online%' OR url LIKE '/bigscreen%' OR url LIKE '/drag%' OR component LIKE 'online/%' OR component LIKE 'bigscreen/%' OR component LIKE 'drag/%';
DELETE FROM sys_permission WHERE perms LIKE 'online:%' OR perms LIKE 'drag:%' OR perms LIKE 'onl:%';

-- 清理角色-权限关联
DELETE FROM sys_role_permission WHERE permission_id IN (
    SELECT id FROM sys_permission WHERE id IN (
        SELECT id FROM sys_permission WHERE url LIKE '/online%' OR url LIKE '/bigscreen%' OR url LIKE '/drag%'
    )
);

-- 删除低代码开发者角色
DELETE FROM sys_role WHERE role_code = 'lowdeveloper';
DELETE FROM sys_user_role WHERE role_id IN (SELECT id FROM sys_role WHERE role_code = 'lowdeveloper');

-- 删除 Online 表
DROP TABLE IF EXISTS onl_drag_share;
DROP TABLE IF EXISTS onl_drag_table_relation;
DROP TABLE IF EXISTS onl_drag_page_comp;
DROP TABLE IF EXISTS onl_drag_page;
DROP TABLE IF EXISTS onl_drag_dataset_param;
DROP TABLE IF EXISTS onl_drag_dataset_item;
DROP TABLE IF EXISTS onl_drag_dataset_head;
DROP TABLE IF EXISTS onl_drag_comp;
DROP TABLE IF EXISTS onl_cgreport_param;
DROP TABLE IF EXISTS onl_cgreport_item;
DROP TABLE IF EXISTS onl_cgreport_head;
DROP TABLE IF EXISTS onl_cgform_index;
DROP TABLE IF EXISTS onl_cgform_head;
DROP TABLE IF EXISTS onl_cgform_field;
DROP TABLE IF EXISTS onl_cgform_enhance_sql;
DROP TABLE IF EXISTS onl_cgform_enhance_js;
DROP TABLE IF EXISTS onl_cgform_enhance_java;
DROP TABLE IF EXISTS onl_cgform_button;
DROP TABLE IF EXISTS onl_auth_relation;
DROP TABLE IF EXISTS onl_auth_page;
DROP TABLE IF EXISTS onl_auth_data;

-- 清理白名单中的 Online 表
DELETE FROM sys_table_white_list WHERE table_name LIKE 'onl_%';

-- 清理字典中的 Online 表类型
DELETE FROM sys_dict WHERE dict_code = 'cgform_table_type';

-- 清理网关路由中的 Online/大屏路径
UPDATE sys_gateway_route SET uri = REGEXP_REPLACE(uri, ',*/online/\\*\\*', '') WHERE route_id = 'jeecg-system';
UPDATE sys_gateway_route SET uri = REGEXP_REPLACE(uri, ',*/bigscreen/\\*\\*', '') WHERE route_id = 'jeecg-system';
UPDATE sys_gateway_route SET uri = REGEXP_REPLACE(uri, ',*/drag/\\*\\*', '') WHERE route_id = 'jeecg-system';