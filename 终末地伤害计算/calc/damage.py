"""
伤害计算方法，包括单次伤害公式实现。
"""

def compute_damage_values(character, weapon, skill, skill_level, character_level, weapon_level,
                          atk_percent, dmg_percent, crit_rate, crit_dmg,
                          use_temp_effect, temp_effect_times, extra_multiplier=0.0):
    """
    计算伤害数值，返回字典包含 non_crit, crit, expect, final_atk
    """
    # ---------- 数据提取 ----------
    char_lv_data = character.levels.get(character_level)
    if char_lv_data is None:
        raise ValueError(f"角色等级 {character_level} 数据不存在！")

    char_fixed = character.fixed_attributes
    main_ability = char_fixed.get("主能力")
    sub_ability = char_fixed.get("副能力")
    char_element = char_fixed.get("属性")
    char_crit_rate = float(char_fixed.get("暴击率", 0))
    char_crit_dmg = float(char_fixed.get("暴击效果", 0))

    base_atk = char_lv_data.get("攻击力", 0)
    strength = char_lv_data.get("力量", 0)
    agility = char_lv_data.get("敏捷", 0)
    intellect = char_lv_data.get("智识", 0)
    will = char_lv_data.get("意志", 0)

    char_strength_plus = char_lv_data.get("力量+", 0)
    char_agility_plus = char_lv_data.get("敏捷+", 0)
    char_intellect_plus = char_lv_data.get("智识+", 0)
    char_will_plus = char_lv_data.get("意志+", 0)

    weapon_lv_data = weapon.levels.get(weapon_level, {})
    weapon_fixed = weapon.fixed_attributes

    weapon_base_atk = weapon_lv_data.get("基础攻击力", 0)
    weapon_atk_percent = weapon_lv_data.get("攻击力+", 0)
    weapon_add_atk_fixed = weapon_lv_data.get("附加攻击力+", 0)
    weapon_main_plus = weapon_lv_data.get("主能力+", 0)
    weapon_sub_plus = weapon_lv_data.get("副能力+", 0)
    weapon_strength_plus = weapon_lv_data.get("力量+", 0)
    weapon_agility_plus = weapon_lv_data.get("敏捷+", 0)
    weapon_intellect_plus = weapon_lv_data.get("智识+", 0)
    weapon_will_plus = weapon_lv_data.get("意志+", 0)

    type_damage = {
        "物理伤害+": weapon_lv_data.get("物理伤害+", 0),
        "法术伤害+": weapon_lv_data.get("法术伤害+", 0),
        "冰系伤害+": weapon_lv_data.get("冰系伤害+", 0),
        "火系伤害+": weapon_lv_data.get("火系伤害+", 0),
        "雷系伤害+": weapon_lv_data.get("雷系伤害+", 0),
        "草系伤害+": weapon_lv_data.get("草系伤害+", 0),
        "战技伤害+": weapon_lv_data.get("战技伤害+", 0),
        "连携技伤害+": weapon_lv_data.get("连携技伤害+", 0),
        "终结技伤害+": weapon_lv_data.get("终结技伤害+", 0)
    }
    skill_specific_damage = type_damage.get(f"{skill}伤害+", 0)

    persistent_effect = weapon_fixed.get("持续效果")
    persistent_strength = weapon_fixed.get("效果强度", 0)
    temp_effect = weapon_fixed.get("临时效果")
    # 兼容两种字段名：临时效果强度 或 临时附加强度
    temp_strength = weapon_fixed.get("临时效果强度", 0)
    if temp_strength == 0:
        temp_strength = weapon_fixed.get("临时附加强度", 0)
    weapon_temp_times = weapon_fixed.get("临时效果次数", 0)

    talents = []
    for i in range(1, 3):
        talent_name = f"天赋{i}"
        talent_effect = char_fixed.get(talent_name)
        if talent_effect:
            talent_strength = char_fixed.get(f"{talent_name}效果强度", 0)
            talent_times = char_fixed.get(f"{talent_name}效果次数", 0)
            talents.append((talent_effect, talent_strength, talent_times))

    skill_multipliers = character.skill_multipliers.get(skill, {}).get(skill_level)
    if skill_multipliers is None:
        raise ValueError("技能倍率数据缺失！")

    # ---------- 计算最终属性 ----------
    final_strength = strength + char_strength_plus + weapon_strength_plus
    final_agility = agility + char_agility_plus + weapon_agility_plus
    final_intellect = intellect + char_intellect_plus + weapon_intellect_plus
    final_will = will + char_will_plus + weapon_will_plus

    if main_ability == "力量":
        final_strength += weapon_main_plus
    elif main_ability == "敏捷":
        final_agility += weapon_main_plus
    elif main_ability == "智识":
        final_intellect += weapon_main_plus
    elif main_ability == "意志":
        final_will += weapon_main_plus

    if sub_ability == "力量":
        final_strength += weapon_sub_plus
    elif sub_ability == "敏捷":
        final_agility += weapon_sub_plus
    elif sub_ability == "智识":
        final_intellect += weapon_sub_plus
    elif sub_ability == "意志":
        final_will += weapon_sub_plus

    main_value = 0
    if main_ability == "力量":
        main_value = final_strength
    elif main_ability == "敏捷":
        main_value = final_agility
    elif main_ability == "智识":
        main_value = final_intellect
    elif main_ability == "意志":
        main_value = final_will

    sub_value = 0
    if sub_ability == "力量":
        sub_value = final_strength
    elif sub_ability == "敏捷":
        sub_value = final_agility
    elif sub_ability == "智识":
        sub_value = final_intellect
    elif sub_ability == "意志":
        sub_value = final_will

    ability_bonus = main_value * 0.005 + sub_value * 0.002

    extra_fixed_atk = 0
    if persistent_effect and persistent_strength != 0:
        if persistent_effect == "攻击力+":
            extra_fixed_atk += persistent_strength
    if use_temp_effect and temp_effect and temp_strength != 0 and temp_effect_times > 0:
        if temp_effect == "攻击力+":
            extra_fixed_atk += temp_strength * temp_effect_times
    for talent_effect, talent_strength, talent_times in talents:
        if talent_effect == "攻击力+" and talent_strength != 0:
            extra_fixed_atk += talent_strength * talent_times

    base_atk_sum = base_atk + weapon_base_atk
    total_atk_percent = weapon_atk_percent + atk_percent
    atk_after_percent = base_atk_sum * (1 + total_atk_percent / 100)
    total_fixed_atk = weapon_add_atk_fixed + extra_fixed_atk
    atk_before_ability = atk_after_percent + total_fixed_atk
    final_atk = atk_before_ability * (1 + ability_bonus)

    element_damage = 0
    if char_element:
        if char_element == "物理":
            element_damage = type_damage.get("物理伤害+", 0)
        elif char_element == "法术":
            element_damage = type_damage.get("法术伤害+", 0)
        elif char_element == "冰":
            element_damage = type_damage.get("冰系伤害+", 0)
        elif char_element == "火":
            element_damage = type_damage.get("火系伤害+", 0)
        elif char_element == "雷":
            element_damage = type_damage.get("雷系伤害+", 0)
        elif char_element == "草":
            element_damage = type_damage.get("草系伤害+", 0)

    total_damage_bonus = element_damage + skill_specific_damage + dmg_percent
    damage_multiplier = 1 + total_damage_bonus / 100

    total_crit_rate = char_crit_rate + crit_rate / 100.0
    total_crit_dmg = char_crit_dmg + crit_dmg / 100.0
    crit_multiplier = 1 + total_crit_rate * total_crit_dmg
    crit_damage_factor = 1 + total_crit_dmg

    total_skill_mult = sum(skill_multipliers)
    base_damage = total_skill_mult * final_atk

    defense_multiplier = 0.5
    extra_factor = 1 + extra_multiplier

    damage_no_crit = base_damage * damage_multiplier * defense_multiplier * extra_factor
    damage_crit = damage_no_crit * crit_damage_factor
    damage_expect = base_damage * crit_multiplier * damage_multiplier * defense_multiplier * extra_factor

    return {
        'non_crit': damage_no_crit,
        'crit': damage_crit,
        'expect': damage_expect,
        'final_atk': final_atk
    }

def calculate_single_damage(character, weapon, skill: str, skill_level: int,
                            character_level: int, weapon_level: int,
                            atk_percent: float, dmg_percent: float,
                            crit_rate: float, crit_dmg: float,
                            use_temp_effect: bool, temp_effect_times: int,
                            extra_multiplier: float = 0.0) -> str:
    """
    根据最终伤害公式计算单次伤害，返回详细结果字符串。
    """
    try:
        vals = compute_damage_values(
            character, weapon, skill, skill_level, character_level, weapon_level,
            atk_percent, dmg_percent, crit_rate, crit_dmg,
            use_temp_effect, temp_effect_times, extra_multiplier
        )
    except ValueError as e:
        return str(e)

    result_str = f"角色：{character.name} Lv.{character_level}\n"
    result_str += f"武器：{weapon.name} Lv.{weapon_level}\n"
    result_str += f"技能：{skill} Lv.{skill_level}\n"
    result_str += f"最终攻击力：{vals['final_atk']:.2f}\n"
    result_str += f"非暴击伤害：{vals['non_crit']:.2f}\n"
    result_str += f"暴击伤害：{vals['crit']:.2f}\n"
    result_str += f"期望伤害：{vals['expect']:.2f}\n"
    return result_str


