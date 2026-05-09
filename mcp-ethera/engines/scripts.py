"""Run the Ethera world PowerShell scripts."""

import subprocess
import json
import re
from pathlib import Path
from typing import Optional


# Script names mapped to their .ps1 files
SCRIPTS = {
    "weather-roll": "weather-roll.ps1",
    "calendar-check": "calendar-check.ps1",
    "event-picker": "event-picker.ps1",
    "travel-calc": "travel-calc.ps1",
    "combat-brief": "combat-brief.ps1",
    "npc-sync": "npc-sync.ps1",
    "national-cycle": "national-cycle.ps1",
    "dc-check": "dc-check.ps1",
    "rest-calc": "rest-calc.ps1",
    "level-up": "level-up.ps1",
}


class ScriptRunner:
    """Runs the Ethera world PowerShell automation scripts."""

    def __init__(self, scripts_dir: str | Path):
        self.scripts_dir = Path(scripts_dir)

    def _run(self, script_name: str, args: str = "") -> str:
        """Run a PowerShell script with the given arguments."""
        script_path = self.scripts_dir / SCRIPTS.get(script_name, script_name)
        if not script_path.exists():
            return f"脚本未找到: {script_path}"

        cmd = [
            "powershell",
            "-NoProfile",
            "-ExecutionPolicy", "Bypass",
            "-Command",
            f'& "{script_path}" {args}'
        ]
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=30,
                encoding="utf-8",
            )
            output = result.stdout.strip()
            if result.stderr.strip():
                output += f"\n[stderr]\n{result.stderr.strip()}"
            if result.returncode != 0:
                output = f"脚本返回错误码 {result.returncode}:\n{output}"
            return output if output else f"脚本 `{script_name}` 执行完毕（无输出）"
        except subprocess.TimeoutExpired:
            return f"脚本 `{script_name}` 执行超时（>30s）"
        except FileNotFoundError:
            return f"PowerShell 未找到，请确保已安装。"
        except Exception as e:
            return f"脚本执行错误: {e}"

    def weather_roll(self, current_weather: str, season: str) -> str:
        """Roll tomorrow's weather."""
        return self._run("weather-roll", f'-CurrentWeather "{current_weather}" -Season "{season}"')

    def calendar_check(self, year: int, month: int, day: int) -> str:
        """Check today's scheduled events."""
        return self._run("calendar-check", f"-Year {year} -Month {month} -Day {day}")

    def event_picker(self, location: str, season: str, time_period: str) -> str:
        """Pick random events for the current time period."""
        args = f'-Location "{location}" -Season "{season}" -TimePeriod "{time_period}"'
        return self._run("event-picker", args)

    def travel_calc(self, origin: str, destination: str, method: str) -> str:
        """Calculate travel parameters."""
        args = f'-Origin "{origin}" -Destination "{destination}" -Method "{method}"'
        return self._run("travel-calc", args)

    def combat_brief(self, **params) -> str:
        """Generate combat brief. Params should match the script's parameters."""
        args = " ".join(
            f'-{k} "{v}"' if isinstance(v, str) else f"-{k} {v}"
            for k, v in params.items()
        )
        return self._run("combat-brief", args)

    def dc_check(self, attr: int, skill_lv: int, env_mod: int, dc: int) -> str:
        """Check if a skill check passes."""
        args = f"-Attr {attr} -SkillLv {skill_lv} -EnvMod {env_mod} -DC {dc}"
        return self._run("dc-check", args)

    def rest_calc(self, con: int, int_: int, duration: str, quality: str) -> str:
        """Calculate rest recovery."""
        args = f'-Con {con} -Int {int_} -Duration "{duration}" -Quality "{quality}"'
        return self._run("rest-calc", args)

    def npc_sync(self) -> str:
        """Sync NPC states from the simulation log."""
        return self._run("npc-sync")

    def national_cycle(self, country: str, month: int, conscripts: int = 0) -> str:
        """Run national monthly cycle."""
        args = f'-Country "{country}" -Month {month} -Conscripts {conscripts}'
        return self._run("national-cycle", args)
