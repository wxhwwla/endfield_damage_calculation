"""
目标：通过GUI选择角色、技能、武器，并计算伤害（骨架）
"""

import tkinter as tk
from tkinter import ttk
import tkinter.filedialog as fd
import tkinter.messagebox as mb
from typing import List, Optional, Dict
import csv
import sys
import os

# 将项目根目录添加到Python路径，以便导入自定义模块
current_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.dirname(current_dir)
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

# 导入人物库和武器库
from 汇总.人物类.人物 import CharacterLibrary, Character, load_library as load_char_lib
from 汇总.武器类.武器 import WeaponLibrary, Weapon, load_library as load_weapon_lib

# 导入计算模块
from 计算 import calculate_single_damage, calculate_rank

# 导入武器界面模块
from 武器界面 import WeaponSelectionFrame

class DamageCalculatorApp:
    """伤害计算器主应用程序类，管理整个GUI流程"""

    def __init__(self):
        # 加载数据
        self.char_lib = load_char_lib()
        self.weapon_lib = load_weapon_lib()

        # 状态变量（存储用户当前选择）
        self.selected_character = None
        self.selected_character_level = None   # 当前选中的角色等级
        self.selected_skill = None
        self.selected_skill_level = 1

        # 创建主窗口
        self.window = tk.Tk()
        self.window.title("伤害计算器")
        self.window.geometry("1080x960")
        self.window.state('zoomed')

        self.main_container = ttk.Frame(self.window)
        self.main_container.pack(fill=tk.BOTH, expand=True)

        # 初始化各个步骤的界面框架
        self.create_character_select_frame()
        self.create_skill_select_frame()
        self.create_weapon_select_frame()   # 创建武器界面

        # 默认显示第一步
        self.show_frame(self.character_frame)

        self.window.mainloop()

    # ---------- 辅助方法：切换框架 ----------
    def show_frame(self, frame):
        for child in self.main_container.winfo_children():
            child.pack_forget()
        frame.pack(fill=tk.BOTH, expand=True)

    # ---------- 第一步：角色选择界面 ----------
    def create_character_select_frame(self):
        self.character_frame = ttk.Frame(self.main_container)

        # 顶部过滤条件框架
        filter_frame = ttk.Frame(self.character_frame)
        filter_frame.pack(fill=tk.X, padx=10, pady=10)

        # 星级筛选
        ttk.Label(filter_frame, text="星级：").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        self.star_var = tk.StringVar()
        self.star_combo = ttk.Combobox(filter_frame, textvariable=self.star_var, state="readonly", width=10)
        all_stars = sorted(set(c.get_fixed_attribute("星级") for c in self.char_lib.characters if c.get_fixed_attribute("星级") is not None))
        star_values = ["全部"] + [str(s) for s in all_stars]
        self.star_combo['values'] = star_values
        self.star_combo.current(0)
        self.star_combo.grid(row=0, column=1, padx=5, pady=5)

        # 类型筛选
        ttk.Label(filter_frame, text="类型：").grid(row=0, column=2, padx=5, pady=5, sticky=tk.W)
        self.type_var = tk.StringVar()
        self.type_combo = ttk.Combobox(filter_frame, textvariable=self.type_var, state="readonly", width=15)
        all_types = sorted(set(c.get_fixed_attribute("类型") for c in self.char_lib.characters if c.get_fixed_attribute("类型") is not None))
        type_values = ["全部"] + all_types
        self.type_combo['values'] = type_values
        self.type_combo.current(0)
        self.type_combo.grid(row=0, column=3, padx=5, pady=5)

        # 搜索框
        ttk.Label(filter_frame, text="名称搜索：").grid(row=0, column=4, padx=5, pady=5, sticky=tk.W)
        self.search_var = tk.StringVar()
        self.search_entry = ttk.Entry(filter_frame, textvariable=self.search_var, width=20)
        self.search_entry.grid(row=0, column=5, padx=5, pady=5)

        # 搜索按钮
        search_btn = ttk.Button(filter_frame, text="搜索", command=self.update_character_list)
        search_btn.grid(row=0, column=6, padx=5, pady=5)

        # 角色列表
        list_frame = ttk.Frame(self.character_frame)
        list_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        columns = ("name", "star", "type")
        self.character_tree = ttk.Treeview(list_frame, columns=columns, show="headings", height=15)
        self.character_tree.heading("name", text="名称")
        self.character_tree.heading("star", text="星级")
        self.character_tree.heading("type", text="类型")
        self.character_tree.column("name", width=200)
        self.character_tree.column("star", width=80)
        self.character_tree.column("type", width=150)

        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.character_tree.yview)
        self.character_tree.configure(yscrollcommand=scrollbar.set)
        self.character_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.character_tree.bind("<Double-1>", self.on_character_selected)
        self.update_character_list()

    def update_character_list(self):
        star_str = self.star_var.get()
        star = None if star_str == "全部" else int(star_str)
        type_str = self.type_var.get()
        char_type = None if type_str == "全部" else type_str
        search_text = self.search_var.get().strip().lower()

        for item in self.character_tree.get_children():
            self.character_tree.delete(item)

        self.char_map = {}

        for c in self.char_lib.characters:
            if star is not None and c.get_fixed_attribute("星级") != star:
                continue
            if char_type is not None and c.get_fixed_attribute("类型") != char_type:
                continue
            if search_text and search_text not in c.name.lower():
                continue
            item_id = f"{c.name}_{c.get_fixed_attribute('星级')}"
            self.char_map[item_id] = c
            self.character_tree.insert("", tk.END, iid=item_id,
                                       values=(c.name, c.get_fixed_attribute("星级"), c.get_fixed_attribute("类型")))

    def on_character_selected(self, event):
        selection = self.character_tree.selection()
        if not selection:
            return
        item_id = selection[0]
        self.selected_character = self.char_map.get(item_id)
        if self.selected_character is None:
            return
        self.update_skill_select_frame()
        self.show_frame(self.skill_frame)

    # ---------- 第二步：技能选择界面 ----------
    def create_skill_select_frame(self):
        self.skill_frame = ttk.Frame(self.main_container)

        info_frame = ttk.Frame(self.skill_frame)
        info_frame.pack(fill=tk.X, padx=10, pady=10)
        self.selected_char_label = ttk.Label(info_frame, text="未选择角色", font=("仿宋", 12))
        self.selected_char_label.pack(side=tk.LEFT, padx=10)

        skill_choice_frame = ttk.LabelFrame(self.skill_frame, text="选择技能", padding=10)
        skill_choice_frame.pack(fill=tk.X, padx=10, pady=10)

        self.skill_var = tk.StringVar()
        self.skill_var.set("战技")
        ttk.Radiobutton(skill_choice_frame, text="战技", variable=self.skill_var, value="战技").pack(anchor=tk.W)
        ttk.Radiobutton(skill_choice_frame, text="连携技", variable=self.skill_var, value="连携技").pack(anchor=tk.W)
        ttk.Radiobutton(skill_choice_frame, text="终结技", variable=self.skill_var, value="终结技").pack(anchor=tk.W)

        level_frame = ttk.Frame(self.skill_frame)
        level_frame.pack(fill=tk.X, padx=10, pady=10)

        ttk.Label(level_frame, text="技能等级 (1-12):").pack(side=tk.LEFT, padx=5)
        self.skill_level_var = tk.IntVar(value=1)
        self.skill_level_spin = ttk.Spinbox(level_frame, from_=1, to=12, textvariable=self.skill_level_var, width=5)
        self.skill_level_spin.pack(side=tk.LEFT, padx=5)

        self.multiplier_label = ttk.Label(self.skill_frame, text="", foreground="blue")
        self.multiplier_label.pack(padx=10, pady=5)

        # 角色等级选择
        char_level_frame = ttk.Frame(self.skill_frame)
        char_level_frame.pack(fill=tk.X, padx=10, pady=5)
        ttk.Label(char_level_frame, text="角色等级：").pack(side=tk.LEFT, padx=5)
        self.char_level_var = tk.IntVar()
        self.char_level_combo = ttk.Combobox(char_level_frame, textvariable=self.char_level_var,
                                              state="readonly", width=8)
        self.char_level_combo.pack(side=tk.LEFT, padx=5)

        btn_frame = ttk.Frame(self.skill_frame)
        btn_frame.pack(fill=tk.X, padx=10, pady=10)

        back_btn = ttk.Button(btn_frame, text="返回", command=lambda: self.show_frame(self.character_frame))
        back_btn.pack(side=tk.LEFT, padx=5)

        next_btn = ttk.Button(btn_frame, text="下一步", command=self.on_skill_next)
        next_btn.pack(side=tk.RIGHT, padx=5)

        self.skill_level_var.trace_add("write", self.update_multiplier_display)
        self.skill_var.trace_add("write", self.update_multiplier_display)

    def update_skill_select_frame(self):
        if self.selected_character:
            self.selected_char_label.config(text=f"当前角色：{self.selected_character.name}")
                    # 更新角色等级下拉框
        levels = self.selected_character.get_levels()
        if levels:
            level_strs = [str(lv) for lv in levels]
            self.char_level_combo['values'] = level_strs
            # 默认选中最高等级
            max_lv = max(levels)
            self.char_level_var.set(max_lv)
            self.selected_character_level = max_lv
        else:
            self.char_level_combo['values'] = []
            self.char_level_var.set('')
            self.selected_character_level = None
            self.update_multiplier_display()

    def update_multiplier_display(self, *args):
        if not self.selected_character:
            return
        skill_name = self.skill_var.get()
        skill_level = self.skill_level_var.get()
        segments = self.selected_character.skill_multipliers.get(skill_name, {}).get(skill_level)
        if segments:
            text = "倍率: "
            if len(segments) == 1:
                text += f"{segments[0]*100:.1f}%"
            else:
                text += " + ".join(f"{seg*100:.1f}%" for seg in segments)
            self.multiplier_label.config(text=text)
        else:
            self.multiplier_label.config(text="无倍率数据")

    def on_skill_next(self):
        self.selected_skill = self.skill_var.get()
        self.selected_skill_level = self.skill_level_var.get()
        self.selected_character_level = self.char_level_var.get()
        # 更新武器界面
        self.weapon_frame.update_for_character(
            self.selected_character,
            self.selected_skill,
            self.selected_skill_level
        )
        self.show_frame(self.weapon_frame)

    # ---------- 第三步：武器选择和计算界面 ----------
    def create_weapon_select_frame(self):
        """创建武器界面，使用独立的 WeaponSelectionFrame 类"""
        self.weapon_frame = WeaponSelectionFrame(
            self.main_container,
            self.weapon_lib,
            self.calc_single_damage,   # 单次计算回调
            self.calc_rank              # 排名计算回调
        )
        # 设置返回按钮的回调
        self.weapon_frame.set_back_callback(lambda: self.show_frame(self.skill_frame))

        self.weapon_frame.set_export_csv_callback(self.save_rank_csv)
        
        # 创建结果显示文本框，并放置在武器界面下方
        result_frame = ttk.LabelFrame(self.weapon_frame, text="计算结果", padding=10)
        result_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        self.result_text = tk.Text(result_frame, height=10, wrap=tk.WORD)
        scroll_result = ttk.Scrollbar(result_frame, orient=tk.VERTICAL, command=self.result_text.yview)
        self.result_text.configure(yscrollcommand=scroll_result.set)
        self.result_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scroll_result.pack(side=tk.RIGHT, fill=tk.Y)

        # 将结果文本框的引用保存到武器界面（可选，但回调中直接使用 self.result_text）
        self.weapon_frame.set_result_text_widget(self.result_text)

    # ---------- 计算回调方法 ----------
    def calc_single_damage(self):
        """单次伤害计算回调，由武器界面的按钮触发"""
        # 从武器界面获取数据
        weapon = self.weapon_frame.get_selected_weapon()
        if not self.selected_character or not weapon:
            self.result_text.insert(tk.END, "请先选择角色和武器！\n")
            return

        weapon_level = self.weapon_frame.get_weapon_level()
        use_temp, temp_times = self.weapon_frame.get_temp_effect_state()
        atk_percent, dmg_percent, crit_rate, crit_dmg = self.weapon_frame.get_other_multipliers()

        # 调用计算模块
        result_str = calculate_single_damage(
            character=self.selected_character,
            weapon=weapon,
            skill=self.selected_skill,
            skill_level=self.selected_skill_level,
            character_level=self.selected_character_level,  # 新增
            weapon_level=weapon_level,
            atk_percent=atk_percent,
            dmg_percent=dmg_percent,
            crit_rate=crit_rate,
            crit_dmg=crit_dmg,
            use_temp_effect=use_temp,
            temp_effect_times=temp_times
        )
        self.result_text.insert(tk.END, result_str + "\n")

    def calc_rank(self):
        if not self.selected_character:
            self.result_text.insert(tk.END, "请先选择角色！\n")
            return

        weapon_level = self.weapon_frame.get_weapon_level()
        # 关键点：这里不要限制“必须选中某个武器”
        use_temp, temp_times = self.weapon_frame.get_temp_effect_state()
        atk_percent, dmg_percent, crit_rate, crit_dmg = self.weapon_frame.get_other_multipliers()

        # 根据是否启用临时效果确定遍历方式
        times_param = temp_times if use_temp else None

        # 这里直接遍历所有武器
        result_str = calculate_rank(
            character=self.selected_character,
            weapon_lib=self.weapon_lib,
            skill=self.selected_skill,
            skill_level=self.selected_skill_level,
            character_level=self.selected_character_level,
            weapon_level=weapon_level,
            atk_percent=atk_percent,
            dmg_percent=dmg_percent,
            crit_rate=crit_rate,
            crit_dmg=crit_dmg,
            use_temp_effect=use_temp,
            temp_effect_times=temp_times
        )
        if not result_str:
            result_str = "没有得到任何遍历结果。"
        self.result_text.insert(tk.END, result_str + "\n")

    def save_rank_csv(self):
        if not self.selected_character:
            self.result_text.insert(tk.END, "请先选择角色！\n")
            return

        weapon_level = self.weapon_frame.get_weapon_level()
        use_temp, temp_times = self.weapon_frame.get_temp_effect_state()
        atk_percent, dmg_percent, crit_rate, crit_dmg = self.weapon_frame.get_other_multipliers()
        times_param = temp_times if use_temp else None

        # 获取结构化数据
        from 遍历 import traverse_weapons_csv_data
        header, rows = traverse_weapons_csv_data(
            character=self.selected_character,
            weapon_lib=self.weapon_lib,
            skill=self.selected_skill,
            skill_level=self.selected_skill_level,
            character_level=self.selected_character_level,
            atk_percent=atk_percent,
            dmg_percent=dmg_percent,
            crit_rate=crit_rate,
            crit_dmg=crit_dmg,
            weapon_level=weapon_level,
            temp_times=times_param
        )

        file_path = fd.asksaveasfilename(defaultextension=".csv",
                                        filetypes=[("CSV 文件", "*.csv"), ("所有文件", "*.*")],
                                        title="导出排名为CSV")
        if not file_path:
            return

        try:
            with open(file_path, "w", encoding="utf-8", newline='') as f:
                writer = csv.writer(f)
                writer.writerow(header)
                writer.writerows(rows)
            mb.showinfo("成功", "保存成功，请用Excel打开（一般来说直接双击该文件即可）")
        except Exception as e:
            mb.showerror("失败", f"保存失败: {e}")

if __name__ == "__main__":
    app = DamageCalculatorApp()


