# roots.json 获取方式说明

说明：仓库内当前对应文件为 `nav/root.json`（文件名不是 `roots.json`）。

## 1. 文件职责

`nav/root.json` 负责维护一级根分类与公共查询入口：
- `rootTag`: 一级分类（如 `crypto`、`sports`、`politics`）
- `eventPath`: 事件查询接口（当前是 `https://gamma-api.polymarket.com/events/keyset`）

## 2. 数据获取方式

### 2.1 一级分类（rootTag）

来源：本地静态维护。

更新方式：
1. 按业务需要手动维护 `id/label/slug/forceShow`。
2. 对动态分类补 `childrenTagsApi`（如 `politics`、`finance`）。

### 2.2 动态子分类（childrenTagsApi）

来源：`gamma-api` 在线接口。

示例：
```bash
curl -s "https://gamma-api.polymarket.com/tags/slug/politics/related-tags/tags" | jq .
```

说明：
- `root.json` 里只保存 API 地址。
- 子分类内容以接口返回为准。

### 2.3 事件数据入口（eventPath）

来源：`root.json` 的 `eventPath` 字段。

示例：
```bash
curl -s "https://gamma-api.polymarket.com/events/keyset?limit=10&active=true&closed=false" | jq .
```

## 3. 查询参数规则

推荐默认参数：
- `active=true`
- `closed=false`
- `archived=false`
- `order=volume24hr`
- `ascending=false`
- `limit=10` 或 `50`

标签筛选：
- 可用 `tag_slug=<slug>`
- 也可用 `tag_id=<id>`（与 slug 等价）

## 4. 校验

```bash
jq . nav/root.json >/dev/null
```
