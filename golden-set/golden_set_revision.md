# Golden set: revisión del grupo

Ficheros para el benchmark: `golden_boe.jsonl` y `golden_debian.jsonl` (15 preguntas cada uno: 8 directas, 4 combinadas, 3 sin respuesta).
Todos los IDs de `chunks` existen en vuestros ficheros de chunks. Ninguna pregunta comparte 5 palabras seguidas con el documento.

> **Regla de acierto a decidir:** en las combinadas, ¿cuenta como acierto en Recall@k que aparezca *uno* de los dos chunks o *los dos*? Elegid una, escribidla y aplicadla a todos los modelos.

## Escenario 1: Estatuto de los Trabajadores (BOE)

### Directas (1 fragmento)

| ID | Pregunta | Respuesta esperada | Chunks |
|---|---|---|---|
| BOE_D01 | ¿Cuántos días de descanso pagado al año me tocan como mínimo y con cuánta antelación me tienen que decir las fechas? | Al menos 30 días naturales de vacaciones retribuidas, que no se pueden cambiar por dinero. El trabajador debe conocer sus fechas como mínimo dos meses antes de empezar a disfrutarlas (art. 38). | `boe_39` |
| BOE_D02 | Me contratan como ingeniera y el convenio no dice nada del periodo de prueba. ¿Cuánto puede durar como máximo? | Seis meses, porque es técnica titulada (para el resto de trabajadores serían dos meses, o tres en empresas de menos de 25 trabajadores) (art. 14). | `boe_14` |
| BOE_D03 | ¿Hay un tope de horas extra que se puedan hacer en un año? | Sí: no más de 80 horas extraordinarias al año (sin contar las compensadas con descanso en los cuatro meses siguientes ni las hechas para reparar siniestros) (art. 35). | `boe_36` |
| BOE_D04 | Si salgo de trabajar a las 23:00, ¿a qué hora es lo más pronto que me pueden hacer entrar al día siguiente? | A las 11:00: entre el final de una jornada y el comienzo de la siguiente deben pasar como mínimo doce horas (art. 34.3). | `boe_35` |
| BOE_D05 | ¿Cuántas pagas extra tengo derecho a cobrar al año y cuándo? | Dos gratificaciones extraordinarias al año: una por Navidad y otra en el mes que fije el convenio o el acuerdo con los representantes. El convenio puede prorratearlas en las doce mensualidades (art. 31). | `boe_32` |
| BOE_D06 | Me caso el mes que viene. ¿Cuántos días libres pagados me corresponden? | Quince días naturales de permiso retribuido por matrimonio o registro de pareja de hecho, con aviso previo y justificación (art. 37.3.a). | `boe_38` |
| BOE_D07 | Quiero dejar la empresa un tiempo para hacer un máster y luego volver. ¿Qué requisitos y duración tiene esa opción? | Es la excedencia voluntaria: hace falta al menos un año de antigüedad y dura entre cuatro meses y cinco años. No se puede repetir hasta pasados cuatro años y al volver solo hay derecho preferente a las vacantes de igual o similar categoría (art. 46.2 y 46.5). | `boe_47` |
| BOE_D08 | Me acaban de despedir y no estoy de acuerdo. ¿Cuánto tiempo tengo para reclamar? | Veinte días hábiles desde el despido; es un plazo de caducidad (art. 59.3). | `boe_62` |

### Combinan 2 fragmentos

| ID | Pregunta | Respuesta esperada | Chunks |
|---|---|---|---|
| BOE_C01 | Me despiden por causas objetivas, pero luego un juez dice que el despido es improcedente. ¿Cómo cambia la indemnización? | Por causas objetivas son 20 días de salario por año trabajado con un máximo de 12 mensualidades (art. 53.1.b). Si se declara improcedente, la empresa elige entre readmitir o pagar 33 días por año con un máximo de 24 mensualidades (art. 56.1). | `boe_56`, `boe_59` |
| BOE_C02 | ¿A partir de cuántas horas a la semana se considera que estoy haciendo horas extra, y cómo me las compensan si no hay nada pactado? | Son extra las horas por encima de la jornada máxima ordinaria, que es de 40 horas semanales de trabajo efectivo de promedio en cómputo anual (art. 34.1). Si no hay pacto, se compensan con descanso dentro de los cuatro meses siguientes; si se pagan, nunca por debajo del valor de la hora ordinaria (art. 35.1). | `boe_35`, `boe_36` |
| BOE_C03 | Un compañero ha faltado varias veces sin justificar. ¿Lo pueden despedir por eso y cómo se lo tienen que comunicar? | Sí: las faltas repetidas e injustificadas de asistencia o puntualidad son causa de despido disciplinario (art. 54.2.a). El despido debe notificarse por escrito, indicando los hechos que lo motivan y la fecha de efectos (art. 55.1). | `boe_57`, `boe_58` |
| BOE_C04 | ¿Qué indemnización me corresponde si dejo la empresa porque me trasladan a otra ciudad, y cuál si la dejo porque me cambian el horario y me perjudica? | Por traslado que obliga a cambiar de residencia: 20 días de salario por año con un máximo de 12 mensualidades (art. 40.1). Por modificación sustancial de horario que perjudica: 20 días por año con un máximo de nueve meses (art. 41.3). | `boe_41`, `boe_42` |

