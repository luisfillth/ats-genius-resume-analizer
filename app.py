import os
import pymupdf as fitz
import gradio as gr
import google.generativeai as genai

# Función para extraer texto de un PDF cargado usando PyMuPDF
def extract_text_from_pdf(pdf_file):
    try:
        # Abrir el documento PDF con PyMuPDF
        doc = fitz.open(pdf_file.name)
        text = ""
        
        # Extraer texto de cada página
        for page in doc:
            text += page.get_text()
            
        # Cerrar el documento
        doc.close()
        
        if not text.strip():
            raise ValueError("El texto extraído del currículum está vacío. Por favor, cargue un PDF diferente.")
        return text
    except Exception as e:
        return f"Error al leer PDF: {e}"

# Función para calcular métricas adicionales del PDF
def calculate_metrics(pdf_file, text):
    # Calcular el número de palabras
    word_count = len(text.split())
    
    # Calcular el tamaño del archivo en MB
    file_size_mb = os.path.getsize(pdf_file.name) / (1024 * 1024)
    
    # Podemos añadir métricas adicionales específicas de PyMuPDF
    try:
        doc = fitz.open(pdf_file.name)
        page_count = len(doc)
        
        # Extraer metadatos si están disponibles
        metadata = doc.metadata
        
        # Cerrar el documento
        doc.close()
        
        return word_count, file_size_mb, page_count, metadata
    except:
        # Si hay algún error, devolvemos solo las métricas básicas
        return word_count, file_size_mb, None, None

# Configuración de Gemini API
def configure_gemini(api_key):
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel("gemini-1.5-flash")
        return model
    except Exception as e:
        return f"Error al configurar Gemini API: {e}"

