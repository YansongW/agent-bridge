"""设备清单与连通性检查。"""

from . import remote


def probe_all(devices):
    """逐个探测设备，返回 [(名字, 设备配置, 是否在线, 说明)]。"""
    results = []
    for name, dev in devices.items():
        online, note = remote.check_online(dev)
        results.append((name, dev, online, note))
    return results
