import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
from io import BytesIO
from xlsxwriter import Workbook

# Encabezado personalizado
st.set_page_config(page_title="Evaluación de Sitios Públicos - León GTO", layout="wide")

# Logo (opcional)
st.image("NetHome.jpg", width=150)  # Asegúrate de tener el archivo en el mismo directorio

# Título y descripción
st.title("📡 Evaluación de Sitios Públicos con Conectividad")
st.markdown("""
Este mapa interactivo presenta los resultados de la revisión técnica de más de 800 sitios públicos en León, Silao, Guanajuato, Irapuato, Salamanca y Celaya evaluando su conectividad a internet mediante pruebas de velocidad, estabilidad y accesibilidad.

**Objetivo del estudio**: Identificar zonas con buena conectividad y aquellas que requieren mejora, para apoyar decisiones de infraestructura y servicio.

**¿Cómo usar esta herramienta?**
- Usa los filtros en el panel lateral para seleccionar municipios y tipos de espacio.
- Elige la capa que deseas visualizar: calificación, velocidad de bajada o subida.
- Haz clic en los marcadores para ver detalles del sitio.
- Exporta los datos filtrados en Excel para análisis adicional.

---
""")

# Cargar datos
df = pd.read_csv('Revisión 800 sitios.csv', encoding='latin1')

# Filtrar datos válidos
df = df.dropna(subset=['Latitud', 'Longitud', 'Bajada', 'Subida', 'Calificación'])
df = df[(df['Bajada'] > -1) & (df['Subida'] > -1)]

# Sidebar: filtros
municipios = sorted(df['Municipio'].dropna().unique())
tipos_espacio = sorted(df['Tipo de espacio'].dropna().unique())
calificacion = sorted(df['Calificación'].dropna().unique())


municipio_sel = st.sidebar.multiselect("Filtrar por municipio", municipios, default=municipios)
tipo_sel = st.sidebar.multiselect("Filtrar por tipo de espacio", tipos_espacio, default=tipos_espacio)
calif_sel = st.sidebar.multiselect("Calificación", calificacion, default=calificacion)
capa_sel = st.sidebar.radio("Selecciona capa a mostrar", ['Calificación', 'Velocidad de Bajada', 'Velocidad de Subida'])

# Aplicar filtros
df_filtrado = df[df['Municipio'].isin(municipio_sel) & df['Tipo de espacio'].isin(tipo_sel) & df['Calificación'].isin(calif_sel)]

# Crear mapa
m = folium.Map(location=[20.866064, -101.176864], zoom_start=9)

# Función para pop-up
def generar_popup(row):
    return folium.Popup(f"""
    <b>{row['Sitio']}</b>
    <b>{row['Nombre']}</b><br>
    Municipio: {row['Municipio']}<br>
    Tipo de espacio: {row['Tipo de espacio']}<br>
    Tipo de conexión: {row['Tipo de conexión']}<br>
    Calificación: {row['Calificación']}<br>
    Bajada: {row['Bajada']} Mbps<br>
    Subida: {row['Subida']} Mbps<br>
    Observaciones: {row['Observaciones']}
    """, max_width=300)

# Agregar marcadores según capa seleccionada
for _, row in df_filtrado.iterrows():
    if capa_sel == 'Calificación':
        color = 'green' if row['Calificación'] >= 7 else 'orange' if row['Calificación'] == 5 else 'red'
        radius = 6
    elif capa_sel == 'Velocidad de Bajada':
        color = 'blue'
        radius = row['Bajada'] / 4
    elif capa_sel == 'Velocidad de Subida':
        color = 'purple'
        radius = row['Subida'] / 4

    folium.CircleMarker(
        location=[row['Latitud'], row['Longitud']],
        radius=radius,
        color=color,
        fill=True,
        fill_color=color,
        fill_opacity=0.6,
        popup=generar_popup(row)
    ).add_to(m)

# Mostrar mapa
st.title("🗺️ Mapa interactivo de evaluación de sitios")
st.markdown("Filtra por municipio, tipo de espacio y elige la capa que deseas visualizar.")
st_folium(m, width=900, height=500)

# Mostrar resumen estadístico
st.subheader("📊 Resumen por municipio")
resumen = df_filtrado.groupby('Municipio')[['Bajada', 'Subida', 'Calificación']].mean().round(2)
st.dataframe(resumen)

# Exportar datos filtrados
st.subheader("📥 Exportar datos filtrados")
def convertir_excel(df):
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='Datos filtrados')
    return output.getvalue()

archivo_excel = convertir_excel(df_filtrado)
st.download_button(
    label="Descargar Excel",
    data=archivo_excel,
    file_name="datos_filtrados.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
)


# Título y descripción
st.subheader("Evaluación por Rubros: Resultados de Pruebas")
st.markdown("""
Se evaluaron 8 rubros clave mediante pruebas específicas. Cada prueba equivale a un punto. 
El puntaje total refleja el número de pruebas superadas satisfactoriamente.
""")

# Datos de la evaluación
data = {
    "Prueba o Aplicación": [
        "Conexión fácil", 
        "Mensajero (Telegram o WhatsApp)", 
        "FaceBook", 
        "Youtube", 
        "Google Maps", 
        "Navegación en Chrome", 
        "Navegación constante", 
        "Buen ancho de banda"
    ],
    "Lo que esperamos": [
        "Que los dispositivos se puedan conectar de manera instantánea o con el menor esfuerzo", 
        "Poder envíar mensaje", 
        "Poder ver de manera correcta las publicaciones y/o reels", 
        "Visualizar los videos", 
        "Que muestre en tiempo real la ubicación actual", 
        "Poder navegar en diversas páginas web y que muestre el contenido", 
        "Que no haya interrupciones o lentitud al momento de cargar la información", 
        "Que el ancho de banda supere los 14MB"
    ],
    "Ponderación": [1, 1, 1, 1, 1, 1, 1, 1]
}

# Crear DataFrame
df = pd.DataFrame(data)

# Mostrar tabla
st.dataframe(df, use_container_width=True)

