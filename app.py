import pandas as pd
import streamlit as st

# Configuración de la página
st.set_page_config(
    page_title="Directorio UGEL Otuzco 2026", page_icon="📚", layout="wide"
)

# --- ESTILOS CSS ESTILO BUSCADOR MODERNO ---
st.markdown(
    """
    <style>
    /* Fondo general oscuro elegante */
    .stApp {
        background-color: #0b0f19;
    }
    
    /* Ocultar el texto auxiliar "Press Enter to apply" */
    .stTextInput small {
        display: none !important;
    }

    /* Estilo para simular la barra de búsqueda central grande */
    div[data-baseweb="input"] {
        background-color: #161e2e !important;
        border-radius: 12px !important;
        border: 1px solid #334155 !important;
        padding: 4px 10px !important;
    }
    
    div[data-baseweb="input"]:focus-within {
        border-color: #38bdf8 !important;
    }

    /* Tarjetas de resultados individuales (Estilo Blog / Tarjeta limpia) */
    .resultado-card {
        background-color: #131c2e;
        border: 1px solid #1e293b;
        padding: 20px;
        border-radius: 12px;
        margin-bottom: 15px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.2);
        transition: border-color 0.2s;
    }
    
    .resultado-card:hover {
        border-color: #334155;
    }

    .card-title {
        color: #f8fafc;
        font-size: 1.2rem;
        font-weight: 600;
        margin-bottom: 8px;
    }

    .card-info {
        color: #94a3b8;
        font-size: 0.95rem;
        margin-bottom: 4px;
    }
    
    .badge-area {
        display: inline-block;
        background-color: #1e293b;
        color: #38bdf8;
        padding: 3px 10px;
        border-radius: 6px;
        font-size: 0.8rem;
        font-weight: 500;
        margin-top: 8px;
    }
    </style>
""",
    unsafe_allow_html=True,
)


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

    # --- ENCABEZADO Y BARRA DE BÚSQUEDA CENTRAL ---
    st.markdown(
        "<h1 style='text-align: center; color: #f8fafc; margin-top: 20px;'>Encuentra tu búsqueda</h1>",
        unsafe_allow_html=True,
    )
    st.markdown(
        "<p style='text-align: center; color: #94a3b8; margin-bottom: 30px;'>Directorio de Servidores - UGEL Otuzco 2026</p>",
        unsafe_allow_html=True,
    )

    # Centrar la barra de búsqueda principal usando columnas
    _, col_centro, _ = st.columns([1, 3, 1])
    with col_centro:
        busqueda = st.text_input(
            "Búsqueda",
            placeholder="🔍 Escribe un nombre, DNI, cargo o celular...",
            label_visibility="collapsed",
        )

    # Filtro opcional de área en la parte superior derecha o debajo
    area_col = next(
        (c for c in df.columns if "AREA" in c.upper() or "ÁREA" in c.upper()), None
    )
    if area_col:
        st.markdown("<br>", unsafe_allow_html=True)
        _, col_filtro, _ = st.columns([2, 2, 2])
        with col_filtro:
            areas = ["Todas las áreas"] + list(df[area_col].dropna().unique())
            area_seleccionada = st.selectbox(
                "Filtrar por área", areas, label_visibility="collapsed"
            )
            if area_seleccionada != "Todas las áreas":
                df = df[df[area_col] == area_seleccionada]

    # --- LÓGICA DE FILTRADO ---
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

    st.markdown("<br>", unsafe_allow_html=True)

    # Contador de resultados
    st.markdown(
        f"<p style='color: #64748b; font-size: 0.95rem;'><b>{len(df_filtered)}</b> resultados encontrados</p>",
        unsafe_allow_html=True,
    )
    st.markdown("---")

    # --- RENDERIZAR RESULTADOS EN FORMATO DE TARJETAS ---
    for _, row in df_filtered.iterrows():
        # Detectar columnas clave de manera segura
        nombre = next(
            (
                str(row[c])
                for c in df.columns
                if "NOMBRE" in c.upper() and pd.notna(row[c])
            ),
            "Sin Nombre",
        )
        cargo = next(
            (
                str(row[c])
                for c in df.columns
                if "CARGO" in c.upper() and pd.notna(row[c])
            ),
            "Sin Cargo",
        )
        dni = next(
            (
                str(row[c])
                for c in df.columns
                if "DNI" in c.upper() and pd.notna(row[c])
            ),
            "N/A",
        )
        celular = next(
            (
                str(row[c])
                for c in df.columns
                if ("CEL" in c.upper() or "TEL" in c.upper())
                and pd.notna(row[c])
            ),
            "N/A",
        )
        correo = next(
            (
                str(row[c])
                for c in df.columns
                if ("CORREO" in c.upper() or "EMAIL" in c.upper())
                and pd.notna(row[c])
            ),
            "N/A",
        )
        area = (
            str(row[area_col])
            if area_col and pd.notna(row[area_col])
            else "General"
        )

        # HTML de la tarjeta individual tipo buscador
        st.markdown(
            f"""
            <div class="resultado-card">
                <div class="card-title">👤 {nombre}</div>
                <div class="card-info"><b>Cargo:</b> {cargo}</div>
                <div class="card-info"><b>DNI:</b> {dni} &nbsp;&nbsp;|&nbsp;&nbsp; <b>Celular:</b> {celular} &nbsp;&nbsp;|&nbsp;&nbsp; <b>Correo:</b> {correo}</div>
                <div><span class="badge-area">📁 {area}</span></div>
            </div>
            """,
            unsafe_allow_html=True,
        )

except Exception as e:
    st.error(f"Error al cargar el archivo de Excel: {e}")
