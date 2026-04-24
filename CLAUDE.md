# CLAUDE.md

本工程是基于 JeecgBoot 裁剪的 CRUD 脚手架平台（已移除 AI 应用平台、AI 应用门户、工具箱、OpenAPI AK/SK 四个模块）。后端 `jeecg-boot/`，前端 `jeecgboot-vue3/`（见其自带 CLAUDE.md）。本文件为**后端** Java 代码的约定——贴近现状描述，AI 写代码时需遵循。

## Lombok 约定

本工程全面依赖 Lombok，编译期注解处理器在 `jeecg-boot-parent/pom.xml` 已配置，勿删。

### Entity（MyBatis-Plus 实体）

固定组合，**不要**省略任何一项：

```java
@Data
@TableName("表名")
@EqualsAndHashCode(callSuper = false)
@Accessors(chain = true)
public class Xxx extends JeecgEntity {
    @Schema(description = "字段描述")
    private String fieldName;
}
```

- `@EqualsAndHashCode(callSuper = false)` 是必须的——继承 `JeecgEntity` 后若不加，lombok 生成的 equals/hashCode 会把父类字段也算进去，导致缓存/集合去重行为异常。
- `@Accessors(chain = true)` 让 setter 返回 `this`，允许 `new Xxx().setA(1).setB(2)` 链式赋值——代码库里大量这样用。
- `@Schema` 来自 `io.swagger.v3.oas.annotations.media.Schema`（不是 `@ApiModelProperty`，Swagger3 已换）。

### JeecgEntity 父类已提供的字段

**不要在子类重复声明**：

| 字段 | 类型 | 说明 |
|------|------|------|
| `id` | String | `@TableId(type = IdType.ASSIGN_ID)` 雪花算法 ID |
| `createBy` / `createTime` | String / Date | 创建人与创建时间 |
| `updateBy` / `updateTime` | String / Date | 更新人与更新时间 |

若需"组织编码 / 租户"等字段，看是否需要继承 `JeecgTenantEntity` 或自行添加 `sysOrgCode`。

### DTO / VO / Model

只需 `@Data`。不要无脑加 `@Builder`——**本仓库 0 处使用 `@Builder`**，保持一致。

```java
@Data
public class XxxVO {
    private String id;
    private String name;
}
```

### Service 实现 / Controller / 任何带日志的类

加 `@Slf4j`，用 `log.info(...)`；不要 `LoggerFactory.getLogger()` 手动构造。

```java
@Slf4j
@Service("xxxService")
public class XxxServiceImpl extends ServiceImpl<XxxMapper, Xxx> implements IXxxService { ... }

@Slf4j
@RestController
@RequestMapping("/xxx")
public class XxxController { ... }
```

### 依赖注入

**用 `@Autowired` 字段注入**，不用 `@RequiredArgsConstructor` + `final`。

```java
@Autowired
private IXxxService xxxService;
```

> 本仓库 0 处使用 `@RequiredArgsConstructor`，勿引入新风格，保持一致。

## 命名与分层

- Service 接口：`IXxxService extends IService<Xxx>`（MyBatis-Plus 的 `IService`，不是自己定义的）
- Service 实现：`XxxServiceImpl extends ServiceImpl<XxxMapper, Xxx> implements IXxxService`
- Mapper：`XxxMapper extends BaseMapper<Xxx>`
- Controller：`XxxController`，前缀加 `@RequestMapping("/模块/实体")`
- Entity 包路径：`org.jeecg.modules.<模块>.entity`
- Controller 返回统一用 `org.jeecg.common.api.vo.Result<T>`：
  - `Result.OK(data)` / `Result.OK("xxx成功")` 成功
  - `Result.error("错误消息")` 失败

## 不要使用 / 已知陷阱

- **不用 `@Builder`、`@RequiredArgsConstructor`、`@FieldDefaults`**：本仓库未采用，混用会导致代码风格割裂。
- **不用 `@ApiModel` / `@ApiModelProperty`**：已迁移到 `@Schema`。
- **不用 `@Resource`**：本仓库统一 `@Autowired`。
- **不要手写 `getXxx()` / `setXxx()` / `toString()` / `equals()`**：lombok 已生成；手写会导致 lombok 不再生成对应方法（`@Data` 会跳过已存在的签名）。
- **AI 生成 `XxxDTO.builder().a(1).build()` 会编译失败**——本仓库 DTO 不带 `@Builder`。用构造 + 链式 setter：`new XxxDTO().setA(1).setB(2)`（有 `@Accessors(chain = true)` 时）或普通 setter。
- **删除字段前先 grep `.getXxx(` / `.setXxx(`**：lombok 方法在源文件里看不到，但调用方是实际引用。

## 构建提示

- JDK 17+（工程声明 `17`，兼容 21/24）
- 运行本地编译：`mvn -pl jeecg-module-system/jeecg-system-biz -am compile -DskipTests`
- 如需在某个 bean 上看 lombok 展开后的真实方法签名，临时挂 `lombok-maven-plugin` 跑一次 `mvn lombok:delombok`，产物在 `target/delombok/`（不入 git）。

## 裁剪留痕（重要）

以下名称出现在搜索结果里时要警惕——它们**已从本工程删除**，可能是历史引用或需要继续清理的残留：

- `jeecg-boot-module-airag`、`AiragFlowDTO`、`IAiragFlowService`、`AiRagConfigBean`、`IAiragBaseApi`
- `org.jeecg.modules.airag.*`、`org.jeecg.modules.openapi.*`
- `@jeecg/aiflow`（前端）、`dashboard/ai`、`super/airag`、`views/openapi`
- `runAiragFlow`、`aiIconShow`、`AI_ICON_SHOW`

如果需要恢复其中某个能力，优先从 JeecgBoot 官方源码同步，而不是自行重建。
