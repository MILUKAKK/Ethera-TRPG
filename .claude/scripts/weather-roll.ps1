# weather-roll.ps1 — 每日天气骰子
# 用法: .\weather-roll.ps1 -CurrentWeather "多云" -Season "秋"
# 输出: 一行天气结果

param(
    [string]$CurrentWeather = "晴",
    [string]$Season = "秋"
)

# 季节基准概率
$baseProbs = @{
    "春" = @{ "晴"=30; "多云"=25; "阴"=15; "小雨"=15; "大雨"=10; "雾"=5; "风"=0; "暴雨"=0; "雪"=0 }
    "夏" = @{ "晴"=45; "多云"=20; "阴"=10; "小雨"=5; "大雨"=5; "暴雨"=10; "风"=5; "雾"=0; "雪"=0 }
    "秋" = @{ "晴"=25; "多云"=25; "阴"=20; "小雨"=15; "大雨"=10; "风"=5; "暴雨"=0; "雾"=0; "雪"=0 }
    "冬" = @{ "晴"=20; "多云"=25; "阴"=25; "雪"=20; "风"=10; "小雨"=0; "大雨"=0; "暴雨"=0; "雾"=0 }
}

# 天气连续修正
$continuity = @{
    "晴"   = @{ "晴"=40; "多云"=30; "阴"=15; "雨类"=10; "其他"=5 }
    "多云" = @{ "多云"=35; "阴"=25; "雨类"=20; "晴"=15; "其他"=5 }
    "阴"   = @{ "雨类"=40; "阴"=30; "多云"=15; "晴"=10; "其他"=5 }
    "小雨" = @{ "阴"=30; "小雨"=25; "多云"=20; "晴"=15; "大雨"=10 }
    "大雨" = @{ "小雨"=30; "阴"=25; "多云"=20; "大雨"=15; "晴"=10 }
    "暴雨" = @{ "小雨"=30; "阴"=25; "多云"=20; "大雨"=15; "晴"=10 }
}

$isRain = @("小雨", "大雨", "暴雨")

# 构建概率池
$pool = @{}
$base = $baseProbs[$Season]
if (-not $base) { $base = $baseProbs["秋"] }

foreach ($w in $base.Keys) { $pool[$w] = $base[$w] }

# 叠加连续修正
if ($continuity.ContainsKey($CurrentWeather)) {
    $cont = $continuity[$CurrentWeather]
    foreach ($k in $cont.Keys) {
        $factor = $cont[$k]
        if ($k -eq "雨类") {
            foreach ($r in $isRain) { if ($pool.ContainsKey($r)) { $pool[$r] = [Math]::Max(0, $pool[$r] + $factor - 15) } }
        } elseif ($k -eq "其他") {
            # distribute evenly
        } elseif ($pool.ContainsKey($k)) {
            $pool[$k] = [Math]::Max(0, $pool[$k] + ($factor - 15))
        }
    }
}

# 加权随机
$total = 0; $weights = @()
foreach ($k in $pool.Keys) { $total += $pool[$k] }
$roll = Get-Random -Minimum 1 -Maximum ($total + 1)
$cumulative = 0
foreach ($k in $pool.Keys) {
    $cumulative += $pool[$k]
    if ($roll -le $cumulative) { $result = $k; break }
}

# 特殊：连续晴3日→雨概率上升
# 这个需要LLM提供"连续晴几天"参数，脚本不跟踪状态
# 简化为：如果当前是晴且季节是秋→阴/雨概率微升
if ($CurrentWeather -eq "晴" -and $Season -eq "秋") {
    if ((Get-Random -Minimum 1 -Maximum 101) -le 10) { $result = "阴" }
}

Write-Output $result
