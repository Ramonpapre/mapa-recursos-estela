# Guarda este archivo como: Mapa_recursos_estela.py
import streamlit as st
import pandas as pd
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode

# Configuración de la página
st.set_page_config(
    page_title="Buscador de recursos E-Stela",
    layout="wide",
)

# Título principal
st.title("🔍 Buscador de recursos E-Stela")

@st.cache_data
def load_data():
    CSV_URL = (
        "https://docs.google.com/spreadsheets/d/e/"
        "2PACX-1vQHZhdhfG9G5jCe2Tm5OpR6cY8gNk2aduQsJnaaVHR0sJg9VcCzjTNLDUVXzB8REA"
        "/pub?output=csv"
    )
    df = pd.read_csv(CSV_URL)
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

# Columnas dinámicas
contenido_col = next(col for col in df.columns if "contenidos" in col.lower())
grado_col     = next(col for col in df.columns if col.lower() == "grado")
espacio_col   = next(col for col in df.columns if col.lower() == "espacio")
unidad_col    = next(col for col in df.columns if "unidad" in col.lower())

# Inicializar flag de búsqueda en sesión
if "search_clicked" not in st.session_state:
    st.session_state.search_clicked = False

# Sidebar: buscador + filtros
st.sidebar.markdown(f"<h2>🔎 Buscar en {contenido_col}</h2>", unsafe_allow_html=True)
término  = st.sidebar.text_input("", placeholder="Introduce palabra o frase...")
grados   = st.sidebar.multiselect("Grado", options=sorted(df[grado_col].dropna().unique()))
espacios = st.sidebar.multiselect("Espacio", options=sorted(df[espacio_col].dropna().unique()))
unidades = st.sidebar.multiselect("Unidad Curricular", options=sorted(df[unidad_col].dropna().unique()))

# Botón Buscar
if st.sidebar.button("🔍 Buscar"):
    st.session_state.search_clicked = True

# Si no se ha hecho clic en Buscar, mostramos un mensaje y terminamos
if not st.session_state.search_clicked:
    st.write("🔹 Configura tus filtros y haz clic en **Buscar** para ver los recursos.")
    st.stop()

# Una vez clickeado Buscar, aplicamos filtros de forma reactiva
data = df.copy()
if término:
    data = data[data[contenido_col].astype(str).str.contains(término, case=False, na=False)]
if grados:
    data = data[data[grado_col].isin(grados)]
if espacios:
    data = data[data[espacio_col].isin(espacios)]
if unidades:
    data = data[data[unidad_col].isin(unidades)]

data_to_show = data.reset_index(drop=True)
st.write(f"Se encontraron {len(data_to_show)} recursos:")

# Configurar AgGrid
gb = GridOptionsBuilder.from_dataframe(data_to_show)
gb.configure_pagination(paginationAutoPageSize=True)

# Estilo por defecto para centrar y ajustar texto
default_style = {
    "display": "flex",
    "alignItems": "center",
    "justifyContent": "center",
}
gb.configure_default_column(
    wrapText=True,
    autoHeight=True,
    wrapHeaderText=True,
    autoHeaderHeight=True,
    cellStyle=default_style
)

gb.configure_grid_options(
    enableRangeSelection=True,
    enableClipboard=True,
    enableCellTextSelection=True
)
grid_options = gb.build()

AgGrid(
    data_to_show,
    gridOptions=grid_options,
    enable_enterprise_modules=False,
    fit_columns_on_grid_load=True,
    height=600,
    selection_mode='single',
    update_mode=GridUpdateMode.SELECTION_CHANGED,
    allow_unsafe_jscode=True,
)
