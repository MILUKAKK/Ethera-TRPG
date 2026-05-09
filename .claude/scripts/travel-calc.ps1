# travel-calc.ps1 — 旅行计算器
# 用法: .\travel-calc.ps1 -Origin "磨坊镇" -Destination "灰石城" -Method "步行"
# 输出: 多行旅行参数

param(
    [string]$Origin = "磨坊镇",
    [string]$Destination = "灰石城",
    [string]$Method = "步行"
)

# Distance database (km)
$distances = @{
    "磨坊镇->灰石城" = 80
    "灰石城->磨坊镇" = 80
    "磨坊镇->歪脖子松" = 12
    "磨坊镇->裂脊隘口" = 120
    "灰石城->白垩城" = 350
    "灰石城->丰收城" = 250
    "灰石城->河卫城" = 300
    "磨坊镇->白垩城" = 430
}

$key = "$Origin->$Destination"
$distance = if ($distances.ContainsKey($key)) { $distances[$key] } else { 50 }

# Speed database (km/day)
$speeds = @{
    "步行" = 30
    "轻装步行" = 40
    "马车" = 50
    "骑行" = 60
    "战马骑行" = 50
}

$speed = if ($speeds.ContainsKey($Method)) { $speeds[$Method] } else { 30 }
$days = [Math]::Ceiling($distance / $speed)

# Supplies
$foodPerDay = 1
$waterPerDay = 2
$totalFood = $days * $foodPerDay
$totalWater = $days * $waterPerDay

# Encounter probability per segment
if ($distance -le 20) { $encPct = 5 }
elseif ($distance -le 80) { $encPct = 10 }
else { $encPct = 15 }

# Output
Write-Output "距离: ${distance}km | 方式: ${Method}(${speed}km/日)"
Write-Output "耗时: ${days}日 | 食物: ${totalFood}日份 | 水: ${totalWater}升"
Write-Output "遭遇概率: ${encPct}%/段 | 建议露营次数: $([Math]::Max(0, $days-1))次"
