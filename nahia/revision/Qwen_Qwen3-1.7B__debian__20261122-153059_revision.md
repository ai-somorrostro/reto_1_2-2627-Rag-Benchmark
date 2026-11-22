# Revisión: Qwen/Qwen3-1.7B · debian
Retrieval: el fragmento correcto estaba en el top-k en 1 de 2 preguntas con respuesta.
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
