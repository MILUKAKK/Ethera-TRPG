# level-up.ps1 — 升级计算
# 用法: .\level-up.ps1 -CurrentLv 1 -NewLv 2 -Str 4 -Con 5 -Int 7 -MA 0 -MaxHP 105 -MaxSP 70 -MaxMP 105
# 输出: 新HP/SP/MP上限 + 获得属性点/技能点

param(
    [int]$CurrentLv = 1,
    [int]$NewLv = 2,
    [int]$Str = 4,
    [int]$Dex = 6,
    [int]$Con = 5,
    [int]$Int = 7,
    [int]$Wis = 6,
    [int]$Cha = 9,
    [int]$MA = 0,
    [int]$MaxHP = 105,
    [int]$MaxSP = 70,
    [int]$MaxMP = 105
)

$levelsGained = $NewLv - $CurrentLv
if ($levelsGained -le 0) {
    Write-Output "无效: 新等级必须大于当前等级"
    exit 1
}

$attrPoints = $levelsGained * 3
$skillPoints = $levelsGained * 2

# HP = (CON * 20) + (Lv * 5)
$oldHP = ($Con * 20) + ($CurrentLv * 5)
$newHP = ($Con * 20) + ($NewLv * 5)

# MP = (INT * 15) + (MA * 5)
$oldMP = ($Int * 15) + ($MA * 5)
$newMP = ($Int * 15) + ($MA * 5)

# SP = (CON * 10) + (STR * 5)
$oldSP = ($Con * 10) + ($Str * 5)
$newSP = ($Con * 10) + ($Str * 5)

Write-Output "=== 升级 Lv.${CurrentLv} → Lv.${NewLv} (${levelsGained}级) ==="
Write-Output "HP上限: ${oldHP} → ${newHP} (+$($newHP-$oldHP))"
Write-Output "MP上限: ${oldMP} → ${newMP} (+$($newMP-$oldMP))"
Write-Output "SP上限: ${oldSP} → ${newSP} (+$($newSP-$oldSP))"
Write-Output ""
Write-Output "获得属性点: +${attrPoints}  (STR/DEX/CON/INT/WIS/CHA自由分配)"
Write-Output "获得技能点: +${skillPoints}  (注入技能或解锁新技能)"
Write-Output ""
Write-Output "注: LUK和MA不可通过属性点提升(需特殊事件)"
Write-Output "注: 属性分配后HP/MP/SP上限随之变化——需重新计算"

# XP table for reference
$xpTable = @{}
$xpNeeded = 0
for ($lv = $CurrentLv; $lv -lt $NewLv; $lv++) {
    $needed = switch ($lv) {
        1 { 100 } 2 { 200 } 3 { 400 } 4 { 600 } 5 { 800 }
        6 { 1100 } 7 { 1400 } 8 { 1800 } 9 { 2300 } 10 { 3000 }
        11 { 3900 } 12 { 5000 } 13 { 6500 } 14 { 8500 } 15 { 11000 }
        16 { 14000 } 17 { 18000 } 18 { 23000 } 19 { 30000 }
        default { 30000 }
    }
    $xpNeeded += $needed
}
Write-Output "所需XP: ${xpNeeded}"
