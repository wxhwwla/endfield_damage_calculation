#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
添加武器示例数据到库中，并保存到文件。
"""

from model.weapon import Weapon, WeaponLibrary, save_weapon_library
from utils.path import WEAPON_PATH


def main():
    lib = WeaponLibrary()

    塔尔11 = Weapon("塔尔11", {"星级": 3, "类型": "单手剑"})
    塔尔11.add_level(1,  {"等级": 1, "基础攻击力": 29, "主能力+": 10, "附加攻击力+": 12})
    塔尔11.add_level(20, {"等级": 20, "基础攻击力": 83, "主能力+": 10, "附加攻击力+": 12})
    塔尔11.add_level(40, {"等级": 40, "基础攻击力": 140, "主能力+": 18, "附加攻击力+": 12})
    塔尔11.add_level(60, {"等级": 60, "基础攻击力": 197, "主能力+": 26, "附加攻击力+": 12})
    塔尔11.add_level(80, {"等级": 80, "基础攻击力": 254, "主能力+": 34, "附加攻击力+": 12})
    塔尔11.add_level(90, {"等级": 90, "基础攻击力": 283, "主能力+": 42, "附加攻击力+": 12})
    lib.add_weapon(塔尔11)

    浪潮 = Weapon("浪潮", {"星级": 4, "类型": "单手剑"})
    浪潮.add_level(1,  {"等级": 1, "基础攻击力": 34, "智识+": 12, "攻击力+": 3,
                        "临时效果": "攻击力+", "临时附加强度": 12, "临时效果次数": 1})
    浪潮.add_level(20, {"等级": 20, "基础攻击力": 100, "智识+": 12, "攻击力+": 3,
                        "临时效果": "攻击力+", "临时附加强度": 12, "临时效果次数": 1})
    浪潮.add_level(40, {"等级": 40, "基础攻击力": 169, "智识+": 21, "攻击力+": 3,
                        "临时效果": "攻击力+", "临时附加强度": 12, "临时效果次数": 1})
    浪潮.add_level(60, {"等级": 60, "基础攻击力": 238, "智识+": 21, "攻击力+": 5.4,
                        "临时效果": "攻击力+", "临时附加强度": 12, "临时效果次数": 1})
    浪潮.add_level(80, {"等级": 80, "基础攻击力": 307, "智识+": 31, "攻击力+": 5.4,
                        "临时效果": "攻击力+", "临时附加强度": 12, "临时效果次数": 1})
    浪潮.add_level(90, {"等级": 90, "基础攻击力": 341, "智识+": 31, "攻击力+": 7.8,
                        "临时效果": "攻击力+", "临时附加强度": 12, "临时效果次数": 1})
    lib.add_weapon(浪潮)

    save_weapon_library(lib)
    print(f"武器库已保存到 {WEAPON_PATH}")

    # 加载验证
    from model.weapon import load_weapon_library
    loaded_lib = load_weapon_library()
    print("从文件加载的武器库：")
    for w in loaded_lib.weapons:
        print(w)
        for lv in w.get_levels():
            atk = w.get_level_attribute(lv, "基础攻击力", "?")
            print(f"  等级 {lv}: 基础攻击力 {atk}")

if __name__ == "__main__":
    main()


    