"""Agent 调度：在目标设备的 tmux 会话里启动、查看、接管、结束 CLI Agent。

设计要点：
- 每个 Agent 任务跑在一个独立 tmux 会话里，断线不丢任务；
- 启动方式 = 先开 tmux 会话运行 Agent 命令，再用 send-keys 把任务描述
  “敲”进去——这样交互式 CLI（kimi、claude 等）都能通用，无需关心
  各自的命令行参数差异。
"""

import re
import time

from . import remote


def make_session_name(agent_name):
    """生成合法的 tmux 会话名：agent-<名字>-<时间戳>。"""
    safe = re.sub(r"[^a-zA-Z0-9_-]", "-", agent_name)
    return f"agent-{safe}-{time.strftime('%m%d-%H%M%S')}"


def start(device, agent, prompt=""):
    """启动一个远程 Agent 会话，返回 (是否成功, 会话名或错误信息)。"""
    command = agent.get("command", "").strip()
    if not command:
        return False, "Agent 配置缺少 command"
    workdir = agent.get("workdir", "").strip()
    if workdir:
        command = f"cd {remote.shq(workdir)} && {command}"
    session = make_session_name(agent.get("_name", "task"))

    rc, out = remote.run(device, f"tmux new-session -d -s {remote.shq(session)} {remote.shq(command)}")
    if rc != 0:
        if "tmux" in out and ("not found" in out or "command not found" in out):
            return False, "目标设备没装 tmux，请先运行 scripts/setup_remote_mac.sh"
        return False, f"tmux 会话创建失败：{out}"

    if prompt:
        # 等 Agent 的交互界面完全启动再输入。文字和回车分两次发：
        # 界面未就绪时回车容易丢失（实测 Kimi CLI 就出现过），
        # 文字先落进输入框、单独再补一个回车最稳。
        time.sleep(3)
        rc, out = remote.run(device, f"tmux send-keys -t {remote.shq(session)} {remote.shq(prompt)}")
        if rc == 0:
            time.sleep(1)
            rc, out = remote.run(device, f"tmux send-keys -t {remote.shq(session)} Enter")
        if rc != 0:
            return False, f"会话已创建（{session}），但发送任务描述失败：{out}"
    return True, session


def list_sessions(device):
    """列出目标设备上的 tmux 会话，返回 [(会话名, 状态行)]。"""
    rc, out = remote.run(device, "tmux ls 2>&1")
    if rc != 0:
        # “no server running” / “error connecting” = 没有会话，不是错误
        return []
    sessions = []
    for line in out.splitlines():
        if not line.strip():
            continue
        name = line.split(":", 1)[0].strip()
        sessions.append((name, line.strip()))
    return sessions


def logs(device, session, lines=200):
    """抓取会话最近输出，返回 (是否成功, 文本)。"""
    rc, out = remote.run(
        device,
        f"tmux capture-pane -p -t {remote.shq(session)} -S -{int(lines)} 2>&1",
    )
    if rc != 0:
        return False, out
    return True, out


def stop(device, session):
    """结束会话，返回 (是否成功, 说明)。"""
    rc, out = remote.run(device, f"tmux kill-session -t {remote.shq(session)} 2>&1")
    if rc != 0:
        return False, out
    return True, f"会话 {session} 已结束"


def attach(device, session):
    """接管会话（交互式，不返回）。"""
    remote.exec_interactive(device, f"tmux attach -t {remote.shq(session)}")
