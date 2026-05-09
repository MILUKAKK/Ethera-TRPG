# MCP 游戏模式

> 本项目默认运行在 MCP 模式下。此文件声明模式前提。

---

MCP 服务器由 `.claude/mcp.json` 配置，在 Claude Code 启动时自动加载。

游戏模式下的工作方式：
- 不读取全部 .md 文件
- 改为通过 MCP 资源（resources）和工具（tools）按需查询数据
- 遵循 `mcp-ethera/GAME_PROMPT.md` 的指令
- 使用 MCP 工具进行判定和文件维护

---

> 注意：MCP 服务器配置修改后需要重启 Claude Code 会话才能生效。
