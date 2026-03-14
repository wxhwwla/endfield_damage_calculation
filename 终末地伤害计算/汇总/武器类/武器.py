#这个文件主要是负责添加武器

import json
import os
from typing import List, Dict, Any, Optional
# AI说这东西这些类型提示不会影响程序运行，但可以提高代码可读性，并让 IDE 和静态类型检查工具（如 mypy）更好地理解代码意图。

WEAPON =["等级","星级","类型","基础攻击力",
         "主能力+","副能力+",
         "力量+","敏捷+","智识+","意志+",
         "攻击力+","附加攻击力+",
         "物理伤害+","法术伤害+",
         "冰系伤害+","火系伤害+","雷系伤害+","草系伤害+",
         "战技伤害+","连携技伤害+","终结技伤害+","源石技艺强度+",
         "持续效果：","效果强度","临时效果：","临时效果强度","临时效果次数"]
# 定义一个常量WEAPON，它是一个字符串列表，包含了游戏中所有可能的武器属性名称。
# 这个列表并不是必须的，但可以作为一个参考，便于管理和查看系统中有哪些属性，也可以用于后续的校验（例如检查传入的属性名是否合法）。

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
# 获取当前脚本所在目录的绝对路径

class Weapon:
# 定义一个武器类，每个实例代表一个武器（固定属性 + 多等级数据）

    def __init__(self,name:str,fixed_attributes:Dict[str,any]):
    # 定义武器的名字为字符串
    # 定义该武器的属性，属性放在列表的字典里，键为属性名，值为字符串等
    # 仅需要写入这个武器所需的属性

        self.name = name
        self.fixed_attributes = fixed_attributes
        # 固定属性字典（如星级、类型等不随等级变化的属性）
        # 将传入的名字或者属性字典保存为变量
        self.levels: Dict[int, Dict[str, Any]] = {}
        # self.levels 是一个字典，用于存储该武器的所有等级数据
        # 键（int）：武器等级（如 1, 20, 40...）
        # 值（Dict[str, Any]）：该等级下的具体属性字典，包含如“基础攻击力”、“主能力+”等随等级变化的属性
        # 这样设计使得一个武器对象可以持有多个等级的数据，避免了为每个等级创建独立武器实例的冗余

    def add_level(self, level: int, attributes: Dict[str, Any]):
        self.levels[level] = attributes
        # 该方法将传入的等级 level 和对应的属性字典 attributes 存入 self.levels 字典
        # 如果该等级已存在，旧数据会被覆盖（可根据需要添加检查或合并逻辑）

    def get_levels(self) -> List[int]:
        return sorted(self.levels.keys())
        # 返回武器所有可用等级的列表，并按升序排序，方便遍历或显示

    def get_fixed_attribute(self, attr_name: str, default=None):
        return self.fixed_attributes.get(attr_name, default)
        # 从 fixed_attributes 字典中安全获取指定属性值，若不存在则返回 default
        # 固定属性包括星级、类型等不随等级变化的属性

    def get_level_attribute(self, level: int, attr_name: str, default=None):
        level_data = self.levels.get(level)
        if level_data:
            return level_data.get(attr_name, default)
        return default
        # 首先根据 level 获取该等级的数据字典 level_data
        # 如果等级存在，则从该字典中获取 attr_name 对应的值；否则返回 default
        # 实现了按等级访问动态属性
                
    def get_attribute(self,attr_name:str, level: int = None, default=None):
    # 定义方法get_attribute，用于获取武器的某个属性值
    # 第一个参数为需要获取的属性名称
    # 第二个参数为如果没有该属性，则返回None    
    # 兼容旧接口：若提供 level 则从等级数据中获取，否则从固定属性中获取
    # 若属性均不存在，返回 default   
        if level is not None:
            return self.get_level_attribute(level, attr_name, default)
        else:
            return self.get_fixed_attribute(attr_name, default)
        # 兼容旧接口：若提供 level 则从等级数据中获取，否则从固定属性中获取
        # 若属性均不存在，返回 default 
        # 该方法统一了固定属性和等级属性的访问方式
        # 如果调用时传入了 level，则视为获取该等级的动态属性；否则视为获取固定属性
        # 这样在已有代码（如筛选武器）中，调用 w.get_attribute("星级") 仍能正确获取固定属性，无需修改

    def to_dict(self) -> Dict:
        return {
            "name": self.name,
            "fixed": self.fixed_attributes,
            "levels": {str(level): attrs for level, attrs in self.levels.items()}
        }
        # 将 Weapon 对象转换为普通字典，以便用 json 模块保存到文件
        # 由于 JSON 要求键必须为字符串，将等级字典的键从整数 level 转换为字符串 str(level)

    @classmethod
    def from_dict(cls, data: Dict) -> "Weapon":
    # 类方法，根据从 JSON 加载的字典重建 Weapon 对象
    # 先调用构造函数创建实例（传入名称和固定属性），然后遍历 levels 中的每个键值对
    # 将字符串键转回整数，并调用 add_level 添加等级数据
        w = cls(data["name"], data["fixed"])
        for level_str, attrs in data["levels"].items():
            w.add_level(int(level_str), attrs)
        return w
    
    def __repr__(self):
    #定义一个查询的函数，可以查询放进去的武器
        return f"Weapon(name={self.name!r}, fixed={self.fixed_attributes}, levels={list(self.levels.keys())})"
        #这个方法的返回值是一个字符串，里面包含了武器的名称和属性字典。!r 表示使用 repr() 来格式化 self.name，确保字符串带有引号，更清晰
    

