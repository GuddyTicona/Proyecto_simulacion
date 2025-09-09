from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QTableWidget, QTableWidgetItem,
    QLabel, QHeaderView, QFrame, QGroupBox, QPushButton, QHBoxLayout, QComboBox
)
from PyQt6.QtGui import QFont, QColor
from PyQt6.QtCore import Qt, QTimer
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import matplotlib.pyplot as plt
import numpy as np

class TabVariables(QWidget):
    def __init__(self):
        super().__init__()
        self.resultados = []  # Lista de resultados
        self.mensaje_oculto = "🎉 ¡Mensaje secreto revelado! 🎉"
        self.setup_styles()
        self.init_ui()

    def setup_styles(self):
        self.setStyleSheet("""
            QWidget { background-color: #f8f9fa; color: #333; font-family: 'Segoe UI', Arial, sans-serif; }
            QGroupBox { font-weight: bold; border: 2px solid #e0e0e0; border-radius: 8px; margin-top: 10px; padding-top: 15px; background-color: white; }
            QGroupBox::title { subcontrol-origin: margin; left: 10px; padding: 0 5px; color: #6c5ce7; font-weight: bold; }
            QTableWidget { background-color: white; border: 1px solid #e0e0e0; border-radius: 8px; gridline-color: #eee; alternate-background-color: #f8f9fa; }
            QTableWidget::item { padding: 8px; border-bottom: 1px solid #eee; }
            QTableWidget::item:selected { background-color: #e3f2fd; color: #333; }
            QHeaderView::section { background-color: #6c5ce7; color: white; padding: 10px; border: none; font-weight: bold; font-size: 12px; }
        """)

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        # Título
        title = QLabel("Resultados de Pruebas Estadísticas")
        font = QFont()
        font.setPointSize(16)
        font.setBold(True)
        title.setFont(font)
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("color: #6c5ce7; margin-bottom: 10px;")
        layout.addWidget(title)

        # Tabla
        group_box = QGroupBox("Tabla de Resultados")
        group_layout = QVBoxLayout(group_box)
        self.tabla_resultados = QTableWidget()
        self.tabla_resultados.setColumnCount(5)
        self.tabla_resultados.setHorizontalHeaderLabels(
            ["Prueba", "Valor", "Límite Inferior", "Límite Superior", "Resultado"]
        )
        self.tabla_resultados.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.tabla_resultados.setAlternatingRowColors(True)
        self.tabla_resultados.verticalHeader().setVisible(False)
        group_layout.addWidget(self.tabla_resultados)
        layout.addWidget(group_box)

        # Separador
        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setFrameShadow(QFrame.Shadow.Sunken)
        separator.setStyleSheet("color: #e0e0e0; margin: 10px 0;")
        layout.addWidget(separator)

        # Controles de gráfico
        controls_layout = QHBoxLayout()
        self.combo_grafico = QComboBox()
        self.combo_grafico.addItems(["Media", "Varianza", "Uniformidad"])
        self.btn_graficar = QPushButton("Mostrar Gráfico")
        self.btn_graficar.clicked.connect(self.mostrar_grafico)
        controls_layout.addWidget(self.combo_grafico)
        controls_layout.addWidget(self.btn_graficar)
        layout.addLayout(controls_layout)

        # Gráfico
        self.fig, self.ax = plt.subplots(figsize=(6, 4))
        self.canvas = FigureCanvas(self.fig)
        layout.addWidget(self.canvas)

        # Mensaje oculto: solo se crea una vez
        self.hidden_text = self.ax.text(
            0.5, 0.5, self.mensaje_oculto,
            fontsize=16, color="red", alpha=0.0,
            ha="center", va="center", transform=self.ax.transAxes,
            fontweight="bold"
        )

        # Conectar clic para revelar mensaje
        self.canvas.mpl_connect("button_press_event", self.revelar_mensaje)

    def mostrar_resultados(self, resultados):
        self.resultados = resultados
        self.tabla_resultados.setRowCount(0)
        for res in resultados:
            row = self.tabla_resultados.rowCount()
            self.tabla_resultados.insertRow(row)
            self.tabla_resultados.setItem(row, 0, QTableWidgetItem(res.get("prueba", "")))
            self.tabla_resultados.setItem(row, 1, QTableWidgetItem(f"{res.get('valor', 0):.6f}"))
            li = res.get("limite_inferior")
            ls = res.get("limite_superior")
            self.tabla_resultados.setItem(row, 2, QTableWidgetItem(f"{li:.6f}" if li is not None else "N/A"))
            self.tabla_resultados.setItem(row, 3, QTableWidgetItem(f"{ls:.6f}" if ls is not None else "N/A"))
            acepta = res.get("acepta_hipotesis", False)
            result_item = QTableWidgetItem("✓ Aceptada" if acepta else "✗ Rechazada")
            result_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            result_item.setBackground(QColor("#d4edda") if acepta else QColor("#f8d7da"))
            result_item.setForeground(QColor("#155724") if acepta else QColor("#721c24"))
            self.tabla_resultados.setItem(row, 4, result_item)

    def mostrar_grafico(self):
        self.ax.clear()
        tipo = self.combo_grafico.currentText()
        valores = [r["valor"] for r in self.resultados if tipo.lower() in r["prueba"].lower()]
        if not valores:
            valores = [0]

        # Dibujar histograma
        self.ax.hist(valores, bins=10, color="#6c5ce7", alpha=0.7, edgecolor="white")

        if tipo == "Media":
            media = np.mean(valores)
            self.ax.axvline(media, color="red", linestyle="--", label=f"Media = {media:.4f}")
            self.ax.legend()
            self.ax.set_title("Prueba de Media")
        elif tipo == "Varianza":
            varianza = np.var(valores)
            self.ax.set_title(f"Prueba de Varianza (σ² = {varianza:.4f})")
        elif tipo == "Uniformidad":
            self.ax.set_title("Prueba de Uniformidad (Chi-Cuadrado)")

        # Mantener hidden_text sin recrearlo
        self.hidden_text.set_alpha(0.0)
        self.ax.add_artist(self.hidden_text)
        self.canvas.draw()

    def revelar_mensaje(self, event=None):
        if not hasattr(self, "hidden_text") or self.hidden_text is None:
            return

        self.alpha = 0.0
        self.increasing = True
        self.parpadeos = 0

        if hasattr(self, "_parpadeo_timer") and self._parpadeo_timer.isActive():
            self._parpadeo_timer.stop()

        self._parpadeo_timer = QTimer()
        self._parpadeo_timer.setInterval(50)

        def parpadeo():
            if self.increasing:
                self.alpha += 0.05
                if self.alpha >= 1.0:
                    self.alpha = 1.0
                    self.increasing = False
            else:
                self.alpha -= 0.05
                if self.alpha <= 0.0:
                    self.alpha = 0.0
                    self._parpadeo_timer.stop()
            self.hidden_text.set_alpha(self.alpha)
            self.canvas.draw()

        self._parpadeo_timer.timeout.connect(parpadeo)
        self._parpadeo_timer.start()
