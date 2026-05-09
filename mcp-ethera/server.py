"""埃塞拉大陆 · MCP 世界引擎

为 Claude Code 提供 TRPG 世界的资源与工具。
通过 MCP 协议，LLM 可按需查询世界数据、调用 GM 脚本、维护游戏状态。

使用方式：
  python server.py

环境变量：
  WORLD_ROOT — 项目根目录（默认：自动探测上级目录）
"""

import os
import sys
import json
from pathlib import Path
from typing import Optional

from mcp.server.fastmcp import FastMCP

from engines.file_loader import FileLoader
from engines.scripts import ScriptRunner
from engines.lore import LoreSearcher

# ── 路径探测 ──────────────────────────────────────────────

def find_world_root() -> Path:
    """自动探测项目根目录。优先环境变量，其次上级目录探测。"""
    if env_root := os.environ.get("WORLD_ROOT"):
        return Path(env_root)

    # 从当前文件位置向上搜索，找 CLAUDE.md
    current = Path(__file__).resolve()
    for parent in [current] + list(current.parents):
        if (parent / "CLAUDE.md").exists():
            return parent
        if (parent / "系统手册.md").exists():
            return parent

    # 兜底
    return Path.cwd()


WORLD_ROOT = find_world_root()
SCRIPTS_DIR = WORLD_ROOT / ".claude" / "scripts"
DATA_DIR = Path(__file__).parent / "data"

# 确保 data 目录存在
DATA_DIR.mkdir(parents=True, exist_ok=True)

# ── 初始化引擎组件 ─────────────────────────────────────────

loader = FileLoader(WORLD_ROOT)
scripts = ScriptRunner(SCRIPTS_DIR if SCRIPTS_DIR.exists() else WORLD_ROOT / ".claude" / "scripts")
lore = LoreSearcher(WORLD_ROOT, DATA_DIR / "chroma_db")

# 后台初始化向量检索（不阻塞启动）
try:
    lore.initialize()
except Exception:
    pass

# ── FastMCP 服务器 ─────────────────────────────────────────

mcp = FastMCP(
    "埃塞拉世界引擎",
    instructions="埃塞拉大陆 TRPG 世界的数据访问与推演工具。为 GM 提供完整的资源查询与推演工具集。",
)


# ═══════════════════════════════════════════════════════════
# 资源 Resources — 按需读取完整 .md 文件（不压缩，全文返回）
# ═══════════════════════════════════════════════════════════

@mcp.resource("etera://player/profile",
              description="玩家面板：属性、技能、物品、人际关系")
def resource_player_profile() -> str:
    return loader.read_player_profile()


@mcp.resource("etera://player/quests",
              description="当前任务：进行中的任务与已完成任务")
def resource_player_quests() -> str:
    return loader.read_active_quests()


@mcp.resource("etera://player/map",
              description="玩家当前已知地理信息")
def resource_player_map() -> str:
    return loader.read_known_map()


@mcp.resource("etera://player/known-npcs",
              description="玩家已结识的 NPC 名录")
def resource_player_known_npcs() -> str:
    return loader.read_known_npcs()


@mcp.resource("etera://world/state",
              description="世界状态：当前时间、天气、季节、节奏标记")
def resource_world_state() -> str:
    return loader.read_world_state()


@mcp.resource("etera://world/calendar",
              description="日期与时间规则：历法、时辰、季节系统")
def resource_world_calendar() -> str:
    return loader.read_world_calendar()


@mcp.resource("etera://world/log",
              description="世界推演日志：NPC行动摘要与区域动态")
def resource_world_log() -> str:
    return loader.read_world_log()


@mcp.resource("etera://world/factions",
              description="势力动态：国家间关系与势力矩阵")
def resource_world_factions() -> str:
    return loader.read_faction_dynamics()


@mcp.resource("etera://world/calendar-events",
              description="世界日历：预设事件日程")
def resource_world_calendar_events() -> str:
    return loader.read_world_calendar_events()


