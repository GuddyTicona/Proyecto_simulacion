# ui/tab_automata_celular.py
"""
Autómata Celular (Conway) + Modo COVID-19 - Tab independiente
Clase: TabAutomataCelular

Modo Conway: comportamiento clásico B3/S23 (ya existente).
Modo COVID-19: autómata epidemiológico simple con movilidad y estados S/I/R/V,
    controles para probabilidad de contagio, movilidad, recuperación, % vacunados,
    y gráfica dinámica de evolución.
"""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QSpinBox, QPushButton,
    QTableWidget, QTableWidgetItem, QSlider, QCheckBox, QGroupBox, QLineEdit,
    QFileDialog, QMessageBox, QComboBox, QFormLayout, QDoubleSpinBox
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
        # defaults (Conway)
        self._n = 20
        self._cell_alive_color = QColor(0, 0, 0)  # negro para vivo (estilo clásico)
        self._cell_dead_color = QColor(255, 255, 255)  # blanco para muerto
        self._running = False
        self._toroidal = False
        self._timer_interval = 200
        self._timer = QTimer(self)
        self._timer.timeout.connect(self._on_timer_tick)

        # Conway state
        self._state = []  # used for Conway (0/1)
        self._history_hashes = []
        self._history_len = 80
        self.birth_set = {3}
        self.survive_set = {2, 3}
        self.rule_sequence = []
        self.rule_seq_index = 0

        # COVID state (separate)
        # states: 'S' (susceptible), 'I' (infected), 'R' (recovered), 'V' (vaccinated)
        self._state_covid = []
        self._infection_age = []  # counters for infected cells
        self._covid_running = False
        self._covid_stats = {"S": [], "I": [], "R": [], "V": []}
        self._max_stats_len = 1000

        # default COVID params
        self.covid_init_infected_pct = 0.02
        self.covid_init_vaccinated_pct = 0.0
        self.covid_p_infect = 0.3
        self.covid_p_move = 0.2
        self.covid_recovery_time = 10  # steps

        # UI and init
        self._init_ui()
        # create grid before invoking mode change so internal lists exist
        self._create_grid(self._n)
        # set initial mode visibility/behavior
        self._on_mode_changed(self.combo_mode.currentText())

    # ---------------- UI ----------------
    def _init_ui(self):
        main = QVBoxLayout(self)

        # MODE selector (Conway / COVID)
        mode_row = QHBoxLayout()
        mode_row.addWidget(QLabel("Modo:"))
        self.combo_mode = QComboBox()
        self.combo_mode.addItems(["Conway", "COVID-19"])
        mode_row.addWidget(self.combo_mode)
        mode_row.addStretch()
        main.addLayout(mode_row)

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

        main.addLayout(top_row)

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

        # Conway autostop options (only visible for Conway)
        self.chk_autostop_extinct = QCheckBox("Autostop si se extingue")
        self.chk_autostop_stagnant = QCheckBox("Autostop si sin cambios")
        self.chk_autostop_cycle = QCheckBox("Detectar ciclos")
        self.chk_autostop_extinct.setChecked(True)
        self.chk_autostop_stagnant.setChecked(True)
        ctrl_row.addWidget(self.chk_autostop_extinct)
        ctrl_row.addWidget(self.chk_autostop_stagnant)
        ctrl_row.addWidget(self.chk_autostop_cycle)

        main.addLayout(ctrl_row)

        # main content: grid + plot (plot used for COVID)
        content_row = QHBoxLayout()

        # grid widget
        self.table = QTableWidget()
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table.horizontalHeader().setVisible(False)
        self.table.verticalHeader().setVisible(False)
        self.table.setShowGrid(True)
        content_row.addWidget(self.table, stretch=3)

        # right panel: covid-specific controls + plot
        right_v = QVBoxLayout()

        # COVID controls group
        self.covid_controls_group = QGroupBox("Controles COVID-19")
        covid_layout = QFormLayout(self.covid_controls_group)
        self.cov_init_inf = QDoubleSpinBox()
        self.cov_init_inf.setRange(0.0, 1.0)
        self.cov_init_inf.setSingleStep(0.01)
        self.cov_init_inf.setValue(self.covid_init_infected_pct)
        self.cov_init_vac = QDoubleSpinBox()
        self.cov_init_vac.setRange(0.0, 1.0)
        self.cov_init_vac.setSingleStep(0.01)
        self.cov_init_vac.setValue(self.covid_init_vaccinated_pct)
        self.cov_p_infect = QDoubleSpinBox()
        self.cov_p_infect.setRange(0.0, 1.0)
        self.cov_p_infect.setSingleStep(0.01)
        self.cov_p_infect.setValue(self.covid_p_infect)
        self.cov_p_move = QDoubleSpinBox()
        self.cov_p_move.setRange(0.0, 1.0)
        self.cov_p_move.setSingleStep(0.01)
        self.cov_p_move.setValue(self.covid_p_move)
        self.cov_rec_time = QSpinBox()
        self.cov_rec_time.setRange(1, 1000)
        self.cov_rec_time.setValue(self.covid_recovery_time)
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
        main.addLayout(content_row)

        # bottom row: load/save for both modes
        bottom_row = QHBoxLayout()
        self.btn_save = QPushButton("Guardar CSV")
        self.btn_load = QPushButton("Cargar CSV")
        bottom_row.addWidget(self.btn_save)
        bottom_row.addWidget(self.btn_load)
        main.addLayout(bottom_row)

        # connections common
        self.btn_apply_size.clicked.connect(self._on_apply_size)
        self.chk_toroidal.stateChanged.connect(self._on_toroidal_change)
        self.slider_speed.valueChanged.connect(self._on_speed_change)

        # Conway connections
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

        # COVID connections
        self.btn_covid_random.clicked.connect(self._covid_generate_random)
        self.btn_covid_start.clicked.connect(self._covid_start)
        self.btn_covid_pause.clicked.connect(self._covid_pause)
        self.btn_covid_step.clicked.connect(self._covid_step)  # calls one-step wrapper
        # reuse load/save (already connected above)

        # mode selector
        self.combo_mode.currentTextChanged.connect(self._on_mode_changed)

    # ---------------- grid construction ----------------
    def _create_grid(self, n):
        self._n = int(n)
        self.table.clear()
        self.table.setRowCount(self._n)
        self.table.setColumnCount(self._n)
        cell_size = max(8, min(28, int(600 / self._n)))
        for r in range(self._n):
            self.table.setRowHeight(r, cell_size)
        for c in range(self._n):
            self.table.setColumnWidth(c, cell_size)
        # initialize both models' states
        self._state = [[0 for _ in range(self._n)] for __ in range(self._n)]
        self._state_covid = [["S" for _ in range(self._n)] for __ in range(self._n)]
        self._infection_age = [[0 for _ in range(self._n)] for __ in range(self._n)]
        # create table items
        for r in range(self._n):
            for c in range(self._n):
                item = QTableWidgetItem()
                item.setFlags(item.flags() ^ Qt.ItemFlag.ItemIsEditable)
                item.setBackground(QBrush(self._cell_dead_color))
                self.table.setItem(r, c, item)
        self._history_hashes.clear()
        # clear covid stats and plot
        self._clear_covid_stats()
        self._redraw_plot()

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
        """COVID painting: state in {'S','I','R','V'}"""
        if r < 0 or c < 0 or r >= self._n or c >= self._n:
            return
        self._state_covid[r][c] = state
        # infection age maintained separately
        item = self.table.item(r, c)
        if item is None:
            item = QTableWidgetItem()
            item.setFlags(item.flags() ^ Qt.ItemFlag.ItemIsEditable)
            self.table.setItem(r, c, item)
        # colors mapping (classic: white background, infected red, recovered green, vaccinated blue)
        color_map = {
            "S": QBrush(QColor(255, 255, 255)),
            "I": QBrush(QColor(200, 30, 30)),
            "R": QBrush(QColor(80, 180, 80)),
            "V": QBrush(QColor(80, 140, 220)),
        }
        item.setBackground(color_map.get(state, QBrush(QColor(255, 255, 255))))

    def _on_cell_clicked(self, row, col):
        mode = self.combo_mode.currentText()
        if mode == "Conway":
            new_state = 0 if self._state[row][col] else 1
            self._set_cell_state(row, col, new_state)
            self._history_hashes.clear()
        else:
            # cycle through states S -> I -> R -> V -> S
            cur = self._state_covid[row][col]
            order = ["S", "I", "R", "V"]
            next_state = order[(order.index(cur) + 1) % len(order)]
            self._set_cell_state_covid(row, col, next_state)
            if next_state != "I":
                self._infection_age[row][col] = 0
            else:
                self._infection_age[row][col] = 0
            # reset covid stats
            self._clear_covid_stats()
            self._redraw_plot()

    # ---------------- neighbors (shared utility) ----------------
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

    # ---------------- Conway: rules & step ----------------
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

    def set_rule_sequence(self, rule_list):
        self.rule_sequence = [r.strip() for r in rule_list]
        self.rule_seq_index = 0
        if self.rule_sequence:
            self.set_rules_from_string(self.rule_sequence[0])

    def _advance_rule_sequence(self):
        if self.rule_sequence:
            self.rule_seq_index = (self.rule_seq_index + 1) % len(self.rule_sequence)
            self.set_rules_from_string(self.rule_sequence[self.rule_seq_index])

    def step_once(self):
        """Conway single step"""
        # ensure rules
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

        if self.rule_sequence:
            self._advance_rule_sequence()

    def _on_timer_tick(self):
        mode = self.combo_mode.currentText()
        if mode == "Conway":
            self.step_once()
        else:
            self._covid_step_once()

    # ---------------- timer / controls ----------------
    def start(self):
        mode = self.combo_mode.currentText()
        if mode == "Conway":
            if not self._running:
                self._running = True
                self._timer.start(self._timer_interval)
        else:
            self._covid_start()

    def pause(self):
        mode = self.combo_mode.currentText()
        if mode == "Conway":
            if self._running:
                self._running = False
                self._timer.stop()
        else:
            self._covid_pause()

    def _on_speed_change(self, val):
        self._timer_interval = int(val)
        if self._timer.isActive():
            self._timer.setInterval(self._timer_interval)

    def clear(self):
        mode = self.combo_mode.currentText()
        if mode == "Conway":
            for r in range(self._n):
                for c in range(self._n):
                    self._set_cell_state(r, c, 0)
            self._history_hashes.clear()
        else:
            # reset covid grid to all susceptible
            for r in range(self._n):
                for c in range(self._n):
                    self._set_cell_state_covid(r, c, "S")
                    self._infection_age[r][c] = 0
            self._clear_covid_stats()
            self._redraw_plot()

    def randomize(self, fill_prob=0.3):
        mode = self.combo_mode.currentText()
        if mode == "Conway":
            for r in range(self._n):
                for c in range(self._n):
                    alive = random.random() < fill_prob
                    self._set_cell_state(r, c, alive)
            self._history_hashes.clear()
        else:
            self._covid_generate_random()

    def _on_random(self):
        # quick dialog-less random (30% by default)
        self.randomize(fill_prob=0.3)

    def _on_apply_size(self):
        n = self.spin_n.value()
        self._create_grid(n)

    def _on_toroidal_change(self, state):
        self._toroidal = (state == Qt.CheckState.Checked)

    # ---------------- history / cycle detection ----------------
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

    # ---------------- COVID implementation ----------------
    def _clear_covid_stats(self):
        self._covid_stats = {"S": deque(maxlen=self._max_stats_len),
                             "I": deque(maxlen=self._max_stats_len),
                             "R": deque(maxlen=self._max_stats_len),
                             "V": deque(maxlen=self._max_stats_len)}
        self._redraw_plot()

    def _covid_count_states(self):
        counts = {"S": 0, "I": 0, "R": 0, "V": 0}
        for r in range(self._n):
            for c in range(self._n):
                s = self._state_covid[r][c]
                counts[s] += 1
        return counts

    def _covid_generate_random(self):
        p_inf = float(self.cov_init_inf.value())
        p_vac = float(self.cov_init_vac.value())
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
        # trim handled by deque

    def _redraw_plot(self):
        self.ax.clear()
        # plot current stats
        x = list(range(len(self._covid_stats["S"])))
        if x:
            self.ax.plot(x, list(self._covid_stats["S"]), label="S")
            self.ax.plot(x, list(self._covid_stats["I"]), label="I")
            self.ax.plot(x, list(self._covid_stats["R"]), label="R")
            self.ax.plot(x, list(self._covid_stats["V"]), label="V")
            self.ax.legend()
            self.ax.set_xlabel("Generación")
            self.ax.set_ylabel("Número de individuos")
        else:
            self.ax.text(0.5, 0.5, "No hay datos COVID", ha='center')
        self.canvas.draw()

    def _covid_step_once(self):
        """
        COVID step:
         - Movement: with probability p_move, swap cell with a random neighbor (simulate mobility)
         - Infection: infected cells try to infect susceptible neighbors with p_infect
         - Recovery: infected with age >= recovery_time -> R
         - Auto-stop: if no infected remain, stop and show message.
        """
        p_infect = float(self.cov_p_infect.value())
        p_move = float(self.cov_p_move.value())
        rec_time = int(self.cov_rec_time.value())

        # Movement phase: build swaps
        swaps = []
        for r in range(self._n):
            for c in range(self._n):
                if random.random() < p_move:
                    neigh = self._neighbor_coords(r, c)
                    if not neigh:
                        continue
                    rr, cc = random.choice(neigh)
                    swaps.append((r, c, rr, cc))
        # apply swaps
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
                    for rr, cc in self._neighbor_coords(r, c):
                        if self._state_covid[rr][cc] == "S":
                            if random.random() < p_infect:
                                new_infections.append((rr, cc))
                    # age increment and possible recovery
                    self._infection_age[r][c] += 1
                    if self._infection_age[r][c] >= rec_time:
                        self._set_cell_state_covid(r, c, "R")
                        self._infection_age[r][c] = 0

        # apply new infections
        for rr, cc in new_infections:
            if self._state_covid[rr][cc] == "S":
                self._set_cell_state_covid(rr, cc, "I")
                self._infection_age[rr][cc] = 0

        # update stats and plot
        self._push_covid_stats()
        self._redraw_plot()

        # AUTOSTOP: si no quedan infectados, detener y notificar
        counts = self._covid_count_states()
        if counts.get("I", 0) == 0:
            # stop timer and flag
            self._covid_running = False
            if self._timer.isActive():
                self._timer.stop()
            QMessageBox.information(self, "Autostop COVID", "Epidemia contenida: no quedan infectados (I=0).")

    # COVID start/pause interfaces
    def _covid_start(self):
        if not self._covid_running:
            # ensure other mode's running flag is false
            self._running = False
            self._covid_running = True
            # set timer interval and start (shared QTimer)
            self._timer.setInterval(self._timer_interval)
            self._timer.start(self._timer_interval)

    def _covid_pause(self):
        if self._covid_running:
            self._covid_running = False
            if self._timer.isActive():
                self._timer.stop()

    def _covid_step(self):
        # wrapper called by button: execute one covid step
        self._covid_step_once()

    # ---------------- load/save / presets / cargar desde Ri (Conway + COVID) ----------------
    def cargar_desde_ri(self, ri_list, umbral=0.5):
        """Conway mapping: fila-major -> alive if Ri >= umbral"""
        flat_count = self._n * self._n
        for i in range(flat_count):
            r = i // self._n; c = i % self._n
            val = ri_list[i] if i < len(ri_list) else 0.0
            alive = bool(val >= umbral)
            self._set_cell_state(r, c, alive)
        self._history_hashes.clear()

    def cargar_topk_desde_ri(self, ri_list, k):
        """Conway top-k mapping"""
        flat_count = self._n * self._n
        if k <= 0:
            return
        indexed = [(i, ri_list[i] if i < len(ri_list) else 0.0) for i in range(min(len(ri_list), flat_count))]
        if len(indexed) < flat_count:
            indexed += [(i, 0.0) for i in range(len(indexed), flat_count)]
        indexed_sorted = sorted(indexed, key=lambda x: x[1], reverse=True)
        top_indices = set(i for i, _ in indexed_sorted[:k])
        for i in range(flat_count):
            r = i // self._n; c = i % self._n
            alive = (i in top_indices)
            self._set_cell_state(r, c, alive)
        self._history_hashes.clear()

    def _on_load_from_ri_clicked(self):
        QMessageBox.information(self, "Cargar desde Ri",
                                "Este botón está pensado para llamadas por código: tab.cargar_desde_ri(ri_list, umbral).")

    def _on_load_topk_clicked(self):
        QMessageBox.information(self, "Cargar top-K",
                                "Este botón está pensado para llamadas por código: tab.cargar_topk_desde_ri(ri_list, k).")

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
        path, _ = QFileDialog.getSaveFileName(self, "Guardar estado CSV", "life_state.csv", "CSV Files (*.csv)")
        if not path:
            return
        try:
            with open(path, "w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow(["n", self._n, "toroidal", int(self._toroidal)])
                # for conway save 0/1 matrix
                for r in range(self._n):
                    writer.writerow(self._state[r])
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
                try:
                    if header[0] == "n":
                        self._n = int(header[1])
                        tor = int(header[3]) if len(header) > 3 else 0
                        self._toroidal = bool(tor)
                        self.spin_n.setValue(self._n)
                        self._create_grid(self._n)
                        rows = list(reader)
                    else:
                        rows = [header] + list(reader)
                except Exception:
                    rows = [header] + list(reader)
                # try to detect whether saved file is Conway (0/1) or COVID (S/I/R/V)
                for r_idx, row in enumerate(rows):
                    for c_idx, val in enumerate(row):
                        if r_idx < self._n and c_idx < self._n:
                            token = val.strip()
                            # if token numeric -> Conway
                            try:
                                v = int(float(token))
                                self._set_cell_state(r_idx, c_idx, bool(v))
                            except Exception:
                                # text token -> assume COVID states
                                if token.upper() in ("S", "I", "R", "V"):
                                    self._set_cell_state_covid(r_idx, c_idx, token.upper())
                                else:
                                    # fallback: set dead
                                    self._set_cell_state(r_idx, c_idx, 0)
            QMessageBox.information(self, "Cargado", f"Estado cargado desde {path}")
            self._history_hashes.clear()
            self._clear_covid_stats()
            self._redraw_plot()
        except Exception as e:
            QMessageBox.critical(self, "Error carga", str(e))

    # -------------- integration helpers ----------------
    def get_state_flat(self):
        # returns Conway flat 0/1 if in Conway, else flatten covid states as chars
        mode = self.combo_mode.currentText()
        flat = []
        if mode == "Conway":
            for r in range(self._n):
                for c in range(self._n):
                    flat.append(self._state[r][c])
        else:
            for r in range(self._n):
                for c in range(self._n):
                    flat.append(self._state_covid[r][c])
        return flat

    def _on_mode_changed(self, mode_text):
        """Toggle UI and behavior depending on the selected mode.
        Limpia el grid automáticamente al cambiar de modo (comportamiento solicitado)."""
        mode = mode_text

        # always stop any running simulation first
        if self._timer.isActive():
            self._timer.stop()
        self._running = False
        self._covid_running = False

        # clear grid when switching mode to avoid interpretaciones mezcladas
        # (comportamiento 'más adecuado' que acordamos)
        if mode == "COVID-19":
            # switch to COVID: clear and initialize COVID state
            self.covid_controls_group.setVisible(True)
            self.btn_start.setText("Iniciar (modo activo)")
            self.btn_pause.setText("Pausar")
            self.btn_step.setText("Siguiente")
            self.btn_random.setText("Generar aleatorio (Conway)")
            # Clear and re-create COVID state clean
            for r in range(self._n):
                for c in range(self._n):
                    self._set_cell_state_covid(r, c, "S")
                    self._infection_age[r][c] = 0
            self._clear_covid_stats()
            # push initial counts and redraw
            self._push_covid_stats()
            self._redraw_plot()
        else:
            # Conway mode
            self.covid_controls_group.setVisible(False)
            self.btn_start.setText("Iniciar")
            self.btn_pause.setText("Pausar")
            self.btn_step.setText("Siguiente")
            self.btn_random.setText("Generar aleatorio")
            # Clear Conway grid
            for r in range(self._n):
                for c in range(self._n):
                    self._set_cell_state(r, c, 0)
            self._history_hashes.clear()
            # ensure display reflects cleared Conway
            for r in range(self._n):
                for c in range(self._n):
                    self._set_cell_state(r, c, 0)

    # Convenience public wrappers for external callers
    def cargar_desde_ri_public(self, ri_list, umbral=0.5):
        self.cargar_desde_ri(ri_list, umbral)

    def cargar_topk_desde_ri_public(self, ri_list, k):
        self.cargar_topk_desde_ri(ri_list, k)
