class Zombie:
    """僵尸基类，所有僵尸都继承自此类"""

    def __init__(self, name, health, damage, speed, reward=10):
        self.name = name  # 僵尸名称
        self.health = health  # 生命值
        self.max_health = health  # 最大生命值
        self.damage = damage  # 攻击力
        self.speed = speed  # 移动速度（每回合移动的格数）
        self.reward = reward  # 消灭后获得的阳光奖励
        self.position = None  # 位置坐标 (行, 列)
        self.move_counter = 0  # 移动计数器，用于控制移动速度
        self.target_plant = None  # 当前攻击的植物

    def set_position(self, row, col):
        """设置僵尸位置"""
        self.position = (row, col)

    def is_alive(self):
        """判断僵尸是否存活"""
        return self.health > 0

    def take_damage(self, damage):
        """受到伤害"""
        self.health -= damage
        if self.health < 0:
            self.health = 0

    def can_move(self):
        """判断是否可以移动（基于速度）"""
        self.move_counter += 1
        return self.move_counter >= (1 / self.speed)

    def move(self, plants):
        """移动僵尸，或攻击植物"""
        if not self.position:
            return False

        row, col = self.position

        # 检查当前位置是否有植物
        self.target_plant = None
        for plant in plants:
            p_row, p_col = plant.position if plant.position else (None, None)
            if p_row == row and p_col == col:
                self.target_plant = plant
                break

        # 如果有目标植物，则攻击
        if self.target_plant and self.target_plant.is_alive():
            self.target_plant.take_damage(self.damage)
            return False

        # 否则移动
        if self.can_move():
            self.move_counter = 0
            new_col = col - 1
            # 检查是否到达终点（左端）
            if new_col < 0:
                return "reach_end"  # 到达终点，游戏失败
            self.position = (row, new_col)
            return True
        return False

    def update(self, plants):
        """更新僵尸状态"""
        return self.move(plants)

    def __str__(self):
        health_percent = (self.health / self.max_health) * 100
        return f"{self.name} (HP: {self.health}/{self.max_health} {health_percent:.0f}%)"


# 具体僵尸类型
class BasicZombie(Zombie):
    """普通僵尸"""

    def __init__(self):
        super().__init__(
            name="普通僵尸",
            health=100,
            damage=10,
            speed=0.2  # 每2回合移动一次
        )


class ConeheadZombie(Zombie):
    """路障僵尸：有额外防御"""

    def __init__(self):
        super().__init__(
            name="路障僵尸",
            health=200,
            damage=10,
            speed=0.2,
            reward=15
        )


class BucketheadZombie(Zombie):
    """铁桶僵尸：更高防御"""

    def __init__(self):
        super().__init__(
            name="铁桶僵尸",
            health=300,
            damage=10,
            speed=0.2,  # 每3回合移动一次
            reward=20
        )


class FastZombie(Zombie):
    """快速僵尸：移动速度快"""

    def __init__(self):
        super().__init__(
            name="快速僵尸",
            health=70,
            damage=10,
            speed=0.5,  # 每回合移动一次
            reward=15
        )


# 僵尸工厂，用于创建僵尸
class ZombieFactory:
    @staticmethod
    def create_zombie(zombie_type):
        if zombie_type == "basic":
            return BasicZombie()
        elif zombie_type == "conehead":
            return ConeheadZombie()
        elif zombie_type == "buckethead":
            return BucketheadZombie()
        elif zombie_type == "fast":
            return FastZombie()
        else:
            raise ValueError(f"未知僵尸类型: {zombie_type}")
