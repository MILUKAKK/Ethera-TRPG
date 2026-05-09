# calendar-check.ps1 — 世界日历闹钟
# 用法: .\calendar-check.ps1 -Year 1782 -Month 9 -Day 5 -WeekDay "金曜日"
# 输出: 今日预设事件列表（无则输出"NONE"）

param(
    [int]$Year = 1782,
    [int]$Month = 9,
    [int]$Day = 4,
    [string]$WeekDay = "木曜日"
)

$calendarFile = "F:\OneDrive\文档\类地星球\世界模拟信息\世界运行\世界日历.md"

if (-not (Test-Path $calendarFile)) {
    Write-Output "CALENDAR_FILE_NOT_FOUND"
    exit 1
}

$lines = Get-Content $calendarFile -Encoding UTF8
$found = $false
$inSection = $false
$results = @()

for ($i = 0; $i -lt $lines.Count; $i++) {
    $line = $lines[$i]

    # Track which month section we're in
    if ($line -match "^##\s+(\S+月)") { $inSection = ($Matches[1] -eq "$Month月") }
    if ($line -match "^##\s+(?!\S+月)") { $inSection = $false }

    if (-not $inSection) { continue }

    # Find date pattern: | 第X日 | 曜日 | ...
    if ($line -match "\|\s*第${Day}日\s*\|") {
        $found = $true
        $results += $line
        # Also capture the next few lines that continue the event
        for ($j = $i+1; $j -lt $lines.Count -and $j -lt $i+5; $j++) {
            $nextLine = $lines[$j]
            if ($nextLine -match "^\|" -or $nextLine -match "^-") { continue }
            if ($nextLine -match "^$" -or $nextLine -match "^##" -or $nextLine -match "^---") { break }
            if ($nextLine.Trim() -ne "") { $results += $nextLine }
        }
        break
    }
}

if (-not $found) {
    Write-Output "NONE"
} else {
    Write-Output ($results -join "`n")
}
