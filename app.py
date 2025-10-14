import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
from io import BytesIO
from xlsxwriter import Workbook

# --- Personalización de estilos ---
st.set_page_config(page_title="Evaluación de Sitios Públicos - León GTO", layout="wide")
st.markdown("""
    <style>
    .main {background-color: #f8fafc;}
    .block-container {padding-top: 2rem;}
    .stButton>button {background-color: #2563eb; color: white;}
    .stDataFrame {background-color: #f1f5f9;}
    .css-1v0mbdj {background-color: #f1f5f9;}
    </style>
""", unsafe_allow_html=True)

# --- Encabezado con columnas ---
col1, col2 = st.columns([1, 6])
with col1:
    st.image("NetHome.jpg", width=120)
with col2:
    st.title("📡 Evaluación de Sitios Públicos con Conectividad")
    st.markdown("""
    <span style='font-size:18px; color:#2563eb;'>
    Este mapa interactivo presenta los resultados de la revisión técnica de más de <b>800 sitios públicos</b> en León, Silao, Guanajuato, Irapuato, Salamanca y Celaya evaluando su conectividad a internet mediante pruebas de velocidad, estabilidad y accesibilidad.
    </span>
    """, unsafe_allow_html=True)

st.markdown("""
<div style='background-color:#e0e7ef; padding: 1rem; border-radius: 10px;'>
<b>Objetivo del estudio:</b> Identificar zonas con buena conectividad y aquellas que requieren mejora, para apoyar decisiones de infraestructura y servicio.<br>
<b>¿Cómo usar esta herramienta?</b>
<ul>
<li>Usa los <b>filtros</b> en el panel lateral para seleccionar municipios y tipos de espacio.</li>
<li>Elige la <b>capa</b> que deseas visualizar: calificación, velocidad de bajada o subida.</li>
<li>Haz clic en los <b>marcadores</b> para ver detalles del sitio.</li>
<li>Exporta los datos filtrados en Excel para análisis adicional.</li>
</ul>
</div>
""", unsafe_allow_html=True)

# --- Cargar datos ---
df = pd.read_csv('Revisión 800 sitios.csv', encoding='latin1')
df = df.dropna(subset=['Latitud', 'Longitud', 'Bajada', 'Subida', 'Calificación'])
df = df[(df['Bajada'] > -1) & (df['Subida'] > -1)]

# --- Sidebar: filtros ---
st.sidebar.header("🔎 Filtros")
municipios = sorted(df['Municipio'].dropna().unique())
tipos_espacio = sorted(df['Tipo de espacio'].dropna().unique())
calificacion = sorted(df['Calificación'].dropna().unique())

municipio_sel = st.sidebar.multiselect("Municipio", municipios, default=municipios)
tipo_sel = st.sidebar.multiselect("Tipo de espacio", tipos_espacio, default=tipos_espacio)
calif_sel = st.sidebar.multiselect("Calificación", calificacion, default=calificacion)
capa_sel = st.sidebar.radio("Capa a mostrar", ['Calificación', 'Velocidad de Bajada', 'Velocidad de Subida'])

# --- Aplicar filtros ---
df_filtrado = df[df['Municipio'].isin(municipio_sel) & df['Tipo de espacio'].isin(tipo_sel) & df['Calificación'].isin(calif_sel)]

# --- Crear mapa ---
m = folium.Map(location=[20.866064, -101.176864], zoom_start=9, tiles="CartoDB positron")

def generar_popup(row):
    return folium.Popup(f"""
    <b>{row['Sitio']}</b><br>
    <b>{row['Nombre']}</b><br>
    <b>Municipio:</b> {row['Municipio']}<br>
    <b>Tipo de espacio:</b> {row['Tipo de espacio']}<br>
    <b>Tipo de conexión:</b> {row['Tipo de conexión']}<br>
    <b>Calificación:</b> {row['Calificación']}<br>
    <b>Bajada:</b> {row['Bajada']} Mbps<br>
    <b>Subida:</b> {row['Subida']} Mbps<br>
    <b>Observaciones:</b> {row['Observaciones']}
    """, max_width=300)

for _, row in df_filtrado.iterrows():
    if capa_sel == 'Calificación':
        color = 'green' if row['Calificación'] >= 7 else 'orange' if row['Calificación'] == 5 else 'red'
        radius = 7
    elif capa_sel == 'Velocidad de Bajada':
        color = 'blue'
        radius = max(5, min(row['Bajada'] / 4, 15))
    elif capa_sel == 'Velocidad de Subida':
        color = 'purple'
        radius = max(5, min(row['Subida'] / 4, 15))

    folium.CircleMarker(
        location=[row['Latitud'], row['Longitud']],
        radius=radius,
        color=color,
        fill=True,
        fill_color=color,
        fill_opacity=0.7,
        popup=generar_popup(row)
    ).add_to(m)

st.markdown("### 🗺️ Mapa interactivo de evaluación de sitios")
st_folium(m, width=950, height=520)

# --- Resumen estadístico ---
st.markdown("### 📊 Resumen por municipio")
resumen = df_filtrado.groupby('Municipio')[['Bajada', 'Subida', 'Calificación']].mean().round(2)
st.dataframe(resumen.style.background_gradient(cmap='Blues'), use_container_width=True)

# --- Exportar datos filtrados ---
st.markdown("### 📥 Exportar datos filtrados")
def convertir_excel(df):
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='Datos filtrados')
    return output.getvalue()

archivo_excel = convertir_excel(df_filtrado)
st.download_button(
    label="⬇️ Descargar Excel",
    data=archivo_excel,
    file_name="datos_filtrados.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
)

# --- Evaluación por rubros ---
st.markdown("### 📝 Evaluación por Rubros: Resultados de Pruebas")
st.markdown("""
Se evaluaron <b>8 rubros clave</b> mediante pruebas específicas. Cada prueba equivale a un punto. 
El puntaje total refleja el número de pruebas superadas satisfactoriamente.
""", unsafe_allow_html=True)

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
df_rubros = pd.DataFrame(data)
st.dataframe(df_rubros.style.highlight_max(axis=0, color="#ffffff"), use_container_width=True)