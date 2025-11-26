import numpy as np
from scipy import stats

def distribucion_uniforme_discreta_pmf(x, a, b):
    """Función de masa de probabilidad para distribución uniforme discreta"""
    return np.where((x >= a) & (x <= b), 1/(b - a + 1), 0)

def distribucion_uniforme_discreta_cdf(x, a, b):
    """Función de distribución para distribución uniforme discreta"""
    return np.where(x < a, 0, np.where(x <= b, (np.floor(x) - a + 1)/(b - a + 1), 1))

def distribucion_bernoulli_pmf(x, p):
    """Función de masa de probabilidad para distribución Bernoulli"""
    return np.where(x == 0, 1-p, np.where(x == 1, p, 0))

def distribucion_bernoulli_cdf(x, p):
    """Función de distribución para distribución Bernoulli"""
    return np.where(x < 0, 0, np.where(x < 1, 1-p, 1))

def distribucion_binomial_pmf(x, n, p):
    """Función de masa de probabilidad para distribución binomial"""
    return stats.binom.pmf(x, n, p)

def distribucion_binomial_cdf(x, n, p):
    """Función de distribución para distribución binomial"""
    return stats.binom.cdf(x, n, p)

def distribucion_poisson_pmf(x, lam):
    """Función de masa de probabilidad para distribución Poisson"""
    return stats.poisson.pmf(x, lam)

def distribucion_poisson_cdf(x, lam):
    """Función de distribución para distribución Poisson"""
    return stats.poisson.cdf(x, lam)