class WeaponLibrary:
#武器库类，用于管理武器

    def __init__(self):
    # 初始化方法，创建一个空列表 self.weapons，用于存储所有武器对象。
    # 类型注解 List[Weapon] 表明这个列表中的元素都是 Weapon 实例。

        self.weapons:list[Weapon] = []

    def add_weapon(self,weapon:Weapon):
    # 定义一个方法add_weapon，要求传入的参数为一个Waepon的对象
    # 我看了一下后面的示例，这个Weapon对象是指("武器名字"，{"属性1"：数值.然后接下来的都是属性})

        self.weapons.append(weapon)
        # 将该武器添加到上面那个初始化方法的列表中

    def find_weapon_by_name(self, name: str) -> Optional[Weapon]:
    # 根据名称查找武器原型（假设名称唯一）
    # name: str为外部输入，期望查找的武器名称
        for w in self.weapons:
            if w.name == name:
                return w
        return None

    def filter_weapons(self, star: Optional[int] = None, weapon_type: Optional[str] = None) -> List[Weapon]:
    # 定义一个筛选函数，筛选目标为星级和武器类型，返回值为一个武器的列表
        result = []
        for w in self.weapons:
            if star is not None and w.get_attribute("星级") != star:
                continue
            # 筛选出输入的星级（如果提供了 star 参数）
            # 如果没有就跳过

            if weapon_type is not None and w.get_attribute("类型") != weapon_type:
                continue
            # 筛选武器类型（如果提供了 weapon_type 参数）
            # 如果没有就跳过
            # w.get_attribute("星级") 实际调用的是 get_fixed_attribute
            # 因为未提供 level 参数（好吧，我说实话不太看得

            result.append(w)
            # 两个条件都为 None 时返回所有武器
            # 返回符合条件的武器列表

        return result
    
    def to_dict_list(self) -> List[Dict]:
    # 将整个武器库转换为可 JSON 序列化的列表
    # 将武器库中的所有武器依次调用 to_dict()，生成一个字典列表，便于整体保存
        return [w.to_dict() for w in self.weapons]

    @classmethod
    def from_dict_list(cls, data: List[Dict]) -> "WeaponLibrary":
    # 从列表恢复武器库
    # 从字典列表重建 WeaponLibrary 对象 
    # 遍历列表，每个元素通过 Weapon.from_dict 转换为武器对象，然后添加到新创建的库中
        lib = cls()
        for item in data:
            lib.add_weapon(Weapon.from_dict(item))
        return lib


def save_library(lib: WeaponLibrary, filename: str = None):
# 把整个武器库 lib 批量保存成 JSON 文件，持久化存盘

    if filename is None:
        filename = os.path.join(SCRIPT_DIR, "weapons.json")
    # 如果调用时没有指定文件名，就用默认的文件路径
    # SCRIPT_DIR 通常是当前脚本的目录，也就是保存到你工程的指定文件夹下
    # 如果 filename 为 None，则默认保存到脚本所在目录下的 weapons.json

    with open(filename, "w", encoding="utf-8") as f:
        json.dump(lib.to_dict_list(), f, indent=2, ensure_ascii=False)
    # 以写模式打开目标 json 文件，采用 utf-8 编码保证中文不会乱码
    # lib.to_dict_list() 获得当前库的所有武器的字典列表
    # （通常就是 [weapon.to_dict() for weapon in lib.weapons]）
    # json.dump 负责将这个数据结构保存为可读性好的带缩进（indent=2）的 JSON 文件
    # ensure_ascii=False 确保中文不会被转成 Unicode 转义序列，方便可读


