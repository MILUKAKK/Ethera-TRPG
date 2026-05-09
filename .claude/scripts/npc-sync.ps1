# npc-sync.ps1 — NPC状态同步
# 用法: .\npc-sync.ps1
# 从世界推演日志中提取[NPC:xxx]元数据行，同步到各NPC档案的"当前状态"行
# 无参数——自动扫描当日条目

param()

$logFile = "F:\OneDrive\文档\类地星球\世界模拟信息\世界运行\世界推演日志.md"
$npcDir = "F:\OneDrive\文档\类地星球\世界模拟信息\NPC数据库"

if (-not (Test-Path $logFile)) {
    Write-Output "LOG_NOT_FOUND"
    exit 1
}

$lines = Get-Content $logFile -Encoding UTF8
$metaLines = @()

foreach ($line in $lines) {
    if ($line -match "\[NPC:([^\]]+)\]\s*(.+)") {
        $npcName = $Matches[1].Trim()
        $statusText = $Matches[2].Trim()
        $metaLines += @{ Name = $npcName; Status = $statusText }
    }
}

if ($metaLines.Count -eq 0) {
    Write-Output "NO_META_LINES"
    exit 0
}

$nameToFile = @{
    "索恩" = "索恩.md"
    "伯恩" = "伯恩.md"
    "玛莎" = "玛莎.md"
    "汉克" = "汉克.md"
    "莉娜" = "莉娜.md"
    "波特" = "波特.md"
}

foreach ($meta in $metaLines) {
    $fileName = if ($nameToFile.ContainsKey($meta.Name)) { $nameToFile[$meta.Name] } else { continue }
    $filePath = Join-Path $npcDir $fileName

    if (-not (Test-Path $filePath)) {
        Write-Output "NPC_FILE_NOT_FOUND: $fileName"
        continue
    }

    $npcLines = Get-Content $filePath -Encoding UTF8
    $newLines = @()
    $synced = $false

    for ($i = 0; $i -lt $npcLines.Count; $i++) {
        $l = $npcLines[$i]
        # Find the "当前状态" line and replace it
        if ($l -match "^>\s*\*\*当前状态\*\*") {
            $newLines += "> **当前状态** [木曜日·朝时]：$($meta.Status)"
            $synced = $true
        } else {
            $newLines += $l
        }
    }

    if ($synced) {
        $newLines -join "`n" | Set-Content $filePath -Encoding UTF8
        Write-Output "SYNCED: $($meta.Name) → $fileName"
    } else {
        Write-Output "NO_STATUS_LINE: $($meta.Name)"
    }
}

Write-Output "DONE"
