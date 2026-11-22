# Revisión: mistralai/Ministral-3-8B-Instruct-2512 · debian
Retrieval: el fragmento correcto estaba en el top-k en 9 de 12 preguntas con respuesta.
Pistas automáticas (no son la nota): abstención = la respuesta contiene «No aparece en el documento».

## q_deb_01 · directa
**Pregunta:** Antes de instalar paquetes con APT, ¿qué orden refresca la lista de paquetes disponibles?

**Esperada:** Hay que ejecutar apt update: descarga los ficheros Packages, Sources y de traducción, normalmente comprimidos. Si se instala desde un juego de CD-ROM/DVD no hay descarga y la operación es muy rápida.

**Respuesta del modelo:** Antes de instalar paquetes con APT, la orden que refresca la lista de paquetes disponibles es:

**apt update**

*(Sección [6.2.1. Inicialización](6.2. Los programas aptitude, apt-get y apt > 6.2.1. Inicialización)).*

- Fragmento correcto en el top-k: sí
- Se abstiene (pista): no
- Cita artículo/sección (pista): sí

## q_deb_02 · directa
**Pregunta:** ¿Qué diferencia hay entre desinstalar un paquete con aptitude remove y con aptitude purge?

**Esperada:** apt remove (o aptitude remove) elimina el paquete pero conserva los archivos de configuración; apt purge (o aptitude purge, dpkg -P) realiza una desinstalación completa y elimina también esos archivos de configuración.

**Respuesta del modelo:** No aparece en el documento.

