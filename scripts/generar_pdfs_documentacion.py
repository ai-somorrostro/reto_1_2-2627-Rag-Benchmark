# -*- coding: utf-8 -*-
import os
import sys
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import cm
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, HRFlowable
)
from reportlab.pdfgen import canvas

class NumberedCanvas(canvas.Canvas):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_header_footer(num_pages)
            super().showPage()
        super().save()

    def draw_header_footer(self, page_count):
        self.saveState()
        self.setFont("Helvetica-Bold", 8)
        self.setFillColor(colors.HexColor("#64748b"))
        
        # Header (pages > 1)
        if self._pageNumber > 1:
            header_title = getattr(self, "doc_title", "Benchmark RAG · Grupo 1")
            self.drawString(36, A4[1] - 26, header_title)
            self.setStrokeColor(colors.HexColor("#cbd5e1"))
            self.setLineWidth(0.5)
            self.line(36, A4[1] - 30, A4[0] - 36, A4[1] - 30)
            
        # Footer (all pages)
        self.setFont("Helvetica", 8)
        self.setFillColor(colors.HexColor("#64748b"))
        self.drawString(36, 20, "Práctica: Benchmark de LLMs y Embeddings Locales para RAG — Grupo 1")
        page_str = f"Página {self._pageNumber} de {page_count}"
        self.drawRightString(A4[0] - 36, 20, page_str)
        self.setStrokeColor(colors.HexColor("#cbd5e1"))
        self.setLineWidth(0.5)
        self.line(36, 28, A4[0] - 36, 28)
        
        self.restoreState()


def get_styles():
    base = getSampleStyleSheet()
    styles = {
        "Title": ParagraphStyle(
            "DocTitle",
            parent=base["Normal"],
            fontName="Helvetica-Bold",
            fontSize=16,
            leading=20,
            textColor=colors.HexColor("#0f172a"),
            spaceAfter=3,
        ),
        "Subtitle": ParagraphStyle(
            "DocSubtitle",
            parent=base["Normal"],
            fontName="Helvetica",
            fontSize=9.5,
            leading=13,
            textColor=colors.HexColor("#2563eb"),
            spaceAfter=8,
        ),
        "Heading1": ParagraphStyle(
            "SectionH1",
            parent=base["Normal"],
            fontName="Helvetica-Bold",
            fontSize=11,
            leading=14,
            textColor=colors.HexColor("#0f172a"),
            spaceBefore=7,
            spaceAfter=4,
            keepWithNext=True,
        ),
        "Heading2": ParagraphStyle(
            "SectionH2",
            parent=base["Normal"],
            fontName="Helvetica-Bold",
            fontSize=9.5,
            leading=12,
            textColor=colors.HexColor("#1e40af"),
            spaceBefore=5,
            spaceAfter=3,
            keepWithNext=True,
        ),
        "Body": ParagraphStyle(
            "BodyDark",
            parent=base["Normal"],
            fontName="Helvetica",
            fontSize=8,
            leading=11,
            textColor=colors.HexColor("#1e293b"),
            spaceAfter=3,
        ),
        "BodyBold": ParagraphStyle(
            "BodyDarkBold",
            parent=base["Normal"],
            fontName="Helvetica-Bold",
            fontSize=8,
            leading=11,
            textColor=colors.HexColor("#0f172a"),
            spaceAfter=3,
        ),
        "Callout": ParagraphStyle(
            "CalloutText",
            parent=base["Normal"],
            fontName="Helvetica",
            fontSize=7.8,
            leading=10.5,
            textColor=colors.HexColor("#0f172a"),
        ),
        "TableHeader": ParagraphStyle(
            "TableHead",
            parent=base["Normal"],
            fontName="Helvetica-Bold",
            fontSize=7.5,
            leading=9.5,
            textColor=colors.white,
            alignment=1,
        ),
        "TableCell": ParagraphStyle(
            "TableBody",
            parent=base["Normal"],
            fontName="Helvetica",
            fontSize=7.2,
            leading=9,
            textColor=colors.HexColor("#1e293b"),
        ),
        "TableCellBold": ParagraphStyle(
            "TableBodyBold",
            parent=base["Normal"],
            fontName="Helvetica-Bold",
            fontSize=7.2,
            leading=9,
            textColor=colors.HexColor("#0f172a"),
        ),
        "TableCellCenter": ParagraphStyle(
            "TableBodyCenter",
            parent=base["Normal"],
            fontName="Helvetica",
            fontSize=7.2,
            leading=9,
            textColor=colors.HexColor("#1e293b"),
            alignment=1,
        ),
    }
    return styles


