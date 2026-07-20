"""agentctl 命令行入口。

子命令总览：
  agentctl devices                          列出设备与在线状态
  agentctl exec <设备> <命令...>            在设备上执行命令
  agentctl agent list                       列出可用 Agent
  agentctl agent run <设备> <agent> [任务]  启动一个远程 Agent 会话
  agentctl agent sessions <设备>            列出设备上的 Agent 会话
  agentctl agent logs <设备> <会话> [-n N]  查看会话输出
  agentctl agent send <设备> <会话> <文本...>  往会话里追加输入（多轮对话）
  agentctl agent attach <设备> <会话>       接管会话（交互式）
  agentctl agent stop <设备> <会话>         结束会话
"""

import argparse
import sys

from . import __version__, agents, config, devices as devices_mod, remote


def cmd_devices(_args):
    devs = config.load_devices()
    if not devs:
        print("设备清单为空，请编辑 config/devices.toml")
        return 0
    print(f"{'设备':<14}{'地址':<18}{'状态'}")
    print("-" * 50)
    for name, dev, online, note in devices_mod.probe_all(devs):
        host = dev.get("host", "?")
        status = "✅ 在线" if online else f"❌ {note}"
        print(f"{name:<14}{host:<18}{status}")
        if dev.get("description"):
            print(f"{'':<14}{dev['description']}")
    return 0


def cmd_exec(args):
    dev = config.get_device(args.device)
    command = " ".join(args.command)
    rc, out = remote.run(dev, command, timeout=300)
    if out:
        print(out)
    if rc != 0:
        print(f"[退出码 {rc}]", file=sys.stderr)
    return rc


def cmd_agent_list(_args):
    agents_cfg = config.load_agents()
    if not agents_cfg:
        print("Agent 清单为空，请编辑 config/agents.toml")
        return 0
    print(f"{'Agent':<14}{'启动命令':<20}{'说明'}")
    print("-" * 50)
    for name, a in agents_cfg.items():
        print(f"{name:<14}{a.get('command', '?'):<20}{a.get('description', '')}")
    return 0


def cmd_agent_run(args):
    dev = config.get_device(args.device)
    agent = config.get_agent(args.agent)
    agent["_name"] = args.agent
    prompt = " ".join(args.prompt)
    ok, msg = agents.start(dev, agent, prompt)
    if not ok:
        print(f"启动失败：{msg}", file=sys.stderr)
        return 1
    print(f"已启动会话：{msg}")
    print(f"查看输出：agentctl agent logs {args.device} {msg}")
    print(f"接管会话：agentctl agent attach {args.device} {msg}")
    return 0


def cmd_agent_sessions(args):
    dev = config.get_device(args.device)
    sessions = agents.list_sessions(dev)
    if not sessions:
        print("该设备上当前没有 tmux 会话")
        return 0
    for _name, line in sessions:
        print(line)
    return 0


def cmd_agent_logs(args):
    dev = config.get_device(args.device)
    ok, out = agents.logs(dev, args.session, lines=args.lines)
    if not ok:
        print(f"读取失败：{out}", file=sys.stderr)
        return 1
    print(out)
    return 0


def cmd_agent_attach(args):
    dev = config.get_device(args.device)
    agents.attach(dev, args.session)  # 不返回
    return 0


def cmd_agent_send(args):
    dev = config.get_device(args.device)
    text = " ".join(args.text)
    ok, msg = agents.send(dev, args.session, text)
    print(msg)
    return 0 if ok else 1


def cmd_agent_stop(args):
    dev = config.get_device(args.device)
    ok, msg = agents.stop(dev, args.session)
    print(msg)
    return 0 if ok else 1


def build_parser():
    p = argparse.ArgumentParser(
        prog="agentctl",
        description="多设备 CLI 互通与远程 CLI Agent 调度工具",
    )
    p.add_argument("--version", action="version", version=f"agentctl {__version__}")
    sub = p.add_subparsers(dest="cmd", required=True)

    sp = sub.add_parser("devices", help="列出设备与在线状态")
    sp.set_defaults(func=cmd_devices)

    sp = sub.add_parser("exec", help="在设备上执行命令")
    sp.add_argument("device", help="设备名（见 config/devices.toml）")
    sp.add_argument("command", nargs=argparse.REMAINDER, help="要执行的命令")
    sp.set_defaults(func=cmd_exec)

    ap = sub.add_parser("agent", help="远程 Agent 调度")
    asub = ap.add_subparsers(dest="sub", required=True)

    sp = asub.add_parser("list", help="列出可用 Agent")
    sp.set_defaults(func=cmd_agent_list)

    sp = asub.add_parser("run", help="启动远程 Agent 会话")
    sp.add_argument("device")
    sp.add_argument("agent")
    sp.add_argument("prompt", nargs=argparse.REMAINDER, help="任务描述（可省略，稍后 attach 手动输入）")
    sp.set_defaults(func=cmd_agent_run)

    sp = asub.add_parser("sessions", help="列出设备上的会话")
    sp.add_argument("device")
    sp.set_defaults(func=cmd_agent_sessions)

    sp = asub.add_parser("logs", help="查看会话输出")
    sp.add_argument("device")
    sp.add_argument("session")
    sp.add_argument("-n", "--lines", type=int, default=200, help="抓取最近多少行（默认 200）")
    sp.set_defaults(func=cmd_agent_logs)

    sp = asub.add_parser("attach", help="接管会话（交互式）")
    sp.add_argument("device")
    sp.add_argument("session")
    sp.set_defaults(func=cmd_agent_attach)

    sp = asub.add_parser("send", help="往会话里追加输入（多轮对话）")
    sp.add_argument("device")
    sp.add_argument("session")
    sp.add_argument("text", nargs=argparse.REMAINDER, help="要发送的文本（/auto 这类斜杠命令也可以）")
    sp.set_defaults(func=cmd_agent_send)

    sp = asub.add_parser("stop", help="结束会话")
    sp.add_argument("device")
    sp.add_argument("session")
    sp.set_defaults(func=cmd_agent_stop)

    return p


def main(argv=None):
    args = build_parser().parse_args(argv)
    if args.cmd == "exec" and not args.command:
        sys.exit("用法：agentctl exec <设备> <命令...>")
    if args.cmd == "agent" and args.sub == "send" and not args.text:
        sys.exit("用法：agentctl agent send <设备> <会话> <文本...>")
    try:
        return args.func(args)
    except KeyboardInterrupt:
        return 130


if __name__ == "__main__":
    sys.exit(main())
