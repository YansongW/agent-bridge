"""读取 config/ 下的设备清单（devices.toml）与 Agent 清单（agents.toml）。

优先使用标准库 tomllib（Python 3.11+）；老版本 Python 自动回退到
内置的迷你解析器（只支持本项目用到的 TOML 子集：节、字符串、布尔、注释）。
"""

import os
import sys

# 项目根目录 = 本文件所在包的上一级
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONFIG_DIR = os.environ.get("AGENTCTL_CONFIG", os.path.join(PROJECT_ROOT, "config"))


# ---------------------------------------------------------------- 迷你 TOML 解析器
def _mini_toml_load(path):
    """解析本项目配置文件用到的 TOML 子集：[section]、key = "value"、true/false、# 注释。"""
    data = {}
    current = data
    with open(path, "r", encoding="utf-8") as f:
        for lineno, raw in enumerate(f, 1):
            line = raw.strip()
            if not line or line.startswith("#"):
                continue
            if line.startswith("[") and line.endswith("]"):
                name = line[1:-1].strip()
                if not name:
                    raise ValueError(f"{path}:{lineno} 节名不能为空")
                current = {}
                data[name] = current
                continue
            if "=" not in line:
                raise ValueError(f"{path}:{lineno} 无法解析：{line!r}")
            key, _, value = line.partition("=")
            key = key.strip()
            value = value.strip()
            # 去掉行尾注释（值里没有 # 的情况下安全）
            if not value.startswith(('"', "'")) and "#" in value:
                value = value.split("#", 1)[0].strip()
            if len(value) >= 2 and value[0] == value[-1] and value[0] in ('"', "'"):
                current[key] = value[1:-1]
            elif value.lower() == "true":
                current[key] = True
            elif value.lower() == "false":
                current[key] = False
            else:
                try:
                    current[key] = int(value)
                except ValueError:
                    raise ValueError(f"{path}:{lineno} 不支持的值：{value!r}（请用双引号包起来）")
    return data


def _load_toml(path):
    try:
        import tomllib  # Python 3.11+
        with open(path, "rb") as f:
            return tomllib.load(f)
    except ImportError:
        return _mini_toml_load(path)


def _load(name):
    # 优先读 *.local.toml（本地私有配置，已被 .gitignore 排除，适合放真实 IP）
    local_variant = os.path.join(CONFIG_DIR, name.replace(".toml", ".local.toml"))
    path = os.path.join(CONFIG_DIR, name)
    if os.path.isfile(local_variant):
        path = local_variant
    if not os.path.isfile(path):
        sys.exit(f"找不到配置文件：{path}\n请先按 README 的说明创建它。")
    try:
        return _load_toml(path)
    except Exception as e:
        sys.exit(f"配置文件 {path} 解析失败：{e}")


def load_devices():
    """返回 {设备名: {host, user, local, description, ...}}"""
    return _load("devices.toml")


def load_agents():
    """返回 {agent名: {command, description, ...}}"""
    return _load("agents.toml")


def get_device(name):
    devices = load_devices()
    if name not in devices:
        known = "、".join(sorted(devices)) or "（空）"
        sys.exit(f"未知设备：{name}\n已知设备：{known}\n请在 {CONFIG_DIR}/devices.toml 中添加。")
    return devices[name]


def get_agent(name):
    agents = load_agents()
    if name not in agents:
        known = "、".join(sorted(agents)) or "（空）"
        sys.exit(f"未知 Agent：{name}\n已知 Agent：{known}\n请在 {CONFIG_DIR}/agents.toml 中添加。")
    return agents[name]
