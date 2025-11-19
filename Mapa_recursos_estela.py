import streamlit as st
import pandas as pd
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode

# Configuración de la página
st.set_page_config(page_title="Buscador de recursos e-stela", layout="wide")

# URL de imagen de fondo
fondo_url = "https://lh3.googleusercontent.com/RgI1Jv1scZCNCly5WK2R6Ky4o9IWQXtYhDPW5r5YVVkXCI4x-mN0vqtCSoZdRMiHy-cehlnI_ICQ9TTtHPIK2T04AYPPDDDZ626_6Lacl_ipPmB6e84Zv0ROcVgTTd3b5dOscQ9euOvzpbPMVM_AeUBgZZoObtGrxUoQUS_ykzRWoiUbNMH4_Q=w1280"

# Fondo con cover y ocultar elementos de interfaz (Share, Manage App)
st.markdown(f"""
    <style>
    .stApp {{
        background: url('{fondo_url}') no-repeat center center fixed;
        background-size: cover;
    }}

    /* Ocultar barra superior derecha */
    div[data-testid="stToolbar"] {{
        display: none !important;
    }}

    /* Ocultar botón "Manage app" inferior derecho */
    div[data-testid="stStatusWidget"] {{
        display: none !important;
    }}

    /* Ocultar menú de hamburguesa superior derecha */
    div[data-testid="stHeader"] {{
        display: none !important;
    }}

    /* Asegurar que los botones del sidebar ocupen todo el ancho de su columna */
    section[data-testid="stSidebar"] button {{
        width: 100% !important;
    }}
    </style>
""", unsafe_allow_html=True)

# Fuente Montserrat
st.markdown("""
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Montserrat:wght@400;600&display=swap" rel="stylesheet">
    <style>
    html * { font-family: 'Montserrat', sans-serif !important; font-weight: 400 !important; }
    h1, h2, h3, h4, h5, h6 { font-weight: 600 !important; }
    .ag-theme-streamlit, .ag-cell, .ag-header-cell { font-family: Arial, sans-serif !important; }
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

# Estado inicial de búsqueda y visibilidad de filtros
if "search_clicked" not in st.session_state:
    st.session_state.search_clicked = False

if "show_filters" not in st.session_state:
    st.session_state.show_filters = True  # mostrar filtros al inicio

def clear_filters():
    st.session_state.search_clicked = False
    st.session_state.by_content = False
    st.session_state.by_rie = False
    st.session_state.content_term = ""
    st.session_state.rie_term = ""
    st.session_state.grados = []
    st.session_state.espacios = []
    st.session_state.unidades = []

# --- SIDEBAR ---

# Siempre mostramos algún control en el sidebar, aunque esté "oculto"
if st.session_state.show_filters:
    # Título de filtros
    st.sidebar.markdown("<h2>Filtros de búsqueda</h2>", unsafe_allow_html=True)

    by_content = st.sidebar.checkbox(
        "Buscar en los Contenidos del Programa de Educación Primaria",
        key="by_content"
    )
    by_rie = st.sidebar.checkbox(
        f"Buscar en {rie_col}",
        key="by_rie"
    )

    content_term = (
        st.sidebar.text_input(
            "",
            placeholder="Palabra o frase del programa",
            key="content_term"
        ) if by_content else ""
    )

    rie_term = (
        st.sidebar.text_input(
            "",
            placeholder=f"Palabra o frase en {rie_col}",
            key="rie_term"
        ) if by_rie else ""
    )

    grados = st.sidebar.multiselect(
        "Grado",
        sorted(df[grado_col].dropna().unique()),
        key="grados",
        placeholder="Elige una opción"
    )
    espacios = st.sidebar.multiselect(
        "Espacio",
        sorted(df[espacio_col].dropna().unique()),
        key="espacios",
        placeholder="Elige una opción"
    )
    unidades = st.sidebar.multiselect(
        "Unidad Curricular",
        sorted(df[unidad_col].dropna().unique()),
        key="unidades",
        placeholder="Elige una opción"
    )

    # Botones Buscar / Limpiar / Ocultar (todos con el mismo ancho de columna)
    bcol1, bcol2, bcol3 = st.sidebar.columns(3)
    with bcol1:
        st.button("🔍 Buscar", key="btn_buscar",
                  on_click=lambda: st.session_state.update(search_clicked=True))
    with bcol2:
        st.button("🧹 Limpiar", key="btn_limpiar", on_click=clear_filters)
    with bcol3:
        st.button("⬅ Ocultar", key="btn_ocultar",
                  on_click=lambda: st.session_state.update(show_filters=False))

    # Imagen pequeña debajo de botones
    st.sidebar.markdown("""
        <div style='text-align: center; margin-top: 20px;'>
            <img src='https://lh3.googleusercontent.com/1JtO4LDmm5yOCEnjIr3sBKI20Hqz0b6msB5chINRS4TZuL8UyDn69bYzuwK7lnHTxGr59as95mprtvrU1GRDm7b2adiF8QgM5OEhDOfV0-sqCFmslQvW3q_WA9ENRJVzkac6UyKjb6_3cyJyFg_jXgMSQOJYhwEevCCQFp7y75xsGpX7LrM3=w1280' width='120'>
        </div>
    """, unsafe_allow_html=True)

else:
    # Sidebar "oculto": solo un botón para volver a mostrar filtros
    st.sidebar.markdown("<h3>Filtros ocultos</h3>", unsafe_allow_html=True)
    st.sidebar.button("📂 Mostrar filtros", key="btn_mostrar",
                      on_click=lambda: st.session_state.update(show_filters=True))

# --- LÓGICA DE BÚSQUEDA ---

# Si nunca se hizo clic en Buscar, no mostramos resultados
if not st.session_state.search_clicked:
    st.stop()

data = df.copy()
conds = []
if st.session_state.get("by_content") and st.session_state.get("content_term"):
    conds.append(
        data[t_col].str.contains(
            st.session_state.content_term,
            case=False,
            na=False
        )
    )
if st.session_state.get("by_rie") and st.session_state.get("rie_term"):
    conds.append(
        data[rie_col].str.contains(
            st.session_state.rie_term,
            case=False,
            na=False
        )
    )

if conds:
    mask = conds[0]
    for c in conds[1:]:
        mask |= c
    data = data[mask]

grados_sel = st.session_state.get("grados", [])
espacios_sel = st.session_state.get("espacios", [])
unidades_sel = st.session_state.get("unidades", [])

if grados_sel:
    data = data[data[grado_col].isin(grados_sel)]
if espacios_sel:
    data = data[data[espacio_col].isin(espacios_sel)]
if unidades_sel:
    data = data[data[unidad_col].isin(unidades_sel)]

data_to_show = data.reset_index(drop=True)

if len(data_to_show) > 0:
    gb = GridOptionsBuilder.from_dataframe(data_to_show)
    gb.configure_pagination(paginationAutoPageSize=True)
    gb.configure_default_column(
        wrapText=True,
        autoHeight=True,
        wrapHeaderText=True,
        autoHeaderHeight=True,
        resizable=True
    )
    gb.configure_grid_options(
        enableRangeSelection=True,
        enableClipboard=True,
        enableCellTextSelection=True,
        domLayout='normal'
    )
    gb.configure_column("Contenido del Programa de Primaria", width=500)
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
else:
    st.write("No se encontraron recursos para los filtros seleccionados.")
