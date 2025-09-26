import sys
import random
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                               QHBoxLayout, QGridLayout, QLabel, QPushButton,
                               QMessageBox, QTextEdit)
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QFont, QTextCursor

from Plant import PlantFactory
import Plant  # 显式导入plant模块用于类型检查
from zombie import ZombieFactory
import zombie  # 显式导入zombie模块用于类型检查
from level import Level


class GameBoard(QGridLayout):
    """游戏棋盘布局"""

    def __init__(self, rows, cols, parent=None):
        super().__init__(parent)
        self.rows = rows
        self.cols = cols
        self.cells = []

        # 创建棋盘单元格
        for row in range(rows):
            row_cells = []
            for col in range(cols):
                cell = QLabel(" ")
                cell.setAlignment(Qt.AlignCenter)
                cell.setStyleSheet("border: 1px solid #cccccc; background-color: #f0f0f0;")
                cell.setMinimumSize(60, 60)
                cell.setMaximumSize(60, 60)
                cell.setFont(QFont("SimHei", 12))
                cell.setObjectName(f"cell_{row}_{col}")
                self.addWidget(cell, row, col)
                row_cells.append(cell)
            self.cells.append(row_cells)


class PlantSelection(QVBoxLayout):
    """植物选择面板"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.plant_buttons = {}

        # 创建植物选择按钮
        plants = [
            ("向日葵", "sunflower", 50),
            ("豌豆射手", "peashooter", 100),
            ("坚果墙", "wallnut", 50),
            ("樱桃炸弹", "cherrybomb", 150)
        ]

        for name, plant_type, cost in plants:
            btn = QPushButton(f"{name} (¥{cost})")
            btn.setObjectName(plant_type)
            btn.setMinimumHeight(40)
            btn.setFont(QFont("SimHei", 10))
            self.addWidget(btn)
            self.plant_buttons[plant_type] = btn

        self.addStretch()


class GameInfo(QVBoxLayout):
    """游戏信息面板"""

    def __init__(self, parent=None):
        super().__init__(parent)

        self.sun_label = QLabel("阳光: 50")
        self.level_label = QLabel("关卡: 1")
        self.wave_label = QLabel("波次: 1/2")
        self.status_label = QLabel("状态: 游戏进行中")

        for label in [self.sun_label, self.level_label, self.wave_label, self.status_label]:
            label.setFont(QFont("SimHei", 12))
            label.setStyleSheet("margin: 5px 0;")
            self.addWidget(label)

        self.addStretch()

        # 日志区域
        self.log_label = QLabel("游戏日志:")
        self.log_label.setFont(QFont("SimHei", 12, QFont.Bold))
        self.addWidget(self.log_label)

        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setMaximumHeight(200)
        self.addWidget(self.log_text)

    def update_sun(self, sun):
        self.sun_label.setText(f"阳光: {sun}")

    def update_level(self, level):
        self.level_label.setText(f"关卡: {level}")

    def update_wave(self, wave_info):
        if wave_info:
            self.wave_label.setText(f"波次: {wave_info['wave_number']}/{wave_info['total_waves']}")

    def update_status(self, status):
        self.status_label.setText(f"状态: {status}")

    def add_log(self, message):
        self.log_text.append(message)
        # 修复：使用正确的QTextCursor.End常量
        self.log_text.moveCursor(QTextCursor.End)


class PlantsVsZombies(QMainWindow):
    """植物大战僵尸主游戏类"""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("植物大战僵尸 - 文字版")
        self.setMinimumSize(900, 600)

        # 游戏状态
        self.current_level = 1
        self.max_levels = 3
        self.sun = 50
        self.selected_plant = None
        self.game_running = False
        self.game_over = False

        # 初始化游戏组件
        self.init_game()

        # 设置UI
        self.init_ui()

        # 游戏计时器（每1000毫秒一个回合）
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.game_loop)

    def init_game(self):
        """初始化游戏状态"""
        self.level = Level(self.current_level)
        self.plants = []
        self.zombies = []
        self.sun = 50
        self.game_running = False
        self.game_over = False

    def init_ui(self):
        """初始化用户界面"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)

        # 左侧：植物选择面板
        plant_panel = QWidget()
        self.plant_selection = PlantSelection()
        plant_panel.setLayout(self.plant_selection)
        plant_panel.setMinimumWidth(150)
        main_layout.addWidget(plant_panel)

        # 中间：游戏棋盘
        board_widget = QWidget()
        self.board = GameBoard(self.level.rows, self.level.cols)
        board_widget.setLayout(self.board)
        main_layout.addWidget(board_widget)

        # 右侧：游戏信息面板
        info_panel = QWidget()
        self.game_info = GameInfo()
        info_panel.setLayout(self.game_info)
        info_panel.setMinimumWidth(200)
        main_layout.addWidget(info_panel)

        # 底部：控制按钮
        control_layout = QHBoxLayout()
        self.start_button = QPushButton("开始游戏")
        self.start_button.clicked.connect(self.start_game)
        self.next_level_button = QPushButton("下一关")
        self.next_level_button.clicked.connect(self.next_level)
        self.next_level_button.setEnabled(False)
        self.quit_button = QPushButton("退出游戏")
        self.quit_button.clicked.connect(self.close)

        for btn in [self.start_button, self.next_level_button, self.quit_button]:
            btn.setMinimumHeight(30)
            control_layout.addWidget(btn)

        # 将控制布局添加到主布局
        main_layout.addLayout(control_layout)

        # 连接植物选择按钮
        for plant_type, btn in self.plant_selection.plant_buttons.items():
            btn.clicked.connect(lambda checked, pt=plant_type: self.select_plant(pt))

        # 连接棋盘单元格点击事件
        for row in range(self.level.rows):
            for col in range(self.level.cols):
                cell = self.board.cells[row][col]
                # 修复：保留原始的鼠标事件处理
                original_event = cell.mousePressEvent
                cell.mousePressEvent = lambda event, r=row, c=col, orig=original_event: \
                    [orig(event), self.place_plant(r, c)][-1]

        # 更新UI显示
        self.update_ui()

    def select_plant(self, plant_type):
        """选择要种植的植物"""
        if not self.game_running or self.game_over:
            return

        # 获取植物成本
        plant_instance = PlantFactory.create_plant(plant_type)

        # 检查阳光是否足够
        if self.sun >= plant_instance.cost:
            self.selected_plant = plant_type
            self.game_info.add_log(f"已选择: {plant_instance.name}")
            # 高亮显示选中的植物按钮
            for pt, btn in self.plant_selection.plant_buttons.items():
                if pt == plant_type:
                    btn.setStyleSheet("background-color: #aaffaa;")
                else:
                    btn.setStyleSheet("")
        else:
            self.game_info.add_log(f"阳光不足，无法选择 {plant_instance.name}")
            self.selected_plant = None

    def place_plant(self, row, col):
        """在指定位置种植植物"""
        if not self.game_running or self.game_over or not self.selected_plant:
            return

        # 检查位置是否已种植植物
        for plant_instance in self.plants:
            if plant_instance.position == (row, col):
                self.game_info.add_log("该位置已种植植物")
                return

        # 创建植物并检查成本
        plant_instance = PlantFactory.create_plant(self.selected_plant)

        if self.sun >= plant_instance.cost:
            # 扣除阳光并种植植物
            self.sun -= plant_instance.cost
            plant_instance.set_position(row, col)
            self.plants.append(plant_instance)
            self.game_info.add_log(f"已种植 {plant_instance.name} 在位置 ({row + 1}, {col + 1})")

            # 立即更新UI，确保植物显示
            self.update_board()
            self.game_info.update_sun(self.sun)

            # 取消选择
            self.selected_plant = None
            for btn in self.plant_selection.plant_buttons.values():
                btn.setStyleSheet("")
        else:
            self.game_info.add_log(f"阳光不足，无法种植 {plant_instance.name}")

    def start_game(self):
        """开始或继续游戏"""
        if self.game_over:
            # 重新开始当前关卡
            self.init_game()
            self.update_ui()

        self.game_running = True
        self.start_button.setText("暂停游戏")
        self.start_button.clicked.connect(self.pause_game)
        self.next_level_button.setEnabled(False)
        self.game_info.add_log("游戏开始!")
        self.timer.start(1000)  # 1000毫秒 = 1秒

    def pause_game(self):
        """暂停游戏"""
        self.game_running = False
        self.start_button.setText("继续游戏")
        self.start_button.clicked.connect(self.start_game)
        self.game_info.add_log("游戏已暂停")
        self.timer.stop()

    def next_level(self):
        """进入下一关"""
        if self.current_level < self.max_levels:
            self.current_level += 1
            self.init_game()
            self.update_ui()
            self.game_info.add_log(f"进入第 {self.current_level} 关!")
            self.start_game()
        else:
            QMessageBox.information(self, "游戏完成", "恭喜你完成了所有关卡!")
            self.close()

    def game_loop(self):
        """游戏主循环"""
        if not self.game_running or self.game_over:
            return

        # 1. 生成新僵尸
        zombie_type = self.level.get_next_zombie()
        if zombie_type:
            # 随机选择一行生成僵尸
            row = random.randint(0, self.level.rows - 1)
            zombie_instance = ZombieFactory.create_zombie(zombie_type)
            zombie_instance.set_position(row, self.level.cols - 1)  # 从最右侧出现
            self.zombies.append(zombie_instance)
            self.game_info.add_log(f"{zombie_instance.name} 出现了!")

        # 2. 向日葵产生阳光
        for plant_instance in self.plants:
            if isinstance(plant_instance, Plant.Sunflower):
                sun_produced = plant_instance.update()
                if sun_produced > 0:
                    self.sun += sun_produced
                    self.game_info.update_sun(self.sun)
                    self.game_info.add_log(f"向日葵产生了 {sun_produced} 点阳光")
            else:
                plant_instance.update()

        # 3. 植物攻击
        for plant_instance in self.plants[:]:  # 使用切片避免迭代中修改列表
            if plant_instance.is_alive():
                attacked_zombies = plant_instance.attack(self.zombies)
                for zombie_instance in attacked_zombies:
                    if zombie_instance.is_alive():
                        self.game_info.add_log(
                            f"{plant_instance.name} 攻击了 {zombie_instance.name}，造成 {plant_instance.attack_power} 点伤害")
                    else:
                        self.game_info.add_log(f"{zombie_instance.name} 被消灭了!")
                        self.sun += zombie_instance.reward
                        self.game_info.update_sun(self.sun)
                        self.level.zombie_eliminated()
            else:
                # 移除已死亡的植物
                self.game_info.add_log(f"{plant_instance.name} 被摧毁了!")
                self.plants.remove(plant_instance)

        # 4. 僵尸移动和攻击
        for zombie_instance in self.zombies[:]:  # 使用切片避免迭代中修改列表
            if zombie_instance.is_alive():
                result = zombie_instance.update(self.plants)
                if result == "reach_end":
                    # 僵尸到达终点，游戏结束
                    self.game_over = True
                    self.game_running = False
                    self.timer.stop()
                    self.start_button.setText("重新开始")
                    self.start_button.clicked.connect(self.start_game)
                    self.game_info.add_log("僵尸到达终点，游戏失败!")
                    self.game_info.update_status("游戏失败")
                    QMessageBox.information(self, "游戏结束", "僵尸到达终点，游戏失败!")
                    return
            else:
                # 移除已死亡的僵尸
                self.zombies.remove(zombie_instance)

        # 5. 检查关卡是否完成
        if self.level.is_complete():
            self.game_running = False
            self.timer.stop()
            self.game_info.add_log(f"第 {self.current_level} 关完成!")
            self.game_info.update_status("关卡完成")
            self.start_button.setText("重新开始本关")
            self.start_button.clicked.connect(self.start_game)
            self.next_level_button.setEnabled(True)
            QMessageBox.information(self, "关卡完成", f"恭喜你完成了第 {self.current_level} 关!")

        # 6. 更新UI
        self.update_board()
        self.game_info.update_wave(self.level.get_current_wave_info())

    def update_board(self):
        """更新游戏棋盘显示"""
        # 清空棋盘
        for row in range(self.level.rows):
            for col in range(self.level.cols):
                self.board.cells[row][col].setText(" ")
                self.board.cells[row][col].setStyleSheet("border: 1px solid #cccccc; background-color: #f0f0f0;")

        # 绘制植物
        for plant_instance in self.plants:
            if plant_instance.is_alive() and plant_instance.position:
                row, col = plant_instance.position
                # 用不同的字符表示不同的植物
                if isinstance(plant_instance, Plant.Sunflower):
                    self.board.cells[row][col].setText("向")
                    self.board.cells[row][col].setStyleSheet("border: 1px solid #cccccc; background-color: #ffffaa;")
                elif isinstance(plant_instance, Plant.Peashooter):
                    self.board.cells[row][col].setText("豌")
                    self.board.cells[row][col].setStyleSheet("border: 1px solid #cccccc; background-color: #aaffaa;")
                elif isinstance(plant_instance, Plant.WallNut):
                    self.board.cells[row][col].setText("坚")
                    self.board.cells[row][col].setStyleSheet("border: 1px solid #cccccc; background-color: #aaaaaa;")
                elif isinstance(plant_instance, Plant.CherryBomb):
                    self.board.cells[row][col].setText("樱")
                    self.board.cells[row][col].setStyleSheet("border: 1px solid #cccccc; background-color: #ffaaaa;")

        # 绘制僵尸
        for zombie_instance in self.zombies:
            if zombie_instance.is_alive() and zombie_instance.position:
                row, col = zombie_instance.position
                # 用不同的字符表示不同的僵尸
                if isinstance(zombie_instance, zombie.BasicZombie):
                    self.board.cells[row][col].setText("僵")
                elif isinstance(zombie_instance, zombie.ConeheadZombie):
                    self.board.cells[row][col].setText("路")
                elif isinstance(zombie_instance, zombie.BucketheadZombie):
                    self.board.cells[row][col].setText("铁")
                elif isinstance(zombie_instance, zombie.FastZombie):
                    self.board.cells[row][col].setText("快")

                # 根据生命值设置颜色
                health_percent = (zombie_instance.health / zombie_instance.max_health) * 100
                if health_percent > 70:
                    self.board.cells[row][col].setStyleSheet("border: 1px solid #cccccc; background-color: #ffaaaa;")
                elif health_percent > 30:
                    self.board.cells[row][col].setStyleSheet("border: 1px solid #cccccc; background-color: #ffddaa;")
                else:
                    self.board.cells[row][col].setStyleSheet("border: 1px solid #cccccc; background-color: #ffffaa;")

    def update_ui(self):
        """更新整个UI"""
        self.game_info.update_sun(self.sun)
        self.game_info.update_level(self.current_level)
        self.game_info.update_wave(self.level.get_current_wave_info())
        self.game_info.update_status("准备就绪")
        self.update_board()
        self.game_info.log_text.clear()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    # 设置中文字体支持
    font = QFont("SimHei")
    app.setFont(font)
    game = PlantsVsZombies()
    game.show()
    sys.exit(app.exec())
