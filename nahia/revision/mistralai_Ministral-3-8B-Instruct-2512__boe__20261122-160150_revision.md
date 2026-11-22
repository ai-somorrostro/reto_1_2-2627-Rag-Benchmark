# Revisión: mistralai/Ministral-3-8B-Instruct-2512 · boe
Retrieval: el fragmento correcto estaba en el top-k en 12 de 12 preguntas con respuesta.
Pistas automáticas (no son la nota): abstención = la respuesta contiene «No aparece en el documento».

## q_boe_01 · directa
**Pregunta:** ¿A partir de qué edad mínima se permite trabajar por cuenta ajena y en qué único supuesto excepcional puede autorizarse hacerlo antes?

**Esperada:** La edad mínima general es de dieciséis años. Excepcionalmente, la autoridad laboral puede autorizar por escrito y para actos determinados la intervención de menores de dieciséis años en espectáculos públicos, siempre que no suponga peligro para su salud ni para su formación profesional y humana (Artículo 6).

**Respuesta del modelo:** Según los fragmentos proporcionados:

- **Edad mínima para trabajar por cuenta ajena**: Se permite a partir de los **16 años** (Artículo 6.1 y Artículo 7.b).

- **Único supuesto excepcional para autorizarse antes de los 16 años**: La intervención en **espectáculos públicos**, siempre que sea por escrito, para actos determinados, no suponga peligro para su salud ni formación, y esté autorizada por la **autoridad laboral** (Artículo 6.4).

- Fragmento correcto en el top-k: sí
- Se abstiene (pista): no
- Cita artículo/sección (pista): sí

## q_boe_02 · directa
**Pregunta:** ¿Cuál es la duración máxima permitida para un pacto de no competencia una vez extinguido el contrato de trabajo, tanto para los técnicos como para el resto de trabajadores?

**Esperada:** No puede superar los dos años para los técnicos ni los seis meses para los demás trabajadores, y exige que el empresario tenga un efectivo interés industrial o comercial y abone una compensación económica adecuada (Artículo 21).

**Respuesta del modelo:** La duración máxima permitida para un pacto de no competencia una vez extinguido el contrato de trabajo es:

- **Para técnicos**: hasta **dos años** (Artículo 21, apartado 2).
- **Para los demás trabajadores**: hasta **seis meses** (Artículo 21, apartado 2).

- Fragmento correcto en el top-k: sí
- Se abstiene (pista): no
- Cita artículo/sección (pista): sí

## q_boe_03 · directa
**Pregunta:** ¿Cuántas horas retribuidas al año corresponden para formación profesional vinculada a la actividad de la empresa y durante cuántos años como máximo se pueden acumular?

**Esperada:** Corresponden veinte horas anuales retribuidas para trabajadores con al menos un año de antigüedad, acumulables por un periodo de hasta cinco años (Artículo 23).

**Respuesta del modelo:** Según el **Artículo 23. Promoción y formación profesional en el trabajo**, apartado 3:

- **Horas retribuidas anuales**: Los trabajadores con al menos un año de antigüedad en la empresa tienen derecho a **20 horas anuales de formación profesional para el empleo**, vinculada a la actividad de la empresa.
- **Acumulación máxima**: Estas horas pueden acumularse por un período de **hasta cinco años**.

- Fragmento correcto en el top-k: sí
- Se abstiene (pista): no
- Cita artículo/sección (pista): sí

## q_boe_04 · directa
**Pregunta:** ¿Qué porcentaje máximo de las percepciones salariales de una persona trabajadora puede abonarse en especie?

**Esperada:** El salario en especie no puede superar en ningún caso el treinta por ciento de las percepciones salariales del trabajador ni minorar la cuantía íntegra en dinero del salario mínimo interprofesional (Artículo 26).

**Respuesta del modelo:** Según el **Artículo 26.1**, el salario en especie **no podrá superar el treinta por ciento** de las percepciones salariales del trabajador.

- Fragmento correcto en el top-k: sí
- Se abstiene (pista): no
- Cita artículo/sección (pista): sí

## q_boe_05 · directa
**Pregunta:** ¿Qué porcentaje de recargo por demora se aplica cuando la empresa se retrasa en el abono del salario?

**Esperada:** El interés por mora en el pago del salario es del diez por ciento de lo adeudado (Artículo 29).

**Respuesta del modelo:** El interés por mora en el pago del salario será el **diez por ciento** de lo adeudado.
*(Artículo 29. Liquidación y pago, apartado 3).*

