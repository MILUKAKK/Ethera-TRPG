# combat-brief.ps1 — 战斗预期简报
# 用法: .\combat-brief.ps1 -PlayerStr 4 -PlayerDex 6 -PlayerCon 5 -PlayerSwordLv 1 -PlayerHP 105 -EnemyName "草原狼" -EnemyCount 2
# 输出: 伤害预估/持续轮数/威胁评级

param(
    [int]$PlayerStr = 4,
    [int]$PlayerDex = 6,
    [int]$PlayerCon = 5,
    [int]$PlayerSwordLv = 1,
    [int]$PlayerHP = 105,
    [string]$EnemyName = "草原狼",
    [int]$EnemyCount = 1
)

# Enemy database (simplified from 怪物与敌人.md)
$enemies = @{
    "草原狼" = @{ HP=30; AtkMin=5; AtkMax=10; Def=1; Dex=8; XP=15 }
    "冰原巨狼" = @{ HP=70; AtkMin=12; AtkMax=20; Def=5; Dex=10; XP=100 }
    "黑熊" = @{ HP=105; AtkMin=12; AtkMax=20; Def=4; Dex=6; XP=100 }
    "野猪" = @{ HP=70; AtkMin=10; AtkMax=16; Def=5; Dex=8; XP=50 }
    "山狮" = @{ HP=48; AtkMin=10; AtkMax=18; Def=2; Dex=12; XP=60 }
    "隙鬼" = @{ HP=50; AtkMin=8; AtkMax=14; Def=8; Dex=9; XP=65 }
    "腐蚀软泥" = @{ HP=40; AtkMin=3; AtkMax=6; Def=2; Dex=2; XP=35 }
    "游魂" = @{ HP=28; AtkMin=5; AtkMax=10; Def=5; Dex=8; XP=40 }
    "骸骨战士" = @{ HP=38; AtkMin=6; AtkMax=12; Def=6; Dex=7; XP=33 }
    "毒蛇" = @{ HP=10; AtkMin=1; AtkMax=3; Def=0; Dex=10; XP=25 }
    "征召步兵" = @{ HP=60; AtkMin=8; AtkMax=14; Def=5; Dex=5; XP=40 }
    "银翼骑兵" = @{ HP=90; AtkMin=8; AtkMax=16; Def=10; Dex=9; XP=100 }
    "黑铁步兵" = @{ HP=135; AtkMin=12; AtkMax=20; Def=25; Dex=5; XP=240 }
}

$enemy = if ($enemies.ContainsKey($EnemyName)) { $enemies[$EnemyName] } else { @{ HP=50; AtkMin=5; AtkMax=10; Def=3; Dex=7; XP=30 } }

# Player damage calculation (simplified)
# 物理伤害 = (武器基础伤害 + STR修正) × 技能等级系数 - 对方防御
$weaponBase = 5.5  # 小刀 3-6 中值
$strMod = $PlayerStr * 1.5  # = 6
$skillCoeff = switch ($PlayerSwordLv) { 1 { 0.6 } 2 { 0.8 } 3 { 1.0 } 4 { 1.2 } 5 { 1.4 } default { 0.6 } }
$baseDmg = [Math]::Max(1, [Math]::Round(($weaponBase + $strMod) * $skillCoeff - $enemy.Def))
$playerDmgMin = [Math]::Max(1, [Math]::Round($baseDmg * 0.7))
$playerDmgMax = [Math]::Max(2, [Math]::Round($baseDmg * 1.3))

# Enemy damage
$enemyDmgMin = $enemy.AtkMin
$enemyDmgMax = $enemy.AtkMax

# Player defense
$playerDef = [Math]::Round($PlayerCon * 1.5)  # CON*1.5

# Estimate rounds (simplified)
$totalEnemyHP = $enemy.HP * $EnemyCount
$playerDmgPerRound = ($playerDmgMin + $playerDmgMax) / 2
$enemyDmgPerRound = (($enemyDmgMin + $enemyDmgMax) / 2 - $playerDef) * $EnemyCount
if ($enemyDmgPerRound -lt 1) { $enemyDmgPerRound = 1 }

$roundsEstimate = [Math]::Ceiling($totalEnemyHP / [Math]::Max(1, $playerDmgPerRound))

# Threat assessment
$totalEnemyDmgEstimate = $roundsEstimate * $enemyDmgPerRound
$threatRatio = $totalEnemyDmgEstimate / $PlayerHP
$threatLevel = switch ($threatRatio) {
    { $_ -lt 0.2 } { "轻松 — 预计几乎不受伤害" }
    { $_ -lt 0.5 } { "可胜 — 预计轻伤" }
    { $_ -lt 1.0 } { "危险 — 预计显著受伤" }
    { $_ -lt 2.0 } { "极险 — 可能濒死或战败" }
    default { "碾压 — 极高战败风险" }
}

Write-Output "玩家攻击: ${playerDmgMin}-${playerDmgMax}/轮 | 敌人攻击: ${enemyDmgMin}-${enemyDmgMax}/轮"
Write-Output "敌人总HP: ${totalEnemyHP}(${EnemyCount}只×${enemy.HP}) | 预计轮数: ~${roundsEstimate}轮"
Write-Output "威胁: ${threatLevel}"
Write-Output "XP预估: $($enemy.XP * $EnemyCount)"
