#!/usr/bin/env bash
# 一键推送到 GitHub
#
# 用法：
#   bash scripts/push_to_github.sh <仓库地址>
# 例：
#   bash scripts/push_to_github.sh https://github.com/simaqi123/longge-adventure.git
#
# 说明：
#   · 需要本机已配置 GitHub 凭据（PAT 或 SSH key）
#   · 推送前会先跑一遍完整校验，任一项不过就中止

set -euo pipefail

REPO_URL="${1:-}"
if [ -z "$REPO_URL" ]; then
    echo "用法: bash scripts/push_to_github.sh <仓库地址>"
    echo "例:  bash scripts/push_to_github.sh https://github.com/simaqi123/longge-adventure.git"
    exit 1
fi

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$(cd "$HERE/.." && pwd)"
cd "$ROOT"

echo "==> 推送前校验"
python scripts/validate_ssot.py data/养生知识表.csv
python scripts/build_survival_map.py
python scripts/build_constitution_test.py
python scripts/validate_survival_map.py
python scripts/validate_deep_model.py
python scripts/validate_constitution_html.py
python scripts/test_survival_map_injection.py
python scripts/leak_scan.py

echo "==> 设置远端"
if git remote get-url origin >/dev/null 2>&1; then
    git remote set-url origin "$REPO_URL"
else
    git remote add origin "$REPO_URL"
fi

BRANCH="main"
git branch -M "$BRANCH" 2>/dev/null || true

echo "==> 提交并推送"
git add -A
git diff --cached --quiet || git commit -m "docs: 补充 AGENTS.md、CI 校验管线与泄漏扫描"
git push -u origin "$BRANCH"

echo
echo "✅ 推送完成"
echo "   仓库: $REPO_URL"
