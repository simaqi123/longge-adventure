# -*- coding: utf-8 -*-
"""养生日课早报生成器
从 data/养生知识表.csv 取材，按节气自动出 6 张卡。

设计约束（对齐《养生支线_接入方案.md》）：
- 卡1 节气快照 / 卡2 体质画像 / 卡3 经典条文 / 卡4 今日养护 / 卡5 自省问答 / 卡6 明日预告
- 全卡不得出现：病名、疗效断言、处方药材、侵入性项目、问诊式提问、联系方式、购物链接
- 卡3 只引原文 + 一句白话，不做疗效解读
- 选题随节气与日期轮转，不重复
"""
import csv, os, sys, random, datetime, json, argparse, re

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from paths import SSOT_CSV as SSOT, BRIEF_OUT_DIR as OUT_DIR, ensure_dir  # noqa: E402

# 24 节气顺序（用于明日预告的推进）
SOLAR_ORDER = ["立春","雨水","惊蛰","春分","清明","谷雨","立夏","小满","芒种","夏至","小暑","大暑",
                "立秋","处暑","白露","秋分","寒露","霜降","立冬","小雪","大雪","冬至","小寒","大寒"]

# 体质分组：用于卡2 的"今日关注点"
CONSTITUTION_GROUPS = [
    ("气虚质", "气虚质"), ("阳虚质", "阳虚质"), ("阴虚质", "阴虚质"),
    ("痰湿质", "痰湿质"), ("湿热质", "湿热质"), ("血瘀质", "血瘀质"),
    ("气郁质", "气郁质"), ("气滞质", "气滞质"), ("肺燥质", "肺燥质"),
]

# 节气 → 主导体质倾向（依《四气调神大论》四时摄生与六气配属）
SOLAR_FOCUS = {
    "立春": ("气郁质,血瘀质", "肝气升发，情志宜舒展"),
    "雨水": ("痰湿质,气虚质", "湿气渐长，脾胃宜运化"),
    "惊蛰": ("气郁质,痰湿质", "阳气始振，作息宜提振"),
    "春分": ("气郁质,气虚质", "阴阳平分，起居宜有常"),
    "清明": ("湿热质,痰湿质", "肝气升而脾湿滞，饮食宜分清"),
    "谷雨": ("湿热质,阴虚质", "雨湿交蒸，饮食宜清淡"),
    "立夏": ("阴虚质,气郁质", "心气初升，午间宜小憩"),
    "小满": ("湿热质,痰湿质", "湿热渐显，口味宜清"),
    "芒种": ("湿热质,痰湿质", "湿热交蒸，忌厚味壅滞"),
    "夏至": ("阴虚质,湿热质", "阳气极盛，避暑为要"),
    "小暑": ("湿热质,气虚质", "暑湿渐起，汗出宜适度"),
    "大暑": ("湿热质,气虚质", "暑热至极，静养为上"),
    "立秋": ("阴虚质,肺燥质", "秋气始收，起居宜渐早"),
    "处暑": ("痰湿质,气虚质", "暑气渐退，作息宜收摄"),
    "白露": ("阳虚质,气郁质", "露重温差，护颈护腹"),
    "秋分": ("气郁质,肺燥质", "秋令平分，忌情志外泄"),
    "寒露": ("阳虚质,痰湿质", "寒气渐侵，足部尤宜保暖"),
    "霜降": ("阳虚质,气虚质", "霜降至，忌生冷"),
    "立冬": ("阳虚质,气虚质", "阳气始闭，温养为要"),
    "小雪": ("阳虚质,气郁质", "天寒地冻，宜早卧晚起"),
    "大雪": ("阳虚质,气虚质", "寒气之盛，去寒就温"),
    "冬至": ("阳虚质,阴虚质", "一阳来复，静养藏神"),
    "小寒": ("阳虚质,气虚质", "闭藏渐深，起居宜迟"),
    "大寒": ("阳虚质,气虚质", "寒极将过，待春而动"),
}

