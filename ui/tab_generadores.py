# tab_generadores.py
# Versión completa del Tab "Generadores" con selector de distribuciones
# Integración con DistribucionesContinuas y DistribucionesDiscretas tal como están definidas.
# Idioma: español

import sys
import csv
import math
import random
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton,
    QTableWidget, QTableWidgetItem, QComboBox, QHeaderView, QStackedWidget,
    QDialog, QFileDialog, QMessageBox, QGroupBox, QFrame, QFormLayout
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

# Matplotlib (usar backend qtagg)
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import pandas as pd
import numpy as np

# Importar tus generadores existentes (deben existir esos módulos)
from generators.cuadrados_medios import CuadradosMedios
from generators.productos_medios import ProductosMedios
from generators.multiplicador_constante import MultiplicadorConstante

# Importar tus clases de distribuciones (tal como confirmaste)
from distribuciones.distribuciones_continuas import DistribucionesContinuas
from distribuciones.distribuciones_discretas import DistribucionesDiscretas


# ----------------- Widgets reutilizables -----------------
class ModernButton(QPushButton):
    def __init__(self, text, parent=None, color="#4a90e2", hover_color="#357abd", pressed_color="#2a5d90"):
        super().__init__(text, parent)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setMinimumHeight(35)
        self.setStyleSheet(f"""
            QPushButton {{
                background-color: {color};
                color: white;
                border: none;
                padding: 8px 12px;
                border-radius: 6px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: {hover_color};
            }}
            QPushButton:pressed {{
                background-color: {pressed_color};
            }}
            QPushButton:disabled {{
                background-color: #cccccc;
                color: #666666;
            }}
        """)


class ModernLineEdit(QLineEdit):
    def __init__(self, placeholder="", parent=None):
        super().__init__(parent)
        self.setPlaceholderText(placeholder)
        self.setMinimumHeight(30)
        self.setStyleSheet("""
            QLineEdit {
                padding: 6px;
                border: 1px solid #dcdcdc;
                border-radius: 6px;
                background-color: white;
            }
            QLineEdit:focus {
                border: 2px solid #6c5ce7;
            }
        """)


# ----------------- Dialog para preguntar si aplicar distribución -----------------
class ApplyDistributionDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Aplicar distribución")
        self.setModal(True)
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        lbl = QLabel("¿Desea aplicar una distribución a los números generados (Ri)?")
        lbl.setWordWrap(True)
        layout.addWidget(lbl)

        row = QHBoxLayout()
        btn_si = ModernButton("Sí", color="#00b894", hover_color="#00a382", pressed_color="#008f74")
        btn_no = ModernButton("No", color="#fd79a8", hover_color="#f24d8a", pressed_color="#e6337c")
        row.addStretch()
        row.addWidget(btn_si)
        row.addWidget(btn_no)
        layout.addLayout(row)

        btn_si.clicked.connect(self.accept)
        btn_no.clicked.connect(self.reject)


