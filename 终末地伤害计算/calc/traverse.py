"""
批量遍历武器的排名功能、CSV导出等逻辑。
提出一个核心遍历内核 _traverse_weapons_results，只做遍历与数据汇总（返回list of tuple）。
traverse_weapons 用于输出字符串表格，给GUI文本框展示。
traverse_weapons_csv_data 用于输出 header, rows，给CSV导出
"""

from calc.damage import compute_damage_values

def _traverse_weapons_results(character, weapon_lib, skill, skill_level, character_level,
                             atk_percent, dmg_percent, crit_rate, crit_dmg,
                             weapon_level=1, temp_times=None):
    """
    内部核心遍历，返回所有武器所有层数的结果列表。
    :return: [(武器名, 层数, 最终攻击力, 非暴击伤害), ...]
    """
    weapon_type = character.get_fixed_attribute("武器")
    results = []
    for w in weapon_lib.weapons:
        if w.get_fixed_attribute("类型") != weapon_type:
            continue
        if weapon_level not in w.get_levels():
            continue
        max_times = w.fixed_attributes.get("临时效果次数", 0)
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
            except ValueError as e:
                print(f"武器 {w.name} times={times} 计算出错：", e)
                continue
            non_crit = vals['non_crit']
            final_atk = vals['final_atk']
            results.append((w.name, times, final_atk, non_crit))
    results.sort(key=lambda x: x[3], reverse=True)
    return results

def traverse_weapons(character, weapon_lib, skill, skill_level, character_level,
                     atk_percent, dmg_percent, crit_rate, crit_dmg,
                     weapon_level=1, temp_times=None):
    """
    输出用于GUI文本展示的字符串(带表头，列宽对齐)。
    """
    header = ["武器名称", "临时效果层数", "最终攻击力", "非暴击伤害"]
    results = _traverse_weapons_results(
        character, weapon_lib, skill, skill_level, character_level,
        atk_percent, dmg_percent, crit_rate, crit_dmg,
        weapon_level=weapon_level, temp_times=temp_times
    )
    rows = [header] + [[str(name), str(times), f"{atk:.2f}", f"{dmg:.2f}"] for name, times, atk, dmg in results]

    # 计算每列对齐宽度
    col_widths = [max(len(row[i]) for row in rows) for i in range(len(header))]
    output = ""
    for row in rows:
        output += "  ".join(row[i].ljust(col_widths[i]) for i in range(len(header))) + "\n"

    if not results:
        return "没有符合条件的武器，或所有计算都失败，请检查数据和筛选条件。"
    return output

def traverse_weapons_csv_data(character, weapon_lib, skill, skill_level, character_level,
                             atk_percent, dmg_percent, crit_rate, crit_dmg,
                             weapon_level=1, temp_times=None):
    """
    输出供CSV导出的结构(header, rows)。
    """
    header = ["武器名称", "临时效果层数", "最终攻击力", "非暴击伤害"]
    results = _traverse_weapons_results(
        character, weapon_lib, skill, skill_level, character_level,
        atk_percent, dmg_percent, crit_rate, crit_dmg,
        weapon_level=weapon_level, temp_times=temp_times
    )
    rows = [[name, times, f"{atk:.2f}", f"{dmg:.2f}"] for name, times, atk, dmg in results]
    return header, rows

def calculate_rank(character, weapon_lib, skill: str, skill_level: int,
                   character_level: int, weapon_level: int,
                   atk_percent: float, dmg_percent: float,
                   crit_rate: float, crit_dmg: float,
                   use_temp_effect: bool, temp_effect_times: int) -> str:
    """
    调用遍历模块进行排名计算。
    当 use_temp_effect=False 时，遍历所有层数；否则只遍历指定层数。
    :param character: 角色对象
    :param weapon_lib: 武器库对象
    :param skill: 技能名称
    :param skill_level: 技能等级
    :param character_level: 角色等级
    :param weapon_level: 指定的武器等级
    :param atk_percent: 攻击力加成%
    :param dmg_percent: 伤害加成%
    :param crit_rate: 暴击率%
    :param crit_dmg: 暴击伤害%
    :param use_temp_effect: 是否启用临时效果
    :param temp_effect_times: 临时效果叠加层数
    :return: 排序后的字符串
    """
    times_param = temp_effect_times if use_temp_effect else None
    result_str = traverse_weapons(
        character, weapon_lib, skill, skill_level, character_level,
        atk_percent, dmg_percent, crit_rate, crit_dmg,
        weapon_level=weapon_level,
        temp_times=times_param
    )
    return result_str


