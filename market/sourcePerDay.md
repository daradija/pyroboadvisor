Este componente pasa el source trabajar por días.
Source se programa por acciones y la serie de días, que es como funcionan todos los proveedores de datos.

Pero para las estrategias es fundamental que el forward test sea por días.
Es decir, no se debe utilizar informaicón del futuro para tomar decisiones de compra y venta.
Por ello la estrategia ha de tomar la decisión del día en curso solo con la información de los días anteriores.

Para asegurar este requisito PyRoboAdvisor ha creado un componente que se llama sourcePerDay.
SourcePerDay da solo los datos de apertura. Para que la estrategia decida que comprar y vender.

Y programa las ordenes de compra y venta. Que se ejecutarán según la información del resto de la vela, en este caso High, Low.
Close solo sirve con fine de tasación.

