![Texto Alternativo](ats-genius-resume-analizer.png)

# ATS Genius: Análisis Inteligente de Currículum Vitae con Gemini 📄🤖

Una aplicación web desarrollada con Gradio que analiza currículums vitae (CV) en formato PDF utilizando la API de Google Gemini, ofreciendo análisis de compatibilidad con descripciones de puestos específicos y evaluación general basada en sistemas ATS (Applicant Tracking System).

## 📋 Características

- **Interfaz Gráfica Intuitiva**: Diseñada con Gradio, ofrece una experiencia de usuario amigable con barra lateral para configuración.
- **Análisis Dual**:
- **Análisis con Descripción de Puesto**: Compara tu CV con una descripción de trabajo específica, evaluando la adecuación y ofreciendo recomendaciones    personalizadas.
- **Análisis General ATS**: Evalúa tu CV según criterios estándar de sistemas ATS, ofreciendo puntuación, análisis de estructura y recomendaciones de mejora.
- **Evaluacion Detallada**: Proporciona detalles y recomendaciones detalladas sobre tu CV, basada en más de 20 criterios: 
Contenido: Parseo ATS, logros cuantificables.
Formato: Peso, metadatos, tipo de archivo.
Estilo: Gramática, repetición, voz pasiva, diseño.
Secciones: Experiencia, educación, contacto, aficiones.
Habilidades: Duras y blandas.
- **Procesamiento de PDF**: Extrae automáticamente el texto de archivos PDF para su análisis.
- **Integración con Google Gemini**: Utiliza modelos avanzados de IA para proporcionar análisis detallados y recomendaciones profesionales.

## 🚀 Instalación

1. Clona este repositorio:
   ```bash
   git clone https://github.com/luisfillth/ats-genius-resume-analizer.git
   cd ats-genius-resume-analizer
   ```

2. Instala las dependencias requeridas:
   ```bash
   pip install -r requirements.txt
   ```

3. Obtén una clave API de Google Gemini:
   - Visita [Google AI Studio](https://aistudio.google.com/)
   - Regístrate o inicia sesión
   - Crea una nueva clave API

## 💻 Instrucciones de uso

1. Ejecuta la aplicación:
   ```bash
   python app.py
   ```

2. Accede a la interfaz web a través de la URL local proporcionada (generalmente http://127.0.0.1:7860/).

3. En la barra lateral izquierda:
   - Introduce tu clave API de Gemini
   - Selecciona el tipo de análisis deseado

4. En el área principal:
   - Sube tu currículum en formato PDF
   - Si seleccionaste "Analizar con descripción de puesto", introduce la descripción del puesto
   - Haz clic en "Procesar Currículum"

5. Revisa los resultados detallados del análisis

## 📊 Tipos de Análisis

### Análisis con Descripción de Puesto
Proporciona:
- Puntuación de adecuación en escala 1-10
- Puntos fuertes y cualificaciones principales
- Áreas de mejora identificadas
- Recomendaciones específicas
- Veredicto final de adecuación
- Para puntuaciones ≥ 7: Guía de preparación para entrevistas

### Análisis General ATS
Proporciona:
- Puntuación global del currículum (%)
- Análisis de formato y estructura
- Palabras clave identificadas
- Fortalezas y debilidades generales
- Recomendaciones de mejora
- Versión optimizada del currículum

## ⚙️ Requisitos Técnicos

- Python >= 3.9
- Conexión a Internet (para API de Gemini)
- Clave API Key de Google Gemini

## 👨‍💻 Desarrollo

Este proyecto utiliza las siguientes tecnologías:
- **Gradio**: Para la interfaz de usuario web
- **PyMuPDF**: Para la extracción de texto de archivos PDF
- **Google Generative AI**: Para el análisis mediante IA

## 🔮 Mejoras futuras

- Resaltar errores del CV en pantalla.
- Gráficos interactivos de puntuación.
- Historial de análisis previos.
- Exportar resultados a PDF.
- Enviar sugerencias por correo.
- Base de datos para almacenar currículums y reportes.

## 📄 Licencia

[MIT License](LICENSE)

## 🙏 Créditos

Desarrollado por [H Luisfillth](https://www.linkedin.com/in/luisfillth0504/)  
GitHub: [luisfillth](https://github.com/luisfillth)

"Un buen currículum abre puertas, pero uno optimizado las deja abiertas."
