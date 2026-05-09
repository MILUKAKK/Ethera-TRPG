# 禁用 MCP 游戏模式，恢复原始模式
# 运行此脚本后，说"开始游戏"将恢复读取全部文件的原始行为

$rulesFile = "..\.claude\rules\900_MCP_GAME_MODE.md"

if (Test-Path $rulesFile) {
    Remove-Item $rulesFile -Force
    Write-Host "✅ MCP 游戏模式已禁用" -ForegroundColor Green
    Write-Host "   已删除规则文件: $rulesFile" -ForegroundColor Gray
} else {
    Write-Host "ℹ️  MCP 游戏模式未启用（规则文件不存在）" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "现在说"开始游戏"将恢复原始行为（读取全部文件）。" -ForegroundColor Cyan
Write-Host "如需重新启用，运行 enable-mcp-mode.ps1" -ForegroundColor Cyan
