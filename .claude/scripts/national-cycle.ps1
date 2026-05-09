# national-cycle.ps1 — 国家月度运转
# 用法: .\national-cycle.ps1 -Country "艾尔德兰" -Month 9 -Year 1782 -Conscripts 0 -Refugees 0 -WarSpending 0
# 输出: 更新后的人口/财政/粮仓关键数字

param(
    [string]$Country = "艾尔德兰",
    [int]$Month = 9,
    [int]$Year = 1782,
    [int]$Conscripts = 0,
    [int]$Refugees = 0,
    [int]$WarSpending = 0
)

# Base data for 艾尔德兰
$baseData = @{
    "艾尔德兰" = @{
        Population = 3800000
        AnnualRevenue = 8500000
        AnnualSpending = 8500000
        Debt = 2000000
        Granary = 5000  # 吨，四座战略粮仓合计
        Mobilized = 0
    }
}

$data = if ($baseData.ContainsKey($Country)) { $baseData[$Country].Clone() } else { $null }
if (-not $data) {
    Write-Output "COUNTRY_NOT_FOUND"
    exit 1
}

# Monthly calculations
$monthlyNaturalGrowth = [Math]::Round($data.Population * 0.0008)    # +0.08%/月 (= ~1%/年)
$monthlyNaturalDeath = [Math]::Round($data.Population * 0.0021)      # -0.21%/月 (= ~2.5%/年)
$netNatural = $monthlyNaturalGrowth - $monthlyNaturalDeath            # ≈ -0.13%/月 (中世纪常态：缓慢下降)
$netPopulation = $netNatural - $Conscripts + $Refugees
$newPopulation = $data.Population + $netPopulation

# Financial
$monthlyRevenue = [Math]::Round($data.AnnualRevenue / 12)
$monthlySpending = [Math]::Round($data.AnnualSpending / 12) + $WarSpending
$monthlyBalance = $monthlyRevenue - $monthlySpending
$newDebt = $data.Debt + [Math]::Max(0, -$monthlyBalance)

# Granary (消耗视动员人数)
$dailyConsumptionPerPerson = 0.002  # 吨
$monthlyConsumption = $data.Mobilized * $dailyConsumptionPerPerson * 28
$newGranary = [Math]::Max(0, $data.Granary - $monthlyConsumption)

# Mobilization tracked externally (passed via $Conscripts parameter)
$newMobilized = $data.Mobilized + $Conscripts

Write-Output "=== ${Country}月度运转 · ${Year}年${Month}月 ==="
Write-Output "人口: $($newPopulation) (本月变化: $netPopulation)"
Write-Output "  自然增长: +$monthlyNaturalGrowth | 自然死亡: -$monthlyNaturalDeath"
if ($Conscripts -ne 0) { Write-Output "  征召减少: -$Conscripts" }
if ($Refugees -ne 0) { Write-Output "  难民增加: +$Refugees" }
Write-Output "财政: 收入${monthlyRevenue}金/月 | 支出${monthlySpending}金/月 | 盈余: ${monthlyBalance}金"
if ($monthlyBalance -lt 0) { Write-Output "  ⚠ 赤字! 新国债: ${newDebt}金" }
Write-Output "粮仓: ${newGranary}吨 (消耗: $([Math]::Round($monthlyConsumption,1))吨)"
Write-Output "动员人数: ${newMobilized}"
