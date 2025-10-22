import numpy as np
from math import exp, log, sqrt, pi, gamma as gamma_func

class DistribucionesContinuas:
    def __init__(self, generador_ri):
        self.generador_ri = generador_ri
    
    def uniforme(self, a, b, n=1):
        """Distribución Uniforme Continua U(a,b)"""
        ri_df = self.generador_ri.generar(n)
        variables = [a + (b - a) * ri for ri in ri_df['Ri']]
        
        return {
            'variables': variables,
            'numeros_aleatorios': ri_df,
            'parametros': f'U({a},{b})',
            'media_teorica': (a + b) / 2,
            'varianza_teorica': (b - a)**2 / 12
        }
    
    def exponencial(self, lambd, n=1):
        """Distribución Exponencial(λ)"""
        ri_df = self.generador_ri.generar(n)
        variables = [- (1 / lambd) * log(1 - ri) for ri in ri_df['Ri']]
        
        return {
            'variables': variables,
            'numeros_aleatorios': ri_df,
            'parametros': f'Exp(λ={lambd})',
            'media_teorica': 1 / lambd,
            'varianza_teorica': 1 / (lambd**2)
        }
    
    def normal(self, mu, sigma, n=1):
        """Distribución Normal N(μ,σ) usando Box-Muller"""
        ri_df = self.generador_ri.generar(2 * n)
        
        variables = []
        for i in range(0, len(ri_df), 2):
            if i + 1 < len(ri_df):
                r1, r2 = ri_df.iloc[i]['Ri'], ri_df.iloc[i+1]['Ri']
                z0 = sqrt(-2 * log(r1)) * np.cos(2 * pi * r2)
                variables.append(mu + sigma * z0)
        
        return {
            'variables': variables[:n],
            'numeros_aleatorios': ri_df,
            'parametros': f'N(μ={mu},σ={sigma})',
            'media_teorica': mu,
            'varianza_teorica': sigma**2
        }
    
    def gamma(self, alpha, beta, n=1):
        """Distribución Gamma(α,β)"""
        ri_df = self.generador_ri.generar(n)
        variables = [-beta/alpha * log((1-ri)/(1+ri)) for ri in ri_df['Ri']]
        
        return {
            'variables': variables,
            'numeros_aleatorios': ri_df,
            'parametros': f'Gamma(α={alpha},β={beta})',
            'media_teorica': alpha * beta,
            'varianza_teorica': alpha * (beta**2)
        }
    
    def weibull(self, alpha, beta, y=0, n=1):
        """Distribución Weibull(α,β,γ)"""
        ri_df = self.generador_ri.generar(n)
        variables = [y + beta * (-log(1 - ri))**(1/alpha) for ri in ri_df['Ri']]
        
        media_teorica = y + beta * gamma_func(1 + 1/alpha)
        varianza_teorica = beta**2 * (gamma_func(1 + 2/alpha) - gamma_func(1 + 1/alpha)**2)
        
        return {
            'variables': variables,
            'numeros_aleatorios': ri_df,
            'parametros': f'Weibull(α={alpha},β={beta},γ={y})',
            'media_teorica': media_teorica,
            'varianza_teorica': varianza_teorica
        }