@mcp.resource("etera://gm/rules",
              description="GM 核心准则：最高指导规则")
def resource_gm_rules() -> str:
    return loader.read_gm_rule("GM准则")


@mcp.resource("etera://gm/output-format",
              description="输出格式规范：回复结构、符号、HUD")
def resource_gm_output_format() -> str:
    return loader.read_gm_rule("输出格式规范")


@mcp.resource("etera://gm/update-checklist",
              description="文件更新触发清单：每次回复后必须更新的文件")
def resource_gm_update_checklist() -> str:
    return loader.read_gm_rule("文件更新触发清单")


@mcp.resource("etera://gm/whitelist",
              description="玩家可知内容白名单：什么可以/不可以告诉玩家")
def resource_gm_whitelist() -> str:
    return loader.read_gm_rule("玩家可知内容白名单")


@mcp.resource("etera://gm/behavior-rules",
              description="信息边界 + 六维选项模型 + 性格演化 + 冲突驳回")
def resource_gm_behavior_rules() -> str:
    return loader.read_gm_rule("玩家可知内容白名单")


@mcp.resource("etera://gm/tech-restrictions",
              description="科技限制清单：时代认知边界")
def resource_gm_tech_restrictions() -> str:
    return loader.read_gm_rule("科技限制清单")


@mcp.resource("etera://gm/hidden-info",
              description="角色隐藏信息：所有重要NPC的秘密与揭露条件")
def resource_gm_hidden_info() -> str:
    return loader.read_gm_rule("角色隐藏信息")


@mcp.resource("etera://gm/foreshadowing",
              description="伏笔追踪：已铺设的剧情伏笔及其状态")
def resource_gm_foreshadowing() -> str:
    return loader.read_gm_rule("伏笔追踪")


@mcp.resource("etera://gm/branches",
              description="剧情分支树：活跃/休眠/已关闭的剧情分支")
def resource_gm_branches() -> str:
    return loader.read_gm_rule("剧情分支树")


@mcp.resource("etera://gm/events",
              description="随机事件池：284个随机事件")
def resource_gm_events() -> str:
    return loader.read_gm_rule("随机事件池")


@mcp.resource("etera://gm/seals",
              description="封印知识框架：七封印节点与崩溃五阶段")
def resource_gm_seals() -> str:
    return loader.read_gm_rule("封印知识框架")


@mcp.resource("etera://npc/{name}",
              description="读取指定 NPC 的完整档案")
def resource_npc(name: str) -> str:
    return loader.parse_npc(name)


@mcp.resource("etera://npc/index",
              description="NPC 数据库优先级索引")
def resource_npc_index() -> str:
    return loader.read_npc_index()


# ═══════════════════════════════════════════════════════════
# 工具 Tools — GM 可以调用的操作与判定
# ═══════════════════════════════════════════════════════════

@mcp.tool(description="读取任意 .md 文件。path 为相对项目根目录的路径，如 GM判定信息/GM准则.md")
def read_file(path: str) -> str:
    return loader.read_file(path)


@mcp.tool(description="列出指定子目录下的所有 .md 文件。subdir 为空则列出根目录。")
def list_files(subdir: str = "") -> str:
    files = loader.list_md_files(subdir)
    if not files:
        return "该目录下没有 .md 文件。"
    lines = [f"{f['path']}  ({f['size']} bytes)" for f in files]
    return f"共 {len(files)} 个文件：\n" + "\n".join(lines)


@mcp.tool(description="列出 NPC 数据库中的所有角色文件。")
def list_npc_database() -> str:
    files = loader.read_npc_database_files()
    lines = [f"  {f['name']}" for f in files if not f['name'].startswith('_')]
    specials = [f"  {f['name']}" for f in files if f['name'].startswith('_')]
    result = f"共 {len(files)} 个文件\n"
    if specials:
        result += "\n系统文件：\n" + "\n".join(specials) + "\n"
    result += "\nNPC角色：\n" + "\n".join(lines)
    return result