*(El fragmento solo menciona **apt remove** y **apt purge** en la sección [6.2.2. Instalación y eliminación](#), pero no detalla las diferencias entre `aptitude remove` y `aptitude purge`).*

- Fragmento correcto en el top-k: sí
- Se abstiene (pista): sí
- Cita artículo/sección (pista): sí

## q_deb_03 · directa
**Pregunta:** ¿Qué comando actualiza el sistema sin eliminar paquetes ni instalar otros nuevos?

**Esperada:** Se usa aptitude safe-upgrade (o apt upgrade / apt-get upgrade), precedido de apt update: actualiza los paquetes instalados sin eliminar ninguno. apt-get es algo más estricto y se niega a instalar paquetes que no estaban instalados previamente.

**Respuesta del modelo:** No aparece en el documento.

---
*Nota: Ninguno de los fragmentos menciona un comando específico que actualice el sistema **sin modificar paquetes instalados ni instalar nuevos** (es decir, solo actualizaciones de versiones de paquetes existentes sin cambios en la lista de software).*

- Fragmento correcto en el top-k: NO (el LLM no pudo acertar por culpa del buscador)
- Se abstiene (pista): sí
- Cita artículo/sección (pista): sí

## q_deb_04 · directa
**Pregunta:** ¿Cómo busco paquetes por palabra clave y veo luego la ficha de uno concreto desde la terminal?

**Esperada:** Con apt-cache search palabra_clave para buscar y apt-cache show paquete para ver su descripción, dependencias y responsable. apt search, apt show, aptitude search y aptitude show funcionan igual.

**Respuesta del modelo:** Para buscar paquetes por palabra clave desde la terminal, puedes usar los siguientes comandos:

1. **Con `apt-cache`**:
   - Busca paquetes por palabra clave con:
     ```
     apt-cache search palabra_clave
     ```
     *(Ejemplo: `apt-cache search video`)*
     **Sección**: [6.3. La orden apt-cache] y [6.10. Búsqueda de paquetes]

   - Luego, para ver la ficha detallada de un paquete concreto (descripción, dependencias, responsable, etc.), usa:
     ```
     apt-cache show nombre_paquete
     ```
     *(Ejemplo: `apt-cache show kino`)*
     **Sección**: [6.3. La orden apt-cache]

2. **Con `axi-cache`** (alternativa más avanzada):
   - Busca paquetes por palabra clave con:
     ```
     axi-cache search término
     ```
     *(Ejemplo: `axi-cache search video`)*
     **Sección**: [6.3. La orden apt-cache] (*ALTERNATIVA*).

   - Para ver la ficha de un paquete, puedes usar también:
     ```
     aptitude show nombre_paquete
     ```
     *(Ejemplo: `aptitude show kino`)*
     **Sección**: [6.5.1. aptitude] y [6.10. Búsqueda de paquet

- Fragmento correcto en el top-k: sí
- Se abstiene (pista): no
- Cita artículo/sección (pista): sí

## q_deb_05 · directa
**Pregunta:** ¿Qué orden instala de golpe las dependencias de compilación de un paquete fuente?

**Esperada:** apt-get build-dep paquete-fuente instala todos los paquetes mencionados en los campos Build-Depends, siempre que la distribución aparezca en una línea deb-src de /etc/apt/sources.list.

**Respuesta del modelo:** Según el fragmento **[15.1. Recompilación de un paquete desde sus fuentes > 15.1.2. Realización de cambios]**, la orden que instala de golpe las dependencias de compilación (`Build-Depends`) de un paquete fuente es:

**`apt-get build-dep`**

*Nota: Esto aplica a paquetes fuente disponibles en una distribución mencionada en el archivo `/etc/apt/sources.list` y que incluyan líneas `deb-src`.*

---
*Cita exacta del fragmento:*
> *"**apt-get** permite instalar todos los paquetes mencionados en los campos **Build-Depends** de un paquete fuente disponible en una distribución mencionada en una línea **deb-src** del archivo **/etc/apt/sources.list**. Esto solo cuestión de ejecutar el **paquete-fuente apt-get build-dep**."*

- Fragmento correcto en el top-k: sí
- Se abstiene (pista): no
- Cita artículo/sección (pista): no

## q_deb_06 · directa
**Pregunta:** ¿Para qué sirve fakeroot cuando se construye un paquete Debian?

**Esperada:** Permite ejecutar un programa dándole la impresión de que corre como root y crea archivos con dueños y permisos arbitrarios, sin conceder privilegios reales. Por eso dpkg-buildpackage lo emplea por defecto para preparar paquetes.

**Respuesta del modelo:** Según el fragmento **[15.1. Recompilación de un paquete desde sus fuentes > 15.1.3. Inicio de la recompilación]**, **fakeroot** sirve para:

*"Engañar a un programa para que cree que está ejecutando como **root** y genera archivos con permisos y dueños arbitrarios (incluyendo *root*), sin que realmente se obtengan privilegios de administrador. Esto evita riesgos al construir paquetes Debian, ya que el proceso se ejecuta como el usuario común que invoca **fakeroot**, pero simula permisos de *root* durante la creación del paquete."*

Además, se menciona que **dpkg-buildpackage** lo usa por defecto al generar paquetes.

---
*Nota: También aparece en el fragmento **[8.10. Compilación de un núcleo > 8.10.1. Introducción y prerequisitos]** como herramienta necesaria para crear paquetes Debian del núcleo sin permisos de administrador.*

- Fragmento correcto en el top-k: sí
- Se abstiene (pista): no
- Cita artículo/sección (pista): no

## q_deb_07 · directa
**Pregunta:** ¿Qué me dice la orden id cuando la ejecuto en una sesión?

**Esperada:** Muestra la identidad del usuario que ejecuta la sesión junto con la lista de grupos a los que pertenece; sirve para comprobar permisos sobre archivos o dispositivos.

**Respuesta del modelo:** La orden **`id`** muestra la **identidad del usuario** que está ejecutando la sesión, incluyendo su **UID (User ID)** y **GID (Group ID)**, junto con la lista de **grupos a los que pertenece**.

En el ejemplo proporcionado:
```
uid=1000(rhertzog) gid=1000(rhertzog) groups=1000(rhertzog),24(cdrom),25(floppy),27(sudo),29(audio),30(dip),44(video),46(plugdev),108(netdev),109(bluetooth),115(scanner)
```
Muestra:
- **UID (uid)**: `1000` (con el nombre de usuario `rhertzog`).
- **GID (gid)**: `1000` (grupo primario `rhertzog`).
- **Grupos secundarios**: `cdrom`, `floppy`, `sudo`, `audio`, `dip`, `video`, `plugdev`, `netdev`, `bluetooth` y `scanner`.

---
**Fuente**: [B.1. Consola y órdenes básicas > B.1.5. Información de sistema: memoria, espacio en disco, identidad](fragmento proporcionado).

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

**Respuesta del modelo:** Según los fragmentos proporcionados, las diferencias entre **dpkg** y **apt** al instalar un paquete `.deb` son las siguientes:

1. **dpkg**:
   - Es la herramienta base para manejar paquetes `.deb` y solo instala o analiza paquetes proporcionados directamente (no descarga dependencias).
   - **No gestiona dependencias automáticamente**: si falta alguna dependencia, la instalación fallará.
   - Trabaja directamente con el paquete `.deb` y no tiene conocimiento de otros paquetes disponibles en el sistema.
   - Ejemplo de uso: `dpkg -i paquete.deb` (fragmento *5.4. Manipulación de paquetes con dpkg*).
   - Es una herramienta de sistema más técnica, usada "tras bambalinas" (fragmento *5.4. Manipulación de paquetes con dpkg*).

2. **apt**:
   - Es una herramienta de nivel superior que **automatiza la instalación de dependencias** y garantiza la consistencia del sistema.
   - Puede instalar paquetes `.deb` directamente (si se especifica la ruta con `./`) y resolver dependencias desde repositorios configurados (fragmento *6.2. Los programas aptitude, apt-get y apt*).
   - Optimiza el uso de `dpkg` al evitar múltiples llamadas costosas (fragmento *5.4.1. Instal

- Fragmento correcto en el top-k: sí
- Se abstiene (pista): no
- Cita artículo/sección (pista): no

## q_deb_10 · combinada
**Pregunta:** En una salida de df aparece /dev/sda5 montado en /home con un 83 % de uso: ¿qué utilidad produjo ese dato y cómo pedir cifras más legibles?

**Esperada:** La salida procede de df (disk free), que reporta el espacio disponible en cada disco montado en el sistema de archivos; con la opción -h (human readable) los tamaños se muestran en unidades legibles, normalmente mebibytes o gibibytes.

**Respuesta del modelo:** La utilidad que produjo ese dato es **`df`** (de *disk free*), descrita en el fragmento **[B.1. Consola y órdenes básicas > B.1.5. Información de sistema: memoria, espacio en disco, identidad]**.

Para obtener cifras más legibles (ej. gibibytes en lugar de bloques de 1 KB), se usa la opción:
```
df -h
```
*(donde `-h` significa *human readable*). Esto convierte automáticamente los valores en unidades comprensibles como MiB, GiB, etc.

---
*Nota: El fragmento no menciona explícitamente el caso de `/dev/sda5` montado en `/home`, pero sí explica el formato de nombres de particiones (como `/dev/sda5`) en **[8.8. Configuración del gestor de arranque > 8.8.1. Identificación de discos]**, donde se indica que es una partición secundaria (tras una extendida).*

- Fragmento correcto en el top-k: sí
- Se abstiene (pista): no
- Cita artículo/sección (pista): no

## q_deb_11 · combinada
**Pregunta:** Detecté un proceso sospechoso al comparar los procesos de los usuarios con las sesiones activas. ¿Cómo obtengo su identificador y cómo le pido que termine de forma normal?

**Esperada:** ps auxw muestra todos los procesos con la identidad de su usuario y, cotejado con who o w, permite detectar servicios no declarados. Con ps aux se obtiene el pid; kill -TERM pid pide una terminación ordenada, mientras que kill -KILL pid la fuerza.

**Respuesta del modelo:** Para obtener el identificador (*pid*) de un proceso sospechoso, puedes usar el comando **`ps aux`** (sección **[B.1. Consola y órdenes básicas > B.1.4. Gestión de proceso]**).

Una vez identificado el *pid*, puedes pedirle que termine de forma normal enviando la señal **`TERM`** con el comando:
```
kill -TERM *pid*
```
(Sección **[B.1. Consola y órdenes básicas > B.1.4. Gestión de proceso]**).

Si el proceso no responde, puedes usar **`KILL`** para finalizarlo de forma forzada:
```
kill -KILL *pid*
```

- Fragmento correcto en el top-k: sí
- Se abstiene (pista): no
- Cita artículo/sección (pista): sí

## q_deb_12 · combinada
**Pregunta:** Mi /etc/apt/sources.list tiene fuentes desconocidas pero debsums no detecta cambios en los archivos. ¿Puedo dar el sistema por sano y qué debería hacer?

**Esperada:** No. sources.list muestra de dónde es probable que provengan los paquetes y, con muchas fuentes desconocidas, el administrador puede reinstalar el sistema. Además, dpkg --verify y debsums detectan cambios en archivos procedentes de un paquete Debian, pero son inútiles si el propio paquete está comprometido: conviene usar la verificación de firma digital de APT (digital signature verification system) e instalar únicamente desde orígenes certificados.

**Respuesta del modelo:** No aparece en el documento cómo actuar cuando **`debsums` no detecta cambios en los archivos** a pesar de tener fuentes desconocidas en `/etc/apt/sources.list`.

---
**Sobre las fuentes desconocidas en `sources.list`:**
- **Debes revisar indicios de paquetes externos** como:
  - Archivos `.deb` en directorios inusuales.
  - Números de versión de paquetes con sufijos no estándar (ej. `ubuntu`, `lmde`).
  - Contenido en `/usr/local/` (puede indicar instalación manual de software).
  *(Fragmento: **3.2.3. Adopción de un servidor Debian existente**)*

---
**Recomendaciones adicionales (aunque no resuelven tu caso específico):**
1. Usar herramientas como **`cruft`** o **`cruft-ng`** para listar archivos no asociados a paquetes Debian (aunque advierte que no deben borrarse ciegamente).
2. Verificar versiones de paquetes con:
   ```bash
   apt-show-versions
   ```
   *(Fragmento: **3.2.3. Adopción de un servidor Debian existente**)*

---
**No hay instrucciones directas en los fragmentos sobre cómo validar la salud del sistema cuando `debsums` no detecta inconsistencias**, pero **la precaución general es analizar

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

*(El manual proporcionado se refiere exclusivamente a LXC, no a Docker, por lo que no contiene información sobre cómo lanzar un contenedor con `docker run`).*

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
