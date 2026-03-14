#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
添加角色示例数据到库中，并保存到文件。
"""

from model.character import Character, CharacterLibrary, save_character_library
from utils.path import CHAR_PATH


def main():
    lib = CharacterLibrary()

    管理员 = Character("管理员", {"星级": 6, "类型": "近卫", "武器": "单手剑", "属性": "物理",
                        "主能力": "敏捷", "副能力": "力量", "暴击率": "0.05", "暴击效果": "0.5"})

    管理员.add_level(1,  {"等级": 1, "攻击力": 30, "力量": 14, "敏捷": 14, "智识": 9, "意志": 10, "敏捷+": 0})
    管理员.add_level(20, {"等级": 20, "攻击力": 92, "力量": 38, "敏捷": 41, "智识": 28, "意志": 31, "敏捷+": 0})
    管理员.add_level(40, {"等级": 40, "攻击力": 157, "力量": 62, "敏捷": 69, "智识": 47, "意志": 53, "敏捷+": 10})
    管理员.add_level(60, {"等级": 60, "攻击力": 222, "力量": 86, "敏捷": 98, "智识": 67, "意志": 74, "敏捷+": 25})
    管理员.add_level(80, {"等级": 80, "攻击力": 287, "力量": 111, "敏捷": 126, "智识": 87, "意志": 96, "敏捷+": 40})
    管理员.add_level(90, {"等级": 90, "攻击力": 319, "力量": 123, "敏捷": 140, "智识": 96, "意志": 107, "敏捷+": 60})

    # 技能倍率数据
    战技倍率列表 = [1.56, 1.71, 1.87, 2.02, 2.18, 2.34, 2.49, 2.65, 2.80, 3.00, 3.23, 3.50]
    连携技段1 = [0.45, 0.49, 0.54, 0.58, 0.62, 0.67, 0.71, 0.76, 0.80, 0.86, 0.93, 1.00]
    连携技段2 = [1.78, 1.96, 2.13, 2.31, 2.49, 2.67, 2.84, 3.02, 3.20, 3.42, 3.69, 4.00]
    终结技段1 = [3.56, 3.91, 4.27, 4.62, 4.98, 5.33, 5.69, 6.04, 6.40, 6.84, 7.38, 8.00]
    终结技段2 = [2.67, 2.94, 3.20, 3.47, 3.74, 4.00, 4.27, 4.54, 4.80, 5.14, 5.54, 6.00]

    skill_data = {
        "战技": {i+1: [战技倍率列表[i]] for i in range(12)},
        "连携技": {i+1: [连携技段1[i], 连携技段2[i]] for i in range(12)},
        "终结技": {i+1: [终结技段1[i], 终结技段2[i]] for i in range(12)}
    }
    管理员.set_skill_multipliers(skill_data)

    lib.add_character(管理员)

    save_character_library(lib)
    print(f"角色库已保存到 {CHAR_PATH}")

    # 加载验证
    from model.character import load_character_library
    loaded_lib = load_character_library()
    print("从文件加载的角色库：")
    for c in loaded_lib.characters:
        print(c)
        for lv in c.get_levels():
            atk = c.get_level_attribute(lv, "攻击力", "?")
            print(f"  等级 {lv}: 攻击力 {atk}")
        print("  技能倍率示例(等级1):")
        for skill_name in ["战技", "连携技", "终结技"]:
            if skill_name == "战技":
                print(f"    战技 Lv1: {c.get_skill_multiplier('战技', 1, 0)*100:.1f}%")
            elif skill_name == "连携技":
                print(f"    连携技 Lv1: 段1 {c.get_skill_multiplier('连携技', 1, 0)*100:.1f}%, 段2 {c.get_skill_multiplier('连携技', 1, 1)*100:.1f}%")
            elif skill_name == "终结技":
                print(f"    终结技 Lv1: 段1 {c.get_skill_multiplier('终结技', 1, 0)*100:.1f}%, 段2 {c.get_skill_multiplier('终结技', 1, 1)*100:.1f}%")

if __name__ == "__main__":
    main()


    