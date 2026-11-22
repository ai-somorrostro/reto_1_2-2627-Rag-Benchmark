# Revisión: Qwen/Qwen3-8B · debian
Retrieval: el fragmento correcto estaba en el top-k en 8 de 12 preguntas con respuesta.
Pistas automáticas (no son la nota): abstención = la respuesta contiene «No aparece en el documento».

## q_deb_01 · directa
**Pregunta:** Antes de instalar paquetes con APT, ¿qué orden refresca la lista de paquetes disponibles?

**Esperada:** Hay que ejecutar apt update: descarga los ficheros Packages, Sources y de traducción, normalmente comprimidos. Si se instala desde un juego de CD-ROM/DVD no hay descarga y la operación es muy rápida.

**Respuesta del modelo:** La orden que refresca la lista de paquetes disponibles antes de instalar con APT es `apt update`. Esta orden actualiza la lista de paquetes disponibles desde los repositorios configurados en `/etc/apt/sources.list` y los archivos en `/etc/apt/preferences.d/` y `/etc/apt/preferences`. No aparece en el documento.

- Fragmento correcto en el top-k: NO (el LLM no pudo acertar por culpa del buscador)
- Se abstiene (pista): sí
- Cita artículo/sección (pista): sí

## q_deb_02 · directa
**Pregunta:** ¿Qué diferencia hay entre desinstalar un paquete con aptitude remove y con aptitude purge?

**Esperada:** apt remove (o aptitude remove) elimina el paquete pero conserva los archivos de configuración; apt purge (o aptitude purge, dpkg -P) realiza una desinstalación completa y elimina también esos archivos de configuración.

**Respuesta del modelo:** La diferencia entre desinstalar un paquete con **aptitude remove** y con **aptitude purge** radica en el tratamiento de los archivos de configuración. 

- Con **aptitude remove**, se elimina el paquete pero se mantienen los archivos de configuración. Esto permite reinstalar el paquete fácilmente con la misma configuración anterior.  
- Con **aptitude purge**, se realiza una desinstalación completa, eliminando también los archivos de configuración junto con otros archivos temporales y copias asociados al paquete.  