- Fragmento correcto en el top-k: sí
- Se abstiene (pista): no
- Cita artículo/sección (pista): sí

## q_boe_06 · directa
**Pregunta:** ¿Qué tipos de sanciones tiene expresamente prohibido imponer la empresa a una persona trabajadora por incumplimientos laborales?

**Esperada:** No se pueden imponer sanciones que consistan en la reducción de la duración de las vacaciones, otra minoración de los derechos al descanso del trabajador ni multa de haber (Artículo 58).

**Respuesta del modelo:** Según el **Artículo 58.3**, la empresa **no podrá imponer sanciones que consistan en**:

- La **reducción de la duración de las vacaciones** del trabajador.
- **Otra minoración de los derechos al descanso** del trabajador.
- **Multa de haber** (es decir, descontar salario como sanción).

*No aparece en el documento* cualquier otra prohibición específica sobre tipos de sanciones.

- Fragmento correcto en el top-k: sí
- Se abstiene (pista): sí
- Cita artículo/sección (pista): sí

## q_boe_07 · directa
**Pregunta:** ¿De cuántos días hábiles dispone una persona trabajadora para impugnar un despido y cuándo caduca ese plazo?

**Esperada:** La acción contra el despido caduca a los veinte días hábiles siguientes a aquel en que se hubiera producido, quedando interrumpido el plazo por la presentación de la solicitud de conciliación (Artículo 59).

**Respuesta del modelo:** El plazo de caducidad para impugnar un despido es de **20 días hábiles**, y este plazo caduca desde el día siguiente a la fecha en que se hubiera producido el despido.

*Fuente: Artículo 59.3* (segunda mención del artículo).

- Fragmento correcto en el top-k: sí
- Se abstiene (pista): no
- Cita artículo/sección (pista): sí

## q_boe_08 · directa
**Pregunta:** ¿En qué plazos prescriben las faltas leves, graves y muy graves de los trabajadores desde que la empresa tiene conocimiento de ellas?

**Esperada:** Las faltas leves prescriben a los diez días, las graves a los veinte días y las muy graves a los sesenta días desde que la empresa tuvo conocimiento de su comisión, y en todo caso a los seis meses de haberse cometido (Artículo 60).

**Respuesta del modelo:** Las faltas leves prescriben a los **10 días**, las graves a los **20 días** y las muy graves a los **60 días** desde que la empresa tuvo conocimiento de su comisión.

*Fuente: Artículo 60.2.*

- Fragmento correcto en el top-k: sí
- Se abstiene (pista): no
- Cita artículo/sección (pista): sí

## q_boe_09 · combinada
**Pregunta:** En una empresa con exactamente cincuenta trabajadores en su centro de trabajo, ¿a partir de qué porcentaje de brecha salarial entre sexos debe justificarse la diferencia en el registro retributivo y cuántos miembros componen su comité de empresa?

**Esperada:** Cuando el promedio retributivo de un sexo supere al del otro en un veinticinco por ciento o más debe incluirse una justificación en el registro salarial (Artículo 28), y su comité de empresa estará compuesto por cinco miembros (Artículo 66).

**Respuesta del modelo:** En una empresa con exactamente **cincuenta trabajadores**, según el **Artículo 28.2** y **Artículo 28.3**:

- **Brecha salarial**: Debe justificarse la diferencia cuando el promedio de las retribuciones de un sexo sea superior al del otro en **un 25% o más** (tomando el conjunto de la masa salarial o la media de las percepciones).
- **Miembros del comité de empresa**: Según el **Artículo 66.1.a**, en una empresa de **50 a 100 trabajadores**, el comité de empresa está compuesto por **5 miembros**.

- Fragmento correcto en el top-k: sí
- Se abstiene (pista): no
- Cita artículo/sección (pista): sí

## q_boe_10 · combinada
**Pregunta:** ¿Cuántas mensualidades completas adeudadas en un año permiten al trabajador pedir la extinción indemnizada de su contrato, y puede la empresa extinguir el contrato por causas objetivas alegando una ineptitud previa al cumplimiento del periodo de prueba?

**Esperada:** El trabajador puede solicitar la extinción cuando se le adeuden tres mensualidades completas en un año o haya retrasos durante seis meses, aun no consecutivos (Artículo 50). Por su parte, la empresa no puede alegar con posterioridad una ineptitud que ya existía antes de cumplirse el periodo de prueba (Artículo 52).

