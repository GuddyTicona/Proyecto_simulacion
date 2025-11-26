# tab_generadores.py
# Versión modificada del Tab "Generadores" SIN selector de distribuciones
# Solo mantiene la generación de números pseudoaleatorios
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


# ----------------- Ventana resultado (Tabla + Histograma Ri) -----------------
class HistogramResultWindow(QDialog):
    def __init__(self, ri_list, parent=None, titulo="Generador"):
        super().__init__(parent)
        self.setWindowTitle(f"Histograma - {titulo}")
        self.ri_list = list(ri_list)
        self._build_ui()
        self._populate_table()
        self._draw_histogram()
        self.resize(820, 620)

    def _build_ui(self):
        layout = QVBoxLayout(self)

        self.table = QTableWidget()
        self.table.setColumnCount(2)
        self.table.setHorizontalHeaderLabels(["Iteración", "Ri"])
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
            self.table.setItem(i, 0, it)
            self.table.setItem(i, 1, ri_item)

    def _draw_histogram(self):
        self.fig.clear()
        ax = self.fig.add_subplot(111)
        
        if not self.ri_list:
            ax.text(0.5, 0.5, "No hay datos para graficar", ha='center', va='center')
            self.canvas.draw()
            return

        # Histograma simple de los Ri
        ax.hist(self.ri_list, bins=min(20, len(self.ri_list)), density=True, 
                edgecolor='white', alpha=0.8, color='#4a90e2')
        
        # Calcular estadísticas
        mean_val = np.mean(self.ri_list)
        std_val = np.std(self.ri_list)
        
        # Línea de media
        ax.axvline(mean_val, color='red', linestyle='--', linewidth=1.5, 
                  label=f'Media: {mean_val:.4f}')
        
        ax.set_title("Distribución de Números Pseudoaleatorios (Ri)")
        ax.set_xlabel("Valor de Ri")
        ax.set_ylabel("Densidad")
        ax.legend()
        ax.grid(alpha=0.3)
        self.canvas.draw()

    def _export_csv(self):
        path, _ = QFileDialog.getSaveFileName(self, "Guardar CSV", "numeros_generados.csv", "CSV Files (*.csv)")
        if not path:
            return
        try:
            with open(path, mode="w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow(["Iteracion", "Ri"])
                for i, r in enumerate(self.ri_list, start=1):
                    writer.writerow([i, f"{r:.8f}"])
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
        self.btn_hist_cm.clicked.connect(lambda: self.ver_histograma_ventana(self.ri_list_cm, "Cuadrados Medios"))
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

        self.btn_generar_pm = ModernButton("Generar Números", color="#353b3a")
        self.btn_limpiar_pm = ModernButton("Limpiar", color="#1f3c68")
        self.btn_hist_pm = ModernButton("Ver Histograma", color="#6c5ce7")
        self.btn_exportar_pm = ModernButton("Exportar CSV", color="#063dd4")
        layout.addWidget(self.crear_group_buttons([self.btn_generar_pm, self.btn_limpiar_pm, self.btn_hist_pm, self.btn_exportar_pm]))

        self.tabla_pm = QTableWidget()
        self.tabla_pm.setColumnCount(6)
        self.tabla_pm.setHorizontalHeaderLabels(["Iteración", "X", "Y", "Producto", "Dígitos del centro", "Ri"])
        self.tabla_pm.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        layout.addWidget(self.tabla_pm)

        self.btn_generar_pm.clicked.connect(self.generar_pm)
        self.btn_limpiar_pm.clicked.connect(self.limpiar_pm)
        self.btn_hist_pm.clicked.connect(lambda: self.ver_histograma_ventana(self.ri_list_pm, "Productos Medios"))
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

        self.btn_generar_mc = ModernButton("Generar Números", color="#07033f")
        self.btn_limpiar_mc = ModernButton("Limpiar", color="#b1afb9")
        self.btn_hist_mc = ModernButton("Ver Histograma", color="#090430")
        self.btn_exportar_mc = ModernButton("Exportar CSV", color="#696661")
        layout.addWidget(self.crear_group_buttons([self.btn_generar_mc, self.btn_limpiar_mc, self.btn_hist_mc, self.btn_exportar_mc]))

        self.tabla_mc = QTableWidget()
        self.tabla_mc.setColumnCount(5)
        self.tabla_mc.setHorizontalHeaderLabels(["Iteración", "Xi", "k*Xi", "Dígitos del centro", "Ri"])
        self.tabla_mc.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        layout.addWidget(self.tabla_mc)

        self.btn_generar_mc.clicked.connect(self.generar_mc)
        self.btn_limpiar_mc.clicked.connect(self.limpiar_mc)
        self.btn_hist_mc.clicked.connect(lambda: self.ver_histograma_ventana(self.ri_list_mc, "Multiplicador Constante"))
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

    # ---------------- Histograma Ri (ventana mejorada) ----------------
    def ver_histograma_ventana(self, ri_list, titulo):
        if not ri_list:
            QMessageBox.warning(self, "Advertencia", "No hay datos para mostrar. Genere números primero.")
            return
        
        win = HistogramResultWindow(ri_list, parent=self, titulo=titulo)
        self._open_windows.append(win)
        win.show()

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