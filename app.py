import pandas as pd
import streamlit as st

# Configuración de la página
st.set_page_config(
    page_title="Directorio UGEL Otuzco 2026", page_icon="📚", layout="wide"
)

# --- ESTILOS CSS MINIMALISTAS Y MODERNOS (2026) ---
st.markdown(
    """
    <style>
    /* Fondo general oscuro uniforme y suave */
    .stApp {
        background-color: #0b0f19;
    }
    
    /* Tipografía principal limpia */
    h1 {
        color: #f8fafc;
        font-family: 'Inter', sans-serif;
        font-weight: 700;
        letter-spacing: -0.5px;
    }
    
    p {
        color: #94a3b8;
        font-size: 1.05rem;
    }

    /* Ocultar el texto auxiliar "Press Enter to apply" de las cajas de texto */
    .stTextInput small {
        display: none !important;
    }

    /* Eliminar cajas pesadas en los inputs y hacerlos flotantes/modernos */
    div[data-baseweb="input"] {
        background-color: #1e293b !important;
        border-radius: 8px !important;
        border: 1px solid #334155 !important;
    }
    
    div[data-baseweb="input"]:focus-within {
        border-color: #38bdf8 !important;
    }

    /* Estilo limpio para los selectores (dropdowns) */
    div[data-baseweb="select"] > div {
        background-color: #1e293b !important;
        border-radius: 8px !important;
        border: 1px solid #334155 !important;
        color: #f8fafc !important;
    }

    /* Métricas limpias sin contenedores pesados (Estilo Minimalista) */
    div[data-testid="metric-container"] {
        background-color: transparent !important;
        border: none !important;
        box-shadow: none !important;
        padding: 0px !important;
    }
    
    div[data-testid="metric-container"] label {
        color: #94a3b8 !important;
        font-weight: 500;
        font-size: 0.9rem;
    }
    
    div[data-testid="metric-container"] div[data-testid="stMetricValue"] {
        color: #38bdf8 !important;
        font-size: 2.2rem !important;
        font-weight: 700;
    }

    /* Tabla elegante sin bordes exagerados */
    div[data-testid="stDataFrame"] {
        border-radius: 8px;
        overflow: hidden;
        border: 1px solid #1e293b;
    }
    </style>
""",
    unsafe_allow_html=True,
)

# Título principal limpio
st.title("Directorio de Servidores · UGEL Otuzco")
st.markdown("Consulta institucional rápida y en tiempo real.")


# Cargar los datos desde el archivo Excel
@st.cache_data
def cargar_datos():
    excel_path = "DIRECTORIO UGEL OTUZCO 2026.xlsx"
    df_raw = pd.read_excel(excel_path, header=None)

    header_row_index = None
    for idx, row in df_raw.iterrows():
        if any(
            isinstance(v, str) and "NOMBRES Y APELLIDOS" in v.upper()
            for v in row.values
        ):
            header_row_index = idx
            break

    if header_row_index is not None:
        df = pd.read_excel(excel_path, header=header_row_index)
    else:
        df = pd.read_excel(excel_path, header=7)

    df.columns = [str(c).strip() for c in df.columns]

    col_num = next(
        (c for c in df.columns if "Nº" in c or "N°" in c or "NUM" in c.upper()),
        df.columns[0],
    )
    col_nombre = next(
        (c for c in df.columns if "NOMBRE" in c.upper()), df.columns[1]
    )

    df = df.dropna(subset=[col_nombre], how="any")
    df = df[df[col_num].notna()]

    return df


try:
    df = cargar_datos()

    # --- FILTROS MODERNOS SIN BORDES INNECESARIOS ---
    st.markdown("###")
    col1, col2 = st.columns([2, 1])

    with col1:
        busqueda = st.text_input(
            "Búsqueda general",
            placeholder="Escribe un nombre, DNI, cargo o celular...",
            label_visibility="collapsed",
        )

    area_col = next(
        (c for c in df.columns if "AREA" in c.upper() or "ÁREA" in c.upper()), None
    )
    if area_col:
        with col2:
            areas = ["Todas las áreas"] + list(df[area_col].dropna().unique())
            area_seleccionada = st.selectbox(
                "Filtrar por área", areas, label_visibility="collapsed"
            )
            if area_seleccionada != "Todas las áreas":
                df = df[df[area_col] == area_seleccionada]

    # --- BÚSQUEDA FLEXIBLE EN TIEMPO REAL ---
    if busqueda:
        palabras = busqueda.strip().split()
        if palabras:

            def safe_join(row):
                return " ".join([str(val) for val in row.values if pd.notna(val)])

            texto_completo = df.apply(safe_join, axis=1).str.lower()

            condicion = texto_completo.str.contains(palabras[0].lower(), na=False)
            for palabra in palabras[1:]:
                condicion = condicion | texto_completo.str.contains(
                    palabra.lower(), na=False
                )

            df_filtered = df[condicion]
        else:
            df_filtered = df
    else:
        df_filtered = df

    st.markdown("---")

    # Métrica limpia y moderna sin cuadros grises
    st.metric(label="Registros encontrados", value=len(df_filtered))
    st.markdown("###")

    # Mostrar la tabla interactiva optimizada
    st.dataframe(df_filtered, use_container_width=True, hide_index=True)

except Exception as e:
    st.error(f"Error al cargar el archivo de Excel: {e}")
