Casos de uso del paquete Marco
------------------------------

1. Realizar descubrimiento de nodos

	- **Versión**
	- **Autores**
	- **Fuentes**
	- **Objetivos asociados**: 1
	- **Requisitos asociados**
	- **Descripción**

		A petición de un usuario, una instancia del *software* realizará una operación de descubrimiento de los diferentes nodos presentes en la red.
	
	- **Precondición**

		El software debe estar en ejecución cuando comience la secuencia de interacción.

	- **Secuencia normal**:

		1. El usuario envía un mensaje al sistema indicando que desea descubrir un servicio.

		2. El sistema recibe el mensaje, procesa el contenido y en caso de que los datos sean válidos, realiza la operación. En caso contrario retorna un mensaje indicativo al usuario.

		3. La operación se realiza y mientras tanto el usuario espera. El tiempo de espera es definido por el usuario, o se utiliza un tiempo por defecto en caso de que no sea indicado en el mensaje inicial. Durante el tiempo de espera son procesadas las respuestas hasta ese momento. 
	
	- **Poscondición**:
		Se retornan los datos recogidos o una lista vacía en caso de la búsqueda haya sido infructuosa.
	
	- **Excepciones**:

		- En caso de que los datos que el usuario introduzca sean erróneos se indicará dicha situación al usuario.

		- En caso de un fallo interno (p. ej. error en la comunicación entre partes) el usuario será notificado.

	- **Rendimiento**
	- **Frecuencia**
	- **Importancia**
		Muy alta

	- **Urgencia**
		Elevada

	- **Estado**
		Todos los objetivos han sido cumplidos.

	- **Estabilidad**
		Alta

	- **Comentarios**

2. Realizar descubrimiento de un servicio

	- **Versión**
	- **Autores**
	- **Fuentes**
	- **Objetivos asociados**: 1
	- **Requisitos asociados**
	- **Descripción**

		A petición de un usuario, una instancia del *software* realizará una operación de descubrimiento de los diferentes servicios presentes en la red.
	
	- **Precondición**

		El software debe estar en ejecución cuando comience la secuencia de interacción.

	- **Secuencia normal**:

		1. El usuario envía un mensaje al sistema indicando que desea descubrir un servicio.

		2. El sistema recibe el mensaje, procesa el contenido y en caso de que los datos sean válidos, realiza la operación. En caso contrario retorna un mensaje indicativo al usuario.

		3. La operación se realiza y mientras tanto el usuario espera. El tiempo de espera es definido por el usuario, o se utiliza un tiempo por defecto en caso de que no sea indicado en el mensaje inicial. Durante el tiempo de espera son procesadas las respuestas hasta ese momento. 
	
	- **Poscondición**:
		Se retornan los datos recogidos o una lista vacía en caso de la búsqueda haya sido infructuosa.
	
	- **Excepciones**:

		- En caso de que los datos que el usuario introduzca sean erróneos se indicará dicha situación al usuario.

		- En caso de un fallo interno (p. ej. error en la comunicación entre partes) el usuario será notificado.

	- **Rendimiento**
	- **Frecuencia**
	- **Importancia**
		Muy alta

	- **Urgencia**
		Elevada

	- **Estado**
		Todos los objetivos han sido cumplidos.

	- **Estabilidad**
		Alta

	- **Comentarios**

Consultar información sobre un nodo

	- **Versión**
	- **Autores**
	- **Fuentes**
	- **Objetivos asociados**: 3
	- **Requisitos asociados**
	- **Descripción**

		A petición de un usuario, una instancia del *software* realizará una operación de consulta sobre un nodo.
	
	- **Precondición**

		El software debe estar en ejecución cuando comience la secuencia de interacción.

	- **Secuencia normal**:

		1. El usuario envía un mensaje al sistema indicando que desea realizar una consulta sobre los servicios que un nodo contiene.

		2. El sistema envía únicamente a ese nodo la operación de consulta.

		3. Se espera durante un tiempo determinado por el usuario (o en caso de que no sea proporcionado, un valor por defecto) a que el nodo responda.

		4. En caso de que el nodo consultado responda, se procesa la lista de servicios incluida en el mensaje.
	
	- **Poscondición**:
		
		Se retornan los datos recogidos o una lista vacía en caso de que el mensaje de respuesta no incluya ninguno.
	
	- **Excepciones**:

		- En caso de que los datos que el usuario introduzca sean erróneos se indicará dicha situación al usuario.

		- En caso de un fallo interno (p. ej. error en la comunicación entre partes) el usuario será notificado.

		- En caso de que el nodo no se encuentre en la red, se indicará al usuario dicha situación.

	- **Rendimiento**
	- **Frecuencia**
	- **Importancia**
		
		Media

	- **Urgencia**
		
		Baja

	- **Estado**
		
		Todos los objetivos han sido cumplidos.

	- **Estabilidad**
		Alta

	- **Comentarios**

Publicar un servicio raíz

Publicar un servicio de usuario

Eliminar un servicio




