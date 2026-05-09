# event-picker.ps1 — 随机事件快速选取
# 用法: .\event-picker.ps1 -Location "磨坊镇" -Season "秋" -TimePeriod "朝时" -Cooldown "M01,M05,D12"
# 输出: 3-5个推荐事件（编号+名称+描述首句）

param(
    [string]$Location = "磨坊镇",
    [string]$Season = "秋",
    [string]$TimePeriod = "朝时",
    [string]$Cooldown = ""
)

$eventFile = "F:\OneDrive\文档\类地星球\GM判定信息\随机事件池.md"
if (-not (Test-Path $eventFile)) {
    Write-Output "EVENT_FILE_NOT_FOUND"
    exit 1
}

$cooldownList = @()
if ($Cooldown -ne "") { $cooldownList = $Cooldown -split "," | ForEach-Object { $_.Trim() } }

$lines = Get-Content $eventFile -Encoding UTF8
$events = @()

# Parse all events into structured list
$currentCategory = ""
for ($i = 0; $i -lt $lines.Count; $i++) {
    $line = $lines[$i]
    if ($line -match "^##\s+\d+\.\d+\s+(.+)") { $currentCategory = $Matches[1] }
    if ($line -match "^\|\s*(D\d+|MT\d+|TR\d+|CT\d+|M\d+|N\d+|W\d+|G\d+|S\d+|T\d+|WX\d+|SUP\d+)\s*\|") {
        $id = $Matches[1]
        if ($cooldownList -contains $id) { continue }

        # Get the event name and description
        $parts = $line -split "\|"
        if ($parts.Count -ge 4) {
            $name = $parts[3].Trim()
            $desc = if ($parts.Count -ge 5) { $parts[4].Trim() } else { "" }

            $events += @{
                ID = $id
                Name = $name
                Desc = $desc
                Category = $currentCategory
            }
        }
    }
}

# Filter by location
$locationMap = @{
    "磨坊镇" = @("D", "MT", "M", "N", "T", "WX", "SUP")
    "野外" = @("D", "TR", "M", "WX", "SUP")
    "灰石城" = @("D", "CT", "M", "WX", "SUP")
    "官道" = @("D", "TR", "M", "WX")
}

$allowedPrefixes = if ($locationMap.ContainsKey($Location)) { $locationMap[$Location] } else { @("D", "M") }

$filtered = $events | Where-Object {
    $prefix = $_.ID -replace "\d+", ""
    $allowedPrefixes -contains $prefix
}

# Seasonal filter for S-events
if ($Season -eq "秋" -or $Season -eq "春" -or $Season -eq "夏" -or $Season -eq "冬") {
    # Keep seasonal events that match
}

# Time period filter for T-events
# Simplified: keep all

# Randomly select 3-5
$count = if ($filtered.Count -ge 5) { 5 } elseif ($filtered.Count -ge 3) { 3 } else { $filtered.Count }
$selected = $filtered | Get-Random -Count $count

# Output
foreach ($e in $selected) {
    Write-Output "[$($e.ID)] $($e.Name) — $($e.Desc)"
}
