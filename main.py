import sys
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QTabWidget, QWidget, QVBoxLayout, QLabel,
    QPushButton, QFrame, QMessageBox
)
from PyQt6.QtGui import QFont
from PyQt6.QtCore import Qt

# Importar tus pestañas
from ui.tab_generadores import TabGeneradores
from ui.tab_pruebas import TabPruebas
from ui.tab_variables import TabVariables  
from ui.tab_automata_celular import TabAutomataCelular
from ui.manual_usuario import ManualUsuario  

class WelcomeWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Bienvenido")
        self.resize(600, 400)
        self.setMinimumSize(500, 350)

        # Fondo degradado claro
        self.setStyleSheet("""
            QWidget {
                background: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:1,
                                            stop:0 #74b9ff, stop:1 #55efc4);
                color: #2d3436;
            }
        """)

        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        box = QFrame()
        box.setStyleSheet("""
            QFrame {
                background-color: #dfe6e9;
                border-radius: 15px;
                padding: 30px;
                border: 2px solid #0984e3;
            }
        """)
        box_layout = QVBoxLayout(box)
        box_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        label = QLabel("Bienvenido al Sistema de Números Pseudoaleatorios :)")
        label.setFont(QFont("Segoe UI", 16, QFont.Weight.Bold))
        label.setWordWrap(True)
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        box_layout.addWidget(label)

        box_layout.addSpacing(20)

        self.btn_enter = QPushButton("Ingresar")
        self.btn_enter.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
        self.btn_enter.setStyleSheet("""
            QPushButton {
                background-color: #00b894;
                color: white;
                padding: 12px 25px;
                border-radius: 10px;
            }
            QPushButton:hover {
                background-color: #019875;
            }
        """)
        box_layout.addWidget(self.btn_enter, alignment=Qt.AlignmentFlag.AlignCenter)

        layout.addWidget(box)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("🎲 Sistema de Números Pseudoaleatorios 🎲")
        self.resize(1200, 800)  #
        self.setMinimumSize(900, 650)

        self.tabs = QTabWidget()
        self.setCentralWidget(self.tabs)

        # Diseño de pestañas actualizado
        self.tabs.setStyleSheet("""
            QTabWidget::pane { 
                border: 1px solid #0984e3; 
                top:-1px; 
                background: #dfe6e9; 
            }
            QTabBar::tab { 
                background: #74b9ff; 
                padding: 10px 15px; 
                border-top-left-radius: 8px; 
                border-top-right-radius: 8px; 
                color: #2d3436; 
                margin-right: 2px;
                font-weight: bold;
            }
            QTabBar::tab:selected { 
                background: #0984e3; 
                color: white; 
            }
            QTabBar::tab:hover {
                background: #3498db;
            }
        """)

      
        self.generadores_tab = TabGeneradores()
        self.pruebas_tab = TabPruebas(self.generadores_tab)
        self.variables_tab = TabVariables()
        self.automata_tab = TabAutomataCelular()
        self.manual_tab = ManualUsuario()  # 

        # Agregar pestañas
        self.tabs.addTab(self.generadores_tab, "🎲 Generadores")
        self.tabs.addTab(self.pruebas_tab, "📊 Pruebas Estadísticas")
        self.tabs.addTab(self.variables_tab, "📈 Variables Aleatorias")
        self.tabs.addTab(self.automata_tab, "🔬 Autómata Celular")
        self.tabs.addTab(self.manual_tab, "📚 Manual de Usuario")  # ✅ NUEVA PESTAÑA

        self.pruebas_tab.resultados_generados.connect(self.variables_tab.mostrar_resultados)

        # Botón salir
        self.btn_exit = QPushButton("Salir")
        self.btn_exit.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
        self.btn_exit.setStyleSheet("""
            QPushButton {
                background-color: #e17055;
                color: white;
                padding: 6px 15px;
                border-radius: 8px;
            }
            QPushButton:hover {
                background-color: #d35400;
            }
        """)
        self.btn_exit.clicked.connect(self.salir_con_confirmacion)
        self.tabs.setCornerWidget(self.btn_exit, Qt.Corner.TopRightCorner)
        
        # ✅ Mostrar mensaje de bienvenida con opción al manual
        self.mostrar_bienvenida()

    def salir_con_confirmacion(self):
        """Salir con mensaje de confirmación bonito"""
        reply = QMessageBox.question(
            self,
            "👋 ¡Hasta Pronto!",
            "¿Estás seguro de que quieres salir?\n\n"
            "¡Gracias por usar nuestro Sistema de Simulación! \n"
            "Esperamos verte pronto de nuevo. 😊",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            self.close()

    def mostrar_bienvenida(self):
        """Mostrar mensaje de bienvenida al iniciar"""
        from PyQt6.QtCore import QTimer
        
        QTimer.singleShot(500, self._mostrar_bienvenida_delay)

    def _mostrar_bienvenida_delay(self):
        """Muestra bienvenida después de que la ventana esté cargada"""
        msg = QMessageBox(self)
        msg.setWindowTitle("🌟 ¡Bienvenido al Sistema de Simulación!")
        msg.setText("""
        <h3>🎯 Sistema Integral de Simulación</h3>
        
        <p><b>🎲 Generadores:</b> Crea números pseudoaleatorios</p>
        <p><b>📊 Pruebas:</b> Valida la calidad de las secuencias</p>
        <p><b>📈 Variables:</b> Simula distribuciones probabilísticas</p>
        <p><b>🔬 Autómatas:</b> Modela sistemas complejos</p>
        <p><b>📚 Manual:</b> Consulta ayuda completa integrada</p>
        
        <p>¿Necesitas ayuda para comenzar?</p>
        """)
        
        btn_manual = msg.addButton("📚 Ir al Manual", QMessageBox.ButtonRole.ActionRole)
        btn_empezar = msg.addButton("Comenzar a Explorar", QMessageBox.ButtonRole.AcceptRole)
        msg.setDefaultButton(btn_empezar)
        
        msg.exec()
        
        if msg.clickedButton() == btn_manual:
            self.tabs.setCurrentIndex(4)  # Cambiar a pestaña manual


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    app.setFont(QFont("Segoe UI", 10))

    welcome = WelcomeWindow()
    main_window = MainWindow()
    
    welcome.btn_enter.clicked.connect(lambda: (main_window.show(), welcome.close()))
    welcome.show()
    
    sys.exit(app.exec())