**Respuesta del modelo:** 1. Según el **Artículo 50.1.b)**, el trabajador podrá solicitar la extinción indemnizada del contrato si hay **tres mensualidades completas de salario adeudadas en un año** (aunque no sean consecutivas), o si hay retrasos en el pago del salario durante **seis meses** (también no consecutivos).

2. Según el **Artículo 52** (apartado a), la ineptitud **existente con anterioridad al cumplimiento del periodo de prueba no podrá alegarse con posterioridad a dicho cumplimiento**. Por lo tanto, **no puede la empresa extinguir el contrato por causas objetivas alegando una ineptitud previa al periodo de prueba**.

- Fragmento correcto en el top-k: sí
- Se abstiene (pista): no
- Cita artículo/sección (pista): sí

## q_boe_11 · combinada
**Pregunta:** ¿Con qué antelación mínima debe comunicar la persona trabajadora a la empresa el disfrute del permiso parental de hasta ocho semanas, y con cuántas horas mínimas de antelación debe comunicarse la convocatoria de una asamblea de trabajadores?

**Esperada:** El permiso parental debe comunicarse a la empresa con una antelación mínima de diez días, salvo fuerza mayor o plazo distinto en convenio (Artículo 48 bis), mientras que la convocatoria de una asamblea de trabajadores debe comunicarse con al menos cuarenta y ocho horas de antelación (Artículo 79).

**Respuesta del modelo:** Según los fragmentos proporcionados:

1. **Permiso parental**:
   La persona trabajadora debe comunicar a la empresa el disfrute del permiso parental con una antelación mínima de **diez días** (Artículo 48 bis, apartado 2).

2. **Convocatoria de asamblea de trabajadores**:
   La convocatoria debe comunicarse al empresario con **cuarenta y ocho horas de antelación, como mínimo** (Artículo 79).

- Fragmento correcto en el top-k: sí
- Se abstiene (pista): no
- Cita artículo/sección (pista): sí

## q_boe_12 · combinada
**Pregunta:** ¿A partir de cuántos trabajadores en un centro de trabajo se constituye un comité de empresa en lugar de delegados de personal, y cuántos delegados corresponden si hay cuarenta empleados?

**Esperada:** El comité de empresa se constituye en centros de cincuenta o más trabajadores (Artículo 63); con cuarenta empleados corresponden tres delegados de personal, que es el número fijado para centros de entre treinta y uno y cuarenta y nueve trabajadores (Artículo 62).

**Respuesta del modelo:** Según el **Artículo 62** y el **Artículo 63** del documento:

- **Comité de empresa**: Se constituye en cada centro de trabajo que tenga **50 o más trabajadores** (*Artículo 63.1*).
- **Delegados de personal**: Se aplican en empresas o centros de trabajo con **menos de 50 trabajadores** (y desde 6 hasta 10 si así lo deciden los trabajadores por mayoría). Para **40 empleados**, el número de delegados de personal sería **uno** (*Artículo 62.1*).

*Resumen*: A partir de **50 trabajadores**, se constituye un comité de empresa; con **40 empleados**, habrá **1 delegado de personal**.

- Fragmento correcto en el top-k: sí
- Se abstiene (pista): no
- Cita artículo/sección (pista): sí

## q_boe_13 · sin_respuesta
**Pregunta:** ¿Cuál es la cuantía exacta en euros del Salario Mínimo Interprofesional mensual fijada para el año en curso?

**Esperada:** No aparece en el documento

**Respuesta del modelo:** No aparece en el documento.

*(El texto proporcionado solo regula el procedimiento para fijar el SMI, pero no indica la cuantía concreta en euros para ningún año, incluyendo el año en curso).*

- Fragmento correcto en el top-k: n/a (sin respuesta)
- Se abstiene (pista): sí
- Cita artículo/sección (pista): sí

## q_boe_14 · sin_respuesta
**Pregunta:** ¿Qué porcentaje de retención de IRPF se aplica en la nómina sobre las gratificaciones extraordinarias?

**Esperada:** No aparece en el documento

**Respuesta del modelo:** No aparece en el documento.

- Fragmento correcto en el top-k: n/a (sin respuesta)
- Se abstiene (pista): sí
- Cita artículo/sección (pista): sí

## q_boe_15 · sin_respuesta
**Pregunta:** ¿Cuál es el importe mínimo por kilómetro que debe abonar la empresa en concepto de dietas y kilometraje por desplazamiento?

**Esperada:** No aparece en el documento

**Respuesta del modelo:** No aparece en el documento.

- Fragmento correcto en el top-k: n/a (sin respuesta)
- Se abstiene (pista): sí
- Cita artículo/sección (pista): sí