def load_library(filename: str = None) -> WeaponLibrary:
# 从一个 JSON 文件中加载（反序列化）所有武器的数据
# 恢复成一个 WeaponLibrary 对象。这通常用于程序启动或数据还原

    if filename is None:
        filename = os.path.join(SCRIPT_DIR, "weapons.json")
    # 如果调用时没有给文件名，就用默认存储位置（通常和 save_library 保持一致）

    try:
        with open(filename, "r", encoding="utf-8") as f:
            data = json.load(f)
        # 按 utf-8 编码打开文件
        # json.load 反序列化为 Python 列表（每个元素是一个武器的字典表示）

        return WeaponLibrary.from_dict_list(data)
        # 调用 WeaponLibrary 的批量工厂方法（上文解释过）
        # 把字典列表还原成真正的 WeaponLibrary 对象，包含所有武器实例

    except FileNotFoundError:
        return WeaponLibrary()
        # 如果目标 json 文件不存在，说明要么是第一次运行，要么没保存过库
        # 此时不给出异常，而是直接返回一个空的武器库，保证主程序可正常运行（即降级为“空库启动”）


if __name__ == "__main__":
    lib = WeaponLibrary()
    # 变成实例

    塔尔11 = Weapon("塔尔11", {"星级":3, "类型":"单手剑",})
    塔尔11.add_level(1,  {"等级":1, "基础攻击力":29, "主能力+":10, "附加攻击力+":12})
    塔尔11.add_level(20,  {"等级":20, "基础攻击力":83, "主能力+":10, "附加攻击力+":12})
    塔尔11.add_level(40,  {"等级":40, "基础攻击力":140, "主能力+":18, "附加攻击力+":12})
    塔尔11.add_level(60,  {"等级":60, "基础攻击力":197, "主能力+":26, "附加攻击力+":12})
    塔尔11.add_level(80,  {"等级":80, "基础攻击力":254, "主能力+":34, "附加攻击力+":12})
    塔尔11.add_level(90,  {"等级":90, "基础攻击力":283, "主能力+":42, "附加攻击力+":12})
    # 添加等级数据

    lib.add_weapon(塔尔11)
    # 把武器放入角色库中，为批量管理、多存取做准备

    浪潮 = Weapon("浪潮", {"星级":4, "类型":"单手剑",})
    浪潮.add_level(1,  {"等级":1, "基础攻击力":34, "智识+":12, "攻击力+":3,
                        "临时效果":"攻击力+", "临时附加强度":12, "临时效果次数":1})
    浪潮.add_level(20,  {"等级":20, "基础攻击力":100, "智识+":12, "攻击力+":3,
                        "临时效果":"攻击力+", "临时附加强度":12, "临时效果次数":1})
    浪潮.add_level(40,  {"等级":40, "基础攻击力":169, "智识+":21, "攻击力+":3,
                        "临时效果":"攻击力+", "临时附加强度":12, "临时效果次数":1})
    浪潮.add_level(60,  {"等级":60, "基础攻击力":238, "智识+":21, "攻击力+":5.4,
                        "临时效果":"攻击力+", "临时附加强度":12, "临时效果次数":1})
    浪潮.add_level(80,  {"等级":80, "基础攻击力":307, "智识+":31, "攻击力+":5.4,
                        "临时效果":"攻击力+", "临时附加强度":12, "临时效果次数":1})
    浪潮.add_level(90,  {"等级":90, "基础攻击力":341, "智识+":31, "攻击力+":7.8,
                        "临时效果":"攻击力+", "临时附加强度":12, "临时效果次数":1})
    lib.add_weapon(浪潮)

    save_library(lib)
    print(f"武器库已保存到 {os.path.join(SCRIPT_DIR, 'weapons.json')}")
    # 用先前的save_library把整个库对象序列化成JSON，存入硬盘
    # 路径用默认目录和characters.json文件名

    loaded_lib = load_library()
    # 通过load_library()将武器库文件读回内存，确保保存/加载流程可用

    print("从文件加载的武器库：")
    for w in loaded_lib.weapons:
        print(w)
        for lv in w.get_levels():
            atk = w.get_level_attribute(lv, "基础攻击力", "?")
            print(f"  等级 {lv}: 基础攻击力 {atk}")
    # 打印武器对象（通常会看到名称等基本信息）。
    # 遍历各等级的数据，输出每一等级的攻击力。


