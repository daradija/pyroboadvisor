import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import yfinance as yf

# 1. Descargar datos del S&P 500 del último año
sp500_data = yf.download("^GSPC", period="10y", interval="1d")

# 2. Aplicar logaritmo natural a los precios de cierre
sp500_data['ln_Close'] = np.log(sp500_data['Close'])

# 3. Preparar los datos para la regresión
# Convertir la fecha en un valor numérico (días transcurridos desde la primera fecha)
sp500_data['Days'] = (sp500_data.index - sp500_data.index[0]).days
X = sp500_data['Days'].values.reshape(-1, 1)  # Variable independiente: tiempo
y = sp500_data['ln_Close'].values             # Variable dependiente: ln(Close)

retornoLog=np.log(y[1:]/y[:-1])
# media del retorno logarítmico
media_retorno_log = np.mean(retornoLog)
# desviación estándar del retorno logarítmico
desviacion_retorno_log = np.std(retornoLog)
sharpe_log = media_retorno_log / desviacion_retorno_log * 252/ np.sqrt(252)  # Anualizado, asumiendo 252 días de trading al año

print("Sharpe Log del SP500:", sharpe_log)

# Ajustar el modelo de regresión lineal
# Usa numpy
y_pred = np.polyval(np.polyfit(X.flatten(), y, 1), X.flatten())

# model = LinearRegression()
# model.fit(X, y)
# y_pred = model.predict(X)

# 4. Graficar la serie y la recta de regresión
plt.figure(figsize=(10, 5))
# Graficar ln(Close) conectado con una línea
plt.plot(sp500_data.index, sp500_data['ln_Close'], label='ln(Close)', color='blue')
# Graficar la recta de regresión
plt.plot(sp500_data.index, y_pred, label='Regresión lineal', color='red')
plt.xlabel('Fecha')
plt.ylabel('ln(Close)')
plt.title('Evolución del ln(Close) del S&P 500 (último año) con regresión')
plt.ylim(bottom=0)  # El eje y comienza en 0
plt.legend()
plt.grid(True)
plt.show()

# Mostrar coeficientes del modelo (opcional)
slope = model.coef_[0]
intercept = model.intercept_
r2 = model.score(X, y)
print("Pendiente (slope):", slope)
print("Intersección (intercept):", intercept)
print("R²:", r2)
