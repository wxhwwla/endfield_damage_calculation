"""
武器选择界面模块，封装武器列表、等级选择、效果显示、临时效果选项以及其他乘区输入。
"""

import tkinter as tk
from tkinter import ttk
from typing import Dict, Optional, Callable, Tuple

class WeaponSelectionFrame(ttk.Frame):
    """武器选择界面，包含武器列表、等级选择、效果显示、临时效果选项和其他乘区输入"""

    def __init__(self, parent, weapon_lib, on_calc_single: Callable, on_calc_rank: Callable):
        """
        :param parent: 父容器
        :param weapon_lib: 武器库对象
        :param on_calc_single: 单次计算回调函数（无参，由外部实现）
        :param on_calc_rank: 排名计算回调函数（无参）
        """
        super().__init__(parent)
        self.weapon_lib = weapon_lib
        self.on_calc_single = on_calc_single
        self.on_calc_rank = on_calc_rank

        # 当前选中的武器对象（由内部更新）
        self.selected_weapon = None
        self.weapon_map = {}  # 用于存储Treeview iid到武器对象的映射

        # 结果文本框（由外部设置，可选）
        self.result_text = None

        # 创建界面控件
        self._create_widgets()

    def _create_widgets(self):
        # 显示当前角色和技能信息（由外部更新文本）
        info_frame = ttk.Frame(self)
        info_frame.pack(fill=tk.X, padx=10, pady=10)
        self.char_skill_label = ttk.Label(info_frame, text="", font=("仿宋", 12))
        self.char_skill_label.pack(side=tk.LEFT, padx=10)

        # 武器筛选框架（仅显示角色可用武器类型）
        filter_frame = ttk.LabelFrame(self, text="武器筛选", padding=10)
        filter_frame.pack(fill=tk.X, padx=10, pady=10)

        ttk.Label(filter_frame, text="可用武器类型：").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        self.weapon_type_label = ttk.Label(filter_frame, text="")
        self.weapon_type_label.grid(row=0, column=1, padx=5, pady=5, sticky=tk.W)

        # 武器列表（Treeview）
        list_frame = ttk.Frame(self)
        list_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        columns = ("name", "star", "type", "levels")
        self.weapon_tree = ttk.Treeview(list_frame, columns=columns, show="headings", height=10)
        self.weapon_tree.heading("name", text="武器名称")
        self.weapon_tree.heading("star", text="星级")
        self.weapon_tree.heading("type", text="类型")
        self.weapon_tree.heading("levels", text="可用等级")
        self.weapon_tree.column("name", width=200)
        self.weapon_tree.column("star", width=80)
        self.weapon_tree.column("type", width=150)
        self.weapon_tree.column("levels", width=150)

        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.weapon_tree.yview)
        self.weapon_tree.configure(yscrollcommand=scrollbar.set)
        self.weapon_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # 武器等级选择
        level_frame = ttk.Frame(self)
        level_frame.pack(fill=tk.X, padx=10, pady=5)
        ttk.Label(level_frame, text="武器等级：").pack(side=tk.LEFT, padx=5)
        self.weapon_level_var = tk.IntVar()
        self.weapon_level_combo = ttk.Combobox(level_frame, textvariable=self.weapon_level_var,
                                                state="readonly", width=8)
        self.weapon_level_combo.pack(side=tk.LEFT, padx=5)
        self.weapon_level_combo['values'] = []

        # 武器效果显示及临时效果选项
        effect_frame = ttk.LabelFrame(self, text="武器效果", padding=10)
        effect_frame.pack(fill=tk.X, padx=10, pady=10)

        # 持续效果标签
        self.persistent_effect_label = ttk.Label(effect_frame, text="持续效果：无")
        self.persistent_effect_label.pack(anchor=tk.W, padx=5, pady=2)

        # 临时效果复选框和次数输入
        temp_frame = ttk.Frame(effect_frame)
        temp_frame.pack(anchor=tk.W, padx=5, pady=2)
        self.use_temp_effect_var = tk.BooleanVar(value=False)
        self.use_temp_check = ttk.Checkbutton(temp_frame, text="启用临时效果",
                                               variable=self.use_temp_effect_var,
                                               command=self._on_temp_effect_toggle)
        self.use_temp_check.pack(side=tk.LEFT)

        ttk.Label(temp_frame, text="次数：").pack(side=tk.LEFT, padx=(10, 2))
        self.temp_effect_times_var = tk.IntVar(value=0)
        self.temp_times_spin = ttk.Spinbox(temp_frame, from_=0, to=99,
                                           textvariable=self.temp_effect_times_var,
                                           width=5, state="disabled")
        self.temp_times_spin.pack(side=tk.LEFT)

        # 临时效果详细信息（显示类型和强度）
        self.temp_effect_detail = ttk.Label(effect_frame, text="")
        self.temp_effect_detail.pack(anchor=tk.W, padx=5, pady=2)

        # 其他乘区输入
        other_frame = ttk.LabelFrame(self, text="其他乘区", padding=10)
        other_frame.pack(fill=tk.X, padx=10, pady=10)

        # 攻击力加成
        ttk.Label(other_frame, text="攻击力加成%：").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        self.atk_percent_var = tk.DoubleVar(value=0.0)
        ttk.Entry(other_frame, textvariable=self.atk_percent_var, width=10).grid(row=0, column=1, padx=5, pady=5)

        # 伤害加成
        ttk.Label(other_frame, text="伤害加成%：").grid(row=0, column=2, padx=5, pady=5, sticky=tk.W)
        self.dmg_percent_var = tk.DoubleVar(value=0.0)
        ttk.Entry(other_frame, textvariable=self.dmg_percent_var, width=10).grid(row=0, column=3, padx=5, pady=5)

        # 暴击率
        ttk.Label(other_frame, text="暴击率%：").grid(row=1, column=0, padx=5, pady=5, sticky=tk.W)
        self.crit_rate_var = tk.DoubleVar(value=0.0)
        ttk.Entry(other_frame, textvariable=self.crit_rate_var, width=10).grid(row=1, column=1, padx=5, pady=5)

        # 暴击伤害
        ttk.Label(other_frame, text="暴击伤害%：").grid(row=1, column=2, padx=5, pady=5, sticky=tk.W)
        self.crit_dmg_var = tk.DoubleVar(value=0.0)
        ttk.Entry(other_frame, textvariable=self.crit_dmg_var, width=10).grid(row=1, column=3, padx=5, pady=5)

        # 操作按钮
        btn_frame = ttk.Frame(self)
        btn_frame.pack(fill=tk.X, padx=10, pady=10)

        back_btn = ttk.Button(btn_frame, text="返回技能", command=self._go_back)
        back_btn.pack(side=tk.LEFT, padx=5)

        calc_single_btn = ttk.Button(btn_frame, text="计算当前武器伤害", command=self.on_calc_single)
        calc_single_btn.pack(side=tk.LEFT, padx=5)

        rank_btn = ttk.Button(btn_frame, text="遍历所有武器排名", command=self.on_calc_rank)
        rank_btn.pack(side=tk.LEFT, padx=5)

    # ---------- 内部方法 ----------
    def _on_temp_effect_toggle(self):
        """根据复选框状态启用或禁用次数输入框"""
        if self.use_temp_effect_var.get():
            self.temp_times_spin.config(state="normal")
        else:
            self.temp_times_spin.config(state="disabled")

    def _go_back(self):
        """返回技能选择界面（需要外部设置回调）"""
        if hasattr(self, 'back_callback') and self.back_callback:
            self.back_callback()

    def set_back_callback(self, callback):
        """设置返回按钮的回调函数"""
        self.back_callback = callback

    def set_result_text_widget(self, text_widget):
        """设置结果文本框的引用（可选）"""
        self.result_text = text_widget

    # ---------- 公开方法：供外部更新界面 ----------
    def update_for_character(self, character, skill, skill_level):
        """
        根据选中的角色更新武器列表和显示信息
        :param character: 角色对象
        :param skill: 技能名称
        :param skill_level: 技能等级
        """
        if not character:
            return
        weapon_type = character.get_fixed_attribute("武器")
        self.weapon_type_label.config(text=weapon_type if weapon_type else "未知")

        self.char_skill_label.config(
            text=f"角色：{character.name} | 技能：{skill} Lv.{skill_level}"
        )

        # 清空武器列表和状态
        for item in self.weapon_tree.get_children():
            self.weapon_tree.delete(item)
        self.weapon_map = {}
        self.selected_weapon = None
        self.weapon_level_combo['values'] = []
        self.weapon_level_var.set('')
        self.persistent_effect_label.config(text="持续效果：无")
        self.temp_effect_detail.config(text="")
        self.use_temp_effect_var.set(False)
        self.temp_effect_times_var.set(0)
        self._on_temp_effect_toggle()

        # 加载符合条件的武器
        for w in self.weapon_lib.weapons:
            if w.get_fixed_attribute("类型") == weapon_type:
                item_id = f"{w.name}_{w.get_fixed_attribute('星级')}"
                self.weapon_map[item_id] = w
                levels_str = ", ".join(str(lv) for lv in w.get_levels())
                self.weapon_tree.insert("", tk.END, iid=item_id,
                                        values=(w.name, w.get_fixed_attribute("星级"), w.get_fixed_attribute("类型"), levels_str))

        self.weapon_tree.bind("<<TreeviewSelect>>", self._on_weapon_selected)

    # ---------- 内部事件处理 ----------
    def _on_weapon_selected(self, event):
        """当武器列表选中一行时更新效果显示和等级下拉框"""
        selection = self.weapon_tree.selection()
        if not selection:
            return
        item_id = selection[0]
        self.selected_weapon = self.weapon_map.get(item_id)
        if not self.selected_weapon:
            return

        # 更新等级下拉框
        levels = self.selected_weapon.get_levels()
        if levels:
            level_strs = [str(lv) for lv in levels]
            self.weapon_level_combo['values'] = level_strs
            self.weapon_level_var.set(levels[0])
        else:
            self.weapon_level_combo['values'] = []
            self.weapon_level_var.set('')

        # 更新效果信息
        fixed = self.selected_weapon.fixed_attributes

        # 持续效果
        persistent = fixed.get("持续效果")
        persistent_strength = fixed.get("效果强度", 0)
        if persistent and persistent_strength != 0:
            self.persistent_effect_label.config(text=f"持续效果：{persistent} +{persistent_strength}")
        else:
            self.persistent_effect_label.config(text="持续效果：无")

        # 临时效果
        temp = fixed.get("临时效果")
        temp_strength = fixed.get("临时效果强度", 0)
        temp_times = fixed.get("临时效果次数", 0)
        if temp and temp_strength != 0:
            self.temp_effect_detail.config(text=f"临时效果：{temp} +{temp_strength} (武器自带次数 {temp_times})")
            self.temp_effect_times_var.set(temp_times)
            # 默认不启用
            self.use_temp_effect_var.set(False)
            self._on_temp_effect_toggle()
        else:
            self.temp_effect_detail.config(text="临时效果：无")
            self.use_temp_effect_var.set(False)
            self.temp_effect_times_var.set(0)
            self._on_temp_effect_toggle()

    # ---------- 公开数据获取方法 ----------
    def get_selected_weapon(self):
        """返回当前选中的武器对象，若无则返回None"""
        return self.selected_weapon

    def get_weapon_level(self):
        """返回当前选中的武器等级，若未选择则返回0"""
        try:
            return self.weapon_level_var.get()
        except:
            return 0

    def get_temp_effect_state(self) -> Tuple[bool, int]:
        """返回临时效果启用状态和次数 (use_temp, temp_times)"""
        use_temp = self.use_temp_effect_var.get()
        temp_times = self.temp_effect_times_var.get() if use_temp else 0
        return use_temp, temp_times

    def get_other_multipliers(self) -> Tuple[float, float, float, float]:
        """返回其他乘区的值 (atk_percent, dmg_percent, crit_rate, crit_dmg) 均为百分比数值"""
        return (self.atk_percent_var.get(),
                self.dmg_percent_var.get(),
                self.crit_rate_var.get(),
                self.crit_dmg_var.get())
    

    