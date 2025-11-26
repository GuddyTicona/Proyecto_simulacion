# ui/tab_automata_celular.py
"""
Autómata Celular 

Tres modos completos:
1. CONWAY 
2. UNIDIMENSIONALES - Reglas elementales 
3. COVID-19 - Modelo epidemiológico
"""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QSpinBox, QPushButton,
    QTableWidget, QTableWidgetItem, QSlider, QCheckBox, QGroupBox, QLineEdit,
    QFileDialog, QMessageBox, QComboBox, QFormLayout, QDoubleSpinBox,
    QTabWidget
)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QColor, QBrush

import random
import csv
import hashlib
from collections import deque

# matplotlib for plotting
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure


class TabAutomataCelular(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # =========================================================================
        # CONFIGURACIÓN INICIAL - TRES MODOS
        # =========================================================================
        
        # CONWAY (Bidimensional)
        self._n = 20
        self._cell_alive_color = QColor(0, 0, 0)  # negro para vivo (estilo clásico)
        self._cell_dead_color = QColor(255, 255, 255)  # blanco para muerto
        self._running = False
        self._toroidal = False
        self._timer_interval = 200
        self._timer = QTimer(self)
        self._timer.timeout.connect(self._on_timer_tick)

        # Estado Conway
        self._state = []  # 0/1 para Conway
        self._history_hashes = []
        self._history_len = 80
        self.birth_set = {3}
        self.survive_set = {2, 3}

        # UNIDIMENSIONALES
        self._unidimensional_rules = {
            "Regla 30": 30, "Regla 90": 90, "Regla 110": 110, 
            "Regla 184": 184, "Regla 54": 54, "Regla 73": 73
        }
        self._current_1d_rule = 30
        self._1d_width = 100
        self._1d_generations = 100
        self._1d_state = []  # Estado actual 1D
        self._1d_history = []  # Historial de generaciones
        self._1d_running = False

        # COVID-19 (Epidemiológico)
        self._state_covid = []
        self._infection_age = []
        self._covid_running = False
        self._covid_stats = {"S": [], "I": [], "R": [], "V": []}
        self._max_stats_len = 1000

        # Parámetros COVID por defecto
        self.covid_init_infected_pct = 0.02
        self.covid_init_vaccinated_pct = 0.0
        self.covid_p_infect = 0.3
        self.covid_p_move = 0.2
        self.covid_recovery_time = 10

        # =========================================================================
        # INTERFAZ DE USUARIO
        # =========================================================================
        self._init_ui()
        self._create_grid(self._n)
        self._init_1d_grid()
        self._init_covid_grid()

    def _init_ui(self):
        main = QVBoxLayout(self)

        # =========================================================================
        # PESTAÑAS PARA LOS TRES MODOS
        # =========================================================================
        self.tabs = QTabWidget()
        
        # Pestaña 1: CONWAY
        self.conway_tab = QWidget()
        self._setup_conway_tab()
        self.tabs.addTab(self.conway_tab, "Conway")
        
        # Pestaña 2: UNIDIMENSIONALES
        self.unidimensional_tab = QWidget()
        self._setup_unidimensional_tab()
        self.tabs.addTab(self.unidimensional_tab, "Unidimensionales")
        
        # Pestaña 3: COVID-19
        self.covid_tab = QWidget()
        self._setup_covid_tab()
        self.tabs.addTab(self.covid_tab, "COVID-19")
        
        main.addWidget(self.tabs)

        # Conectar eventos de cambio de pestaña
        self.tabs.currentChanged.connect(self._on_tab_changed)

    # =============================================================================
    # CONWAY - AUTÓMATA BIDIMENSIONAL
    # =============================================================================
    def _setup_conway_tab(self):
        layout = QVBoxLayout(self.conway_tab)

        # top row: size, toroidal, rule, presets (Conway)
        top_row = QHBoxLayout()

        size_box = QGroupBox("Tamaño (N x N)")
        size_layout = QHBoxLayout(size_box)
        self.spin_n = QSpinBox()
        self.spin_n.setRange(5, 200)
        self.spin_n.setValue(self._n)
        self.btn_apply_size = QPushButton("Aplicar")
        size_layout.addWidget(self.spin_n)
        size_layout.addWidget(self.btn_apply_size)
        top_row.addWidget(size_box)

        self.chk_toroidal = QCheckBox("Toroidal")
        top_row.addWidget(self.chk_toroidal)

        rule_box = QGroupBox("Regla (B/S)")
        rule_layout = QHBoxLayout(rule_box)
        self.le_rule = QLineEdit("B3/S23")
        self.btn_apply_rule = QPushButton("Aplicar regla")
        rule_layout.addWidget(self.le_rule)
        rule_layout.addWidget(self.btn_apply_rule)
        top_row.addWidget(rule_box)

        presets_box = QGroupBox("Presets (Conway)")
        presets_layout = QHBoxLayout(presets_box)
        self.combo_presets = QComboBox()
        self.combo_presets.addItems(["Seleccionar...", "Glider", "Blinker", "Toad", "Beacon", "Gosper Glider Gun (small)"])
        self.btn_load_preset = QPushButton("Cargar preset")
        presets_layout.addWidget(self.combo_presets)
        presets_layout.addWidget(self.btn_load_preset)
        top_row.addWidget(presets_box)

        layout.addLayout(top_row)

        # control row: common controls (play/pause/step for current mode)
        ctrl_row = QHBoxLayout()
        self.btn_start = QPushButton("Iniciar")
        self.btn_pause = QPushButton("Pausar")
        self.btn_step = QPushButton("Siguiente")
        self.btn_random = QPushButton("Generar aleatorio")
        self.btn_clear = QPushButton("Limpiar")
        ctrl_row.addWidget(self.btn_start)
        ctrl_row.addWidget(self.btn_pause)
        ctrl_row.addWidget(self.btn_step)
        ctrl_row.addWidget(self.btn_random)
        ctrl_row.addWidget(self.btn_clear)

        # speed
        speed_box = QGroupBox("Velocidad (ms)")
        speed_layout = QHBoxLayout(speed_box)
        self.slider_speed = QSlider(Qt.Orientation.Horizontal)
        self.slider_speed.setRange(20, 1000)
        self.slider_speed.setValue(self._timer_interval)
        speed_layout.addWidget(self.slider_speed)
        ctrl_row.addWidget(speed_box)

        # Conway autostop options
        self.chk_autostop_extinct = QCheckBox("Autostop si se extingue")
        self.chk_autostop_stagnant = QCheckBox("Autostop si sin cambios")
        self.chk_autostop_cycle = QCheckBox("Detectar ciclos")
        self.chk_autostop_extinct.setChecked(True)
        self.chk_autostop_stagnant.setChecked(True)
        ctrl_row.addWidget(self.chk_autostop_extinct)
        ctrl_row.addWidget(self.chk_autostop_stagnant)
        ctrl_row.addWidget(self.chk_autostop_cycle)

        layout.addLayout(ctrl_row)

        # grid widget
        self.table = QTableWidget()
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table.horizontalHeader().setVisible(False)
        self.table.verticalHeader().setVisible(False)
        self.table.setShowGrid(True)
        layout.addWidget(self.table)

        # bottom row: load/save
        bottom_row = QHBoxLayout()
        self.btn_save = QPushButton("Guardar CSV")
        self.btn_load = QPushButton("Cargar CSV")
        bottom_row.addWidget(self.btn_save)
        bottom_row.addWidget(self.btn_load)
        layout.addLayout(bottom_row)

        # connections Conway
        self.btn_apply_size.clicked.connect(self._on_apply_size)
        self.chk_toroidal.stateChanged.connect(self._on_toroidal_change)
        self.slider_speed.valueChanged.connect(self._on_speed_change)
        self.btn_start.clicked.connect(self.start)
        self.btn_pause.clicked.connect(self.pause)
        self.btn_step.clicked.connect(self.step_once)
        self.btn_random.clicked.connect(self._on_random)
        self.btn_clear.clicked.connect(self.clear)
        self.table.cellClicked.connect(self._on_cell_clicked)
        self.btn_load_preset.clicked.connect(self._on_load_preset)
        self.btn_apply_rule.clicked.connect(self._on_apply_rule)
        self.btn_save.clicked.connect(self._on_save_csv)
        self.btn_load.clicked.connect(self._on_load_csv)

    # =============================================================================
    # UNIDIMENSIONALES - AUTÓMATAS 1D
    # =============================================================================
    def _setup_unidimensional_tab(self):
        layout = QVBoxLayout(self.unidimensional_tab)

        # Controles superiores 1D
        top_controls = QHBoxLayout()

        # Configuración 1D
        config_group = QGroupBox("Configuración 1D")
        config_layout = QFormLayout(config_group)
        
        self.combo_1d_rules = QComboBox()
        self.combo_1d_rules.addItems(self._unidimensional_rules.keys())
        config_layout.addRow("Regla:", self.combo_1d_rules)
        
        self.spin_1d_width = QSpinBox()
        self.spin_1d_width.setRange(50, 500)
        self.spin_1d_width.setValue(self._1d_width)
        config_layout.addRow("Ancho:", self.spin_1d_width)
        
        self.spin_1d_generations = QSpinBox()
        self.spin_1d_generations.setRange(50, 500)
        self.spin_1d_generations.setValue(self._1d_generations)
        config_layout.addRow("Generaciones:", self.spin_1d_generations)
        
        top_controls.addWidget(config_group)

        # Controles 1D
        ctrl_group = QGroupBox("Controles 1D")
        ctrl_layout = QVBoxLayout(ctrl_group)
        
        self.btn_1d_random = QPushButton("Estado aleatorio")
        self.btn_1d_single = QPushButton("Una célula central")
        self.btn_1d_start = QPushButton("Iniciar evolución")
        self.btn_1d_pause = QPushButton("Pausar")
        self.btn_1d_step = QPushButton("Siguiente generación")
        self.btn_1d_clear = QPushButton("Limpiar")
        
        ctrl_layout.addWidget(self.btn_1d_random)
        ctrl_layout.addWidget(self.btn_1d_single)
        ctrl_layout.addWidget(self.btn_1d_start)
        ctrl_layout.addWidget(self.btn_1d_pause)
        ctrl_layout.addWidget(self.btn_1d_step)
        ctrl_layout.addWidget(self.btn_1d_clear)
        
        top_controls.addWidget(ctrl_group)
        layout.addLayout(top_controls)

        # Grid unidimensional
        grid_group = QGroupBox("Evolución Unidimensional - Cada fila es una generación")
        grid_layout = QVBoxLayout(grid_group)
        self.table_1d = QTableWidget()
        self.table_1d.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table_1d.horizontalHeader().setVisible(False)
        self.table_1d.verticalHeader().setVisible(False)
        self.table_1d.setShowGrid(True)
        grid_layout.addWidget(self.table_1d)
        layout.addWidget(grid_group)

        # Información sobre reglas
        info_group = QGroupBox("Información de la Regla")
        info_layout = QVBoxLayout(info_group)
        self.info_1d_label = QLabel()
        self.info_1d_label.setWordWrap(True)
        info_layout.addWidget(self.info_1d_label)
        layout.addWidget(info_group)

        # Conexiones unidimensionales
        self.btn_1d_random.clicked.connect(self._1d_random_initial)
        self.btn_1d_single.clicked.connect(self._1d_single_initial)
        self.btn_1d_start.clicked.connect(self._1d_start)
        self.btn_1d_pause.clicked.connect(self._1d_pause)
        self.btn_1d_step.clicked.connect(self._1d_step)
        self.btn_1d_clear.clicked.connect(self._1d_clear)
        self.combo_1d_rules.currentTextChanged.connect(self._on_1d_rule_changed)
        self.spin_1d_width.valueChanged.connect(self._on_1d_size_changed)
        self.spin_1d_generations.valueChanged.connect(self._on_1d_generations_changed)

        # Actualizar información inicial
        self._update_1d_info()

    def _init_1d_grid(self):
        """Inicializar grid unidimensional"""
        width = self._1d_width
        generations = self._1d_generations
        
        self.table_1d.clear()
        self.table_1d.setRowCount(generations)
        self.table_1d.setColumnCount(width)
        
        # Tamaño de celdas
        cell_size = max(3, min(10, int(800 / width)))
        for c in range(width):
            self.table_1d.setColumnWidth(c, cell_size)
        for r in range(generations):
            self.table_1d.setRowHeight(r, cell_size)
        
        # Inicializar estado 1D
        self._1d_state = [0] * width
        self._1d_history = []
        
        # Crear items
        for r in range(generations):
            for c in range(width):
                item = QTableWidgetItem()
                item.setFlags(item.flags() ^ Qt.ItemFlag.ItemIsEditable)
                item.setBackground(QBrush(self._cell_dead_color))
                self.table_1d.setItem(r, c, item)

    def _1d_rule_function(self, left, center, right):
        """Aplicar regla unidimensional a tripleta"""
        rule_num = self._current_1d_rule
        pattern = (left << 2) | (center << 1) | right
        return (rule_num >> pattern) & 1

    def _1d_evolve_generation(self):
        """Evolucionar una generación 1D"""
        width = len(self._1d_state)
        new_state = [0] * width
        
        for i in range(width):
            left = self._1d_state[(i-1) % width]
            center = self._1d_state[i]
            right = self._1d_state[(i+1) % width]
            new_state[i] = self._1d_rule_function(left, center, right)
        
        return new_state

    def _1d_display(self):
        """Mostrar estado unidimensional en la tabla"""
        width = self._1d_width
        generations = self._1d_generations
        
        # Limitar historial al número de generaciones
        while len(self._1d_history) > generations:
            self._1d_history.pop(0)
        
        # Mostrar todas las generaciones
        for gen_idx, generation in enumerate(self._1d_history):
            if gen_idx >= generations:
                break
            for cell_idx, cell in enumerate(generation):
                if cell_idx < width:
                    item = self.table_1d.item(gen_idx, cell_idx)
                    if item:
                        color = self._cell_alive_color if cell else self._cell_dead_color
                        item.setBackground(QBrush(color))

    def _1d_random_initial(self):
        """Estado inicial aleatorio 1D"""
        self._1d_state = [random.randint(0, 1) for _ in range(self._1d_width)]
        self._1d_history = [self._1d_state.copy()]
        self._1d_display()

    def _1d_single_initial(self):
        """Una sola célula viva en el centro"""
        self._1d_state = [0] * self._1d_width
        self._1d_state[self._1d_width // 2] = 1
        self._1d_history = [self._1d_state.copy()]
        self._1d_display()

    def _1d_step(self):
        """Evolucionar una generación 1D"""
        if not self._1d_history:
            self._1d_history = [self._1d_state.copy()]
        
        new_gen = self._1d_evolve_generation()
        self._1d_state = new_gen
        self._1d_history.append(new_gen.copy())
        self._1d_display()

    def _1d_start(self):
        """Iniciar evolución automática 1D"""
        if not self._1d_running:
            self._1d_running = True
            self._timer.start(self._timer_interval)

    def _1d_pause(self):
        """Pausar evolución 1D"""
        if self._1d_running:
            self._1d_running = False
            self._timer.stop()

    def _1d_clear(self):
        """Limpiar grid 1D"""
        self._1d_state = [0] * self._1d_width
        self._1d_history = []
        self._init_1d_grid()

    def _on_1d_rule_changed(self, rule_name):
        """Cambiar regla unidimensional"""
        self._current_1d_rule = self._unidimensional_rules[rule_name]
        self._update_1d_info()

    def _on_1d_size_changed(self, value):
        """Cambiar tamaño 1D"""
        self._1d_width = value
        self._1d_clear()

    def _on_1d_generations_changed(self, value):
        """Cambiar número de generaciones"""
        self._1d_generations = value
        self._init_1d_grid()
        if self._1d_history:
            self._1d_display()

    def _update_1d_info(self):
        """Actualizar información sobre la regla 1D actual"""
        rule_num = self._current_1d_rule
        info = f"Regla {rule_num}:\n"
        
        if rule_num == 30:
            info += "Comportamiento caótico, genera números aleatorios"
        elif rule_num == 90:
            info += "Patrón fractal tipo Sierpinski, comportamiento lineal"
        elif rule_num == 110:
            info += "Universalidad computacional, comportamiento complejo"
        elif rule_num == 184:
            info += "Modelo de tráfico vehicular, partículas que se mueven"
        elif rule_num == 54:
            info += "Patrones complejos, comportamiento interesante"
        elif rule_num == 73:
            info += "Patrones repetitivos, comportamiento estructurado"
            
        info += f"\n\nBinario: {rule_num:08b}"
        self.info_1d_label.setText(info)

    # =============================================================================
    # COVID-19 - MODELO EPIDEMIOLÓGICO (CORREGIDO)
    # =============================================================================
    def _setup_covid_tab(self):
        layout = QVBoxLayout(self.covid_tab)

        # main content: grid + plot (plot used for COVID)
        content_row = QHBoxLayout()

        # grid widget
        self.table_covid = QTableWidget()
        self.table_covid.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table_covid.horizontalHeader().setVisible(False)
        self.table_covid.verticalHeader().setVisible(False)
        self.table_covid.setShowGrid(True)
        content_row.addWidget(self.table_covid, stretch=3)

        # right panel: covid-specific controls + plot
        right_v = QVBoxLayout()

        # COVID controls group
        self.covid_controls_group = QGroupBox("Controles COVID-19")
        covid_layout = QFormLayout(self.covid_controls_group)
        
        self.cov_init_inf = QDoubleSpinBox()
        self.cov_init_inf.setRange(0.0, 1.0)
        self.cov_init_inf.setSingleStep(0.01)
        self.cov_init_inf.setValue(self.covid_init_infected_pct)
        self.cov_init_inf.valueChanged.connect(self._on_covid_params_changed)
        
        self.cov_init_vac = QDoubleSpinBox()
        self.cov_init_vac.setRange(0.0, 1.0)
        self.cov_init_vac.setSingleStep(0.01)
        self.cov_init_vac.setValue(self.covid_init_vaccinated_pct)
        self.cov_init_vac.valueChanged.connect(self._on_covid_params_changed)
        
        self.cov_p_infect = QDoubleSpinBox()
        self.cov_p_infect.setRange(0.0, 1.0)
        self.cov_p_infect.setSingleStep(0.01)
        self.cov_p_infect.setValue(self.covid_p_infect)
        self.cov_p_infect.valueChanged.connect(self._on_covid_params_changed)
        
        self.cov_p_move = QDoubleSpinBox()
        self.cov_p_move.setRange(0.0, 1.0)
        self.cov_p_move.setSingleStep(0.01)
        self.cov_p_move.setValue(self.covid_p_move)
        self.cov_p_move.valueChanged.connect(self._on_covid_params_changed)
        
        self.cov_rec_time = QSpinBox()
        self.cov_rec_time.setRange(1, 1000)
        self.cov_rec_time.setValue(self.covid_recovery_time)
        self.cov_rec_time.valueChanged.connect(self._on_covid_params_changed)
        
        covid_layout.addRow("Infectados iniciales %", self.cov_init_inf)
        covid_layout.addRow("Vacunados iniciales %", self.cov_init_vac)
        covid_layout.addRow("Prob contagio (p)", self.cov_p_infect)
        covid_layout.addRow("Prob movimiento (p_move)", self.cov_p_move)
        covid_layout.addRow("Tiempo recuperación (pasos)", self.cov_rec_time)

        # COVID action buttons
        cov_btn_row = QHBoxLayout()
        self.btn_covid_random = QPushButton("Generar COVID aleatorio")
        self.btn_covid_start = QPushButton("Iniciar COVID")
        self.btn_covid_pause = QPushButton("Pausar COVID")
        self.btn_covid_step = QPushButton("Siguiente COVID")
        cov_btn_row.addWidget(self.btn_covid_random)
        cov_btn_row.addWidget(self.btn_covid_start)
        cov_btn_row.addWidget(self.btn_covid_pause)
        cov_btn_row.addWidget(self.btn_covid_step)
        covid_layout.addRow(cov_btn_row)
        right_v.addWidget(self.covid_controls_group)

        # plot (matplotlib)
        self.fig = Figure(figsize=(4, 3))
        self.canvas = FigureCanvas(self.fig)
        self.ax = self.fig.add_subplot(111)
        right_v.addWidget(self.canvas)

        content_row.addLayout(right_v, stretch=2)
        layout.addLayout(content_row)

        # COVID connections
        self.btn_covid_random.clicked.connect(self._covid_generate_random)
        self.btn_covid_start.clicked.connect(self._covid_start)
        self.btn_covid_pause.clicked.connect(self._covid_pause)
        self.btn_covid_step.clicked.connect(self._covid_step)
        self.table_covid.cellClicked.connect(self._on_cell_clicked)

    def _init_covid_grid(self):
        """Inicializar grid específico para COVID"""
        self.table_covid.clear()
        self.table_covid.setRowCount(self._n)
        self.table_covid.setColumnCount(self._n)
        
        cell_size = max(8, min(28, int(600 / self._n)))
        for r in range(self._n):
            self.table_covid.setRowHeight(r, cell_size)
        for c in range(self._n):
            self.table_covid.setColumnWidth(c, cell_size)
        
        # Inicializar estados COVID
        self._state_covid = [["S" for _ in range(self._n)] for __ in range(self._n)]
        self._infection_age = [[0 for _ in range(self._n)] for __ in range(self._n)]
        
        # Crear items de tabla específicos para COVID
        for r in range(self._n):
            for c in range(self._n):
                item = QTableWidgetItem()
                item.setFlags(item.flags() ^ Qt.ItemFlag.ItemIsEditable)
                # Color inicial para susceptibles (blanco)
                item.setBackground(QBrush(QColor(255, 255, 255)))
                self.table_covid.setItem(r, c, item)
        
        self._clear_covid_stats()

    def _on_covid_params_changed(self):
        """Actualizar parámetros COVID cuando cambian los controles"""
        self.covid_init_infected_pct = self.cov_init_inf.value()
        self.covid_init_vaccinated_pct = self.cov_init_vac.value()
        self.covid_p_infect = self.cov_p_infect.value()
        self.covid_p_move = self.cov_p_move.value()
        self.covid_recovery_time = self.cov_rec_time.value()

    # =============================================================================
    # MÉTODOS COMUNES - GRID Y ESTADOS
    # =============================================================================
    def _create_grid(self, n):
        """Crear grid para Conway y COVID por separado"""
        self._n = int(n)
        
        # Grid Conway
        self.table.clear()
        self.table.setRowCount(self._n)
        self.table.setColumnCount(self._n)
        cell_size = max(8, min(28, int(600 / self._n)))
        for r in range(self._n):
            self.table.setRowHeight(r, cell_size)
        for c in range(self._n):
            self.table.setColumnWidth(c, cell_size)
        
        # Inicializar estados Conway
        self._state = [[0 for _ in range(self._n)] for __ in range(self._n)]
        
        # Crear items de tabla Conway
        for r in range(self._n):
            for c in range(self._n):
                item = QTableWidgetItem()
                item.setFlags(item.flags() ^ Qt.ItemFlag.ItemIsEditable)
                item.setBackground(QBrush(self._cell_dead_color))
                self.table.setItem(r, c, item)
        
        self._history_hashes.clear()
        
        # También inicializar grid COVID
        self._init_covid_grid()

    def _set_cell_state(self, r, c, alive):
        """Conway painting (alive=True/False)."""
        if r < 0 or c < 0 or r >= self._n or c >= self._n:
            return
        self._state[r][c] = 1 if alive else 0
        item = self.table.item(r, c)
        if item is None:
            item = QTableWidgetItem()
            item.setFlags(item.flags() ^ Qt.ItemFlag.ItemIsEditable)
            self.table.setItem(r, c, item)
        item.setBackground(QBrush(self._cell_alive_color if alive else self._cell_dead_color))

    def _set_cell_state_covid(self, r, c, state):
        """COVID painting: state in {'S','I','R','V'} - CORREGIDO"""
        if r < 0 or c < 0 or r >= self._n or c >= self._n:
            return
            
        self._state_covid[r][c] = state
        item = self.table_covid.item(r, c)
        
        if item is None:
            # Crear item si no existe
            item = QTableWidgetItem()
            item.setFlags(item.flags() ^ Qt.ItemFlag.ItemIsEditable)
            self.table_covid.setItem(r, c, item)
            
        # Mapa de colores más distintivo
        color_map = {
            "S": QColor(255, 255, 255),    # Blanco - Susceptible
            "I": QColor(255, 50, 50),      # Rojo - Infectado
            "R": QColor(50, 200, 50),      # Verde - Recuperado
            "V": QColor(50, 100, 255),     # Azul - Vacunado
        }
        
        item.setBackground(QBrush(color_map.get(state, QColor(255, 255, 255))))

    def _on_cell_clicked(self, row, col):
        current_tab = self.tabs.currentIndex()
        
        if current_tab == 0:  # Conway
            new_state = 0 if self._state[row][col] else 1
            self._set_cell_state(row, col, new_state)
            self._history_hashes.clear()
            
        elif current_tab == 2:  # COVID-19 - CORREGIDO
            cur = self._state_covid[row][col]
            order = ["S", "I", "R", "V"]
            next_state = order[(order.index(cur) + 1) % len(order)]
            self._set_cell_state_covid(row, col, next_state)
            
            if next_state == "I":
                self._infection_age[row][col] = 0
            else:
                self._infection_age[row][col] = 0
                
            self._clear_covid_stats()

    # =============================================================================
    # MÉTODOS DE CONTROL COMUNES
    # =============================================================================
    def _on_timer_tick(self):
        """Tick del timer para simulaciones"""
        current_tab = self.tabs.currentIndex()
        if current_tab == 0 and self._running:  # Conway
            self.step_once()
        elif current_tab == 1 and self._1d_running:  # Unidimensionales
            self._1d_step()
        elif current_tab == 2 and self._covid_running:  # COVID-19
            self._covid_step_once()

    def start(self):
        """Iniciar simulación Conway"""
        if not self._running:
            self._running = True
            self._timer.start(self._timer_interval)

    def pause(self):
        """Pausar simulación Conway"""
        if self._running:
            self._running = False
            self._timer.stop()

    def _on_speed_change(self, val):
        """Cambiar velocidad"""
        self._timer_interval = int(val)
        if self._timer.isActive():
            self._timer.setInterval(self._timer_interval)

    def clear(self):
        """Limpiar Conway"""
        for r in range(self._n):
            for c in range(self._n):
                self._set_cell_state(r, c, 0)
        self._history_hashes.clear()

    def randomize(self, fill_prob=0.3):
        """Generar estado aleatorio Conway"""
        for r in range(self._n):
            for c in range(self._n):
                alive = random.random() < fill_prob
                self._set_cell_state(r, c, alive)
        self._history_hashes.clear()

    def _on_random(self):
        self.randomize(fill_prob=0.3)

    def _on_apply_size(self):
        n = self.spin_n.value()
        self._create_grid(n)

    def _on_toroidal_change(self, state):
        self._toroidal = (state == Qt.CheckState.Checked)

    def _on_tab_changed(self, index):
        """Cambio entre pestañas"""
        # Detener todas las simulaciones
        if self._timer.isActive():
            self._timer.stop()
        self._running = False
        self._1d_running = False
        self._covid_running = False
        
        # Inicializar automáticamente al cambiar a COVID
        if index == 2:  # Pestaña COVID-19
            self._init_covid_grid()
            self._covid_generate_random()

    # =============================================================================
    # CONWAY - IMPLEMENTACIÓN
    # =============================================================================
    def _neighbor_coords(self, r, c):
        coords = []
        for dr in (-1, 0, 1):
            for dc in (-1, 0, 1):
                if dr == 0 and dc == 0:
                    continue
                rr = r + dr; cc = c + dc
                if self._toroidal:
                    rr %= self._n; cc %= self._n
                    coords.append((rr, cc))
                else:
                    if 0 <= rr < self._n and 0 <= cc < self._n:
                        coords.append((rr, cc))
        return coords

    def set_rules_from_string(self, rule_str):
        s = rule_str.strip().lower()
        if s == "conway":
            s = "b3/s23"
        if "/" not in s:
            raise ValueError("Formato inválido. Use 'B3/S23'.")
        bpart, spart = s.split("/")
        if not (bpart.startswith("b") and spart.startswith("s")):
            raise ValueError("Formato inválido. Use 'B3/S23'.")
        self.birth_set = set(int(ch) for ch in bpart[1:] if ch.isdigit())
        self.survive_set = set(int(ch) for ch in spart[1:] if ch.isdigit())

    def step_once(self):
        """Conway single step"""
        if not hasattr(self, "birth_set") or not hasattr(self, "survive_set"):
            self.set_rules_from_string("B3/S23")

        new_state = [[0 for _ in range(self._n)] for __ in range(self._n)]
        for r in range(self._n):
            for c in range(self._n):
                alive = self._state[r][c] == 1
                neighbors = sum(1 for rr, cc in self._neighbor_coords(r, c) if self._state[rr][cc])
                if alive:
                    new_state[r][c] = 1 if (neighbors in self.survive_set) else 0
                else:
                    new_state[r][c] = 1 if (neighbors in self.birth_set) else 0

        changed = False
        for r in range(self._n):
            for c in range(self._n):
                if bool(new_state[r][c]) != bool(self._state[r][c]):
                    changed = True
                self._set_cell_state(r, c, bool(new_state[r][c]))

        self._push_history_hash()

        if self.chk_autostop_extinct.isChecked():
            if all(self._state[r][c] == 0 for r in range(self._n) for c in range(self._n)):
                self.pause()
                QMessageBox.information(self, "Autostop", "El mundo se extinguió (todas las celdas muertas).")
                return
        if self.chk_autostop_stagnant.isChecked() and not changed:
            self.pause()
            QMessageBox.information(self, "Autostop", "No hubo cambios (estancamiento).")
            return
        if self.chk_autostop_cycle.isChecked() and self._detect_cycle():
            self.pause()
            QMessageBox.information(self, "Autostop", "Ciclo detectado (estado repetido).")
            return

    def _state_to_bytes(self):
        flat = bytearray()
        for r in range(self._n):
            for c in range(self._n):
                flat.append(1 if self._state[r][c] else 0)
        return bytes(flat)

    def _push_history_hash(self):
        b = self._state_to_bytes()
        h = hashlib.sha256(b).hexdigest()
        self._history_hashes.append(h)
        if len(self._history_hashes) > self._history_len:
            self._history_hashes.pop(0)

    def _detect_cycle(self):
        if not self._history_hashes:
            return False
        cur = self._history_hashes[-1]
        return self._history_hashes.count(cur) > 1

    # =============================================================================
    # COVID-19 - IMPLEMENTACIÓN (CORREGIDA)
    # =============================================================================
    def _clear_covid_stats(self):
        self._covid_stats = {
            "S": deque(maxlen=self._max_stats_len),
            "I": deque(maxlen=self._max_stats_len),
            "R": deque(maxlen=self._max_stats_len),
            "V": deque(maxlen=self._max_stats_len)
        }
        self._redraw_plot()

    def _covid_count_states(self):
        counts = {"S": 0, "I": 0, "R": 0, "V": 0}
        for r in range(self._n):
            for c in range(self._n):
                s = self._state_covid[r][c]
                counts[s] += 1
        return counts

    def _covid_generate_random(self):
        """Usar parámetros actuales de los controles"""
        # Actualizar parámetros desde controles
        self._on_covid_params_changed()
        
        p_inf = self.covid_init_infected_pct
        p_vac = self.covid_init_vaccinated_pct
        
        for r in range(self._n):
            for c in range(self._n):
                rnd = random.random()
                if rnd < p_inf:
                    self._set_cell_state_covid(r, c, "I")
                    self._infection_age[r][c] = 0
                elif rnd < p_inf + p_vac:
                    self._set_cell_state_covid(r, c, "V")
                    self._infection_age[r][c] = 0
                else:
                    self._set_cell_state_covid(r, c, "S")
                    self._infection_age[r][c] = 0
                    
        self._clear_covid_stats()
        self._push_covid_stats()
        self._redraw_plot()

    def _push_covid_stats(self):
        counts = self._covid_count_states()
        for k in ("S", "I", "R", "V"):
            self._covid_stats[k].append(counts[k])

    def _redraw_plot(self):
        self.ax.clear()
        x = list(range(len(self._covid_stats["S"])))
        if x:
            self.ax.plot(x, list(self._covid_stats["S"]), label="S (Susceptibles)", color='blue')
            self.ax.plot(x, list(self._covid_stats["I"]), label="I (Infectados)", color='red')
            self.ax.plot(x, list(self._covid_stats["R"]), label="R (Recuperados)", color='green')
            self.ax.plot(x, list(self._covid_stats["V"]), label="V (Vacunados)", color='orange')
            self.ax.legend()
            self.ax.set_xlabel("Pasos de tiempo")
            self.ax.set_ylabel("Número de individuos")
            self.ax.set_title("Evolución de la Pandemia COVID-19")
            self.ax.grid(True, alpha=0.3)
        else:
            self.ax.text(0.5, 0.5, "No hay datos COVID", ha='center', va='center', transform=self.ax.transAxes)
        self.canvas.draw()

    def _covid_step_once(self):
        """Usar parámetros actualizados"""
        # Actualizar parámetros desde controles
        self._on_covid_params_changed()
        
        p_infect = self.covid_p_infect
        p_move = self.covid_p_move
        rec_time = self.covid_recovery_time

        # Movement phase
        swaps = []
        for r in range(self._n):
            for c in range(self._n):
                if random.random() < p_move:
                    neigh = self._neighbor_coords(r, c)
                    if neigh:
                        rr, cc = random.choice(neigh)
                        swaps.append((r, c, rr, cc))
        
        for (r, c, rr, cc) in swaps:
            self._state_covid[r][c], self._state_covid[rr][cc] = self._state_covid[rr][cc], self._state_covid[r][c]
            self._infection_age[r][c], self._infection_age[rr][cc] = self._infection_age[rr][cc], self._infection_age[r][c]
            self._set_cell_state_covid(r, c, self._state_covid[r][c])
            self._set_cell_state_covid(rr, cc, self._state_covid[rr][cc])

        # Infection & recovery phase
        new_infections = []
        for r in range(self._n):
            for c in range(self._n):
                if self._state_covid[r][c] == "I":
                    # Infectar vecinos susceptibles
                    for rr, cc in self._neighbor_coords(r, c):
                        if self._state_covid[rr][cc] == "S" and random.random() < p_infect:
                            new_infections.append((rr, cc))
                    
                    # Avanzar edad de infección
                    self._infection_age[r][c] += 1
                    if self._infection_age[r][c] >= rec_time:
                        self._set_cell_state_covid(r, c, "R")
                        self._infection_age[r][c] = 0

        # Aplicar nuevas infecciones
        for rr, cc in new_infections:
            if self._state_covid[rr][cc] == "S":
                self._set_cell_state_covid(rr, cc, "I")
                self._infection_age[rr][cc] = 0

        self._push_covid_stats()
        self._redraw_plot()

        # AUTOSTOP
        counts = self._covid_count_states()
        if counts.get("I", 0) == 0:
            self._covid_running = False
            if self._timer.isActive():
                self._timer.stop()
            QMessageBox.information(self, "Autostop COVID", "Epidemia contenida: no quedan infectados (I=0).")

    def _covid_start(self):
        if not self._covid_running:
            self._covid_running = True
            self._timer.start(self._timer_interval)

    def _covid_pause(self):
        if self._covid_running:
            self._covid_running = False
            if self._timer.isActive():
                self._timer.stop()

    def _covid_step(self):
        self._covid_step_once()

    # =============================================================================
    # MÉTODOS RESTANTES (PRESETS, LOAD/SAVE, ETC.)
    # =============================================================================
    def _on_apply_rule(self):
        txt = self.le_rule.text().strip()
        try:
            self.set_rules_from_string(txt)
            QMessageBox.information(self, "Regla aplicada", f"Regla aplicada: {txt}")
        except Exception as e:
            QMessageBox.critical(self, "Error regla", str(e))

    def _on_load_preset(self):
        key = self.combo_presets.currentText()
        self.clear()
        mid = self._n // 2
        if key == "Glider":
            coords = [(0,1),(1,2),(2,0),(2,1),(2,2)]
            base_r, base_c = mid-2, mid-2
        elif key == "Blinker":
            coords = [(0,0),(0,1),(0,2)]
            base_r, base_c = mid, mid-1
        elif key == "Toad":
            coords = [(-1,0),(-1,1),(-1,2),(0,-1),(0,0),(0,1)]
            base_r, base_c = mid, mid
        elif key == "Beacon":
            coords = [(0,0),(0,1),(1,0),(1,1),(2,2),(2,3),(3,2),(3,3)]
            base_r, base_c = mid-2, mid-2
        elif key == "Gosper Glider Gun (small)":
            coords = [(0,1),(0,2),(1,0),(1,1),(1,2),(3,10),(3,11),(4,10),(4,11)]
            base_r, base_c = 2, 2
        else:
            QMessageBox.information(self, "Preset", "Selecciona un preset válido.")
            return
        for dr, dc in coords:
            self._set_cell_state(base_r + dr, base_c + dc, True)
        self._history_hashes.clear()

    def _on_save_csv(self):
        path, _ = QFileDialog.getSaveFileName(self, "Guardar estado CSV", "automata_state.csv", "CSV Files (*.csv)")
        if not path:
            return
        try:
            with open(path, "w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                current_tab = self.tabs.currentIndex()
                writer.writerow(["mode", "conway" if current_tab == 0 else "covid" if current_tab == 2 else "1d"])
                writer.writerow(["n", self._n, "toroidal", int(self._toroidal)])
                
                if current_tab == 0:  # Conway
                    for r in range(self._n):
                        writer.writerow(self._state[r])
                elif current_tab == 2:  # COVID-19
                    for r in range(self._n):
                        writer.writerow(self._state_covid[r])
                elif current_tab == 1:  # Unidimensionales
                    writer.writerow(["width", self._1d_width, "generations", self._1d_generations])
                    writer.writerow(["rule", self._current_1d_rule])
                    for gen in self._1d_history:
                        writer.writerow(gen)
                        
            QMessageBox.information(self, "Guardado", f"Estado guardado en {path}")
        except Exception as e:
            QMessageBox.critical(self, "Error guardado", str(e))

    def _on_load_csv(self):
        path, _ = QFileDialog.getOpenFileName(self, "Cargar estado CSV", "", "CSV Files (*.csv)")
        if not path:
            return
        try:
            with open(path, "r", encoding="utf-8") as f:
                reader = csv.reader(f)
                header = next(reader)
                mode = "conway"
                if header[0] == "mode":
                    mode = header[1]
                    header = next(reader)
                
                if mode == "1d":
                    # Cargar unidimensional
                    if header[0] == "width":
                        self._1d_width = int(header[1])
                        self._1d_generations = int(header[3])
                        self.spin_1d_width.setValue(self._1d_width)
                        self.spin_1d_generations.setValue(self._1d_generations)
                        rule_row = next(reader)
                        self._current_1d_rule = int(rule_row[1])
                        self._init_1d_grid()
                        self._1d_history = []
                        for row in reader:
                            if row:
                                self._1d_history.append([int(x) for x in row])
                        if self._1d_history:
                            self._1d_state = self._1d_history[-1].copy()
                            self._1d_display()
                    self.tabs.setCurrentIndex(1)
                else:
                    # Cargar Conway o COVID
                    if header[0] == "n":
                        self._n = int(header[1])
                        tor = int(header[3]) if len(header) > 3 else 0
                        self._toroidal = bool(tor)
                        self.spin_n.setValue(self._n)
                        self._create_grid(self._n)
                        rows = list(reader)
                    else:
                        rows = [header] + list(reader)
                    
                    for r_idx, row in enumerate(rows):
                        for c_idx, val in enumerate(row):
                            if r_idx < self._n and c_idx < self._n:
                                token = val.strip()
                                if mode == "conway":
                                    try:
                                        v = int(float(token))
                                        self._set_cell_state(r_idx, c_idx, bool(v))
                                    except:
                                        self._set_cell_state(r_idx, c_idx, 0)
                                else:
                                    if token.upper() in ("S", "I", "R", "V"):
                                        self._set_cell_state_covid(r_idx, c_idx, token.upper())
                    
                    if mode == "conway":
                        self.tabs.setCurrentIndex(0)
                    else:
                        self.tabs.setCurrentIndex(2)
                        self._clear_covid_stats()
                        self._redraw_plot()
                        
            QMessageBox.information(self, "Cargado", f"Estado cargado desde {path}")
            self._history_hashes.clear()
            
        except Exception as e:
            QMessageBox.critical(self, "Error carga", str(e))

    # Métodos públicos para integración
    def cargar_desde_ri(self, ri_list, umbral=0.5):
        """Cargar estado Conway desde lista Ri"""
        for i in range(min(len(ri_list), self._n * self._n)):
            r, c = i // self._n, i % self._n
            alive = ri_list[i] >= umbral
            self._set_cell_state(r, c, alive)
        self._history_hashes.clear()

    def cargar_topk_desde_ri(self, ri_list, k):
        """Cargar top-K celdas desde lista Ri"""
        if k <= 0:
            return
        indexed = [(i, ri_list[i] if i < len(ri_list) else 0.0) for i in range(min(len(ri_list), self._n * self._n))]
        if len(indexed) < self._n * self._n:
            indexed += [(i, 0.0) for i in range(len(indexed), self._n * self._n)]
        indexed_sorted = sorted(indexed, key=lambda x: x[1], reverse=True)
        top_indices = set(i for i, _ in indexed_sorted[:k])
        for i in range(self._n * self._n):
            r, c = i // self._n, i % self._n
            alive = (i in top_indices)
            self._set_cell_state(r, c, alive)
        self._history_hashes.clear()

    def get_state_flat(self):
        """Obtener estado actual como lista plana"""
        current_tab = self.tabs.currentIndex()
        if current_tab == 0:  # Conway
            return [cell for row in self._state for cell in row]
        elif current_tab == 1:  # Unidimensionales
            return self._1d_state if self._1d_state else []
        elif current_tab == 2:  # COVID-19
            state_map = {"S": 0, "I": 1, "R": 2, "V": 3}
            return [state_map[state] for row in self._state_covid for state in row]
        return []

    # Wrappers públicos
    def cargar_desde_ri_public(self, ri_list, umbral=0.5):
        self.cargar_desde_ri(ri_list, umbral)

    def cargar_topk_desde_ri_public(self, ri_list, k):
        self.cargar_topk_desde_ri(ri_list, k)