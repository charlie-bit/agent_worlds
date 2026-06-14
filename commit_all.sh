#!/bin/bash

# 切换到项目根目录（脚本所在目录，避免写死路径）
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$PROJECT_ROOT" || exit 1

echo "==== 当前工作目录：$(pwd) ===="

# 1. 查看变更文件
echo -e "\n[1] 检测代码变更"
git status

# 2. 概念图自动同步
echo -e "\n[2] 检测 agent 目录层级是否变化"

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

# 3. 全部加入暂存区
echo -e "\n[3] 添加所有文件到暂存"
git add .

# 4. 读取提交备注
read -p "请输入本次commit描述: " commit_msg

# 5. 提交
echo -e "\n[4] 提交代码"
git commit -m "$commit_msg"

if [ $? -ne 0 ]; then
    echo "❌ Commit失败"
    exit 1
fi

# 6. 推送
echo -e "\n[5] 推送到远程仓库"
git push

if [ $? -eq 0 ]; then
    echo "✅ Commit并Push成功"
else
    echo "❌ Push失败"
    exit 1
fi