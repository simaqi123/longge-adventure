# 贡献指南

欢迎参与。这个仓库的价值不在代码量，在**规矩严不严**。

---

## 提交前必跑

```bash
python scripts/validate_ssot.py data/养生知识表.csv     # 必须 0 错误
python scripts/validate_survival_map.py                 # 必须全部通过
python scripts/validate_deep_model.py                   # 必须全部通过
python scripts/validate_constitution_html.py            # 必须全部通过
python scripts/test_survival_map_injection.py           # 必须 44/44 拦截
```

任何一项不过，**不要提交**。PR 里附上这五条命令的输出。

---

## 三条硬规矩

### 1. 不破结构不变量

```
Σ 独占素材 ≡ SSOT 实际条目数
面积口径唯一：月产出件数
必须且仅有一个现金出口
```

改 `survival_map_data.py` 的 `ROLES` 或 `THEME_OWNER` 时，
必须先想清楚新主题归谁，然后确认第一条恒等式没破。校验器会替你盯着。

### 2. 不破数字分层

页面上每个数字必须标明属于哪一层：

| 层级 | 要求 |
|---|---|
| 可核验 | 来自 SSOT 或脚本实跑，逐条可回溯 |
| 口径值 | 明确标注"非实测"，可被真实记录覆盖 |
| 不推算 | 收入、转化率、成本——一律不上页面 |

**最常见的越界**：把口径值写成实测值、把推算说成结论。
校验器会拦截"工时为实测数据"这类表述，但绕过它需要刻意为之——别做那个人。

### 3. 不破合规红线

新增任何条目、文案、页面内容前，先读 [`docs/合规边界手册.md`](docs/合规边界手册.md)。

- 「内容要点」禁含疾病治疗表述、医疗用语、功效断言、特定人群限定、问诊诱导
- 科普页面禁含联系方式、链接、二维码、扫码引导
- 食材清单每味必须标真实归属，处方药材一律不得出现

**免责声明不能用来豁免正文违规。** 这是最容易被钻的空子，别钻。

---

## 怎么加一条知识

1. 在 `data/养生知识表.csv` 末尾追加一行，`ID` 用下一个可用编号
2. `主题` 选一个已有主题（新增主题要同步改 `THEME_OWNER`，见规矩 1）
3. `内容要点` 写**生活建议**，不写医疗表述
4. `出处` 填可溯源来源
5. `食材清单` 每味标归属（标错会被拦）
6. `数据级别` 三选一
7. 跑完上面五条命令
8. 重建页面：`python scripts/build_survival_map.py`

---

## 怎么改角色体系

`survival_map_data.py` 里改，改完必须跑全套校验。

新增位次时检查三件事：

1. `THEME_OWNER` 是否需要新增归属（否则素材守恒会破）
2. `actions` 里每个 `auto` 节点是否有对应的 `TOOL_EVIDENCE`（否则"工具证据"校验会挂）
3. `build_survival_map.py` 里是否需要为新位次补展示文案

---

## 别做的事

- ❌ 手工改 `web/` 下的 HTML —— 它们是生成物，下次构建会被覆盖
- ❌ 手工改 `data/养生知识表.csv` 之外的副本来"对齐"某处 —— 改 SSOT，改 SSOT
- ❌ 在页面上加免责声明来让违规内容"看起来合规"
- ❌ 把内部编号、私有路径、机构信息提交进来
- ❌ 引入第三方依赖 —— 本仓库刻意保持零依赖，Python 标准库即可运行

---

## 许可

提交即表示同意你的贡献以 MIT 协议发布。

涉及知识表内容的贡献，确保条目能溯源到公开来源（《内经》原文、公开标准、公开法规），
或为已获授权的原创整理，并在 `备注` 里写明加工过程。


---

## Working on the English edition

The English table (`data/wellness_kb.en.csv`) and the English page
(`web/solo-wellness-map.en.html`) are **generated artifacts**. Do not edit them
by hand — edit `scripts/build_en_kb.py`, `scripts/build_en_map.py` or
`scripts/i18n_en.py` and rebuild.

Three rules apply to every English change:

1. **Mirror the Chinese table.** Row count, ID sequence and theme distribution
   must match `data/养生知识表.csv` exactly. `validate_en_kb.py` compares them.
2. **No disease names, no therapeutic claims.** English health claims are read
   strictly (FTC, and the FDA's treatment of many herbs). The English
   validator has its own red-line word lists, with negation-context handling
   so that a prohibition is not mistaken for a claim.
3. **No Chinese prose in the output.** The generators refuse to write a file
   that still contains Chinese characters (except real file names a reader has
   to type). If a translation is missing, add it to `scripts/i18n_en.py`.

Run the English checks before pushing:

```bash
python scripts/build_en_kb.py
python scripts/validate_en_kb.py
python scripts/build_en_map.py
python scripts/validate_en_map.py
```

If you add a role slot, a roadmap phase or a risk, add the English copy to
`scripts/i18n_en.py` in the same commit — the English build fails loudly
rather than silently falling back to Chinese.
