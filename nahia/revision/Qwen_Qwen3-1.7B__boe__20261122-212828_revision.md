# Revisión: Qwen/Qwen3-1.7B · boe
Retrieval: el fragmento correcto estaba en el top-k en 12 de 12 preguntas con respuesta.
Pistas automáticas (no son la nota): abstención = la respuesta contiene «No aparece en el documento».

## q_boe_01 · directa
**Pregunta:** ¿A partir de qué edad mínima se permite trabajar por cuenta ajena y en qué único supuesto excepcional puede autorizarse hacerlo antes?

**Esperada:** La edad mínima general es de dieciséis años. Excepcionalmente, la autoridad laboral puede autorizar por escrito y para actos determinados la intervención de menores de dieciséis años en espectáculos públicos, siempre que no suponga peligro para su salud ni para su formación profesional y humana (Artículo 6).

**Respuesta del modelo:** La edad mínima para trabajar por cuenta ajena es de dieciséis años. El único supuesto excepcional que permite autorizar el trabajo antes de esa edad es cuando la actividad no suponga peligro para la salud ni para la formación profesional y humana del menor, y el permiso deberá constar por escrito.

- Fragmento correcto en el top-k: sí
- Se abstiene (pista): no
- Cita artículo/sección (pista): no

## q_boe_02 · directa
**Pregunta:** ¿Cuál es la duración máxima permitida para un pacto de no competencia una vez extinguido el contrato de trabajo, tanto para los técnicos como para el resto de trabajadores?

**Esperada:** No puede superar los dos años para los técnicos ni los seis meses para los demás trabajadores, y exige que el empresario tenga un efectivo interés industrial o comercial y abone una compensación económica adecuada (Artículo 21).

**Respuesta del modelo:** La duración máxima permitida para un pacto de no competencia una vez extinguido el contrato de trabajo es de dos años para los técnicos y de seis meses para los demás trabajadores. Esto se establece en el artículo 21.2.

- Fragmento correcto en el top-k: sí
- Se abstiene (pista): no
- Cita artículo/sección (pista): sí

## q_boe_03 · directa
**Pregunta:** ¿Cuántas horas retribuidas al año corresponden para formación profesional vinculada a la actividad de la empresa y durante cuántos años como máximo se pueden acumular?

**Esperada:** Corresponden veinte horas anuales retribuidas para trabajadores con al menos un año de antigüedad, acumulables por un periodo de hasta cinco años (Artículo 23).

**Respuesta del modelo:** La respuesta es: 20 horas retribuidas al año corresponden para formación profesional vinculada a la actividad de la empresa y durante cuantos años como máximo se pueden acumular es de 5 años. 

Esta información se encuentra en el artículo 33.2 del documento.

- Fragmento correcto en el top-k: sí
- Se abstiene (pista): no
- Cita artículo/sección (pista): sí

## q_boe_04 · directa
**Pregunta:** ¿Qué porcentaje máximo de las percepciones salariales de una persona trabajadora puede abonarse en especie?

**Esperada:** El salario en especie no puede superar en ningún caso el treinta por ciento de las percepciones salariales del trabajador ni minorar la cuantía íntegra en dinero del salario mínimo interprofesional (Artículo 26).

**Respuesta del modelo:** El porcentaje máximo de las percepciones salariales de una persona trabajadora que puede abonarse en especie es el **treinta por ciento (30%)**. Este se establece en el artículo 26, numeral 1.

- Fragmento correcto en el top-k: sí
- Se abstiene (pista): no
- Cita artículo/sección (pista): sí

## q_boe_05 · directa
**Pregunta:** ¿Qué porcentaje de recargo por demora se aplica cuando la empresa se retrasa en el abono del salario?

**Esperada:** El interés por mora en el pago del salario es del diez por ciento de lo adeudado (Artículo 29).

**Respuesta del modelo:** No aparece en el documento.

- Fragmento correcto en el top-k: sí
- Se abstiene (pista): sí
- Cita artículo/sección (pista): sí

## q_boe_06 · directa
**Pregunta:** ¿Qué tipos de sanciones tiene expresamente prohibido imponer la empresa a una persona trabajadora por incumplimientos laborales?

**Esperada:** No se pueden imponer sanciones que consistan en la reducción de la duración de las vacaciones, otra minoración de los derechos al descanso del trabajador ni multa de haber (Artículo 58).

**Respuesta del modelo:** La empresa no puede imponer sanciones que consistan en la reducción de la duración de las vacaciones u otra minoración de los derechos al descanso del trabajador. Esta sanción está expresamente prohibida en el artículo 58.

- Fragmento correcto en el top-k: sí
- Se abstiene (pista): no
- Cita artículo/sección (pista): sí

## q_boe_07 · directa
**Pregunta:** ¿De cuántos días hábiles dispone una persona trabajadora para impugnar un despido y cuándo caduca ese plazo?

**Esperada:** La acción contra el despido caduca a los veinte días hábiles siguientes a aquel en que se hubiera producido, quedando interrumpido el plazo por la presentación de la solicitud de conciliación (Artículo 59).

**Respuesta del modelo:** La persona trabajadora dispone de 20 días hábiles para impugnar un despido. Este plazo caduca a los 20 días siguientes de la fecha en que se hubiera producido el despido.

- Fragmento correcto en el top-k: sí
- Se abstiene (pista): no
- Cita artículo/sección (pista): no

