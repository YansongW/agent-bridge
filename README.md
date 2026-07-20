# Agent Bridge

[English](#english) | 中文

> 从任何设备（MacBook / iPhone / iPad）用一条命令，调度异地 Mac 上的 CLI Agent（Kimi、Claude、Codex……）。

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.9%2B-blue.svg)](https://www.python.org)
[![Platform](https://img.shields.io/badge/Platform-macOS%20%7C%20iOS-lightgrey.svg)]()

## 这是什么

你有一台放在别处的 Mac（Mac mini / MacBook），和手边的 iPhone / iPad / MacBook。
Agent Bridge 让你：

- **远程下命令**：从任何设备给异地的 Mac 发 CLI 命令；
- **远程派 Agent**：让异地 Mac 上安装的 AI CLI Agent（Kimi CLI、Claude Code、Codex 等）替你干活，结果随时取回；
- **断线不丢任务**：所有 Agent 任务跑在 tmux 会话里，手机断网、合上盖子，任务照跑，回来接着看。

核心命令 `agentctl` 是纯 Python 标准库实现（3.9+，零第三方依赖），配置即数据——新增设备或 Agent 只改一个 TOML 文件，不写代码。

## 它是怎么工作的

```
iPhone / iPad ──(SSH App 或 浏览器)──┐
                                     ├──Tailscale 组网──> 异地 Mac ── sshd ── tmux ── CLI Agents
MacBook ──────(终端 + agentctl)──────┘                     (kimi / claude / codex ...)
```

| 层 | 选型 | 作用 |
|---|---|---|
| 组网 | [Tailscale](https://tailscale.com)（免费） | 让所有设备在互联网上互相找得到，加密、不暴露端口 |
| 传输 | SSH（macOS 自带） | 设备之间下命令的“水管” |
| 会话 | tmux | 任务在远程持续运行，断线不丢、随时接管 |
| 调度 | `agentctl`（本项目） | 把“在哪台设备、跑哪个 Agent、跑什么任务”变成一条命令 |

## 命令速查

```bash
agentctl devices                              # 哪些设备在线
agentctl exec mac-mini "ls ~/Documents"       # 在异地 Mac 上执行任意命令
agentctl agent list                           # 有哪些 Agent 可用
agentctl agent run mac-mini kimi "总结 ~/notes.txt"   # 派任务给异地 Mac 上的 Kimi
agentctl agent sessions mac-mini              # 正在跑的 Agent 会话
agentctl agent logs mac-mini agent-kimi-0716-153000   # 看输出
agentctl agent send mac-mini agent-kimi-0716-153000 "继续补充第二点"   # 多轮对话：追加输入（也可发 /auto 等命令）
agentctl agent attach mac-mini agent-kimi-0716-153000 # 接管会话（Ctrl+B 再按 D 退出）
agentctl agent stop mac-mini agent-kimi-0716-153000   # 结束会话
```

## 快速开始

```bash
git clone https://github.com/<你的用户名>/agent-bridge.git
cd agent-bridge
bash scripts/install.sh        # 安装 agentctl 到 ~/.local/bin
```

然后按文档顺序完成搭建（每步都有面向新手的图文说明）：

| 步骤 | 文档 |
|---|---|
| 1. Tailscale 组网（所有设备） | [docs/01-tailscale-setup.md](docs/01-tailscale-setup.md) |
| 2. 异地 Mac 初始化 + 免密 SSH | [docs/02-remote-mac-setup.md](docs/02-remote-mac-setup.md) |
| 3. iPhone / iPad 接入（SSH App + Web 终端） | [docs/03-mobile-access.md](docs/03-mobile-access.md) |
| 4. 验收清单 | [docs/04-acceptance.md](docs/04-acceptance.md) |

## 添加设备 / Agent

都是改配置，不写代码：

```toml
# config/devices.toml
[mac-mini]
host = "100.64.0.2"      # 设备的 Tailscale 地址
user = "yansong"

# config/agents.toml
[gemini]
command = "gemini"
description = "Google Gemini CLI"
```

> 真实设备清单（含内网 IP）不想公开？复制为 `config/devices.local.toml`，
> agentctl 会优先读取它，且该文件已被 `.gitignore` 排除。

## 安全说明

- 所有远程流量走 Tailscale 加密隧道，SSH 端口不暴露公网；
- SSH 只用密钥登录（文档含禁用密码登录的步骤）；
- Web 终端（ttyd）只绑定 Tailscale 内网地址 + 账号密码双重保护；
- 私钥、令牌等机密永远不会出现在本项目的文件里（见 `.gitignore` 与 [AGENTS.md](AGENTS.md) 的安全红线）。

## 贡献

欢迎 Issue 和 PR。改动约定见 [AGENTS.md](AGENTS.md)（改命令要同步文档、零依赖红线等）。

## License

[MIT](LICENSE)

---

## English

**Agent Bridge** is a small CLI (`agentctl`) that lets you run commands and drive AI CLI agents (Kimi CLI, Claude Code, Codex, …) on a remote Mac from any of your devices — MacBook, iPhone, or iPad.

- **Networking**: Tailscale (free, encrypted, no port exposure)
- **Transport**: plain SSH — no custom protocol
- **Sessions**: every agent task runs in a tmux session, so it survives disconnects and can be re-attached anytime
- **Zero dependencies**: Python 3.9+ standard library only; devices and agents are declared in TOML files, no code changes needed to add new ones

Example:

```bash
agentctl agent run mac-mini kimi "summarize ~/notes.txt"   # dispatch a task
agentctl agent logs mac-mini <session>                     # read the result
agentctl agent send mac-mini <session> "elaborate on 2nd point"  # multi-turn follow-up
agentctl agent attach mac-mini <session>                   # take over interactively
```

Setup guides (currently in Chinese, PRs for translation welcome): [docs/](docs/). Licensed under [MIT](LICENSE).
