# **Tutorial configuración IB**

### Paso 0º Crear cuenta de Interactive Broke


Para crear una cuenta se hace desde aquí: 

Link del portal: https://www.interactivebrokers.ie/es/home.php (Sale arriba a la derecha «ABRIR CUENTA»)

O si lo prefieres, directamente crear cuenta: https://www.interactivebrokers.co.uk/Universal/Application?locale=es_ES

Lo **importante** es que dejes estos parámetros iguales cuando te aparezcan.

1º CUENTA INDIVIDUAL    
![](assets/Cuenta_individual.png)

2º TIPO DE CUENTA - Efectivo/«Cash» VS Margen/«Margin»     
![](assets/Tipo_cuenta.png)

3º TIPO DE INVERSIÓN
![](Tipo_inversion.png)

Finalmente una vez creada. Si eres de la UE, puedes transferir el dinero para operar con **SEPA**.

### Paso 1º: Configuración portal:
https://www.interactivebrokers.ie/sso/Login?RL=1&locale=es_ES   
![](assets/17618160371096.jpg)

Una vez dentro nos vamos arriba a la derecha, al pequeño monigote blanco.   
![](assets/17618161091805.jpg)

![](assets/17618160996414.jpg)

Una vez le demos, le damos a configuración:   
![](assets/17618161321728.jpg)


Bajamos un poco, y le damos a:
**Plan de comisiones**, debéis dejarlo por niveles si no vais a meter cantidad muy grandes.   
![](assets/17618161828449.jpg)

Poned como **Divisa base** - USD   
![](assets/17618163930984.jpg)

Con esto ya habríamos terminado con la configuración del portal.

### Paso 2º: Configuración Trade Work Station (TWS):

Descargar el programa:

El TWS sin conexión, última versión.   
https://www.interactivebrokers.ie/es/index.php?f=16874   
![](assets/17618169466055.jpg)


Una vez descargado e instalado. (Instalado cuestión de darle todo a siguiente).

Deberás hacer login:   
![](assets/17618170020338.jpg)

Una vez dentro le vas a dar a (arriba a la izquierda):   
![](assets/17618178390713.jpg)

Ahí vas a dejarlo igual que aquí:   

En API - Settings:   
![](assets/17618179083793.jpg)

Vas a dejar así las 2 primeras:   
![](assets/17618179275855.jpg)

Ahora en cerrar y salir:   
![](assets/17618179478757.jpg)

Vas a dejarlo así:   
![](assets/17618179861695.jpg)

Ya estaría configurado.

De forma extra, podéis cambiar en filtrar:    
![](assets/17618180417472.jpg)

Y dejarlo así:   
![](assets/17618180700294.jpg)

Aquí dejarlo siempre puesto en cartera:   
![](assets/17618180969899.jpg)

Luego abajo a la izquierda, dejarlo así, para que aparezca **ACTIVAS**, se le debe dar click en ese apartado y darle a **ÓRDENES EN TIEMPO REAL**   
![](assets/17618181583566.jpg)

![](assets/17618181235655.jpg)

Así, una vez configurado así, en ACTIVAS:   
![](assets/17618182383512.jpg)
Te saldrán las órdenes de hoy cargadas que no se han ejecutado (no tienen por qué ejecutarse todas, forman parte del normal uso).


Y en OPERACIONES:   
![](assets/17618183004858.jpg)
Saldrían aquellas que ya se han ejecutado hoy.


Una vez hecho eso, ya estaría todo perfecto.

Sería cuestión de abrir el Visual Studio Code.

Abrir terminal.

Para el diario:   
`cd "$env:USERPROFILE\pyroboadvisor"; .\venv\Scripts\Activate.ps1; python sample_b.py` 

Para el semanal:   
`cd "$env:USERPROFILE\pyroboadvisor"; .\venv\Scripts\Activate.ps1; python daemon.py` 

Una forma cómoda de disposición en pantalla es dejar TWS achatado encima de VS Code y ir viendo como carga.
![](assets/17618189433881.jpg)

Al terminar verás como van entrando las órdenes en la sección de **ACTIVAS** en directo.
![](assets/17618182383512.jpg)

![](assets/17618182383512.jpg)
![](assets/Órdenes_entrantes.png)