@mcp.tool(description="""掷骰判定。formula 格式如 '2d6+3'（两个六面骰+3加值）、'd20'、'3d8-2'。
返回每个骰子的点数、加值、总和。""")
def gm_roll(formula: str) -> str:
    """掷骰子。支持格式: NdS+M（N个S面骰，加值M）"""
    import random
    import re

    pattern = r'^(\d+)?d(\+?\d+)([+-]\d+)?$'
    m = re.match(pattern, formula.replace(' ', ''))
    if not m:
        return f"格式错误：'{formula}'。请用 NdS+M 格式，如 2d6+3"

    count = int(m.group(1)) if m.group(1) else 1
    sides = int(m.group(2))
    modifier = int(m.group(3)) if m.group(3) else 0

    if count < 1 or sides < 1:
        return "骰子参数无效。"
    if count > 100:
        return "骰子数量不能超过 100。"

    rolls = [random.randint(1, sides) for _ in range(count)]
    total = sum(rolls) + modifier

    parts = []
    if count > 1:
        parts.append(f"[{' + '.join(map(str, rolls))}]")
    parts.append(str(sum(rolls)))
    if modifier != 0:
        parts.append(f"{'+' if modifier > 0 else '-'}{abs(modifier)}")
        parts.append(f"= {total}")

    return f"🎲 {formula} → {' '.join(parts)}"


@mcp.tool(description="""推进游戏时间并触发联动脚本。
hours: 推进的时辰数（1-10）
location: 当前地点（用于随机事件）
season: 季节（春/夏/秋/冬）
time_period: 当前时段（晨时/朝时/午时/夕时/昏时/夜时/暗时）""")
def advance_time(
    hours: int,
    location: str = "磨坊镇",
    season: str = "秋",
    time_period: str = ""
) -> str:
    """推进游戏时间，运行日历检查和事件脚本。"""
    results = [f"⏳ 推进 {hours} 时辰..."]
    cal = scripts.calendar_check(1782, 9, 5)
    results.append(f"\n【日历】{cal}")

    if season and location:
        tp = time_period if time_period else "朝时"
        events = scripts.event_picker(location, season, tp)
        results.append(f"\n【事件】{events}")

    weather = scripts.weather_roll("当前", season)
    results.append(f"\n【天气】{weather}")

    return "\n".join(results)


@mcp.tool(description="""计算旅行参数。
origin: 出发地
destination: 目的地
method: 交通方式（步行/骑马/马车/船运）""")
def travel_calc(origin: str, destination: str, method: str = "步行") -> str:
    return scripts.travel_calc(origin, destination, method)


@mcp.tool(description="""战斗简报：根据敌我双方参数预估战斗结果。
params 为字典，包含玩家和敌人的属性数据。""")
def combat_brief(params: str) -> str:
    """传入 JSON 格式的战斗参数。"""
    try:
        parsed = json.loads(params) if isinstance(params, str) else params
        return scripts.combat_brief(**parsed)
    except (json.JSONDecodeError, TypeError) as e:
        return f"参数解析错误：{e}。请传入 JSON 格式的参数字典。"


@mcp.tool(description="""技能判定：判断玩家的技能尝试是否成功。
attr: 对应属性值 (STR/DEX/CON/INT/WIS/CHA)
skill_lv: 技能等级（0-5）
env_mod: 环境修正值 (默认0)
dc: 难度等级 (目标值)""")
def dc_check(attr: int, skill_lv: int, env_mod: int = 0, dc: int = 10) -> str:
    return scripts.dc_check(attr, skill_lv, env_mod, dc)


@mcp.tool(description="""休息恢复计算。
con: 体质值
int_: 智力值
duration: 休息时长（夜睡/短休/长休）
quality: 休息质量（旅馆舒适/野外露宿/篝火小憩等）""")
def rest_calc(con: int, int_: int, duration: str, quality: str = "普通") -> str:
    return scripts.rest_calc(con, int_, duration, quality)


