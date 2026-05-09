# dc-check.ps1 — DC判定计算
# 用法: .\dc-check.ps1 -Attr 6 -SkillLv 2 -EnvMod -2 -DC 13
# 输出: 判别值 vs DC → 结果等级

param(
    [int]$Attr = 5,
    [int]$SkillLv = 0,
    [int]$EnvMod = 0,
    [int]$DC = 10
)

$skillBonus = $SkillLv * 2
$checkValue = $Attr + $skillBonus + $EnvMod
$diff = $checkValue - $DC

$result = switch ($diff) {
    { $_ -ge 8 }  { "大成功" }
    { $_ -ge 3 }  { "成功" }
    { $_ -ge -2 } { "勉强成功或轻微失败" }
    { $_ -ge -7 } { "失败" }
    default      { "大失败" }
}

Write-Output "判定: ${Attr}(属性) + ${skillBonus}(技能Lv${SkillLv}×2) + ${EnvMod}(环境) = ${checkValue} vs DC${DC} → ${result} (差值${diff})"
