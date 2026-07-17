# 第 3 步：iPhone / iPad 接入（两个入口，建议都配）

## 这一步在干嘛

手机和平板没有自带终端，给它们开两扇门：
1. **SSH App**（Blink / Termius）——完整终端体验，适合认真干活；
2. **Web 终端**（浏览器打开一个网页就是终端）——零安装，应急备用。

> 前提：移动端已完成 [第 1 步 Tailscale](01-tailscale-setup.md)，异地 Mac 已完成 [第 2 步初始化](02-remote-mac-setup.md)。

## 入口一：SSH App

### 方案① Termius（免费版够用）

1. App Store 安装 **Termius**；
2. 新建 Host：Address 填异地 Mac 的 Tailscale 地址（`100.64.0.2`），Username 填 macOS 用户名；
3. 认证方式选 **Key**，需要把本机的私钥导入手机：
   - 在本机 MacBook 上把私钥发到手机（隔空投送最方便）：
     ```bash
     # 在 MacBook 上执行，会打开隔空投送窗口
     open -R ~/.ssh/id_ed25519
     ```
     然后在 Finder 里右键该文件 → 共享 → 隔空投送到 iPhone；
   - 在 Termius 里导入这个文件作为 Key；
   - **注意：私钥 = 总钥匙。传完手机后，确认 AirDrop 记录/“文件”App 里没有多余副本散落。**
4. 连接，看到终端提示符就成功了。

### 方案② Blink Shell（付费，体验更好，可选）

1. App Store 安装 **Blink Shell**（订阅制，约 ¥128/年，可先试用）；
2. 在 Blink 里执行 `ssh yansong@100.64.0.2`，首次会引导你导入或生成密钥；
3. Blink 支持 Mosh（断网自动续连），地铁、电梯里用体验明显更好——以后网络环境差时值得考虑。

## 入口二：Web 终端（ttyd）

在**异地 Mac** 上执行一次（用 SSH 从本机执行即可）：

```bash
brew install ttyd   # 跑过 setup_remote_mac.sh 的话已装好
```

然后创建一个开机自启、只对内网开放的 Web 终端服务。在异地 Mac 上：

```bash
# 两个需要你自己替换的值：
TS_IP="100.64.0.2"                    # 换成这台 Mac 的 Tailscale 地址
TOKEN="请换成一串够长的随机字符"        # 相当于网页的登录密码
TTYD_BIN="$(brew --prefix)/bin/ttyd"

# 创建 launchd 自启配置
mkdir -p ~/Library/LaunchAgents
cat > ~/Library/LaunchAgents/com.agentbridge.ttyd.plist <<EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
  <key>Label</key><string>com.agentbridge.ttyd</string>
  <key>ProgramArguments</key>
  <array>
    <string>$TTYD_BIN</string>
    <string>--interface</string><string>$TS_IP</string>
    <string>--port</string><string>7681</string>
    <string>--credential</string><string>admin:$TOKEN</string>
    <string>--writable</string>
    <string>/bin/zsh</string>
  </array>
  <key>RunAtLoad</key><true/>
  <key>KeepAlive</key><true/>
</dict>
</plist>
EOF

launchctl load ~/Library/LaunchAgents/com.agentbridge.ttyd.plist
```

> 安全要点解释（不用背）：`--interface` 让网页**只监听 Tailscale 内网地址**，公网上根本摸不到这个端口；`--credential` 要求输入账号密码（admin + 你的 TOKEN）才能进；双重保险。

手机/iPad 使用：保持 Tailscale 连接 → Safari 打开 `http://100.64.0.2:7681` → 输入 admin 和 TOKEN → 出现终端。

## 在移动端上使用 agentctl

推荐做法：**把 agentctl 项目也放一份在异地 Mac 上**，手机 SSH/网页进去后直接调度：

```bash
# 在异地 Mac 上执行（可从本机 SSH 过去执行）
git clone <你的仓库地址> ~/agent-bridge   # 或者直接 scp 整个文件夹过去
cd ~/agent-bridge && bash scripts/install.sh
```

这样手机端 = 异地 Mac 的终端，所有 `agentctl` 命令照常用，还能调度其他设备。

## 常见问题

- **网页打不开**：iPhone 的 Tailscale 开关开了吗？异地 Mac 的 ttyd 在跑吗（`ssh` 过去执行 `launchctl list | grep ttyd`）？
- **终端里中文显示方块**：Blink/Termius 里把字体换成支持中文的等宽字体（设置里改）。
