package org.jeecg.common.online.api;

import com.alibaba.fastjson.JSONObject;

import java.util.List;
import java.util.Map;

/**
 * Online 基础 API 缺失接口补全
 * 由于工程裁剪移除了 Online 模块，但 hibernate-re 依赖仍引用了此接口，故补全空接口以保证启动。
 */
public interface IOnlineBaseExtApi {

    /**
     * 根据表名查询列信息
     */
    List<Map<String, Object>> getColumnsByTableName(String tableName);

    /**
     * 根据表名和数据 ID 查询数据
     */
    JSONObject queryOnlineDataById(String tableName, String dataId);

    /**
     * 保存 Online 表单数据
     */
    void saveOnlineData(String tableName, JSONObject data);
}
