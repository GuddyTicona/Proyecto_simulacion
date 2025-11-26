# ui/manual_usuario.py
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTextEdit, QPushButton, 
    QListWidget, QSplitter, QLabel, QScrollArea, QFrame, 
    QMessageBox, QSizePolicy
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

class ManualUsuario(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(5)
        
        # Título
        titulo = QLabel("📚 Manual de Usuario - Sistema de Simulación")
        titulo.setFont(QFont("Segoe UI", 16, QFont.Weight.Bold))
        titulo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        titulo.setStyleSheet("""
            QLabel {
                color: #2d3436; 
               
                background-color: #dfe6e9;
                border-radius: 10px;
                border: 2px solid #0984e3;
            }
        """)
        layout.addWidget(titulo)
        
        # Splitter para navegación y contenido
        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.setChildrenCollapsible(False)
        
        # Panel de navegación
        nav_widget = QWidget()
        nav_widget.setMaximumWidth(300)
        nav_layout = QVBoxLayout(nav_widget)
        nav_layout.setContentsMargins(5, 5, 5, 5)
        nav_layout.setSpacing(10)
        
        nav_label = QLabel("📑 Contenido del Manual")
        nav_label.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
        nav_label.setStyleSheet("color: #0984e3; padding: 10px;")
        nav_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        nav_layout.addWidget(nav_label)
        
        self.lista_contenido = QListWidget()
        self.lista_contenido.setFont(QFont("Segoe UI", 10))
        self.lista_contenido.addItems([
            "🚀 Introducción General",
            "🎲 Generadores de Números",
            "📊 Pruebas Estadísticas", 
            "📈 Variables Aleatorias",
            "🔬 Autómatas Celulares",
            "💡 Consejos Prácticos",
            "❓ Preguntas Frecuentes"
        ])
        self.lista_contenido.currentRowChanged.connect(self.mostrar_contenido)
        self.lista_contenido.setStyleSheet("""
            QListWidget {
                background-color: white;
                border: 2px solid #bdc3c7;
                border-radius: 8px;
                padding: 5px;
            }
            QListWidget::item {
                padding: 12px 8px;
                border-bottom: 1px solid #ecf0f1;
                margin: 2px;
                border-radius: 5px;
            }
            QListWidget::item:selected {
                background-color: #3498db;
                color: white;
                border-radius: 5px;
            }
            QListWidget::item:hover {
                background-color: #ecf0f1;
                border-radius: 5px;
            }
        """)
        nav_layout.addWidget(self.lista_contenido)
        
        # Panel de contenido
        self.contenido_widget = QWidget()
        self.contenido_layout = QVBoxLayout(self.contenido_widget)
        self.contenido_layout.setContentsMargins(20, 20, 20, 20)
        
        # Área de scroll para el contenido
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidget(self.contenido_widget)
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.scroll_area.setStyleSheet("""
            QScrollArea {
                border: 2px solid #bdc3c7;
                border-radius: 8px;
                background-color: white;
            }
            QScrollBar:vertical {
                background: #f1f1f1;
                width: 5px;
                margin: 0px;
            }
            QScrollBar::handle:vertical {
                background: #3498db;
                border-radius: 2px;
                min-height: 1px;
            }
            QScrollBar::handle:vertical:hover {
                background: #2980b9;
            }
        """)
        
        splitter.addWidget(nav_widget)
        splitter.addWidget(self.scroll_area)
        splitter.setSizes([300, 700])
        
        layout.addWidget(splitter)
        
        # Mostrar contenido inicial
        self.lista_contenido.setCurrentRow(0)
        
    def mostrar_contenido(self, index):
        """Muestra el contenido según la selección"""
        # Limpiar contenido anterior
        for i in reversed(range(self.contenido_layout.count())): 
            widget = self.contenido_layout.itemAt(i).widget()
            if widget:
                widget.deleteLater()
        
        # Crear nuevo contenido
        contenido_widget = self.crear_contenido_seccion(index)
        self.contenido_layout.addWidget(contenido_widget)
    
    def crear_contenido_seccion(self, index):
        """Crea el widget de contenido para cada sección"""
        scroll_content = QScrollArea()
        scroll_content.setWidgetResizable(True)
        scroll_content.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        scroll_content.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        
        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)
        content_layout.setContentsMargins(10, 10, 10, 10)
        
        text_edit = QTextEdit()
        text_edit.setReadOnly(True)
        text_edit.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        
        # Obtener el contenido HTML según el índice
        contenidos_html = {
            0: self.get_html_introduccion(),
            1: self.get_html_generadores(),
            2: self.get_html_pruebas(),
            3: self.get_html_variables(),
            4: self.get_html_automatas(),
            5: self.get_html_consejos(),
            6: self.get_html_preguntas()
        }
        
        html_content = contenidos_html.get(index, self.get_html_introduccion())
        text_edit.setHtml(html_content)
        
        # Estilos del text edit
        text_edit.setStyleSheet("""
            QTextEdit {
                background-color: white;
                border: none;
                font-family: "Segoe UI";
                font-size: 13px;
                line-height: 1;
                padding: 10px;
            }
        """)
        
        content_layout.addWidget(text_edit)
        scroll_content.setWidget(content_widget)
        
        return scroll_content

    def get_html_introduccion(self):
        return """
        <div style='font-family: "Segoe UI"; font-size: 14px; line-height: 1;'>
            <h1 style='color: #2c3e50; text-align: center;'>🚀 Sistema de Simulación - Manual de Usuario</h1>
            
            <div style='background-color: #e8f4fd; padding: 20px; border-radius: 10px; border-left: 5px solid #3498db; margin: 20px 0;'>
                <h2 style='color: #2980b9; margin-top: 0;'>🎯 ¿Qué es este sistema?</h2>
                <p>Este es un sistema integral de simulación que combina <b>4 módulos principales</b> 
                para el estudio de números pseudoaleatorios y sistemas complejos.</p>
            </div>
            
            <h3 style='color: #2c3e50;'>✨ Módulos Disponibles:</h3>
            <ul style='line-height: 1.8;'>
                <li style='margin: 10px 0;'><b>🎲 Generadores:</b> Crea secuencias de números pseudoaleatorios</li>
                <li style='margin: 10px 0;'><b>📊 Pruebas Estadísticas:</b> Valida la calidad de los generadores</li>
                <li style='margin: 10px 0;'><b>📈 Variables Aleatorias:</b> Simula distribuciones probabilísticas</li>
                <li style='margin: 10px 0;'><b>🔬 Autómatas Celulares:</b> Modela sistemas complejos y epidemiológicos</li>
            </ul>
            
            <div style='background-color: #fff8e1; padding: 20px; border-radius: 10px; border-left: 5px solid #f39c12; margin: 20px 0;'>
                <h3 style='color: #e67e22; margin-top: 0;'>💡 Flujo Recomendado:</h3>
                <ol style='line-height: 1.8;'>
                    <li style='margin: 10px 0;'>Genera números en la pestaña <b>Generadores</b></li>
                    <li style='margin: 10px 0;'>Valida su calidad en <b>Pruebas Estadísticas</b></li>
                    <li style='margin: 10px 0;'>Usa los números para simular distribuciones en <b>Variables Aleatorias</b></li>
                    <li style='margin: 10px 0;'>Explora sistemas complejos en <b>Autómatas Celulares</b></li>
                </ol>
            </div>
        </div>
        """

    def get_html_generadores(self):
        return """
        <div style='font-family: "Segoe UI"; font-size: 14px; line-height: 1.6;'>
            <h1 style='color: #2c3e50;'>🎲 Generadores de Números Pseudoaleatorios</h1>
            
            <h2>📋 Generadores Disponibles</h2>
            <ul style='line-height: 1.8;'>
                <li><b>Cuadrados Medios:</b> Método clásico usando cuadrados</li>
                <li><b>Congruencial Lineal:</b> Algoritmo estándar industrial</li>
                <li><b>Congruencial Multiplicativo:</b> Variante eficiente</li>
                <li><b>Transformada Inversa:</b> Para distribuciones específicas</li>
            </ul>
            
            <h2>🎮 Cómo Usar</h2>
            <ol style='line-height: 1.8;'>
                <li>Selecciona el tipo de generador</li>
                <li>Configura los parámetros requeridos</li>
                <li>Haz clic en "Generar"</li>
                <li>Visualiza los resultados en la tabla</li>
                <li>Exporta si es necesario</li>
            </ol>
        </div>
        """

    def get_html_pruebas(self):
        return """
        <div style='font-family: "Segoe UI"; font-size: 14px; line-height: 1.6;'>
            <h1 style='color: #2c3e50;'>📊 Pruebas Estadísticas</h1>
            
            <p>Valida la calidad y aleatoriedad de tus secuencias generadas.</p>
            
            <h2>🔍 Pruebas Disponibles</h2>
            <ul style='line-height: 1.8;'>
                <li><b>Prueba de Medias:</b> Verifica que la media sea 0.5</li>
                <li><b>Prueba de Varianza:</b> Valida la dispersión correcta</li>
                <li><b>Prueba Chi-cuadrada:</b> Evalúa distribución uniforme</li>
                <li><b>Prueba de Kolmogorov-Smirnov:</b> Compara distribuciones</li>
                <li><b>Prueba de Póker:</b> Analiza patrones en los números</li>
            </ul>
        </div>
        """

    def get_html_variables(self):
        return """
        <div style='font-family: "Segoe UI"; font-size: 14px; line-height: 1.6;'>
            <h1 style='color: #2c3e50;'>📈 Variables Aleatorias</h1>
            
            <p>Simula diferentes distribuciones probabilísticas usando números pseudoaleatorios.</p>
            
            <h2>📊 Distribuciones Continuas</h2>
            <ul style='line-height: 1.8;'>
                <li><b>Uniforme:</b> Todos los valores igualmente probables</li>
                <li><b>Normal:</b> Distribución en forma de campana</li>
                <li><b>Exponencial:</b> Tiempos entre eventos</li>
            </ul>
        </div>
        """

    def get_html_automatas(self):
        return """
        <div style='font-family: "Segoe UI"; font-size: 14px; line-height: 1.6;'>
            <h1 style='color: #2c3e50;'>🔬 Autómatas Celulares</h1>
            
            <p>Modela sistemas complejos y comportamientos emergentes.</p>
            
            <h2>🎮 Tres Modos Disponibles</h2>
            
            <h3>1. Conway (Juego de la Vida)</h3>
            <ul style='line-height: 1.8;'>
                <li><b>Reglas:</b> B3/S23 (Nacen con 3, Sobreviven con 2 o 3)</li>
                <li><b>Controles:</b> Iniciar, Pausar, Siguiente, Aleatorio</li>
                <li><b>Características:</b> Patrones, naves espaciales, osciladores</li>
            </ul>
            
            <h3>2. Unidimensionales</h3>
            <ul style='line-height: 1.8;'>
                <li><b>Reglas Elementales:</b> 30, 90, 110, 184, etc.</li>
                <li><b>Visualización:</b> Evolución temporal por generaciones</li>
            </ul>
        </div>
        """

    def get_html_consejos(self):
        return """
        <div style='font-family: "Segoe UI"; font-size: 14px; line-height: 1.6;'>
            <h1 style='color: #2c3e50;'>💡 Consejos Prácticos</h1>
            
            <h2>🎯 Para Mejores Resultados</h2>
            
            <div style='background-color: #f7f9fc; padding: 15px; border-radius: 8px; margin: 10px 0;'>
                <h3 style='color: #3498db;'>🔧 Generadores</h3>
                <ul style='line-height: 1.8;'>
                    <li>Usa semillas diferentes para comparar resultados</li>
                    <li>El congruencial lineal es más estable para producción</li>
                    <li>Verifica siempre con pruebas estadísticas</li>
                </ul>
            </div>
        </div>
        """

    def get_html_preguntas(self):
        return """
        <div style='font-family: "Segoe UI"; font-size: 14px; line-height: 1.6;'>
            <h1 style='color: #2c3e50;'>❓ Preguntas Frecuentes</h1>
            
            <h2>🔧 Problemas Técnicos</h2>
            
            <h3>¿Los números generados son realmente aleatorios?</h3>
            <p><b>R:</b> Son <i>pseudoaleatorios</i> - determinísticos pero que pasan pruebas de aleatoriedad.</p>
            
            <h3>¿Qué hago si una prueba estadística falla?</h3>
            <p><b>R:</b> Intenta con diferentes parámetros o otro generador.</p>
        </div>
        """