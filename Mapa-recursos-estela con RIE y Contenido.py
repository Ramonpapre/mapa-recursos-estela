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
rie_col       = next(col for col in df.columns if "rie" in col.lower())
grado_col     = next(col for col in df.columns if col.lower() == "grado")
espacio_col   = next(col for col in df.columns if col.lower() == "espacio")
unidad_col    = next(col for col in df.columns if "unidad" in col.lower())

# Inicializar flag de búsqueda en sesión
if "search_clicked" not in st.session_state:
    st.session_state.search_clicked = False

# Sidebar: opciones de búsqueda
st.sidebar.markdown("<h2>🔎 Filtros de búsqueda</h2>", unsafe_allow_html=True)
by_content = st.sidebar.checkbox(f"Buscar en {contenido_col}")
by_rie     = st.sidebar.checkbox(f"Buscar en {rie_col}")

content_term = ""
rie_term     = ""
if by_content:
    content_term = st.sidebar.text_input(
        "", placeholder=f"Palabra o frase en {contenido_col}..."
    )
if by_rie:
    rie_term = st.sidebar.text_input(
        "", placeholder=f"Palabra o frase en {rie_col}..."
    )

# Filtros adicionales
grados   = st.sidebar.multiselect(
    "Grado", options=sorted(df[grado_col].dropna().unique())
)
espacios = st.sidebar.multiselect(
    "Espacio", options=sorted(df[espacio_col].dropna().unique())
)
unidades = st.sidebar.multiselect(
    "Unidad Curricular", options=sorted(df[unidad_col].dropna().unique())
)

# Botón Buscar
if st.sidebar.button("🔍 Buscar"):
    st.session_state.search_clicked = True

# Mensaje inicial antes de buscar
if not st.session_state.search_clicked:
    st.write("🔹 Configura los filtros y haz clic en **Buscar** para ver los recursos.")
    st.stop()

# Aplicar filtros de búsqueda
data = df.copy()

# Condiciones de texto por columnas
conds = []
if by_content and content_term:
    conds.append(
        data[contenido_col].astype(str).str.contains(content_term, case=False, na=False)
    )
if by_rie and rie_term:
    conds.append(
        data[rie_col].astype(str).str.contains(rie_term, case=False, na=False)
    )
if conds:
    combined = conds[0]
    for c in conds[1:]:
        combined |= c
    data = data[combined]

# Aplicar filtros de multiselección
if grados:
    data = data[data[grado_col].isin(grados)]
if espacios:
    data = data[data[espacio_col].isin(espacios)]
if unidades:
    data = data[data[unidad_col].isin(unidades)]

# Preparar datos para mostrar
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
