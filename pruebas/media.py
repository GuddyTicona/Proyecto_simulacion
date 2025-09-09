import math
import scipy.stats as stats

def prueba_medias(numeros, alpha=0.05):
    """
    Prueba de medias
    H0: μ = 0.5
    H1: μ ≠ 0.5
    """
    n = len(numeros)
    
    # Calcular la media (F)
    media = sum(numeros) / n
    
    # Calcular límites de aceptación
    z_alpha_2 = stats.norm.ppf(1 - alpha/2)
    limite_inferior = 0.5 - z_alpha_2 * (1 / math.sqrt(12 * n))
    limite_superior = 0.5 + z_alpha_2 * (1 / math.sqrt(12 * n))
    
    # Verificar hipótesis
    acepta_hipotesis = limite_inferior <= media <= limite_superior
    
    return {
        "media": media,
        "limite_inferior": limite_inferior,
        "limite_superior": limite_superior,
        "acepta_hipotesis": acepta_hipotesis,
        "n": n,
        "z_alpha_2": z_alpha_2
    }