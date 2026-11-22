# Revisión: Qwen/Qwen3-1.7B · debian
Retrieval: el fragmento correcto estaba en el top-k en 8 de 12 preguntas con respuesta.
Pistas automáticas (no son la nota): abstención = la respuesta contiene «No aparece en el documento».

## q_deb_01 · directa
**Pregunta:** Antes de instalar paquetes con APT, ¿qué orden refresca la lista de paquetes disponibles?

**Esperada:** Hay que ejecutar apt update: descarga los ficheros Packages, Sources y de traducción, normalmente comprimidos. Si se instala desde un juego de CD-ROM/DVD no hay descarga y la operación es muy rápida.

**Respuesta del modelo:** La orden que refresca la lista de paquetes disponibles antes de instalar paquetes con APT es **dpkg --set-selections**. Esta orden restaura el estado de los paquetes seleccionados que desea instalar.

- Fragmento correcto en el top-k: NO (el LLM no pudo acertar por culpa del buscador)
- Se abstiene (pista): no
- Cita artículo/sección (pista): no

## q_deb_02 · directa
**Pregunta:** ¿Qué diferencia hay entre desinstalar un paquete con aptitude remove y con aptitude purge?

**Esperada:** apt remove (o aptitude remove) elimina el paquete pero conserva los archivos de configuración; apt purge (o aptitude purge, dpkg -P) realiza una desinstalación completa y elimina también esos archivos de configuración.

**Respuesta del modelo:** La diferencia entre desinstalar un paquete con `aptitude remove` y con `aptitude purge` es que:

- `aptitude remove` elimina el paquete y sus dependencias necesarias, pero no elimina los archivos de configuración del paquete.
- `aptitude purge` elimina el paquete, sus dependencias y los archivos de configuración del paquete.

Cita: [5.2. Metainformación de un paquete > 5.2.2. Scripts de configuración > 5.2.2.2. Eliminación de un paquete]

- Fragmento correcto en el top-k: sí
- Se abstiene (pista): no
- Cita artículo/sección (pista): no

## q_deb_03 · directa
**Pregunta:** ¿Qué comando actualiza el sistema sin eliminar paquetes ni instalar otros nuevos?

**Esperada:** Se usa aptitude safe-upgrade (o apt upgrade / apt-get upgrade), precedido de apt update: actualiza los paquetes instalados sin eliminar ninguno. apt-get es algo más estricto y se niega a instalar paquetes que no estaban instalados previamente.

**Respuesta del modelo:** La respuesta es: **apt upgrade**.

Esta orden busca paquetes instalados que pueden ser actualizados sin eliminar ningún paquete.

- Fragmento correcto en el top-k: sí
- Se abstiene (pista): no
- Cita artículo/sección (pista): no

## q_deb_04 · directa
**Pregunta:** ¿Cómo busco paquetes por palabra clave y veo luego la ficha de uno concreto desde la terminal?

**Esperada:** Con apt-cache search palabra_clave para buscar y apt-cache show paquete para ver su descripción, dependencias y responsable. apt search, apt show, aptitude search y aptitude show funcionan igual.

**Respuesta del modelo:** La búsqueda de paquetes por palabra clave se realiza con la orden **apt-cache search**. Para ver la ficha de un paquete específico, se utiliza la orden **apt-cache show**. 

