# ------------------ PRODUCTOS MEDIOS ------------------
class ProductosMedios:
    def __init__(self, semilla1: int, semilla2: int, n: int):
        self.x = semilla1
        self.y = semilla2
        self.n = n
        self.d = max(len(str(semilla1)), len(str(semilla2)), 4)  # Al menos 4 dígitos

    def generar_tabla(self):
        resultados = []

        for i in range(1, self.n + 1):
            producto = self.x * self.y
            producto_str = str(producto).zfill(2 * self.d)
            inicio = (len(producto_str) - self.d) // 2
            x_centro = int(producto_str[inicio:inicio + self.d])
            r = x_centro / (10 ** self.d)

            resultados.append({
                "Iteración": i,
                "X": str(self.x).zfill(self.d),
                "Y": str(self.y).zfill(self.d),
                "Producto": str(producto).zfill(2*self.d),
                "Dígitos del centro": str(x_centro).zfill(self.d),
                "Ri": r
            })

            # Preparar siguiente iteración
            self.x, self.y = self.y, x_centro

        return resultados
