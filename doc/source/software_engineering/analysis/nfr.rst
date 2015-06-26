Identificación de requisitos no funcionales
-------------------------------------------

Los siguientes requisitos no funcionales son especificados:

Comunicación
~~~~~~~~~~~~

El número de mensajes transmitidos por el protocolo debe reducirse a la cantidad más pequeña posible, a fin de minimizar el impacto general en la red y en los nodos receptores. Por ello, las comunicaciones se realizarán a través de mensajes **multicast**, que únicamente son procesados por los nodos suscritos al grupo en el que son transmitidos. De esta forma los nodos no interesados evitan dedicar tiempo de CPU al análisis de estos datagramas.

Minimalismo
~~~~~~~~~~~

Toda aquella funcionalidad que no esté relacionada con el descubrimiento y publicación de servicios y nodos se delegará a paquetes software que se apoyen sobre MarcoPolo, delegando la responsabilidad a dichos paquetes. De esta forma MarcoPolo se convierte en un sistema mínimo, y por tanto más sencillo de mantener y comprender.

Portabilidad
~~~~~~~~~~~~

MarcoPolo debe ser un protocolo capaz de funcionar en cualquier configuración de **hardware** y **software** que soporte los requisitos de red exigidos por el mismo.

Integrable
~~~~~~~~~~

La funcionalidad de MarcoPolo debe ser aprovechable por usuarios de forma directa (mediante la interacción con el propio paquete) o indireta, a través de mecanismos de conexión con otras aplicacicones.

Independencia del lenguaje
~~~~~~~~~~~~~~~~~~~~~~~~~~

El protocolo debe ser independiente del lenguaje de programación en el que sea implementado. Dicha implementación debe proporcionar puntos de acceso consumibles por cualquier paquete **software**.


Separación del protocolo y la implementación
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

MarcoPolo es un protocolo. La implementación de referencia del mismo proporciona una referencia para su aplicación, pero no es el único enfoque válido para realizar dicha implementación.

Gestión de errores
~~~~~~~~~~~~~~~~~~

La gestión y recuperación de errores debe ser transparente para el usuario. En caso de que dicha transparencia no pueda ser satisfecha, el protocolo y la implementación deben proveer mensajes claros que describan el error, y qué agente ha causado el mismo (el usuario debido a un error de uso, un error interno, etcétera).

Separación de roles
~~~~~~~~~~~~~~~~~~~

En el protocolo existen dos roles claramente definidos: el descubrimiento de nodos y servicios (Marco) y la publicación de estos (Polo) en la red. Se deberá mantener la independencia entre dichos roles, de forma que puedan funcionar de forma independiente.

Estándares de comunicación y representación de información
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Todos los mensajes transmitidos en el sistema deberán ser codificados en UTF-8 y serán serializados utilizando el formato JavaScript Object Notation (JSON).


Configurabilidad
~~~~~~~~~~~~~~~~

Se deberá facilitar la configurabilidad de MarcoPolo a través de archivos de configuración o cualquier sistema similar.

Sincronización
~~~~~~~~~~~~~~

Los diferentes mensajes transmitidos deberán ser definidos con la secuencia en la que son transmitidos, a qué mensaje responden y qué mensaje debe suceder, etcétera.

Documentación
~~~~~~~~~~~~~

Los siguientes casos deberán ser documentados:

- Documentación del mecanismo de comunicación
- Referencia de la API, que incluirá todos los aspectos internos de MarcoPolo y de los diferentes mecanismos de conexión.

Homogeneidad
~~~~~~~~~~~~

Los diferentes lenguajes de programación para los que se desarrollen mecanismos de conexión con MarcoPolo deberán ser creados siguiendo una semántica homogénea (nombres de métodos y parámetros, orden, tipos de retorno, gestión de errores), sin que ello impida el uso de características propias de cada lenguaje que se consideren beneficiosas.

Calidad del software
~~~~~~~~~~~~~~~~~~~~

Se deberán utilizar mecanismos de verificación del funcionamiento del software como la aplicación de test unitarios para situaciones en las que el sistema se comporta de forma correcta como para situaciones anómalas.

Comunicación no fiable
~~~~~~~~~~~~~~~~~~~~~~

Todos los mensajes se transmiten en datagramas UDP.

Gestión de usuarios
~~~~~~~~~~~~~~~~~~~

Los usuarios se comunicarán con MarcoPolo a través de comunicaciones seguras (utilizando el protocolo TLS/SSL y tokens de usuario) con el objetivo de evitar suplantaciones de identidad.

Sencillez de la API
~~~~~~~~~~~~~~~~~~~

La API de MarcoPolo debe ser sencilla de comprender y utilizar.

..Diferentes tipos de mensajes



Versión
Autores
Fuentes
Objetivos asociados
Requisitos asociados
Descripción
Importancia
Urgencia
Estado
Estabilidad
Comentarios