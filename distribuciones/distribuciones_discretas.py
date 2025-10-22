from math import exp, factorial

class DistribucionesDiscretas:
    def __init__(self, generador_ri):
        self.generador_ri = generador_ri
    
    def uniforme_discreta(self, a, b, n=1):
        """Distribución Uniforme Discreta U(a,b)"""
        ri_df = self.generador_ri.generar(n)
        variables = [a + int((b - a + 1) * ri) for ri in ri_df['Ri']]
        
        media_teorica = (a + b) / 2
        varianza_teorica = ((b - a + 1)**2 - 1) / 12
        
        return {
            'variables': variables,
            'numeros_aleatorios': ri_df,
            'parametros': f'U({a},{b}) discreta',
            'media_teorica': media_teorica,
            'varianza_teorica': varianza_teorica
        }
    
    def bernoulli(self, p, n=1):
        """Distribución Bernoulli(p)"""
        ri_df = self.generador_ri.generar(n)
        variables = [1 if ri >= (1 - p) else 0 for ri in ri_df['Ri']]
        
        return {
            'variables': variables,
            'numeros_aleatorios': ri_df,
            'parametros': f'Bernoulli(p={p})',
            'media_teorica': p,
            'varianza_teorica': p * (1 - p)
        }
    
    def binomial(self, n_trials, p, n=1):
        """Distribución Binomial(n,p)"""
        resultados = []
        for _ in range(n):
            ri_df = self.generador_ri.generar(n_trials)
            exitos = sum([1 if ri >= (1 - p) else 0 for ri in ri_df['Ri']])
            resultados.append(exitos)
        
        ri_final = self.generador_ri.generar(n)
        
        return {
            'variables': resultados,
            'numeros_aleatorios': ri_final,
            'parametros': f'Binomial(n={n_trials}, p={p})',
            'media_teorica': n_trials * p,
            'varianza_teorica': n_trials * p * (1 - p)
        }
    
    def poisson(self, lambd, n=1):
        """Distribución Poisson(λ)"""
        ri_df = self.generador_ri.generar(n)
        variables = []
        
        for ri in ri_df['Ri']:
            k = 0
            p = exp(-lambd)
            F = p
            
            while ri > F:
                k += 1
                p *= lambd / k
                F += p
            
            variables.append(k)
        
        return {
            'variables': variables,
            'numeros_aleatorios': ri_df,
            'parametros': f'Poisson(λ={lambd})',
            'media_teorica': lambd,
            'varianza_teorica': lambd
        }