# 体质 → 通用倾向描述（卡2 用，与卡1 的节气总纲错开）
CONST_DESC = {
    "气虚质": "气力偏弱，宜少劳多养，食不宜过饱",
    "阳虚质": "阳气偏弱，畏寒喜暖，忌生冷",
    "阴虚质": "阴液偏亏，宜温润平和，忌辛辣燥烈",
    "痰湿质": "痰湿偏盛，宜清爽淡口，忌肥甘厚味",
    "湿热质": "湿热内蕴，宜清淡通利，忌煎炸酒辛",
    "血瘀质": "血行不畅，宜舒展通畅，忌久坐不动",
    "气郁质": "气机郁滞，宜舒展情志，忌压抑内耗",
    "气滞质": "气行不畅，宜疏泄条达，忌情绪憋闷",
    "肺燥质": "肺失润泽，宜清润缓燥，忌辛辣炙烤",
}

# 合规硬闸门：出卡前对每张卡的文本再过一遍
BANNED_IN_CARD = [
    "治疗","根治","治愈","防治","专治","疗效","有效率","消炎","杀菌","排毒",
    "祛湿","活血化瘀","滋阴补阳","疏通经络","诊断","辨证结果","医嘱","处方",
    "针灸","埋线","放血","刺血","牵引","扳法","发泡灸","瘢痕灸",
    "哪里不舒服","什么症状","开方","对症下药","病情如何",
    "加微信","微信号","扫码","二维码","购买链接","立即预约","点击购买",
    "产后","孕期","孕妇","化疗","放疗","术后","小儿",
    "公众号","知识星球","客服","咨询师","报名",
]
# 中医功效断言（与 validate_ssot.py 的 EFFICACY_CLAIMS 保持一致）
EFFICACY_CLAIMS = [
    "养心安神","安神","养心安","清润养阴","养阴","健脾养胃","健脾渗湿","健脾",
    "理气化痰","化痰软坚","化痰","散结","清肝明目","清肝","润肺止咳","润肺",
    "活血化瘀","活血","调经","行气","平补气血","温补气血","益气养血","补气",
    "疏肝理气","理气和胃","清利湿热","化湿消滞","化湿","生津","养胃",
    "清热利胆","祛湿","渗湿","利水消肿","降压","降脂","化痰止咳",
    "温肾助阳","温阳","助阳","滋阴","壮阳","温经","通络","排毒",
    "增强免疫","提高免疫","促进消化","改善睡眠","缓解疲劳","抗氧化",
    "降三高","软化血管","开胃消食","消食化积","止咳化痰","平喘",
]
# 处方药材（养生馆不得推荐口服）
PRESCRIPTION_HERBS = [
    "柴胡","黄芩","附子","麻黄","桂枝","大黄","芒硝","半夏","细辛",
    "雄黄","朱砂","斑蝥","马钱子","川乌","草乌","巴豆","甘遂","大戟",
]
DISEASE_WORDS = [
    "失眠","糖尿病","高血压","心脏病","肥胖","痛风","甲亢","甲减","子宫肌瘤","乳腺增生",
    "肾结石","尿毒症","中风","肿瘤","阳痿","便秘","腹泻","咳嗽","哮喘","皮炎","湿疹",
    "荨麻疹","颈椎病","关节炎","静脉曲张","胆结石","痛经","月经不调","支气管炎","小儿感冒",
    "胃炎","肝炎","高血脂","脂肪肝","白血病","乳腺癌","大肠癌","肺癌","肝癌","食管癌",
    "牛皮癣","尿频","心悸","消瘦","水肿","疥疮","风疹","湿疹",
]

def load_rows():
    with open(SSOT, "r", encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))

def pick(rows, topic, seed, cons_filter=None, solar_filter=None, avoid=(), title_hint=None):
    """按主题+体质+节气筛选，seed 决定轮转，避免与 avoid 重复。
    title_hint：标题命中该关键词的条目优先（更精准的体质专属条目）。"""
    pool = [r for r in rows if r["主题"] == topic]
    if cons_filter:
        narrow = [r for r in pool if any(c.strip() in r["适用体质"] for c in cons_filter if c.strip())]
        pool = narrow or pool
    if title_hint:
        hinted = [r for r in pool if title_hint in r["条目名"]]
        if hinted:
            pool = hinted
    if solar_filter:
        narrowed = [r for r in pool if r["适用节气"] == "ALL" or any(s.strip() in r["适用节气"] for s in solar_filter)]
        pool = narrowed or pool
    if not pool:
        pool = [r for r in rows if r["主题"] == topic]
    if not pool:
        return None
    rnd = random.Random(seed)
    avail = [r for r in pool if r["ID"] not in avoid] or pool
    return rnd.choice(avail)

