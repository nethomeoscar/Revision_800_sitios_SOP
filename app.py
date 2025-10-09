import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
from io import BytesIO
from xlsxwriter import Workbook

# Cargar datos
df = pd.read_csv('Revisión 800 sitios.csv', encoding='latin1')

# Filtrar datos válidos
df = df.dropna(subset=['Latitud', 'Longitud', 'Bajada', 'Subida', 'Calificación'])
df = df[(df['Bajada'] > -1) & (df['Subida'] > -1)]

# Sidebar: filtros
municipios = sorted(df['Municipio'].dropna().unique())
tipos_espacio = sorted(df['Tipo de espacio'].dropna().unique())

municipio_sel = st.sidebar.multiselect("Filtrar por municipio", municipios, default=municipios)
tipo_sel = st.sidebar.multiselect("Filtrar por tipo de espacio", tipos_espacio, default=tipos_espacio)
capa_sel = st.sidebar.radio("Selecciona capa a mostrar", ['Calificación', 'Velocidad de Bajada', 'Velocidad de Subida'])

# Aplicar filtros
df_filtrado = df[df['Municipio'].isin(municipio_sel) & df['Tipo de espacio'].isin(tipo_sel)]

# Crear mapa
m = folium.Map(location=[21.12, -101.68], zoom_start=12)

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
        color = 'green' if row['Calificación'] >= 7 else 'orange' if row['Calificación'] == 6 else 'red'
        radius = 6
    elif capa_sel == 'Velocidad de Bajada':
        color = 'blue'
        radius = row['Bajada'] / 5
    elif capa_sel == 'Velocidad de Subida':
        color = 'purple'
        radius = row['Subida'] / 5

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
st_folium(m, width=900, height=600)

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