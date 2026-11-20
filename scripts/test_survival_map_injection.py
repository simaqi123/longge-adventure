# -*- coding: utf-8 -*-
"""养生一人公司生存地图 · 注入测试

目的：验证 validate_survival_map.py 与 validate_deep_model.py 的红线**确实拦得住**，
而不是只验证合规样本通过。

每条用例都是一次真实篡改，跑完必须把原文件原样还原（try/finally 保证）。

用例分两组：
  BASE_CASES —— 原有 22 条，覆盖红线与横截面地图真实性
  DEEP_CASES —— 新增，覆盖工序链 / 推演 / 路线 / 风险四个新增区域
"""

import io
import json
import os
import re
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from paths import SURVIVAL_MAP_HTML as TARGET  # noqa: E402
VALIDATORS = [
    os.path.join(os.path.dirname(os.path.abspath(__file__)), "validate_survival_map.py"),
    os.path.join(os.path.dirname(os.path.abspath(__file__)), "validate_deep_model.py"),
]


def _load_real_values():
    """从当前页面里读出真实的数值，作为篡改注入串的基准。

    为什么必须动态取：硬编码的数字一旦上游数据变更就会失配，
    注入替换「没生效」→ 用例看起来通过，其实什么都没测。
    这是上一轮 4 条用例漏过的真实原因。
    """
    html = io.open(TARGET, encoding="utf-8").read()
    m = re.search(r"const MODEL = (\{.*?\});\n", html, re.S)
    if not m:
        raise SystemExit("未找到内联 MODEL 数据，无法定位注入基准值")
    model = json.loads(m.group(1))
    # 选一个非变现位次作为基准（素材位次有 material，渠道位次 material=0）
    for key, role in model["roles"].items():
        if role.get("material"):
            ue = role.get("unit_econ") or {}
            return {
                "area": role["area"],
                "material": role["material"],
                "residual_minutes": ue.get("residual_minutes"),
                "total_minutes": ue.get("total_minutes"),
                "pieces_per_month": ue.get("pieces_per_month"),
            }
    raise SystemExit("未找到带素材的位次，无法定位注入基准值")


_REAL = _load_real_values()

# 用例名 -> (注入片段, 替换模式)
#   替换模式 "append"：在 </body> 前插入片段
#   替换模式 "replace_all"：把 old 全部替换为 new
#   替换模式 "replace_one"：把 old 的第一次出现替换为 new
BASE_CASES = [
    ("微信号", "append", None, '<div>微信：wellness2026</div>'),
    ("外链", "append", None, '<div>详情见 https://example.com/x</div>'),
    ("二维码", "append", None, '<div>扫描二维码进群</div>'),
    ("手机号", "append", None, '<div>联系电话 13800138000</div>'),
    ("公众号", "append", None, '<div>公众号：养生日常</div>'),
    ("邮箱", "append", None, '<div>邮箱 a@example.com</div>'),
    ("购物导流", "append", None, '<div>立即购买养生年卡</div>'),
    ("功效断言", "append", None, '<div>本图所示内容可祛湿化痰</div>'),
    ("病名", "append", None, '<div>适合糖尿病与高血压人群</div>'),
    ("问询诱导", "append", None, '<div>你最近哪里不舒服</div>'),
    ("特定人群", "append", None, '<div>孕妇与小儿慎用</div>'),
    ("侵入项目", "append", None, '<div>可配合针灸推拿</div>'),
    ("削弱免责", "append", None, '<div>仅供参考，无需就医</div>'),
    ("破坏免责", "replace_all", ("不构成诊断或治疗建议", "仅供参考，自行判断"), None),
    ("删除一处免责", "replace_one",
     ("不构成诊断或治疗建议；身体不适请至正规医疗机构就诊。", ""), None),
    ("外链资源", "append", None, '<script src="https://cdn.x.com/a.js"></script>'),
    # v3 面积标注格式为「月产 N 件 · 独占素材 M 条」
    ("虚假面积", "append", None,
     '<div class="tm-area">月产 9999 件 · 独占素材 9999 条</div>'),
    ("虚假工具率", "append", None, '<div>工具化 99%</div>'),
    # 真正的象限篡改：把某位次的象限名换成另一个合法象限，
    # 让读者以为它处在更先进的阶段。校验器必须发现数据层与页面不符。
    ("篡改象限归属", "replace_one",
     ('"quadrant": "tool_zone"', '"quadrant": "system_zone"'), None),
    ("篡改工具化率", "replace_one", ('"rate": 80', '"rate": 100'), None),
    ("删treemap方块", "replace_all", ('class="tm-cell"', 'class="tm-cell-x"'), None),
]