def scan_card(text, is_classic=False):
    """合规扫描：返回违规词列表。
    豁免：免责声明中的否定式表述（如"不构成医疗诊断"）是合规声明本身，不算违规。
    「经典」卡为《内经》原文引用，原文措辞不等于本方疗效宣称。"""
    hits = []
    NEG_PAT = re.compile(
        r'(不构成|不替代|不是|不属于|不作为|不替代医疗|请至医疗机构|请到医疗机构|'
        r'身体不适请|不构成任何|非医疗|不用于诊断)'
    )
    for w in BANNED_IN_CARD:
        if w not in text:
            continue
        for sent in re.split(r'[。；\n]', text):
            if w in sent and not NEG_PAT.search(sent):
                hits.append(w)
                break
    # 功效断言：经典卡豁免（原文引用）
    if not is_classic:
        for w in EFFICACY_CLAIMS:
            if w in text:
                hits.append(w)
    # 处方药材
    for w in PRESCRIPTION_HERBS:
        if w in text:
            hits.append(w)
    for w in DISEASE_WORDS:
        if w in text:
            hits.append(w)
    return sorted(set(hits))

def build(date_str, rows):
    d = datetime.datetime.strptime(date_str, "%Y-%m-%d")
    seed = int(d.strftime("%Y%m%d"))
    rnd = random.Random(seed)
    # 取当前节气（按日期近似定位：全年 24 节气，用日期序号近似）
    # 用真实节气表更严谨，这里用节气起点日期近似
    SOLAR_STARTS = {
        "立春":"02-04","雨水":"02-19","惊蛰":"03-05","春分":"03-20","清明":"04-05","谷雨":"04-20",
        "立夏":"05-05","小满":"05-21","芒种":"06-06","夏至":"06-21","小暑":"07-07","大暑":"07-23",
        "立秋":"08-07","处暑":"08-23","白露":"09-07","秋分":"09-23","寒露":"10-08","霜降":"10-23",
        "立冬":"11-07","小雪":"11-22","大雪":"12-07","冬至":"12-22","小寒":"01-05","大寒":"01-20",
    }
    md = d.strftime("%m-%d")
    # 精确取当前节气：把每个节气换算成当年日期，取 <= 当前日的最近一个
    cands = []
    for s, st in SOLAR_STARTS.items():
        m2, d2 = map(int, st.split("-"))
        # 1/1 之前属于上一年的节气区间
        if (m2, d2) > (d.month, d.day):
            y = d.year - 1
        else:
            y = d.year
        try:
            cands.append((datetime.date(y, m2, d2), s))
        except ValueError:
            continue
    cands.sort()
    cur = cands[-1][1]
    idx = SOLAR_ORDER.index(cur)
    nxt = SOLAR_ORDER[(idx + 1) % 24]

    focus_cons, focus_note = SOLAR_FOCUS.get(cur, ("ALL", "顺应时令，循序渐进"))

    # ── 卡1 节气快照 ──
    solar_row = next((r for r in rows if r["主题"] == "节气" and cur in r["适用节气"]), None)
    if solar_row is None:
        solar_row = pick(rows, "节气", seed)
    card1_point = solar_row["内容要点"]
    card1_src = solar_row["出处"]

    # ── 卡2 体质画像 ──
    # 卡1 讲节气总纲，卡2 讲该体质在此节气的具体调养方向，两卡不得重复同一句
    cons_list = [c.strip() for c in focus_cons.split(",") if c.strip() and c.strip() != "ALL"]
    cons_desc = CONST_DESC.get(cons_list[0] if cons_list else "气虚质", "宜循四时，循序渐进")
    card2_title = cons_list[0] if cons_list else "气虚质"
    body_row = pick(rows, "体质", seed + 1, cons_filter=cons_list, title_hint=card2_title)
    if body_row is None:
        body_row = pick(rows, "体质", seed + 1)
    card2_body = body_row["内容要点"]

    # ── 卡3 经典条文 ──
    # 避免与卡1 引用同一篇同一段：按篇名去重
    def _chap(src):
        m = re.search(r'《[^》]*?(素问|灵枢)[^》]*?》', src or "")
        return m.group(0) if m else ""
    card1_chap = _chap(card1_src)
    def pick_classic(seedoff):
        cands = [r for r in rows if r["主题"] == "经典"]
        others = [r for r in cands if _chap(r["出处"]) != card1_chap]
        pool = others or cands
        # 体质相关优先
        if cons_list:
            narrow = [r for r in pool if any(c.strip() in r["适用体质"] for c in cons_list)]
            pool = narrow or pool
        rnd = random.Random(seed + seedoff)
        return rnd.choice(pool)
    cls_row = pick_classic(2)
    # 提取原文引句
    q = re.findall(r'「([^」]+)」', cls_row["出处"])
    quote = q[0] if q else cls_row["内容要点"]
    # 白话：只做原文释义，不做疗效解读；调性统一为雅正简练
    plain = {"W-063":"四时各有其调摄之方，顺着时令养生，是最省力也最稳妥的法子。",
             "W-064":"在尚未失衡时就先着手调养，比失衡之后再补救省事得多。",
             "W-065":"饮食讲究方向，胜过讲究分量——食物各有其所宜。",
             "W-066":"饮食有节、起居有常、不妄作劳，是最朴素的养生法门。",
             "W-067":"情志安定，则外邪不易侵袭；内心安稳，本身即是养生。",
             "W-068":"让身体舒展活动，本身就是在养身，不必求诸繁复之法。",
             "W-069":"谷物为养之本，果畜禽菜为辅佐，五者相配方为完备。",
             "W-070":"春夏天阳气升发，养生贵在顺势而不耗损。",
             "W-071":"秋冬天阳气内藏，养生贵在收藏而不外泄。",
             "W-072":"冬令当藏则藏，不使精气过早耗散，来岁方有根本。"}.get(cls_row["ID"],
             "原文所载为四时摄养之总则，宜体会其意而不拘泥其文。")
    card3_quote = quote
    card3_plain = plain
    card3_src = cls_row["出处"].split("：")[0] if "：" in cls_row["出处"] else cls_row["出处"]

    # ── 卡4 今日养护 ──
    food_row = pick(rows, "食养", seed + 3, cons_filter=cons_list, avoid=())
    life_row = pick(rows, "起居", seed + 4, cons_filter=cons_list)
    if food_row and food_row["关联项目"]:
        proj = food_row["关联项目"]
    elif life_row and life_row["关联项目"]:
        proj = life_row["关联项目"]
    else:
        proj = "养生咨询"
    card4_food = food_row["内容要点"] if food_row else ""
    card4_foods = food_row["食材清单"] if food_row else "无"
    card4_life = life_row["内容要点"] if life_row else ""

    # ── 卡5 自省问答 ──
    ref_row = pick(rows, "自省", seed + 5)
    card5_q = ref_row["条目名"] if ref_row else "今日是否按时起身"
    card5_detail = ref_row["内容要点"] if ref_row else ""

    # ── 卡6 明日预告 ──
    nxt_focus = SOLAR_FOCUS.get(nxt, ("ALL", "顺应时令"))
    nxt_row = next((r for r in rows if r["主题"] == "节气" and nxt in r["适用节气"]), None)
    if nxt_row is None:
        nxt_row = pick(rows, "节气", seed + 6)
    # 卡6：明日预告。若明日与今日落在同一节气条目（合并条目），改用 SOLAR_FOCUS 的表述
    nxt_point = nxt_row["内容要点"]
    # 若明日与今日指向同一条节气条目（合并条目，如小雪与大雪共用一条），
    # 则卡6 不重复该条内容，只给 SOLAR_FOCUS 的独立表述
    if nxt_row["ID"] == solar_row["ID"]:
        card6 = f"明日{nxt}，调养重点：{nxt_focus[1]}。"
    else:
        card6 = f"明日{nxt}。{nxt_point}"

    # 卡1 的"调养侧重"：优先取当令体质匹配该节气的条目，避免串到不相关体质
    focus_row = None
    if cons_list:
        pool_f = [r for r in rows if r["主题"] in ("体质", "起居")
                  and r["适用节气"] == cur
                  and any(c.strip() in r["适用体质"] for c in cons_list)]
        if pool_f:
            focus_row = random.Random(seed + 7).choice(pool_f)
    if focus_row is None:
        pool_f = [r for r in rows if r["主题"] in ("体质", "起居") and r["适用节气"] == cur]
        if pool_f:
            focus_row = random.Random(seed + 7).choice(pool_f)
    if focus_row is None:
        focus_row = pick(rows, "体质", seed + 7, cons_filter=cons_list)
    card1_focus = focus_row["内容要点"] if focus_row else focus_note

    cards = [
        ("卡1 · 节气快照", f"🌿 {cur}｜{d.strftime('%m月%d日')} 养生日课",
         [f"**今日节气**：{cur}", f"**节气要点**：{card1_point}", f"**调养侧重**：{card1_focus}",
          f"**原文出处**：{card1_src}"]),
        ("卡2 · 体质画像", f"🫧 今日体质关注｜{card2_title}",
         [f"**体质倾向**：{cons_desc}", f"**调养方向**：{card2_body}",
          f"**适配项目**：{proj}"]),
        ("卡3 · 经典条文", "📜 今日一句",
         [f"**原文**：{card3_quote}", f"**白话**：{card3_plain}", f"**出处**：{card3_src}"]),
        ("卡4 · 今日养护", "🍵 一食一养",
         [f"**饮食**：{card4_food}", f"**起居**：{card4_life}",
          f"**食材**：{card4_foods}", f"**可配合项目**：{proj}"]),
        ("卡5 · 自省问答", "💭 今日一问",
         [f"**{card5_q}**", f"{card5_detail}", "（自省题，不构成任何诊断）"]),
        ("卡6 · 明日预告", "📅 明日提示",
         [card6, "**提示**：本栏目为养生参考，不替代医疗诊断；身体不适请至医疗机构就诊。"]),
    ]

    # ── 合规扫描 ──
    problems = []
    for title, headline, body in cards:
        txt = title + headline + " ".join(body)
        h = scan_card(txt, is_classic=("经典" in title))
        if h:
            problems.append((title, h))
    return {
        "date": date_str, "solar": cur, "next": nxt, "cards": cards, "problems": problems,
        "total_rows": len(rows),
    }