## q_boe_08 · directa
**Pregunta:** ¿En qué plazos prescriben las faltas leves, graves y muy graves de los trabajadores desde que la empresa tiene conocimiento de ellas?

**Esperada:** Las faltas leves prescriben a los diez días, las graves a los veinte días y las muy graves a los sesenta días desde que la empresa tuvo conocimiento de su comisión, y en todo caso a los seis meses de haberse cometido (Artículo 60).

**Respuesta del modelo:** Las faltas leves prescribirán a los diez días, las graves a los veinte días y las muy graves a los sesenta días a partir de la fecha en que la empresa tuvo conocimiento de su comisión.

- Fragmento correcto en el top-k: sí
- Se abstiene (pista): no
- Cita artículo/sección (pista): no

## q_boe_09 · combinada
**Pregunta:** En una empresa con exactamente cincuenta trabajadores en su centro de trabajo, ¿a partir de qué porcentaje de brecha salarial entre sexos debe justificarse la diferencia en el registro retributivo y cuántos miembros componen su comité de empresa?

**Esperada:** Cuando el promedio retributivo de un sexo supere al del otro en un veinticinco por ciento o más debe incluirse una justificación en el registro salarial (Artículo 28), y su comité de empresa estará compuesto por cinco miembros (Artículo 66).

**Respuesta del modelo:** En una empresa con exactamente cincuenta trabajadores en su centro de trabajo, la diferencia salarial entre sexos debe justificarse en el registro retributivo cuando el promedio de las retribuciones a los trabajadores de un sexo sea superior a los del otro en un veinticinco por ciento o más. El comité de empresa tendrá trece miembros.

- Fragmento correcto en el top-k: sí
- Se abstiene (pista): no
- Cita artículo/sección (pista): no

## q_boe_10 · combinada
**Pregunta:** ¿Cuántas mensualidades completas adeudadas en un año permiten al trabajador pedir la extinción indemnizada de su contrato, y puede la empresa extinguir el contrato por causas objetivas alegando una ineptitud previa al cumplimiento del periodo de prueba?

**Esperada:** El trabajador puede solicitar la extinción cuando se le adeuden tres mensualidades completas en un año o haya retrasos durante seis meses, aun no consecutivos (Artículo 50). Por su parte, la empresa no puede alegar con posterioridad una ineptitud que ya existía antes de cumplirse el periodo de prueba (Artículo 52).

**Respuesta del modelo:** La respuesta es: No aparece en el documento.

Explicación: La pregunta sobre el número de mensualidades completas adeudadas en un año que permiten pedir la extinción indemnizada de su contrato no se encuentra en los fragmentos proporcionados. Además, la pregunta sobre si la empresa puede extinguir el contrato por causas objetivas alegando una ineptitud previa al cumplimiento del periodo de prueba tampoco se encuentra en los fragmentos.

- Fragmento correcto en el top-k: sí
- Se abstiene (pista): sí
- Cita artículo/sección (pista): sí

## q_boe_11 · combinada
**Pregunta:** ¿Con qué antelación mínima debe comunicar la persona trabajadora a la empresa el disfrute del permiso parental de hasta ocho semanas, y con cuántas horas mínimas de antelación debe comunicarse la convocatoria de una asamblea de trabajadores?

**Esperada:** El permiso parental debe comunicarse a la empresa con una antelación mínima de diez días, salvo fuerza mayor o plazo distinto en convenio (Artículo 48 bis), mientras que la convocatoria de una asamblea de trabajadores debe comunicarse con al menos cuarenta y ocho horas de antelación (Artículo 79).

**Respuesta del modelo:** El disfrute del permiso parental de hasta ocho semanas debe comunicarse a la empresa con una antelación de diez días, según el artículo 48 bis. 

La convocatoria de una asamblea de trabajadores debe comunicarse al empresario con una antelación de cuarenta y ocho horas, según el artículo 77.

- Fragmento correcto en el top-k: sí
- Se abstiene (pista): no
- Cita artículo/sección (pista): sí

## q_boe_12 · combinada
**Pregunta:** ¿A partir de cuántos trabajadores en un centro de trabajo se constituye un comité de empresa en lugar de delegados de personal, y cuántos delegados corresponden si hay cuarenta empleados?

**Esperada:** El comité de empresa se constituye en centros de cincuenta o más trabajadores (Artículo 63); con cuarenta empleados corresponden tres delegados de personal, que es el número fijado para centros de entre treinta y uno y cuarenta y nueve trabajadores (Artículo 62).

**Respuesta del modelo:** Según el artículo 62, el comité de empresa se constituye en cada centro de trabajo cuyo censo sea de cincuenta o más trabajadores. Si hay cuarenta empleados en un centro de trabajo, no se constituye un comité de empresa, sino que corresponde a los delegados de personal.

Por lo tanto, no se constituye un comité de empresa en un centro de trabajo con cuarenta empleados, y los delegados de personal corresponden en número de uno.

- Fragmento correcto en el top-k: sí
- Se abstiene (pista): no
- Cita artículo/sección (pista): sí

## q_boe_13 · sin_respuesta
**Pregunta:** ¿Cuál es la cuantía exacta en euros del Salario Mínimo Interprofesional mensual fijada para el año en curso?

**Esperada:** No aparece en el documento

**Respuesta del modelo:** No aparece en el documento.

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
