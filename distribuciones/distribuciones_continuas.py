import numpy as np
from scipy import stats
import math

def distribucion_uniforme_pdf(x, a, b):
    """Función de densidad de probabilidad para distribución uniforme"""
    return np.where((x >= a) & (x <= b), 1/(b-a), 0)

def distribucion_uniforme_cdf(x, a, b):
    """Función de distribución acumulativa para distribución uniforme"""
    return np.where(x < a, 0, np.where(x <= b, (x-a)/(b-a), 1))

def distribucion_erlang_pdf(x, k, lam):
    """Función de densidad para distribución Erlang (caso especial de Gamma)"""
    return stats.gamma.pdf(x, k, scale=1/lam)

def distribucion_erlang_cdf(x, k, lam):
    """Función de distribución para distribución Erlang"""
    return stats.gamma.cdf(x, k, scale=1/lam)

def distribucion_exponencial_pdf(x, lam):
    """Función de densidad para distribución exponencial"""
    return lam * np.exp(-lam * x)

def distribucion_exponencial_cdf(x, lam):
    """Función de distribución para distribución exponencial"""
    return 1 - np.exp(-lam * x)

def distribucion_gamma_pdf(x, alpha, beta):
    """Función de densidad para distribución gamma"""
    return stats.gamma.pdf(x, alpha, scale=beta)

def distribucion_gamma_cdf(x, alpha, beta):
    """Función de distribución para distribución gamma"""
    return stats.gamma.cdf(x, alpha, scale=beta)

def distribucion_normal_pdf(x, mu, sigma):
    """Función de densidad para distribución normal"""
    return stats.norm.pdf(x, mu, sigma)

def distribucion_normal_cdf(x, mu, sigma):
    """Función de distribución para distribución normal"""
    return stats.norm.cdf(x, mu, sigma)

def distribucion_weibull_pdf(x, alpha, beta, gamma=0):
    """Función de densidad para distribución Weibull"""
    return stats.weibull_min.pdf(x - gamma, alpha, scale=beta)

def distribucion_weibull_cdf(x, alpha, beta, gamma=0):
    """Función de distribución para distribución Weibull"""
    return stats.weibull_min.cdf(x - gamma, alpha, scale=beta)