# 新增区域用例：针对工序链、推演、路线、风险
DEEP_CASES = [
    # ① 推演区塞入收入承诺
    ("推演收入承诺", "append", None,
     '<div>按此推演，预计月入 5 万</div>'),
    ("收益承诺", "append", None,
     '<div>保底收入 8000 元/月</div>'),
    # ② 篡改单位经济数字（页面与数据层必须对得上）
    #    注意：内联 JSON 使用紧凑分隔符（无空格），注入串须与之一致。
    #    取值在运行时从真实数据里取，避免数据变更后用例失效（失效=测了个寂寞）。
    ("篡改残余工时", "replace_one", (f'"residual_minutes":{_REAL["residual_minutes"]}',
                                     '"residual_minutes":999'), None),
    ("篡改单件总工时", "replace_one", (f'"total_minutes":{_REAL["total_minutes"]}',
                                      '"total_minutes":1'), None),
    ("篡改位次面积", "replace_one", (f'"area":{_REAL["area"]}', '"area":9999'), None),
    ("篡改月产出件数", "replace_one",
     (f'"pieces_per_month":{_REAL["pieces_per_month"]}',
      '"pieces_per_month":9999'), None),
    # ③ 破坏 v3 核心不变量：让两个位次同时独占同一主题，
    #    Σ 独占素材就会超过 205 条 —— 必须被素材守恒校验拦下
    ("破坏素材守恒", "replace_one",
     (f'"material":{_REAL["material"]}', '"material":9999'), None),
    #    把渠道位次（成品出口）也标成独占素材
    ("渠道位次独占素材", "replace_one", ('"is_channel":true', '"is_channel":false'), None),
    #    抹掉现金出口标记
    ("删现金出口标记", "replace_one", ('"is_cash":true', '"is_cash":false'), None),
    # ③ 删掉关键面板
    ("删工序链面板", "replace_all", ('id="panel-chain"', 'id="panel-chain-x"'), None),
    ("删推演面板", "replace_all", ('id="panel-sim"', 'id="panel-sim-x"'), None),
    ("删路线面板", "replace_all", ('id="panel-roadmap"', 'id="panel-roadmap-x"'), None),
    ("删风险面板", "replace_all", ('id="panel-risk"', 'id="panel-risk-x"'), None),
    # ④ 删推演引擎（页面将无法离线运行）
    ("删推演引擎", "replace_all", ('const SIM = (function', 'const SIM_X = (function'), None),
    ("删MODEL数据", "replace_all", ('const MODEL = {', 'const MODEL_X = {'), None),
    # ⑤ 篡改有效产出系数（产能会失真）
    #    注意：内联 JSON 使用紧凑分隔符（无空格），注入串须与之一致
    ("篡改产出系数", "replace_one", ('"effective_factor":0.55', '"effective_factor":1'), None),
    # ⑥ 把工时口径改成「实测」冒充实测
    ("冒充实测工时", "replace_all",
     ("工时为口径值（非实测）", "工时为实测数据"), None),
    # ⑦ 删掉「不含收入预测」的声明
    ("删收入声明", "replace_all", ("不做收入预测", "暂不涉及"), None),
    # ⑧ 路线图的出口条件被抽掉
    ("删出口条件", "replace_all", ("出口条件：", "说明："), None),
    # ⑨ 风险判据的阈值被抹掉
    ("删风险阈值", "replace_all", ("判定阈值", "参考项"), None),
    # ⑩ 篡改瓶颈阈值（会改变瓶颈判定）
    ("篡改瓶颈阈值", "replace_one", ('"bottleneck_threshold":25', '"bottleneck_threshold":80'), None),
    # ⑪ 首屏预渲染指向不存在的位次（首屏空白，且不会报任何错）
    #     这类 bug 最隐蔽：无头测试若只测计算不测渲染就会漏掉。
    ("首屏位次失效", "replace_one",
     ("renderChain(MODEL.order[0])", "renderChain('nonexistent_role')"), None),    # ⑪ 篡改周可用工时
    ("篡改周工时", "replace_one", ('"weekly_focus_hours":24', '"weekly_focus_hours":100'), None),
]

CASES = BASE_CASES + DEEP_CASES


def run_validators():
    """跑全部校验器，返回 (是否发现问题, 首个问题描述)。"""
    for v in VALIDATORS:
        r = subprocess.run(
            [sys.executable, v], capture_output=True, text=True, encoding="utf-8"
        )
        out = r.stdout
        if "✗" in out:
            detail = [
                l.strip() for l in out.split("\n")
                if l.strip().startswith("✗ ") and "发现" not in l
            ]
            return True, (detail[0][2:78] if detail else "校验器报错")
    return False, "← 漏过"


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    original = open(TARGET, encoding="utf-8").read()
    ok = 0
    print("═" * 62)
    print("养生一人公司生存地图 · 注入测试")
    print(f"═" * 62)
    print(f"  横截面用例 {len(BASE_CASES)} 条 · 深度模型用例 {len(DEEP_CASES)} 条\n")
    try:
        for name, mode, args, frag in CASES:
            if mode == "append":
                content = original.replace("</body>", frag + "\n</body>")
            elif mode == "replace_all":
                content = original.replace(args[0], args[1])
            elif mode == "replace_one":
                content = original.replace(args[0], args[1], 1)
            else:
                content = original
            with open(TARGET, "w", encoding="utf-8") as f:
                f.write(content)
            caught, msg = run_validators()
            ok += caught
            mark = "✅" if caught else "❌"
            print(f"  {mark} {name:14s} {msg}")
    finally:
        with open(TARGET, "w", encoding="utf-8") as f:
            f.write(original)
        print("\n  已还原原文件")

    # 还原后必须仍然通过
    caught, msg = run_validators()
    passed = not caught
    print(f"\n  拦截率 {ok}/{len(CASES)}")
    print(f"  还原后校验：{'✅ 通过' if passed else '❌ 未通过'}")
    return 0 if (ok == len(CASES) and passed) else 1


if __name__ == "__main__":
    sys.exit(main())
