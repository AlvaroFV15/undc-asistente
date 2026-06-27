import streamlit as st
import os
import glob
from core_rag import responder_pregunta_undc, procesar_e_indexar

# Configuración visual de la interfaz de Streamlit
st.set_page_config(
    page_title="UNDC - Asistente Universitario",
    page_icon="🎓",
    layout="wide"
)

# Inicializar el historial de chat en el estado de la sesión si no existe
if "messages" not in st.session_state:
    st.session_state.messages = []

# Título principal de la aplicación
st.title("🎓 UNDC - Asistente Universitario Inteligente")
st.caption("Consulta de forma rápida las políticas de asistencia, exámenes, disciplina y más.")
st.markdown("---")

# Barra lateral izquierda (Sidebar)
with st.sidebar:
    # Intenta cargar el logotipo oficial de la UNDC
    st.image("https://1cirlg.undc.edu.pe/assets/img/logo.png", width=140)
    
    st.markdown("### 📚 Reglamentos Disponibles")
    st.write("Archivos PDF actualmente colocados en la carpeta `documentos/`:")

    # Escanear el directorio para ver qué archivos tiene el alumno
    archivos_pdf = glob.glob("documentos/*.pdf")
    if archivos_pdf:
        for pdf in archivos_pdf:
            st.markdown(f"- 📄 `{os.path.basename(pdf)}`")
    else:
        st.warning("⚠️ No se han encontrado archivos PDF en la carpeta `documentos/`.")

    st.markdown("---")
    st.markdown("### ⚙️ Panel de Administración")
    st.write("Si has subido un nuevo reglamento, presiona este botón para regenerar la base de datos vectorial.")
    
    # Botón dinámico para re-indexar sin reiniciar el contenedor Docker
    if st.button("🔄 Sincronizar y Re-indexar PDFs", key="reindex"):
        if archivos_pdf:
            with st.spinner("Procesando documentos y actualizando embeddings..."):
                procesar_e_indexar()
                st.success("¡Base de datos vectorial FAISS actualizada con éxito!")
                st.rerun()
        else:
            st.error("No hay archivos PDF en la carpeta `documentos/` para indexar.")

    st.markdown("---")
    st.caption("Proyecto Desarrollado para la Universidad Nacional de Cañete (UNDC).")

# Renderizar el historial de conversación en pantalla
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])
        # Si el mensaje contiene fuentes (RAG), las mostramos en un expander
        if "fuentes" in message and message["fuentes"]:
            with st.expander("📚 Ver fuentes consultadas"):
                for fuente in message["fuentes"]:
                    st.write(f"- {fuente}")

# Entrada de texto del Chat (Caja de texto inferior)
if prompt := st.chat_input("Escribe tu duda (ej: ¿con cuántas faltas repruebo un curso?)"):
    # 1. Mostrar pregunta del usuario en pantalla
    with st.chat_message("user"):
        st.write(prompt)
    
    # Guardar en el historial
    st.session_state.messages.append({"role": "user", "content": prompt})

    # 2. Generar la respuesta usando el Core de RAG
    with st.chat_message("assistant"):
        with st.spinner("Buscando en los reglamentos de la UNDC..."):
            resultado = responder_pregunta_undc(prompt)
            respuesta = resultado["respuesta"]
            fuentes = resultado["fuentes"]
            
            st.write(respuesta)
            
            # Si hay fuentes, las desplegamos de manera elegante
            if fuentes:
                with st.expander("📚 Ver fuentes consultadas"):
                    for fuente in fuentes:
                        st.write(f"- {fuente}")

    # Guardar la respuesta de la IA en el historial de sesión
    st.session_state.messages.append({
        "role": "assistant",
        "content": respuesta,
        "fuentes": fuentes
    })