import math
import scipy.stats as stats
import numpy as np

def prueba_varianza(numeros, alpha=0.05):
    """
    Prueba de varianza 
    H0: σ² = 1/12
    H1: σ² ≠ 1/12
    """
    n = len(numeros)
    
    # Calcular la media
    media = sum(numeros) / n
    
    # Calcular la varianza (V(r))
    suma_cuadrados = sum((x - media) ** 2 for x in numeros)
    varianza = suma_cuadrados / (n - 1)
    
    # Calcular límites de aceptación
    chi2_alpha_2 = stats.chi2.ppf(1 - alpha/2, n-1)
    chi2_1_minus_alpha_2 = stats.chi2.ppf(alpha/2, n-1)
    
    limite_inferior = chi2_1_minus_alpha_2 / (12 * (n - 1))
    limite_superior = chi2_alpha_2 / (12 * (n - 1))
    
    # Verificar hipótesis
    acepta_hipotesis = limite_inferior <= varianza <= limite_superior
    
    return {
        "varianza": varianza,
        "limite_inferior": limite_inferior,
        "limite_superior": limite_superior,
        "acepta_hipotesis": acepta_hipotesis,
        "n": n,
        "suma_cuadrados": suma_cuadrados,
        "chi2_alpha_2": chi2_alpha_2,
        "chi2_1_minus_alpha_2": chi2_1_minus_alpha_2
    }