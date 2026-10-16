# Contributing

欢迎补充新的版本签名、兼容性结果和去业务化测试夹具。

提交前请确认：

1. 你有权使用并公开相关测试数据。
2. 不提交厂商程序、类型库、帮助文件或许可证密钥。
3. 不提交客户名称、设备名称、寄存器表、串口、IP、路径或现场配置。
4. 新夹具使用虚构名称和地址，并更新 `fixtures/MANIFEST.sha256`。
5. 在 `spec/file-signatures.json` 中把结构验证与真实软件打开验证分开记录。
6. 执行：

   ```bash
   python tools/verify_fixtures.py
   python -m unittest discover -s tests -v
   ```

兼容性报告应提供软件完整版本、Build、文件来源版本、打开方向和实际结果；无法确认的内容必须标记为推断。