# Función de adecuación del currículum a la descripción del puesto con análisis avanzado
def analyze_resume(job_description, resume_text, word_count, file_size_mb, api_key, metadata=None, page_count=None, progress=gr.Progress()):
    if not resume_text or resume_text.startswith("Error"):
        return "Por favor, cargue un currículum válido primero."
    
    if not job_description:
        return "Por favor, proporcione una descripción del puesto."
    
    if not api_key:
        return "Por favor, proporcione una clave API de Gemini válida."
    
    # Información adicional que podemos incluir gracias a PyMuPDF
    additional_info = ""
    if page_count is not None:
        additional_info += f"\n        - Número de páginas: {page_count}"
    
    if metadata is not None and isinstance(metadata, dict):
        if metadata.get("title"):
            additional_info += f"\n        - Título del documento: {metadata.get('title')}"
        if metadata.get("author"):
            additional_info += f"\n        - Autor: {metadata.get('author')}"
    
    prompt_job_desc = f"""Como Gestor Técnico de Recursos Humanos con experiencia, proporcione una evaluación profesional detallada del currículum vitae del candidato : {resume_text} con respecto a la descripción del puesto: {job_description}. 
    Nota: Por favor, no invente la respuesta, sólo responda a partir de la descripción del puesto proporcionada.
    Información adicional del CV:
        - Número de palabras: {word_count}
        - Tamaño del archivo: {file_size_mb:.2f} MB{additional_info}

    Por favor, analiza:

    1. **Análisis de Contenido (CONTENT)**  
        - **ATSParseRateReport (Tasa de Parseo ATS)**  
            *Objetivo*: Evaluar qué tan bien el CV puede ser leído y procesado por sistemas de seguimiento de candidatos (ATS).  
            *Métricas*: Número de palabras (mínimo 400, máximo 800 recomendadas por ATS). Tasa de parseo en porcentaje, considerando "excelente" por encima del 85%.  
            *Resultado*: Devuelve un puntaje de 0 a 100.  
            *Peso en la puntuación total*: 15%.  
        - **QuantifyingImpactReport (Cuantificación del Impacto)**  
            *Objetivo*: Verificar si el CV incluye logros cuantificables para demostrar impacto.  
            *Análisis*: Identificar si hay "bullets" (puntos) que carezcan de cuantificación (por ejemplo, "reduje costos en un 30%").  
            *Resultado*: Devuelve un puntaje de 0 a 100.  
            *Peso*: 20%.

    2. **Análisis de Formato (FORMAT)**  
        - **FormatAndSizeReport (Formato y Tamaño del Archivo)**  
            *Objetivo*: Asegurar que el CV esté en un formato adecuado y tenga un tamaño de archivo manejable.  
            *Métricas*: Formato PDF (válido). Tamaño del archivo menor a 2 MB. Verificar que no contenga metadatos innecesarios (opción "isMetaDataDisabled" activada).  
            *Resultado*: Devuelve un puntaje de 0 a 100.  
            *Peso*: 2%.

    3. **Análisis de Estilo (STYLE)**  
        - **RepetitionReport (Reporte de Repetición)**  
            *Objetivo*: Identificar si hay verbos o palabras repetidas en exceso, lo que puede hacer que el CV sea monótono.  
            *Análisis*: Verificar si el CV contiene un uso excesivo de verbos o palabras repetidas.  
            *Resultado*: Devuelve un puntaje de 0 a 100.  
            *Peso*: 5%.  
        - **SpellingGrammarReport (Reporte de Ortografía y Gramática)**  
            *Objetivo*: Detectar errores ortográficos, gramaticales o de puntuación.  
            *Análisis*: Identificar y comunicar errores ortográficos, gramaticales o de puntuación (por ejemplo, frases que no comienzan con mayúscula, errores tipográficos).  
            *Resultado*: Devuelve un puntaje de 0 a 100.  
            *Peso*: 10%.  
        - **LengthReporter (Reporte de Longitud)**  
            *Objetivo*: Evaluar si la longitud del CV es adecuada (ni muy corto ni muy largo).  
            *Métricas*: Longitud del CV entre 400 y 800 palabras.  
            *Resultado*: Devuelve un puntaje de 0 a 100.  
            *Peso*: 1%.  
        - **BulletLengthReport (Reporte de Longitud de Bullets)**  
            *Objetivo*: Asegurar que los puntos o "bullets" no sean demasiado largos o cortos, para mantener claridad y concisión.  
            *Análisis*: Verificar si hay bullets problemáticos (muy largos o muy cortos).  
            *Resultado*: Devuelve un puntaje de 0 a 100.  
            *Peso*: 0.5%.  
        - **DesignReport (Reporte de Diseño)**  
            *Objetivo*: Evaluar el diseño visual del CV (colores, fuentes, disposición).  
            *Análisis*:  
                - **Disposición**: La información más importante debe presentarse en el primer tercio del CV (por ejemplo, la sección Resumen). Generalmente, debe seguirse con Experiencia Laboral y Educación. En un diseño de dos columnas, se pueden colocar secciones de Habilidades y Logros a la derecha.  
                - **Secciones Adicionales**: Dependiendo de la experiencia, se pueden agregar Idiomas, Aficiones, Proyectos, etc.  
                - **Colores**: Los colores deben reflejar personalidad, pero ser legibles (evitar combinaciones como texto verde claro sobre fondo rojo). No usar más de 2-3 colores.  
                - **Fuentes**: Evitar fuentes como Times New Roman. Usar fuentes modernas como Lato o Raleway. Usar dos fuentes complementarias (una para encabezados, otra para texto).  
                - **Número de páginas**: Preferiblemente una página, pero se aceptan dos si es necesario.  
                - **Tono**: Formal y educado, adaptado a la industria (puede ser más relajado si el puesto lo requiere, por ejemplo, en industrias creativas).  
            *Resultado*: Devuelve un puntaje de 0 a 100.  
            *Peso*: 0.5%.  
        - **EmailReport (Reporte de Correo Electrónico)**  
            *Objetivo*: Verificar que el email proporcionado sea profesional y esté presente.  
            *Análisis*: Verificar que el email esté presente y sea profesional (por ejemplo, evitar direcciones como "partylover123@gmail.com").  
            *Resultado*: Devuelve un puntaje de 0 a 100.  
            *Peso*: 2%.  
        - **PassiveVoiceReport (Reporte de Voz Pasiva)**  
            *Objetivo*: Identificar el uso excesivo de voz pasiva, que puede debilitar el impacto del CV.  
            *Análisis*: Verificar si hay bullets con uso excesivo de voz pasiva (por ejemplo, "el proyecto fue completado" en lugar de "completé el proyecto").  
            *Resultado*: Devuelve un puntaje de 0 a 100.  
            *Peso*: 2%.  
        - **BuzzwordsReport (Reporte de Palabras de Moda)**  
            *Objetivo*: Detectar el uso excesivo de "buzzwords" (palabras como "sinergia" o "proactivo") que pueden sonar vacías.  
            *Análisis*: Verificar si el CV presenta buzzwords problemáticos.  
            *Resultado*: Devuelve un puntaje de 0 a 100.  
            *Peso*: 2%.

    4. **Análisis de Secciones (SECTIONS)**  
        - **ContactReporter (Reporte de Contacto)**  
            *Objetivo*: Asegurar que el CV incluya información de contacto esencial.  
            *Análisis*: Verificar la presencia de datos de contacto: Nombre, Email, Teléfono, LinkedIn (si aplica).  
            *Resultado*: Devuelve un puntaje de 0 a 100.  
            *Peso*: 4%.  
        - **EssentialsReporter (Reporte de Secciones Esenciales)**  
            *Objetivo*: Verificar la presencia de secciones esenciales como Experiencia Laboral, Educación y Habilidades.  
            *Análisis*: Comprobar la presencia de las secciones Resumen, Habilidades, Educación y Experiencia Laboral. Si no hay Experiencia Laboral, se recomienda agregar una sección de Proyectos.  
            *Resultado*: Devuelve un puntaje de 0 a 100.  
            *Peso*: 4%.  
        - **PersonalityReport (Reporte de Personalidad)**  
            *Objetivo*: Evaluar si el CV incluye secciones que muestren la personalidad del candidato.  
            *Análisis*: Verificar la presencia de secciones como "Pasiones", "Libros", "Mi Tiempo" o "Aficiones". Si no están presentes, recomendar agregar al menos una para mostrar personalidad.  
            *Resultado*: Devuelve un puntaje de 0 a 100.  
            *Peso*: 1%.  
        - **AdditionalSectionsReport (Reporte de Secciones Adicionales)**  
            *Objetivo*: Evaluar la presencia de secciones opcionales que añadan valor al CV.  
            *Análisis*: Verificar la presencia de secciones como Idiomas, Proyectos Personales, Certificaciones o Enlaces Sociales. Si no están presentes, recomendar agregarlas si son relevantes para el puesto.  
            *Resultado*: Devuelve un puntaje de 0 a 100.  
            *Peso*: 2%.

    5. **Análisis de Habilidades (SKILLS)**  
        - **HardSkillsReport (Reporte de Habilidades Duras)**  
            *Objetivo*: Identificar habilidades técnicas específicas (como herramientas, lenguajes de programación, etc.).  
            *Análisis*: Verificar la presencia de habilidades técnicas. Si no hay, recomendar agregar habilidades relevantes (por ejemplo, "Python", "Gestión de Proyectos").  
            *Resultado*: Devuelve un puntaje de 0 a 100.  
            *Peso*: 20%.  
        - **SoftSkillsReport (Reporte de Habilidades Blandas)**  
            *Objetivo*: Identificar habilidades interpersonales (como trabajo en equipo, comunicación, etc.).  
            *Análisis*: Verificar la presencia de habilidades interpersonales. Si no hay, recomendar agregar habilidades relevantes (por ejemplo, "Trabajo en equipo", "Resolución de problemas").  
            *Resultado*: Devuelve un puntaje de 0 a 100.  
            *Peso*: 10%.

    6. **Puntuación General (OVERALL)**  
        - **OverallScoreReport (Reporte de Puntuación General)**  
            *Objetivo*: Calcular la puntuación general del CV considerando todas las categorías anteriores.  
            *Análisis*:  
                - Calcular la puntuación general como un promedio ponderado de los puntajes de todas las categorías.  
                - Incluir comentarios sobre:  
            *Factores Negativos*: Mencionar los factores que bajaron el puntaje (por ejemplo, errores gramaticales, ausencia de experiencia laboral).  
            *Factores Positivos*: Mencionar los factores que subieron el puntaje (por ejemplo, compatibilidad con ATS, logros cuantificables).  
            *Resultado*: Devuelve un puntaje final de 0 a 100.

    7. **Evaluación Final**  
        - **Adecuación General al Puesto**: Evaluar la adecuación del candidato al puesto en una escala de 1 a 10, considerando la alineación entre el CV y la descripción del puesto.  
        - **Principales Puntos Fuertes y Cualificaciones**: Identificar las fortalezas clave del candidato (por ejemplo, experiencia relevante, proyectos destacados).  
        - **Lagunas Notables o Áreas de Mejora**: Señalar áreas donde el CV no cumple con los requisitos del puesto o estándares generales (por ejemplo, falta de experiencia laboral, habilidades específicas ausentes).  
        - **Recomendaciones Específicas para Mejorar el Currículum**: Proporcionar consejos prácticos para mejorar el CV (por ejemplo, corregir errores gramaticales, agregar una sección de experiencia laboral).  
        - **Veredicto Final sobre la Adecuación al Puesto**: Concluir si el candidato es adecuado para el puesto basado en el análisis.

    8. **Preparación para la Entrevista (Condicional)**  
        - Si el veredicto final es positivo (puntuación de adecuación >= 7):  
            Proporcionar una breve hoja de ruta para que el candidato se prepare para la entrevista, incluyendo:  
                - Ejemplos de preguntas que podría enfrentar (por ejemplo, "¿Puedes hablarnos de un proyecto en el que hayas trabajado?").  
                - Puntos clave a destacar (por ejemplo, experiencia relevante, habilidades técnicas).  
        - Si el veredicto final es negativo (puntuación < 7):  
            Especificar que el candidato debe realizar los cambios sugeridos y volver a presentar su CV.

    **Formato de la Respuesta**  
    - Utilice títulos claros para cada sección (por ejemplo, "Análisis de Contenido", "Evaluación Final").  
    - Mantenga un lenguaje profesional y objetivo, adecuado para un contexto de recursos humanos.
    """
    
    progress(0.3, desc="Iniciando análisis avanzado...")
    progress(0.5, desc="Procesando con Gemini API...")
    
    gemini_model = configure_gemini(api_key)
    if isinstance(gemini_model, str):  # Es un mensaje de error
        return gemini_model
        
    response = gemini_model.generate_content(prompt_job_desc)
    progress(1.0, desc="Análisis completado")
    
    return response.text

