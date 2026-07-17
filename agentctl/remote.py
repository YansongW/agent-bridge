"""SSH 远程执行封装。

设备配置里 local = true 的条目直接在本机执行，不走 SSH（用于回环测试）。
SSH 使用 BatchMode（免密密钥登录），不会卡在密码提示上。
"""

import shlex
import subprocess

SSH_OPTS = [
    "-o", "BatchMode=yes",        # 只接受密钥登录，绝不交互式问密码
    "-o", "ConnectTimeout=5",     # 连接超时 5 秒，挂了快速报错
    "-o", "StrictHostKeyChecking=accept-new",  # 首次连接自动记录主机指纹
]

# SSH 非交互执行时不会读取 .zshrc/.bash_profile，PATH 里常常没有
# Homebrew / miniconda / ~/.local/bin，导致 tmux、kimi 等命令“找不到”。
# 所以每条远程命令前都先补齐常见安装位置（存在的目录才会生效，无副作用）。
PATH_SETUP = (
    'export PATH="$HOME/.local/bin:$HOME/homebrew/bin'
    ':/opt/homebrew/bin:/usr/local/bin:$HOME/miniconda3/bin:$PATH"'
)


def is_local(device):
    return bool(device.get("local"))


def ssh_target(device):
    user = device.get("user", "").strip()
    host = device.get("host", "").strip()
    if not host:
        raise ValueError("设备配置缺少 host")
    return f"{user}@{host}" if user else host


def run(device, command, timeout=60):
    """在目标设备上执行命令，返回 (退出码, 输出文本)。

    command 是一个字符串，会在目标的 shell 里执行（已自动补齐 PATH）。
    """
    full_command = f"{PATH_SETUP}; {command}"
    if is_local(device):
        argv = ["bash", "-lc", full_command]
    else:
        argv = ["ssh", *SSH_OPTS, ssh_target(device), full_command]
    try:
        proc = subprocess.run(
            argv, capture_output=True, text=True, timeout=timeout,
        )
    except subprocess.TimeoutExpired:
        return 124, f"命令执行超时（>{timeout} 秒）"
    except FileNotFoundError:
        return 127, "找不到 ssh 命令"
    output = (proc.stdout + proc.stderr).strip()
    return proc.returncode, output


def check_online(device, timeout=5):
    """探测设备是否可执行命令。返回 (是否在线, 说明)。"""
    rc, out = run(device, "echo agentctl-ok", timeout=timeout)
    if rc == 0 and "agentctl-ok" in out:
        return True, "在线"
    if rc == 255:
        return False, "SSH 连不上（检查 Tailscale 是否在线、远程登录是否开启）"
    if rc == 124:
        return False, "连接超时"
    return False, f"异常（退出码 {rc}）：{out[:120]}"


def exec_interactive(device, command):
    """把当前终端交给一个交互式 SSH 会话（用于 agent attach）。此函数不返回。"""
    import os
    if is_local(device):
        os.execvp("bash", ["bash", "-lc", command])
    argv = ["ssh", *SSH_OPTS, "-t", ssh_target(device), command]
    os.execvp("ssh", argv)


def shq(s):
    """shell 引号转义的快捷方式。"""
    return shlex.quote(s)
