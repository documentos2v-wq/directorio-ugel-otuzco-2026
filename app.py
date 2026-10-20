import pandas as pd
import streamlit as st

# Configuración de la página
st.set_page_config(
    page_title="Directorio UGEL Otuzco 2026", page_icon="📚", layout="wide"
)

# --- ESTILOS CSS PARA LOGO REDONDO Y DISEÑO MODERNO ---
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

    /* Estilo del contenedor circular para el logo */
    .logo-container {
        display: flex;
        justify-content: center;
        align-items: center;
        margin-bottom: 15px;
    }
    
    .logo-circle {
        width: 90px;
        height: 90px;
        border-radius: 50%;
        overflow: hidden;
        background-color: #ffffff;
        display: flex;
        justify-content: center;
        align-items: center;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
        border: 2px solid #334155;
    }
    
    .logo-circle img {
        width: 100%;
        height: 100%;
        object-fit: cover;
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

    /* Tarjetas de resultados individuales */
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

    # --- ENCABEZADO CON LOGO CIRCULAR Y TÍTULO "UGEL - OTUZCO" ---
    # Nota: Asegúrate de guardar la imagen del logo en la misma carpeta del script con el nombre "logo.jpg" (o ajusta el nombre abajo)
    try:
        import base64

        with open("UGEL - LOGO.jpg", "rb") as image_file:
            encoded_string = base64.b64encode(image_file.read()).decode()
        st.markdown(
            f"""
            <div class="logo-container">
                <div class="logo-circle">
                    <img src="data:image/jpeg;base64,{encoded_string}" alt="Logo UGEL">
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    except Exception:
        pass  # Si el archivo no está en la ruta exacta, omite el error visualmente

    st.markdown(
        "<h1 style='text-align: center; color: #f8fafc; margin-top: 10px;'>UGEL - OTUZCO</h1>",
        unsafe_allow_html=True,
    )
    st.markdown(
        "<p style='text-align: center; color: #
