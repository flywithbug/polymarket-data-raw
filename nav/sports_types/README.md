# sports.json 拆分说明

本目录将 `nav/sports.json` 的顶层 `children` 按“运动类型”拆分为多个文件，便于分开维护。

## 规则

- 若节点 `p_slug == sports`：该节点按自身 `slug` 归类。
- 其他节点：按其 `p_slug` 归类。

示例：
- `NBA (p_slug=basketball)` -> `basketball.json`
- `UCL (p_slug=soccer)` -> `soccer.json`
- `Football (p_slug=sports, slug=football)` -> `football.json`

## 文件

- `index.json`：类型索引
- `sports_config.yaml`：根节点排序与提级联赛配置
- `<type>.json`：每个运动类型一个文件，结构为：
  - `sportType`
  - `source`
  - `item`（该类型的根节点对象，内部可含 `children`）

## root_config 配置项

- `rootOrder`：根节点排序（按 slug）
- `rootPromotedSlugs`：要提到根节点的联赛 slug 列表

说明：
- 提级联赛会从全树中按 `slug` 查找并插入根节点。
- 提级后同 slug 的原根节点项会去重，避免重复。

## 合并

```bash
python3 scripts/merge_sports_types.py
```

会按 `index.json + sports_config.yaml` 生成 `nav/sports.json`，并自动备份 `nav/sports.json.bak`。
