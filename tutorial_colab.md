# **SIMULACIÓN EN COLAB (\~2 minutos instalación)**

La instalación en colab para poder simular es MUY SENCILLA, cosa de 2
minutos. Colab es un **entorno gratuito para programación colaborativa**
» Google Colab (Abrev. colab).

¿En qué consiste lo que vas a hacer? En vez de usar PyRoboAdvisor en tu
ordenador, lo usarás en un entorno virtual de la nube, en drive.

**Paso 0 (opcional)**: si ya tienes cuenta de google, este paso no es
necesario. Si quieres crear una nueva cuenta para tenerlo más ordenado
también puedes hacer este paso.

**Paso 1º**: Instalar Google Colab (es añadir una extensión dentro de
Drive).

**Paso 2º**: Instalar PyRoboAdvisor (es irse al github, darle a un botón
en colab, ejecutar 2 celdas de código que te aparecerán en colab, darle
a ejecutar y listo).

Una vez hecho esto, estarás listo para empezar.

#### **PASO 0º (OPCIONAL) Crear cuenta de google específica (por si quisieras tenerlo separado de tu drive personal).**

En tu chrome, abres incógnito (abrimos incógnito para que tu sesión
iniciada no interfiera a la hora de crear una nueva cuenta).   
![](assets/17604706264319.jpg)


Buscas en google «crear correo google»

Nos abrirá « <https://support.google.com/mail/answer/56256?hl=es> ».  
![](assets/17604706526930.jpg)

![](assets/17604706612698.jpg)

![](assets/17604706677973.jpg)



Desde aquí ya simplemente rellenas y creas tu cuenta.  

![](assets/17604706856322.jpg)


Una vez la crees, cierra la pestaña incógnito, seguiremos y abre una
pestaña normal.

#### **PASO 1º: Instalar Collaboratory**

Nos venimos a este link <https://drive.google.com/drive/my-drive>

![](assets/17604706956628.jpg)


Arriba a la derecha asegúrate de que estás en la cuenta de google en la
que quieres estar.

![](assets/17604707079491.jpg)


Ahora le vas a dar a «+ Nuevo»

![](assets/17604707158548.jpg)


Se te abrirá esto:

![](assets/17604707222778.jpg)


En el buscador de arriba debes escribir: « Colaboratory »

![](assets/17604707305510.jpg)


Le das a instalar

![](assets/17604707419473.jpg)


Ahora le das a « Continuar ».

![](assets/17604707487000.jpg)


Le das a continuar

![](assets/17604707551464.jpg)


Se te empezará a instalar:

![](assets/17604707627379.jpg)


Cuando finalice ( \~5 segundos ) le das a:

![](assets/17604707703354.jpg)


Cierras:

![](assets/17604707760237.jpg)


#### **PASO 2º Usar PyRoboAdvisor con colab:**

Ahora abrimos el github en otra pestaña «
<https://github.com/daradija/pyroboadvisor> »

![](assets/17604707834461.jpg)


Ahora puedes o buscar el archivo correspondiente a tu licencia o darle
directamente a los links de abajo:

Si tu licencia es de la serie A debes abrir este:
![](assets/17604708015316.jpg)

<https://github.com/daradija/pyroboadvisor/blob/main/colab.ipynb>

Si tu licencia es de la serie B debes abrir este:
![](assets/17604708087115.jpg)

<https://github.com/daradija/pyroboadvisor/blob/main/colab_b.ipynb>

Para ambos casos se abrirá algo muy parecido, si te fijas al abrir habrá
2 celdas de código:   

![](assets/17604708215833.jpg)


Arriba saldrá esto, debes darle para abrirlo en colab.   

![](assets/17604708337640.jpg)


Se nos abrirá esto:   

![](assets/17604708438083.jpg)


Aquí vamos a ejecutar ambas celdas ¿cómo?\
Forma 1º: darle a « Ejecutar todas » (arriba).  

![](assets/17604708514173.jpg)



Forma 2º: Pulsamos « Ctrl + F9 » que ejecuta ambas directamente.\
Forma 3º: Posicionamos el ratón encima de ambas celdas y le damos al
play en cada una de ellas.

Al tratar de ejecutar saldrá esto, le das a « Ejecutar de todos modos »:

Es una advertencia protocolaria típica que sale al ejecutar cualquier
script de colab. No te preocupes.\
Si quieres, puedes auditar el código completo en
<https://github.com/daradija/pyroboadvisor>\
Si eres un fanático del orden / seguridad, puedes hacer el PASO 0º para
que así puedas hacerlo en una cuenta de google nueva y vacía.   

![](assets/17604708948941.jpg)


Ahora en la segunda celda, te pedirá el Email y la Licencia (Key),
deberás ponerla.\
Metes tu Email , pulsas ENTER.\
Metes tu Licencia (Key) (te la han enviado al correo cuando compraste),
pulsas ENTER.

![](assets/17604709146371.jpg)

![](assets/17604709146371.jpg)

![](assets/17604709489790.jpg)


Te saldrán varias opciones, desde aquí puedes simular, pon **0** y pulsa
ENTER.

![](assets/17604709707002.jpg)


Si quieres ver una gráfica al final de la simulación, pon « **s** », si no
pon « n ».

Aquí ahora pon el apalancamiento, pon por ejemplo « **1.6** » y dale a
ENTER.

![](assets/17604709979221.jpg)


¡¡¡Seguidamente se te empezará a ejecutar!!! La primera vez tarda
especialmente más.

Te mostrará 2 gráficos, en este caso con la estrategia A2.\
**En el primero** veríamos el valor de lo invertido a lo largo del
tiempo (para una cantidad genérica 100.000 dólares).\
**En el segundo** vemos una regresión lineal en la que podemos apreciar
la correlación con el SP500 y su pendiente (1,68 en este caso).


![](assets/17604710132971.jpg)


![](assets/17604710171071.jpg)

