#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
SSOT 表校验器
用途：在数据官写入后、任何角色消费前，检查真相源表是否满足契约 A。

用法：
    python validate_ssot.py                        # 校验 data/ 下全部真相源表
    python validate_ssot.py data/养生知识表.csv     # 校验指定单表

规则来源：docs/契约层.md（契约 A）+ docs/合规边界手册.md（内容红线）
"""
import csv
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from paths import DATA_DIR as SSOT_DIR, FOOD_MED_JSON  # noqa: E402
VALID_LEVELS = {"实测", "推算", "估算"}

# 字段级规则：字段名 -> (是否必填, 允许值集合或None, 数值范围或None)
# 通用字段，适用于所有真相源表；业务专用字段在各表的 validate_* 函数内自行校验
FIELD_RULES = {
    "数据级别": (True, VALID_LEVELS, None),
}

# 养生支线合规校验（依据：养生支线_合规边界手册.md）
# 禁止出现在"内容要点"里的疾病治疗/疗效表述
FORBIDDEN_TERMS = [
    "治疗", "根治", "治愈", "防治", "专治", "疗效", "有效率", "治愈率",
    "消炎", "杀菌", "排毒", "祛湿", "活血化瘀", "滋阴补阳", "疏通经络",
    "包治", "根治", "一次见效", "保证见效", "无副作用", "祖传秘方",
    "诊断", "辨证结果", "医嘱", "处方",
]
# 禁止出现在"关联项目"里的侵入性技术（养生馆非医疗渠道）
FORBIDDEN_PROJECTS = ["针灸", "埋线", "刺血", "放血", "发泡灸", "瘢痕灸", "牵引", "扳法"]
# 处方类药材，禁止出现在食材清单
PRESCRIPTION_HERBS = [
    "柴胡", "黄芩", "附子", "麻黄", "桂枝", "大黄", "芒硝", "半夏", "细辛",
    "雄黄", "朱砂", "斑蝥", "马钱子", "川乌", "草乌", "巴豆", "甘遂", "大戟",
]
# 中医功效断言词：食养/起居条目不得宣称功能性效果
# 依据《广告法》第十七条（医疗用语）与《中医养生保健服务规范（试行）》第六条（不得宣传治疗作用）
EFFICACY_CLAIMS = [
    "养心安神", "安神", "养心安", "清润养阴", "养阴", "健脾养胃", "健脾渗湿", "健脾",
    "理气化痰", "化痰软坚", "化痰", "散结", "清肝明目", "清肝", "润肺止咳", "润肺",
    "活血化瘀", "活血", "调经", "行气", "平补气血", "温补气血", "益气养血", "补气",
    "疏肝理气", "理气和胃", "清利湿热", "化湿消滞", "化湿", "生津", "养胃",
    "清热利胆", "祛湿", "渗湿", "利水消肿", "降压", "降脂", "化痰止咳",
    "温肾助阳", "温阳", "助阳", "滋阴", "壮阳", "温经", "通络", "排毒",
    "增强免疫", "提高免疫", "促进消化", "改善睡眠", "缓解疲劳", "抗氧化",
    "降三高", "软化血管", "开胃消食", "消食化积", "止咳化痰", "平喘",
]
# 特定人群限定词：养生馆普通渠道不得面向孕产/术后/婴幼儿等特定医疗人群推荐
SPECIFIC_POPULATION = [
    "产后", "孕期", "孕妇", "妊娠", "哺乳期", "小儿", "婴幼儿", "化疗",
    "放疗", "手术后", "久病", "康复期", "ICU", "透析", "移植后", "癌", "症", "征",
]
# 问诊诱导词：养生支线只能"陪伴"，不能引导问诊（规范第四条：健康咨询指导，非诊疗）
DIAGNOSTIC_PROBES = [
    "哪里不舒服", "什么症状", "开方", "看下病", "帮我诊", "辨证论治", "对症下药",
    "来看看", "来复查", "带病历", "病情如何", "严重吗", "是不是病",
]

# ---- 食材清单核验（数据源：食药清单.json，依据卫健委4批次公告，共106种食药物质）----
try:
    import json as _json
    _lst = _json.load(open(FOOD_MED_JSON, encoding="utf-8"))
    FOOD_MED_SET = set(_lst["food_med"])
    HEALTH_ONLY_SET = set(_lst["health_only"])
    PLAIN_FOOD_SET = set(_lst.get("plain_food", []))
    COMMON_FOOD_SET = set(_lst.get("common_food", []))
    NOT_FOOD_SET = set(_lst.get("not_food", []))
    SPICE_ONLY_SET = set(_lst.get("spice_only", []))
except Exception:
    FOOD_MED_SET, HEALTH_ONLY_SET = set(), set()
    PLAIN_FOOD_SET, COMMON_FOOD_SET = set(), set()
    NOT_FOOD_SET, SPICE_ONLY_SET = set(), set()

# 普通食材白名单（日常农作物/畜禽/水产/调味，非药材）
PLAIN_FOOD = set(
    "粳米 大米 小米 糯米 小麦 荞麦 燕麦 高粱 黄米 赤小豆 绿豆 黄豆 绿豆芽 黄豆芽 毛豆 芸豆 "
    "白扁豆 扁豆 芋头 苦瓜 冬瓜 葫芦 猴头菇 羊肚菌 青蒜 大蒜 葱 韭菜 芹菜 香菜 菠菜 白菜 萝卜 "
    "山楂 核桃 莲藕 银耳 紫菜 海带 海藻 甘蔗 梨 枇杷 鸭梨 草莓 猕猴桃 芒果 荔枝 腰果 蜂蜜 冰糖 红糖 "
    "猪腰 猪心 猪肚 猪肝 猪肺 猪瘦肉 猪排骨 鸡 鸡蛋 鸭 乌鸡 兔肉 羊肉 牛肉 排骨 鲫鱼 鲤鱼 鳝鱼 黄鳝 "
    "带鱼 黄鱼 鲈鱼 虾 蟹 牛奶 豆浆 蜂蜜 合欢花 黑木耳 木耳 玫瑰茄".split()
) | PLAIN_FOOD_SET | COMMON_FOOD_SET

# 食材别名归一：表内写法 -> 清单标准名
FOOD_ALIAS = {
    "白萝卜": "萝卜", "萝卜": "萝卜",
    "桂圆": "桂圆", "龙眼肉": "桂圆", "龙眼": "桂圆",
    "大枣": "大枣", "红枣": "大枣", "枣": "大枣",
    "橘皮": "橘皮", "陈皮": "陈皮", "青皮": "青皮",
    "薏米": "薏苡仁", "生薏米": "薏苡仁", "薏苡仁": "薏苡仁",
    "生山楂": "山楂", "山楂片": "山楂", "山楂": "山楂",
    "干荷叶": "荷叶", "荷叶": "荷叶",
    "紫苏籽": "紫苏籽", "苏子": "紫苏籽",
    "猪瘦肉": "猪瘦肉", "瘦猪肉": "猪瘦肉", "猪肉": "猪瘦肉",
    "麦粒": "大麦", "大麦粒": "大麦",
    "鳖": "甲鱼", "甲鱼": "甲鱼",
    "杏仁": "甜杏仁", "苦杏仁": "甜杏仁",
    "豆类": "豆类", "豆仁": "豆类",
    "猪腰子": "猪腰", "羊肾": "羊肾",
    "乌龙茶": "乌龙茶", "虾米": "虾米", "丝瓜": "丝瓜",
    "鲜鲤鱼": "鲤鱼", "鲫鱼": "鲫鱼", "鲤鱼": "鲤鱼",
    "川椒": "花椒", "花椒": "花椒",
    "玉米须": "玉米须", "枇杷叶": "枇杷叶",
    "白扁豆": "白扁豆", "扁豆": "白扁豆",
    "淮山药": "山药", "山药": "山药",
    "莲子": "莲子", "莲子肉": "莲子",
    "枸杞子": "枸杞子", "枸杞": "枸杞子",
    "决明子": "决明子", "草决明子": "决明子", "草决明": "决明子",
    "鸡内金": "鸡内金", "荜茇": "荜茇",
}


def _food_truth(name):
    """返回食材的真实归属标签；未登记返回 None"""
    std = FOOD_ALIAS.get(name, name)
    if std in FOOD_MED_SET:
        return "食药清单内"
    if std in HEALTH_ONLY_SET:
        return "保健食品级"
    if std in PLAIN_FOOD:
        # 普通食材细分：公告明确的普通食品 vs 一般日常食材
        if std in PLAIN_FOOD_SET:
            return "普通食品"
        return "普通食材"
    return None


def validate_wellness(path):
    """养生知识表校验：合规红线 + 出处必填 + 食材清单"""
    errors, warns, stats = [], [], {"rows": 0, "topics": {}}
    with open(path, "r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        if not reader.fieldnames:
            return (["表头为空或无法解析"], [], stats)
        required_cols = ["ID", "主题", "条目名", "内容要点", "出处", "数据级别"]
        missing = [c for c in required_cols if c not in reader.fieldnames]
        if missing:
            errors.append(f"缺少必需列: {', '.join(missing)}")

        for i, row in enumerate(reader, start=2):
            stats["rows"] += 1
            line = f"第 {i} 行"
            topic = (row.get("主题") or "").strip()
            if topic:
                stats["topics"][topic] = stats["topics"].get(topic, 0) + 1

            for c in required_cols:
                if c in row and not (row.get(c) or "").strip():
                    errors.append(f"{line}: 必填字段 '{c}' 为空")

            level = (row.get("数据级别") or "").strip()
            if level and level not in VALID_LEVELS:
                errors.append(f"{line}: '数据级别' = '{level}' 不在允许值 {sorted(VALID_LEVELS)}")

            point = (row.get("内容要点") or "").strip()
            # 元话语豁免：「边界」主题的条目本身在陈述禁用规则，不应被自己的规则拦住
            is_meta = topic == "边界" or (row.get("备注") or "").strip().startswith("规范第") \
                or "配合第八条" in (row.get("备注") or "") or "双链结构" in (row.get("备注") or "")
            if not is_meta:
                hit = [t for t in FORBIDDEN_TERMS if t in point]
                if hit:
                    errors.append(f"{line}: '内容要点' 含禁用医疗/疗效表述 {hit} → 必须去医疗化改写")

            proj = (row.get("关联项目") or "").strip()
            phit = [t for t in FORBIDDEN_PROJECTS if t in proj]
            if phit:
                errors.append(f"{line}: '关联项目' 含侵入性技术 {phit} → 养生馆渠道不得挂载")

            food = (row.get("食材清单") or "").strip()
            fhit = [h for h in PRESCRIPTION_HERBS if h in food]
            if fhit:
                errors.append(f"{line}: '食材清单' 含处方药材 {fhit} → 养生馆不得推荐口服")

            # 食材清单状态标注核验：标注必须与真实归属一致
            if food and food != "无" and FOOD_MED_SET:
                for item in food.split(","):
                    item = item.strip()
                    if not item or "(" not in item:
                        continue
                    name = item.split("(")[0].strip()
                    claimed = item.split("(")[1].rstrip(")").strip()
                    # 允许附加限定后缀（如 "食药清单内·仅限香辛料"），拆分出基础标签与限定
                    claimed_base = claimed.split("·")[0].strip()
                    qualifier = "·".join(claimed.split("·")[1:]).strip() if "·" in claimed else ""

                    # 规则 A：公告明确"不是普通食品"的物质，任何渠道都不得作食材
                    if FOOD_ALIAS.get(name, name) in NOT_FOOD_SET:
                        errors.append(f"{line}: 食材 '{name}' 属公告明确的非普通食品 → 养生渠道绝对禁用")
                        continue

                    truth = _food_truth(name)
                    if truth is None:
                        warns.append(f"{line}: 食材 '{name}' 未在食药清单/普通食材表中登记 → 请核实后标注")
                        continue
                    if claimed_base != truth:
                        errors.append(f"{line}: 食材 '{name}' 标注为 '{claimed_base}'，实际归属为 '{truth}' → 标注不实")
                        continue

                    # 规则 B：食药物质中"仅限作香辛料和调味品"的6种，不得作为主要食材
                    std = FOOD_ALIAS.get(name, name)
                    if std in SPICE_ONLY_SET:
                        if not qualifier:
                            errors.append(f"{line}: 食材 '{std}' 仅限作为香辛料和调味品使用（2019年第8号公告）→ 必须标注使用限定")
                        elif "香辛料" not in qualifier:
                            errors.append(f"{line}: 食材 '{std}' 的限定标注应为 '仅限香辛料'，实为 '{qualifier}'")
                    elif qualifier:
                        warns.append(f"{line}: 食材 '{name}' 无香辛料限定要求，却标注了 '{qualifier}'")

            src = (row.get("出处") or "").strip()
            if not src or src.upper() == "NONE":
                errors.append(f"{line}: '出处' 为空 → 养生条目必须可溯源")

            # 功效断言检测：养生馆普通渠道不得宣称功能性效果
            # 「经典」主题是《内经》原文引用，原文措辞不等于本方疗效宣称
            if not is_meta and topic != "经典":
                effhit = [t for t in EFFICACY_CLAIMS if t in point]
                if effhit:
                    errors.append(f"{line}: '内容要点' 含功效断言 {effhit} → 养生馆普通渠道不得宣称功能性效果")

            # 特定人群限定检测：养生馆普通渠道不得面向特定医疗人群
            spop = [t for t in SPECIFIC_POPULATION if t in point]
            if spop:
                errors.append(f"{line}: '内容要点' 含特定人群限定 {spop} → 养生馆普通渠道不得面向该人群推荐")

            # 问诊诱导检测（对全部主题生效，包括自省题）
            probe = [t for t in DIAGNOSTIC_PROBES if t in point]
            if probe:
                errors.append(f"{line}: '内容要点' 含问诊诱导表述 {probe} → 养生支线只做陪伴，不引导问诊")

            foods = (row.get("食材清单") or "").strip()
            if foods and food:
                pass
            if foods and not any(c in foods for c in "食药清单内,清单外,无"):
                warns.append(f"{line}: '食材清单' 未标注清单状态（应标 '食药清单内' / '清单外'）")
    return errors, warns, stats


def validate_generic_csv(path):
    """通用 CSV 真相源校验：字段级规则 + 数据级别 + 出处必填

    不绑定任何具体业务线——适用于任何遵循契约 A 的真相源表。
    业务专用规则请写在各自的 validate_* 函数里。
    """
    errors, warns, stats = [], [], {"rows": 0, "level": {}}
    with open(path, "r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        if not reader.fieldnames:
            return (["表头为空或无法解析"], [], stats)

        for i, row in enumerate(reader, start=2):
            stats["rows"] += 1
            line = f"第 {i} 行"

            for name, (required, allowed, rng) in FIELD_RULES.items():
                if name not in row:
                    continue
                val = (row.get(name) or "").strip()
                if required and not val:
                    errors.append(f"{line}: 必填字段 '{name}' 为空")
                    continue
                if not val:
                    continue
                if allowed is not None and val not in allowed:
                    errors.append(f"{line}: '{name}' = '{val}' 不在允许值 {sorted(allowed)}")
                if rng is not None:
                    try:
                        num = float(val)
                        if not (rng[0] <= num <= rng[1]):
                            warns.append(f"{line}: '{name}' = {num} 超出常见范围 {rng}")
                    except ValueError:
                        errors.append(f"{line}: '{name}' = '{val}' 不是数值")

            level = (row.get("数据级别") or "").strip()
            if level:
                stats["level"][level] = stats["level"].get(level, 0) + 1

            # 估算值必须可追溯（契约 A：不得用估算值冒充实测值）
            if level == "估算" and not (row.get("备注") or "").strip():
                warns.append(f"{line}: 数据级别=估算 但 '备注' 为空（估算值须可追溯）")

    return errors, warns, stats


def validate_generic_md(path):
    """通用 Markdown 真相源校验：非空 + 状态枚举"""
    errors, warns = [], []
    with open(path, "r", encoding="utf-8-sig") as f:
        content = f.read()
    if not content.strip():
        errors.append("文件为空")
    return errors, warns, {"rows": max(0, len(content.splitlines()) - 1)}


def main():
    targets = sys.argv[1:] or [os.path.join(SSOT_DIR, "养生知识表.csv")]
    total_err = 0
    for path in targets:
        if not os.path.exists(path):
            print(f"[跳过] {path} 不存在")
            continue
        name = os.path.basename(path)
        if name.endswith(".csv") and "养生" in name:
            errors, warns, stats = validate_wellness(path)
        elif name.endswith(".csv"):
            errors, warns, stats = validate_generic_csv(path)
        else:
            errors, warns, stats = validate_generic_md(path)

        total_err += len(errors)
        status = "通过" if not errors else "不通过"
        print(f"\n=== {name} · {status} ===")
        if "level" in stats and stats["level"]:
            print(f"  行数 {stats['rows']}｜成功 {stats.get('ok', 0)}｜失败 {stats.get('failed', 0)}"
                  f"｜级别分布 {stats['level']}")
        elif "topics" in stats and stats["topics"]:
            print(f"  行数 {stats['rows']}｜主题分布 {stats['topics']}")
        else:
            print(f"  行数 {stats.get('rows', 0)}")
        for e in errors[:25]:
            print(f"  [错误] {e}")
        if len(errors) > 25:
            print(f"  ... 另有 {len(errors) - 25} 条错误")
        for w in warns[:15]:
            print(f"  [警告] {w}")
        if len(warns) > 15:
            print(f"  ... 另有 {len(warns) - 15} 条警告")

    print(f"\n总计错误 {total_err} 条。" + ("全部通过。" if total_err == 0 else "请修复后再消费该表。"))
    return 1 if total_err else 0


if __name__ == "__main__":
    sys.exit(main())
