# Guarda este archivo como: Mapa_recursos_estela.py
import streamlit as st
import pandas as pd

# Configuración de la página
st.set_page_config(
    page_title="Buscador de recursos E-Stela",
    layout="wide",
)

# Título principal
st.title("🔍 Buscador de recursos E-Stela")

@st.cache_data
def load_data():
    SHEET_ID = "1sFzavqHkqsYOVU9RM7XYIKHZkDNgdiDb"
    url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=xlsx"
    df = pd.read_excel(url, sheet_name=0)
    # Limpieza de nombres de columna
    df.columns = (
        df.columns
          .str.strip()
          .str.replace("\n", " ")
          .str.replace("\r", " ")
    )
    return df

# Carga de datos
df = load_data()
df.columns = [col.strip() for col in df.columns]

# Detectar dinámicamente las columnas clave
contenido_col = next(col for col in df.columns if "contenidos" in col.lower())
grado_col     = next(col for col in df.columns if col.lower() == "grado")
espacio_col   = next(col for col in df.columns if col.lower() == "espacio")
unidad_col    = next(col for col in df.columns if "unidad" in col.lower())

# Sidebar: buscador + filtros + botón
# Mostrar solo el texto de búsqueda en tamaño mayor
st.sidebar.markdown(
    f"<h2>Buscar según Programa de Educación Básica Integrada (EBI)</h2>",
    unsafe_allow_html=True
)

# Caja de texto para el término de búsqueda (sin label redundante)
término = st.sidebar.text_input(
    "",
    placeholder="Introduce palabra o frase..."
)

# Filtros
grados   = st.sidebar.multiselect(
    "Grado",
    options=sorted(df[grado_col].dropna().unique())
)
espacios = st.sidebar.multiselect(
    "Espacio",
    options=sorted(df[espacio_col].dropna().unique())
)
unidades = st.sidebar.multiselect(
    "Unidad Curricular",
    options=sorted(df[unidad_col].dropna().unique())
)

# Botón de búsqueda
buscar = st.sidebar.button("🔍 Buscar")

# Solo cuando se pulse “Buscar” aplicamos filtros y mostramos resultados
if buscar:
    data = df.copy()
    if término:
        data = data[
            data[contenido_col]
                .astype(str)
                .str.contains(término, case=False, na=False)
        ]
    if grados:
        data = data[data[grado_col].isin(grados)]
    if espacios:
        data = data[data[espacio_col].isin(espacios)]
    if unidades:
        data = data[data[unidad_col].isin(unidades)]

    st.write(f"Se encontraron {len(data)} recursos:")
    # Eliminamos el índice para que no aparezca
    data_to_show = data.reset_index(drop=True)
    st.dataframe(data_to_show)
else:
    st.write("🔹 Usa los filtros y haz clic en **Buscar** para ver los recursos.")
