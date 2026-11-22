# Revisión: HuggingFaceTB/SmolLM3-3B · debian
Retrieval: el fragmento correcto estaba en el top-k en 6 de 7 preguntas con respuesta.
Pistas automáticas (no son la nota): abstención = la respuesta contiene «No aparece en el documento».

## q_deb_01 · directa
**Pregunta:** Antes de instalar paquetes con APT, ¿qué orden refresca la lista de paquetes disponibles?

**Esperada:** Hay que ejecutar apt update: descarga los ficheros Packages, Sources y de traducción, normalmente comprimidos. Si se instala desde un juego de CD-ROM/DVD no hay descarga y la operación es muy rápida.

**Respuesta del modelo:** La orden que refresca la lista de paquetes disponibles antes de instalar paquetes con APT es:

**apt-file update**

Esta orden se encuentra en la sección [6.4. La orden apt-file](#sect.apt-file) del documento.

- Fragmento correcto en el top-k: NO (el LLM no pudo acertar por culpa del buscador)
- Se abstiene (pista): no
- Cita artículo/sección (pista): sí

## q_deb_02 · directa
**Pregunta:** ¿Qué diferencia hay entre desinstalar un paquete con aptitude remove y con aptitude purge?

**Esperada:** apt remove (o aptitude remove) elimina el paquete pero conserva los archivos de configuración; apt purge (o aptitude purge, dpkg -P) realiza una desinstalación completa y elimina también esos archivos de configuración.

**Respuesta del modelo:** La diferencia entre desinstalar un paquete con `aptitude remove` y con `aptitude purge` es que:

- `aptitude remove` elimina el paquete y sus archivos de configuración, pero no los archivos temporales ni los archivos de registro asociados. Esto significa que el paquete puede ser reinstalado fácilmente con la misma configuración.

- `aptitude purge` elimina el paquete, sus archivos de configuración, archivos temporales y archivos de registro asociados. Esto realiza una desinstalación completa, lo que significa que no es posible reinstalar el paquete con la misma configuración.

Por ejemplo, si usas `aptitude remove` para desinstalar un paquete, podrías reinstalarlo rápidamente con la misma configuración. Sin embargo, si usas `aptitude purge`, la desinstalación es completa y no se pueden recuperar los archivos de configuración ni los archivos temporales.

- Fragmento correcto en el top-k: sí
- Se abstiene (pista): no
- Cita artículo/sección (pista): no

## q_deb_03 · directa
**Pregunta:** ¿Qué comando actualiza el sistema sin eliminar paquetes ni instalar otros nuevos?

**Esperada:** Se usa aptitude safe-upgrade (o apt upgrade / apt-get upgrade), precedido de apt update: actualiza los paquetes instalados sin eliminar ninguno. apt-get es algo más estricto y se niega a instalar paquetes que no estaban instalados previamente.

**Respuesta del modelo:** Para actualizar el sistema sin eliminar paquetes ni instalar nuevos, puede utilizar la orden:

**apt upgrade**

Esta orden busca paquetes instalados que pueden ser actualizados sin eliminar ningún paquete. Asegura la actualización menos intrusiva posible.

- Fragmento correcto en el top-k: sí
- Se abstiene (pista): no
- Cita artículo/sección (pista): no

## q_deb_04 · directa
**Pregunta:** ¿Cómo busco paquetes por palabra clave y veo luego la ficha de uno concreto desde la terminal?

**Esperada:** Con apt-cache search palabra_clave para buscar y apt-cache show paquete para ver su descripción, dependencias y responsable. apt search, apt show, aptitude search y aptitude show funcionan igual.

**Respuesta del modelo:** Para buscar paquetes por palabra clave y ver luego la ficha de uno concreto desde la terminal, puedes usar la orden `apt-cache search` para realizar la búsqueda y luego `apt-cache show` para ver la ficha del paquete seleccionado.

Ejemplo:
```
$ apt-cache search video
```
Esto mostrará una lista de paquetes cuyos nombres o descripciones contengan la palabra clave "video".

Luego, para ver la ficha de un paquete específico, puedes usar:
```
$ apt-cache show paquete
```
Reemplaza "paquete" con el nombre del paquete que deseas ver.

Además, si prefieres usar `aptitude`, puedes hacerlo de la siguiente manera:
```
$ aptitude search video
```
Para ver la ficha de un paquete específico:
```
$ aptitude show paquete
```
Ambas órdenes te permitirán buscar y ver la ficha de los paquetes de manera eficiente desde la terminal.

- Fragmento correcto en el top-k: sí
- Se abstiene (pista): no
- Cita artículo/sección (pista): no

## q_deb_05 · directa
**Pregunta:** ¿Qué orden instala de golpe las dependencias de compilación de un paquete fuente?

**Esperada:** apt-get build-dep paquete-fuente instala todos los paquetes mencionados en los campos Build-Depends, siempre que la distribución aparezca en una línea deb-src de /etc/apt/sources.list.

**Respuesta del modelo:** Para instalar las dependencias de compilación de un paquete fuente, puedes usar el comando:

**apt-get build-dep nombre-paquete**

Este comando instalará todos los paquetes necesarios para la compilación del paquete fuente.

- Fragmento correcto en el top-k: sí
- Se abstiene (pista): no
- Cita artículo/sección (pista): no

## q_deb_06 · directa
**Pregunta:** ¿Para qué sirve fakeroot cuando se construye un paquete Debian?

**Esperada:** Permite ejecutar un programa dándole la impresión de que corre como root y crea archivos con dueños y permisos arbitrarios, sin conceder privilegios reales. Por eso dpkg-buildpackage lo emplea por defecto para preparar paquetes.

**Respuesta del modelo:** **Fakeroot** sirve para ejecutar un programa bajo la ilusión de que se está ejecutando como el usuario root, permitiendo crear un compendio (paquete) con archivos que tendrán permisos y dueños arbitrarios, incluyendo al usuario root. Esto es útil para evitar que el usuario que ejecuta el programa tenga que tener permisos de root para crear el paquete, reduciendo así los riesgos de seguridad.

- Fragmento correcto en el top-k: sí
- Se abstiene (pista): no
- Cita artículo/sección (pista): no

## q_deb_07 · directa
**Pregunta:** ¿Qué me dice la orden id cuando la ejecuto en una sesión?

**Esperada:** Muestra la identidad del usuario que ejecuta la sesión junto con la lista de grupos a los que pertenece; sirve para comprobar permisos sobre archivos o dispositivos.

**Respuesta del modelo:** La orden `id` muestra la identidad del usuario ejecutando la sesión junto con la lista de grupos a los que pertenece. Ejecutando `id` en una sesión, obtendrás información sobre tu identificador de usuario (`uid`), tu grupo principal actual (`gid`), y la lista de grupos a los que perteneces (`groups`). Por ejemplo, en el fragmento proporcionado, la salida de `id` sería:

```
uid=1000(rhertzog) gid=1000(rhertzog) groups=1000(rhertzog),24(cdrom),25(floppy),27(sudo),29(audio),30(dip),44(video),46(plugdev),108(netdev),109(bluetooth),115(scanner)
```

Esta información es útil para entender los permisos de acceso a archivos y dispositivos, ya que algunos pueden estar limitados a miembros de ciertos grupos.

- Fragmento correcto en el top-k: sí
- Se abstiene (pista): no
- Cita artículo/sección (pista): no
