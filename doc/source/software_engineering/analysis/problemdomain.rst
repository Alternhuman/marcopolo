Dominio del problema
--------------------

MarcoPolo tiene como objetivo responder a la necesidad de contar con un mecanismo que sea capaz de configurar la disposición de cada uno de los nodos en la red de forma completamente automática respetando los requisitos de alto nivel definidos para todo el sistema, tales como la escalabilidad del mismo.


Análisis de alternativas
~~~~~~~~~~~~~~~~~~~~~~~~

Actualmente existen varias soluciones en el mercado que proporcionan una solución a este problema:

- *DNS*
	Si se conocen los nombres de los equipos que conforman la red los cambios en las asociaciones de direcciones de red no afectan al sistema (pues los nombres no son alterados). Esta solución es sencilla de implementar pero no es escalable (el sistema debe contar con una lista de los nombres).

- *mDNS*, *DNS-SD*
	El protocolo mDNS (**multicast DNS**) responde a esta problemática mediante un sistema de resolución de nombres que no cuenta con un servidor central para realizar el proceso, sino que todos los nodos interesados reciben las diferentes consultas y responden en caso de que sea necesario.

	*mDNS* es utilizado también como protocolo de descubrimiento de servicios, para hallar qué equipos son capaces de realizar una tarea concreta, identificada esta por un nombre (p. ej. `distcc.local`).

	Las implementaciones mayoritarias de *mDNS* son Avahi y **Bonjour**.

	Sin embargo, mDNS no permite realizar "segmentaciones" en los nodos presentes en un mismo espacio de direcciones. Todos los nodos reciben todas las peticiones, y responden acordemente.

En función de las necesidades anteriormente definidas y las alternativas evaluadas, se elabora el siguiente esquema de acción: Se deberá crear un protocolo de descubrimiento de servicios que no base su funcionamiento en nombres y cuya configuración permita realizar segmentaciones de nodos en el nivel de aplicación de la pila de protocolos OSI.

