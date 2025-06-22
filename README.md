# PyRoboAdvisor

Para conocer el proyecto y la filosofía detrás de PyRoboAdvisor, visita el siguiente enlace:
# [PyRoboAdvisor](https://pyroboadvisor.com)

# Pre-requisitos
Para ejecutar PyRoboAdvisor, debes comprar una licencia de la estrategia A1.
Tras la compra llega una clave por correo electrónico.

Actualmente solo está operativo el modo de simulación. 
En nuestro roadmap está previsto implementar un driver de acceso a Interactive Brokers, que es el broker que utilizamos para operar.

Por lo tanto si quieres probar PyRoboAdvisor, de forma automatizada debes tener una cuenta de Interactive Brokers.

# Instalación

Instala python 3.10 o superior.

Descarga el código fuente de PyRoboAdvisor desde el repositorio oficial de GitHub:

```bash
git clone https://github.com/daradija/pyroboadvisor.git
cd pyroboadvisor
```

Edita el archivo sample.py y añade tu email y clave de licencia:

```python
p={
    "fecha_inicio": "2019-01-01",
    "fecha_fin": "2025-12-31",
    "money": 100000,
    "numberStocksInPortfolio": 10,
    "orderMarginBuy": 0.005,  # margen de ordenes de compra y venta
    "orderMarginSell": 0.005,  # margen de ordenes de compra y venta
    "apalancamiento": 10 / 6,  # apalancamiento de las compras
    "ring_size": 240,
    "rlog_size": 24,
    "cabeza": 5,
    "seeds": 100,
    "percentil": 95,
    "prediccion": 1,

    "key": "",
    "email": "",
}
```

Instala las dependencias necesarias ejecutando el siguiente comando:

```bash
pip install -r requirements.txt
``` 

Sin funciona prueba:
```bash
python3 -m pip install -r requirements.txt
```

# Ejecución
Para ejecutar PyRoboAdvisor, utiliza el siguiente comando:
```bash
python3 sample.py
````

Por consola se muestra el progreso de la simulación y al finalizar se genera un 
gráfico con el resultado de la simulación.

```console
2024-04-30 Value: $317250 $43055 ENPH/124 INCY/264 PODD/606 MRNA/720 PCG/1278 RMD/18 TSLA/206 
TAE: 30.97% DDPP: 77.92%/77.77% Comisión: $0.00
2024-05-01 Value: $316576 $43055 ENPH/124 INCY/264 PODD/606 MRNA/720 PCG/1278 RMD/18 TSLA/206 
TAE: 30.88% DDPP: 75.42%/77.76% Comisión: $0.00
2024-05-02 Value: $329023 $43055 ENPH/124 INCY/264 PODD/606 MRNA/720 PCG/1278 RMD/18 TSLA/206 
TAE: 32.04% DDPP: 87.50%/77.77% Comisión: $0.00
2024-05-03 Value: $330670 $43055 ENPH/124 INCY/264 PODD/606 MRNA/720 PCG/1278 RMD/18 TSLA/206 
TAE: 32.17% DDPP: 87.92%/77.79% Comisión: $0.18
2024-05-06 Value: $331146 $25202 ENPH/124 INCY/264 PODD/606 MRNA/720 PAYC/105 PCG/1278 RMD/18 TSLA/206 
TAE: 32.14% DDPP: 88.75%/77.80% Comisión: $0.00
2024-05-07 Value: $334058 $25202 ENPH/124 INCY/264 PODD/606 MRNA/720 PAYC/105 PCG/1278 RMD/18 TSLA/206 
TAE: 32.39% DDPP: 90.42%/77.81% Comisión: $0.00
2024-05-08 Value: $327842 $25202 ENPH/124 INCY/264 PODD/606 MRNA/720 PAYC/105 PCG/1278 RMD/18 TSLA/206 
TAE: 31.79% DDPP: 85.83%/77.82% Comisión: $150.57
2024-05-09 Value: $329793 $100297 AMD/91 ENPH/124 INCY/264 PODD/606 PAYC/105 PCG/1278 RMD/18 TSLA/206 
TAE: 31.95% DDPP: 86.67%/77.83% Comisión: $0.00
2024-05-10 Value: $321358 $100297 AMD/91 ENPH/124 INCY/264 PODD/606 PAYC/105 PCG/1278 RMD/18 TSLA/206 
````
Durante la simulación se muestra:
- La fecha, en formato `YYYY-MM-DD`.
- El valor total de la cartera.
- El valor en efectivo disponible.
- Las acciones en la cartera, con su cantidad.
- El TAE (Tasa Anual Equivalente) de la cartera desde el comienzo de la simulación.
- El draw down por percentiles, tanto el instantaneo como el medio.