@mcp.tool(description="""分析 NPC 在给定刺激下的行为倾向。
npc_name: NPC 名称
trigger: 触发事件描述
attitude: NPC 对玩家的当前态度（友好/中立/敌对/警惕）""")
def npc_reaction(npc_name: str, trigger: str, attitude: str = "中立") -> str:
    """基于 NPC 性格和当前状态分析行为倾向。

    此工具从 NPC 档案中提取性格信息，结合触发事件给出行为判断。
    实际游戏中的最终行为由 GM（LLM）综合叙事决定。
    """
    npc_data = loader.parse_npc(npc_name)
    # 提取性格部分
    personality_section = ""
    in_personality = False
    for line in npc_data.split("\n"):
        if "性格" in line or "性情" in line:
            in_personality = True
        if in_personality:
            personality_section += line + "\n"
            if line.strip() == "" and len(personality_section) > 200:
                break

    return (
        f"## NPC: {npc_name}\n"
        f"态度: {attitude}\n"
        f"触发: {trigger}\n\n"
        f"### 性格参考\n{personality_section if personality_section else '(无性格数据)'}\n\n"
        f"> GM 请根据以上性格信息，结合当前叙事综合判断 NPC 行为。"
    )


@mcp.tool(description="""语义搜索世界设定。
query: 搜索关键词（自然语言）
top_k: 返回结果数量（默认3，最多10）""")
def search_lore(query: str, top_k: int = 3) -> str:
    k = min(max(top_k, 1), 10)
    results = lore.search(query, k)
    if not results:
        return f"未找到与「{query}」相关的设定。"

    lines = [f"## 与「{query}」相关的设定\n"]
    for i, r in enumerate(results, 1):
        source = r.get("source", "?")
        heading = r.get("heading", "")
        score = r.get("score", 0)
        content = r.get("content", "")
        # 截取内容到合理长度
        if len(content) > 1000:
            content = content[:1000] + "\n...(后略)"
        lines.append(f"---\n### {i}. {heading}\n*来源: {source}*\n\n{content}")

    return "\n".join(lines)


@mcp.tool(description="""将内容写入指定的 .md 文件。
path: 相对项目根目录的文件路径（如 玩家可知信息/游戏存档/纪元1782年_果月_日曜日.md）
content: 文件完整内容。此操作会覆盖文件原有内容。""")
def update_file(path: str, content: str) -> str:
    """写入或覆盖一个 .md 文件。"""
    try:
        full_path = loader.resolve(path)
        full_path.parent.mkdir(parents=True, exist_ok=True)
        full_path.write_text(content, encoding="utf-8")
        return f"✅ 已写入: {path} ({len(content)} 字符)"
    except (PermissionError, OSError) as e:
        return f"❌ 写入失败: {e}"
    except Exception as e:
        return f"❌ 错误: {e}"


@mcp.tool(description="""追加内容到游戏存档文件。
date_path: 日期路径（如 纪元1782年_果月_日曜日）
entry: 追加的剧情条目""")
def append_story_log(date_path: str, entry: str) -> str:
    """追加内容到当天的游戏存档。"""
    file_path = f"玩家可知信息/游戏存档/{date_path}.md"
    try:
        full_path = loader.resolve(file_path)
        full_path.parent.mkdir(parents=True, exist_ok=True)
        existing = full_path.read_text(encoding="utf-8") if full_path.exists() else ""
        # 自动编号
        existing_lines = existing.strip().split("\n")
        last_num = 0
        for line in existing_lines:
            if line.strip().startswith("1. ") or line.strip().startswith("2. "):
                parts = line.strip().split(". ", 1)
                try:
                    n = int(parts[0])
                    last_num = max(last_num, n)
                except ValueError:
                    pass
        new_entry = f"\n{last_num + 1}. {entry}"
        full_path.write_text(existing + new_entry, encoding="utf-8")
        return f"✅ 已追加到 {file_path}"
    except Exception as e:
        return f"❌ 写入失败: {e}"


