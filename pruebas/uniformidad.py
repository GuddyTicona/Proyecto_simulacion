import math
import scipy.stats as stats
import numpy as np

def prueba_uniformidad(numeros, alpha=0.05, k=10):
    """
    Prueba de uniformidad (Chi-cuadrado) según las fórmulas proporcionadas
    H0: Los números ri están uniformemente distribuidos
    H1: Los números ri no están uniformemente distribuidos
    """
    n = len(numeros)
    
    # Crear intervalos
    intervalos = np.linspace(0, 1, k + 1)
    
    # Calcular frecuencias observadas
    frecuencias_obs, _ = np.histogram(numeros, bins=intervalos)
    
    # Frecuencia esperada
    frecuencia_esp = n / k
    
    # Calcular chi-cuadrado
    chi_cuadrado = 0
    tabla_frecuencias = []
    
    for i in range(k):
        intervalo_str = f"({intervalos[i]:.3f} - {intervalos[i+1]:.3f})"
        fo = frecuencias_obs[i]
        fe = frecuencia_esp
        diff = fo - fe
        diff_cuad = diff ** 2
        termino = diff_cuad / fe
        
        chi_cuadrado += termino
        
        tabla_frecuencias.append({
            'intervalo': intervalo_str,
            'frecuencia_observada': fo,
            'frecuencia_esperada': fe,
            'diferencia': diff,
            'diferencia_cuadrada': diff_cuad,
            'termino_chi': termino
        })
    
    # Calcular chi-cuadrado crítico
    chi_critico = stats.chi2.ppf(1 - alpha, k - 1)
    
    # Verificar hipótesis
    acepta_hipotesis = chi_cuadrado < chi_critico
    
    return {
        "chi_cuadrado": chi_cuadrado,
        "chi_critico": chi_critico,
        "acepta_hipotesis": acepta_hipotesis,
        "tabla_frecuencias": tabla_frecuencias,
        "n": n,
        "k": k,
        "alpha": alpha
    }