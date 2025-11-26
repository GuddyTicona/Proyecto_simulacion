import sys
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QTabWidget, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QTextEdit, QTableWidget, QTableWidgetItem,
    QMessageBox, QGroupBox, QHeaderView, QFrame, QDialog, QSpinBox,
    QDoubleSpinBox, QComboBox
)
from PyQt6.QtCore import Qt, pyqtSignal, QTimer
from PyQt6.QtGui import QFont, QColor
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import matplotlib.pyplot as plt
import numpy as np

# Importa tus funciones de pruebas
from pruebas.media import prueba_medias
from pruebas.varianza import prueba_varianza
from pruebas.uniformidad import prueba_uniformidad

# ---------------------- BOTÓN MODERNO ---------------------- #
class ModernButton(QPushButton):
    def __init__(self, text, parent=None, color="#6c5ce7", hover_color="#5d4ac7", pressed_color="#4e3aa7"):
        super().__init__(text, parent)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setMinimumHeight(40)
        self.setStyleSheet(f"""
            QPushButton {{
                background-color: {color};
                color: white;
                border: none;
                padding: 10px 15px;
                border-radius: 8px;
                font-weight: bold;
                font-size: 13px;
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

# ---------------------- DIALOG UNIFORMIDAD ---------------------- #
class UniformidadDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Prueba de Uniformidad χ² Avanzada")
        self.setMinimumSize(750, 500)
        self.numeros = []
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)

        # Inputs α y k
        input_layout = QHBoxLayout()
        self.alpha_input = QDoubleSpinBox()
        self.alpha_input.setDecimals(2)
        self.alpha_input.setSingleStep(0.01)
        self.alpha_input.setRange(0.01, 0.1)
        self.alpha_input.setValue(0.05)
        input_layout.addWidget(QLabel("Nivel de significancia α:"))
        input_layout.addWidget(self.alpha_input)

        self.intervals_input = QSpinBox()
        self.intervals_input.setRange(2, 20)
        self.intervals_input.setValue(5)
        input_layout.addWidget(QLabel("Número de intervalos k:"))
        input_layout.addWidget(self.intervals_input)

        layout.addLayout(input_layout)

        # Botón calcular
        self.btn_calcular = ModernButton("Calcular Uniformidad", color="#424149", hover_color="#475353", pressed_color="#8aa7e5")
        self.btn_calcular.clicked.connect(self.ejecutar_uniformidad)
        layout.addWidget(self.btn_calcular)

        # Tabla de frecuencias
        self.tabla_frecuencias = QTableWidget()
        self.tabla_frecuencias.setColumnCount(6)
        self.tabla_frecuencias.setHorizontalHeaderLabels(
            ["Intervalo", "FO", "FE", "FO-FE", "(FO-FE)²", "(FO-FE)²/FE"]
        )
        self.tabla_frecuencias.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.tabla_frecuencias.setAlternatingRowColors(True)
        layout.addWidget(self.tabla_frecuencias)

        # Resultado final
        self.resultado_label = QLabel("")
        self.resultado_label.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
        layout.addWidget(self.resultado_label)

    def set_numeros(self, numeros):
        self.numeros = numeros

    def ejecutar_uniformidad(self):
        if not self.numeros:
            QMessageBox.warning(self, "Advertencia", "No hay números para analizar.")
            return

        alpha = self.alpha_input.value()
        k = self.intervals_input.value()

        resultados = prueba_uniformidad(self.numeros, alpha=alpha, k=k)
        tabla = resultados["tabla_frecuencias"]
        chi = resultados["chi_cuadrado"]
        chi_critico = resultados["chi_critico"]
        acepta = resultados["acepta_hipotesis"]

        # Llenar tabla
        self.tabla_frecuencias.setRowCount(len(tabla))
        for i, fila in enumerate(tabla):
            self.tabla_frecuencias.setItem(i, 0, QTableWidgetItem(f"{fila['intervalo']}"))
            self.tabla_frecuencias.setItem(i, 1, QTableWidgetItem(f"{fila['frecuencia_observada']}"))
            self.tabla_frecuencias.setItem(i, 2, QTableWidgetItem(f"{fila['frecuencia_esperada']:.6f}"))
            self.tabla_frecuencias.setItem(i, 3, QTableWidgetItem(f"{fila['diferencia']:.6f}"))
            self.tabla_frecuencias.setItem(i, 4, QTableWidgetItem(f"{fila['diferencia_cuadrada']:.6f}"))
            self.tabla_frecuencias.setItem(i, 5, QTableWidgetItem(f"{fila['termino_chi']:.6f}"))

        # Mostrar resultado final
        self.resultado_label.setText(
            f"χ² calculado: {chi:.6f} | χ² crítico: {chi_critico:.6f} | "
            f"{'Se acepta H₀' if acepta else 'Se rechaza H₀'}"
        )

# ---------------------- VENTANA DE GRÁFICO ---------------------- #
class GraficoDialog(QDialog):
    def __init__(self, valores, tipo, mensaje_oculto):
        super().__init__()
        self.setWindowTitle(f"Histograma - {tipo}")
        self.setMinimumSize(800, 500)
        self.valores = valores
        self.tipo = tipo
        self.mensaje_oculto = mensaje_oculto
        self.alpha_msg = 0.0
        self.increasing = True
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        self.fig, self.ax = plt.subplots(figsize=(7,4))
        self.canvas = FigureCanvas(self.fig)
        layout.addWidget(self.canvas)

        # Texto oculto
        self.hidden_text = self.ax.text(
            0.5, 0.5, self.mensaje_oculto,
            fontsize=16, color="red", alpha=0.0,
            ha="center", va="center", transform=self.ax.transAxes,
            fontweight="bold"
        )
        self.canvas.mpl_connect("button_press_event", self.revelar_mensaje)

        # Dibujar histograma
        self.ax.clear()
        self.ax.hist(self.valores, bins=10, color="#6c5ce7", alpha=0.7, edgecolor="white")
        if self.tipo == "Medias":
            self.ax.axvline(np.mean(self.valores), color="red", linestyle="--", label=f"Media = {np.mean(self.valores):.4f}")
            self.ax.legend()
            self.ax.set_title("Prueba de Media")
        elif self.tipo == "Varianza":
            self.ax.set_title(f"Prueba de Varianza (σ² = {np.var(self.valores):.4f})")
        elif self.tipo == "Uniformidad":
            self.ax.set_title("Prueba de Uniformidad (Chi-Cuadrado)")
        self.ax.add_artist(self.hidden_text)
        self.canvas.draw()

    def revelar_mensaje(self, event=None):
        self.alpha_msg = 0.0
        self.increasing = True
        if hasattr(self, "_parpadeo_timer") and self._parpadeo_timer.isActive():
            self._parpadeo_timer.stop()

        self._parpadeo_timer = QTimer()
        self._parpadeo_timer.setInterval(50)

        def parpadeo():
            if self.increasing:
                self.alpha_msg += 0.05
                if self.alpha_msg >= 1.0:
                    self.alpha_msg = 1.0
                    self.increasing = False
            else:
                self.alpha_msg -= 0.05
                if self.alpha_msg <= 0.0:
                    self.alpha_msg = 0.0
                    self._parpadeo_timer.stop()
            self.hidden_text.set_alpha(self.alpha_msg)
            self.canvas.draw()

        self._parpadeo_timer.timeout.connect(parpadeo)
        self._parpadeo_timer.start()

# ---------------------- TAB PRUEBAS ---------------------- #
class TabPruebas(QWidget):
    resultados_generados = pyqtSignal(list)

    def __init__(self, generadores_tab):
        super().__init__()
        self.generadores_tab = generadores_tab
        self.resultados_medias = None
        self.resultados_varianza = None
        self.resultados_uniformidad = None
        self.mensaje_oculto = "🎉 ¡MENSAJE REVELADO! 🎉"
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        # --- Título --- #
        title = QLabel("Pruebas Estadísticas")
        title.setFont(QFont("Segoe UI", 18, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("color: #6c5ce7; margin-bottom: 10px;")
        layout.addWidget(title)

        # --- Entrada de datos --- #
        input_group = QGroupBox("Datos de Números Pseudoaleatorios")
        input_layout = QVBoxLayout(input_group)
        self.nums_text_edit = QTextEdit()
        self.nums_text_edit.setPlaceholderText("Ingrese números separados por coma")
        self.nums_text_edit.setFixedHeight(100)
        input_layout.addWidget(self.nums_text_edit)

        self.btn_usar_generador = ModernButton("Generar números", color="#00b894", hover_color="#00a382", pressed_color="#008f74")
        self.btn_usar_generador.clicked.connect(self.llenar_desde_generador)
        input_layout.addWidget(self.btn_usar_generador)
        layout.addWidget(input_group)

        # --- Botones de pruebas --- #
        btn_layout = QHBoxLayout()
        self.btn_prueba_medias = ModernButton("Prueba de Medias", color="#35343a")
        self.btn_prueba_varianza = ModernButton("Prueba de Varianza", color="#5C4254")
        self.btn_uniformidad_directo = ModernButton("Uniformidad χ²", color="#85817e")
        self.btn_uniformidad_avanzada = ModernButton("Uniformidad χ² Avanzada", color="#3E405F")
        self.btn_histograma = ModernButton("Mostrar Gráfico", color="#00cec9")
        self.btn_limpiar = ModernButton("Limpiar Todo", color="#462727")

        self.btn_prueba_medias.clicked.connect(self.ejecutar_medias)
        self.btn_prueba_varianza.clicked.connect(self.ejecutar_varianza)
        self.btn_uniformidad_directo.clicked.connect(self.ejecutar_uniformidad_directo)
        self.btn_uniformidad_avanzada.clicked.connect(self.mostrar_ventana_uniformidad)
        self.btn_histograma.clicked.connect(self.mostrar_histograma_tab)
        self.btn_limpiar.clicked.connect(self.limpiar_todo)

        for btn in [self.btn_prueba_medias, self.btn_prueba_varianza, self.btn_uniformidad_directo,
                    self.btn_uniformidad_avanzada, self.btn_histograma, self.btn_limpiar]:
            btn_layout.addWidget(btn)
        layout.addLayout(btn_layout)

        # --- Separador --- #
        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setFrameShadow(QFrame.Shadow.Sunken)
        layout.addWidget(separator)

        # --- Tabla de resultados --- #
        self.tabla_resultados = QTableWidget()
        self.tabla_resultados.setColumnCount(5)
        self.tabla_resultados.setHorizontalHeaderLabels(["Prueba", "Valor", "Límite Inferior", "Límite Superior", "Resultado"])
        self.tabla_resultados.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.tabla_resultados.setAlternatingRowColors(True)
        self.tabla_resultados.verticalHeader().setVisible(False)
        layout.addWidget(self.tabla_resultados)

        # --- Combo de selección de prueba para gráfico --- #
        combo_layout = QHBoxLayout()
        self.combo_grafico = QComboBox()
        self.combo_grafico.addItems(["Medias", "Varianza", "Uniformidad"])
        combo_layout.addWidget(QLabel("Seleccionar prueba:"))
        combo_layout.addWidget(self.combo_grafico)
        layout.addLayout(combo_layout)

    # --- FUNCIONES AUXILIARES --- #
    def obtener_numeros(self):
        texto_manual = self.nums_text_edit.toPlainText().strip()
        if texto_manual:
            try:
                return [float(x) for x in texto_manual.replace(',', ' ').split()]
            except ValueError:
                QMessageBox.warning(self, "Error", "Ingrese solo números válidos.")
                return []
        return self.generadores_tab.obtener_ri_actual()

    def llenar_desde_generador(self):
        nums = self.generadores_tab.obtener_ri_actual()
        if not nums:
            QMessageBox.warning(self, "Advertencia", "No hay números generados.")
            return
        self.nums_text_edit.setText(', '.join(f"{n:.6f}" for n in nums))
        QMessageBox.information(self, "Éxito", f"Se han cargado {len(nums)} números del generador.")

    def limpiar_todo(self):
        self.nums_text_edit.clear()
        self.tabla_resultados.setRowCount(0)
        self.resultados_medias = None
        self.resultados_varianza = None
        self.resultados_uniformidad = None
        self.enviar_resultados()
        QMessageBox.information(self, "Limpiar", "Campos y resultados limpiados.")

    def actualizar_tabla(self, prueba, valor, limite_inf, limite_sup, acepta):
        row = self.tabla_resultados.rowCount()
        self.tabla_resultados.insertRow(row)
        self.tabla_resultados.setItem(row, 0, QTableWidgetItem(prueba))
        self.tabla_resultados.setItem(row, 1, QTableWidgetItem(f"{valor:.6f}"))
        self.tabla_resultados.setItem(row, 2, QTableWidgetItem(f"{limite_inf:.6f}" if limite_inf else "N/A"))
        self.tabla_resultados.setItem(row, 3, QTableWidgetItem(f"{limite_sup:.6f}" if limite_sup else "N/A"))
        item = QTableWidgetItem("✓ Aceptada" if acepta else "✗ Rechazada")
        item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
        item.setBackground(QColor("#d4edda") if acepta else QColor("#f8d7da"))
        item.setForeground(QColor("#155724") if acepta else QColor("#721c24"))
        self.tabla_resultados.setItem(row, 4, item)

    # --- FUNCIONES DE PRUEBAS --- #
    def ejecutar_medias(self):
        nums = self.obtener_numeros()
        if not nums: return
        self.resultados_medias = prueba_medias(nums)
        self.actualizar_tabla("Medias", self.resultados_medias["media"],
                               self.resultados_medias["limite_inferior"],
                               self.resultados_medias["limite_superior"],
                               self.resultados_medias["acepta_hipotesis"])
        self.enviar_resultados()

    def ejecutar_varianza(self):
        nums = self.obtener_numeros()
        if not nums: return
        self.resultados_varianza = prueba_varianza(nums)
        self.actualizar_tabla("Varianza", self.resultados_varianza["varianza"],
                               self.resultados_varianza["limite_inferior"],
                               self.resultados_varianza["limite_superior"],
                               self.resultados_varianza["acepta_hipotesis"])
        self.enviar_resultados()

    def ejecutar_uniformidad_directo(self):
        nums = self.obtener_numeros()
        if not nums: return
        self.resultados_uniformidad = prueba_uniformidad(nums)
        self.actualizar_tabla("Uniformidad χ²", self.resultados_uniformidad["chi_cuadrado"],
                               0, self.resultados_uniformidad["chi_critico"],
                               self.resultados_uniformidad["acepta_hipotesis"])
        self.enviar_resultados()

    def mostrar_ventana_uniformidad(self):
        nums = self.obtener_numeros()
        if not nums:
            QMessageBox.warning(self, "Advertencia", "No hay números para analizar.")
            return
        dialog = UniformidadDialog(self)
        dialog.set_numeros(nums)
        dialog.exec()

    def enviar_resultados(self):
        resultados_para_variables = []
        if self.resultados_medias:
            resultados_para_variables.append({
                "prueba": "Medias",
                "valor": self.resultados_medias["media"],
                "limite_inferior": self.resultados_medias["limite_inferior"],
                "limite_superior": self.resultados_medias["limite_superior"],
                "acepta_hipotesis": self.resultados_medias["acepta_hipotesis"]
            })
        if self.resultados_varianza:
            resultados_para_variables.append({
                "prueba": "Varianza",
                "valor": self.resultados_varianza["varianza"],
                "limite_inferior": self.resultados_varianza["limite_inferior"],
                "limite_superior": self.resultados_varianza["limite_superior"],
                "acepta_hipotesis": self.resultados_varianza["acepta_hipotesis"]
            })
        if self.resultados_uniformidad:
            resultados_para_variables.append({
                "prueba": "Uniformidad χ²",
                "valor": self.resultados_uniformidad["chi_cuadrado"],
                "limite_inferior": 0,
                "limite_superior": self.resultados_uniformidad["chi_critico"],
                "acepta_hipotesis": self.resultados_uniformidad["acepta_hipotesis"]
            })
        if resultados_para_variables:
            self.resultados_generados.emit(resultados_para_variables)

    # --- FUNCIONES DE GRÁFICO --- #
    def mostrar_histograma_tab(self):
        nums = self.obtener_numeros()
        if not nums:
            QMessageBox.warning(self, "Advertencia", "No hay números para mostrar.")
            return

        tipo = self.combo_grafico.currentText()
        valores = []
        if tipo == "Medias" and self.resultados_medias:
            valores = [self.resultados_medias["media"]]
        elif tipo == "Varianza" and self.resultados_varianza:
            valores = [self.resultados_varianza["varianza"]]
        elif tipo == "Uniformidad" and self.resultados_uniformidad:
            valores = [self.resultados_uniformidad["chi_cuadrado"]]
        else:
            valores = nums

        dialog = GraficoDialog(valores, tipo, self.mensaje_oculto)
        dialog.exec()
