# Guarda este archivo como: Mapa_recursos_estela.py
import streamlit as st
import pandas as pd
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode

# 1) Configuración de la página (debe ser lo primero)
st.set_page_config(
    page_title="Buscador de recursos E-Stela",
    layout="wide",
)

# 2) Inyección de CSS para imagen de fondo (opcional)
st.markdown("""
    <style>
    .stApp {
        background-image: url("https://drive.google.com/uc?export=view&id=1Fe9_6CuknIC3aJjpbbACpyK6cGmLO1voj");
        background-position: left bottom;
        background-repeat: no-repeat;
        background-size: 200px auto;
    }
    </style>
""", unsafe_allow_html=True)

# 3) Título principal
st.title("🔍 Buscador de recursos E-Stela")

@st.cache_data
def load_data():
    CSV_URL = (
        "https://docs.google.com/spreadsheets/d/e/"
        "2PACX-1vQHZhdhfG9G5jCe2Tm5OpR6cY8gNk2aduQsJnaaVHR0sJg9VcCzjTNLDUVXzB8REA"
        "/pub?output=csv"
    )
    df = pd.read_csv(CSV_URL, dtype=str)
    df.columns = (
        df.columns.str.strip()
                  .str.replace("\n", " ")
                  .str.replace("\r", " ")
    )
    return df

# 4) Carga de datos
df = load_data()
df.columns = [c.strip() for c in df.columns]

# 5) Detectar columnas dinámicas
contenido_col = next(c for c in df.columns if "contenidos" in c.lower())
rie_col       = next(c for c in df.columns if "rie" in c.lower())
grado_col     = next(c for c in df.columns if c.lower() == "grado")
espacio_col   = next(c for c in df.columns if c.lower() == "espacio")
unidad_col    = next(c for c in df.columns if "unidad" in c.lower())

# 6) Inicializar estado de búsqueda
if "search_clicked" not in st.session_state:
    st.session_state.search_clicked = False

# Callback para limpiar filtros
def clear_filters():
    st.session_state.search_clicked = False
    st.session_state.by_content     = False
    st.session_state.by_rie         = False
    st.session_state.content_term   = ""
    st.session_state.rie_term       = ""
    st.session_state.grados         = []
    st.session_state.espacios       = []
    st.session_state.unidades       = []

# 7) Sidebar: filtros
st.sidebar.markdown("<h2>🔎 Filtros de búsqueda</h2>", unsafe_allow_html=True)
by_content = st.sidebar.checkbox(f"Buscar en {contenido_col}", key="by_content")
by_rie     = st.sidebar.checkbox(f"Buscar en {rie_col}",     key="by_rie")

content_term = (
    st.sidebar.text_input("", placeholder=f"Palabra o frase en {contenido_col}…", key="content_term")
    if by_content else ""
)
rie_term = (
    st.sidebar.text_input("", placeholder=f"Palabra o frase en {rie_col}…", key="rie_term")
    if by_rie else ""
)

grados   = st.sidebar.multiselect("Grado", sorted(df[grado_col].dropna().unique()), key="grados")
espacios = st.sidebar.multiselect("Espacio", sorted(df[espacio_col].dropna().unique()), key="espacios")
unidades = st.sidebar.multiselect("Unidad Curricular", sorted(df[unidad_col].dropna().unique()), key="unidades")

# 8) Botones alineados: Buscar a la izquierda, Limpiar a la derecha
col1, col2 = st.sidebar.columns(2)
with col1:
    col1.button("🔍 Buscar", on_click=lambda: st.session_state.update(search_clicked=True))
with col2:
    col2.button("🧹 Limpiar", on_click=clear_filters)

# 9) Antes de buscar
if not st.session_state.search_clicked:
    st.write("🔹 Configura los filtros y haz clic en **Buscar** para ver los recursos.")
    st.stop()

# 10) Aplicar filtros de texto
data = df.copy()
conds = []
if by_content and content_term:
    conds.append(data[contenido_col].str.contains(content_term, case=False, na=False))
if by_rie and rie_term:
    conds.append(data[rie_col].str.contains(rie_term, case=False, na=False))
if conds:
    mask = conds[0]
    for c in conds[1:]:
        mask |= c
    data = data[mask]

# 11) Aplicar filtros de multiselección
if grados:
    data = data[data[grado_col].isin(grados)]
if espacios:
    data = data[data[espacio_col].isin(espacios)]
if unidades:
    data = data[data[unidad_col].isin(unidades)]

# 12) Preparar datos y mostrar conteo
data_to_show = data.reset_index(drop=True)
st.write(f"Se encontraron {len(data_to_show)} recursos:")

# 13) Configurar y renderizar AgGrid
gb = GridOptionsBuilder.from_dataframe(data_to_show)
gb.configure_pagination(paginationAutoPageSize=True)
default_style = {"display": "flex", "alignItems": "center", "justifyContent": "center"}
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