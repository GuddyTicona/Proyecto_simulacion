from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton,
    QTableWidget, QTableWidgetItem, QComboBox, QHeaderView, QStackedWidget,
    QDialog, QFileDialog, QMessageBox, QGroupBox, QFrame, QSizePolicy
)
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QFont, QIcon, QPixmap, QPalette, QColor
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import matplotlib.pyplot as plt
import csv
import sys
import os

# Importar los generadores (asegúrate de que estos módulos existan)
from generators.cuadrados_medios import CuadradosMedios
from generators.productos_medios import ProductosMedios
from generators.multiplicador_constante import MultiplicadorConstante


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
                padding: 10px 15px;
                border-radius: 4px;
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
        self.setMinimumHeight(35)
        self.setStyleSheet("""
            QLineEdit {
                padding: 8px;
                border: 1px solid #ddd;
                border-radius: 4px;
                background-color: white;
            }
            QLineEdit:focus {
                border: 2px solid #4a90e2;
            }
        """)


class TabGeneradores(QWidget):
    def __init__(self):
        super().__init__()
        self.setup_styles()
        self.init_ui()

    def setup_styles(self):
        # Estilos modernos para la aplicación con colores atractivos
        self.setStyleSheet("""
            QWidget {
                background-color: #f8f9fa;
                color: #333;
                font-family: 'Segoe UI', Arial, sans-serif;
            }
            QComboBox {
                padding: 8px;
                border: 1px solid #ddd;
                border-radius: 4px;
                background-color: white;
                selection-background-color: #6c5ce7;
            }
            QComboBox:focus {
                border: 2px solid #6c5ce7;
            }
            QComboBox QAbstractItemView {
                background-color: white;
                selection-background-color: #6c5ce7;
                selection-color: white;
            }
            QGroupBox {
                font-weight: bold;
                border: 1px solid #e0e0e0;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 15px;
                background-color: white;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
                color: #6c5ce7;
            }
            QLabel {
                color: #444;
                font-weight: 500;
            }
            QTableWidget {
                background-color: white;
                border: 1px solid #e0e0e0;
                border-radius: 8px;
                gridline-color: #eee;
                alternate-background-color: #f8f9fa;
            }
            QTableWidget::item {
                padding: 8px;
                border-bottom: 1px solid #eee;
            }
            QTableWidget::item:selected {
                background-color: #e3f2fd;
                color: #333;
            }
            QHeaderView::section {
                background-color: #6c5ce7;
                color: white;
                padding: 10px;
                border: none;
                font-weight: bold;
            }
        """)

    def init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(15)
        main_layout.setContentsMargins(20, 20, 20, 20)

        # Título principal
        title = QLabel("Generadores de Números Pseudoaleatorios")
        title_font = QFont()
        title_font.setPointSize(18)
        title_font.setBold(True)
        title.setFont(title_font)
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("color: #6c5ce7; margin: 10px 0; padding: 10px;")
        main_layout.addWidget(title)

        # Selector de generador
        selector_layout = QHBoxLayout()
        selector_label = QLabel("Seleccione el Generador:")
        selector_label.setStyleSheet("font-weight: bold; color: #444;")
        selector_layout.addWidget(selector_label)
        
        self.combo_generador = QComboBox()
        self.combo_generador.addItems(["Cuadrados Medios", "Productos Medios", "Multiplicador Constante"])
        self.combo_generador.currentIndexChanged.connect(self.cambiar_generador)
        selector_layout.addWidget(self.combo_generador)
        selector_layout.addStretch()
        
        main_layout.addLayout(selector_layout)

        # StackedWidget para las diferentes páginas
        self.stacked = QStackedWidget()
        main_layout.addWidget(self.stacked)

        # Crear páginas para cada generador
        self.pagina_cm = self.crear_pagina_cm()
        self.pagina_pm = self.crear_pagina_pm()
        self.pagina_mc = self.crear_pagina_mc()
        
        self.stacked.addWidget(self.pagina_cm)
        self.stacked.addWidget(self.pagina_pm)
        self.stacked.addWidget(self.pagina_mc)

        # Listas de Ri
        self.ri_list_cm = []
        self.ri_list_pm = []
        self.ri_list_mc = []

    def cambiar_generador(self, index):
        self.stacked.setCurrentIndex(index)

    def crear_group_inputs(self, inputs):
        group = QGroupBox("Parámetros de Entrada")
        layout = QVBoxLayout(group)
        
        for label_text, input_widget in inputs:
            h_layout = QHBoxLayout()
            label = QLabel(label_text)
            label.setMinimumWidth(120)
            label.setStyleSheet("font-weight: bold;")
            h_layout.addWidget(label)
            h_layout.addWidget(input_widget)
            layout.addLayout(h_layout)
            
        return group

    def crear_group_buttons(self, buttons):
        group = QFrame()
        layout = QHBoxLayout(group)
        layout.setSpacing(10)
        
        for button in buttons:
            layout.addWidget(button)
            
        layout.addStretch()
        return group

    # ---------- PÁGINA CUADRADOS MEDIOS ----------
    def crear_pagina_cm(self):
        pagina = QWidget()
        layout = QVBoxLayout(pagina)
        layout.setSpacing(15)

        # Inputs
        self.semilla_input_cm = ModernLineEdit("Semilla X0")
        self.cantidad_input_cm = ModernLineEdit("Cantidad n")
        
        input_group = self.crear_group_inputs([
            ("Semilla X0:", self.semilla_input_cm),
            ("Cantidad n:", self.cantidad_input_cm)
        ])
        layout.addWidget(input_group)

        # Botones
        self.btn_generar_cm = ModernButton("Generar Números", color="#00b894", hover_color="#00a382", pressed_color="#008f74")
        self.btn_limpiar_cm = ModernButton("Limpiar", color="#fd79a8", hover_color="#f24d8a", pressed_color="#e6337c")
        self.btn_hist_cm = ModernButton("Ver Histograma", color="#6c5ce7", hover_color="#5d4ac7", pressed_color="#4e3aa7")
        self.btn_exportar_cm = ModernButton("Exportar CSV", color="#fdcb6e", hover_color="#fdb43e", pressed_color="#fd9e0e")
        
        button_group = self.crear_group_buttons([
            self.btn_generar_cm, self.btn_limpiar_cm, 
            self.btn_hist_cm, self.btn_exportar_cm
        ])
        layout.addWidget(button_group)

        # Tabla
        self.tabla_cm = QTableWidget()
        self.tabla_cm.setColumnCount(5)
        self.tabla_cm.setHorizontalHeaderLabels(["Iteración", "Xi-1", "Xi^2", "Xi", "Ri"])
        self.tabla_cm.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.tabla_cm.setAlternatingRowColors(True)
        # Eliminar la numeración de filas
        self.tabla_cm.verticalHeader().setVisible(False)
        layout.addWidget(self.tabla_cm)

        # Conexiones
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
        semilla_text = self.semilla_input_cm.text().strip()
        n_text = self.cantidad_input_cm.text().strip()
        
        if not semilla_text or not n_text:
            QMessageBox.warning(self, "Error", "Todos los campos son obligatorios")
            return
            
        if not (semilla_text.isdigit() and n_text.isdigit()):
            QMessageBox.warning(self, "Error", "Semilla y cantidad deben ser números enteros")
            return

        semilla = int(semilla_text)
        n = int(n_text)
        
        if semilla <= 0 or n <= 0:
            QMessageBox.warning(self, "Error", "Los valores deben ser positivos")
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

    # ---------- PÁGINA PRODUCTOS MEDIOS ----------
    def crear_pagina_pm(self):
        pagina = QWidget()
        layout = QVBoxLayout(pagina)
        layout.setSpacing(15)

        # Inputs
        self.semilla1_input_pm = ModernLineEdit("Semilla X0")
        self.semilla2_input_pm = ModernLineEdit("Semilla X1")
        self.cantidad_input_pm = ModernLineEdit("Cantidad n")
        
        input_group = self.crear_group_inputs([
            ("Semilla X0:", self.semilla1_input_pm),
            ("Semilla X1:", self.semilla2_input_pm),
            ("Cantidad n:", self.cantidad_input_pm)
        ])
        layout.addWidget(input_group)

        # Botones
        self.btn_generar_pm = ModernButton("Generar Números", color="#00b894", hover_color="#00a382", pressed_color="#008f74")
        self.btn_limpiar_pm = ModernButton("Limpiar", color="#fd79a8", hover_color="#f24d8a", pressed_color="#e6337c")
        self.btn_hist_pm = ModernButton("Ver Histograma", color="#6c5ce7", hover_color="#5d4ac7", pressed_color="#4e3aa7")
        self.btn_exportar_pm = ModernButton("Exportar CSV", color="#fdcb6e", hover_color="#fdb43e", pressed_color="#fd9e0e")
        
        button_group = self.crear_group_buttons([
            self.btn_generar_pm, self.btn_limpiar_pm, 
            self.btn_hist_pm, self.btn_exportar_pm
        ])
        layout.addWidget(button_group)

        # Tabla
        self.tabla_pm = QTableWidget()
        self.tabla_pm.setColumnCount(6)
        self.tabla_pm.setHorizontalHeaderLabels(["Iteración", "X", "Y", "Producto", "Dígitos del centro", "Ri"])
        self.tabla_pm.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.tabla_pm.setAlternatingRowColors(True)
        # Eliminar la numeración de filas
        self.tabla_pm.verticalHeader().setVisible(False)
        layout.addWidget(self.tabla_pm)

        # Conexiones
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
        sem1 = self.semilla1_input_pm.text().strip()
        sem2 = self.semilla2_input_pm.text().strip()
        n_text = self.cantidad_input_pm.text().strip()
        
        if not sem1 or not sem2 or not n_text:
            QMessageBox.warning(self, "Error", "Todos los campos son obligatorios")
            return
            
        if not (sem1.isdigit() and sem2.isdigit() and n_text.isdigit()):
            QMessageBox.warning(self, "Error", "Semillas y cantidad deben ser números enteros")
            return

        generator = ProductosMedios(int(sem1), int(sem2), int(n_text))
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

    # ---------- PÁGINA MULTIPLICADOR CONSTANTE ----------
    def crear_pagina_mc(self):
        pagina = QWidget()
        layout = QVBoxLayout(pagina)
        layout.setSpacing(15)

        # Inputs
        self.semilla_input_mc = ModernLineEdit("Semilla X0")
        self.constante_input_mc = ModernLineEdit("Constante k")
        self.cantidad_input_mc = ModernLineEdit("Cantidad n")
        
        input_group = self.crear_group_inputs([
            ("Semilla X0:", self.semilla_input_mc),
            ("Constante k:", self.constante_input_mc),
            ("Cantidad n:", self.cantidad_input_mc)
        ])
        layout.addWidget(input_group)

        # Botones
        self.btn_generar_mc = ModernButton("Generar Números", color="#303131", hover_color="#4d9788", pressed_color="#008f74")
        self.btn_limpiar_mc = ModernButton("Limpiar", color="#110558", hover_color="#0d6777", pressed_color="#e6337c")
        self.btn_hist_mc = ModernButton("Ver Histograma", color="#083030", hover_color="#DCD9EC", pressed_color="#4e3aa7")
        self.btn_exportar_mc = ModernButton("Exportar CSV", color="#434744", hover_color="#3a3732", pressed_color="#fd9e0e")
        
        button_group = self.crear_group_buttons([
            self.btn_generar_mc, self.btn_limpiar_mc, 
            self.btn_hist_mc, self.btn_exportar_mc
        ])
        layout.addWidget(button_group)

        # Tabla
        self.tabla_mc = QTableWidget()
        self.tabla_mc.setColumnCount(5)
        self.tabla_mc.setHorizontalHeaderLabels(["Iteración", "Xi", "k*Xi", "Dígitos del centro", "Ri"])
        self.tabla_mc.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.tabla_mc.setAlternatingRowColors(True)
        self.tabla_mc.verticalHeader().setVisible(False)
        layout.addWidget(self.tabla_mc)

        # Conexiones
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
        semilla = self.semilla_input_mc.text().strip()
        const = self.constante_input_mc.text().strip()
        n_text = self.cantidad_input_mc.text().strip()
        
        if not semilla or not const or not n_text:
            QMessageBox.warning(self, "Error", "Todos los campos son obligatorios")
            return
            
        if not (semilla.isdigit() and const.isdigit() and n_text.isdigit()):
            QMessageBox.warning(self, "Error", "Semilla, constante y cantidad deben ser números enteros")
            return

        generator = MultiplicadorConstante(int(semilla), int(const), int(n_text))
        resultados = generator.generar_tabla()
        self.ri_list_mc = [r["Ri"] for r in resultados]

        self.tabla_mc.setRowCount(len(resultados))
        for i, r in enumerate(resultados):
            # Mostrar la multiplicación explícita: "Xi * k = resultado"
            k = int(const)
            xi = int(r["Xi"])
            mult_str = f"{xi} * {k} = {r['k*Xi']}"
            
            self.tabla_mc.setItem(i, 0, QTableWidgetItem(str(r["Iteración"])))
            self.tabla_mc.setItem(i, 1, QTableWidgetItem(str(r["Xi"])))
            self.tabla_mc.setItem(i, 2, QTableWidgetItem(mult_str))
            self.tabla_mc.setItem(i, 3, QTableWidgetItem(r["Dígitos del centro"]))
            self.tabla_mc.setItem(i, 4, QTableWidgetItem(f"{r['Ri']:.6f}"))

    # ---------- HISTOGRAMA ----------
    def ver_histograma_ventana(self, ri_list, titulo):
        if not ri_list:
            QMessageBox.warning(self, "Advertencia", "No hay datos para mostrar. Genere números primero.")
            return
            
        dialog = QDialog(self)
        dialog.setWindowTitle(f"Histograma de Ri - {titulo}")
        dialog.setMinimumSize(700, 500)
        layout = QVBoxLayout(dialog)

        fig, ax = plt.subplots(figsize=(8, 5))
        canvas = FigureCanvas(fig)
        layout.addWidget(canvas)

        # Configurar estilo moderno para el histograma
        plt.style.use('default')
        colors = ["#08051d", "#e66008", "#065066", "#267b7e", "#2b0b03"]
        ax.hist(ri_list, bins=10, color=colors[0], edgecolor="white", alpha=0.8)
        ax.set_title(f"Distribución de números generados - {titulo}", fontsize=14, fontweight='bold', pad=20)
        ax.set_xlabel("Valor de Ri", fontweight='bold')
        ax.set_ylabel("Frecuencia", fontweight='bold')
        ax.grid(True, alpha=0.3)
        
        # Añadir línea de media
        mean_val = sum(ri_list) / len(ri_list)
        ax.axvline(mean_val, color=colors[2], linestyle='--', linewidth=2, label=f'Media: {mean_val:.4f}')
        ax.legend()
        
        # Mejorar estética general
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['left'].set_alpha(0.5)
        ax.spines['bottom'].set_alpha(0.5)
        
        canvas.draw()

        dialog.exec()

    # ---------- MÉTODO PARA PRUEBAS ----------
    def obtener_ri_actual(self):
        """Devuelve la lista de Ri según el generador actualmente seleccionado en el ComboBox."""
        index = self.combo_generador.currentIndex()
        if index == 0:  # Cuadrados Medios
            return self.ri_list_cm
        elif index == 1:  # Productos Medios
            return self.ri_list_pm
        elif index == 2:  # Multiplicador Constante
            return self.ri_list_mc
        return []

    # ---------- EXPORTAR CSV ----------
    def exportar_csv(self, tabla, generador_nombre):
        if tabla.rowCount() == 0:
            QMessageBox.warning(self, "Advertencia", "No hay datos para exportar. Genere números primero.")
            return
            
        path, _ = QFileDialog.getSaveFileName(
            self, "Guardar CSV", f"{generador_nombre}.csv", "CSV Files (*.csv)"
        )
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


if __name__ == "__main__":
    from PyQt6.QtWidgets import QApplication
    app = QApplication(sys.argv)
    
    # Establecer estilo fusion para una apariencia más moderna
    app.setStyle("Fusion")
    
    window = TabGeneradores()
    window.setWindowTitle("Generadores de Números Pseudoaleatorios")
    window.resize(1000, 700)
    window.show()
    
    sys.exit(app.exec())