#!/bin/bash

# 切换到项目根目录（脚本所在目录，避免写死路径）
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$PROJECT_ROOT" || exit 1

echo "==== 当前工作目录：$(pwd) ===="

# 1. 查看变更文件
echo -e "\n[1] 检测代码变更"
git status

# 2. 概念图自动同步
#    generate_concept.py 的输入只取决于 agents/<world>/*/README.md
#    （扫目录 + 读每个 README 的 H1 与首句简介）。
#    只要 agents/ 下任一 README.md 有增/删/改，概念图就可能过期 -> 自动重跑。
echo -e "\n[2] 检测 agent 目录层级是否变化"
# 只匹配 agents/<world>/<agent>/README.md（恰好一层 agent 目录），
# 与 generate_concept.py 的 glob 层级一致；排除 <域>-system/ 里的占位 README。
if git status --porcelain -- agents/ | grep -qE '\bagents/[^/]+/[^/]+/README\.md$'; then
    echo "  检测到 agent README 变动，重新生成概念图..."
    if python3 "$PROJECT_ROOT/diagrams/generate_concept.py"; then
        echo "  ✅ 概念图已刷新 (diagrams/concept.svg)"
    else
        echo "  ⚠️  概念图生成失败，请检查 generate_concept.py" >&2
    fi
else
    echo "  无 agent 层级变化，跳过。"
fi

# 3. 全部加入暂存区（含刚刷新的 concept.svg）
echo -e "\n[3] 添加所有文件到暂存"
git add .

# 4. 读取提交备注
read -p "请输入本次commit描述: " commit_msg

# 5. 执行提交（只本地 commit，不自动 push —— 推送由人工把控）
git commit -m "$commit_msg"
echo "✅ 已本地提交。如需推送，手动执行：git push"
