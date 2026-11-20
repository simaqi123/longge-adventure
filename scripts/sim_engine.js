// ─────────────────────────────────────────────────────────────
// 养生一人公司 · 经营推演引擎（前端实时计算）
// ─────────────────────────────────────────────────────────────
// 输入：位次、每周投入工时、瓶颈优化力度、自动化投入
// 输出：日/周产能、瓶颈环节、盈亏平衡判断、90 天累计产出
//
// 设计约束（与数据层一致）：
//   · 不承诺收入。收入不由本引擎推算——没有真实定价与转化数据时，
//     任何收入预测都是虚构。本引擎只算「产能与工时」这两件可核验的事。
//   · 盈亏判断只做「产能是否匹配目标节奏」的判定，不输出金额。
//
// ─────────────────────────────────────────────────────────────

const SIM = (function () {

  // 从数据层取该位次的工序链与单位经济
  function chainOf(roleKey) {
    const r = MODEL.roles[roleKey];
    return r ? r.chain_steps : [];
  }

  function econOf(roleKey) {
    const r = MODEL.roles[roleKey];
    return r ? r.unit_econ : null;
  }

  /**
   * 核心推演
   * @param {string} roleKey   位次
   * @param {number} hoursPerWeek  每周投入工时（人）
   * @param {number} optRate   瓶颈优化力度 0-100（把瓶颈手工环节接进管线的比例）
   * @param {number} autoRate  自动化投入 0-100（额外投入工时用于把重复环节接进管线）
   */
  function run(roleKey, hoursPerWeek, optRate, autoRate) {
    const steps = chainOf(roleKey);
    const econ = econOf(roleKey);
    if (!steps.length || !econ) return null;

    // 1) 自动化投入的效果：把 semi 环节往前推
    //    每投入 1 单位自动化工时，可把一个 semi 环节的定稿工时压到 40%
    const autoGain = Math.round(econ.semi_minutes * (autoRate / 100) * 0.6);

    // 2) 瓶颈优化：瓶颈工序若是手工/半自动，按优化力度削减
    const bStep = steps.find(s => s.bottleneck);
    let bottleneckSaved = 0;
    let bottleneckName = bStep ? bStep.name : '—';
    if (bStep && bStep.state !== 'auto') {
      bottleneckSaved = Math.round(bStep.minutes * (optRate / 100) * 0.7);
    }

    // 3) 合成单件残余工时
    const residual = Math.max(
      1,
      econ.residual_minutes - autoGain - bottleneckSaved
    );

    // 4) 产能：投入工时中，一部分用于维持性开销
    const usableMinutes = hoursPerWeek * 60 * MODEL.config.effective_factor;
    const piecesPerWeek = usableMinutes / residual;
    const piecesPerDay = piecesPerWeek / 5;   // 按每周 5 个工作日

    // 5) 90 天累计（约 12.9 周）
    const pieces90 = piecesPerWeek * (90 / 7);

    // 6) 瓶颈重算：优化后新的最大工序
    const newSteps = steps.map(s => {
      let m = s.minutes;
      if (s.name === bottleneckName) m -= bottleneckSaved;
      if (s.state === 'semi') m -= Math.round(autoGain * (s.minutes / (econ.semi_minutes || 1)));
      return { name: s.name, minutes: Math.max(1, m), state: s.state };
    });
    const top = newSteps.reduce((a, b) => (b.minutes > a.minutes ? b : a), newSteps[0]);
    const totalNew = newSteps.reduce((s, x) => s + x.minutes, 0);

    // 7) 健康度判定（基于可核验的结构指标）
    const manualCount = steps.filter(s => s.state === 'manual').length;
    const health = judge(steps, optRate, autoRate, manualCount);

    // 8) 节奏可行性：能否支撑一个现实的内容节奏
    const cadence = cadenceJudge(piecesPerWeek);

    return {
      roleKey,
      unit: econ.unit,
      residualMinutes: residual,
      baselineResidual: econ.residual_minutes,
      savedMinutes: (econ.residual_minutes - residual),
      usableMinutes: Math.round(usableMinutes),
      piecesPerWeek: Math.round(piecesPerWeek * 10) / 10,
      piecesPerDay: Math.round(piecesPerDay * 10) / 10,
      pieces90: Math.round(pieces90),
      bottleneckName,
      bottleneckSaved,
      newBottleneck: top.name,
      newBottleneckShare: Math.round(top.minutes / totalNew * 100),
      steps: newSteps.map(s => ({
        ...s,
        share: Math.round(s.minutes / totalNew * 100),
      })),
      health,
      cadence,
    };
  }

  // 健康度：只依据结构事实，不给主观打分
  function judge(steps, optRate, autoRate, manualCount) {
    const issues = [];
    if (manualCount >= 2) {
      issues.push({
        level: 'warn',
        text: `仍有 ${manualCount} 个纯手工环节，单点依赖偏高，一人公司的产能会随状态波动`,
      });
    }
    if (optRate < 40) {
      issues.push({
        level: 'warn',
        text: '瓶颈工序优化力度不足 40%，最大工序仍会吃掉大部分精力',
      });
    }
    if (autoRate < 30) {
      issues.push({
        level: 'info',
        text: '自动化投入偏低，半自动环节的定稿工时未被压缩',
      });
    }
    const autoSteps = steps.filter(s => s.state === 'auto').length;
    if (autoSteps / steps.length >= 0.5) {
      issues.push({
        level: 'good',
        text: `已进管线环节占 ${Math.round(autoSteps / steps.length * 100)}%，素材供给端已可重跑`,
      });
    }
    if (!issues.length) {
      issues.push({ level: 'info', text: '结构上尚未发现明显短板，先按当前参数试跑一轮' });
    }
    return issues;
  }

  // 节奏判定：产能是否够一个现实的内容节奏
  function cadenceJudge(piecesPerWeek) {
    if (piecesPerWeek >= 20) {
      return { level: 'good', text: `周产 ${Math.round(piecesPerWeek)} 件，可支撑高频日更` };
    }
    if (piecesPerWeek >= 8) {
      return { level: 'good', text: `周产 ${Math.round(piecesPerWeek)} 件，可支撑每周 2–3 更的稳定节奏` };
    }
    if (piecesPerWeek >= 3) {
      return { level: 'warn', text: `周产 ${Math.round(piecesPerWeek)} 件，属低频更新，需靠质量而非数量取胜` };
    }
    return { level: 'bad', text: `周产仅 ${Math.round(piecesPerWeek)} 件，节奏过密会牺牲质量，建议降频` };
  }

  return { run };
})();