El DDPP (Draw Down por Percentiles) es una medida del riesgo de la cartera, que me he inventado. Un número mayor es mejor. Por ejemplo un 100% indica que el valor de tasación está por encima del 100% de los últimos 240 días (1 año).

![](assets/17506106676794.jpg)
Gráfica mostrada al final, comparando la estrategia con el índice de referencia.

# Parámetros

Si deseas afinar el algoritmo, puedes modificar los parámetros en el diccionario `p` del archivo `sample.py`.

## Periodo de simulación
Los parámetros `fecha_inicio` y `fecha_fin` definen el periodo de simulación.

Para especificar la cantidad de dolares iniciales, utiliza el parámetro `money`.

Para modelar el tamañano de acciones en la cartera, utiliza el parámetro `numberStocksInPortfolio`.

Cada vez que el sistema decide comprar o vender acciones se utiliza el precio de apertura mas un margen. Para ello, utiliza los parámetros `orderMarginBuy` y `orderMarginSell`. Que están en tantos por 1. Por ejemplo, si quieres un margen del 0.5% para las órdenes de compra y venta, debes establecer `orderMarginBuy` y `orderMarginSell` a 0.005.
El objetivo es introducir las ordenes en el book order y pagar menos comisiones.

Si estos valores suben, el sistema compra y vende menos vece, pero el rendimiento no se ve muy mermado. A partir del 5% he observado que compra tan poco que deja de operar. Pagar menos comisiones por hacer menos operaciones a cambio de esperar mas días para ver una rotación. 

Jugar con una asimetría conduce a resultados curiosos.

Si deseas utilizar el apalancamiento que ofrece el broker, puedes establecer el parámetro `apalancamiento`. Un valor mayor de 1 indica que se está utilizando apalancamiento. Y menor de 1 indica lo contrario. 

El resto de parámetros son internos del algoritmo y no es necesario modificarlos, a menos que sepas lo que estás haciendo:

`ring_size` es una ventana para suavizar los precios de las acciones y evitar el ruido de las fluctuaciones diarias. Un valor de 240 es adecuado para un periodo de 1 año con datos diarios. Observarás que si lo cambias suele bajar el desempeño. Ya que la bolsa suele tener un ciclos de 240 días laborales por año.

Ahora se utiliza otro conjunto de días para establecer la tendencia de los precios, que es `rlog_size`. Este parámetro define el número de días que se utilizan para calcular la tendencia de los precios. Un valor de 24 es aproximadamente 1 mes de datos. Un periodo mas pequeño puede detectar tendencias a corto plazo, mientras que un periodo mas grande puede detectar tendencias a largo plazo.

Se realizan del orden de 'seeds' estimadores. Poner mas seeds puede mejorar la precisión de las predicciones, pero también aumenta el tiempo de ejecución. Un valor de 100 es un buen punto de partida.

Los estimadores usan un número de acciones como referencia ('cabeza') para establecer el estimador.  

El parámetro mas poderoso es el `percentil`, en teoría se tendría que usar el percentil 50, pero he observado que el percentil 95 da mejores resultados. Es decir, hay que ser obtimista con respecto a las predicciones. 

El sistema por defecto realiza una predicción de 1 día, es decir, el sistema predice el precio de la acción al día siguiente. Si deseas cambiar esto, puedes modificar el parámetro `prediccion`. Por ejemplo, si quieres predecir el precio a 5 días vista, establece `prediccion` a 5, 10, el número ha de ser menor que la ventana `rlog_size`. Ya que la predicción consume parte de esta ventana. No pongas mas de un 50% del valor de `rlog_size`.