def make_callout(text, styles, bg_color="#eff6ff", border_color="#3b82f6"):
    p = Paragraph(text, styles["Callout"])
    t = Table([[p]], colWidths=[A4[0] - 72])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor(bg_color)),
        ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor(border_color)),
        ("LINEBEFORE", (0, 0), (0, -1), 3.5, colors.HexColor(border_color)),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ("LEFTPADDING", (0, 0), (-1, -1), 7),
        ("RIGHTPADDING", (0, 0), (-1, -1), 7),
    ]))
    return t


# ===========================================================================
# PDF 1: GUÍA EXPLICATIVA DEL PROYECTO (CÓDIGO, FASES Y RESULTADOS)
# ===========================================================================
def generar_pdf_proyecto(ruta_salida):
    doc = SimpleDocTemplate(
        ruta_salida,
        pagesize=A4,
        leftMargin=36,
        rightMargin=36,
        topMargin=38,
        bottomMargin=34,
    )
    styles = get_styles()
    story = []

    # --- PÁGINA 1: Contexto, Código y Fase 1 ---
    story.append(Paragraph("Guía Técnica y Resumen del Proyecto RAG", styles["Title"]))
    story.append(Paragraph("Estructura de Código, Metodología de Chunking, Fases 1 a 4 y Resultados Clave · Grupo 1", styles["Subtitle"]))
    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#2563eb"), spaceAfter=6))

    story.append(Paragraph("1. Objetivo y Stack de Inferencia Unificado", styles["Heading1"]))
    p1 = (
        "<b>Objetivo:</b> Decidir con datos empíricos qué embedding y qué LLM usar en un sistema RAG para dos dominios: "
        "<i>Estatuto de los Trabajadores</i> (normativa jurídica, citas milimétricas) y <i>Manual de Debian</i> "
        "(documentación técnica, comandos, rutas y términos en inglés).<br/>"
        "<b>Stack Técnico:</b> Servidor con NVIDIA A800 40GB (partición MIG <code>3g.20gb</code>, 20 GB VRAM). Todo el "
        "benchmark está unificado en <b>vLLM 0.34.0</b> (PyTorch 2.14.0+cu130) con pesos en <b>FP8</b> "
        "(solo-pesos vía kernel Marlin en Ampere) y <b>caché KV fijada a 2.0 GB</b> para asegurar comparativas deterministas de memoria."
    )
    story.append(Paragraph(p1, styles["Body"]))

    story.append(Paragraph("2. Mapa y Contexto del Código", styles["Heading1"]))
    files_data = [
        [Paragraph("Fichero / Script", styles["TableHeader"]), Paragraph("Módulo / Fase", styles["TableHeader"]), Paragraph("Descripción Breve y Propósito", styles["TableHeader"])],
        [Paragraph("<code>scripts/convertir_boe.py</code>", styles["TableCellBold"]), Paragraph("Fase 1: Extracción BOE", styles["TableCell"]), Paragraph("Convierte el PDF con Docling; filtra cabeceras, pies y números de página con regex; recompone saltos de párrafo en <code>boe_limpio.md</code>.", styles["TableCell"])],
        [Paragraph("<code>scripts/convertir_debian.py</code>", styles["TableCellBold"]), Paragraph("Fase 1: Extracción Debian", styles["TableCell"]), Paragraph("Desempaqueta el EPUB oficial en español, preserva la jerarquía de secciones y convierte bloques de pantalla en bloques de código en <code>debian.md</code>.", styles["TableCell"])],
        [Paragraph("<code>scripts/trocear.py</code>", styles["TableCellBold"]), Paragraph("Fase 1: Chunking Semántico", styles["TableCell"]), Paragraph("Trocea respetando párrafos y código a máx. 1.800 caracteres (~450 tokens). Inyecta encabezados jerárquicos y enlaces adyacentes (<code>boe_final.json</code> y <code>debian_final.json</code>).", styles["TableCell"])],
        [Paragraph("<code>golden-set/golden_*.jsonl</code>", styles["TableCellBold"]), Paragraph("Fase 1: Golden Set", styles["TableCell"]), Paragraph("15 preguntas calibradas por escenario (8 directas, 4 combinadas y 3 sin respuesta para abstención). Respuestas esperadas y chunks gold vinculados.", styles["TableCell"])],
        [Paragraph("<code>scripts/run_all_embeddings.py</code><br/><code>scripts/benchmark_embeddings_vllm.py</code>", styles["TableCellBold"]), Paragraph("Fase 2: Retrieval", styles["TableCell"]), Paragraph("Indexa en vLLM, almacena vectores en disco (<code>.npy</code>) y calcula Recall@1, 3, 5 y MRR aislando cada ejecución en un subproceso con log continuo de VRAM.", styles["TableCell"])],
        [Paragraph("<code>scripts/benchmark_llms_vllm.py</code>", styles["TableCellBold"]), Paragraph("Fase 3: Inferencia LLMs", styles["TableCell"]), Paragraph("Inferencia offline en vLLM con top-k=5 fijo, temp=0, max_tokens=512. Mide coste (TTFT, tok/s, latencia) y ejecuta la prueba del Oráculo inyectando el chunk exacto.", styles["TableCell"])],
        [Paragraph("<code>scripts/generar_tablas_llm.py</code>", styles["TableCellBold"]), Paragraph("Fase 3: Tablas B y C", styles["TableCell"]), Paragraph("Compila resultados brutos y evaluaciones manuales para emitir <code>results/llms/tablas_b_c.md</code>.", styles["TableCell"])],
        [Paragraph("<code>scripts/auditar_trazabilidad.py</code>", styles["TableCellBold"]), Paragraph("Auditoría Formal", styles["TableCell"]), Paragraph("Comprueba la correspondencia exacta entre las tablas consolidadas, los JSONs brutos y las evaluaciones de los CSVs.", styles["TableCell"])],
        [Paragraph("<code>decision_fase4.md</code>", styles["TableCellBold"]), Paragraph("Fase 4: Decisión y Plan B", styles["TableCell"]), Paragraph("Documento con los umbrales de decisión, frases justificativas, análisis de sensibilidad, Plan B (8 GB) y anomalías técnicas.", styles["TableCell"])],
    ]
    t_files = Table(files_data, colWidths=[4.2 * cm, 3.6 * cm, 10.9 * cm])
    t_files.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1e293b")),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
        ("TOPPADDING", (0, 0), (-1, -1), 2.5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 2.5),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f8fafc")]),
    ]))
    story.append(t_files)

    story.append(Paragraph("3. Fase 1: Metodología de Chunking y Golden Set", styles["Heading1"]))
    p_f1 = (
        "• <b>Limpieza de documentos:</b> En el BOE se eliminaron cabeceras ('BOLETÍN OFICIAL DEL ESTADO') y numeraciones de página para evitar ruido en el contexto. En Debian se extrajeron los ficheros XHTML del EPUB manteniendo las etiquetas de código <code>&lt;pre&gt;</code>.<br/>"
        "• <b>Algoritmo de Chunking (<code>scripts/trocear.py</code>):</b> Divide el documento respetando límites naturales de párrafo y bloques de código. Tamaño máximo acotado a <b>1.800 caracteres</b> (~450-500 tokens). Si una sección excede ese límite, se trocea inyectando el encabezado en cada parte: <code>Título (parte N de M)</code> y enlazando los IDs del fragmento anterior y siguiente. Generó <b>348 chunks</b> en el BOE y <b>1.018 chunks</b> en Debian.<br/>"
        "• <b>Golden Set:</b> 15 preguntas por escenario (8 directas con 1 chunk, 4 combinadas que requieren relacionar 2 chunks y 3 preguntas trampa sin respuesta). Se redactaron con paráfrasis para evitar que el retriever gane por solapamiento léxico superficial."
    )
    story.append(Paragraph(p_f1, styles["Body"]))

    story.append(PageBreak())

    # --- PÁGINA 2: Fases 2, 3, 4 y Hallazgos ---
    story.append(Paragraph("4. Fase 2: Benchmark de Embeddings (Tabla A)", styles["Heading1"]))
    story.append(Paragraph("Se evaluaron 3 modelos multilingües de ~600M parámetros. Harrier y Qwen3 requirieron prefijo (<code>Instruct: ...\nQuery: ...</code>):", styles["Body"]))
    
    emb_data = [
        [Paragraph("Escenario", styles["TableHeader"]), Paragraph("Modelo", styles["TableHeader"]), Paragraph("Params", styles["TableHeader"]), Paragraph("Recall@5 (Hit)", styles["TableHeader"]), Paragraph("Recall@5 (Estricto)", styles["TableHeader"]), Paragraph("MRR", styles["TableHeader"]), Paragraph("Indexado", styles["TableHeader"]), Paragraph("VRAM", styles["TableHeader"])],
        [Paragraph("<b>BOE</b>", styles["TableCellBold"]), Paragraph("BAAI/bge-m3", styles["TableCell"]), Paragraph("568M", styles["TableCellCenter"]), Paragraph("0.8333", styles["TableCellCenter"]), Paragraph("0.5833", styles["TableCellCenter"]), Paragraph("0.6983", styles["TableCellCenter"]), Paragraph("1.06 s", styles["TableCellCenter"]), Paragraph("1.89 GB", styles["TableCellCenter"])],
        [Paragraph("<b>BOE</b>", styles["TableCellBold"]), Paragraph("Qwen3-Embedding-0.6B", styles["TableCell"]), Paragraph("600M", styles["TableCellCenter"]), Paragraph("0.8333", styles["TableCellCenter"]), Paragraph("0.7500", styles["TableCellCenter"]), Paragraph("0.6991", styles["TableCellCenter"]), Paragraph("1.59 s", styles["TableCellCenter"]), Paragraph("3.51 GB", styles["TableCellCenter"])],
        [Paragraph("<b>BOE (G)</b>", styles["TableCellBold"]), Paragraph("<b>harrier-oss-v1-0.6b</b>", styles["TableCellBold"]), Paragraph("600M", styles["TableCellCenter"]), Paragraph("<b>1.0000</b>", styles["TableCellCenter"]), Paragraph("<b>1.0000</b>", styles["TableCellCenter"]), Paragraph("<b>0.7361</b>", styles["TableCellCenter"]), Paragraph("1.60 s", styles["TableCellCenter"]), Paragraph("3.51 GB", styles["TableCellCenter"])],
        [Paragraph("<b>Debian (G)</b>", styles["TableCellBold"]), Paragraph("<b>BAAI/bge-m3</b>", styles["TableCellBold"]), Paragraph("568M", styles["TableCellCenter"]), Paragraph("<b>0.8333</b>", styles["TableCellCenter"]), Paragraph("0.6667", styles["TableCellCenter"]), Paragraph("<b>0.6219</b>", styles["TableCellCenter"]), Paragraph("3.52 s", styles["TableCellCenter"]), Paragraph("1.90 GB", styles["TableCellCenter"])],
        [Paragraph("<b>Debian</b>", styles["TableCellBold"]), Paragraph("Qwen3-Embedding-0.6B", styles["TableCell"]), Paragraph("600M", styles["TableCellCenter"]), Paragraph("0.7500", styles["TableCellCenter"]), Paragraph("0.5833", styles["TableCellCenter"]), Paragraph("0.5769", styles["TableCellCenter"]), Paragraph("5.29 s", styles["TableCellCenter"]), Paragraph("3.49 GB", styles["TableCellCenter"])],
        [Paragraph("<b>Debian</b>", styles["TableCellBold"]), Paragraph("harrier-oss-v1-0.6b", styles["TableCell"]), Paragraph("600M", styles["TableCellCenter"]), Paragraph("0.7500", styles["TableCellCenter"]), Paragraph("0.7500", styles["TableCellCenter"]), Paragraph("0.5573", styles["TableCellCenter"]), Paragraph("5.34 s", styles["TableCellCenter"]), Paragraph("3.51 GB", styles["TableCellCenter"])],
    ]
    t_emb = Table(emb_data, colWidths=[2.2 * cm, 4.4 * cm, 1.5 * cm, 2.5 * cm, 2.7 * cm, 1.7 * cm, 1.7 * cm, 2.0 * cm])
    t_emb.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#0f766e")),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
        ("TOPPADDING", (0, 0), (-1, -1), 2),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 2),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f0fdfa")]),
        ("BACKGROUND", (0, 3), (-1, 3), colors.HexColor("#dcfce7")),
        ("BACKGROUND", (0, 4), (-1, 4), colors.HexColor("#dcfce7")),
    ]))
    story.append(t_emb)
    story.append(Paragraph(
        "<b>Decisión de Retrieval:</b> En el BOE gana <b>harrier-oss-v1</b> (100% acierto en Recall@5). En Debian gana <b>bge-m3</b> (único ≥ 0.80 Recall@5); harrier colapsa al 75% al enfrentarse a comandos y terminología técnica en inglés.",
        styles["BodyBold"]
    ))

    story.append(Paragraph("5. Fase 3: Benchmark de LLMs · Calidad, Coste y Prueba de Oráculo", styles["Heading1"]))
    llm_data = [
        [Paragraph("Modelo", styles["TableHeader"]), Paragraph("Tamaño", styles["TableHeader"]), Paragraph("Corr. BOE", styles["TableHeader"]), Paragraph("Corr. Deb", styles["TableHeader"]), Paragraph("Fidelidad", styles["TableHeader"]), Paragraph("Falsas Abst.", styles["TableHeader"]), Paragraph("Formato Deb", styles["TableHeader"]), Paragraph("Velocidad", styles["TableHeader"]), Paragraph("VRAM Pico", styles["TableHeader"])],
        [Paragraph("<code>lfm3-1.7b</code>", styles["TableCellBold"]), Paragraph("1.7B", styles["TableCellCenter"]), Paragraph("0.93", styles["TableCellCenter"]), Paragraph("0.93", styles["TableCellCenter"]), Paragraph("93 %", styles["TableCellCenter"]), Paragraph("11-12 / 12", styles["TableCellCenter"]), Paragraph("40 %", styles["TableCellCenter"]), Paragraph("63.9 tok/s", styles["TableCellCenter"]), Paragraph("5.36 GB", styles["TableCellCenter"])],
        [Paragraph("<code>llama3.2-3b</code>", styles["TableCellBold"]), Paragraph("3B", styles["TableCellCenter"]), Paragraph("0.93", styles["TableCellCenter"]), Paragraph("1.07", styles["TableCellCenter"]), Paragraph("87-100%", styles["TableCellCenter"]), Paragraph("5-6 / 12", styles["TableCellCenter"]), Paragraph("73 %", styles["TableCellCenter"]), Paragraph("<b>66.4 tok/s</b>", styles["TableCellCenter"]), Paragraph("7.07 GB", styles["TableCellCenter"])],
        [Paragraph("<code>nemotron-bolt</code>", styles["TableCellBold"]), Paragraph("8B / 4B ef.", styles["TableCellCenter"]), Paragraph("1.60", styles["TableCellCenter"]), Paragraph("<b>1.53</b>", styles["TableCellCenter"]), Paragraph("<b>100 %</b>", styles["TableCellCenter"]), Paragraph("1-3 / 12", styles["TableCellCenter"]), Paragraph("<b>100 %</b>", styles["TableCellCenter"]), Paragraph("26.7 tok/s", styles["TableCellCenter"]), Paragraph("14.80 GB", styles["TableCellCenter"])],
        [Paragraph("<code>qwen3.5-9b</code>", styles["TableCellBold"]), Paragraph("9B", styles["TableCellCenter"]), Paragraph("<b>1.87</b>", styles["TableCellCenter"]), Paragraph("1.53", styles["TableCellCenter"]), Paragraph("<b>100 %</b>", styles["TableCellCenter"]), Paragraph("1-3 / 12", styles["TableCellCenter"]), Paragraph("67 %", styles["TableCellCenter"]), Paragraph("45.0 tok/s", styles["TableCellCenter"]), Paragraph("<b>14.27 GB</b>", styles["TableCellCenter"])],
    ]
    t_llm = Table(llm_data, colWidths=[3.2 * cm, 1.8 * cm, 2.2 * cm, 2.2 * cm, 2.0 * cm, 2.1 * cm, 2.0 * cm, 1.9 * cm, 1.9 * cm])
    t_llm.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1e3a8a")),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
        ("TOPPADDING", (0, 0), (-1, -1), 2),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 2),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f8fafc")]),
        ("BACKGROUND", (0, 3), (-1, 3), colors.HexColor("#eff6ff")),
        ("BACKGROUND", (0, 4), (-1, 4), colors.HexColor("#eff6ff")),
    ]))
    story.append(t_llm)
    story.append(Paragraph(
        "<b>Prueba del Oráculo (Extra):</b> Al inyectar el chunk exacto sin retrieval, la nota de LFM3 sube de 0.67 a 1.25. Demuestra empíricamente que los modelos pequeños sufren de <b>fallo por ruido</b>: se desconciertan ante 5 chunks en contexto.",
        styles["Body"]
    ))

    story.append(Paragraph("6. Fase 4: Decisiones por Escenario y Plan B (8 GB VRAM)", styles["Heading1"]))
    dec_text = (
        "<b>• BOE:</b> <code>harrier-oss-v1 (0.6B) + Qwen3.5-9B (FP8, vLLM)</code>. Máxima corrección (1.87/2), 100% fidelidad, "
        "solo 1 falsa abstención y el más barato de los viables (14.27 GB VRAM, 45 tok/s, 1.35s latencia). VRAM total combinada: ~15.5 GB.<br/>"
        "<b>• Debian:</b> <code>bge-m3 (568M) + Nemotron-3.5-Bolt-E4B (FP8, vLLM)</code>. bge-m3 es el único embedding viable en Debian (0.83). "
        "Nemotron es el único LLM que cumple el 100% de citación exacta de sección técnica (Qwen cayó al 67% al citar 'Fragmento 1'). VRAM total: ~15.9 GB.<br/>"
        "<b>• Plan B (8 GB VRAM):</b> <b>No desplegaríamos ninguno de los modelos evaluados.</b> Los modelos de 1.7B y 3B caben físicamente en 8 GB, "
        "pero sufren histeria de abstención (rechazan injustificadamente entre el 50% y el 92% de las preguntas). La solución de ingeniería "
        "es cuantizar Qwen3.5-9B a 4 bits (AWQ o GGUF Q4_K_M en llama.cpp), ocupando ~6.5 GB totales preservando calidad de razonamiento."
    )
    story.append(make_callout(dec_text, styles, bg_color="#f8fafc", border_color="#1e293b"))

    story.append(Paragraph("7. Lo que no esperábamos (Anomalías Técnicas)", styles["Heading1"]))
    p_sorpresas = (
        "<b>1. Paradoja de Nemotron:</b> Anunciado como '4B efectivos', fue el más lento (26.7 tok/s) y gastó 14.8 GB de VRAM. "
        "Causa: vLLM carga los 8B de parámetros y usa kernels Triton menos optimizados en GPU Ampere.<br/>"
        "<b>2. Divergencia de Embeddings:</b> Harrier arrasa en legal (100%) y colapsa en técnico (75%), donde bge-m3 gana.<br/>"
        "<b>3. Bipolaridad de LFM3-1.7B:</b> Se abstiene por reflejo ('No aparece en el documento') e inmediatamente redacta la respuesta correcta."
    )
    story.append(Paragraph(p_sorpresas, styles["Body"]))

    doc.build(story, canvasmaker=NumberedCanvas)
    print(f"[OK] Generado PDF 1: {ruta_salida} ({os.path.getsize(ruta_salida)} bytes)")


