from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QGroupBox, 
                             QLabel, QSlider, QDoubleSpinBox, QSpinBox, 
                             QComboBox, QSplitter, QFormLayout, QTextEdit,
                             QFrame, QSizePolicy)
from PyQt6.QtCore import Qt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import numpy as np

# Importar distribuciones
from distribuciones.distribuciones_continuas import *
from distribuciones.distribuciones_discretas import *

class MatplotlibCanvas(FigureCanvas):
    def __init__(self, parent=None, width=5, height=4, dpi=100):
        self.fig = Figure(figsize=(width, height), dpi=dpi)
        super().__init__(self.fig)
        self.setParent(parent)

class TabVariables(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()
        
    def init_ui(self):
        # Layout principal
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(10)
        
        # Splitter para dividir controles y gráficos
        splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # =========================================================================
        # PANEL DE CONTROLES (IZQUIERDA)
        # =========================================================================
        controls_widget = QWidget()
        controls_widget.setMaximumWidth(400)
        controls_layout = QVBoxLayout(controls_widget)
        controls_layout.setSpacing(15)
        
        # Grupo de selección de distribución
        dist_group = QGroupBox("CONFIGURACIÓN DE DISTRIBUCIÓN")
        dist_group.setStyleSheet("QGroupBox { font-weight: bold; }")
        dist_layout = QFormLayout(dist_group)
        dist_layout.setVerticalSpacing(10)
        
        self.dist_type_combo = QComboBox()
        self.dist_type_combo.addItems(["Continuas", "Discretas"])
        self.dist_type_combo.currentTextChanged.connect(self.on_dist_type_changed)
        dist_layout.addRow("Tipo de distribución:", self.dist_type_combo)
        
        self.dist_combo = QComboBox()
        self.dist_combo.currentTextChanged.connect(self.on_distribution_changed)
        dist_layout.addRow("Distribución:", self.dist_combo)
        
        # Grupo de parámetros
        self.params_group = QGroupBox("PARÁMETROS")
        self.params_group.setStyleSheet("QGroupBox { font-weight: bold; }")
        self.params_layout = QFormLayout(self.params_group)
        self.params_layout.setVerticalSpacing(8)
        
        # Grupo de información estadística
        self.info_group = QGroupBox("INFORMACIÓN ESTADÍSTICA")
        self.info_group.setStyleSheet("QGroupBox { font-weight: bold; }")
        info_layout = QVBoxLayout(self.info_group)
        self.info_text = QTextEdit()
        self.info_text.setMaximumHeight(180)
        self.info_text.setReadOnly(True)
        self.info_text.setStyleSheet("""
            QTextEdit {
                background-color: #f8f9fa;
                border: 1px solid #dee2e6;
                border-radius: 4px;
                padding: 8px;
                font-family: Consolas, monospace;
            }
        """)
        info_layout.addWidget(self.info_text)
        
        # Agregar grupos al layout de controles
        controls_layout.addWidget(dist_group)
        controls_layout.addWidget(self.params_group)
        controls_layout.addWidget(self.info_group)
        controls_layout.addStretch()
        
        # =========================================================================
        # PANEL DE GRÁFICOS (DERECHA)
        # =========================================================================
        graphs_widget = QWidget()
        graphs_layout = QVBoxLayout(graphs_widget)
        graphs_layout.setSpacing(15)
        
        # Frame para PDF/PMF
        pdf_frame = QFrame()
        pdf_frame.setFrameStyle(QFrame.Shape.StyledPanel)
        pdf_layout = QVBoxLayout(pdf_frame)
        
        pdf_label = QLabel("FUNCIÓN DE DENSIDAD/MASA DE PROBABILIDAD (PDF/PMF)")
        pdf_label.setStyleSheet("font-weight: bold; color: #2c3e50; font-size: 12px;")
        pdf_layout.addWidget(pdf_label)
        
        self.pdf_canvas = MatplotlibCanvas(self, width=7, height=4, dpi=100)
        pdf_layout.addWidget(self.pdf_canvas)
        
        # Frame para CDF
        cdf_frame = QFrame()
        cdf_frame.setFrameStyle(QFrame.Shape.StyledPanel)
        cdf_layout = QVBoxLayout(cdf_frame)
        
        cdf_label = QLabel("FUNCIÓN DE DISTRIBUCIÓN ACUMULATIVA (CDF)")
        cdf_label.setStyleSheet("font-weight: bold; color: #2c3e50; font-size: 12px;")
        cdf_layout.addWidget(cdf_label)
        
        self.cdf_canvas = MatplotlibCanvas(self, width=7, height=4, dpi=100)
        cdf_layout.addWidget(self.cdf_canvas)
        
        # Agregar frames al layout de gráficos
        graphs_layout.addWidget(pdf_frame)
        graphs_layout.addWidget(cdf_frame)
        
        # =========================================================================
        # CONFIGURACIÓN FINAL
        # =========================================================================
        # Agregar widgets al splitter
        splitter.addWidget(controls_widget)
        splitter.addWidget(graphs_widget)
        splitter.setSizes([350, 800])
        
        # Estilo del splitter
        splitter.setStyleSheet("""
            QSplitter::handle {
                background-color: #bdc3c7;
                width: 3px;
            }
            QSplitter::handle:hover {
                background-color: #3498db;
            }
        """)
        
        main_layout.addWidget(splitter)
        
        # Diccionario para almacenar controles de parámetros
        self.param_controls = {}
        
        # Inicializar con distribuciones continuas
        self.on_dist_type_changed("Continuas")
        
        # Aplicar estilo general
        self.apply_styles()
    
    def apply_styles(self):
        """Aplica estilos consistentes a los controles"""
        style = """
            QComboBox, QDoubleSpinBox, QSpinBox {
                padding: 6px;
                border: 1px solid #bdc3c7;
                border-radius: 4px;
                background-color: white;
                min-height: 20px;
            }
            QComboBox:focus, QDoubleSpinBox:focus, QSpinBox:focus {
                border-color: #3498db;
            }
            QGroupBox {
                margin-top: 10px;
                font-weight: bold;
                color: #2c3e50;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }
        """
        self.setStyleSheet(style)
    
    def mostrar_resultados(self, resultados):
        """Método para mostrar resultados desde otras pestañas"""
        pass
        
    def on_dist_type_changed(self, dist_type):
        """Actualiza las distribuciones disponibles según el tipo seleccionado"""
        self.dist_combo.clear()
        
        if dist_type == "Continuas":
            distributions = [
                "Uniforme", "Erlang", "Exponencial", 
                "Gamma", "Normal", "Weibull"
            ]
        else:
            distributions = [
                "Uniforme Discreta", "Bernoulli", "Binomial", "Poisson"
            ]
        
        self.dist_combo.addItems(distributions)
        self.on_distribution_changed(self.dist_combo.currentText())
    
    def on_distribution_changed(self, distribution):
        """Actualiza los controles de parámetros según la distribución seleccionada"""
        # Limpiar layout de parámetros
        self.clear_params_layout()
        
        # Crear controles específicos para cada distribución
        if distribution == "Uniforme":
            self.create_uniforme_controls()
        elif distribution == "Erlang":
            self.create_erlang_controls()
        elif distribution == "Exponencial":
            self.create_exponencial_controls()
        elif distribution == "Gamma":
            self.create_gamma_controls()
        elif distribution == "Normal":
            self.create_normal_controls()
        elif distribution == "Weibull":
            self.create_weibull_controls()
        elif distribution == "Uniforme Discreta":
            self.create_uniforme_discreta_controls()
        elif distribution == "Bernoulli":
            self.create_bernoulli_controls()
        elif distribution == "Binomial":
            self.create_binomial_controls()
        elif distribution == "Poisson":
            self.create_poisson_controls()
        
        # Actualizar gráficos
        self.update_plots()
    
    def clear_params_layout(self):
        """Limpia todos los controles de parámetros"""
        while self.params_layout.rowCount() > 0:
            self.params_layout.removeRow(0)
        self.param_controls.clear()
    
    def create_uniforme_controls(self):
        """Crea controles para distribución uniforme continua"""
        self.param_controls['a'] = QDoubleSpinBox()
        self.param_controls['a'].setRange(-100, 100)
        self.param_controls['a'].setValue(0.0)
        self.param_controls['a'].setSingleStep(0.1)
        self.param_controls['a'].valueChanged.connect(self.update_plots)
        
        self.param_controls['b'] = QDoubleSpinBox()
        self.param_controls['b'].setRange(-100, 100)
        self.param_controls['b'].setValue(1.0)
        self.param_controls['b'].setSingleStep(0.1)
        self.param_controls['b'].valueChanged.connect(self.update_plots)
        
        self.params_layout.addRow("Límite inferior (a):", self.param_controls['a'])
        self.params_layout.addRow("Límite superior (b):", self.param_controls['b'])
    
    def create_erlang_controls(self):
        """Crea controles para distribución Erlang"""
        self.param_controls['k'] = QSpinBox()
        self.param_controls['k'].setRange(1, 100)
        self.param_controls['k'].setValue(2)
        self.param_controls['k'].valueChanged.connect(self.update_plots)
        
        self.param_controls['lam'] = QDoubleSpinBox()
        self.param_controls['lam'].setRange(0.1, 10.0)
        self.param_controls['lam'].setValue(1.0)
        self.param_controls['lam'].setSingleStep(0.1)
        self.param_controls['lam'].valueChanged.connect(self.update_plots)
        
        self.params_layout.addRow("Forma (k):", self.param_controls['k'])
        self.params_layout.addRow("Tasa (λ):", self.param_controls['lam'])
    
    def create_exponencial_controls(self):
        """Crea controles para distribución exponencial"""
        self.param_controls['lam'] = QDoubleSpinBox()
        self.param_controls['lam'].setRange(0.1, 10.0)
        self.param_controls['lam'].setValue(1.0)
        self.param_controls['lam'].setSingleStep(0.1)
        self.param_controls['lam'].valueChanged.connect(self.update_plots)
        
        self.params_layout.addRow("Tasa (λ):", self.param_controls['lam'])
    
    def create_gamma_controls(self):
        """Crea controles para distribución gamma"""
        self.param_controls['alpha'] = QDoubleSpinBox()
        self.param_controls['alpha'].setRange(0.1, 20.0)
        self.param_controls['alpha'].setValue(2.0)
        self.param_controls['alpha'].setSingleStep(0.1)
        self.param_controls['alpha'].valueChanged.connect(self.update_plots)
        
        self.param_controls['beta'] = QDoubleSpinBox()
        self.param_controls['beta'].setRange(0.1, 10.0)
        self.param_controls['beta'].setValue(1.0)
        self.param_controls['beta'].setSingleStep(0.1)
        self.param_controls['beta'].valueChanged.connect(self.update_plots)
        
        self.params_layout.addRow("Forma (α):", self.param_controls['alpha'])
        self.params_layout.addRow("Escala (β):", self.param_controls['beta'])
    
    def create_normal_controls(self):
        """Crea controles para distribución normal"""
        self.param_controls['mu'] = QDoubleSpinBox()
        self.param_controls['mu'].setRange(-50, 50)
        self.param_controls['mu'].setValue(0.0)
        self.param_controls['mu'].setSingleStep(0.1)
        self.param_controls['mu'].valueChanged.connect(self.update_plots)
        
        self.param_controls['sigma'] = QDoubleSpinBox()
        self.param_controls['sigma'].setRange(0.1, 20.0)
        self.param_controls['sigma'].setValue(1.0)
        self.param_controls['sigma'].setSingleStep(0.1)
        self.param_controls['sigma'].valueChanged.connect(self.update_plots)
        
        self.params_layout.addRow("Media (μ):", self.param_controls['mu'])
        self.params_layout.addRow("Desviación (σ):", self.param_controls['sigma'])
    
    def create_weibull_controls(self):
        """Crea controles para distribución Weibull"""
        self.param_controls['alpha'] = QDoubleSpinBox()
        self.param_controls['alpha'].setRange(0.1, 10.0)
        self.param_controls['alpha'].setValue(1.0)
        self.param_controls['alpha'].setSingleStep(0.1)
        self.param_controls['alpha'].valueChanged.connect(self.update_plots)
        
        self.param_controls['beta'] = QDoubleSpinBox()
        self.param_controls['beta'].setRange(0.1, 10.0)
        self.param_controls['beta'].setValue(1.0)
        self.param_controls['beta'].setSingleStep(0.1)
        self.param_controls['beta'].valueChanged.connect(self.update_plots)
        
        self.param_controls['gamma'] = QDoubleSpinBox()
        self.param_controls['gamma'].setRange(-10.0, 10.0)
        self.param_controls['gamma'].setValue(0.0)
        self.param_controls['gamma'].setSingleStep(0.1)
        self.param_controls['gamma'].valueChanged.connect(self.update_plots)
        
        self.params_layout.addRow("Forma (α):", self.param_controls['alpha'])
        self.params_layout.addRow("Escala (β):", self.param_controls['beta'])
        self.params_layout.addRow("Localización (γ):", self.param_controls['gamma'])
    
    def create_uniforme_discreta_controls(self):
        """Crea controles para distribución uniforme discreta"""
        self.param_controls['a'] = QSpinBox()
        self.param_controls['a'].setRange(0, 100)
        self.param_controls['a'].setValue(0)
        self.param_controls['a'].valueChanged.connect(self.update_plots)
        
        self.param_controls['b'] = QSpinBox()
        self.param_controls['b'].setRange(0, 100)
        self.param_controls['b'].setValue(10)
        self.param_controls['b'].valueChanged.connect(self.update_plots)
        
        self.params_layout.addRow("Mínimo (a):", self.param_controls['a'])
        self.params_layout.addRow("Máximo (b):", self.param_controls['b'])
    
    def create_bernoulli_controls(self):
        """Crea controles para distribución Bernoulli"""
        self.param_controls['p'] = QDoubleSpinBox()
        self.param_controls['p'].setRange(0.0, 1.0)
        self.param_controls['p'].setValue(0.5)
        self.param_controls['p'].setSingleStep(0.05)
        self.param_controls['p'].valueChanged.connect(self.update_plots)
        
        self.params_layout.addRow("Probabilidad (p):", self.param_controls['p'])
    
    def create_binomial_controls(self):
        """Crea controles para distribución binomial"""
        self.param_controls['n'] = QSpinBox()
        self.param_controls['n'].setRange(1, 100)
        self.param_controls['n'].setValue(10)
        self.param_controls['n'].valueChanged.connect(self.update_plots)
        
        self.param_controls['p'] = QDoubleSpinBox()
        self.param_controls['p'].setRange(0.0, 1.0)
        self.param_controls['p'].setValue(0.5)
        self.param_controls['p'].setSingleStep(0.05)
        self.param_controls['p'].valueChanged.connect(self.update_plots)
        
        self.params_layout.addRow("Ensayos (n):", self.param_controls['n'])
        self.params_layout.addRow("Probabilidad (p):", self.param_controls['p'])
    
    def create_poisson_controls(self):
        """Crea controles para distribución Poisson"""
        self.param_controls['lam'] = QDoubleSpinBox()
        self.param_controls['lam'].setRange(0.1, 50.0)
        self.param_controls['lam'].setValue(5.0)
        self.param_controls['lam'].setSingleStep(0.1)
        self.param_controls['lam'].valueChanged.connect(self.update_plots)
        
        self.params_layout.addRow("Tasa (λ):", self.param_controls['lam'])
    
    def update_plots(self):
        """Actualiza los gráficos según la distribución y parámetros seleccionados"""
        distribution = self.dist_combo.currentText()
        dist_type = self.dist_type_combo.currentText()
        
        try:
            if dist_type == "Continuas":
                self.update_continuous_plots(distribution)
            else:
                self.update_discrete_plots(distribution)
        except Exception as e:
            print(f"Error al actualizar gráficos: {e}")
    
    def update_continuous_plots(self, distribution):
        """Actualiza gráficos para distribuciones continuas"""
        params = self.get_current_params()
        
        if distribution == "Uniforme":
            a, b = params['a'], params['b']
            x = np.linspace(a - (b-a)*0.2, b + (b-a)*0.2, 1000)
            pdf = distribucion_uniforme_pdf(x, a, b)
            cdf = distribucion_uniforme_cdf(x, a, b)
            info = self.get_uniforme_info(a, b)
            
        elif distribution == "Erlang":
            k, lam = params['k'], params['lam']
            x = np.linspace(0, (k+4)/lam, 1000)
            pdf = distribucion_erlang_pdf(x, k, lam)
            cdf = distribucion_erlang_cdf(x, k, lam)
            info = self.get_erlang_info(k, lam)
            
        elif distribution == "Exponencial":
            lam = params['lam']
            x = np.linspace(0, 5/lam, 1000)
            pdf = distribucion_exponencial_pdf(x, lam)
            cdf = distribucion_exponencial_cdf(x, lam)
            info = self.get_exponencial_info(lam)
            
        elif distribution == "Gamma":
            alpha, beta = params['alpha'], params['beta']
            x = np.linspace(0, (alpha+4)*beta, 1000)
            pdf = distribucion_gamma_pdf(x, alpha, beta)
            cdf = distribucion_gamma_cdf(x, alpha, beta)
            info = self.get_gamma_info(alpha, beta)
            
        elif distribution == "Normal":
            mu, sigma = params['mu'], params['sigma']
            x = np.linspace(mu - 4*sigma, mu + 4*sigma, 1000)
            pdf = distribucion_normal_pdf(x, mu, sigma)
            cdf = distribucion_normal_cdf(x, mu, sigma)
            info = self.get_normal_info(mu, sigma)
            
        elif distribution == "Weibull":
            alpha, beta, gamma = params['alpha'], params['beta'], params['gamma']
            x_min = max(0, gamma - beta)
            x = np.linspace(x_min, gamma + 4*beta, 1000)
            pdf = distribucion_weibull_pdf(x, alpha, beta, gamma)
            cdf = distribucion_weibull_cdf(x, alpha, beta, gamma)
            info = self.get_weibull_info(alpha, beta, gamma)
        
        self.update_pdf_plot(x, pdf, distribution, "Continua")
        self.update_cdf_plot(x, cdf, distribution, "Continua")
        self.info_text.setText(info)
    
    def update_discrete_plots(self, distribution):
        """Actualiza gráficos para distribuciones discretas"""
        params = self.get_current_params()
        
        if distribution == "Uniforme Discreta":
            a, b = params['a'], params['b']
            x = np.arange(a, b + 1)
            pmf = distribucion_uniforme_discreta_pmf(x, a, b)
            cdf = distribucion_uniforme_discreta_cdf(x, a, b)
            info = self.get_uniforme_discreta_info(a, b)
            
        elif distribution == "Bernoulli":
            p = params['p']
            x = np.arange(0, 2)
            pmf = distribucion_bernoulli_pmf(x, p)
            cdf = distribucion_bernoulli_cdf(x, p)
            info = self.get_bernoulli_info(p)
            
        elif distribution == "Binomial":
            n, p = params['n'], params['p']
            x = np.arange(0, n + 1)
            pmf = distribucion_binomial_pmf(x, n, p)
            cdf = distribucion_binomial_cdf(x, n, p)
            info = self.get_binomial_info(n, p)
            
        elif distribution == "Poisson":
            lam = params['lam']
            x_max = min(50, int(3 * lam) + 5)
            x = np.arange(0, x_max + 1)
            pmf = distribucion_poisson_pmf(x, lam)
            cdf = distribucion_poisson_cdf(x, lam)
            info = self.get_poisson_info(lam)
        
        self.update_pmf_plot(x, pmf, distribution)
        self.update_cdf_plot(x, cdf, distribution, "Discreta")
        self.info_text.setText(info)
    
    def get_current_params(self):
        """Obtiene los parámetros actuales de los controles"""
        params = {}
        for key, control in self.param_controls.items():
            if isinstance(control, (QDoubleSpinBox, QSpinBox)):
                params[key] = control.value()
        return params
    
    def update_pdf_plot(self, x, y, distribution, dist_type):
        """Actualiza el gráfico de PDF"""
        self.pdf_canvas.fig.clear()
        ax = self.pdf_canvas.fig.add_subplot(111)
        
        ax.plot(x, y, 'b-', linewidth=2, alpha=0.8)
        ax.fill_between(x, y, alpha=0.3, color='blue')
        ax.set_xlabel('x', fontsize=10)
        ax.set_ylabel('f(x)', fontsize=10)
        ax.set_title(f'Distribución {distribution} - PDF', fontsize=11, fontweight='bold')
        ax.grid(True, alpha=0.3)
        ax.tick_params(labelsize=9)
        
        self.pdf_canvas.draw()
    
    def update_pmf_plot(self, x, y, distribution):
        """Actualiza el gráfico de PMF"""
        self.pdf_canvas.fig.clear()
        ax = self.pdf_canvas.fig.add_subplot(111)
        
        ax.bar(x, y, alpha=0.7, edgecolor='blue', width=0.8, color='skyblue')
        ax.set_xlabel('x', fontsize=10)
        ax.set_ylabel('P(X = x)', fontsize=10)
        ax.set_title(f'Distribución {distribution} - PMF', fontsize=11, fontweight='bold')
        ax.grid(True, alpha=0.3)
        ax.tick_params(labelsize=9)
        
        self.pdf_canvas.draw()
    
    def update_cdf_plot(self, x, y, distribution, dist_type):
        """Actualiza el gráfico de CDF"""
        self.cdf_canvas.fig.clear()
        ax = self.cdf_canvas.fig.add_subplot(111)
        
        if dist_type == "Continua":
            ax.plot(x, y, 'r-', linewidth=2, alpha=0.8)
        else:
            ax.step(x, y, where='post', color='red', linewidth=2, alpha=0.8)
        
        ax.set_xlabel('x', fontsize=10)
        ax.set_ylabel('F(x)', fontsize=10)
        ax.set_title(f'Distribución {distribution} - CDF', fontsize=11, fontweight='bold')
        ax.grid(True, alpha=0.3)
        ax.tick_params(labelsize=9)
        
        self.cdf_canvas.draw()
    
    # Métodos para información estadística (mejorados)
    def get_uniforme_info(self, a, b):
        media = (a + b) / 2
        varianza = (b - a) ** 2 / 12
        return f"""📊 Distribución Uniforme Continua U({a}, {b})

• Media (μ): {media:.4f}
• Varianza (σ²): {varianza:.4f}
• Desviación estándar (σ): {np.sqrt(varianza):.4f}
• Rango: [{a}, {b}]"""
    
    def get_erlang_info(self, k, lam):
        media = k / lam
        varianza = k / (lam ** 2)
        return f"""📊 Distribución Erlang k={k}, λ={lam}

• Media (μ): {media:.4f}
• Varianza (σ²): {varianza:.4f}
• Desviación estándar (σ): {np.sqrt(varianza):.4f}
• Moda: {(k-1)/lam if k >= 1 else 0:.4f}"""
    
    def get_exponencial_info(self, lam):
        media = 1 / lam
        varianza = 1 / (lam ** 2)
        return f"""📊 Distribución Exponencial λ={lam}

• Media (μ): {media:.4f}
• Varianza (σ²): {varianza:.4f}
• Desviación estándar (σ): {np.sqrt(varianza):.4f}
• Mediana: {np.log(2)/lam:.4f}"""
    
    def get_gamma_info(self, alpha, beta):
        media = alpha * beta
        varianza = alpha * beta ** 2
        return f"""📊 Distribución Gamma α={alpha}, β={beta}

• Media (μ): {media:.4f}
• Varianza (σ²): {varianza:.4f}
• Desviación estándar (σ): {np.sqrt(varianza):.4f}
• Moda: {beta*(alpha-1) if alpha >= 1 else 0:.4f}"""
    
    def get_normal_info(self, mu, sigma):
        return f"""📊 Distribución Normal N({mu}, {sigma}²)

• Media (μ): {mu:.4f}
• Varianza (σ²): {sigma**2:.4f}
• Desviación estándar (σ): {sigma:.4f}
• Coeficiente de asimetría: 0"""
    
    def get_weibull_info(self, alpha, beta, gamma):
        from scipy.special import gamma as gamma_func
        media = gamma + beta * gamma_func(1 + 1/alpha)
        varianza = beta**2 * (gamma_func(1 + 2/alpha) - gamma_func(1 + 1/alpha)**2)
        return f"""📊 Distribución Weibull α={alpha}, β={beta}, γ={gamma}

• Media (μ): {media:.4f}
• Varianza (σ²): {varianza:.4f}
• Desviación estándar (σ): {np.sqrt(varianza):.4f}"""
    
    def get_uniforme_discreta_info(self, a, b):
        media = (a + b) / 2
        varianza = ((b - a + 1)**2 - 1) / 12
        return f"""📊 Distribución Uniforme Discreta U({a}, {b})

• Media (μ): {media:.4f}
• Varianza (σ²): {varianza:.4f}
• Desviación estándar (σ): {np.sqrt(varianza):.4f}
• Rango: {{{', '.join(map(str, range(a, b+1)))}}}"""
    
    def get_bernoulli_info(self, p):
        media = p
        varianza = p * (1 - p)
        return f"""📊 Distribución Bernoulli p={p}

• Media (μ): {media:.4f}
• Varianza (σ²): {varianza:.4f}
• Desviación estándar (σ): {np.sqrt(varianza):.4f}
• Éxito: P(X=1) = {p:.4f}
• Fracaso: P(X=0) = {1-p:.4f}"""
    
    def get_binomial_info(self, n, p):
        media = n * p
        varianza = n * p * (1 - p)
        return f"""📊 Distribución Binomial n={n}, p={p}

• Media (μ): {media:.4f}
• Varianza (σ²): {varianza:.4f}
• Desviación estándar (σ): {np.sqrt(varianza):.4f}
• Moda: {int((n+1)*p) if (n+1)*p not in [int((n+1)*p)] else f"{int((n+1)*p)-1} y {int((n+1)*p)}" if p != 0 and p != 1 else int((n+1)*p)}"""
    
    def get_poisson_info(self, lam):
        media = lam
        varianza = lam
        return f"""📊 Distribución Poisson λ={lam}

• Media (μ): {media:.4f}
• Varianza (σ²): {varianza:.4f}
• Desviación estándar (σ): {np.sqrt(varianza):.4f}
• Moda: {int(lam) if lam >= 1 else 0}"""