# Función para calcular la puntuación del currículum y las sugerencias mediante Google Gemini
def get_suggestions_from_gemini(resume_text, word_count, file_size_mb, api_key, metadata=None, page_count=None, progress=gr.Progress()):
    if not resume_text or resume_text.startswith("Error"):
        return "Por favor, cargue un currículum válido primero."
    
    if not api_key:
        return "Por favor, proporcione una clave API de Gemini válida."
    
    # Información adicional que podemos incluir gracias a PyMuPDF
    additional_info = ""
    if page_count is not None:
        additional_info += f"\n        - Número de páginas: {page_count}"
    
    if metadata is not None and isinstance(metadata, dict):
        if metadata.get("title"):
            additional_info += f"\n        - Título del documento: {metadata.get('title')}"
        if metadata.get("author"):
            additional_info += f"\n        - Autor: {metadata.get('author')}"
    
    prompt = f"""Como experto en ATS (Applicant Tracking System), analiza el siguiente currículum vitae: {resume_text}

    Información adicional del CV:
        - Número de palabras: {word_count}
        - Tamaño del archivo: {file_size_mb:.2f} MB{additional_info}
            
    Proporcione:
        1. **Análisis de Contenido (CONTENT)**  
            - **ATSParseRateReport (Tasa de Parseo ATS)**  
                *Objetivo*: Evaluar qué tan bien el CV puede ser leído y procesado por sistemas de seguimiento de candidatos (ATS).  
                *Métricas*: Número de palabras (mínimo 400, máximo 800 recomendadas por ATS). Tasa de parseo en porcentaje, considerando "excelente" por encima del 85%.  
                *Resultado*: Devuelve un puntaje de 0 a 100.  
            - **QuantifyingImpactReport (Cuantificación del Impacto)**  
                *Objetivo*: Verificar si el CV incluye logros cuantificables para demostrar impacto.  
                *Análisis*: Identificar si hay "bullets" (puntos) que carezcan de cuantificación (por ejemplo, "reduje costos en un 30%").  
                *Resultado*: Devuelve un puntaje de 0 a 100.  

        2. **Análisis de Formato y Estilo**  
            - Formato, diseño, ortografía, gramática, longitud de bullets, uso de voz pasiva, buzzwords, etc.
            - Evaluar el estilo de redacción profesional y la claridad del contenido

        3. **Análisis de Secciones y Habilidades**
            - Verificar secciones esenciales: Información de contacto, experiencia, educación, habilidades
            - Identificar y evaluar habilidades duras (técnicas) y blandas (interpersonales)

        4. **Puntuación General y Recomendaciones**
            - Puntuación global del currículum (%)
            - Análisis del formato y la estructura del currículum vitae
            - Palabras clave específicas encontradas
            - Puntos fuertes y débiles generales
            - Recomendaciones específicas de mejora
        
        Empiece con el porcentaje de coincidencia bien visible.
        Al final, cree un currículum más limpio y estructurado que tenga más probabilidades de ser seleccionado por la ATS.
    """
    
    progress(0.3, desc="Iniciando análisis ATS avanzado...")
    progress(0.5, desc="Procesando con Gemini API...")
    
    gemini_model = configure_gemini(api_key)
    if isinstance(gemini_model, str):  # Es un mensaje de error
        return gemini_model
        
    response = gemini_model.generate_content(prompt)
    progress(1.0, desc="Análisis completado")
    
    return response.text

