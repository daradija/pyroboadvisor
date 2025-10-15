# **Instalación PyRoboAdvisor en Windows10**

# Paso 1º: Instalar «Python»

Pones en el buscador « microsoft store »\
![](assets/17604713979727.jpg)

Y le das a este:\
![](assets/17604714004320.jpg)

En el buscador pones « python 3.11 »
![](assets/17604714042298.jpg)

Y te pones este:\
![](assets/17604714078101.jpg)

Le das click a **Obtener**\
![](assets/17604714112566.jpg)

Ahora en nuestro buscador de internet, buscamos « visual studio code »\
<https://code.visualstudio.com/download>
![](assets/17604714182553.jpg)
![](assets/17604714238033.jpg)

Se nos empezará a descargar\

Abre el instalador, dale a todo a siguiente.

# Paso 2º: Instalar «GIT»

Escribe en el buscador « download git »\
<https://git-scm.com/downloads>\
![](assets/17604714616084.jpg)

Le damos a **Windows**\
![](assets/17604714651541.jpg)

Le das aquí: **Git for Windows/x64 Setup**\
![](assets/17604714679490.jpg)

Abre el instalador que acabas de descargar, y dale todo a siguiente
(Next), no hay que cambiar nada.\
![](assets/17604714727064.jpg)
![](assets/17604714773687.jpg)

Se te instalará correctamente\
![](assets/17604714822508.jpg)

Dale a **Finish**\
![](assets/17604714867452.jpg)

# Paso 3º: Instalar Visual Studio Code

Busca en google « visual studio code »\
![](assets/17604714926089.jpg)

Te llevará aquí, le das a <https://code.visualstudio.com/>
![](assets/17604714987350.jpg)

Cuando se termine de descargar, das click al instalador, le das todo a
siguiente.\
![](assets/17604715161919.jpg)
![](assets/17604715193759.jpg)
![](assets/17604715239384.jpg)

# Paso 4º: Terminar instalación

Abre el Visual Studio Code

Le vas a dar a Extensiones y vas a añadir « Python » de Microsoft\
![](assets/17604715311130.jpg)

Ahora vas a pulsar ctrol + J, para abrir un terminal (También puedes
arriba dándole a Terminal » New Terminal).

Ahora vamos a descargar el código fuente de PyRoboAdvisor desde el
repositorio oficial de GitHub:

Escribe en el terminal:

`git clone <https://github.com/daradija/pyroboadvisor.git>`

`cd pyroboadvisor`
![](assets/17604715447554.jpg)

Ahora vas a poner este comando para crear un entorno virtual para que no
tenga conflictos con otras dependencias de python:  
`python3 -m venv venv`

Luego pondrás en el terminal

`venv\Scripts\activate`  

![](assets/17604717104072.jpg)


Vamos a abrir el proyecto\

![](assets/17604717643745.jpg)
![](assets/17604717751058.jpg)


Abrimos sample_b.py\
![](assets/17604717949845.jpg)

Ahora le vas a dar aquí:\
![](assets/17604718020510.jpg)

En el buscador que te va a aparecer, le vas a dar a « Python: Select
Interpreter »\
![](assets/17604718081772.jpg)

De entre las opciones que te saldrán, deberás darle a la que aparece con
(venv)\
![](assets/17604718217226.jpg)


Volvemos al terminal, vas a darle a ctrol + J para invocarlo.\

Vas a poner este comando:\
`python -m pip install --upgrade pip`


Luego vas a poner este:\
`pip install -r requirements.txt`
![](assets/17604718523612.jpg)

Queda poco. Ahora vas a poner:\
`cd driver`

Y luego (sí, es el mismo de antes):\
`pip install -r requirements.txt`

Finalmente pon:\
`cd ..`
![](assets/17604719423361.jpg)

**¡¡¡Ya lo tendrías instalado!!!**

Vamos a hacer una simulación:

Escribe: python sample_b.py

Te pedirá el *Email* y la *key (la que te llegó por correo)*.\
Escribe el email ENTER Pon tu key ENTER
![](assets/17604719535455.jpg)

Ahora te aparecera un pequeño menu, como queremos hacer una simulación
ponemos « **0** » y luego ENTER.
![](assets/17604719590091.jpg)

Nos preguntará si queremos ver una gráfica al final, escribe « s » y
dale a ENTER.\
![](assets/17604719716157.jpg)

Ahora nos pedirá el apalancamiento. Vamos a poner 1.6 por ejemplo y vas
a pulsar ENTER.
![](assets/17604719777704.jpg)

Y esto empezará a funcionar, tarda bastante, no te preocupes.\
![](assets/17604719847563.jpg)

Al principio de la simulación mostrará TAEs enormes, no te preocupes es
normal. Eso se debe a que está extrapolando los resultados de los
primeros días a todo un año, por lo que las variaciones son enormes,
luego se estabiliza.\
![](assets/17604719985139.jpg)

Finalmente te mostrará dos gráficos.\
![](assets/17604720050375.jpg)
![](assets/17604720079418.jpg)

En el primero vemos el valor de nuestra operativa con nuestra estrategia cotrapuesto al del SP500.

En el segundo una nube de puntos con una regresión lineal de los valores contrapuestos del SP500 y los de nuestra operativa.