@mcp.tool(description="""同步 NPC 状态：从推演日志中提取 META 行更新 NPC 数据库。
应在每日结束时调用。""")
def sync_npc_state() -> str:
    return scripts.npc_sync()


@mcp.tool(description="""更新玩家面板中的数值。
updates 为 JSON 字符串，如 {"HP": 95, "SP": 60, "金钱": "铜麦穗 × 25"}。
支持的键：HP, SP, MP, 金钱, 位置, 物品增减, 技能变化。""")
def update_player(updates: str) -> str:
    """更新玩家面板指定数值。"""
    try:
        data = json.loads(updates)
    except json.JSONDecodeError as e:
        return f"参数解析错误: {e}"

    profile_path = loader.resolve("玩家可知信息/玩家档案.md")
    content = profile_path.read_text(encoding="utf-8")
    changes = []

    for key, value in data.items():
        if key == "HP":
            content = _update_table_value(content, "生命值\\(HP\\)", f"{value}")
            changes.append(f"HP → {value}")
        elif key == "SP":
            content = _update_table_value(content, "体力值\\(SP\\)", f"{value}")
            changes.append(f"SP → {value}")
        elif key == "MP":
            content = _update_table_value(content, "魔力值\\(MP\\)", f"{value}")
            changes.append(f"MP → {value}")
        elif key == "金钱":
            content = _update_section(content, "金钱", value)
            changes.append(f"金钱 → {value}")
        elif key == "位置":
            content = _update_item(content, "位置", value)
        elif key.startswith("物品"):
            content = _update_section(content, "持有物品", value)
            changes.append(f"物品已更新")
        elif key.startswith("技能"):
            content = _update_section(content, "已学技能", value)
            changes.append(f"技能已更新")

    profile_path.write_text(content, encoding="utf-8")
    return f"✅ 玩家已更新: {', '.join(changes)}" if changes else "无变更。"


def _update_table_value(text: str, key_pattern: str, new_value: str) -> str:
    """Replace value in a markdown table row by matching the key column."""
    import re
    pattern = rf"(\|\s*{key_pattern}\s*\|\s*)[^|]*(\s*\|)"
    replacement = rf"\g<1>{new_value}\g<2>"
    return re.sub(pattern, replacement, text)


def _update_section(text: str, section_name: str, new_content: str) -> str:
    """Replace content under a ## heading."""
    import re
    pattern = rf"(##\s*{section_name}\s*\n\n).*?(?=\n##|\Z)"
    replacement = rf"\g<1>{new_content}"
    return re.sub(pattern, replacement, text, flags=re.DOTALL)


def _update_item(text: str, key: str, value: str) -> str:
    """Update a specific line item."""
    import re
    return re.sub(
        rf"(\|\s*{key}\s*\|\s*)[^|]*(\s*\|)",
        rf"\g<1>{value}\g<2>",
        text
    )


@mcp.tool(description="""获取当前场景的完整上下文。
一次性读取：玩家面板、当前任务、已知NPC、世界状态 + 指定地点的完整设定。
location: 当前地点名称
npcs: 当前在场的 NPC 列表（逗号分隔）""")
def get_scene_context(location: str = "", npcs: str = "") -> str:
    parts = ["# 场景上下文（自动加载）\n"]

    # 核心数据
    parts.append("---\n## 玩家面板")
    parts.append(loader.read_player_profile())

    parts.append("\n---\n## 当前任务")
    parts.append(loader.read_active_quests())

    parts.append("\n---\n## 世界状态")
    parts.append(loader.read_world_state())

    # 加载地点数据
    if location:
        loc_path = f"世界模拟信息/地图/{location}.md"
        loc_content = loader.read_file(loc_path)
        if "未找到" not in loc_content:
            parts.append(f"\n---\n## 当前地点: {location}")
            parts.append(loc_content)

    # 加载 NPC 数据
    if npcs:
        for npc_name in [n.strip() for n in npcs.split(",") if n.strip()]:
            npc_content = loader.parse_npc(npc_name)
            if "未找到" not in npc_content:
                parts.append(f"\n---\n## 在场NPC: {npc_name}")
                npc_lines = npc_content.split("\n")
                # 只取基本信息部分（~40行）
                parts.append("\n".join(npc_lines[:60]))
                if len(npc_lines) > 60:
                    parts.append("...(完整档案可通过 resource etera://npc/{name} 查询)")

    return "\n".join(parts)


