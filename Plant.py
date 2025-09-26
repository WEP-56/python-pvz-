class Plant:
    """植物基类，所有植物都继承自此类"""

    def __init__(self, name, health, cost, attack_power=0, attack_range=1, attack_cooldown=1):
        self.name = name  # 植物名称
        self.health = health  # 生命值
        self.cost = cost  # 阳光消耗
        self.attack_power = attack_power  # 攻击力
        self.attack_range = attack_range  # 攻击范围
        self.attack_cooldown = attack_cooldown  # 攻击冷却时间（回合）
        self.cooldown_timer = 0  # 当前冷却计时器
        self.position = None  # 位置坐标 (行, 列)

    def set_position(self, row, col):
        """设置植物位置"""
        self.position = (row, col)

    def is_alive(self):
        """判断植物是否存活"""
        return self.health > 0

    def take_damage(self, damage):
        """受到伤害"""
        self.health -= damage
        if self.health < 0:
            self.health = 0

    def can_attack(self):
        """判断是否可以攻击"""
        return self.attack_power > 0 and self.cooldown_timer == 0

    def attack(self, zombies):
        """攻击范围内的僵尸"""
        if not self.can_attack():
            return []

        # 重置冷却计时器
        self.cooldown_timer = self.attack_cooldown

        # 找出攻击范围内的僵尸
        attacked_zombies = []
        if self.position:
            row, col = self.position
            for zombie in zombies:
                z_row, z_col = zombie.position
                # 检查是否在攻击范围内（简化版：同一行且在植物前方）
                if z_row == row and z_col >= col and (z_col - col) <= self.attack_range:
                    zombie.take_damage(self.attack_power)
                    attacked_zombies.append(zombie)

        return attacked_zombies

    def update(self):
        """每回合更新植物状态"""
        if self.cooldown_timer > 0:
            self.cooldown_timer -= 1

    def __str__(self):
        return f"{self.name} (HP: {self.health})"


# 具体植物类型
class Sunflower(Plant):
    """向日葵：产生阳光"""

    def __init__(self):
        super().__init__(name="向日葵", health=30, cost=50)
        self.sun_production = 25  # 每回合产生的阳光
        self.production_cooldown = 2  # 产生阳光的冷却时间
        self.sun_timer = 0

    def update(self):
        """更新向日葵状态，可能产生阳光"""
        super().update()
        self.sun_timer += 1
        if self.sun_timer >= self.production_cooldown:
            self.sun_timer = 0
            return self.sun_production
        return 0


class Peashooter(Plant):
    """豌豆射手：基础攻击植物"""

    def __init__(self):
        super().__init__(
            name="豌豆射手",
            health=30,
            cost=100,
            attack_power=10,
            attack_range=3,
            attack_cooldown=1
        )


class WallNut(Plant):
    """坚果墙：高生命值，用于阻挡僵尸"""

    def __init__(self):
        super().__init__(
            name="坚果墙",
            health=300,
            cost=50,
            attack_power=0  # 没有攻击力
        )


class CherryBomb(Plant):
    """樱桃炸弹：范围攻击，一次性使用"""

    def __init__(self):
        super().__init__(
            name="樱桃炸弹",
            health=30,
            cost=150,
            attack_power=100,
            attack_range=2  # 大范围攻击
        )
        self.used = False

    def attack(self, zombies):
        if self.used or not self.position:
            return []

        self.used = True
        self.health = 0  # 攻击后消失

        # 攻击范围内的所有僵尸
        attacked_zombies = []
        row, col = self.position
        for zombie in zombies:
            z_row, z_col = zombie.position
            # 检查是否在2x2范围内
            if abs(z_row - row) <= 1 and abs(z_col - col) <= 1:
                zombie.take_damage(self.attack_power)
                attacked_zombies.append(zombie)

        return attacked_zombies


# 植物工厂，用于创建植物
class PlantFactory:
    @staticmethod
    def create_plant(plant_type):
        if plant_type == "sunflower":
            return Sunflower()
        elif plant_type == "peashooter":
            return Peashooter()
        elif plant_type == "wallnut":
            return WallNut()
        elif plant_type == "cherrybomb":
            return CherryBomb()
        else:
            raise ValueError(f"未知植物类型: {plant_type}")
