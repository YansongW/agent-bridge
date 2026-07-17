#!/bin/bash
# 异地 Mac 初始化脚本：装 tmux / ttyd、建工作目录。
#
# 用法（在本机执行，把 mac-mini 换成你的设备名或 Tailscale IP）：
#   scp scripts/setup_remote_mac.sh yansong@100.64.0.2:/tmp/
#   ssh yansong@100.64.0.2 'bash /tmp/setup_remote_mac.sh'
#
# 前提：异地 Mac 已开启“远程登录”、已装 Tailscale、已配置好免密 SSH，
# 且装有 Homebrew（脚本里用的是官方安装路径 /opt/homebrew 或 ~/homebrew 均可，
# 找不到 brew 时会提示你手动安装）。

set -e
echo "==> 检查 Homebrew"
BREW=""
for candidate in /opt/homebrew/bin/brew /usr/local/bin/brew "$HOME/homebrew/bin/brew"; do
    if [ -x "$candidate" ]; then BREW="$candidate"; break; fi
done
if [ -z "$BREW" ]; then
    echo "没有找到 Homebrew。请先在 https://brew.sh 复制安装命令装好它，再重新运行本脚本。"
    exit 1
fi
echo "    使用 $BREW"

echo "==> 安装 tmux（让 Agent 任务断线不丢）"
"$BREW" list tmux >/dev/null 2>&1 || "$BREW" install tmux

echo "==> 安装 ttyd（Web 终端，给 iPhone/iPad 浏览器用）"
"$BREW" list ttyd >/dev/null 2>&1 || "$BREW" install ttyd

echo "==> 创建 Agent 工作目录 ~/agent-workspace"
mkdir -p "$HOME/agent-workspace"

echo ""
echo "完成！这台 Mac 现在可以被 agentctl 调度了。"
echo "Web 终端（ttyd）的开机自启配置，请参考 docs/03-mobile-access.md。"
