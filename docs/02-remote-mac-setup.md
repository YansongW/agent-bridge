# 第 2 步：异地 Mac 初始化（开远程登录 + 装软件 + 免密 SSH）

## 这一步在干嘛

让异地 Mac 具备三个能力：
1. **接收命令**（开启 macOS 自带的 SSH 服务，苹果叫它“远程登录”）；
2. **跑长任务**（装 tmux，任务断线不丢）；
3. **认出“自己人”**（装上本机 MacBook 的公钥，实现免密、且禁用密码登录更安全）。

> 前提：异地 Mac 已完成 [第 1 步 Tailscale 组网](01-tailscale-setup.md)。

## 一、开启“远程登录”（需要在异地 Mac 上操作一次）

1. 打开 **系统设置**（System Settings）；
2. 进入 **通用 → 共享**（General → Sharing）；
3. 打开 **远程登录**（Remote Login）开关；
4. 点旁边的 ⓘ，确认“允许访问”里包含你的用户（默认“所有用户”即可）。

## 二、安装基础软件（tmux / ttyd）

把本项目的初始化脚本拷到异地 Mac 上执行。在**本机 MacBook** 终端执行（把 `yansong` 换成异地 Mac 的用户名、`100.64.0.2` 换成它的 Tailscale 地址）：

```bash
cd ~/Desktop/agent-bridge
scp scripts/setup_remote_mac.sh yansong@100.64.0.2:/tmp/
ssh yansong@100.64.0.2 'bash /tmp/setup_remote_mac.sh'
```

第一次 `ssh` 会问两件事：
1. `Are you sure you want to continue connecting?` → 输入 `yes` 回车（记录主机指纹）；
2. `password:` → 输入**异地 Mac 的开机密码**（输入时屏幕不显示，正常）。

脚本会自动装 tmux 和 ttyd、建好 `~/agent-workspace` 目录。如果它提示没有 Homebrew，先在异地 Mac 上按 https://brew.sh 首页那行命令安装 Homebrew，再重新跑脚本。

## 三、配置免密 SSH（本机操作）

本机已经生成了密钥对（`~/.ssh/id_ed25519` / `.pub`）。把**公钥**装到异地 Mac 上：

```bash
ssh-copy-id -i ~/.ssh/id_ed25519.pub yansong@100.64.0.2
```

输入一次异地 Mac 的密码后，验证免密成功：

```bash
ssh yansong@100.64.0.2 "echo 免密成功"
```

不再问密码、直接打印“免密成功” = 搞定。

> macOS 较新版本自带 `ssh-copy-id`。如果提示没有这个命令，改用这条（效果一样）：
> ```bash
> cat ~/.ssh/id_ed25519.pub | ssh yansong@100.64.0.2 'mkdir -p ~/.ssh && chmod 700 ~/.ssh && cat >> ~/.ssh/authorized_keys && chmod 600 ~/.ssh/authorized_keys'
> ```

### （推荐）禁用密码登录，只认钥匙

免密能用之后，把异地 Mac 的 SSH 改成只接受密钥登录，挡住互联网上无穷无尽的密码猜测攻击。在异地 Mac 上编辑 `/etc/ssh/sshd_config`，把这一行：

```
#PasswordAuthentication yes
```

改成：

```
PasswordAuthentication no
```

然后重启远程登录（系统设置 → 共享 → 关掉再打开“远程登录”）。
**注意：改之前务必确认免密登录已经能用，否则会把自己锁在门外。**

## 四、把异地 Mac 登记进 agentctl

在本机编辑 `~/Desktop/agent-bridge/config/devices.toml`，照示例加上：

```toml
[mac-mini]
host = "100.64.0.2"      # 换成真实 Tailscale 地址
user = "yansong"          # 换成异地 Mac 的用户名
description = "异地 Mac mini"
```

验证：

```bash
agentctl devices
# mac-mini 显示 ✅ 在线 = 第 2 步完成
```