# Función principal para procesar el PDF
def process_pdf(file):
    if file is None:
        return "Por favor, cargue un archivo PDF.", None, None, None, None, None
    
    resume_text = extract_text_from_pdf(file)
    
    if resume_text.startswith("Error"):
        return resume_text, None, None, None, None, None
    
    # Calcular métricas adicionales con PyMuPDF
    word_count, file_size_mb, page_count, metadata = calculate_metrics(file, resume_text)
    
    return "Currículum cargado y procesado correctamente. Continúe con la acción seleccionada.", resume_text, word_count, file_size_mb, page_count, metadata

# Función para procesar según la opción seleccionada
def process_based_on_option(option, file, job_description, api_key, progress=gr.Progress()):
    status, resume_text, word_count, file_size_mb, page_count, metadata = process_pdf(file)
    
    if resume_text is None:
        return status
    
    if not api_key:
        return "Por favor, proporcione una clave API de Gemini válida."
    
    if option == "Analizar con descripción de puesto":
        if not job_description:
            return "Por favor, proporcione una descripción del puesto."
        return analyze_resume(job_description, resume_text, word_count, file_size_mb, api_key, metadata, page_count, progress)
    
    elif option == "Análisis general ATS":
        return get_suggestions_from_gemini(resume_text, word_count, file_size_mb, api_key, metadata, page_count, progress)
    
    return "Por favor, seleccione una opción válida."

