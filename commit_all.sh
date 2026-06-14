#!/bin/bash

# 切换到项目根目录
PROJECT_ROOT="/Users/groot/agent_worlds"
cd "$PROJECT_ROOT" || exit 1

echo "==== 当前工作目录：$(pwd) ===="

# 1. 查看变更文件
echo -e "\n[1] 检测代码变更"
git status

# 2. 全部加入暂存区
echo -e "\n[2] 添加所有文件到暂存"
git add .

# 3. 读取提交备注
read -p "请输入本次commit描述: " commit_msg

# 4. 执行提交
git commit -m "$commit_msg"

# 5. 推送远端（可选，注释掉就只本地commit）
echo -e "\n[3] 开始推送到远程仓库"
git push
echo "✅ 全部代码提交推送完成"