Esta información se encuentra en el artículo [6.10. Búsqueda de paquetes](#6.10. Búsqueda de paquetes).

- Fragmento correcto en el top-k: sí
- Se abstiene (pista): no
- Cita artículo/sección (pista): sí

## q_deb_05 · directa
**Pregunta:** ¿Qué orden instala de golpe las dependencias de compilación de un paquete fuente?

**Esperada:** apt-get build-dep paquete-fuente instala todos los paquetes mencionados en los campos Build-Depends, siempre que la distribución aparezca en una línea deb-src de /etc/apt/sources.list.

**Respuesta del modelo:** La orden que instala de golpe las dependencias de compilación de un paquete fuente es **apt-get build-dep**.

- Fragmento correcto en el top-k: sí
- Se abstiene (pista): no
- Cita artículo/sección (pista): no

## q_deb_06 · directa
**Pregunta:** ¿Para qué sirve fakeroot cuando se construye un paquete Debian?

**Esperada:** Permite ejecutar un programa dándole la impresión de que corre como root y crea archivos con dueños y permisos arbitrarios, sin conceder privilegios reales. Por eso dpkg-buildpackage lo emplea por defecto para preparar paquetes.

**Respuesta del modelo:** fakeroot sirve para ejecutar un programa y darle la impresión de que está ejecutando como *root*, creando archivos con permisos y dueños arbitrarios. Esto permite que el programa cree un compendio del paquete Debian con archivos que tienen dueños arbitrarios, incluyendo *root*, sin que realmente obtenga privilegios de root. El programa realmente ejecuta como el usuario que ejecutó fakeroot, y los archivos se crean con los permisos de dicho usuario.

- Fragmento correcto en el top-k: sí
- Se abstiene (pista): no
- Cita artículo/sección (pista): no

## q_deb_07 · directa
**Pregunta:** ¿Qué me dice la orden id cuando la ejecuto en una sesión?

**Esperada:** Muestra la identidad del usuario que ejecuta la sesión junto con la lista de grupos a los que pertenece; sirve para comprobar permisos sobre archivos o dispositivos.

**Respuesta del modelo:** La orden **id** me muestra la identidad del usuario ejecutando la sesión junto con la lista de grupos a los que pertenece.

- Fragmento correcto en el top-k: sí
- Se abstiene (pista): no
- Cita artículo/sección (pista): no

## q_deb_08 · directa
**Pregunta:** ¿Dónde debe instalar el administrador sus propias aplicaciones para no pisar archivos gestionados por dpkg?

**Esperada:** En /usr/local/, el directorio cuyo propósito es albergar programas compilados e instalados manualmente; así se evita sobrescribir archivos instalados por los paquetes Debian.

**Respuesta del modelo:** No aparece en el documento.

- Fragmento correcto en el top-k: NO (el LLM no pudo acertar por culpa del buscador)
- Se abstiene (pista): sí
- Cita artículo/sección (pista): sí

## q_deb_09 · combinada
**Pregunta:** Al instalar un paquete .deb, ¿en qué se diferencian dpkg y apt?

**Esperada:** dpkg es el programa que maneja los archivos .deb: los extrae, analiza y descomprime. APT es un grupo de programas de más alto nivel que instala o elimina paquetes manteniendo satisfechas las dependencias, actualiza la lista y el sistema, y evalúa los paquetes como un todo para producir la mejor combinación.

**Respuesta del modelo:** La diferencia entre **dpkg** y **apt** al instalar un paquete .deb se debe a su función y cómo manejan las dependencias:

- **dpkg** es la herramienta que realiza la instalación de paquetes .deb directamente, utilizando la opción **-i** o **--install**. Es más directo y no requiere un repositorio de paquete asociado. Sin embargo, **dpkg** solo ve lo que está instalado en el sistema y lo que se le proporciona en la línea de órdenes, y no sabe de otras dependencias que puedan estar disponibles en repositorios.

- **apt** es una herramienta más avanzada que permite instalar paquetes .deb junto con sus dependencias, limitando las invocaciones de **dpkg** (ya que cada llamada es costosa debido a la carga de la base de datos en memoria). **apt** maneja las dependencias de manera automática y garantiza la consistencia del sistema después de una actualización.

**dpkg** es una herramienta de sistema (tras bambalinas) y **apt** es una herramienta más cercana al usuario que evita las limitaciones del primero.

- Fragmento correcto en el top-k: NO (el LLM no pudo acertar por culpa del buscador)
- Se abstiene (pista): no
- Cita artículo/sección (pista): no

## q_deb_10 · combinada
**Pregunta:** En una salida de df aparece /srv/files con un 90 % de uso: ¿qué utilidad produjo ese dato y cómo pedir cifras más legibles?

**Esperada:** La salida procede de df (disk free), que reporta el espacio disponible en cada disco montado en el sistema de archivos; con la opción -h (human readable) los tamaños se muestran en unidades legibles, normalmente mebibytes o gibibytes.

**Respuesta del modelo:** La utilidad que produjo ese dato es **df**. Para pedir cifras más legibles, se puede usar la opción **-h**.

- Fragmento correcto en el top-k: sí
- Se abstiene (pista): no
- Cita artículo/sección (pista): no

## q_deb_11 · combinada
**Pregunta:** Detecté un proceso sospechoso al comparar los procesos de los usuarios con las sesiones activas. ¿Cómo obtengo su identificador y cómo le pido que termine de forma normal?

**Esperada:** ps auxw muestra todos los procesos con la identidad de su usuario y, cotejado con who o w, permite detectar servicios no declarados. Con ps aux se obtiene el pid; kill -TERM pid pide una terminación ordenada, mientras que kill -KILL pid la fuerza.

**Respuesta del modelo:** La respuesta es:  
**Obtener el identificador de proceso (PID) se puede hacer ejecutando el comando `ps aux` y buscando el PID del proceso sospechoso. Para terminar de forma normal, se puede enviar la señal `TERM` al proceso utilizando el comando `kill -TERM pid`.**

Esta información se encuentra en el artículo [14.7. Tratamiento de una máquina comprometida > 14.7.1. Detección y visualización de la intrusión](#14.7.1. Detección y visualización de la intrusión).

- Fragmento correcto en el top-k: sí
- Se abstiene (pista): no
- Cita artículo/sección (pista): sí

## q_deb_12 · combinada
**Pregunta:** Mi /etc/apt/sources.list tiene fuentes desconocidas pero debsums no detecta cambios en los archivos. ¿Puedo dar el sistema por sano y qué debería hacer?

**Esperada:** No. sources.list muestra de dónde es probable que provengan los paquetes y, con muchas fuentes desconocidas, el administrador puede reinstalar el sistema. Además, dpkg --verify y debsums detectan cambios en archivos procedentes de un paquete Debian, pero son inútiles si el propio paquete está comprometido: conviene usar la verificación de firma digital de APT (digital signature verification system) e instalar únicamente desde orígenes certificados.

**Respuesta del modelo:** No aparece en el documento.

- Fragmento correcto en el top-k: NO (el LLM no pudo acertar por culpa del buscador)
- Se abstiene (pista): sí
- Cita artículo/sección (pista): sí

## q_deb_13 · sin_respuesta
**Pregunta:** ¿Qué comando de pacman debo usar en Debian para instalar un paquete?

**Esperada:** No aparece en el documento

**Respuesta del modelo:** No aparece en el documento.

- Fragmento correcto en el top-k: n/a (sin respuesta)
- Se abstiene (pista): sí
- Cita artículo/sección (pista): sí

## q_deb_14 · sin_respuesta
**Pregunta:** ¿Cómo se lanza un contenedor con docker run según este manual?

**Esperada:** No aparece en el documento

**Respuesta del modelo:** No aparece en el documento.

- Fragmento correcto en el top-k: n/a (sin respuesta)
- Se abstiene (pista): sí
- Cita artículo/sección (pista): sí

## q_deb_15 · sin_respuesta
**Pregunta:** ¿Qué pasos sigue kubeadm para crear un clúster de Kubernetes en Debian?

**Esperada:** No aparece en el documento

**Respuesta del modelo:** No aparece en el documento.

- Fragmento correcto en el top-k: n/a (sin respuesta)
- Se abstiene (pista): sí
- Cita artículo/sección (pista): sí
