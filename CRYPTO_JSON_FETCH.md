# crypto.json 获取方式说明

对应文件：`nav/crypto.json`

## 1. 文件职责

维护 Crypto 频道下的子分类导航：
- 如 `5m`、`15m`、`1h`、`daily`、`weekly`、`etf`

字段重点：
- `id`
- `label`
- `slug`
- `p_slug`（通常是 `crypto`）
- `forceShow`

## 2. 数据获取方式

### 2.1 子分类列表来源

来源：本地静态维护（`nav/crypto.json`）。

更新方式：
1. 根据产品导航变更更新 `children`。
2. 与 `nav/nav_root.json` 中 `Crypto.children` 保持一致（若该快照被使用）。

### 2.2 每个子分类对应事件数据

来源：`events/keyset`，按 `slug` 查询。

示例：
```bash
curl -s "https://gamma-api.polymarket.com/events/keyset?limit=10&active=true&archived=false&closed=false&order=volume24hr&ascending=false&tag_slug=1h" | jq .
```

常见映射：
- `5 Min` -> `tag_slug=5m`
- `15 Min` -> `tag_slug=15m`
- `1 Hour` -> `tag_slug=1h`
- `Pre Market` -> `tag_slug=pre-market`

## 3. `tag_slug` / `tag_id` 对齐方式

可先查标签：
```bash
curl -s "https://gamma-api.polymarket.com/tags/slug/1h" | jq .
```

然后两种查询方式等价：
```bash
curl -s "https://gamma-api.polymarket.com/events/keyset?active=true&closed=false&limit=2&tag_slug=1h" | jq .
curl -s "https://gamma-api.polymarket.com/events/keyset?active=true&closed=false&limit=2&tag_id=<上一步返回id>" | jq .
```

## 4. 校验

```bash
jq . nav/crypto.json >/dev/null
```