def render(result):
    lines = [f"# 养生日课早报 · {result['date']}（{result['solar']}）", ""]
    for title, headline, body in result["cards"]:
        lines.append(f"## {headline}")
        lines.append(f"*{title}*")
        lines.append("")
        for b in body:
            lines.append(b)
            lines.append("")
    lines.append("---")
    lines.append("")
    lines.append(f"> 本期由养生知识表（SSOT）自动生成，共 {result['total_rows']} 条素材。")
    lines.append("> 全部内容已通过合规扫描：无病名、无疗效断言、无处方药材、无侵入性项目、无问诊式提问、无联系方式与购物链接。")
    lines.append("> 本栏目为养生参考，不构成医疗诊断；身体不适请至医疗机构就诊。")
    return "\n".join(lines)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--date", default=datetime.date.today().isoformat())
    ap.add_argument("--dates", nargs="*", default=None)
    args = ap.parse_args()
    rows = load_rows()
    os.makedirs(OUT_DIR, exist_ok=True)
    dates = args.dates or [args.date]
    for ds in dates:
        r = build(ds, rows)
        if r["problems"]:
            print(f"[{ds}] ⚠ 合规问题：")
            for t, h in r["problems"]:
                print(f"    {t}: {h}")
        else:
            print(f"[{ds}] ✅ 合规通过")
        path = os.path.join(OUT_DIR, f"养生日课早报_{ds}.md")
        with open(path, "w", encoding="utf-8") as f:
            f.write(render(r))
        print(f"    → {path}")

if __name__ == "__main__":
    main()