### Sin respuesta (abstención)

| ID | Pregunta | Respuesta esperada | Chunks |
|---|---|---|---|
| BOE_N01 | Si me quedo en el paro, ¿cuánto dinero voy a cobrar al mes? | No aparece en el documento. El Estatuto no regula la cuantía de la prestación por desempleo.<br>*Nota: Se menciona la entidad gestora de la prestación por desempleo (art. 47) pero no hay cifras.* | — |
| BOE_N02 | ¿Cuántos días a la semana tengo derecho a teletrabajar? | No aparece en el documento. El art. 13 solo remite a la Ley 10/2021 de trabajo a distancia y el art. 34.8 permite solicitar adaptaciones, pero no fija un número de días.<br>*Nota: Pregunta trampa: hay chunks que hablan de trabajo a distancia (boe_13, boe_35).* | — |
| BOE_N03 | ¿De cuánto es la multa para una empresa que no lleva el registro de la jornada? | No aparece en el documento. Las infracciones del empresario se rigen por la Ley sobre Infracciones y Sanciones en el Orden Social (art. 60.1); el Estatuto no da importes.<br>*Nota: El registro diario de jornada sí aparece (art. 34.9 y 35.5), pero no la sanción.* | — |

## Escenario 2: Manual del Administrador de Debian

### Directas (1 fragmento)

| ID | Pregunta | Respuesta esperada | Chunks |
|---|---|---|---|
| DEB_D01 | ¿Qué tengo que ejecutar para que APT descargue la lista más reciente de paquetes disponibles? | apt update (sección 6.2.1). | `debian_104` |
| DEB_D02 | ¿Qué diferencia hay entre desinstalar un paquete con remove y con purge? | apt remove elimina el paquete; apt purge hace una desinstalación completa que también borra sus archivos de configuración (sección 6.2.2). | `debian_105` |
| DEB_D03 | ¿Dónde puedo ver un historial de cuándo se instaló o actualizó cada paquete? | En /var/log/dpkg.log, donde dpkg registra todas sus acciones (sección 5.4.4). | `debian_93` |
| DEB_D04 | Solo recuerdo parte del nombre de un fichero. ¿Qué herramienta lo encuentra casi al instante y de dónde saca la información? | locate, que consulta una base de datos con la ubicación de todos los archivos; esa base se actualiza a diario con updatedb (sección 8.9.6). | `debian_175` |
| DEB_D05 | ¿Cómo doy de alta un usuario nuevo y le permito usar el sonido del equipo? | Con adduser usuario para crear la cuenta, y adduser usuario audio para añadirlo al grupo audio (sección 8.5). | `debian_162` |
| DEB_D06 | Quiero conectarme por SSH a un servidor sin escribir la contraseña cada vez. ¿Qué pasos sigo? | Generar un par de claves en el cliente con ssh-keygen -t rsa (pública en ~/.ssh/id_rsa.pub, privada en ~/.ssh/id_rsa) y copiar la pública al servidor con ssh-copy-id servidor, que la añade a ~/.ssh/authorized_keys (sección 9.2.1). | `debian_190` |
| DEB_D07 | Tengo bullseye-backports en las fuentes, pero APT me sigue instalando la versión antigua. ¿Cómo instalo la nueva? | APT no instala retroadaptaciones salvo que se le indique explícitamente: apt-get install paquete/bullseye-backports (o con -t bullseye-backports) (sección 6.1.2.4). | `debian_98` |
| DEB_D08 | Necesito que un comando se ejecute una sola vez mañana a las 9:00. ¿Qué uso y cómo lo cancelo si me arrepiento? | La orden at (p. ej. at 09:00 con el comando por la entrada estándar). atq lista las tareas pendientes y atrm número-tarea la cancela (sección 9.7.2). | `debian_203` |

