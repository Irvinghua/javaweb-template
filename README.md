JeecgBoot AI低代码平台
===============

当前最新版本： 3.9.1（发布日期：2026-01-28） 


[![AUR](https://img.shields.io/badge/license-Apache%20License%202.0-blue.svg)](https://github.com/jeecgboot/JeecgBoot/blob/master/LICENSE)
[![GitHub stars](https://img.shields.io/github/stars/zhangdaiscott/jeecg-boot.svg?style=social&label=Stars)](https://github.com/jeecgboot/JeecgBoot)
[![GitHub forks](https://img.shields.io/github/forks/zhangdaiscott/jeecg-boot.svg?style=social&label=Fork)](https://github.com/jeecgboot/JeecgBoot)



项目介绍
-----------------------------------

<h3 align="center">企业级AI低代码平台</h3>

JeecgBoot 是一款 AI 驱动的低代码开发平台，以"低代码 + 零代码"双模式覆盖从快速搭建到深度定制的全场景需求。零代码模式下，一句话即可搭建完整业务系统；
代码生成模式下，AI 自动输出前后端代码、建表 SQL 与菜单权限，生成即可运行。
平台支持一句话设计表单、聊天式业务操作等智能能力。
整体遵循"AI 生成 → 在线配置 → 代码生成 → 手工合并"的开发流程，解决 Java 项目中 80% 的重复工作，在大幅提升效率的同时保留充分的灵活性与可控性。

---

采用最新的前后端分离技术栈（Ant Design&Vue3，SpringBoot3，SpringCloud Alibaba，Mybatis-plus，具备强大且颗粒化的权限控制，支持按钮权限和数据权限设置，满足大型业务系统需求。功能涵盖在线表单、表单设计、流程设计、门户设计、报表与大屏设计、OA办公，支持ChatGPT、DeepSeek、Ollama等多种AI大模型。


- `零代码能力:` 国内首个“低代码+零代码”双模驱动的AI智能开发平台！同时支持低代码和零代码; 让开发者用低代码，让业务人员在同一个平台上用零代码！

- `AI驱动开发:` 全新推出AI驱动开发能力，支持一句话生成完整系统，提供零代码模式（一句话搭建系统，无需编写代码）和代码生成模式（基于 jeecg-codegen，自动生成完整代码和建表SQL）两种选择。同时支持一句话自动绘制流程图、设计表单，省去手工绘制繁琐步骤。[实战视频](https://www.bilibili.com/video/BV1KKwTzJEbX/) | [Skills技能清单](https://help.jeecg.com/java/ai/skills/skill-comparison/)


- `JEECG宗旨是:` JEECG旨在通过OnlineCoding平台实现简单功能的零代码快速搭建，同时针对复杂功能采用代码生成器生成代码并手工合并，打造智能且灵活的低代码开发模式，有效解决了当前低代码产品普遍缺乏灵活性的问题，提升开发效率的同时兼顾系统的扩展性和定制化能力。

- `JEECG业务流程:` JEECG业务流程采用BPM工作流引擎实现业务审批，扩展任务接口供开发人员编写业务逻辑，表单提供表单设计器、在线配置表单和编码表单等多种解决方案。通过流程与表单的分离设计（松耦合）及任务节点的灵活配置，既保障了企业流程的安全性与保密性，又大幅降低了开发人员的工作量。





AI 重磅能力
-----------------------------------

JeecgBoot 全新推出 AI 驱动开发能力，**支持一句话生成完整系统**，极大简化开发流程。

**两种模式，灵活选择：**

| 模式 | 说明 |
|------|------|
| 零代码模式 | 一句话即可搭建系统，无需编写任何代码 |
| 代码生成模式 | 基于 jeecg-codegen，自动生成完整代码和建表 SQL |

**更多 AI 能力：**
- 支持一句话自动绘制流程图，省去手工绘制繁琐步骤
- 支持一句话自动设计表单，快速完成表单搭建

**Skills下载：** [jeecgboot/skills](https://github.com/jeecgboot/skills)

**视频教程：** [JeecgBoot+Skills自然语言编程](https://www.bilibili.com/video/BV1KKwTzJEbX/)

**官方文档：** [Skills技能清单](https://help.jeecg.com/java/ai/skills/skill-comparison/)


AI Skills 技能清单
-----------------------------------

结合 Claude Code 的 AI Skills 技能，JeecgBoot 实现了**自然语言驱动的低代码开发**，一句话即可完成从需求到代码/配置的全流程自动化。[详细文档](https://help.jeecg.com/java/ai/skills/skill-comparison/) | [Skills 下载](https://github.com/jeecgboot/skills)

| Skill | 技能 | 功能介绍 | 是否需要写代码 |
|-------|------|----------|---------------|
| `jeecg-codegen` | AI一句话生成全套代码 | 自然语言需求自动转换为 JeecgBoot 全套 CRUD 代码，包括后端 Java 代码 + 前端 Vue3 代码 + 建表 SQL + 菜单权限 SQL，支持无表生成，甚至生成一套系统全代码 | 否（AI 自动生成源码） |
| `jeecg-onlform` | AI一句话创建 Online 表单 | 自然语言需求自动转换为 JeecgBoot Online 表单，完成从表单配置 → 同步数据库 → 生成菜单 SQL 的全流程自动化 | 否 |
| `jeecg-onlreport` | AI一句话创建 Online 报表 | 将自然语言需求自动转换为 JeecgBoot Online 报表，完成从 SQL 编写 → 字段解析 → 报表配置 → 创建报表的全流程自动化 | 否 |
| `jeecg-desform` | AI一句话画表单 | 自然语言的表单需求描述自动转换为 JeecgBoot 的设计器表单，完成从需求解析 → JSON 生成 → API 创建的全流程自动化，甚至可以创建一套系统 | 否 |
| `jeecg-bpmn` | AI一句话画流程 | 将自然语言的审批流程描述自动转换为 Flowable BPMN 2.0 XML，并通过 API 在 JeecgBoot 系统中自动创建流程 | 否 |


适用项目
-----------------------------------
JeecgBoot低代码平台兼容所有J2EE项目开发，支持信创国产化，特别适用于SAAS、企业信息管理系统（MIS）、内部办公系统（OA）、企业资源计划系统（ERP）、客户关系管理系统（CRM）及AI知识库等场景。其半智能手工Merge开发模式，可显著提升70%以上的开发效率，极大降低开发成本。同时，JeecgBoot还是一款全栈式AI开发平台，助力企业快速构建和部署个性化AI应用。。


**信创兼容说明**
- 操作系统：国产麒麟、银河麒麟等国产系统几乎都是基于 Linux 内核，因此它们具有良好的兼容性。
- 数据库：达梦、人大金仓、TiDB
- 中间件：东方通 TongWeb、TongRDS，宝兰德 AppServer、CacheDB, [信创配置文档](https://help.jeecg.com/java/tongweb-deploy/)


版本说明
-----------------------------------

|下载 | SpringBoot3.5 + Shiro                                   |SpringBoot3.5+ SpringAuthorizationServer | SpringBoot3.5 + Sa-Token | SpringBoot2.7(JDK17/JDK8) |
|------|---------------------------------------------------------|----------------------------|-------------------|--------------------------------------------|
| Github | [`main`](https://github.com/jeecgboot/JeecgBoot)        | [`springboot3_sas`](https://github.com/jeecgboot/JeecgBoot/tree/springboot3_sas) 分支  |  [`springboot3-satoken`](https://github.com/jeecgboot/JeecgBoot/tree/springboot3-satoken) 分支|[`springboot2`](https://github.com/jeecgboot/JeecgBoot/tree/springboot2) 分支|
| Gitee | [`main`](https://github.com/jeecgboot/JeecgBoot) | [`springboot3_sas`](https://gitee.com/jeecg/JeecgBoot/tree/springboot3_sas) 分支|  [`springboot3-satoken`](https://gitee.com/jeecg/JeecgBoot/tree/springboot3-satoken) 分支|[`springboot2`](https://github.com/jeecgboot/JeecgBoot/tree/springboot2)     分支 |


- `jeecg-boot` 是后端JAVA源码项目Springboot3+Shiro+Mybatis.
- `jeecgboot-vue3` 是前端VUE3源码项目（vue3+vite6+ts最新技术栈）.
- `JeecgUniapp`  是[配套APP框架](https://github.com/jeecgboot/JeecgUniapp) 适配多个终端，支持APP、小程序、H5、鸿蒙、鸿蒙Next.
- `jeecg-boot-starter`  是[jeecg-boot对应的底层封装starter](https://github.com/jeecgboot/jeecg-boot-starter) ：xxljob、分布式锁starter、rabbitmq、分布式事务、分库分表shardingsphere等.
- 参考 [文档](https://help.jeecg.com/ui/2dev/mini) 可以删除不需要的demo，制作一个精简版本



启动项目
-----------------------------------

> 默认账号密码： admin/123456

- [开发环境搭建](https://help.jeecg.com/java/setup/tools)
- [IDEA启动前后端(单体模式)](https://help.jeecg.com/java/setup/idea/startup)
- [Docker一键启动(单体模式)](https://help.jeecg.com/java/docker/quick)


技术文档
-----------------------------------

- 在线演示：  [平台演示](https://boot3.jeecg.com) | [APP演示](https://jeecg.com/appIndex)
- 官方网站：  [http://www.jeecg.com](http://www.jeecg.com)
- 入门指南：  [快速入门](http://www.jeecg.com/doc/quickstart)  | [开发文档](https://help.jeecg.com)  | [AI应用手册](https://help.jeecg.com/aigc) | [视频教程](http://jeecg.com/doc/video)


为什么选择JeecgBoot?
-----------------------------------
> 界内首款AI低代码开发平台，同时具备AI应用平台和低代码平台，通过AI驱动低代码开发！
> 开源界"小普元"超越传统商业平台。引领低代码开发模式(OnlineCoding-> 代码生成器 -> 手工MERGE)，低代码开发同时又支持灵活编码， 可以帮助解决Java项目70%的重复工作，让开发更多关注业务。既能快速提高开发效率，节省成本，同时又不失灵活性。

- 1.采用最新主流前后分离框架（Spring Boot3 + MyBatisPlus + Vue3.0 + TypeScript + Vite6 + Ant Design Vue4 ）等新技术方案。便于学习容易上手，代码生成器依赖性低，灵活的扩展能力，可快速实现二次开发。
- 2.开发效率高，支持在线建表和AI建表，提供强大代码生成器，单表、树列表、一对多、一对一等数据模型，增删改查功能一键生成，菜单配置直接使用。
- 3.代码生成器提供强大模板机制，支持自定义模板，目前提供四套风格模板（单表两套、树模型一套、一对多三套）。
- 4.低代码能力：在线表单（无需编码，通过在线配置表单，实现表单的增删改查，支持单表、树、一对多、一对一等模型，实现人人皆可编码），在线配置零代码开发、所见即所得支持23种类控件。
- 5.封装完善的用户、角色、菜单、组织机构、数据字典、在线定时任务等基础功能，支持访问授权、按钮权限、数据权限等功能。
- 6.前端UI提供丰富的组件库，支持各种常用组件，如表格、树形控件、下拉框、日期选择器等，满足各种复杂的业务需求 [UI组件库文档](https://help.jeecg.com/category/ui%E7%BB%84%E4%BB%B6%E5%BA%93)。
- 7.提供APP配套框架，一份多代码多终端适配，一份代码多终端适配，小程序、H5、安卓、iOS、鸿蒙Next。
- 8.新版APP框架采用Uniapp、Vue3.0、Vite、Wot-design-uni、TypeScript等最新技术栈，包括二次封装组件、路由拦截、请求拦截等功能。实现了与JeecgBoot完美对接：目前已经实现登录、用户信息、通讯录、公告、移动首页、九宫格、聊天、Online表单、仪表盘等功能，提供了丰富的组件。
- 9.提供新行编辑表格JVXETable，轻松满足各种复杂ERP布局，拥有更高的性能、更灵活的扩展、更强大的功能。
- 10.平台首页风格，提供多种组合模式，支持自定义风格；支持门户设计，支持自定义首页。
- 11.常用共通封装，各种工具类（定时任务、短信接口、邮件发送、Excel导入导出等），基本满足80%项目需求。
- 12.简易Excel导入导出，支持单表导出和一对多表模式导出，生成的代码自带导入导出功能。
- 13.采用前后分离技术，页面UI风格精美，针对常用组件做了封装：时间、行表格控件、截取显示控件、报表组件、编辑器等。
- 14.查询过滤器：查询功能自动生成，后台动态拼SQL追加查询条件；支持多种匹配方式（全匹配/模糊查询/包含查询/不匹配查询）。
- 15.数据权限（精细化数据权限控制，控制到行级、列表级、表单字段级，实现不同人看不同数据，不同人对同一个页面操作不同字段）。
- 16.接口安全机制，可细化控制接口授权，非常简便实现不同客户端只看自己数据等控制；
- 17.权限控制采用RBAC（Role-Based Access Control，基于角色的访问控制）。
- 18.页面校验自动生成（必须输入、数字校验、金额校验、时间空间等）。
- 19.支持SaaS服务模式，提供SaaS多租户架构方案。
- 20.分布式文件服务，集成MinIO、阿里OSS等优秀的第三方，提供便捷的文件上传与管理，同时也支持本地存储。
- 21.主流数据库兼容，一套代码完全兼容MySQL、PostgreSQL、Oracle、SQL Server、MariaDB、达梦、人大金仓等主流数据库。
- 22.集成工作流Flowable，并实现了只需在页面配置流程转向，可极大简化BPM工作流的开发；用BPM的流程设计器画出了流程走向，一个工作流基本就完成了，只需写很少量的Java代码。
- 23.低代码能力：在线流程设计，采用开源Flowable流程引擎，实现在线画流程、自定义表单、表单挂靠、业务流转。
- 24.多数据源：极其简易的使用方式，在线配置数据源配置，便捷地从其他数据抓取数据。
- 25.提供单点登录CAS集成方案，项目中已经提供完善的对接代码。
- 26.低代码能力：表单设计器，支持用户自定义表单布局，支持单表、一对多表单，支持select、radio、checkbox、textarea、date、popup、列表、宏等控件。
- 27.专业接口对接机制，统一采用RESTful接口方式，集成Swagger-UI在线接口文档，JWT token安全验证，方便客户端对接。
- 28.高级组合查询功能，在线配置支持主子表关联查询，可保存查询历史。
- 29.提供各种系统监控，实时跟踪系统运行情况（监控Redis、Tomcat、JVM、服务器信息、请求追踪、SQL监控）。
- 30.消息中心（支持短信、邮件、微信推送等）；集成WebSocket消息通知机制。
- 31.支持多语言，提供国际化方案。
- 32.数据变更记录日志，可记录数据每次变更内容，通过版本对比功能查看历史变化。
- 33.提供简单易用的打印插件，支持谷歌、火狐、IE11+等各种浏览器。
- 34.后端采用Maven分模块开发方式；前端支持菜单动态路由。
- 35.提供丰富的示例代码，涵盖了常用的业务场景，便于学习和参考。



技术架构
-----------------------------------

#### 前端

- 前端环境要求：Node.js要求`Node 20+` 版本以上、pnpm 要求`9+` 版本以上

 ` ( Vite 不再支持已结束生命周期（EOL）的 Node.js 18。现在需要使用 Node.js 20.19+ 或 22.12+)`

- 依赖管理：node、npm、pnpm
- 前端IDE建议：IDEA、WebStorm、Vscode
- 采用 Vue3.0+TypeScript+Vite6+Ant-Design-Vue4等新技术方案，包括二次封装组件、utils、hooks、动态菜单、权限校验、按钮级别权限控制等功能
- 最新技术栈：Vue3.0 + TypeScript + Vite6 + ant-design-vue4 + pinia + echarts + unocss + vxe-table + qiankun + es6


#### 后端

- IDE建议： IDEA (必须安装lombok插件 )
- 语言：Java 默认jdk17(jdk21、jdk24)
- 依赖管理：Maven
- 持久层框架：MybatisPlus 3.5.12
- 安全框架：Apache Shiro 2.0.4，Jwt 4.5.0
- 数据库连接池：阿里巴巴Druid 1.2.24
- 日志打印：logback
- 缓存：Redis
- 其他：autopoi, fastjson，poi，Swagger-ui，quartz, lombok（简化代码）等。
- 默认提供MySQL5.7+数据库脚本

#### 数据库支持

> jeecgboot平台支持以下数据库，默认我们只提供mysql脚本，其他数据库可以参考[转库文档](https://my.oschina.net/jeecg/blog/4905722)自己转。

|  数据库   |  支持   |
| --- | --- |
|   MySQL   |  √   |
|  Oracle11g   |  √   |
|  Sqlserver2017   |  √   |
|   PostgreSQL   |  √   |
|   MariaDB   |  √   |
|   达梦   |  √   |
|   人大金仓   |  √   |
|   TiDB     |  √   |
|   kingbase8   |  √   |



### 功能清单
```
├─系统管理
│  ├─用户管理
│  ├─角色管理
│  ├─菜单管理
│  ├─首页配置
│  ├─权限设置（支持按钮权限、数据权限）
│  ├─表单权限（控制字段禁用、隐藏）
│  ├─部门管理
│  ├─我的部门（二级管理员）
│  └─字典管理
│  └─分类字典
│  └─系统公告
│  └─职务管理
│  └─通讯录
│  ├─多数据源管理
│  ├─白名单管理
│  ├─第三方配置（对接钉钉和企业微信）
│  └─多租户管理（租户管理、租户角色、我的租户、租户默认套餐管理）
├─Online在线开发(低代码)
│  ├─Online在线表单
│  ├─Online代码生成器
│  ├─Online在线报表
│  ├─仪表盘设计器
│  ├─系统编码规则
│  ├─系统校验规则
│  ├─APP版本管理
├─数据可视化
│  ├─报表设计器(支持打印设计）
│  ├─大屏设和仪表盘设计
├─消息中心
│  ├─消息管理
│  ├─模板管理
├─代码生成器(低代码)
│  ├─代码生成器功能（一键生成前后端代码，生成后无需修改直接用，绝对是后端开发福音）
│  ├─代码生成器模板（提供4套模板，分别支持单表和一对多模型，不同风格选择）
│  ├─代码生成器模板（生成代码，自带excel导入导出）
│  ├─查询过滤器（查询逻辑无需编码，系统根据页面配置自动生成）
│  ├─高级查询器（弹窗自动组合查询条件）
│  ├─Excel导入导出工具集成（支持单表，一对多 导入导出）
│  ├─平台移动自适应支持
│  ├─提供新版uniapp3的代码生成器模板
├─系统监控
│  ├─Gateway路由网关
│  ├─定时任务
│  ├─数据源管理
│  ├─性能扫描监控
│  │  ├─监控 Redis
│  │  ├─Tomcat
│  │  ├─jvm
│  │  ├─服务器信息
│  │  ├─请求追踪
│  │  ├─磁盘监控
│  ├─系统日志
│  ├─消息中心（支持短信、邮件、微信推送等等）
│  ├─数据日志（记录数据快照，可对比快照，查看数据变更情况）
│  ├─SQL监控
│  ├─在线用户
│─报表示例
│  ├─曲线图
│  └─饼状图
│  └─柱状图
│  └─折线图
│  └─面积图
│  └─雷达图
│  └─仪表图
│  └─进度条
│  └─排名列表
│  └─等等
│─大屏模板
│  ├─作战指挥中心大屏
│  └─物流服务中心大屏
│─常用示例
│  ├─自定义组件
│  ├─对象存储(对接阿里云)
│  ├─JVXETable示例（各种复杂ERP布局示例）
│  ├─单表模型例子
│  └─一对多模型例子
│  └─打印例子
│  └─一对多TAB例子
│  └─内嵌table例子
│  └─常用选择组件
│  └─异步树table
│  └─接口模拟测试
│  └─表格合计示例
│  └─异步树列表示例
│  └─一对多JEditable
│  └─JEditable组件示例
│  └─图片拖拽排序
│  └─图片翻页
│  └─图片预览
│  └─PDF预览
│  └─分屏功能
│─封装通用组件	
│  ├─行编辑表格JEditableTable
│  └─省略显示组件
│  └─时间控件
│  └─高级查询
│  └─用户选择组件
│  └─报表组件封装
│  └─字典组件
│  └─下拉多选组件
│  └─选人组件
│  └─选部门组件
│  └─通过部门选人组件
│  └─封装曲线、柱状图、饼状图、折线图等等报表的组件（经过封装，使用简单）
│  └─在线code编辑器
│  └─上传文件组件
│  └─验证码组件
│  └─树列表组件
│  └─表单禁用组件
│  └─等等
│─更多页面模板
│  ├─各种高级表单
│  ├─各种列表效果
│  └─结果页面
│  └─异常页面
│  └─个人页面
├─高级功能
│  ├─提供单点登录CAS集成方案
│  ├─提供APP发布方案
│  ├─集成Websocket消息通知机制
│  ├─支持electron桌面应用打包(支持windows、linux、macOS三大平台)
│  ├─docker容器支持
│  ├─提供移动APP框架及源码（Uniapp3版本）支持H5、小程序、APP、鸿蒙Next
│  ├─提供移动APP低代码设计(Online表单、仪表盘)
```



### 系统效果
##### 在线接口文档
![输入图片说明](https://static.oschina.net/uploads/img/201908/27095258_M2Xq.png "在这里输入图片标题")
![输入图片说明](https://static.oschina.net/uploads/img/201904/14160957_hN3X.png "在这里输入图片标题")


### Jeecg Boot 产品功能蓝图
![功能蓝图](https://jeecgos.oss-cn-beijing.aliyuncs.com/upload/test/Jeecg-Boot-lantu202005_1590912449914.jpg "在这里输入图片标题")

####  系统功能架构图
![](https://oscimg.oschina.net/oscnet/up-1569487b95a07dbc3599fb1349a2e3aaae1.png)

## 免责声明

JeecgBoot 基于 [Apache License 2.0](./LICENSE) 开源协议发布。凡下载、复制、安装或以任何方式使用本软件的行为，即视为已阅读、理解并同意上述免责声明。

