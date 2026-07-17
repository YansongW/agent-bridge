# AGENTS.md — 项目约定（给协助开发的 AI 看）

## 项目是什么

`agentctl`：多设备 CLI 互通与远程 CLI Agent 调度工具。
通过 SSH 在远程 Mac 的 tmux 会话里启动交互式 CLI Agent（kimi、claude、codex 等），
实现“断线不丢任务、随时接管”的远程调度。组网依赖 Tailscale，不自己造网络层。

## 技术栈与约束

- Python 3，**只用标准库**（argparse / subprocess / tomllib / shlex）。
  不引入第三方依赖——远程 Mac 可能只有系统 Python 3.9，config.py 内置了
  TOML 迷你解析器作为回退，新增配置语法时必须保持迷你解析器能解析。
- 远程执行一律走 `remote.run()`（BatchMode 免密 SSH），不要发明新的通道。
- 设备与 Agent 都是**数据驱动**：新增设备/Agent 只改 `config/*.toml`，不改代码。
  不要为某个具体 Agent 写专门的代码分支。
- 用户是非计算机专业背景：错误信息用中文、给出下一步该做什么，不要只抛异常。

## 结构

```
bin/agentctl        入口包装脚本（解析软链、选 Python、设 PYTHONPATH）
agentctl/cli.py     子命令定义与分发
agentctl/config.py  配置加载（含迷你 TOML 解析器）
agentctl/devices.py 设备探测
agentctl/remote.py  SSH/本地执行封装
agentctl/agents.py  tmux 会话生命周期（start/logs/attach/stop/list）
config/*.toml       设备清单、Agent 清单
scripts/            安装与远程初始化脚本
docs/               面向非技术用户的操作文档
```

## 修改守则

- 改了命令/子命令 → 同步更新 README.md 命令速查 和 docs/04-acceptance.md 验收项。
- 改了配置格式 → 同步更新 config/*.toml 注释、docs 和 config.py 迷你解析器。
- 改了搭建流程 → 同步更新 docs/01-03。
- 测试方式：本机回环（`localhost` 设备，local=true 不走 SSH），
  至少跑通 `devices / exec / agent run / logs / stop`。

## 安全红线

- 私钥、TOKEN 等机密**绝不写入仓库或配置模板**；模板里只放占位符。
- 生成或展示任何“可复制执行”的脚本时，不得包含真实私钥内容。
- ttyd 等 Web 服务只绑定 Tailscale 内网地址，禁止绑定 0.0.0.0。
