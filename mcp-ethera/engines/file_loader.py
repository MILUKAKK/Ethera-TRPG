"""Read and parse .md files from the Ethera world project."""

import os
from pathlib import Path
from typing import Optional


class FileLoader:
    """Reads .md files from the Ethera world project.

    All files are read in full — no compression, no summarization.
    """

    def __init__(self, root: str | Path):
        self.root = Path(root)
        if not self.root.exists():
            raise FileNotFoundError(f"World root not found: {root}")

    def resolve(self, relative_path: str) -> Path:
        """Resolve a relative path (forward-slash separated) against root."""
        # Normalize: "GM判定信息/GM准则.md" -> Path
        clean = relative_path.replace("/", os.sep).replace("\\", os.sep)
        path = (self.root / clean).resolve()
        # Security: ensure it stays within project root
        if not str(path).startswith(str(self.root.resolve())):
            raise PermissionError(f"Access denied: {relative_path} is outside project root")
        return path

    def read_file(self, relative_path: str) -> str:
        """Read a .md file in full, return as string."""
        path = self.resolve(relative_path)
        if not path.exists():
            # Try with .md extension
            path = path.with_suffix(".md")
        if not path.exists():
            # Search recursively
            found = list(self.root.rglob(f"{path.name}"))
            if found:
                path = found[0]
            else:
                return f"# 文件未找到\n\n`{relative_path}` 不存在。"
        return path.read_text(encoding="utf-8")

    def list_md_files(self, subdir: str = "") -> list[dict]:
        """List all .md files in a subdirectory, with relative paths."""
        search_dir = self.root / subdir if subdir else self.root
        files = []
        for f in sorted(search_dir.rglob("*.md")):
            rel = f.relative_to(self.root)
            files.append({
                "path": str(rel).replace(os.sep, "/"),
                "name": f.stem,
                "size": f.stat().st_size,
            })
        return files

    def parse_npc(self, name: str) -> str:
        """Read a specific NPC file from NPC database."""
        # Try exact name
        path = self.root / "世界模拟信息" / "NPC数据库" / f"{name}.md"
        if path.exists():
            return path.read_text(encoding="utf-8")
        # Search recursively
        for f in (self.root / "世界模拟信息" / "NPC数据库").rglob(f"{name}.md"):
            return f.read_text(encoding="utf-8")
        # Try with prefix/suffix patterns
        for f in (self.root / "世界模拟信息" / "NPC数据库").rglob("*.md"):
            if name in f.stem:
                return f.read_text(encoding="utf-8")
        return f"# NPC未找到\n\n`{name}` 不在NPC数据库中。"

    def read_npc_index(self) -> str:
        """Read NPC priority index."""
        return self.read_file("世界模拟信息/NPC数据库/_优先级索引.md")

    def read_player_profile(self) -> str:
        """Read player panel."""
        return self.read_file("玩家可知信息/玩家档案.md")

    def read_active_quests(self) -> str:
        """Read quest system data."""
        return self.read_file("世界模拟信息/任务.md")

    def read_known_map(self) -> str:
        """Read main continent map."""
        return self.read_file("世界模拟信息/地图/埃塞拉大陆.md")

    def read_known_npcs(self) -> str:
        """Read NPC database index."""
        return self.read_file("世界模拟信息/NPC数据库/_优先级索引.md")

    def read_world_state(self) -> str:
        """Read world state."""
        return self.read_file("世界模拟信息/世界运行/世界状态.md")

    def read_world_calendar(self) -> str:
        """Read calendar and time rules."""
        return self.read_file("世界模拟信息/世界运行/日期与时间规则.md")

    def read_world_log(self) -> str:
        """Read world simulation log."""
        return self.read_file("世界模拟信息/世界运行/世界推演日志.md")

    def read_faction_dynamics(self) -> str:
        """Read faction dynamics."""
        return self.read_file("世界模拟信息/世界运行/势力动态.md")

    def read_world_calendar_events(self) -> str:
        """Read world calendar events."""
        return self.read_file("世界模拟信息/世界运行/世界日历.md")

    def read_gm_rule(self, rule_name: str) -> str:
        """Read a GM rule file by name (with or without .md)."""
        path = self.root / "GM判定规则" / f"{rule_name}.md"
        if not path.exists():
            path = self.root / "GM判定规则" / rule_name
        if path.exists():
            return path.read_text(encoding="utf-8")
        return f"# 规则未找到\n\n`{rule_name}` 不在GM判定信息目录中。"

    def read_npc_database_files(self) -> list[dict]:
        """List all NPC database files."""
        npc_dir = self.root / "世界模拟信息" / "NPC数据库"
        files = []
        for f in sorted(npc_dir.glob("*.md")):
            rel = f.relative_to(self.root)
            files.append({
                "path": str(rel).replace(os.sep, "/"),
                "name": f.stem,
            })
        return files
