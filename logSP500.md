El script logSP500.py de Python que se utiliza para:

- Imprimir el SP500 en escala logarítmica junto a recta de regresión. Pretende demostrar que una escala logaritmica aplicada al dinero o a los índices se ajusta mejor a la realidad.

- Si no se aplica una escala logarítmica se tiene siempre la impresión de que el índice tiene un crecimiento exponencial, que es una burbuja y está a punto de explotar.

- Por otro lado se calcula una versión corregida del Indice Sharpe, su salida es por consola. La corrección consiste en aplicar la escala logarítmica en los retornos diarios. 

- El índice sharpe logaritmico es un número que sirve para comparar estrategias. Mas alto es mejor. Y tiene en cuenta tanto los retornos (numerador) como la volatilidad (denominador), mediante la desviación típica ya que está en el mismo orden de magnitud que los retornos. Y por lo tanto se anulan las unidades ($/$) y es un índice. 

