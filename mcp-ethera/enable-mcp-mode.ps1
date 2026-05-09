# 启用 MCP 游戏模式
# 运行此脚本后，说"开始游戏"将使用 MCP 模式（不读取全部文件）

$rulesDir = "..\.claude\rules"
$rulesFile = "$rulesDir\900_MCP_GAME_MODE.md"

if (-not (Test-Path $rulesDir)) {
    New-Item -ItemType Directory -Path $rulesDir -Force | Out-Null
}

if (Test-Path $rulesFile) {
    Write-Host "✅ MCP 游戏模式已启用（规则文件已存在）" -ForegroundColor Green
} else {
    @"
# MCP 游戏模式（路由规则）

> 此文件为 MCP 游戏模式的入口规则。
> CLAUDE.md 中"读取全部文件"的规则被此文件有条件地覆盖。

---

## 游戏模式启动判定

当用户说"**开始游戏**"、"**继续**"或类似进入游戏模式的话语时：

### IF ethera-engine MCP 服务器可用

遵循 `mcp-ethera/GAME_PROMPT.md` 中的全部指令，**跳过** CLAUDE.md 中"读取全部文件"的指令。

MCP 模式下的工作方式：
- 不读取全部 .md 文件
- 改为通过 MCP 资源（resources）和工具（tools）按需查询数据
- 遵循 GAME_PROMPT.md 中的 6 步流程
- 上下文控制在 ~45K 以内
- 使用 MCP 工具进行判定和文件维护

### ELSE（MCP 不可用）

回退到 CLAUDE.md 的原始指令：读取全部 .md 文件。

---

## 注意

- 不要同时运行两种模式。MCP 可用时，走 MCP 路线。
- 如果 MCP 模式出问题，删除此文件或用 disable-mcp-mode.ps1 恢复原状。
"@ | Out-File -FilePath $rulesFile -Encoding UTF8
    Write-Host "✅ MCP 游戏模式已启用" -ForegroundColor Green
    Write-Host "   规则文件: $($rulesFile | Resolve-Path -Relative)" -ForegroundColor Gray
}

Write-Host ""
Write-Host "现在说"开始游戏"将使用 MCP 模式。" -ForegroundColor Cyan
Write-Host "如需恢复原状，运行 disable-mcp-mode.ps1" -ForegroundColor Cyan
