import base64
import pandas as pd
import streamlit as st

# Configuración de la página
st.set_page_config(
    page_title="Directorio UGEL Otuzco 2026", page_icon="📚", layout="centered"
)

# --- ESTILOS CSS MODERNOS Y ANIMACIÓN RETRO ---
st.markdown(
    """
    <style>
    .stApp {
        background-color: #0b0f19;
    }
    
    .stTextInput small {
        display: none !important;
    }

    .logo-container {
        display: flex;
        justify-content: center;
        align-items: center;
        margin-top: 15px;
        margin-bottom: 10px;
    }
    
    .logo-circle {
        width: 85px;
        height: 85px;
        border-radius: 50%;
        overflow: hidden;
        background-color: #ffffff;
        display: flex;
        justify-content: center;
        align-items: center;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.4);
        border: 2px solid #334155;
    }
    
    .logo-circle img {
        width: 100%;
        height: 100%;
        object-fit: cover;
    }

    /* Tarjeta de resultado única y completa */
    .resultado-card {
        background-color: #131c2e;
        border: 1px solid #1e293b;
        padding: 18px;
        border-radius: 12px;
        margin-bottom: 15px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.2);
    }
    
    .card-title {
        color: #f8fafc;
        font-size: 1.15rem;
        font-weight: 600;
        margin-bottom: 10px;
        border-bottom: 1px solid #1e293b;
        padding-bottom: 6px;
    }

    .card-grid {
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 8px;
    }

    .card-info {
        color: #94a3b8;
        font-size: 0.9rem;
        margin-bottom: 4px;
    }
    
    .card-info span {
        color: #f1f5f9;
    }

    /* Animación estilo arcade / puntos (Buscando en agenda) */
    .empty-state {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        margin-top: 40px;
        text-align: center;
    }

    .pixel-book-container {
        position: relative;
        width: 90px;
        height: 70px;
        animation: floatBook 1.5s ease-in-out infinite alternate;
    }

    @keyframes floatBook {
        0% { transform: translateY(0px); }
        100% { transform: translateY(-8px); }
    }

    /* Páginas pasando con efecto de pulso y movimiento */
    .page-flip {
        animation: flipPage 0.8s steps(2, start) infinite;
        transform-origin: left center;
    }

    @keyframes flipPage {
        0% { transform: rotateY(0deg); opacity: 0.8; }
        50% { transform: rotateY(-45deg); opacity: 1; }
        100% { transform: rotateY(0deg); opacity: 0.8; }
    }
    </style>
""",
    unsafe_allow_html=True,
)


def limpiar_valor(val):
  if pd.isna(val):
    return "N/A"
  s = str(val).strip()
  if s.endswith(".0"):
    s = s[:-2]
  return s if s and s.lower() != "none" else "N/A"


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

  # Carga robusta del logo en círculo
  logo_html = ""
  try:
    with open("UGEL - LOGO.jpg", "rb") as image_file:
      encoded_string = base64.b64encode(image_file.read()).decode()
      logo_html = f"""
            <div class="logo-container">
                <div class="logo-circle">
                    <img src="data:image/jpeg;base64,{encoded_string}" alt="Logo UGEL">
                </div>
            </div>
            """
  except Exception:
    try:
      with open("logo.jpg", "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read()).decode()
        logo_html = f"""
                <div class="logo-container">