Esta información se deriva de la sección [6.2. Los programas aptitude, apt-get y apt > 6.2.2. Instalación y eliminación](#sect.6.2.2).

- Fragmento correcto en el top-k: sí
- Se abstiene (pista): no
- Cita artículo/sección (pista): sí

## q_deb_03 · directa
**Pregunta:** ¿Qué comando actualiza el sistema sin eliminar paquetes ni instalar otros nuevos?

**Esperada:** Se usa aptitude safe-upgrade (o apt upgrade / apt-get upgrade), precedido de apt update: actualiza los paquetes instalados sin eliminar ninguno. apt-get es algo más estricto y se niega a instalar paquetes que no estaban instalados previamente.

**Respuesta del modelo:** El comando que actualiza el sistema sin eliminar paquetes ni instalar otros nuevos es **apt upgrade**. Este comando busca paquetes instalados que pueden ser actualizados sin eliminar ningún paquete, asegurando una actualización menos intrusiva posible. [6.2.3. Actualización del sistema]

- Fragmento correcto en el top-k: sí
- Se abstiene (pista): no
- Cita artículo/sección (pista): no

## q_deb_04 · directa
**Pregunta:** ¿Cómo busco paquetes por palabra clave y veo luego la ficha de uno concreto desde la terminal?

**Esperada:** Con apt-cache search palabra_clave para buscar y apt-cache show paquete para ver su descripción, dependencias y responsable. apt search, apt show, aptitude search y aptitude show funcionan igual.

**Respuesta del modelo:** Para buscar paquetes por palabra clave, puede utilizar el comando `apt-cache search` seguido de la palabra clave deseada. Por ejemplo, `apt-cache search video` devolverá una lista de paquetes cuyos nombres o descripciones contengan la palabra clave "video". 

Para ver la ficha de un paquete concreto, puede usar el comando `apt-cache show` seguido del nombre del paquete. Por ejemplo, `apt-cache show kino` mostrará la ficha del paquete "kino". 

Esto se menciona en el fragmento [6.10. Búsqueda de paquetes].

- Fragmento correcto en el top-k: sí
- Se abstiene (pista): no
- Cita artículo/sección (pista): no

## q_deb_05 · directa
**Pregunta:** ¿Qué orden instala de golpe las dependencias de compilación de un paquete fuente?

**Esperada:** apt-get build-dep paquete-fuente instala todos los paquetes mencionados en los campos Build-Depends, siempre que la distribución aparezca en una línea deb-src de /etc/apt/sources.list.

**Respuesta del modelo:** **apt-get build-dep** instala de golpe las dependencias de compilación de un paquete fuente. Esto permite instalar todos los paquetes mencionados en los campos **Build-Depends** de un paquete fuente disponible en una distribución mencionada en una línea **deb-src** del archivo **/etc/apt/sources.list**. [15.1.2. Realización de cambios]

- Fragmento correcto en el top-k: sí
- Se abstiene (pista): no
- Cita artículo/sección (pista): no

## q_deb_06 · directa
**Pregunta:** ¿Para qué sirve fakeroot cuando se construye un paquete Debian?

**Esperada:** Permite ejecutar un programa dándole la impresión de que corre como root y crea archivos con dueños y permisos arbitrarios, sin conceder privilegios reales. Por eso dpkg-buildpackage lo emplea por defecto para preparar paquetes.

**Respuesta del modelo:** **fakeroot** se utiliza para engañar al programa de manera que crea la ilusión de que está ejecutando como usuario *root*, permitiendo así crear archivos con permisos y dueños arbitrarios, incluyendo *root*, sin realmente tener privilegios de administrador. Esto es útil al construir un paquete Debian, ya que evita los riesgos asociados con ejecutar como *root* durante el proceso de compilación. Este comportamiento es utilizado por defecto por **dpkg-buildpackage** al generar paquetes. [15.1.3. Inicio de la recompilación]

- Fragmento correcto en el top-k: sí
- Se abstiene (pista): no
- Cita artículo/sección (pista): no

## q_deb_07 · directa
**Pregunta:** ¿Qué me dice la orden id cuando la ejecuto en una sesión?

**Esperada:** Muestra la identidad del usuario que ejecuta la sesión junto con la lista de grupos a los que pertenece; sirve para comprobar permisos sobre archivos o dispositivos.

**Respuesta del modelo:** La orden **id** muestra la identidad del usuario ejecutando la sesión junto con la lista de grupos a los que pertenece. Esto incluye el identificador personal (uid), el grupo principal (gid) y la lista de grupos. Este información puede ser útil para verificar a qué grupos se pertenece, ya que el acceso a algunos archivos o dispositivos puede estar limitado a miembros de ciertos grupos. [B.1. Consola y órdenes básicas > B.1.5. Información de sistema: memoria, espacio en disco, identidad]

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

**Respuesta del modelo:** Al instalar un paquete `.deb`, **dpkg** y **apt** se diferencian en su manejo de dependencias y en su enfoque general. **dpkg** es una herramienta de sistema que permite instalar un paquete `.deb` sin descargar nada, pero no gestiona las dependencias, lo que puede llevar a fallos si no se satisfacen. Por otro lado, **apt** es una herramienta más cercana al usuario que automatiza la instalación de paquetes y sus dependencias, asegurando la consistencia del sistema. Además, **apt** puede aprovechar el uso de **dpkg** en etapas separadas, limitando su invocación para optimizar el rendimiento. 

Esto se basa en los fragmentos [5.4. Manipulación de paquetes con dpkg] y [6.2. Los programas aptitude, apt-get y apt].

- Fragmento correcto en el top-k: NO (el LLM no pudo acertar por culpa del buscador)
- Se abstiene (pista): no
- Cita artículo/sección (pista): no

## q_deb_10 · combinada
**Pregunta:** En una salida de df aparece /dev/sda5 montado en /home con un 83 % de uso: ¿qué utilidad produjo ese dato y cómo pedir cifras más legibles?

**Esperada:** La salida procede de df (disk free), que reporta el espacio disponible en cada disco montado en el sistema de archivos; con la opción -h (human readable) los tamaños se muestran en unidades legibles, normalmente mebibytes o gibibytes.

**Respuesta del modelo:** La utilidad **df** produce ese dato. Para pedir cifras más legibles, se puede utilizar la opción **-h** con el comando **df**. Esto convierte los tamaños en unidades más legibles, como mebibytes o gibibytes. 

[B.1. Consola y órdenes básicas > B.1.5. Información de sistema: memoria, espacio en disco, identidad]

- Fragmento correcto en el top-k: sí
- Se abstiene (pista): no
- Cita artículo/sección (pista): no

## q_deb_11 · combinada
**Pregunta:** Detecté un proceso sospechoso al comparar los procesos de los usuarios con las sesiones activas. ¿Cómo obtengo su identificador y cómo le pido que termine de forma normal?

**Esperada:** ps auxw muestra todos los procesos con la identidad de su usuario y, cotejado con who o w, permite detectar servicios no declarados. Con ps aux se obtiene el pid; kill -TERM pid pide una terminación ordenada, mientras que kill -KILL pid la fuerza.

**Respuesta del modelo:** Para obtener el identificador de un proceso sospechoso, puede utilizar el comando **ps auxw**, que muestra una lista de todos los procesos con su identidad de usuario y su identificador de proceso (pid). Una vez que tenga el pid del proceso sospechoso, puede enviarle la señal **TERM** para pedirle que termine de forma normal utilizando el comando **kill -TERM pid**. 

Este procedimiento se describe en la sección [3.2.1.1. La red y los procesos](3.2.1.1. La red y los procesos).

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
