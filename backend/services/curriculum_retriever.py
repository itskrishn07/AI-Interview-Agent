import json
from typing import Dict, Any, List, Optional
from pathlib import Path
from backend.config import settings

class CurriculumDay(BaseModel if False else object):
    pass

class CurriculumRetriever:
    """Provides deterministic structured lookup over curriculum.json."""
    def __init__(self, curriculum_path: Optional[str] = None):
        path = curriculum_path or settings.CURRICULUM_PATH
        self._load(path)

    def _load(self, path: str):
        with open(path, "r", encoding="utf-8") as f:
            self.raw_data = json.load(f)
        
        self.modules = self.raw_data.get("modules", [])
        self.days_map: Dict[int, Dict[str, Any]] = {}
        for d in self.raw_data.get("days", []):
            self.days_map[d["day"]] = d

    def get_day(self, day_num: int) -> Optional[Dict[str, Any]]:
        return self.days_map.get(day_num)

    def get_all_days(self) -> List[Dict[str, Any]]:
        return list(self.days_map.values())

    def get_available_day_numbers(self) -> List[int]:
        return sorted(list(self.days_map.keys()))

    def get_module_for_day(self, day_num: int) -> Optional[Dict[str, Any]]:
        for mod in self.modules:
            days = mod.get("days", [])
            if len(days) == 2 and days[0] <= day_num <= days[1]:
                return mod
        return None

    def format_day_summary(self, day_num: int) -> str:
        day_info = self.get_day(day_num)
        if not day_info:
            return f"Day {day_num}"
        
        mod_info = self.get_module_for_day(day_num)
        mod_title = mod_info.get("title", "") if mod_info else ""
        
        title = day_info.get("title", "")
        tools = ", ".join(day_info.get("tools", []))
        objectives = "\n- ".join(day_info.get("objectives", []))
        
        return f"Day {day_num}: {title} (Module: {mod_title})\nTools: {tools}\nObjectives:\n- {objectives}"

curriculum_retriever = CurriculumRetriever()
