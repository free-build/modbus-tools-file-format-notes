# Modbus Tools 工程文件格式兼容性笔记

本仓库记录 Modbus Poll `.mbp` 与 Modbus Slave `.mbs` 工程文件的版本识别、兼容性和安全解析规则，目标是帮助开源软件实现文件导入、迁移提示和只读分析。

> 这里讨论的是第三方桌面软件的**工程文件格式**，不是 Modbus RTU/TCP 线协议本身。

## 已检查的软件版本

| 软件 | 旧版本 | 新版本 | 工程文件 |
|---|---:|---:|---|
| Modbus Slave | 7.3.0, Build 1402 | 10.0.0, Build 2493 | `.mbs` |
| Modbus Poll | 6.4.2, Build 964 | 13.2.1, Build 2558 | `.mbp` |

“6.4.4 格式”没有在本次研究中得到独立软件样本验证。本仓库对旧 `.mbp` 的结论来自 **6.4.2 Build 964**，不能把两者无条件视为完全相同。

## 快速识别

读取文件开头即可区分目前观察到的四类格式：

| 文件 | 文件开头 | 判定 |
|---|---|---|
| `.mbs` | little-endian `uint32 == 7300` | Modbus Slave 7.x 二进制格式 |
| `.mbs` | little-endian `uint32 == 10000` | Modbus Slave 10.x 二进制格式 |
| `.mbp` | little-endian `uint32 == 6402` | Modbus Poll 6.4.2 二进制格式 |
| `.mbp` | UTF-8 XML 声明，根节点 `<ModbusPoll>` | Modbus Poll 13.x XML 格式 |

识别器必须同时检查文件长度、XML 根节点和版本节点，不能只根据扩展名或一个整数接受文件。

## 已实测的兼容性

- Modbus Slave 10.0.0 可以打开 Modbus Slave 7.3.0 保存的 `.mbs`。
- `.mbs` 一旦由 Modbus Slave 10.0.0 保存为新格式，Modbus Slave 7.3.0 无法再打开；旧程序会报告文件被截断或格式错误。
- Modbus Poll 6.4.2 使用二进制 `.mbp`；Modbus Poll 13.2.1 样本使用 XML `.mbp`。两者不能仅靠修改扩展名互换。
- 本次没有完成 Modbus Poll 13.2.1 对 6.4.2 二进制文件的正式运行时兼容性测试，因此不对该方向作保证。

详见：

- [版本与兼容矩阵](docs/COMPATIBILITY.md)
- [文件识别及解析规则](docs/FORMAT_DETECTION.md)
- [安全实现建议](docs/IMPLEMENTATION_GUIDE.md)
- [去业务化测试夹具](fixtures/README.md)

## 测试夹具

仓库提供四个用于格式识别和回归测试的去业务化文件：

- Modbus Slave 7.3.0 Build 1402 `.mbs`；
- Modbus Slave 10.0.0 Build 2493 `.mbs`；
- Modbus Poll 6.4.2 Build 964 `.mbp`；
- Modbus Poll 13.2.1 Build 2558 `.mbp`。

夹具使用虚构地址和名称，不包含客户寄存器表、设备名称、路径、IP 地址或串口配置。执行 `python tools/verify_fixtures.py` 可以核对签名、XML 版本和 SHA-256。

只读识别工具：

```bash
python tools/detect_format.py fixtures/modbus-poll-13.2.1-build-2558.mbp
```

机器可读的已知版本记录位于 [`spec/file-signatures.json`](spec/file-signatures.json)。夹具当前完成结构和哈希验证；经去业务化后的真实软件打开状态仍明确标记为 `pending`。

## 数据与版权边界

本仓库不包含：

- Modbus Poll、Modbus Slave 可执行文件或类型库；
- 用户设备协议、寄存器表或工程文件；
- 从原厂软件复制的帮助文档或其他受版权保护内容。

结论来自经授权样本的互操作性研究。字段含义没有得到官方确认的地方会明确标记为“观察”或“推断”。Modbus Poll 和 Modbus Slave 的名称及商标归其各自权利人所有；本项目与其开发商无关联。

## 许可证

本仓库原创文档采用 [MIT License](LICENSE)。该许可证不授予任何第三方软件、商标或文件格式规范的权利。

