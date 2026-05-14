# polymarket-data-raw 数据源更新说明

本文档说明当前仓库各数据源（按根节点拆分）的更新方式，以及各类数据内容的获取方式。

## 1. 根节点总表（`nav/root.json`）

文件：`nav/root.json`

用途：
- 维护一级根节点列表（如 `Crypto`、`Sports`、`Politics`、`Finance` 等）。
- 定义每个根节点的基础元数据：`id`、`label`、`slug`、`forceShow`。
- 部分根节点带 `childrenTagsApi`，用于在线拉取子标签。
- `eventPath` 定义事件聚合接口。

更新方式：
1. 手动编辑本地 JSON（新增/删除/调整根节点字段）。
2. 对于支持在线子标签的根节点，仅维护 `childrenTagsApi` 地址，不在本仓库存子节点明细。
3. 保存后做 JSON 格式校验（避免语法错误）。

建议校验命令：
```bash
jq . nav/root.json >/dev/null
```

---

## 2. Crypto 根节点（`slug=crypto`）

相关文件：
- `nav/crypto.json`
- `nav/nav_root.json` 中 `Crypto.children`

用途：
- 维护 Crypto 下的子标签（如 `5m`、`15m`、`1h`、`daily`、`etf` 等）。

更新方式：
1. 以业务最新分类为准，更新 `nav/crypto.json` 的 `children` 数组。
2. 若 `nav/nav_root.json` 作为完整导航快照使用，需要同步更新其中 `Crypto.children`。
3. 保持字段一致：`id`、`label`、`slug`、`p_slug`、`forceShow`。

一致性检查建议：
- `nav/crypto.json` 与 `nav/nav_root.json` 中 `Crypto.children` 内容应同步。
- `p_slug` 应与上层分类语义一致（当前为 `crypto`）。

---

## 3. Sports 根节点（`slug=sports`）

相关文件：
- `nav/sports.json`
- `nav/nav_root.json` 中 `Sports.children`

用途：
- 维护 Sports 下的子标签树（如 `NBA`、`UCL`、`Football`、`Soccer` 子树等）。

更新方式：
1. 更新 `nav/sports.json` 的 `children` 结构（可含多级 `children`）。
2. 若 `nav/nav_root.json` 用作完整导航快照，需要同步更新 `Sports.children`。
3. 关注附加字段：`icon`、`p_slug`、`forceShow`。

一致性检查建议：
- `nav/sports.json` 与 `nav/nav_root.json` 中 `Sports.children` 保持同步。
- 多级节点中 `p_slug` 与上级关系保持一致。

---

## 4. 动态子标签根节点（在线 API 拉取）

在 `nav/root.json` 中，以下根节点通过 `childrenTagsApi` 获取子标签：
- `politics`
- `finance`
- `geopolitics`
- `tech`
- `pop-culture`
- `world`
- `economy`

示例（`politics`）：
- `https://gamma-api.polymarket.com/tags/slug/politics/related-tags/tags`

更新方式：
1. 本地仅维护 `childrenTagsApi` 地址与根节点元数据。
2. 子标签内容以线上接口返回为准，不在本仓库落地静态子节点文件。
3. 当线上接口路径变化时，优先更新 `childrenTagsApi`。

接口可用性检查建议：
```bash
curl -s "https://gamma-api.polymarket.com/tags/slug/politics/related-tags/tags" | jq . >/dev/null
```

---

## 5. 事件数据入口（`eventPath`）

定义位置：`nav/root.json`
- `eventPath`: `https://gamma-api.polymarket.com/events/keyset`

用途：
- 作为事件数据的统一入口地址。

更新方式：
1. 一般无需频繁调整。
2. 如上游 API 路径变更，仅更新 `eventPath` 字段。

接口可用性检查建议：
```bash
curl -s "https://gamma-api.polymarket.com/events/keyset" | jq . >/dev/null
```

---

## 6. 数据内容获取方式（新增）

本节描述“导航配置之外”，如何通过 API 获取实际数据内容。

### 6.1 `tag_slug` 与 `tag_id` 等价筛选

以 `soccer` 为例：

1. 先查标签详情，拿到 `id`：
```bash
curl -s "https://gamma-api.polymarket.com/tags/slug/soccer" | jq .
```
返回示例：
- `slug`: `soccer`
- `id`: `100350`

2. 用 `events/keyset` 查询事件时，`tag_slug=soccer` 与 `tag_id=100350` 返回等价：
```bash
curl -s "https://gamma-api.polymarket.com/events/keyset?active=true&closed=false&limit=2&tag_slug=soccer" | jq .
curl -s "https://gamma-api.polymarket.com/events/keyset?active=true&closed=false&limit=2&tag_id=100350" | jq .
```

说明：
- 工程上优先用 `tag_slug`（可读性更好）。
- 若需要精确对齐标签主键，可用 `tag_id`。

### 6.2 运动联赛来源：`/sports` + 标签映射

联赛总表接口：
```bash
curl -s "https://gamma-api.polymarket.com/sports" | jq .
```

推荐做法：
1. 从 `/sports` 拿到所有运动/联赛候选。
2. 用 `tags/slug/{sport}`（如 `soccer`）拿到总标签 `id`。
3. 以该标签为根，筛选或组织对应运动类型（如 `soccer` 下的 `epl`、`ucl`）。
4. 对具体联赛使用 `events/keyset?...&tag_slug=<league_slug>` 拉事件。

联赛事件示例（EPL）：
```bash
curl -s "https://gamma-api.polymarket.com/events/keyset?limit=10&active=true&archived=false&closed=false&order=volume24hr&ascending=false&tag_slug=epl" | jq .
```

### 6.3 导航配置到查询参数的字段映射

建议统一使用以下映射（与你提供的配置 JSON 一致）：

- 根级公共参数：
  - `apiPath` -> `https://gamma-api.polymarket.com/events/keyset`
  - `events_query` -> 默认查询参数（如 `limit`、`closed`、`order`、`ascending`）
- 分类节点参数：
  - `tag_id` -> 标签主键
  - `events_query.tag_slug` -> 该分类实际请求使用的标签
  - `title` -> 导航展示名
  - `image` -> 展示图（可选）
  - `categories` -> 子分类（递归）

请求拼装逻辑：
1. 先读取根级默认 `events_query`。
2. 下钻到目标分类节点。
3. 用节点 `events_query` 覆盖或补充根级默认参数。
4. 发起 `apiPath + querystring` 请求。

### 6.4 Sports 示例结构说明

根据你给的配置样例，Sports 建议组织为：
- 顶层：`tag_slug=sports`
- 二级：`Soccer(tag_slug=soccer)`
- 三级：`EPL(tag_slug=epl)`、`UCL(tag_slug=ucl)` 等

这样可实现：
- 先拉总体育分类
- 再按运动类型聚合
- 最后按具体联赛拉取事件

---

## 7. 推荐更新流程（按根节点分开执行）

1. 先更新 `nav/root.json` 的根节点元数据（如新增根节点或变更 API 地址）。
2. 再分别更新静态子节点文件：`nav/crypto.json`、`nav/sports.json`。
3. 若项目使用 `nav/nav_root.json` 作为整合快照，同步回填对应 `children`。
4. 同步检查“数据内容获取方式”里用到的接口是否可用（`/tags/slug/*`、`/sports`、`/events/keyset`）。
5. 逐个文件执行 JSON 校验：
```bash
jq . nav/root.json >/dev/null
jq . nav/crypto.json >/dev/null
jq . nav/sports.json >/dev/null
jq . nav/nav_root.json >/dev/null
```
