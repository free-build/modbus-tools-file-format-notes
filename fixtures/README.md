# 去业务化测试夹具

本目录包含四个最小用途测试文件，用于识别不同代际的 `.mbs` 和 `.mbp`，以及验证解析器遇到真实序列化结构时不会崩溃。

| 文件 | 预期签名 | 用途 |
|---|---|---|
| `modbus-slave-7.3.0-build-1402.mbs` | little-endian `7300` | Modbus Slave 7.x 二进制解析 |
| `modbus-slave-10.0.0-build-2493.mbs` | little-endian `10000` | Modbus Slave 10.x 二进制解析 |
| `modbus-poll-6.4.2-build-964.mbp` | little-endian `6402` | Modbus Poll 6.x 二进制解析 |
| `modbus-poll-13.2.1-build-2558.mbp` | XML 根节点 `ModbusPoll` | Modbus Poll 13.x XML 解析 |

## 去业务化处理

- 起始地址统一改为 `100`；
- 寄存器名称替换为 `Fixture` 虚构名称；
- 不包含用户原文件名、业务寄存器名、Windows 路径或 IP 地址；
- 二进制夹具采用等长替换，保留原有序列化边界；
- XML 夹具保留版本与节点结构，清除业务名称和日志路径。

这些文件不是官方发布的格式规范或示例，也不能代表对应版本可能产生的所有合法结构。

## 校验

```bash
python tools/verify_fixtures.py
```

文件哈希记录在 `MANIFEST.sha256`。修改夹具后必须同步更新清单，并在目标版本软件中重新进行打开测试。

