# 第 4 步：验收清单

每完成一项打一个勾。任何一项不过，先回到对应文档排查，别跳过。

## A. 本机自测（不依赖任何其他设备）

- [ ] `agentctl --version` 能打印版本号
- [ ] `agentctl devices` 里 `localhost` 显示 ✅ 在线
- [ ] `agentctl exec localhost "echo hello"` 输出 hello
- [ ] `agentctl agent run localhost kimi "用一句话介绍你自己"` 启动成功
- [ ] `agentctl agent logs localhost <会话名>` 能看到 Kimi 的输出
- [ ] `agentctl agent send localhost <会话名> "再说一句"` 能追加输入，`agent logs` 能看到新内容
- [ ] `agentctl agent stop localhost <会话名>` 能结束会话

## B. 组网（Tailscale）

- [ ] 本机 `ping -c 3 <异地Mac的100.x地址>` 有回复
- [ ] iPhone 连上 Tailscale 后，Safari 打开 https://login.tailscale.com/admin/machines 能看到所有设备在线

## C. 远程控制（SSH）

- [ ] `ssh yansong@<异地Mac地址> "echo 免密成功"` 不问密码直接成功
- [ ] `agentctl devices` 里异地 Mac 显示 ✅ 在线
- [ ] `agentctl exec mac-mini "uname -a"` 返回异地 Mac 的系统信息

## D. 远程 Agent 调度（核心场景）

- [ ] `agentctl agent run mac-mini kimi "总结 ~/agent-workspace 里的文件"` 启动成功
- [ ] `agentctl agent sessions mac-mini` 能看到该会话
- [ ] `agentctl agent logs mac-mini <会话名>` 能看到 Kimi 正在/已经输出
- [ ] **断线续传**：启动一个长任务后，关掉本机终端，重新打开，`agent logs` 依然能看到任务在继续
- [ ] `agentctl agent attach mac-mini <会话名>` 能进入会话手动输入（按 Ctrl+B 再按 D 退出）
- [ ] `agentctl agent send mac-mini <会话名> "继续补充"` 后 `agent logs` 能看到新输入被追加执行（多轮对话）
- [ ] `agentctl agent stop mac-mini <会话名>` 后 `agent sessions` 里会话消失

## E. 移动端

- [ ] iPhone 用 Termius/Blink SSH 到异地 Mac，执行 `agentctl devices` 成功
- [ ] iPad 用 Safari 打开 `http://<异地Mac地址>:7681`，输入账号密码后出现终端
- [ ] 在 iPad 网页终端里执行 `agentctl agent logs mac-mini <会话名>` 看到输出

## 全部通过 = 系统上线 🎉

之后日常使用就是三件事：
1. `agentctl devices` 看谁在线；
2. `agentctl agent run <设备> <agent> "<任务>"` 派活；
3. `agentctl agent logs <设备> <会话>` 收结果。
