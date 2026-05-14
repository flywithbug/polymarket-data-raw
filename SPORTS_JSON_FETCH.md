# sports.json 获取方式说明

对应文件：`nav/sports.json`

## 1. 文件职责

维护 Sports 频道下的联赛/运动分类树：
- 一级示例：`NBA`、`UCL`、`NHL`、`Football`、`Soccer`
- 多级示例：`Soccer -> EPL/UCL/...`

字段重点：
- `id`
- `label`
- `slug`
- `p_slug`
- `icon`
- `children`

## 2. 数据获取方式

### 2.1 联赛分类来源

来源分两层：
1. 本地导航：`nav/sports.json`
2. 在线联赛总表：`https://gamma-api.polymarket.com/sports`

获取示例：
```bash
curl -s "https://gamma-api.polymarket.com/sports" | jq .
```

### 2.2 运动类型聚合（以 soccer 为例）

1. 先拿运动标签 id：
```bash
curl -s "https://gamma-api.polymarket.com/tags/slug/soccer" | jq .
```
当前示例：`id=100350`

2. 使用该标签过滤事件（`tag_slug` 与 `tag_id` 等价）：
```bash
curl -s "https://gamma-api.polymarket.com/events/keyset?active=true&closed=false&limit=2&tag_slug=soccer" | jq .
curl -s "https://gamma-api.polymarket.com/events/keyset?active=true&closed=false&limit=2&tag_id=100350" | jq .
```

### 2.3 联赛级事件（以 epl 为例）

```bash
curl -s "https://gamma-api.polymarket.com/events/keyset?limit=10&active=true&archived=false&closed=false&order=volume24hr&ascending=false&tag_slug=epl" | jq .
```

## 3. 导航字段到请求参数映射

- 导航 `slug` -> `events_query.tag_slug`
- 导航 `id` -> `tag_id`
- `categories`/`children` -> 下钻下一层分类

建议请求拼装顺序：
1. 根参数：`active/closed/archived/order/ascending/limit`
2. 叠加当前节点 `tag_slug` 或 `tag_id`
3. 调用 `https://gamma-api.polymarket.com/events/keyset`

## 4. 校验

```bash
jq . nav/sports.json >/dev/null
```
