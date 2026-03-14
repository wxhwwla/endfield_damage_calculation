"""
武器选择界面Frame，封装武器列表、等级选择、效果显示等控件。
"""

import tkinter as tk
from tkinter import ttk
from typing import Dict, Optional, Callable, Tuple

class WeaponSelectionFrame(ttk.Frame):
    """武器选择界面，包含武器列表、等级选择、效果显示、临时效果选项和其他乘区输入"""

    def __init__(self, parent, weapon_lib, on_calc_single: Callable, on_calc_rank: Callable):
        super().__init__(parent)
        self.weapon_lib = weapon_lib
        self.on_calc_single = on_calc_single
        self.on_calc_rank = on_calc_rank

        self.selected_weapon = None
        self.weapon_map = {}

        # 配置网格权重，使三列可扩展
        self.grid_columnconfigure(0, weight=2)  # 左列
        self.grid_columnconfigure(1, weight=1)  # 中列
        self.grid_columnconfigure(2, weight=2)  # 右列
        self.grid_rowconfigure(0, weight=1)

        self._create_widgets()

    def _create_widgets(self):
        # ========== 左列：武器选择（简化布局，使用单列网格） ==========
        left_frame = ttk.Frame(self)
        left_frame.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
        left_frame.grid_rowconfigure(2, weight=1)  # 武器列表所在行可扩展
        left_frame.grid_columnconfigure(0, weight=1)

        # 武器类型显示（放入一个子框架，保持左对齐）
        type_frame = ttk.Frame(left_frame)
        type_frame.grid(row=0, column=0, sticky="ew", padx=5, pady=2)
        ttk.Label(type_frame, text="可用武器类型：").pack(side=tk.LEFT)
        self.weapon_type_label = ttk.Label(type_frame, text="")
        self.weapon_type_label.pack(side=tk.LEFT, padx=5)

        # 武器列表（带滚动条）
        list_frame = ttk.Frame(left_frame)
        list_frame.grid(row=2, column=0, sticky="nsew", padx=5, pady=5)
        list_frame.grid_rowconfigure(0, weight=1)
        list_frame.grid_columnconfigure(0, weight=1)

        columns = ("name", "star", "type", "levels")
        self.weapon_tree = ttk.Treeview(list_frame, columns=columns, show="headings", height=15)
        self.weapon_tree.heading("name", text="武器名称")
        self.weapon_tree.heading("star", text="星级")
        self.weapon_tree.heading("type", text="类型")
        self.weapon_tree.heading("levels", text="可用等级")
        self.weapon_tree.column("name", width=200)
        self.weapon_tree.column("star", width=60)
        self.weapon_tree.column("type", width=100)
        self.weapon_tree.column("levels", width=100)

        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.weapon_tree.yview)
        self.weapon_tree.configure(yscrollcommand=scrollbar.set)
        self.weapon_tree.grid(row=0, column=0, sticky="nsew")
        scrollbar.grid(row=0, column=1, sticky="ns")

        # 武器等级选择
        level_frame = ttk.Frame(left_frame)
        level_frame.grid(row=3, column=0, sticky="ew", padx=5, pady=5)
        ttk.Label(level_frame, text="武器等级：").pack(side=tk.LEFT, padx=5)
        self.weapon_level_var = tk.IntVar()
        self.weapon_level_combo = ttk.Combobox(level_frame, textvariable=self.weapon_level_var,
                                                state="readonly", width=8)
        self.weapon_level_combo.pack(side=tk.LEFT, padx=5)

        # ========== 中间列：武器效果和其他乘区（保持不变） ==========
        mid_frame = ttk.Frame(self)
        mid_frame.grid(row=0, column=1, sticky="nsew", padx=5, pady=5)
        mid_frame.grid_columnconfigure(0, weight=1)

        # 武器效果
        effect_frame = ttk.LabelFrame(mid_frame, text="武器效果", padding=10)
        effect_frame.grid(row=0, column=0, sticky="ew", padx=5, pady=5)
        self.persistent_effect_label = ttk.Label(effect_frame, text="持续效果：无")
        self.persistent_effect_label.pack(anchor=tk.W, padx=5, pady=2)

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
        self.temp_effect_detail = ttk.Label(effect_frame, text="")
        self.temp_effect_detail.pack(anchor=tk.W, padx=5, pady=2)

        # 其他乘区
        other_frame = ttk.LabelFrame(mid_frame, text="其他乘区", padding=10)
        other_frame.grid(row=1, column=0, sticky="ew", padx=5, pady=5)

        ttk.Label(other_frame, text="攻击力加成%：").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        self.atk_percent_var = tk.DoubleVar(value=0.0)
        ttk.Entry(other_frame, textvariable=self.atk_percent_var, width=10).grid(row=0, column=1, padx=5, pady=5)
        ttk.Label(other_frame, text="伤害加成%：").grid(row=0, column=2, padx=5, pady=5, sticky=tk.W)
        self.dmg_percent_var = tk.DoubleVar(value=0.0)
        ttk.Entry(other_frame, textvariable=self.dmg_percent_var, width=10).grid(row=0, column=3, padx=5, pady=5)
        ttk.Label(other_frame, text="暴击率%：").grid(row=1, column=0, padx=5, pady=5, sticky=tk.W)
        self.crit_rate_var = tk.DoubleVar(value=0.0)
        ttk.Entry(other_frame, textvariable=self.crit_rate_var, width=10).grid(row=1, column=1, padx=5, pady=5)
        ttk.Label(other_frame, text="暴击伤害%：").grid(row=1, column=2, padx=5, pady=5, sticky=tk.W)
        self.crit_dmg_var = tk.DoubleVar(value=0.0)
        ttk.Entry(other_frame, textvariable=self.crit_dmg_var, width=10).grid(row=1, column=3, padx=5, pady=5)

        # 操作按钮
        btn_frame = ttk.Frame(mid_frame)
        btn_frame.grid(row=2, column=0, sticky="ew", padx=5, pady=5)
        ttk.Button(btn_frame, text="返回技能", command=self._go_back).pack(side=tk.LEFT, padx=2)
        ttk.Button(btn_frame, text="计算当前武器", command=self.on_calc_single).pack(side=tk.LEFT, padx=2)
        ttk.Button(btn_frame, text="遍历排名", command=self.on_calc_rank).pack(side=tk.LEFT, padx=2)
        ttk.Button(btn_frame, text="导出CSV", command=self._on_export_rank_csv).pack(side=tk.LEFT, padx=2)

        # ========== 右列：计算结果 ==========
        right_frame = ttk.Frame(self)
        right_frame.grid(row=0, column=2, sticky="nsew", padx=5, pady=5)
        right_frame.grid_rowconfigure(0, weight=1)
        right_frame.grid_columnconfigure(0, weight=1)

        result_frame = ttk.LabelFrame(right_frame, text="计算结果", padding=10)
        result_frame.grid(row=0, column=0, sticky="nsew")
        result_frame.grid_rowconfigure(0, weight=1)
        result_frame.grid_columnconfigure(0, weight=1)

        self.result_text = tk.Text(result_frame, height=20, wrap=tk.WORD)
        scroll_result = ttk.Scrollbar(result_frame, orient=tk.VERTICAL, command=self.result_text.yview)
        self.result_text.configure(yscrollcommand=scroll_result.set)
        self.result_text.grid(row=0, column=0, sticky="nsew")
        scroll_result.grid(row=0, column=1, sticky="ns")

        # 绑定武器选择事件
        self.weapon_tree.bind("<<TreeviewSelect>>", self._on_weapon_selected)

    # 其余方法保持不变（_on_temp_effect_toggle, _go_back, set_back_callback, update_for_character,
    # _on_weapon_selected, get_selected_weapon, get_weapon_level, get_temp_effect_state,
    # get_other_multipliers, set_export_csv_callback, _on_export_rank_csv）
    # 请将原文件中这些方法原封不动地复制过来。
    # 为了简洁，这里省略了这些方法，但您需要保留它们。
    # ---------- 内部方法 ----------
    def _on_temp_effect_toggle(self):
        if self.use_temp_effect_var.get():
            self.temp_times_spin.config(state="normal")
        else:
            self.temp_times_spin.config(state="disabled")

    def _go_back(self):
        if hasattr(self, 'back_callback') and self.back_callback:
            self.back_callback()

    def set_back_callback(self, callback):
        self.back_callback = callback

    # ---------- 公开方法：供外部更新界面 ----------
    def update_for_character(self, character, skill, skill_level):
        if not character:
            return
        weapon_type = character.get_fixed_attribute("武器")
        self.weapon_type_label.config(text=weapon_type if weapon_type else "未知")

        # 清空武器列表
        for item in self.weapon_tree.get_children():
            self.weapon_tree.delete(item)
        self.weapon_map = {}
        self.selected_weapon = None

        # 收集所有可用武器等级（用于下拉框）
        all_levels_set = set()
        for w in self.weapon_lib.weapons:
            if w.get_fixed_attribute("类型") == weapon_type:
                for lv in w.get_levels():
                    all_levels_set.add(lv)
        all_levels = sorted(all_levels_set)
        if all_levels:
            level_strs = [str(lv) for lv in all_levels]
            self.weapon_level_combo['values'] = level_strs
            self.weapon_level_var.set(all_levels[0])
        else:
            self.weapon_level_combo['values'] = []
            self.weapon_level_var.set('')

        # 加载符合条件的武器
        for w in self.weapon_lib.weapons:
            if w.get_fixed_attribute("类型") == weapon_type:
                item_id = f"{w.name}_{w.get_fixed_attribute('星级')}"
                self.weapon_map[item_id] = w
                levels_str = ", ".join(str(lv) for lv in w.get_levels())
                self.weapon_tree.insert("", tk.END, iid=item_id,
                                        values=(w.name, w.get_fixed_attribute("星级"),
                                                w.get_fixed_attribute("类型"), levels_str))

    # ---------- 内部事件处理 ----------
    def _on_weapon_selected(self, event):
        selection = self.weapon_tree.selection()
        if not selection:
            return
        item_id = selection[0]
        self.selected_weapon = self.weapon_map.get(item_id)
        if not self.selected_weapon:
            return

        # 更新等级下拉框为该武器的可用等级
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
        temp_strength = fixed.get("临时附加强度", 0)
        temp_times = fixed.get("临时效果次数", 0)
        if temp and temp_strength != 0:
            self.temp_effect_detail.config(text=f"临时效果：{temp} +{temp_strength} (武器自带次数 {temp_times})")
            self.temp_effect_times_var.set(temp_times)
            self.use_temp_effect_var.set(False)
            self._on_temp_effect_toggle()
        else:
            self.temp_effect_detail.config(text="临时效果：无")
            self.use_temp_effect_var.set(False)
            self.temp_effect_times_var.set(0)
            self._on_temp_effect_toggle()

    # ---------- 公开数据获取方法 ----------
    def get_selected_weapon(self):
        return self.selected_weapon

    def get_weapon_level(self) -> Optional[int]:
        try:
            return int(self.weapon_level_var.get())
        except (ValueError, tk.TclError):
            return None

    def get_temp_effect_state(self) -> Tuple[bool, int]:
        use_temp = self.use_temp_effect_var.get()
        temp_times = self.temp_effect_times_var.get() if use_temp else 0
        return use_temp, temp_times

    def get_other_multipliers(self) -> Tuple[float, float, float, float]:
        def safe_get(var):
            try:
                return var.get()
            except:
                return 0.0
        return (safe_get(self.atk_percent_var),
                safe_get(self.dmg_percent_var),
                safe_get(self.crit_rate_var),
                safe_get(self.crit_dmg_var))

    def set_export_csv_callback(self, callback):
        self.export_csv_callback = callback

    def _on_export_rank_csv(self):
        if hasattr(self, 'export_csv_callback') and self.export_csv_callback:
            self.export_csv_callback()


