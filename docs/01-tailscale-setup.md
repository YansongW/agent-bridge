# 第 1 步：用 Tailscale 把所有设备组成一个“虚拟局域网”

## 这一步在干嘛

你的设备分散在不同地方、不同网络里，正常情况下互相“看不见”。
Tailscale 是一个免费工具：每台设备装上它、登录同一个账号后，它们就像插在了同一个路由器上，各自得到一个固定地址（`100.x.x.x` 开头），随时随地互相访问，全程加密。

**费用：免费**（个人版最多 100 台设备、3 个用户，绰绰有余）。

## 需要准备

- 一个用于登录 Tailscale 的账号：Google、Microsoft、GitHub 或 Apple 账号均可（建议用你常用的那个，所有设备用**同一个**账号登录）；
- 每台设备 10 分钟。

## 每台 Mac 上的操作（本机 MacBook + 异地 Mac）

1. 打开 App Store，搜索 **Tailscale** 并安装（也可以去 https://tailscale.com/download/mac 下载）；
2. 打开 Tailscale，点 **Log in**，用你选的账号登录；
3. 登录后菜单栏会出现 Tailscale 图标，点它能看到这台机器的地址，形如 `100.64.0.2`，**记下来**（后面填 `config/devices.toml` 要用）；
4. 建议：点 Tailscale 图标 → Settings → 勾选 **Launch at login**（开机自动连）。

> 异地 Mac 这一步需要有人在它旁边操作一次（或你通过“屏幕共享”远程操作）。这是整个项目唯一需要“人到场”的环节。

## iPhone / iPad 上的操作

1. App Store 搜索 **Tailscale** 并安装；
2. 打开 App，**用同一个账号登录**；
3. 按提示允许添加 VPN 配置（这是 Tailscale 正常工作必需的，系统会弹窗确认）；
4. 把开关打开，状态变成 Connected 即可。

## 验证组网成功

在本机 MacBook 的终端里执行（把 IP 换成异地 Mac 的 Tailscale 地址）：

```bash
ping -c 3 100.64.0.2
```

看到类似 `64 bytes from 100.64.0.2: icmp_seq=0 ...` 的回复 = 组网成功。
看到 `Request timeout` = 检查两边 Tailscale 是否都登录且已连接。

## 常见问题

- **连不上/超时**：先确认两台设备的 Tailscale 都是 Connected 状态；国内网络偶尔会让 Tailscale 走中转线路，稍慢但能用，一般等一会儿或重开开关会恢复。
- **想看所有设备的地址**：浏览器打开 https://login.tailscale.com/admin/machines ，登录后能看到每台设备的名字和 `100.x` 地址。
- **安全提示**：你的 Tailscale 账号 = 整个网络的钥匙，建议开启该账号的两步验证（Google/Apple 账号设置里开）。