### Combinan 2 fragmentos

| ID | Pregunta | Respuesta esperada | Chunks |
|---|---|---|---|
| DEB_C01 | Quiero que una copia de seguridad se lance cada día a las 3:00 en un portátil que a menudo está apagado a esa hora. ¿Cómo se escribe la programación y qué pasa si el equipo está apagado? | En crontab cada línea lleva minuto, hora, día del mes, mes, día de la semana (y usuario en /etc/crontab) y el programa, p. ej. 0 3 * * * (sección 9.7.1). Si el equipo está apagado la tarea de cron no se ejecuta; anacron sirve para lanzar esas tareas recurrentes teniendo en cuenta el tiempo que estuvo apagado (sección 9.8). | `debian_202`, `debian_204` |
| DEB_C02 | ¿En qué fichero se guarda realmente el hash de la contraseña de un usuario y por qué es más seguro que guardarlo en /etc/passwd? | En /etc/passwd el campo de contraseña vale «x», que indica que está en /etc/shadow (sección 8.4.1). /etc/shadow no lo pueden leer los usuarios normales, lo que evita ataques de diccionario sobre los hashes (sección 8.4.2). | `debian_157`, `debian_158` |
| DEB_C03 | Me falta un programa y solo sé el nombre del ejecutable. ¿Cómo averiguo qué paquete lo trae, aunque no esté instalado, y lo instalo? | Con apt-file search patrón (tras apt-file update) se ve qué paquete contiene ese archivo (sección 6.4), y luego se instala con apt install paquete (sección 6.2.2). | `debian_114`, `debian_105` |
| DEB_C04 | Voy a pasar un servidor de Buster a Bullseye. ¿Qué pasos sigo y cómo detecto después paquetes que ya no tienen versión en Debian? | Leer las notas de publicación y hacer copia de seguridad; cambiar /etc/apt/sources.list a Bullseye, apt update, primero apt upgrade y después apt full-upgrade (sección 6.7.1). Después, apt-show-versions | grep "No available version" o aptitude search ~o lista los paquetes sin versión disponible, que conviene purgar (sección 6.7.3). | `debian_120`, `debian_122` |

### Sin respuesta (abstención)

| ID | Pregunta | Respuesta esperada | Chunks |
|---|---|---|---|
| DEB_N01 | ¿Cómo instalo Docker en Debian? | No aparece en el documento. Docker solo se menciona de pasada en las secciones del cortafuegos (ufw/nftables), sin instrucciones de instalación.<br>*Nota: Pregunta trampa: 'Docker' aparece en debian_315 y debian_317.* | — |
| DEB_N02 | ¿En qué fecha exacta deja de tener soporte Debian 11? | No aparece en el documento. El manual dice que cada versión estable tiene unos 5 años de soporte (seguridad + LTS), pero no da una fecha concreta.<br>*Nota: Relacionado: debian_34 (esperanza de vida de unos 5 años).* | — |
| DEB_N03 | ¿Cómo instalo aplicaciones en formato Flatpak? | No aparece en el documento. | — |

## Problemas detectados en el chunking del BOE

Conviene corregirlos **antes** de empezar el benchmark (después ya no se puede tocar el chunking). Ninguna pregunta del golden set depende de estos chunks.

| Problema | Dónde | Efecto |
|---|---|---|
| Falta el **artículo 1** (ámbito de aplicación) | no hay chunk | Esa parte del Estatuto no se puede recuperar |
| El **artículo 58** está vacío (solo el título) | `boe_61` | Chunk sin contenido |
| El **artículo 82** está pegado dentro del 81, sin su título | `boe_84` | El chunk mezcla dos artículos y el LLM citará mal el 82 |
| El campo `estructura` de las disposiciones dice «Sección 2.ª Adhesión y extensión» | `boe_95` a `boe_137` | Metadato incorrecto (no afecta si no lo usáis) |
| Chunks muy largos: hasta ~15.000 caracteres en el BOE y ~27.000 en Debian (~4.000 y ~7.000 tokens) | p. ej. `boe_11`, `boe_38`, `debian_280` | Con top-5 el prompt del LLM puede pasar de 20.000 tokens: comprobad la ventana de contexto del servidor (p. ej. `num_ctx` en Ollama) |
