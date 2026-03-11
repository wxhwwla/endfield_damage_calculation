# 遍历.py
from 计算 import compute_damage_values

def traverse_weapons(character, weapon_lib, skill, skill_level, character_level,
                     atk_percent, dmg_percent, crit_rate, crit_dmg,
                     weapon_level=1, temp_times=None):
    """
    遍历所有符合条件的武器，计算每个武器在不同临时效果层数下的非暴击伤害，并排序。
    :param character: 角色对象
    :param weapon_lib: 武器库对象
    :param skill: 技能名称
    :param skill_level: 技能等级
    :param character_level: 角色等级
    :param atk_percent: 攻击力加成%
    :param dmg_percent: 伤害加成%
    :param crit_rate: 暴击率%
    :param crit_dmg: 暴击伤害%
    :param weapon_level: 指定的武器等级
    :param temp_times: 如果为None，则遍历所有可能的层数；否则只遍历该指定层数
    :return: 排序后的字符串（制表符分隔）
    """
    weapon_type = character.get_fixed_attribute("武器")
    results = []

    for w in weapon_lib.weapons:
        if w.get_fixed_attribute("类型") != weapon_type:
            continue

        # 检查武器是否有指定的等级
        if weapon_level not in w.get_levels():
            continue

        # 获取武器的最大临时效果层数
        max_times = w.fixed_attributes.get("临时效果次数", 0)

        # 确定要遍历的层数列表
        if temp_times is not None:
            if temp_times > max_times:
                continue
            times_list = [temp_times]
        else:
            times_list = list(range(max_times + 1))

        for times in times_list:
            use_temp = times > 0
            try:
                vals = compute_damage_values(
                    character, w, skill, skill_level, character_level, weapon_level,
                    atk_percent, dmg_percent, crit_rate, crit_dmg,
                    use_temp_effect=use_temp, temp_effect_times=times
                )
            except ValueError:
                # 计算失败则跳过该条目
                continue
            non_crit = vals['non_crit']
            final_atk = vals['final_atk']
            results.append((w.name, times, final_atk, non_crit))

    # 按非暴击伤害从大到小排序
    results.sort(key=lambda x: x[3], reverse=True)

    # 生成输出字符串（使用制表符分隔，便于对齐）
    output = "武器名称\t临时效果层数\t最终攻击力\t非暴击伤害\n"
    for name, times, atk, dmg in results:
        output += f"{name}\t{times}\t{atk:.2f}\t{dmg:.2f}\n"
    return output