# ----------------- Dialog para seleccionar distribución y parámetros -----------------
class DistributionSelectorDialog(QDialog):
    """
    Devuelve un dict: {'tipo': 'continua'|'discreta', 'key': <metodo>, 'params': {...}}
    Los keys coinciden con los nombres usados en las clases de distribuciones.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Seleccionar distribución")
        self.result = None
        self.setMinimumWidth(420)
        self._build_ui()

    def _build_ui(self):
        main = QVBoxLayout(self)

        # Tipo
        tipo_row = QHBoxLayout()
        tipo_row.addWidget(QLabel("Tipo:"))
        self.combo_tipo = QComboBox()
        self.combo_tipo.addItems(["Continua", "Discreta"])
        tipo_row.addStretch()
        tipo_row.addWidget(self.combo_tipo)
        main.addLayout(tipo_row)

        # Distribución
        dist_row = QHBoxLayout()
        dist_row.addWidget(QLabel("Distribución:"))
        self.combo_dist = QComboBox()
        dist_row.addWidget(self.combo_dist)
        dist_row.addStretch()
        main.addLayout(dist_row)

        # Área de parámetros (usaremos QFormLayout para claridad)
        self.params_group = QGroupBox("Parámetros")
        self.params_layout = QFormLayout(self.params_group)
        main.addWidget(self.params_group)

        # Botones
        btn_row = QHBoxLayout()
        self.btn_apply = ModernButton("Aplicar", color="#6c5ce7")
        self.btn_cancel = ModernButton("Cancelar", color="#aaaaaa")
        btn_row.addStretch()
        btn_row.addWidget(self.btn_apply)
        btn_row.addWidget(self.btn_cancel)
        main.addLayout(btn_row)

        # Conexiones
        self.combo_tipo.currentIndexChanged.connect(self._refresh_distributions)
        self.combo_dist.currentIndexChanged.connect(self._render_params)
        self.btn_apply.clicked.connect(self._on_apply)
        self.btn_cancel.clicked.connect(self.reject)

        # Inicializar
        self._refresh_distributions()

    def _clear_params(self):
        while self.params_layout.count():
            item = self.params_layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.setParent(None)

    def _add_param(self, name, default=""):
        le = ModernLineEdit(str(default))
        self.params_layout.addRow(QLabel(name), le)
        return le

    def _refresh_distributions(self):
        t = self.combo_tipo.currentText().lower()
        self.combo_dist.clear()
        if t == "continua":
            self.combo_dist.addItem("Uniforme (a,b)", "uniforme")
            self.combo_dist.addItem("Normal (μ,σ)", "normal")
            self.combo_dist.addItem("Exponencial (λ)", "exponencial")
            self.combo_dist.addItem("Weibull (α,β,γ)", "weibull")
            self.combo_dist.addItem("Gamma (α,β)", "gamma")
        else:
            self.combo_dist.addItem("Uniforme Discreta (a,b)", "uniforme_discreta")
            self.combo_dist.addItem("Bernoulli (p)", "bernoulli")
            self.combo_dist.addItem("Binomial (n,p)", "binomial")
            self.combo_dist.addItem("Poisson (λ)", "poisson")
        self._render_params()

    def _render_params(self):
        self._clear_params()
        key = self.combo_dist.currentData()

        if key == "uniforme":
            self.le_a = self._add_param("a:", "0")
            self.le_b = self._add_param("b:", "1")
        elif key == "normal":
            self.le_mu = self._add_param("μ:", "0")
            self.le_sigma = self._add_param("σ:", "1")
        elif key == "exponencial":
            self.le_lambda = self._add_param("λ:", "1")
        elif key == "weibull":
            self.le_alpha = self._add_param("α (alpha):", "1")
            self.le_beta = self._add_param("β (beta):", "1")
            self.le_y = self._add_param("γ (offset y) (opcional):", "0")
        elif key == "gamma":
            self.le_alpha = self._add_param("α (alpha):", "1")
            self.le_beta = self._add_param("β (beta):", "1")
        elif key == "uniforme_discreta":
            self.le_a = self._add_param("a:", "0")
            self.le_b = self._add_param("b:", "5")
        elif key == "bernoulli":
            self.le_p = self._add_param("p:", "0.5")
        elif key == "binomial":
            self.le_n = self._add_param("n (trials):", "10")
            self.le_p = self._add_param("p:", "0.5")
        elif key == "poisson":
            self.le_lambda = self._add_param("λ:", "3")

    def _on_apply(self):
        key = self.combo_dist.currentData()
        tipo = self.combo_tipo.currentText().lower()
        params = {}
        try:
            if key in ("uniforme", "uniforme_discreta"):
                a = float(self.le_a.text()); b = float(self.le_b.text())
                if b <= a:
                    raise ValueError("b debe ser mayor que a")
                params = {"a": a, "b": b}
            elif key == "normal":
                mu = float(self.le_mu.text()); sigma = float(self.le_sigma.text())
                if sigma <= 0:
                    raise ValueError("σ debe ser > 0")
                params = {"mu": mu, "sigma": sigma}
            elif key == "exponencial":
                lam = float(self.le_lambda.text())
                if lam <= 0:
                    raise ValueError("λ debe ser > 0")
                params = {"lambda": lam}
            elif key == "weibull":
                alpha = float(self.le_alpha.text()); beta = float(self.le_beta.text())
                y = float(self.le_y.text()) if hasattr(self, "le_y") else 0.0
                params = {"alpha": alpha, "beta": beta, "y": y}
            elif key == "gamma":
                alpha = float(self.le_alpha.text()); beta = float(self.le_beta.text())
                params = {"alpha": alpha, "beta": beta}
            elif key == "bernoulli":
                p = float(self.le_p.text())
                if not (0 <= p <= 1):
                    raise ValueError("p debe estar en [0,1]")
                params = {"p": p}
            elif key == "binomial":
                n = int(float(self.le_n.text())); p = float(self.le_p.text())
                if not (0 <= p <= 1):
                    raise ValueError("p debe estar en [0,1]")
                params = {"n": n, "p": p}
            elif key == "poisson":
                lam = float(self.le_lambda.text())
                if lam <= 0:
                    raise ValueError("λ debe ser > 0")
                params = {"lambda": lam}
            else:
                params = {}
        except Exception as e:
            QMessageBox.critical(self, "Error parámetros", str(e))
            return

        self.result = {"tipo": tipo, "key": key, "params": params}
        self.accept()

    def get_result(self):
        return self.result


# ----------------- Ventana resultado (Tabla + Histograma Yi) -----------------
class DistributionResultWindow(QDialog):
    def __init__(self, ri_list, yi_list, parent=None, titulo="Distribución", dist_key=None, dist_params=None):
        super().__init__(parent)
        self.setWindowTitle(f"Resultados - {titulo}")
        self.ri_list = list(ri_list)
        self.yi_list = list(yi_list)
        # Guardar key y params para adaptar gráfico
        self.dist_key = dist_key
        self.dist_params = dist_params or {}
        self._build_ui()
        self._populate_table()
        self._draw_histogram()
        self.resize(820, 620)

    def _build_ui(self):
        layout = QVBoxLayout(self)

        self.table = QTableWidget()
        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels(["Iteración", "Ri", "Yi"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        layout.addWidget(self.table)

        self.fig = Figure(figsize=(6, 3))
        self.canvas = FigureCanvas(self.fig)
        layout.addWidget(self.canvas)

        btns = QHBoxLayout()
        self.btn_export = ModernButton("Exportar CSV", color="#fdcb6e")
        self.btn_close = ModernButton("Cerrar", color="#aaaaaa")
        btns.addStretch()
        btns.addWidget(self.btn_export)
        btns.addWidget(self.btn_close)
        layout.addLayout(btns)

        self.btn_export.clicked.connect(self._export_csv)
        self.btn_close.clicked.connect(self.close)

    def _populate_table(self):
        n = len(self.ri_list)
        self.table.setRowCount(n)
        for i in range(n):
            it = QTableWidgetItem(str(i + 1))
            ri_item = QTableWidgetItem(f"{self.ri_list[i]:.6f}")
            yi_item = QTableWidgetItem(str(self.yi_list[i]))
            self.table.setItem(i, 0, it)
            self.table.setItem(i, 1, ri_item)
            self.table.setItem(i, 2, yi_item)

    def _kde(self, data, xs):
        """
        Estimación KDE simple con kernel Gaussiano y regla de Silverman para el ancho de banda.
        Data: 1D array, xs: puntos donde evaluar.
        """
        data = np.asarray(data)
        n = len(data)
        if n < 2:
            return np.zeros_like(xs)
        sigma = np.std(data, ddof=1)
        if sigma == 0 or np.isnan(sigma):
            sigma = 1.0
        # ancho Silverman
        bw = 1.06 * sigma * n ** (-1/5)
        if bw <= 0:
            bw = 0.1
        const = 1 / (n * bw * np.sqrt(2 * np.pi))
        diffs = (xs[:, None] - data[None, :]) / bw
        vals = const * np.exp(-0.5 * diffs**2)
        return vals.sum(axis=1)

# tab_generadores.py - versión final funcional con selección de distribuciones
# --- Se inicia reemplazo automático con _draw_histogram corregido ---

# Updated _draw_histogram implementation
    def _draw_histogram(self):
        """
        Dibuja el gráfico correctamente SEGÚN el tipo de distribución elegida explícitamente.
        Ajustado con bins óptimos y línea teórica opcional.
        """
        self.fig.clear()
        ax = self.fig.add_subplot(111)
        data_raw = np.array(self.yi_list)

        if data_raw.size == 0:
            ax.text(0.5, 0.5, "No hay datos para graficar", ha='center', va='center')
            self.canvas.draw()
            return

        key = (self.dist_key or "").lower()

        # Distribuciones DISCRETAS
        if key in ("poisson", "bernoulli", "binomial", "uniforme_discreta"):
            vals, counts = np.unique(np.round(data_raw).astype(int), return_counts=True)
            ax.bar(vals, counts, align='center', edgecolor='black', alpha=0.9)
            ax.set_title(f"Distribución discreta: {key}")
            ax.set_xlabel("Valor discreto")
            ax.set_ylabel("Frecuencia")
            ax.set_xticks(vals)

        # Distribución UNIFORME CONTINUA
        elif key == "uniforme":
            bins = max(30, int(len(data_raw) / 3))
            ax.hist(data_raw, bins=bins, density=True, edgecolor='white', alpha=0.8)
            # línea teórica
            a = self.dist_params.get("a"); b = self.dist_params.get("b")
            if a is not None and b is not None:
                ax.axhline(1 / (b - a), linestyle='--')
            ax.set_title("Distribución Uniforme Continua")
            ax.set_xlabel("Yi")
            ax.set_ylabel("Densidad")

        # Distribución NORMAL → histograma + KDE
        elif key == "normal":
            bins = max(30, int(len(data_raw) / 3))
            ax.hist(data_raw, bins=bins, density=True, edgecolor='white', alpha=0.8)
            xs = np.linspace(min(data_raw), max(data_raw), 300)
            kde_vals = self._kde(data_raw, xs)
            ax.plot(xs, kde_vals, linestyle='--', linewidth=1.5)
            ax.set_title("Distribución Normal (hist + KDE)")
            ax.set_xlabel("Yi")
            ax.set_ylabel("Densidad")

        # Exponencial / Gamma / Weibull → bins medios
        elif key in ("exponencial", "gamma", "weibull"):
            bins = max(25, int(len(data_raw) / 2))
            ax.hist(data_raw, bins=bins, density=True, edgecolor='white', alpha=0.8)
            ax.set_title(f"Distribución {key}")
            ax.set_xlabel("Yi")
            ax.set_ylabel("Densidad")

        else:
            ax.hist(data_raw, bins=20, edgecolor='white', alpha=0.8)
            ax.set_title("Histograma genérico")
            ax.set_xlabel("Yi")
            ax.set_ylabel("Frecuencia")

        ax.grid(alpha=0.3)
        self.canvas.draw()

# --- Fin del reemplazo de _draw_histogram ---
    def _export_csv(self):
        path, _ = QFileDialog.getSaveFileName(self, "Guardar CSV", "distribucion.csv", "CSV Files (*.csv)")
        if not path:
            return
        try:
            with open(path, mode="w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow(["Iteracion", "Ri", "Yi"])
                for i, (r, y) in enumerate(zip(self.ri_list, self.yi_list), start=1):
                    writer.writerow([i, f"{r:.8f}", y])
            QMessageBox.information(self, "Éxito", f"CSV guardado en: {path}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudo guardar CSV: {e}")


# ----------------- Tab principal -----------------
class TabGeneradores(QWidget):
    def __init__(self):
        super().__init__()
        self.setup_styles()
        self.init_ui()
    def obtener_ri_actual(self):
        return self.ri_list_cm

    def setup_styles(self):
        self.setStyleSheet("""
            QWidget {
                background-color: #f6f7fb;
                color: #222;
                font-family: 'Segoe UI', Arial, sans-serif;
            }
            QGroupBox { font-weight: bold; border: 1px solid #e6e6e6; border-radius: 8px; padding: 8px; background: white; }
        """)

    def init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(12, 12, 12, 12)
        main_layout.setSpacing(12)

        title = QLabel("Generadores de Números Pseudoaleatorios")
        title_font = QFont(); title_font.setPointSize(16); title_font.setBold(True)
        title.setFont(title_font)
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("color: #6c5ce7; padding: 6px;")
        main_layout.addWidget(title)

        selector_row = QHBoxLayout()
        selector_row.addWidget(QLabel("Seleccione el generador:"))
        self.combo_generador = QComboBox()
        self.combo_generador.addItems(["Cuadrados Medios", "Productos Medios", "Multiplicador Constante"])
        selector_row.addWidget(self.combo_generador)
        selector_row.addStretch()
        main_layout.addLayout(selector_row)

        self.stacked = QStackedWidget()
        main_layout.addWidget(self.stacked)

        self.pagina_cm = self.crear_pagina_cm()
        self.pagina_pm = self.crear_pagina_pm()
        self.pagina_mc = self.crear_pagina_mc()
        self.stacked.addWidget(self.pagina_cm)
        self.stacked.addWidget(self.pagina_pm)
        self.stacked.addWidget(self.pagina_mc)

        # listas Ri
        self.ri_list_cm = []
        self.ri_list_pm = []
        self.ri_list_mc = []

        # ventanas abiertas para mantener referencia
        self._open_windows = []

        # conexiones
        self.combo_generador.currentIndexChanged.connect(self.cambiar_generador)

    def cambiar_generador(self, idx):
        self.stacked.setCurrentIndex(idx)

    def crear_group_inputs(self, inputs):
        group = QGroupBox("Parámetros de entrada")
        layout = QVBoxLayout(group)
        for label_text, widget in inputs:
            row = QHBoxLayout()
            lbl = QLabel(label_text)
            lbl.setMinimumWidth(120)
            lbl.setStyleSheet("font-weight: bold;")
            row.addWidget(lbl)
            row.addWidget(widget)
            layout.addLayout(row)
        return group

    def crear_group_buttons(self, buttons):
        frame = QFrame()
        layout = QHBoxLayout(frame)
        layout.setSpacing(8)
        for b in buttons:
            layout.addWidget(b)
        layout.addStretch()
        return frame

    # ---------------- Página: Cuadrados Medios ----------------
    def crear_pagina_cm(self):
        pagina = QWidget(); layout = QVBoxLayout(pagina); layout.setSpacing(10)
        self.semilla_input_cm = ModernLineEdit("Semilla X0 (entero)")
        self.cantidad_input_cm = ModernLineEdit("Cantidad n (entero)")
        group = self.crear_group_inputs([("Semilla X0:", self.semilla_input_cm), ("Cantidad n:", self.cantidad_input_cm)])
        layout.addWidget(group)

        self.btn_generar_cm = ModernButton("Generar Números", color="#00b894")
        self.btn_limpiar_cm = ModernButton("Limpiar", color="#fd79a8")
        self.btn_hist_cm = ModernButton("Ver Histograma", color="#6c5ce7")
        self.btn_exportar_cm = ModernButton("Exportar CSV", color="#fdcb6e")
        layout.addWidget(self.crear_group_buttons([self.btn_generar_cm, self.btn_limpiar_cm, self.btn_hist_cm, self.btn_exportar_cm]))

        self.tabla_cm = QTableWidget()
        self.tabla_cm.setColumnCount(5)
        self.tabla_cm.setHorizontalHeaderLabels(["Iteración", "Xi-1", "Xi^2", "Xi", "Ri"])
        self.tabla_cm.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        layout.addWidget(self.tabla_cm)

        # conexiones
        self.btn_generar_cm.clicked.connect(self.generar_cm)
        self.btn_limpiar_cm.clicked.connect(self.limpiar_cm)
        self.btn_hist_cm.clicked.connect(lambda: self.ver_histograma_ventana(self.ri_list_cm, "Cuadrados Medios (Ri)"))
        self.btn_exportar_cm.clicked.connect(lambda: self.exportar_csv(self.tabla_cm, "CuadradosMedios"))

        return pagina

    def limpiar_cm(self):
        self.tabla_cm.setRowCount(0)
        self.semilla_input_cm.clear()
        self.cantidad_input_cm.clear()
        self.ri_list_cm = []

    def generar_cm(self):
        sem = self.semilla_input_cm.text().strip()
        n_text = self.cantidad_input_cm.text().strip()
        if not sem or not n_text:
            QMessageBox.warning(self, "Error", "Todos los campos son obligatorios")
            return
        if not (sem.isdigit() and n_text.isdigit()):
            QMessageBox.warning(self, "Error", "Semilla y cantidad deben ser enteros")
            return
        semilla = int(sem); n = int(n_text)
        if semilla <= 0 or n <= 0:
            QMessageBox.warning(self, "Error", "Valores deben ser positivos")
            return

        generador = CuadradosMedios(semilla, n)
        resultados = generador.generar_tabla()
        self.ri_list_cm = [r["Ri"] for r in resultados]

        self.tabla_cm.setRowCount(len(resultados))
        for i, r in enumerate(resultados):
            self.tabla_cm.setItem(i, 0, QTableWidgetItem(str(r["Iteración"])))
            self.tabla_cm.setItem(i, 1, QTableWidgetItem(r["Xi-1"]))
            self.tabla_cm.setItem(i, 2, QTableWidgetItem(r["Xi^2"]))
            self.tabla_cm.setItem(i, 3, QTableWidgetItem(r["Xi"]))
            self.tabla_cm.setItem(i, 4, QTableWidgetItem(f"{r['Ri']:.6f}"))

        # preguntar si aplicar distribución
        self._post_generation_prompt(self.ri_list_cm)

    # ---------------- Página: Productos Medios ----------------
    def crear_pagina_pm(self):
        pagina = QWidget(); layout = QVBoxLayout(pagina); layout.setSpacing(10)
        self.semilla1_input_pm = ModernLineEdit("Semilla X0 (entero)")
        self.semilla2_input_pm = ModernLineEdit("Semilla X1 (entero)")
        self.cantidad_input_pm = ModernLineEdit("Cantidad n (entero)")
        group = self.crear_group_inputs([
            ("Semilla X0:", self.semilla1_input_pm),
            ("Semilla X1:", self.semilla2_input_pm),
            ("Cantidad n:", self.cantidad_input_pm)
        ])
        layout.addWidget(group)

        self.btn_generar_pm = ModernButton("Generar Números", color="#00b894")
        self.btn_limpiar_pm = ModernButton("Limpiar", color="#fd79a8")
        self.btn_hist_pm = ModernButton("Ver Histograma", color="#6c5ce7")
        self.btn_exportar_pm = ModernButton("Exportar CSV", color="#fdcb6e")
        layout.addWidget(self.crear_group_buttons([self.btn_generar_pm, self.btn_limpiar_pm, self.btn_hist_pm, self.btn_exportar_pm]))

        self.tabla_pm = QTableWidget()
        self.tabla_pm.setColumnCount(6)
        self.tabla_pm.setHorizontalHeaderLabels(["Iteración", "X", "Y", "Producto", "Dígitos del centro", "Ri"])
        self.tabla_pm.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        layout.addWidget(self.tabla_pm)

        self.btn_generar_pm.clicked.connect(self.generar_pm)
        self.btn_limpiar_pm.clicked.connect(self.limpiar_pm)
        self.btn_hist_pm.clicked.connect(lambda: self.ver_histograma_ventana(self.ri_list_pm, "Productos Medios (Ri)"))
        self.btn_exportar_pm.clicked.connect(lambda: self.exportar_csv(self.tabla_pm, "ProductosMedios"))

        return pagina

    def limpiar_pm(self):
        self.tabla_pm.setRowCount(0)
        self.semilla1_input_pm.clear()
        self.semilla2_input_pm.clear()
        self.cantidad_input_pm.clear()
        self.ri_list_pm = []

    def generar_pm(self):
        s1 = self.semilla1_input_pm.text().strip()
        s2 = self.semilla2_input_pm.text().strip()
        n_text = self.cantidad_input_pm.text().strip()
        if not s1 or not s2 or not n_text:
            QMessageBox.warning(self, "Error", "Todos los campos son obligatorios")
            return
        if not (s1.isdigit() and s2.isdigit() and n_text.isdigit()):
            QMessageBox.warning(self, "Error", "Semillas y cantidad deben ser enteros")
            return
        generator = ProductosMedios(int(s1), int(s2), int(n_text))
        resultados = generator.generar_tabla()
        self.ri_list_pm = [r["Ri"] for r in resultados]

        self.tabla_pm.setRowCount(len(resultados))
        for i, r in enumerate(resultados):
            self.tabla_pm.setItem(i, 0, QTableWidgetItem(str(r["Iteración"])))
            self.tabla_pm.setItem(i, 1, QTableWidgetItem(r["X"]))
            self.tabla_pm.setItem(i, 2, QTableWidgetItem(r["Y"]))
            self.tabla_pm.setItem(i, 3, QTableWidgetItem(r["Producto"]))
            self.tabla_pm.setItem(i, 4, QTableWidgetItem(r["Dígitos del centro"]))
            self.tabla_pm.setItem(i, 5, QTableWidgetItem(f"{r['Ri']:.6f}"))

        self._post_generation_prompt(self.ri_list_pm)

    # ---------------- Página: Multiplicador Constante ----------------
    def crear_pagina_mc(self):
        pagina = QWidget(); layout = QVBoxLayout(pagina); layout.setSpacing(10)
        self.semilla_input_mc = ModernLineEdit("Semilla X0 (entero)")
        self.constante_input_mc = ModernLineEdit("Constante k (entero)")
        self.cantidad_input_mc = ModernLineEdit("Cantidad n (entero)")
        group = self.crear_group_inputs([
            ("Semilla X0:", self.semilla_input_mc),
            ("Constante k:", self.constante_input_mc),
            ("Cantidad n:", self.cantidad_input_mc)
        ])
        layout.addWidget(group)

        self.btn_generar_mc = ModernButton("Generar Números", color="#303131")
        self.btn_limpiar_mc = ModernButton("Limpiar", color="#110558")
        self.btn_hist_mc = ModernButton("Ver Histograma", color="#083030")
        self.btn_exportar_mc = ModernButton("Exportar CSV", color="#434744")
        layout.addWidget(self.crear_group_buttons([self.btn_generar_mc, self.btn_limpiar_mc, self.btn_hist_mc, self.btn_exportar_mc]))

        self.tabla_mc = QTableWidget()
        self.tabla_mc.setColumnCount(5)
        self.tabla_mc.setHorizontalHeaderLabels(["Iteración", "Xi", "k*Xi", "Dígitos del centro", "Ri"])
        self.tabla_mc.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        layout.addWidget(self.tabla_mc)

        self.btn_generar_mc.clicked.connect(self.generar_mc)
        self.btn_limpiar_mc.clicked.connect(self.limpiar_mc)
        self.btn_hist_mc.clicked.connect(lambda: self.ver_histograma_ventana(self.ri_list_mc, "Multiplicador Constante (Ri)"))
        self.btn_exportar_mc.clicked.connect(lambda: self.exportar_csv(self.tabla_mc, "MultiplicadorConstante"))

        return pagina

    def limpiar_mc(self):
        self.tabla_mc.setRowCount(0)
        self.semilla_input_mc.clear()
        self.constante_input_mc.clear()
        self.cantidad_input_mc.clear()
        self.ri_list_mc = []

    def generar_mc(self):
        sem = self.semilla_input_mc.text().strip()
        const = self.constante_input_mc.text().strip()
        n_text = self.cantidad_input_mc.text().strip()
        if not sem or not const or not n_text:
            QMessageBox.warning(self, "Error", "Todos los campos son obligatorios")
            return
        if not (sem.isdigit() and const.isdigit() and n_text.isdigit()):
            QMessageBox.warning(self, "Error", "Semilla, constante y cantidad deben ser enteros")
            return
        generator = MultiplicadorConstante(int(sem), int(const), int(n_text))
        resultados = generator.generar_tabla()
        self.ri_list_mc = [r["Ri"] for r in resultados]

        self.tabla_mc.setRowCount(len(resultados))
        for i, r in enumerate(resultados):
            k = int(const)
            xi = int(r["Xi"])
            mult_str = f"{xi} * {k} = {r['k*Xi']}"
            self.tabla_mc.setItem(i, 0, QTableWidgetItem(str(r["Iteración"])))
            self.tabla_mc.setItem(i, 1, QTableWidgetItem(str(r["Xi"])))
            self.tabla_mc.setItem(i, 2, QTableWidgetItem(mult_str))
            self.tabla_mc.setItem(i, 3, QTableWidgetItem(r["Dígitos del centro"]))
            self.tabla_mc.setItem(i, 4, QTableWidgetItem(f"{r['Ri']:.6f}"))

        self._post_generation_prompt(self.ri_list_mc)

    # ---------------- Histograma Ri (ventana) ----------------
    def ver_histograma_ventana(self, ri_list, titulo):
        if not ri_list:
            QMessageBox.warning(self, "Advertencia", "No hay datos para mostrar. Genere números primero.")
            return
        dialog = QDialog(self)
        dialog.setWindowTitle(f"Histograma de Ri - {titulo}")
        dialog.setMinimumSize(700, 500)
        l = QVBoxLayout(dialog)
        fig = Figure(figsize=(8, 5))
        canvas = FigureCanvas(fig)
        l.addWidget(canvas)
        ax = fig.add_subplot(111)
        ax.hist(ri_list, bins=10, edgecolor="white", alpha=0.8)
        ax.set_title(f"Distribución de números generados - {titulo}")
        ax.set_xlabel("Ri")
        ax.set_ylabel("Frecuencia")
        mean_val = sum(ri_list) / len(ri_list)
        ax.axvline(mean_val, color='red', linestyle='--', linewidth=1.5, label=f'Media: {mean_val:.4f}')
        ax.legend()
        ax.grid(alpha=0.3)
        canvas.draw()
        dialog.exec()

    # ---------------- Post generation: preguntar y aplicar distribución ----------------
    def _post_generation_prompt(self, ri_list):
        dialog = ApplyDistributionDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            sel = DistributionSelectorDialog(self)
            if sel.exec() == QDialog.DialogCode.Accepted:
                cfg = sel.get_result()
                yi = self._apply_distribution_using_classes(ri_list, cfg)
                # Pasar key y params para que la ventana conozca la distribución
                win = DistributionResultWindow(ri_list, yi, parent=self, titulo=cfg['key'], dist_key=cfg['key'], dist_params=cfg['params'])
                self._open_windows.append(win)
                win.show()

    # ---------------- Adaptador para usar DistribucionesContinuas y Discretas --------------
    def _apply_distribution_using_classes(self, ri_list, cfg):
        """
        Construye un wrapper que expone generar(n) y devuelve DataFrame {'Ri': ...}
        para que las clases dadas funcionen sin modificar.
        """
        class _WrapperGenerador:
            def __init__(self, ris):
                self.ris = list(ris)
            def generar(self, n):
                # Devuelve exactamente n Ri (si no hay suficientes, completa con randoms)
                if n > len(self.ris):
                    extra = [random.random() for _ in range(n - len(self.ris))]
                    arr = self.ris + extra
                else:
                    arr = self.ris[:n]
                return pd.DataFrame({'Ri': arr})

        wrapper = _WrapperGenerador(ri_list)
        dc = DistribucionesContinuas(wrapper)
        dd = DistribucionesDiscretas(wrapper)

        key = cfg['key']
        params = cfg['params']
        n = len(ri_list)

        # Llamadas a métodos según key (respetando nombres de parámetros)
        if key == "uniforme":
            res = dc.uniforme(params['a'], params['b'], n=n)
            yi = res['variables']
        elif key == "normal":
            res = dc.normal(params['mu'], params['sigma'], n=n)
            yi = res['variables']
        elif key == "exponencial":
            res = dc.exponencial(params['lambda'], n=n)
            yi = res['variables']
        elif key == "weibull":
            y = params.get('y', 0.0)
            res = dc.weibull(params['alpha'], params['beta'], y=y, n=n)
            yi = res['variables']
        elif key == "gamma":
            res = dc.gamma(params['alpha'], params['beta'], n=n)
            yi = res['variables']
        elif key == "uniforme_discreta":
            res = dd.uniforme_discreta(int(params['a']), int(params['b']), n=n)
            yi = res['variables']
        elif key == "bernoulli":
            res = dd.bernoulli(params['p'], n=n)
            yi = res['variables']
        elif key == "binomial":
            res = dd.binomial(params['n'], params['p'], n=n)
            yi = res['variables']
        elif key == "poisson":
            res = dd.poisson(params['lambda'], n=n)
            yi = res['variables']
        else:
            yi = list(ri_list)

        return yi

    # ---------------- Exportar CSV (tabla de generador) ----------------
    def exportar_csv(self, tabla, generador_nombre):
        if tabla.rowCount() == 0:
            QMessageBox.warning(self, "Advertencia", "No hay datos para exportar. Genere números primero.")
            return
        path, _ = QFileDialog.getSaveFileName(self, "Guardar CSV", f"{generador_nombre}.csv", "CSV Files (*.csv)")
        if not path:
            return
        try:
            with open(path, mode="w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f, delimiter=';')
                headers = [tabla.horizontalHeaderItem(i).text() for i in range(tabla.columnCount())]
                writer.writerow(headers)
                for row in range(tabla.rowCount()):
                    row_data = [tabla.item(row, col).text() if tabla.item(row, col) else "" for col in range(tabla.columnCount())]
                    writer.writerow(row_data)
            QMessageBox.information(self, "Éxito", f"Datos exportados correctamente a {path}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudo exportar el archivo: {str(e)}")


# ----------------- Ejecutable de prueba -----------------
if __name__ == "__main__":
    from PyQt6.QtWidgets import QApplication
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    window = TabGeneradores()
    window.setWindowTitle("Generadores de Números Pseudoaleatorios")
    window.resize(1000, 720)
    window.show()
    sys.exit(app.exec())
