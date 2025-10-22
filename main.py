import sys
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QTabWidget, QWidget, QVBoxLayout, QLabel,
    QPushButton, QFrame
)
from PyQt6.QtGui import QFont
from PyQt6.QtCore import Qt

# Importar tus pestañas
from ui.tab_generadores import TabGeneradores
from ui.tab_pruebas import TabPruebas
from ui.tab_variables import TabVariables  
from ui.tab_automata_celular import TabAutomataCelular


# ---------------- Ventana de Bienvenida Mejorada ---------------- #
class WelcomeWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Bienvenido")
        self.resize(600, 400)
        self.setMinimumSize(500, 350)

        # Fondo degradado
        self.setStyleSheet("""
            QWidget {
                background: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:1,
                                            stop:0 #6c5ce7, stop:1 #00b894);
            }
        """)

        # Layout principal
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Caja central
        box = QFrame()
        box.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 15px;
                padding: 30px;
            }
        """)
        box_layout = QVBoxLayout(box)
        box_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Mensaje
        label = QLabel("Bienvenido al Sistema de Números Pseudoaleatorios :)")
        label.setFont(QFont("Segoe UI", 16, QFont.Weight.Bold))
        label.setWordWrap(True)
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        box_layout.addWidget(label)

        # Espacio
        box_layout.addSpacing(20)

        # Botón ingresar
        self.btn_enter = QPushButton("Ingresar")
        self.btn_enter.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
        self.btn_enter.setStyleSheet("""
            QPushButton {
                background-color: #6c5ce7;
                color: white;
                padding: 12px 25px;
                border-radius: 10px;
            }
            QPushButton:hover {
                background-color: #341f97;
            }
        """)
        box_layout.addWidget(self.btn_enter, alignment=Qt.AlignmentFlag.AlignCenter)

        layout.addWidget(box)


# ---------------- Ventana Principal ---------------- #
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("🎲 Sistema de Números Pseudoaleatorios 🎲")
        self.resize(1000, 700)
        self.setMinimumSize(800, 600)

        # Crear QTabWidget
        self.tabs = QTabWidget()
        self.setCentralWidget(self.tabs)

        # Estilo de pestañas
        self.tabs.setStyleSheet("""
            QTabWidget::pane { border: 1px solid #ccc; top:-1px; background: #f0f2f5; }
            QTabBar::tab { background: #e0e0e0; padding: 10px; border-top-left-radius: 8px; border-top-right-radius: 8px; }
            QTabBar::tab:selected { background: #6c5ce7; color: white; font-weight: bold; }
        """)

        # Instanciar pestañas
        self.generadores_tab = TabGeneradores()
        self.pruebas_tab = TabPruebas(self.generadores_tab)
        self.variables_tab = TabVariables()
        self.automata_tab = TabAutomataCelular()
        # Agregar pestañas
        self.tabs.addTab(self.generadores_tab, "Generadores")
        self.tabs.addTab(self.pruebas_tab, "Pruebas Estadísticas")
        self.tabs.addTab(self.variables_tab, "Variables Aleatorias")
        self.tabs.addTab(self.automata_tab, "Autómata Celular")
        # Conectar resultados
        self.pruebas_tab.resultados_generados.connect(self.variables_tab.mostrar_resultados)

        # ---------------- Botón Salir ---------------- #
        self.btn_exit = QPushButton("Salir")
        self.btn_exit.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
        self.btn_exit.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c;
                color: white;
                padding: 6px 15px;
                border-radius: 8px;
            }
            QPushButton:hover {
                background-color: #c0392b;
            }
        """)
        self.btn_exit.clicked.connect(self.close)
        self.tabs.setCornerWidget(self.btn_exit, Qt.Corner.TopRightCorner)


# ---------------- Programa Principal ---------------- #
if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    app.setFont(QFont("Segoe UI", 10))

    # Crear ventana de bienvenida
    welcome = WelcomeWindow()
    main_window = MainWindow()

    # Conectar botón ingresar
    welcome.btn_enter.clicked.connect(lambda: (main_window.show(), welcome.close()))

    welcome.show()  # Mostrar primero la bienvenida

    sys.exit(app.exec())
