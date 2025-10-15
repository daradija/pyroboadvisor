# **Instalación PyRoboAdvisor en macOS**

# Paso 1º: Instalación

Buscas en internet « **visual studio code mac** »\
<https://code.visualstudio.com/download>\
![](assets/17604711438910.jpg)
![](assets/17604711503477.jpg)



Cuando se te descargue debes **arrastrar** el zip que se ha descargado,
desde **descargas** -\> a -\> **aplicaciones**.
![](assets/17604711621937.jpg)

Aquí:\
![](assets/17604711659843.jpg)

Una vez ahí le das doble click
![](assets/17604711703638.jpg)

Le das a sí.\
![](assets/17604711765906.jpg)

Se te abrirá visual studio code.
![](assets/17604711844014.jpg)

Si no te aparece con el mismo color que yo tengo no te preocupes.

Le vas a dar aquí debajo, en la tuerca:\
Tuerca - Themes - Color Theme

Y te pones **Quiet Light** o el que prefieras.\
![](assets/17604711915523.jpg)

Ahora vamos a poner el instalador de paquetes de mac, debes abrir un
terminal (ctrol + J) /Ó/ (arriba) Terminal - Nuevo Terminal.\
![](assets/17604711982510.jpg)

Ahora pones en el terminal el siguiente comando:\
`/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"`
![](assets/17604712087826.jpg)

Ahora vamos a instalar python con:\
`brew install python@3.11`
![](assets/17604712134865.jpg)

Ahora vamos a descargar el código de github con:\
`git clone https://github.com/daradija/pyroboadvisor.git`

Luego deberás poner este comando, que te situará en la carpeta que
acabamos de importar.\
`cd pyroboadvisor`
![](assets/17604712219771.jpg)

Ahora debes poner el siguiente comando, este ejecutará un script que
creará un entorno virtual para evitar conflictos con otras dependencias
de Python, el comando es:

`source createVenv`
![](assets/17604712446029.jpg)

Ahora hacemos (para ir al directorio driver):

`cd driver`

Luego:

`pip install -r requirements.txt`

Finalmente volvemos al directorio anterior con:

`cd ..`
![](assets/17604712516134.jpg)
![](assets/17604712550979.jpg)

# Paso 2º: Ejecutar simulación

Debes escribir:

`python ./sample_b`

Te pedirá Email y clave (key, te llegó a tu correo).  
![](assets/17604712642268.jpg)

Luego te pedirá el modo, como vamos a hacer una simulación ponemos «
**0** ».
![](assets/17604712726772.jpg)

Finalmente te pedirá el apalancamiento, puedes poner « **1.6** » por
ejemplo.
![](assets/17604713159055.jpg)

Seguidamente, empezará a ejecutarse, no te preocupes si tarda.
![](assets/17604713197812.jpg)

Cuando empiece a calcular por días, saldrán TAEs enormes, no te
preocupes, piensa que está extrapolando los resultados de los primeros
días a todo un año (TAE). Luego se estabiliza.
![](assets/17604713362054.jpg)

Finalmente, tal y como hemos indicado, saldrán 2 gráficos.
![](assets/17604713445277.jpg)

![](assets/17604713588636.jpg)

En el primero veríamos el valor vs el del SP500, y en el segundo una
regresión lineal de la nube de puntos que contrapone las rentabilidades
del SP500 vs tu simulación.   