# ===========================================================================
# PDF 2: GUÍA DE DEFENSA PARA LAS 3 PRIMERAS DIAPOSITIVAS
# ===========================================================================
def generar_pdf_guion(ruta_salida):
    doc = SimpleDocTemplate(
        ruta_salida,
        pagesize=A4,
        leftMargin=36,
        rightMargin=36,
        topMargin=38,
        bottomMargin=34,
    )
    styles = get_styles()
    story = []

    # --- PÁGINA 1: Diapositiva 1 y Diapositiva 2 ---
    story.append(Paragraph("Guión de Defensa Oral: Diapositivas 1 a 3", styles["Title"]))
    story.append(Paragraph("Qué proyectar, qué decir paso a paso y respuestas preparadas ante el tribunal · Grupo 1", styles["Subtitle"]))
    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#2563eb"), spaceAfter=6))

    resumen_tiempo = (
        "<b>Tu Bloque de Defensa:</b> Apertura, Contexto y Retrieval (Diapositivas 1, 2 y 3).<br/>"
        "<b>Tiempo asignado estricto:</b> <b>00:00 a 03:30 (3 minutos y medio)</b> sobre los 10:00 totales del grupo.<br/>"
        "<b>Objetivo:</b> Demostrar control técnico desde el inicio, presentar los dos corpus, "
        "justificar por qué unificamos en vLLM y convencer al tribunal de que el retrieval de embeddings condiciona todo el sistema RAG."
    )
    story.append(make_callout(resumen_tiempo, styles, bg_color="#eff6ff", border_color="#3b82f6"))
    story.append(Spacer(1, 3))

    story.append(Paragraph("Diapositiva 1 · Portada y Apertura [00:00 - 00:30]", styles["Heading1"]))
    story.append(Paragraph("<b>Qué hay en pantalla:</b> Título de la práctica, subtítulo y miembros del Grupo 1.", styles["BodyBold"]))
    story.append(Paragraph("<b>Qué debes decir (Guión palabra por palabra):</b>", styles["Body"]))
    discurso_1 = (
        "«Buenos días. Somos el Grupo 1, compuesto por Nicolás Pascual, Aimar Mora e Íñigo Guzmán. "
        "Hoy venimos a presentar nuestro benchmark experimental de modelos de embedding y LLMs locales para sistemas RAG.<br/>"
        "Nuestra premisa de partida es clara: <b>no venimos a opinar sobre leaderboards abstractos como MTEB</b>, "
        "sino a defender decisiones de ingeniería basadas en datos empíricos que nosotros mismos hemos medido en hardware real, "
        "con código trazable y registros reproducibles de principio a fin.»"
    )
    story.append(make_callout(discurso_1, styles, bg_color="#f8fafc", border_color="#64748b"))
    story.append(Spacer(1, 4))

    story.append(Paragraph("Diapositiva 2 · Contexto, Escenarios y Stack Técnico [00:30 - 01:45]", styles["Heading1"]))
    story.append(Paragraph("<b>Qué hay en pantalla:</b> Dos columnas comparativas (BOE vs Debian) y ficha del hardware y stack vLLM.", styles["BodyBold"]))
    p_d2_points = (
        "1. <b>Dos corpus radicalmente opuestos:</b><br/>"
        "   • <i>Estatuto de los Trabajadores (BOE):</i> Dominio legal, redacción jurídica homogénea, artículos interconectados y necesidad estricta de citar el artículo exacto.<br/>"
        "   • <i>Manual del Administrador de Debian:</i> Documentación técnica, jerga mezclada de inglés y español, comandos de consola, flags y rutas de ficheros.<br/>"
        "2. <b>El Stack de Inferencia Unificado:</b><br/>"
        "   • Servidor local con GPU <b>NVIDIA A800 de 40 GB</b>, utilizando una partición MIG de 20 GB (<code>3g.20gb</code>).<br/>"
        "   • Unificamos todo el benchmark (tanto embeddings como LLMs) en <b>vLLM 0.34.0</b> en modo offline.<br/>"
        "   • Fijamos la <b>caché KV en 2.0 GB para todos los modelos</b>: esto es crucial, porque si dejas que el motor gestione la caché libremente, la VRAM medida refleja la reserva del servidor y no lo que consume el modelo.<br/>"
        "   • Cuantización unificada en <b>FP8</b> para todos los modelos generativos."
    )
    story.append(Paragraph(p_d2_points, styles["Body"]))
    
    discurso_2 = (
        "«Para que la comparación entre modelos sea justa, fijamos dos cosas: el stack y los datos. "
        "Corremos todo sobre vLLM en una instancia de 20 GB de VRAM. Al fijar la memoria de caché KV en exactamente 2 GB para todos, "
        "aseguramos que cada megabyte de diferencia en nuestros gráficos responda exclusivamente a la arquitectura y los pesos del modelo, "
        "no a una reserva arbitraria del motor de inferencia.»"
    )
    story.append(make_callout(discurso_2, styles, bg_color="#f8fafc", border_color="#64748b"))

    story.append(PageBreak())

    # --- PÁGINA 2: Diapositiva 3 y Preguntas Trampa ---
    story.append(Paragraph("Diapositiva 3 · Fase 1 (Golden Set) y Fase 2 (Benchmark de Embeddings) [01:45 - 03:30]", styles["Heading1"]))
    story.append(Paragraph("<b>Qué hay en pantalla:</b> Tabla A completa de embeddings (Recall@5, MRR, VRAM, tiempo) y gráfico de barras.", styles["BodyBold"]))
    p_d3_points = (
        "1. <b>Fase 1: Preparación del Corpus y Golden Set:</b><br/>"
        "   • Limpiamos el BOE con Docling eliminando cabeceras y pies repetidos que generarían ruido en los chunks.<br/>"
        "   • Creamos un <i>Golden Set</i> riguroso de 15 preguntas por escenario: 8 directas, 4 combinadas (requieren dos chunks) y 3 sin respuesta en el texto para evaluar la honestidad del modelo.<br/>"
        "2. <b>Fase 2: Benchmark de Embeddings (Tabla A):</b><br/>"
        "   • Regla de oro del RAG: <i>'El retrieval es el techo de cristal del sistema. Si el fragmento correcto no llega al top-5, el LLM no tiene forma de acertar'</i>.<br/>"
        "   • Evaluamos 3 modelos de ~600M parámetros: <code>bge-m3</code>, <code>Qwen3-Embedding</code> y <code>harrier-oss-v1</code>.<br/>"
        "   • <b>En el BOE:</b> <code>harrier-oss-v1</code> arrasa con un <b>Recall@5 perfecto de 1.0000</b> (12 de 12 preguntas) y MRR de 0.736.<br/>"
        "   • <b>En Debian:</b> Sin embargo, <i>harrier</i> cae al peor resultado (0.75). El ganador absoluto es <code>bge-m3</code>, siendo el <b>único modelo que supera el umbral del 80% (0.8333)</b>.<br/>"
        "3. <b>Conclusión crítica:</b> El ranking de MTEB falla al predecir comportamiento en producción; un modelo extraordinario en prosa legal en español puede ser deficiente en texto técnico con rutas y comandos."
    )
    story.append(Paragraph(p_d3_points, styles["Body"]))

    discurso_3 = (
        "«El resultado de los embeddings nos dio la primera gran lección del proyecto: <b>el mejor retriever varía según el dominio</b>. "
        "En el BOE, <i>harrier</i> fue impecable, metiendo el 100% de los fragmentos en el top-5. Pero al pasar al manual técnico de Debian, "
        "<i>harrier</i> cayó al 75% y el único que superó nuestro umbral de calidad fue <i>bge-m3</i> con un 83% de Recall.<br/>"
        "Por tanto, fijamos a los dos ganadores: Harrier para alimentar al BOE y BGE-M3 para Debian. "
        "Y ahora le paso la palabra a mi compañero para analizar cómo respondieron los LLMs a estos fragmentos en la Fase 3.»"
    )
    story.append(make_callout(discurso_3, styles, bg_color="#f8fafc", border_color="#1e40af"))
    story.append(Spacer(1, 5))

    story.append(Paragraph("Preguntas Trampa Típicas del Profesor sobre tus 3 Diapositivas", styles["Heading1"]))
    qa_data = [
        [
            Paragraph("<b>Pregunta Trampa</b>", styles["TableHeader"]),
            Paragraph("<b>Respuesta Técnica Exacta que debes dar</b>", styles["TableHeader"])
        ],
        [
            Paragraph("<i>«¿Por qué elegisteis vLLM en lugar de Ollama si Ollama es más sencillo de usar?»</i>", styles["TableCellBold"]),
            Paragraph("«Ollama gestiona la memoria de la GPU de manera opaca a través de su servidor y añade sobrecarga por petición. Con vLLM pudimos fijar de forma determinista <code>kv_cache_memory_bytes=2.0 GB</code> en modo offline. Así garantizamos que las diferencias de VRAM medidas se deban 100% al modelo y no al motor de inferencia, además de ejecutar FP8 directamente en hardware de centros de datos.»", styles["TableCell"])
        ],
        [
            Paragraph("<i>«¿Por qué usasteis FP8 si vuestra GPU es una A800 (arquitectura Ampere) que no tiene aceleración FP8 nativa?»</i>", styles["TableCellBold"]),
            Paragraph("«Totalmente cierto: Ampere no acelera el cómputo matricial en FP8 (eso empezó en Ada y Hopper). En nuestra A800, vLLM aplica FP8 como compresión de solo-pesos mediante kernels Marlin. No buscábamos reducir la latencia de cálculo, sino reducir el consumo de VRAM de los modelos de 9B a la mitad para que cupieran holgadamente en nuestra partición de 20 GB junto a la caché.»", styles["TableCell"])
        ],
        [
            Paragraph("<i>«¿Por qué Harrier saca un 100% en el BOE y cae al 75% en Debian?»</i>", styles["TableCellBold"]),
            Paragraph("«Porque el BOE es prosa jurídica homogénea en español formal, donde la arquitectura decoder moderna de Harrier destaca. En cambio, el manual de Debian mezcla rutas de Linux, comandos de terminal y términos en inglés dentro de frases en español. BGE-M3 es un encoder XLM-RoBERTa con un entrenamiento multilingüe masivo mucho más resistente a esa alternancia de idiomas y sintaxis técnica.»", styles["TableCell"])
        ],
        [
            Paragraph("<i>«¿Cómo garantizasteis que las preguntas del Golden Set no estuvieran sesgadas a favor del retrieval?»</i>", styles["TableCellBold"]),
            Paragraph("«Auditamos que ninguna pregunta compartiera 5 palabras consecutivas con el documento. Se redactaron como situaciones reales de usuario ('Si salgo a las 23:00, ¿a qué hora puedo entrar?') y no copiando artículos literales. Además, incluimos preguntas combinadas que exigen relacionar dos partes del documento y preguntas trampa sin respuesta para evaluar si el modelo alucina.»", styles["TableCell"])
        ],
    ]
    t_qa = Table(qa_data, colWidths=[6.5 * cm, 12.2 * cm])
    t_qa.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#0f172a")),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
        ("TOPPADDING", (0, 0), (-1, -1), 3),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f8fafc")]),
    ]))
    story.append(t_qa)

    doc.build(story, canvasmaker=NumberedCanvas)
    print(f"[OK] Generado PDF 2: {ruta_salida} ({os.path.getsize(ruta_salida)} bytes)")


if __name__ == "__main__":
    generar_pdf_proyecto("resumen_proyecto_fases_resultados.pdf")
    generar_pdf_guion("guion_defensa_diapositivas_1_a_3.pdf")
