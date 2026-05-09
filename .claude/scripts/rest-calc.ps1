# rest-calc.ps1 — 休息恢复计算
# 用法: .\rest-calc.ps1 -Con 5 -Int 7 -MaxHP 105 -MaxSP 70 -MaxMP 105 -Duration "夜睡" -Quality "旅馆舒适"
# 输出: HP/SP/MP恢复量

param(
    [int]$Con = 5,
    [int]$Int = 7,
    [int]$MaxHP = 105,
    [int]$MaxSP = 70,
    [int]$MaxMP = 105,
    [string]$Duration = "夜睡",
    [string]$Quality = "正常"
)

# Duration presets
$restTypes = @{
    "喘息" = @{ Label="战斗喘息(1轮)"; SP=$Con*1 }
    "短休" = @{ Label="短暂休息(1时)"; SP=$Con*3 }
    "夜睡" = @{ Label="夜间睡眠(4时以上)"; HP=$Con*5; SP="全恢复"; MP=$Int*3 }
    "全天" = @{ Label="全天休息"; HP=$Con*10; SP="全恢复"; MP=$Int*2 }
    "劣睡" = @{ Label="劣质睡眠"; HP=([Math]::Round($Con*2.5)); SP=([Math]::Round($MaxSP*0.5)); MP=([Math]::Round($Int*1.5)) }
}

$rest = if ($restTypes.ContainsKey($Duration)) { $restTypes[$Duration] } else { $restTypes["夜睡"] }

# Quality multiplier
$qualityMult = switch ($Quality) {
    "旅馆舒适" { 1.5 }
    "正常" { 1.0 }
    "露天" { 0.5 }
    default { 1.0 }
}

Write-Output "=== $($rest.Label) · 品质: ${Quality}(${qualityMult}×) ==="

if ($rest.ContainsKey("HP")) {
    $hpRecover = [Math]::Round($rest.HP * $qualityMult)
    Write-Output "HP恢复: ${hpRecover}"
} else {
    Write-Output "HP恢复: 无"
}

if ($rest.ContainsKey("SP")) {
    $spResult = if ($rest.SP -eq "全恢复") { "全恢复 (至 ${MaxSP})" } else { [Math]::Round($rest.SP * $qualityMult) }
    Write-Output "SP恢复: ${spResult}"
}

if ($rest.ContainsKey("MP")) {
    $mpRecover = [Math]::Round($rest.MP * $qualityMult)
    Write-Output "MP恢复: ${mpRecover}"
} else {
    Write-Output "MP恢复: 无"
}

Write-Output "(最终值不超过上限: HP${MaxHP}/SP${MaxSP}/MP${MaxMP})"
