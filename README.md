# 🎓 Asistente Universitario Inteligente - UNDC (RAG)

¡Bienvenido al repositorio oficial del **Asistente Universitario de la UNDC**! Este proyecto ha sido desarrollado como el Desafío Final (**Alura Agente**) para la plataforma Alura Latam. 

Se trata de un sistema de **Generación Aumentada por Recuperación (RAG)** diseñado para los estudiantes de la **Universidad Nacional de Cañete (UNDC)**. El asistente interactúa en lenguaje natural para resolver dudas complejas sobre reglamentos de asistencia, disciplina, grados y títulos, y procesos de investigación, evitando la lectura tediosa de densos documentos en PDF.

---

## 🔗 Enlace de la Aplicación en Vivo (OCI)
La aplicación se encuentra desplegada y funcionando las 24 horas del día en la infraestructura de Oracle Cloud:
👉 **[http://159.112.137.35:8501](http://159.112.137.35:8501)**

---

## 🏛️ Arquitectura de la Solución

El sistema implementa una **arquitectura desacoplada y serverless** de alta disponibilidad para garantizar que el servidor de cómputo permanezca sin estado (*stateless*):


<img width="1536" height="1024" alt="image" src="https://github.com/user-attachments/assets/647a0abd-86bf-45a0-8aeb-48e5908be176" />


## 🏗️ Arquitectura de la Solución y Pipeline RAG

La arquitectura del sistema está diseñada de forma desacoplada para mantener el servidor de cómputo en un estado ligero (*stateless*):

### 1. Ingesta y Curaduría
Los reglamentos originales en PDF de la universidad (asistencia, investigación, grados y títulos) se pre-procesan y limpian de ruidos visuales (como imágenes de firmas o sellos antiguos) utilizando Microsoft Word como motor de OCR. Esto garantiza que el cargador de texto lea contenido digital nativo limpio, mejorando drásticamente el rendimiento de búsqueda.

### 2. Procesamiento y Chunking
Se utiliza la librería `PyMuPDFLoader` para una extracción extremadamente veloz de las páginas del PDF. El contenido se segmenta con la clase `RecursiveCharacterTextSplitter` utilizando un tamaño de fragmento (`chunk_size`) de **1000 caracteres** y una superposición (`chunk_overlap`) de **150 caracteres**, garantizando que ninguna idea o regla se corte a la mitad, conservando además los metadatos de origen (nombre de archivo y número de página).

### 3. Indexación Vectorial (Pinecone Cloud)
Los fragmentos de texto se convierten en vectores matemáticos de **3072 dimensiones** utilizando el modelo oficial vigente de Google: **`models/gemini-embedding-001`**. Estos vectores se guardan de forma permanente en un índice serverless en la nube de **Pinecone** configurado con la métrica de distancia *Coseno*. 

*   **Mitigación de Rate Limit:** Para la indexación inicial de los 403 fragmentos generados, se implementó en `core_rag.py` una lógica de **Batching** (lotes de 45 en 45 con pausas de 30 segundos) en Python. Esto respeta la cuota gratuita de 100 RPM de la API de Google, evitando el error `429 RESOURCE_EXHAUSTED` y asegurando una subida exitosa y gratuita.

### 4. Recuperación (Retriever)
Ante una duda del estudiante, la pregunta se convierte en vector usando el mismo modelo de embeddings de Gemini. El *Retriever* consulta Pinecone de manera remota para extraer los **4 fragmentos de texto con mayor relevancia semántica** y construye la variable dinámica de `{contexto}`.

### 5. Generación con IA Emocional (Gemini 2.5 Flash)
La orquestación de la cadena se realiza mediante la sintaxis declarativa de LangChain (LCEL). El prompt de sistema cuenta con tres capas cognitivas estrictas:
*   **Escudo de Seguridad:** Protege al sistema contra *Prompt Injections* y evita que responda preguntas ajenas a la universidad.
*   **Control de Alucinaciones:** Obliga al modelo a basarse únicamente en el contexto; de lo contrario, responde textualmente que la duda no se encuentra contemplada en el reglamento.
*   **Capa de Empatía (Enrutamiento Humano):** Si el estudiante expresa quejas, maltrato por parte de un docente o injusticias en sus notas en lenguaje coloquial, la IA responde con profunda calidez, valida su dolor y lo enruta de forma precisa hacia la **Defensoría Universitaria de la UNDC** o a los procesos formales de **Reclamo de Evaluación** (Art. 95).

### 6. Interfaz de Usuario (Streamlit)
La interfaz web es intuitiva, limpia y responsiva. Implementa un chat conversacional continuo mediante el estado de la sesión (`st.session_state`) y, bajo cada respuesta generada, expone un menú desplegable interactivo (**"Ver fuentes consultadas"**) para que el estudiante verifique de qué reglamento y de qué página exacta proviene la información para respaldar sus reclamos.

---

### 💻 Tecnologías y Servicios Cloud Utilizados

*   **OCI Compute (VM.Standard.E2.1.Micro):** Servidor físico gratuito en la nube de Oracle (Santiago de Chile) donde se ejecuta el contenedor Docker.
*   **OCI Virtual Cloud Network (VCN):** Configuración de subredes públicas y reglas de entrada para habilitar el puerto `8501`.
*   **Pinecone DB (SaaS):** Base de datos vectorial persistente en la nube (capa gratuita AWS `us-east-1`).
*   **Google AI Studio API:** Modelos `gemini-2.5-flash` para generación y `gemini-embedding-001` para representación vectorial.
*   **Docker & Docker Compose:** Contenerización y estandarización del entorno.
*   **Python 3.11 & Streamlit:** Lenguaje de backend y biblioteca de interfaz de usuario.
*   **LangChain (Core / Community):** Framework de orquestación de IA y pipelines de RAG.

---

### 🚀 Cómo Ejecutar el Proyecto Localmente

#### Requisitos Previos
*   Tener instalado **Docker** y **Docker Compose** en tu sistema.
*   Contar con las API Keys de **Google AI Studio** y de **Pinecone** (índice configurado a 3072 dimensiones).

#### Pasos para levantar el contenedor

1.  **Clonar el repositorio:**
    ```bash
    git clone https://github.com/AlvaroFV15/undc-asistente.git
    cd undc-asistente
    ```

2.  **Crear el archivo `.env` en la raíz del proyecto:**
    ```env
    GOOGLE_API_KEY=tu_clave_gemini
    PINECONE_API_KEY=tu_clave_de_pinecone
    PINECONE_INDEX_NAME=undc-index
    ```

3.  **Coloca tus reglamentos universitarios en formato PDF dentro de la carpeta `documentos/`.**

4.  **Construir y levantar el contenedor Docker:**
    ```bash
    docker-compose up -d
    ```

5.  **Acceder a la aplicación:**
    Abre en tu navegador web la dirección: **`http://localhost:8501`**

6.  **Indexar por primera vez:**
    Ve a la barra lateral izquierda y haz clic en el botón **"Sincronizar y Re-indexar PDFs"** para subir los vectores de tus PDFs a Pinecone de manera automática. ¡Ya puedes chatear con los documentos!

---

### 📸 Demostración del Funcionamiento (Logs y Respuestas)

<img width="1904" height="823" alt="image" src="https://github.com/user-attachments/assets/24ff2020-d48b-4da3-a6b0-77216a6491fa" />



<img width="1254" height="129" alt="image" src="https://github.com/user-attachments/assets/b1cef18d-88a6-4460-ba08-0f28af72fa5a" />
