from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QTextEdit,
    QTableWidget, QTableWidgetItem, QMessageBox, QGroupBox, QHeaderView,
    QFrame, QDialog, QSpinBox, QDoubleSpinBox
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont, QColor
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import matplotlib.pyplot as plt

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
                border-radius: 6px;
                font-weight: bold;
                font-size: 12px;
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
        self.setMinimumSize(700, 500)
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
        self.btn_calcular = QPushButton("Calcular Uniformidad")
        self.btn_calcular.clicked.connect(self.ejecutar_uniformidad)
        layout.addWidget(self.btn_calcular)

        # Tabla de frecuencias
        self.tabla_frecuencias = QTableWidget()
        self.tabla_frecuencias.setColumnCount(6)
        self.tabla_frecuencias.setHorizontalHeaderLabels(
            ["Intervalo", "FO", "FE", "FO-FE", "(FO-FE)²", "(FO-FE)²/FE"]
        )
        self.tabla_frecuencias.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        layout.addWidget(self.tabla_frecuencias)

        # Resultado final
        self.resultado_label = QLabel("")
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


# ---------------------- TAB PRUEBAS ---------------------- #
class TabPruebas(QWidget):
    resultados_generados = pyqtSignal(list)

    def __init__(self, generadores_tab):
        super().__init__()
        self.generadores_tab = generadores_tab
        self.resultados_medias = None
        self.resultados_varianza = None
        self.resultados_uniformidad = None
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)

        # Título
        title = QLabel("Pruebas Estadísticas")
        title.setFont(QFont("Segoe UI", 18, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("color: #6c5ce7; margin: 10px 0; padding: 10px;")
        layout.addWidget(title)

        # Entrada de datos
        input_group = QGroupBox("Datos de Números (Manual o Automático)")
        input_layout = QVBoxLayout(input_group)
        self.nums_text_edit = QTextEdit()
        self.nums_text_edit.setPlaceholderText("Ingrese números separados por coma o espacio")
        self.nums_text_edit.setFixedHeight(100)
        input_layout.addWidget(self.nums_text_edit)

        self.btn_usar_generador = ModernButton("Usar números del generador", color="#00b894", hover_color="#00a382", pressed_color="#008f74")
        self.btn_usar_generador.clicked.connect(self.llenar_desde_generador)
        input_layout.addWidget(self.btn_usar_generador)
        layout.addWidget(input_group)

        # Botones
        btn_layout = QHBoxLayout()
        self.btn_prueba_medias = ModernButton("Prueba de Medias", color="#6c5ce7")
        self.btn_prueba_varianza = ModernButton("Prueba de Varianza", color="#fd79a8")
        self.btn_uniformidad_directo = ModernButton("Uniformidad χ²", color="#fdcb6e", hover_color="#f0b45e", pressed_color="#e3a44e")
        self.btn_uniformidad_avanzada = ModernButton("Uniformidad χ² Avanzada", color="#fdcb6e", hover_color="#f0b45e", pressed_color="#e3a44e")
        self.btn_histograma = ModernButton("Ver Histograma", color="#00cec9", hover_color="#00a6a1", pressed_color="#008d89")
        self.btn_limpiar = ModernButton("Limpiar Todo", color="#d63031", hover_color="#c23636", pressed_color="#a52727")

        self.btn_prueba_medias.clicked.connect(self.ejecutar_medias)
        self.btn_prueba_varianza.clicked.connect(self.ejecutar_varianza)
        self.btn_uniformidad_directo.clicked.connect(self.ejecutar_uniformidad_directo)
        self.btn_uniformidad_avanzada.clicked.connect(self.mostrar_ventana_uniformidad)
        self.btn_histograma.clicked.connect(self.mostrar_histograma)
        self.btn_limpiar.clicked.connect(self.limpiar_todo)

        for btn in [self.btn_prueba_medias, self.btn_prueba_varianza, self.btn_uniformidad_directo,
                    self.btn_uniformidad_avanzada, self.btn_histograma, self.btn_limpiar]:
            btn_layout.addWidget(btn)
        layout.addLayout(btn_layout)

        # Separador
        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setFrameShadow(QFrame.Shadow.Sunken)
        layout.addWidget(separator)

        # Tabla de resultados
        self.tabla_resultados = QTableWidget()
        self.tabla_resultados.setColumnCount(5)
        self.tabla_resultados.setHorizontalHeaderLabels(["Prueba", "Valor", "Límite Inferior", "Límite Superior", "Resultado"])
        self.tabla_resultados.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.tabla_resultados.setAlternatingRowColors(True)
        self.tabla_resultados.verticalHeader().setVisible(False)
        layout.addWidget(self.tabla_resultados)

    # ---------------- FUNCIONES ---------------- #
    def obtener_numeros(self):
        texto_manual = self.nums_text_edit.toPlainText().strip()
        if texto_manual:
            try:
                return [float(x) for x in texto_manual.replace(',', ' ').split()]
            except ValueError:
                QMessageBox.warning(self, "Error", "Ingrese solo números válidos separados por coma o espacio.")
                return []
        return self.generadores_tab.obtener_ri_actual()

    def llenar_desde_generador(self):
        nums = self.generadores_tab.obtener_ri_actual()
        if not nums:
            QMessageBox.warning(self, "Advertencia", "No hay números generados. Genere números primero.")
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
        QMessageBox.information(self, "Limpiar", "Todos los campos y resultados han sido limpiados.")

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

    def mostrar_histograma(self):
        nums = self.obtener_numeros()
        if not nums:
            QMessageBox.warning(self, "Advertencia", "No hay números para mostrar.")
            return

        dialog = QDialog(self)
        dialog.setWindowTitle("Histograma de Distribución")
        dialog.setMinimumSize(700, 500)
        layout = QVBoxLayout(dialog)

        fig, ax = plt.subplots(figsize=(8,5))
        canvas = FigureCanvas(fig)
        layout.addWidget(canvas)

        ax.hist(nums, bins=10, color="#6c5ce7", edgecolor="white", alpha=0.8)
        ax.set_title("Distribución de Números Pseudoaleatorios", fontsize=14, fontweight='bold')
        ax.set_xlabel("Valor de Ri", fontweight='bold')
        ax.set_ylabel("Frecuencia", fontweight='bold')
        ax.grid(True, alpha=0.3)

        mean_val = sum(nums)/len(nums)
        ax.axvline(mean_val, color="#fd79a8", linestyle='--', linewidth=2, label=f'Media: {mean_val:.4f}')
        ax.legend()
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)

        stats_text = f"Números: {len(nums)}\nMedia: {mean_val:.6f}\nMín: {min(nums):.6f}\nMáx: {max(nums):.6f}"
        ax.text(0.02,0.98, stats_text, transform=ax.transAxes, verticalalignment='top', bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))

        canvas.draw()
        dialog.exec()
