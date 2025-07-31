import streamlit as st
import pandas as pd
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode

# Configuración de la página
st.set_page_config(page_title="Buscador de recursos e-stela", layout="wide")

# URL de imagen de fondo
fondo_url = "https://lh3.googleusercontent.com/RgI1Jv1scZCNCly5WK2R6Ky4o9IWQXtYhDPW5r5YVVkXCI4x-mN0vqtCSoZdRMiHy-cehlnI_ICQ9TTtHPIK2T04AYPPDDDZ626_6Lacl_ipPmB6e84Zv0ROcVgTTd3b5dOscQ9euOvzpbPMVM_AeUBgZZoObtGrxUoQUS_ykzRWoiUbNMH4_Q=w1280"

# Fondo con cover
st.markdown(f"""
    <style>
    .stApp {{
        background: url('{fondo_url}') no-repeat center center fixed;
        background-size: cover;
    }}
    </style>
""", unsafe_allow_html=True)

# Fuente Montserrat
st.markdown("""
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Montserrat:wght@400;600&display=swap" rel="stylesheet">
    <style>
    html * {{ font-family: 'Montserrat', sans-serif !important; font-weight: 400 !important; }}
    h1, h2, h3, h4, h5, h6 {{ font-weight: 600 !important; }}
    .ag-theme-streamlit, .ag-cell, .ag-header-cell {{ font-family: Arial, sans-serif !important; }}
    </style>
""", unsafe_allow_html=True)

@st.cache_data
def load_data():
    CSV_URL = (
        "https://docs.google.com/spreadsheets/d/e/"
        "2PACX-1vQHZhdhfG9G5jCe2Tm5OpR6cY8gNk2aduQsJnaaVHR0sJg9VcCzjTNLDUVXzB8REA"
        "/pub?output=csv"
    )
    df = pd.read_csv(CSV_URL, dtype=str)
    df.columns = df.columns.str.strip().str.replace("\n", " ").str.replace("\r", " ")
    return df

df = load_data()
df.columns = [c.strip() for c in df.columns]

# Detectar columnas
t_col = next(c for c in df.columns if "contenidos" in c.lower())
rie_col = next(c for c in df.columns if "rie" in c.lower())
grado_col = next(c for c in df.columns if c.lower() == "grado")
espacio_col = next(c for c in df.columns if c.lower() == "espacio")
unidad_col = next(c for c in df.columns if "unidad" in c.lower())

df = df.rename(columns={t_col: "Contenido del Programa de Primaria"})
t_col = "Contenido del Programa de Primaria"

if "search_clicked" not in st.session_state:
    st.session_state.search_clicked = False

def clear_filters():
    st.session_state.search_clicked = False
    st.session_state.by_content = False
    st.session_state.by_rie = False
    st.session_state.content_term = ""
    st.session_state.rie_term = ""
    st.session_state.grados = []
    st.session_state.espacios = []
    st.session_state.unidades = []

# Filtros
st.sidebar.markdown("<h2>Filtros de búsqueda</h2>", unsafe_allow_html=True)
by_content = st.sidebar.checkbox("Buscar en los Contenidos del Programa de Educación Primaria", key="by_content")
by_rie = st.sidebar.checkbox(f"Buscar en {rie_col}", key="by_rie")

content_term = (st.sidebar.text_input("", placeholder="Palabra o frase del programa", key="content_term") if by_content else "")
rie_term = (st.sidebar.text_input("", placeholder=f"Palabra o frase en {rie_col}", key="rie_term") if by_rie else "")

grados = st.sidebar.multiselect("Grado", sorted(df[grado_col].dropna().unique()), key="grados", placeholder="Elige una opción")
espacios = st.sidebar.multiselect("Espacio", sorted(df[espacio_col].dropna().unique()), key="espacios", placeholder="Elige una opción")
unidades = st.sidebar.multiselect("Unidad Curricular", sorted(df[unidad_col].dropna().unique()), key="unidades", placeholder="Elige una opción")

col1, col2 = st.sidebar.columns(2)
with col1: col1.button("🔍 Buscar", on_click=lambda: st.session_state.update(search_clicked=True))
with col2: col2.button("🧹 Limpiar", on_click=clear_filters)

# Imagen pequeña debajo de botones
st.sidebar.markdown("""
    <div style='text-align: center; margin-top: 20px;'>
        <img src='https://lh3.googleusercontent.com/1JtO4LDmm5yOCEnjIr3sBKI20Hqz0b6msB5chINRS4TZuL8UyDn69bYzuwK7lnHTxGr59as95mprtvrU1GRDm7b2adiF8QgM5OEhDOfV0-sqCFmslQvW3q_WA9ENRJVzkac6UyKjb6_3cyJyFg_jXgMSQOJYhwEevCCQFp7y75xsGpX7LrM3=w1280' width='120'>
    </div>
""", unsafe_allow_html=True)

if not st.session_state.search_clicked:
    st.stop()

data = df.copy()
conds = []
if by_content and content_term: conds.append(data[t_col].str.contains(content_term, case=False, na=False))
if by_rie and rie_term: conds.append(data[rie_col].str.contains(rie_term, case=False, na=False))
if conds:
    mask = conds[0]
    for c in conds[1:]: mask |= c
    data = data[mask]

if grados: data = data[data[grado_col].isin(grados)]
if espacios: data = data[data[espacio_col].isin(espacios)]
if unidades: data = data[data[unidad_col].isin(unidades)]

data_to_show = data.reset_index(drop=True)

if len(data_to_show) > 0:
    gb = GridOptionsBuilder.from_dataframe(data_to_show)
    gb.configure_pagination(paginationAutoPageSize=True)
    gb.configure_default_column(wrapText=True, autoHeight=True, wrapHeaderText=True, autoHeaderHeight=True)
    gb.configure_grid_options(enableRangeSelection=True, enableClipboard=True, enableCellTextSelection=True)
    gb.configure_column("Contenido del Programa de Primaria", width=400)
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
