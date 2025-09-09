# ------------------ CUADRADOS MEDIOS ------------------
class CuadradosMedios:
    def __init__(self, semilla: int, n: int):
        if len(str(semilla)) < 4:
            raise ValueError("La semilla debe tener al menos 4 dígitos")
        self.semilla = semilla
        self.n = n
        self.d = 4  # Siempre extraer 4 dígitos centrales

    def generar_tabla(self):
        resultados = []
        x = self.semilla

        for i in range(1, self.n + 1):
            x_cuadrado = x ** 2
            x_cuadrado_str = str(x_cuadrado).zfill(8)  # Siempre 8 dígitos
            inicio = (len(x_cuadrado_str) - self.d) // 2
            x_centro = int(x_cuadrado_str[inicio:inicio + self.d])
            r = x_centro / 10000

            resultados.append({
                "Iteración": i,
                "Xi-1": str(x).zfill(self.d),
                "Xi^2": str(x_cuadrado).zfill(8),
                "Xi": str(x_centro).zfill(self.d),
                "Ri": r
            })

            x = x_centro

        return resultados
