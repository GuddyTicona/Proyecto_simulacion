class MultiplicadorConstante:
    def __init__(self, semilla: int, k: int, n: int):
        self.x = semilla
        self.k = k
        self.n = n
        self.d = max(len(str(semilla)), 4)  # Número de dígitos a usar

    def generar_tabla(self):
        resultados = []

        for i in range(1, self.n + 1):
            multiplicacion = self.x * self.k  # Xi * k
            mult_str = str(multiplicacion).zfill(2 * self.d)  # Completar con ceros para extraer dígitos centrales

            # Extraer dígitos centrales
            inicio = (len(mult_str) - self.d) // 2
            x_centro = int(mult_str[inicio:inicio + self.d])

            # Ri normalizado
            r = x_centro / (10 ** self.d)

            # Guardar resultados
            resultados.append({
                "Iteración": i,
                "Xi": str(self.x).zfill(self.d),
                "k*Xi": str(multiplicacion).zfill(2 * self.d),  # Se ve en la tabla
                "Dígitos del centro": str(x_centro).zfill(self.d),
                "Ri": r
            })

            # Preparar siguiente Xi
            self.x = x_centro

        return resultados