# Configuración de la interfaz Gradio con barra lateral
with gr.Blocks(theme=gr.themes.Soft(), title="ATS Genius: Análisis Inteligente de Currículum Vitae con Gemini") as demo:
    gr.Markdown(
        """
        # 📄 ATS Genius: Análisis Inteligente de Currículum Vitae con Gemini 🤖
        
        **Bienvenido a ATS Genius: Análisis Inteligente de Currículum Vitae con Gemini!**  
        Cargue su currículum, analice su compatibilidad con descripciones de puestos específicos u obtenga un análisis detallado ATS.
        """
    )
    
    with gr.Row():
        # Barra lateral izquierda
        with gr.Column(scale=1, min_width=300):
            with gr.Group():
                gr.Markdown("### ⚙️ Configuración")
                api_key = gr.Textbox(
                    label="Clave API de Gemini", 
                    placeholder="Introduce tu clave API de Gemini aquí...",
                    type="password"
                )
                
                gr.Markdown("### 🔍 Opciones de Análisis")
                option_radio = gr.Radio(
                    ["Analizar con descripción de puesto", "Análisis general ATS"],
                    label="Seleccione el tipo de análisis",
                    value="Analizar con descripción de puesto"
                )
                
                with gr.Accordion("ℹ️ Información sobre el Análisis", open=False):
                    gr.Markdown("""
                    **Análisis avanzado que incluye:**
                    
                    - **Análisis de Contenido**: 
                        - Tasa de parseo ATS
                        - Cuantificación del impacto
                    
                    - **Análisis de Formato**: 
                        - Formato y tamaño del archivo
                    
                    - **Análisis de Estilo**: 
                        - Repetición de palabras
                        - Ortografía y gramática
                        - Longitud del CV
                        - Longitud de bullets
                        - Diseño
                        - Email profesional
                        - Uso de voz pasiva
                        - Buzzwords
                    
                    - **Análisis de Secciones**: 
                        - Información de contacto
                        - Secciones esenciales
                        - Personalidad
                        - Secciones adicionales
                    
                    - **Análisis de Habilidades**: 
                        - Habilidades duras
                        - Habilidades blandas
                    
                    - **Puntuación y evaluación final**
                    """)
                
                gr.Markdown("---")
                gr.Markdown(
                    """
                    Construido por 🎉 [H Luisfillth](https://www.linkedin.com/in/luisfillth0504/) | [Github](https://github.com/luisfillth) 🚀
                    """
                )
        
        # Área principal de contenido
        with gr.Column(scale=3):
            with gr.Group():
                file_input = gr.File(
                    label="Cargue su currículum (sólo PDF)",
                    file_types=[".pdf"]
                )
                
                # Área condicional para la descripción del puesto
                job_description_container = gr.Group(visible=True)
                with job_description_container:
                    job_description = gr.Textbox(
                        label="Descripción del Puesto",
                        placeholder="Pegue aquí la descripción del puesto...",
                        lines=5
                    )
                
                with gr.Row():
                    process_btn = gr.Button("Procesar Currículum", variant="primary")
                    clear_btn = gr.Button("Limpiar", variant="secondary")
                
                output = gr.Markdown(label="Resultados del Análisis")
    
    # Lógica para mostrar/ocultar campos según la opción seleccionada
    def update_visibility(option):
        return gr.Group.update(visible=(option == "Analizar con descripción de puesto"))
    
    option_radio.change(
        fn=update_visibility,
        inputs=option_radio,
        outputs=job_description_container
    )
    
    # Función para limpiar campos
    def clear_fields():
        return None, "", ""
    
    clear_btn.click(
        fn=clear_fields,
        inputs=[],
        outputs=[file_input, job_description, output]
    )
    
    # Lógica para procesar según la opción seleccionada
    process_btn.click(
        fn=process_based_on_option,
        inputs=[option_radio, file_input, job_description, api_key],
        outputs=output
    )

# Iniciar la aplicación Gradio
if __name__ == "__main__":
    demo.launch()