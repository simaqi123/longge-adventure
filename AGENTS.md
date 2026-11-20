# AGENTS.md

> 给 AI 编码助手看的项目约定。人先读 [`README.md`](README.md)。

## 这个项目是什么

一个中医养生方向的一人公司 AI 员工体系。核心资产是**生成管线**，不是页面。

页面（`web/`）是**生成物**。永远不要手改 HTML——改数据层，然后重新生成。

## 目录职责

| 目录 | 职责 | 谁写 |
|---|---|---|
| `data/` | 单一真相源（SSOT）。知识表、食药清单、出处对照表 | 数据官（唯一写入者） |
| `scripts/` | 生成器 + 校验器 + 注入测试 | 工程交付官 |
| `web/` | 生成物。生存地图、体质自测 | **只由脚本写入** |
| `output/` | 生成物。早报 | **只由脚本写入** |
| `docs/` | 方法论、口径声明、合规手册、契约层（中文） | 人工维护 |
| `docs/en/` | 上述文档的英文版 + 引流工具包 | 人工维护 |

## 三条不可破的不变量

改任何东西前先确认这三条没被破坏：

1. **`Σ 独占素材 ≡ SSOT 实际条目数`** — 主题唯一归属，见 `survival_map_data.py` 的 `THEME_OWNER`
2. **面积口径唯一：月产出件数** — 不得混用素材条数与产出件数
3. **必须且仅有一个现金出口** — `THEME_OWNER` 里指向 `monetize` 的主题唯一

## 改代码的标准流程

**改 `data/养生知识表.csv`（数据层）**

```bash
python scripts/validate_ssot.py data/养生知识表.csv    # 0 错误
python scripts/build_survival_map.py
python scripts/build_constitution_test.py
python scripts/validate_survival_map.py
python scripts/validate_deep_model.py
```

**改数据层后，英文版必须同步重建**（英文表与英文页面都是从中文表派生的）：

```bash
python scripts/build_en_kb.py        # → data/wellness_kb.en.csv
python scripts/build_en_map.py       # → web/solo-wellness-map.en.html
python scripts/validate_en_kb.py     # 英文红线 + 与中文表镜像校验
python scripts/validate_en_map.py    # 英文页不变量 + 数字一致性
```

英文版有两条额外约束：

1. **英文表与中文表必须镜像**——行数、ID 序列、主题分布完全一致，
   `validate_en_kb.py` 会比对。改动中文表而不重建英文表，CI 会挂。
2. **英文红线独立于中文红线**——`validate_en_kb.py` 用英文疗效词表与疾病名词表，
   并按句处理否定语境（"must not be called a diagnosis" 是禁止，不是宣称）。

英文表的**生成策略**见 `scripts/build_en_kb.py` 顶部注释：
91 条完整翻译（节气/经典/边界/自省/体质/项目），114 条走结构化模板。
不要用机器翻译直接灌满 205 条——英文健康宣称的监管比中文更严。

**改 `scripts/survival_map_data.py`（位次/角色）**

改完必须跑全套，五条命令全绿才能提交。新增位次时检查：

- `THEME_OWNER` 是否需要新增归属（否则守恒会破）
- `actions` 里每个 `auto` 节点是否有对应的 `TOOL_EVIDENCE`（否则工具证据校验会挂）
- `build_survival_map.py` 是否需要为新位次补展示文案

**改 `scripts/survival_deep_model.py`（工序/工时/路线/风险）**

工时是**口径值不是实测值**，任何工时改动都必须在页面上保持"非实测"标注，
并且不能引入收入/转化率/成本数字。

## 完整校验命令

提交前必须全绿：

```bash
python scripts/validate_ssot.py data/养生知识表.csv
python scripts/validate_survival_map.py
python scripts/validate_deep_model.py
python scripts/validate_constitution_html.py
python scripts/test_survival_map_injection.py
python scripts/build_en_kb.py
python scripts/validate_en_kb.py
python scripts/build_en_map.py
python scripts/validate_en_map.py
python scripts/leak_scan.py
```

倒数第二条是**注入测试**：故意破坏页面确认校验器拦得住（期望 44/44）。
校验器自己说"通过"没有意义，能抓住被破坏的页面才有意义。

## 硬性禁令

- ❌ 手改 `web/` 和 `output/` 下的任何文件
- ❌ 在页面上加免责声明来让违规内容"看起来合规"
- ❌ 把口径值写成实测值、把推算写成结论
- ❌ 在 `内容要点` 里写疾病治疗表述、医疗用语、功效断言、特定人群限定、问诊诱导
- ❌ 在科普页面加联系方式、链接、二维码、扫码引导
- ❌ 引入第三方依赖（保持 Python 标准库）
- ❌ 硬编码真实机构名、价格、个人信息到任何入库文件
- ❌ 在任何表里留下疾病名（含「出处」列）——读者会把它读成适应症
- ❌ 在英文表里写疗效宣称、疾病名、特定人群限定、问诊诱导
- ❌ 手改 `data/wellness_kb.en.csv`——它是生成物，改 `scripts/build_en_kb.py`

最后一条的含义：**脱敏规则必须用通用正则表达**。参考 `scripts/sanitize_for_public.py`——
它自己不含任何真实敏感字面量，靠正则作用于任意来源表。

## 新增知识条目的字段要求

| 列 | 要求 |
|---|---|
| `ID` | `W-` + 三位序号，一经分配不回收 |
| `主题` | 8 类之一；新增主题要同步改 `THEME_OWNER` |
| `内容要点` | 生活建议，不写医疗表述 |
| `出处` | 可溯源：《素问》《灵枢》原文 / 公开标准 / 公开法规 / 主题级资料 |
| `食材清单` | 每味标真实归属（`食药清单内`/`保健食品级`/`普通食品`/`普通食材`） |
| `数据级别` | `实测` / `推算` / `估算` 三选一 |
| `备注` | 加工说明、食材依据、边界依据 |

## 环境

Python 3.8+，零第三方依赖。所有路径由 `scripts/paths.py` 统一解析，
**不要在脚本里硬编码目录名**。