@mcp.tool(description="""列出所有可用的 MCP 资源（Resources）。
方便 GM 了解可以查询哪些数据。""")
def list_resources() -> str:
    resources = [
        ("etera://player/profile", "玩家面板"),
        ("etera://player/quests", "当前任务"),
        ("etera://player/map", "已知地图"),
        ("etera://player/known-npcs", "已知NPC名录"),
        ("etera://world/state", "世界状态"),
        ("etera://world/calendar", "日期与时间规则"),
        ("etera://world/log", "世界推演日志"),
        ("etera://world/factions", "势力动态"),
        ("etera://world/calendar-events", "世界日历"),
        ("etera://gm/rules", "GM核心准则"),
        ("etera://gm/output-format", "输出格式规范"),
        ("etera://gm/update-checklist", "文件更新触发清单"),
        ("etera://gm/whitelist", "玩家可知内容白名单"),
        ("etera://gm/behavior-rules", "玩家信息与行为准则（合并版）"),
        ("etera://gm/tech-restrictions", "科技限制清单"),
        ("etera://gm/hidden-info", "角色隐藏信息"),
        ("etera://gm/foreshadowing", "伏笔追踪"),
        ("etera://gm/branches", "剧情分支树"),
        ("etera://gm/events", "随机事件池"),
        ("etera://gm/seals", "封印知识框架"),
        ("etera://npc/{name}", "NPC档案（替换 {name} 为角色名）"),
        ("etera://npc/index", "NPC索引"),
    ]
    lines = [f"  {uri:40s}  {desc}" for uri, desc in resources]
    return "可用资源:\n\n" + "\n".join(lines)


@mcp.tool(description="""列出所有可用的工具（Tools）。
方便 GM 了解可以执行哪些操作。""")
def list_tools() -> str:
    tools = [
        ("read_file", "读取任意 .md 文件"),
        ("list_files", "列出目录中的 .md 文件"),
        ("list_npc_database", "列出所有 NPC 角色"),
        ("gm_roll", "掷骰判定 (2d6+3)"),
        ("advance_time", "推进时间并触发脚本"),
        ("travel_calc", "计算旅行参数"),
        ("combat_brief", "战斗预估"),
        ("dc_check", "技能判定"),
        ("rest_calc", "休息恢复计算"),
        ("npc_reaction", "NPC行为倾向分析"),
        ("search_lore", "语义搜索世界设定"),
        ("update_file", "写入/覆盖 .md 文件"),
        ("append_story_log", "追加剧情记录"),
        ("update_player", "更新玩家面板数值"),
        ("sync_npc_state", "同步NPC状态"),
        ("get_scene_context", "获取完整场景上下文"),
    ]
    lines = [f"  {name:25s}  {desc}" for name, desc in tools]
    return "可用工具:\n\n" + "\n".join(lines)


# ── 启动入口 ──────────────────────────────────────────────

def main():
    print(f"🌍 埃塞拉世界引擎启动", file=sys.stderr)
    print(f"   根目录: {WORLD_ROOT}", file=sys.stderr)
    print(f"   脚本: {SCRIPTS_DIR}", file=sys.stderr)
    print(f"   向量检索: {'✅ 已就绪' if lore._initialized else '⏳ 按需初始化'}", file=sys.stderr)
    print(file=sys.stderr)
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
