"""
角色相关数据结构、库的类和加载/保存方法。
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import json
from typing import List, Dict, Any, Optional

from utils.path import CHAR_PATH, ensure_dir


class Character:
    def __init__(self, name: str, fixed_attributes: Dict[str, Any]):
        self.name = name
        self.fixed_attributes = fixed_attributes
        self.levels: Dict[int, Dict[str, Any]] = {}
        # 新增：技能倍率数据，格式为 {技能名称: {技能等级: [段1倍率, 段2倍率, ...]}}
        self.skill_multipliers: Dict[str, Dict[int, List[float]]] = {}

    def add_level(self, level: int, attributes: Dict[str, Any]) -> None:
        self.levels[level] = attributes

    def get_levels(self) -> List[int]:
        return sorted(self.levels.keys())

    def get_fixed_attribute(self, attr_name: str, default=None) -> Any:
        return self.fixed_attributes.get(attr_name, default)

    def get_level_attribute(self, level: int, attr_name: str, default=None) -> Any:
        level_data = self.levels.get(level)
        if level_data:
            return level_data.get(attr_name, default)
        return default

    def get_attribute(self, attr_name: str, level: Optional[int] = None, default=None) -> Any:
        if level is not None:
            return self.get_level_attribute(level, attr_name, default)
        else:
            return self.get_fixed_attribute(attr_name, default)
   
    def set_skill_multipliers(self, skill_data: Dict[str, Dict[int, List[float]]]) -> None:       
        # 设置角色的技能倍率数据。
        # :param skill_data: 格式为 {技能名称: {技能等级: [倍率列表]}}
        # 例如：{"战技": {1: [1.56], 2: [1.71], ...},
        # "连携技": {1: [0.45, 1.78], 2: [0.49, 1.96], ...}}
        # data意思是外部传入的,multipliers意思是用于后续程序的

        self.skill_multipliers = skill_data

    def get_skill_multiplier(self, skill_name: str, skill_level: int, segment: int = 0) -> Optional[float]:     
        # 获取技能指定等级指定段的倍率。
        # :param skill_name: 技能名称，如 "战技"、"连携技"、"终结技"
        # :param skill_level: 技能等级 (1-12)
        # :param segment: 段索引,从0开始,0表示第一段
        # :return: 倍率值（浮点数）,若不存在则返回None   

        skill_levels = self.skill_multipliers.get(skill_name)      
        # 外部输入技能名字,也就是skill_name
        # 让skill_levels 变成上面方法得到的数据里 名字相同的那个数据

        if skill_levels:
            segments = skill_levels.get(skill_level)
            if segments and segment < len(segments):
                return segments[segment]
        return None
        # skill_name：技能名称，决定查哪个技能
        # skill_level：技能的等级
        # segment：第几段倍率（有些技能一段，有些多段，需要根据index取）
        # 返回值：技能倍率（float）
        # 若有任何一步查找失败（如技能名或等级不存在，或段数越界），返回 None，防止程序报错
        # 这段代码是多层级的安全取值逻辑
        # 核心目的是：从「技能倍率数据」中精准获取指定技能、指定等级、指定段的倍率值
        

    def to_dict(self) -> Dict:
        # 该方法把当前对象的数据打包成标准dict（字典）格式
        # 方便后续做 JSON 序列化

        return {
            "name": self.name,
            # 保存角色/对象名字

            "fixed": self.fixed_attributes,
            # 固定属性（比如基础攻击、防御、生命等），直接用原本的 dict 格式输出
            # "levels" 用于存储不同等级（通常是角色、武器等每个等级的属性）

            "levels": {str(level): attrs for level, attrs in self.levels.items()},  
            # "levels" 用于存储不同等级（通常是角色、武器等每个等级的属性）
            # level 原本可能是整数型（如 1,2,3...），但在 JSON 规范或前端传输中通常习惯用字符串作为 key。
            # 这句代码就是把原来整数 key 全部转成字符串，确保兼容性
            # 原数据：{1: {...}, 2: {...}}
            # to_dict后：{"1": {...}, "2": {...}}
        
            "skill_multipliers": {
                skill_name: {str(level): seg_list for level, seg_list in level_dict.items()}
                for skill_name, level_dict in self.skill_multipliers.items()
            }
            # 多层结构：技能名 → 等级 → 倍率数组。
            # 最外层遍历所有技能名 (skill_name)，每个技能内部又是一个 level_dict。
            # 技能等级同理，也转字符串 key： {str(level): seg_list for level, seg_list in level_dict.items()}
            # 原数据：{"战技": {1: [1.5], 2: [1.7]}}
            # to_dict后：{"战技": {"1": [1.5], "2": [1.7]}}
        }

    @classmethod
    def from_dict(cls, data: Dict) -> "Character":
        c = cls(data["name"], data["fixed"])
        for level_str, attrs in data["levels"].items():
            c.add_level(int(level_str), attrs)
        # 新增：从字典恢复技能倍率数据
        if "skill_multipliers" in data:
            skill_data = {}
            for skill_name, level_dict in data["skill_multipliers"].items():
                skill_data[skill_name] = {int(level): seg_list for level, seg_list in level_dict.items()}
            c.set_skill_multipliers(skill_data)
        return c

    def __repr__(self):
        return f"Character(name={self.name!r}, fixed={self.fixed_attributes}, levels={list(self.levels.keys())}, skills={list(self.skill_multipliers.keys())})"


class CharacterLibrary:
    def __init__(self):
        self.characters: List[Character] = []

    def add_character(self, character: Character):
        self.characters.append(character)

    def find_character_by_name(self, name: str) -> Optional[Character]:
        for c in self.characters:
            if c.name == name:
                return c
        return None

    def filter_characters(self, star: Optional[int] = None, character_type: Optional[str] = None) -> List[Character]:
        result = []
        for c in self.characters:
            if star is not None and c.get_attribute("星级", default=None) != star:
                continue
            if character_type is not None and c.get_attribute("类型", default=None) != character_type:
                continue
            result.append(c)  # 通过所有过滤条件的角色加入结果
        return result

    def to_dict_list(self) -> List[Dict]:
        return [c.to_dict() for c in self.characters]

    @classmethod
    def from_dict_list(cls, data: List[Dict]) -> "CharacterLibrary":
        lib = cls()
        for item in data:
            lib.add_character(Character.from_dict(item))
        return lib


def load_character_library(filename: str = None) -> CharacterLibrary:
    if filename is None:
        filename = CHAR_PATH
    try:
        with open(filename, "r", encoding="utf-8") as f:
            data = json.load(f)
        return CharacterLibrary.from_dict_list(data)
    except FileNotFoundError:
        return CharacterLibrary()

def save_character_library(lib: CharacterLibrary, filename: str = None):
    if filename is None:
        filename = CHAR_PATH
    ensure_dir(filename)
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(lib.to_dict_list(), f, indent=2, ensure_ascii=False)

if __name__ == "__main__":
    from model.add_character import main
    main()


