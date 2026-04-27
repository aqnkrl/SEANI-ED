import numpy as np

class SEANIEngine:
    """
    Motor matemático de SEANI-ED.
    Implementa métodos numéricos y modelos de ecuaciones diferenciales
    aplicados al análisis del desempeño académico de aspirantes.
    """

    def __init__(self, h=1.0):
        self.h = h  # Paso de tiempo (por defecto: 1 etapa)

    # =========================================================
    # MÉTODOS NUMÉRICOS
    # =========================================================

    def euler(self, f, y0, t_array):
        """
        Método de Euler (orden 1).
        y_{n+1} = y_n + h * f(t_n, y_n)
        """
        y = np.zeros(len(t_array))
        y[0] = y0
        for i in range(len(t_array) - 1):
            h = t_array[i + 1] - t_array[i]
            y[i + 1] = y[i] + h * f(t_array[i], y[i])
        return y

    def euler_mejorado(self, f, y0, t_array):
        """
        Método de Euler Mejorado / Heun (orden 2).
        Predictor:  y*_{n+1} = y_n + h * f(t_n, y_n)
        Corrector:  y_{n+1}  = y_n + (h/2) * [f(t_n, y_n) + f(t_{n+1}, y*_{n+1})]
        """
        y = np.zeros(len(t_array))
        y[0] = y0
        for i in range(len(t_array) - 1):
            h = t_array[i + 1] - t_array[i]
            k1 = f(t_array[i], y[i])
            y_pred = y[i] + h * k1                      # Predictor (Euler básico)
            k2 = f(t_array[i + 1], y_pred)              # Pendiente en el extremo
            y[i + 1] = y[i] + (h / 2) * (k1 + k2)      # Corrector (promedio)
        return y

    def rk4(self, f, y0, t_array):
        """
        Método de Runge-Kutta de orden 4.
        """
        y = np.zeros(len(t_array))
        y[0] = y0
        for i in range(len(t_array) - 1):
            h = t_array[i + 1] - t_array[i]
            k1 = h * f(t_array[i],           y[i])
            k2 = h * f(t_array[i] + h / 2,   y[i] + k1 / 2)
            k3 = h * f(t_array[i] + h / 2,   y[i] + k2 / 2)
            k4 = h * f(t_array[i] + h,        y[i] + k3)
            y[i + 1] = y[i] + (k1 + 2 * k2 + 2 * k3 + k4) / 6
        return y

    # =========================================================
    # MODELOS DE ECUACIONES DIFERENCIALES
    # =========================================================

    def modelo_separables(self, y0, k=0.15):
        """
        Ley del Olvido — Variables Separables
        ED:         dy/dt = -k·y
        Analítica:  y(t) = y0·e^(-kt)
        """
        def f(t, y): return -k * y
        def analitica(t): return y0 * np.exp(-k * t)
        return {
            'f': f, 'analitica': analitica,
            'desc_ed': f'dy/dt = -{k}·y',
            'desc_app': 'Pérdida de retención académica sin repaso (Ley del Olvido)',
            'etiqueta': 'Olvido (Separables)',
        }

    def modelo_lineal(self, y0, a=0.3, b=0.5):
        """
        Crecimiento Acumulativo — ED Lineal de Primer Orden
        ED:         dy/dt = a·y + b
        Analítica:  y(t) = (y0 + b/a)·e^(at) - b/a
        """
        def f(t, y): return a * y + b
        def analitica(t): return (y0 + b / a) * np.exp(a * t) - b / a
        return {
            'f': f, 'analitica': analitica,
            'desc_ed': f'dy/dt = {a}·y + {b}',
            'desc_app': 'Crecimiento acumulativo de conocimiento por módulo estudiado',
            'etiqueta': 'Crecimiento (Lineal)',
        }

    def modelo_bernoulli(self, y0, r=0.5, K=10.0):
        """
        Saturación Cognitiva — Ecuación Logística (caso Bernoulli)
        ED:         dy/dt = r·y·(1 - y/K)
        Analítica:  y(t) = K / (1 + ((K-y0)/y0)·e^(-rt))
        """
        def f(t, y): return r * y * (1 - y / K)
        def analitica(t):
            y0_safe = max(y0, 1e-6)
            return K / (1 + ((K - y0_safe) / y0_safe) * np.exp(-r * t))
        return {
            'f': f, 'analitica': analitica,
            'desc_ed': f'dy/dt = {r}·y·(1 - y/{K})',
            'desc_app': 'Saturación cognitiva: límite de aprendizaje por cansancio mental',
            'etiqueta': 'Saturación (Bernoulli)',
        }

    def modelo_homogeneas(self, y0, c=0.5):
        """
        Nivelación Académica — ED Homogénea
        ED:         dy/dt = y/t + c
        Analítica:  y(t) = C·t + c·t·ln(t)  donde C = y0/t0 - c·ln(t0)
        """
        def f(t, y):
            t = max(t, 0.1)
            return y / t + c

        def analitica(t_arr):
            result = np.zeros_like(t_arr, dtype=float)
            t0 = max(t_arr[0], 0.1)
            C = y0 / t0 - c * np.log(t0)
            for i, t in enumerate(t_arr):
                t = max(t, 0.1)
                result[i] = C * t + c * t * np.log(t)
            return result

        return {
            'f': f, 'analitica': analitica,
            'desc_ed': f'dy/dt = y/t + {c}',
            'desc_app': 'Nivelación: convergencia del puntaje del alumno al promedio grupal',
            'etiqueta': 'Nivelación (Homogénea)',
        }

    def modelo_exactas(self, y0, alpha=0.2):
        """
        Consistencia de Esfuerzo — ED Exacta
        ED exacta:  y·dy + alpha·t·dt = 0
        Forma ED:   dy/dt = -alpha·t / y
        Analítica:  y²(t) = y0² - alpha·t²  →  y(t) = sqrt(max(y0² - alpha·t², 0))
        """
        def f(t, y):
            if abs(y) < 1e-6:
                return 0.0
            return -alpha * t / y

        def analitica(t_arr):
            val = y0**2 - alpha * t_arr**2
            return np.sqrt(np.maximum(val, 0))

        return {
            'f': f, 'analitica': analitica,
            'desc_ed': f'y·dy + {alpha}·t·dt = 0',
            'desc_app': 'Consistencia: estabilidad del flujo de esfuerzo cognitivo',
            'etiqueta': 'Esfuerzo (Exactas)',
        }

    def modelo_factor_integrante(self, y0, p=0.3, q=1.5):
        """
        Factores Externos — ED Lineal con Factor Integrante
        ED:         dy/dt + p·y = q
        F.I.:       μ(t) = e^(pt)
        Analítica:  y(t) = (y0 - q/p)·e^(-pt) + q/p
        """
        def f(t, y): return -p * y + q

        def analitica(t): return (y0 - q / p) * np.exp(-p * t) + q / p

        return {
            'f': f, 'analitica': analitica,
            'desc_ed': f'dy/dt + {p}·y = {q}  (F.I.: μ=e^({p}t))',
            'desc_app': 'Impacto de estrés y factores externos en la retención',
            'etiqueta': 'Factores Externos (F. Integrante)',
        }

    def modelo_variacion_parametros(self, y0, omega=0.8):
        """
        Respuesta a Estímulos — ED cuya solución particular se obtiene por variación de parámetros
        ED:         dy/dt = -omega·sin(t)
        Analítica:  y(t) = y0 + omega·(cos(t) - 1)
        """
        def f(t, y): return -omega * np.sin(t)
        def analitica(t_arr): return y0 + omega * (np.cos(t_arr) - 1)
        return {
            'f': f, 'analitica': analitica,
            'desc_ed': f'dy/dt = -{omega}·sin(t)',
            'desc_app': 'Respuesta oscilatoria ante variación de dificultad de reactivos',
            'etiqueta': 'Respuesta (Variación de Parámetros)',
        }

    def modelo_laplace(self, y0, zeta=0.3, omega_n=1.0):
        """
        Análisis de Impulso — Transformada de Laplace
        Sistema de 2do orden subamortiguado:
        H(s) = ωn² / (s² + 2ζωn·s + ωn²)
        Respuesta al escalón (ζ < 1):
        y(t) = 1 - e^(-ζωnt)[cos(ωdt) + (ζ/√(1-ζ²))·sin(ωdt)]
        Escalada al rango [y0, 10].
        """
        omega_d = omega_n * np.sqrt(max(1 - zeta**2, 1e-6))

        def analitica(t_arr):
            resp = 1 - np.exp(-zeta * omega_n * t_arr) * (
                np.cos(omega_d * t_arr) +
                (zeta / np.sqrt(max(1 - zeta**2, 1e-6))) * np.sin(omega_d * t_arr)
            )
            return y0 + (10 - y0) * resp

        def f(t, y):
            eps = 1e-5
            t_s = max(t, eps)
            dy = (analitica(np.array([t_s + eps])) - analitica(np.array([t_s - eps]))) / (2 * eps)
            return float(dy[0])

        return {
            'f': f, 'analitica': analitica,
            'desc_ed': f'H(s) = {omega_n}²/(s²+2·{zeta}·{omega_n}·s+{omega_n}²)',
            'desc_app': 'Impacto de curso propedéutico intensivo (respuesta al escalón)',
            'etiqueta': 'Impulso (Laplace / 2do Orden)',
        }

    # =========================================================
    # MÉTODO PRINCIPAL
    # =========================================================

    def resolver_modelo(self, nombre_modelo, y0, n_puntos=8, params=None):
        """
        Resuelve el modelo con los 3 métodos numéricos y la solución analítica.
        Retorna dict con series de valores y metadatos.
        """
        if params is None:
            params = {}

        modelos = {
            'separables': lambda: self.modelo_separables(y0, **params),
            'lineales':   lambda: self.modelo_lineal(y0, **params),
            'bernoulli':  lambda: self.modelo_bernoulli(y0, **params),
            'homogeneas': lambda: self.modelo_homogeneas(y0, **params),
            'exactas':    lambda: self.modelo_exactas(y0, **params),
            'factor':     lambda: self.modelo_factor_integrante(y0, **params),
            'variacion':  lambda: self.modelo_variacion_parametros(y0, **params),
            'laplace':    lambda: self.modelo_laplace(y0, **params),
        }

        if nombre_modelo not in modelos:
            raise ValueError(f"Modelo '{nombre_modelo}' no reconocido.")

        config = modelos[nombre_modelo]()
        f = config['f']
        t = np.linspace(0.1, n_puntos, n_puntos)

        y_analitica = config['analitica'](t)
        y_euler     = self.euler(f, y0, t)
        y_euler_mej = self.euler_mejorado(f, y0, t)
        y_rk4       = self.rk4(f, y0, t)

        def clip(arr):
            return [max(0.0, min(10.0, round(float(v), 4))) for v in arr]

        return {
            't':              t,
            'analitica':      clip(y_analitica),
            'euler':          clip(y_euler),
            'euler_mejorado': clip(y_euler_mej),
            'rk4':            clip(y_rk4),
            'desc_ed':        config['desc_ed'],
            'desc_app':       config['desc_app'],
            'etiqueta':       config['etiqueta'],
        }

    def calcular_errores(self, analitica, euler, euler_mejorado, rk4):
        """MAE de cada método numérico respecto a la solución analítica."""
        a  = np.array(analitica)
        e1 = np.array(euler)
        e2 = np.array(euler_mejorado)
        e3 = np.array(rk4)
        return {
            'euler':          round(float(np.mean(np.abs(e1 - a))), 4),
            'euler_mejorado': round(float(np.mean(np.abs(e2 - a))), 4),
            'rk4':            round(float(np.mean(np.abs(e3 - a))), 4),
        }