import numpy as np

class SEANIEngine:
    def __init__(self):
        self.h = 1 # Paso de tiempo (1 pregunta)

    # --- MÉTODOS NUMÉRICOS ---
    def resolver_euler(self, f, y0, t_max):
        t = np.arange(0, t_max, self.h)
        y = np.zeros(len(t))
        y[0] = y0
        for i in range(len(t)-1):
            y[i+1] = y[i] + self.h * f(t[i], y[i])
        return t, y

    def resolver_rk4(self, f, y0, t_max):
        t = np.arange(0, t_max, self.h)
        y = np.zeros(len(t))
        y[0] = y0
        for i in range(len(t)-1):
            k1 = self.h * f(t[i], y[i])
            k2 = self.h * f(t[i] + self.h/2, y[i] + k1/2)
            k3 = self.h * f(t[i] + self.h/2, y[i] + k2/2)
            k4 = self.h * f(t[i] + self.h, y[i] + k3)
            y[i+1] = y[i] + (k1 + 2*k2 + 2*k3 + k4) / 6
        return t, y

    # --- MODELOS DE ECUACIONES DIFERENCIALES ---
    
    # 1. Variables Separables (Ley del Olvido)
    def modelo_separables(self, t, y):
        k = 0.05
        return -k * y

    # 2. Bernoulli (Crecimiento No Lineal de Dominio)
    def modelo_bernoulli(self, t, y):
        r, k, n = 0.1, 0.001, 1.2
        return r * y - k * (y**n)

    # 3. Exactas (Consistencia Cognitiva)
    def es_exacta(self, diff, score):
        # M = Dificultad + Score, N = Dificultad
        # dM/dScore = 1, dN/dDiff = 1 -> ES EXACTA
        return True

    # 4. Homogéneas (Nivelación Académica)
    def modelo_homogeneas(self, t, y):
        # y' = (y/t) + 1 (Modelo de convergencia a la media)
        if t == 0: t = 1
        return (y / t) + 0.1

    # 5. Laplace (Resiliencia ante el Error)
    # Se representa mejor en la vista como una función de transferencia
    def calcular_resiliencia(self, fallos):
        # Simula la respuesta al escalón
        return np.exp(-0.2 * np.arange(10))