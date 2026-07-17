#!/bin/bash
# 把 agentctl 安装到 ~/.local/bin（加入 PATH 后随处可用）。
set -e
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
BIN_DIR="$HOME/.local/bin"

mkdir -p "$BIN_DIR"
chmod +x "$PROJECT_ROOT/bin/agentctl"
ln -sf "$PROJECT_ROOT/bin/agentctl" "$BIN_DIR/agentctl"
echo "已安装：$BIN_DIR/agentctl -> $PROJECT_ROOT/bin/agentctl"

# 检查 PATH
case ":$PATH:" in
    *":$BIN_DIR:"*) echo "PATH 已包含 $BIN_DIR，直接输入 agentctl 即可使用。" ;;
    *)
        echo ""
        echo "注意：$BIN_DIR 还不在你的 PATH 里。请执行下面这行命令，然后重开终端："
        echo ""
        SHELL_RC="$HOME/.zshrc"
        [ -n "$BASH_VERSION" ] && SHELL_RC="$HOME/.bash_profile"
        echo "  echo 'export PATH=\"\$HOME/.local/bin:\$PATH\"' >> $SHELL_RC"
        echo ""
        echo "或者先临时用全路径：$BIN_DIR/agentctl"
        ;;
esac
