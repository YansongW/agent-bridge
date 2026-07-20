<div align="center">

# 🌉 Agent Bridge

**从任何设备，用一条命令，调度异地 Mac 上的 AI CLI Agent。**

*Control coding agents on a remote Mac — Kimi CLI, Claude Code, Codex — from anywhere, with one command.*

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python 3.9+](https://img.shields.io/badge/Python-3.9%2B-blue.svg)](https://www.python.org)
[![Platform](https://img.shields.io/badge/Platform-macOS%20%7C%20iOS-lightgrey.svg)]()
[![Dependencies](https://img.shields.io/badge/Dependencies-Zero-brightgreen.svg)]()

[English](#english) · [快速开始](#-快速开始) · [命令参考](#-命令参考) · [文档](#-文档)

</div>

---

## ✨ 特性

- **一条命令派任务**：`agentctl agent run mac-mini kimi "总结 ~/notes.txt"`，任务即刻在异地 Mac 上开跑。
- **断线不丢任务**：所有 Agent 跑在 tmux 会话里。手机断网、合上盖子、地铁没信号——任务照跑，回来接着看。
- **多轮对话**：`agent send` 往同一个会话里持续追问，也能原样发送 `/auto` 这类斜杠命令，像坐在远程终端前一样。
- **任意 Agent，零适配**：Kimi CLI、Claude Code、Codex……只要是交互式 CLI，往 TOML 里加两行就能调度，不需要任何插件或 API Key。
- **零依赖**：`agentctl` 纯 Python 标准库实现（3.9+），克隆下来就能跑，远程机器不需要装任何 agent-bridge 组件。
- **默认安全**：Tailscale 加密组网 + 仅密钥 SSH，不暴露任何公网端口；真实设备清单可放入 gitignore 的本地配置。

## 🎬 30 秒看懂

```console
$ agentctl devices
设备            地址                状态
--------------------------------------------------
localhost     127.0.0.1         ✅ 在线
mac-mini      100.102.58.80     ✅ 在线

$ agentctl agent run mac-mini kimi "总结 ~/agent-workspace 里的会议纪要"
已启动会话：agent-kimi-0720-124810

$ agentctl agent logs mac-mini agent-kimi-0720-124810
● 会议纪要共 3 份，核心结论如下：……

$ agentctl agent send mac-mini agent-kimi-0720-124810 "把结论整理成待办清单"
已发送到会话 agent-kimi-0720-124810
```

合上盖子去吃饭？没关系。回来后 `agent logs` 接着看，`agent attach` 还能亲自接管。

## 🧠 工作原理

不造新轮子，把四个成熟工具串成一条线：

```
iPhone / iPad ──(SSH App / 浏览器)──┐
                                    ├── Tailscale 加密组网 ──> 异地 Mac ── sshd ── tmux ── CLI Agents
MacBook ──────(终端 + agentctl)─────┘                                (kimi / claude / codex …)
```

| 层 | 选型 | 职责 |
|---|---|---|
| 组网 | [Tailscale](https://tailscale.com/)（免费） | 设备互访，WireGuard 加密，零端口暴露 |
| 传输 | SSH（macOS 自带） | 命令下发与结果回传 |
| 会话 | tmux | 任务常驻运行，断线不丢、随时接管 |
| 调度 | `agentctl`（本项目） | 「在哪台设备、跑哪个 Agent、跑什么任务」一条命令说清楚 |

派发一个任务时，`agentctl` 通过 SSH 在远程 Mac 上创建 tmux 会话、启动 Agent CLI，再用 `send-keys` 把任务描述"敲"进去——所以**任何交互式 CLI 都能被调度**，无需关心各自的启动参数。

## 🚀 快速开始

**环境要求**

| 角色 | 要求 |
|---|---|
| 控制端 | macOS（iPhone / iPad 用 SSH App 或浏览器亦可） |
| 被控端 | macOS + Homebrew；tmux 与 ttyd 由初始化脚本自动安装 |
| 网络 | 一个免费的 [Tailscale](https://tailscale.com/) 账号 |

**安装**

```bash
git clone https://github.com/YansongW/agent-bridge.git
cd agent-bridge
bash scripts/install.sh        # 安装 agentctl 到 ~/.local/bin
```

然后按文档顺序完成组网与被控端初始化（每步都有面向新手的图文说明，全程约 30 分钟）：

1. [Tailscale 组网](docs/01-tailscale-setup.md)
2. [异地 Mac 初始化 + 免密 SSH](docs/02-remote-mac-setup.md)
3. [iPhone / iPad 接入](docs/03-mobile-access.md)（可选）
4. [验收清单](docs/04-acceptance.md)

**本机 30 秒自测**（不依赖任何其他设备）：

```bash
agentctl exec localhost "echo hello"          # hello
agentctl agent run localhost demo "测试"       # demo agent 原样回显，不消耗任何 API
agentctl agent logs localhost <会话名>
```

## 📖 命令参考

| 命令 | 说明 |
|---|---|
| `agentctl devices` | 列出所有设备与在线状态 |
| `agentctl exec <设备> <命令>` | 在设备上执行任意命令 |
| `agentctl agent list` | 列出可调度的 Agent |
| `agentctl agent run <设备> <Agent> [任务]` | 启动 Agent 会话并派发任务 |
| `agentctl agent sessions <设备>` | 列出设备上运行中的会话 |
| `agentctl agent logs <设备> <会话> [-n N]` | 查看会话输出（默认最近 200 行） |
| `agentctl agent send <设备> <会话> <文本>` | 往会话追加输入（多轮对话 / `/auto` 等斜杠命令） |
| `agentctl agent attach <设备> <会话>` | 亲自接管会话（退出：`Ctrl+B` 再按 `D`） |
| `agentctl agent stop <设备> <会话>` | 结束会话 |

## ⚙️ 配置

设备与 Agent 都是**纯数据**，改 TOML 即可，不用碰代码：

```toml
# config/devices.toml
[mac-mini]
host = "100.64.0.2"      # 设备的 Tailscale 地址
user = "yansong"

# config/agents.toml
[kimi]
command = "kimi"
description = "Kimi CLI"
```

> **私有设备清单**：含真实内网地址的配置请放到 `config/devices.local.toml`——
> `agentctl` 优先读取它，且该文件已被 `.gitignore` 排除，永远不会进 git。

## 🔒 安全设计

- 全部远程流量走 Tailscale（WireGuard）加密隧道，SSH 端口不暴露公网；
- SSH 仅密钥登录，[文档提供禁用密码登录的步骤](docs/02-remote-mac-setup.md)；
- Web 终端（ttyd）只绑定 Tailscale 内网地址，账号密码双重保护；
- 私钥、令牌等机密永远不会出现在本仓库（见 `.gitignore` 与 [AGENTS.md](AGENTS.md) 安全红线）。

## 📚 文档

| 文档 | 内容 |
|---|---|
| [docs/01-tailscale-setup.md](docs/01-tailscale-setup.md) | 所有设备的 Tailscale 组网 |
| [docs/02-remote-mac-setup.md](docs/02-remote-mac-setup.md) | 被控端初始化：远程登录 / tmux / 免密 SSH |
| [docs/03-mobile-access.md](docs/03-mobile-access.md) | iPhone / iPad 接入（SSH App + Web 终端） |
| [docs/04-acceptance.md](docs/04-acceptance.md) | 验收清单 |
| [AGENTS.md](AGENTS.md) | 项目约定（给协助开发的 AI 与贡献者） |

## 🤝 贡献

欢迎 Issue 和 PR。改动约定见 [AGENTS.md](AGENTS.md)：改命令要同步文档、零第三方依赖是不可逾越的红线。

## 📄 License

[MIT](LICENSE) © YansongW

---

## English

**Agent Bridge** is a zero-dependency CLI (`agentctl`) that lets you dispatch tasks to AI coding agents (Kimi CLI, Claude Code, Codex, …) running on a remote Mac — from your MacBook, iPhone, or iPad.

It deliberately builds nothing new on the network layer: **Tailscale** for encrypted mesh networking, **SSH** for transport, **tmux** for disconnect-proof sessions. `agentctl` is the glue that turns "which device, which agent, what task" into a single command.

### Features

- **One-command dispatch** — `agentctl agent run mac-mini kimi "summarize ~/notes.txt"`
- **Survives disconnects** — every task runs in tmux; close the lid, come back later, the task is still going
- **Multi-turn sessions** — `agent send` follows up in the same session, and forwards slash commands like `/auto` verbatim
- **Any interactive CLI works** — declare it in TOML and it's schedulable; no plugins, no API keys
- **Zero dependencies** — Python 3.9+ standard library only; nothing to install on the remote side beyond tmux
- **Secure by default** — WireGuard-encrypted mesh, key-only SSH, no public ports

### Quick start

```bash
git clone https://github.com/YansongW/agent-bridge.git
cd agent-bridge
bash scripts/install.sh
```

Then follow the step-by-step guides in [docs/](docs/) (currently in Chinese — translations welcome). Requirements: macOS on both ends, Homebrew on the remote Mac, a free Tailscale account.

### Usage

```bash
agentctl devices                                    # who's online
agentctl exec mac-mini "ls ~/Documents"             # run any command remotely
agentctl agent run mac-mini kimi "summarize notes"  # dispatch a task
agentctl agent logs mac-mini <session>              # read the result
agentctl agent send mac-mini <session> "go on"      # multi-turn follow-up
agentctl agent attach mac-mini <session>            # take over (Ctrl+B, D to detach)
agentctl agent stop mac-mini <session>              # terminate
```

Devices and agents are declared in plain TOML (`config/*.toml`). Put real device inventories in `config/devices.local.toml` — it's read first and git-ignored.

Licensed under [MIT](LICENSE).
