import base64
from difflib import SequenceMatcher
import pandas as pd
import streamlit as st

# Configuración de la página
st.set_page_config(
    page_title="Directorio UGEL Otuzco 2026", page_icon="📚", layout="centered"
)

# --- ESTILOS CSS ROBUSTOS Y SELECTOR COMPACTO ---
st.markdown(
    """
    <style>
    .stApp {
        background-color: #0b0f19 !important;
        color: #f8fafc !important;
    }
    
    .stTextInput small {
        display: none !important;
    }

    .logo-flex-center {
        display: flex;
        justify-content: center;
        align-items: center;
        width: 100%;
        margin-top: 10px;
        margin-bottom: 10px;
    }

    .logo-circle-container {
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

    .logo-circle-container img {
        width: 100%;
        height: 100%;
        object-fit: cover;
    }

    div[data-baseweb="input"] {
        background-color: #161e2e !important;
        border-radius: 12px !important;
        border: 1px solid #334155 !important;
    }

    /* Estilo compacto para el selector de modo de vista */
    div.row-widget.stRadio > div {
        display: flex;
        justify-content: center;
        flex-direction: row;
        gap: 15px;
    }
    
    div.row-widget.stRadio label {
        color: #94a3b8 !important;
        font-size: 0.85rem !important;
    }

    .resultado-card {
        background-color: #131c2e !important;
        border: 1px solid #1e293b !important;
        padding: 16px;
        border-radius: 12px;
        margin-bottom: 15px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3);
    }
    
    .card-title {
        color: #f8fafc !important;
        font-size: 1.1rem;
        font-weight: 600;
        margin-bottom: 10px;
        border-bottom: 1px solid #1e293b;
        padding-bottom: 6px;
    }

    .card-grid {
        display: grid;
        grid-template-columns: 1fr;
        gap: 6px;
    }

    @media (min-width: 640px) {
        .card-grid {
            grid-template-columns: 1fr 1fr;
            gap: 8px;
        }
    }

    .card-info {
        color: #94a3b8 !important;
        font-size: 0.9rem;
        margin-bottom: 4px;
        word-break: break-word;
    }
    
    .card-info span {
        color: #f1f5f9 !important;
    }

    .empty-state {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        margin-top: 30px;
        text-align: center;
    }

    .realistic-book {
        position: relative;
        width: 110px;
        height: 70px;
        margin-bottom: 15px;
    }

    .animated-page {
        transform-origin: 55px 35px;
        animation: flipSheet 1.4s ease-in-out infinite;
    }

    @keyframes flipSheet {
        0% { transform: rotateY(0deg); opacity: 1; }
        50% { transform: rotateY(-90deg); opacity: 0.5; }
        100% { transform: rotateY(-180deg); opacity: 0.9; }
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

  # Carga robusta y centrada del logo usando Base64
  logo_html = ""
  for filename in ["UGEL - LOGO.jpg", "logo.jpg"]:
    try:
      with open(filename, "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read()).decode()
        logo_html = f"""
                <div class="logo-flex-center">
                    <div class="logo-circle-container">
                        <img src="data:image/jpeg;base64,{encoded_string}" alt="Logo UGEL">
                    </div>
                </div>
                """
        break
    except Exception:
      pass

  if logo_html:
    st.markdown(logo_html, unsafe_allow_html=True)

  st.markdown(
      "<h1 style='text-align: center; color: #f8fafc !important; font-size:"
      " 1.5rem; margin-top: 5px;'>UGEL - OTUZCO</h1>",
      unsafe_allow_html=True,
  )
  st.markdown(
      "<p style='text-align: center; color: #94a3b8 !important; font-size:"
      " 0.9rem; margin-bottom: 20px;'>Directorio de Servidores - 2026</p>",
      unsafe_allow_html=True,
  )

  # Barra de búsqueda principal
  busqueda = st.text_input(
      "Búsqueda",
      placeholder="🔍 Escribe un nombre, área (ej. AGA), DNI, cargo...",
      label_visibility="collapsed",
  )

  # Selector muy pequeño y compacto para elegir entre 1 resultado o múltiples
  modo_vista = "Solo 1 resultado"
  if busqueda and busqueda.strip() != "":
    st.markdown("<div style='height: 5px;'></div>", unsafe_allow_html=True)
    modo_vista = st.radio(
        "Modo de vista",
        ["Solo 1 resultado", "Ver múltiples resultados"],
        horizontal=True,
        label_visibility="collapsed",
    )

  # Lógica de búsqueda inteligente y tolerante a errores (Fuzzy Search)
  df_filtered = pd.DataFrame(columns=df.columns)
  if busqueda and busqueda.strip() != "":
    query = busqueda.strip().lower()


    def safe_join(row):
      return " ".join([str(val) for val in row.values if pd.notna(val)])


    # 1. Coincidencia exacta por subcadena
    texto_completo = df.apply(safe_join, axis=1).str.lower()
    exact_matches = df[texto_completo.str.contains(query, na=False)]

    if not exact_matches.empty:
      if modo_vista == "Solo 1 resultado":
        df_filtered = exact_matches.head(1)
      else:
        df_filtered = exact_matches
    else:
      # 2. Búsqueda difusa (similitud) si no hay coincidencia exacta
      best_rows = []
      for _, row in df.iterrows():
        row_text = safe_join(row).lower()
        row_words = row_text.split()
        max_score = 0.0
        for word in row_words:
          score = SequenceMatcher(None, query, word).ratio()
          if score > max_score:
            max_score = score
        if max_score >= 0.65:
          best_rows.append((max_score, row))

      if best_rows:
        best_rows.sort(key=lambda x: x[0], reverse=True)
        matched_df = pd.DataFrame([r[1] for r in best_rows])
        if modo_vista == "Solo 1 resultado":
          df_filtered = matched_df.head(1)
        else:
          df_filtered = matched_df

  st.markdown("<br>", unsafe_allow_html=True)

  # Renderizar resultados o animación
  if busqueda and busqueda.strip() != "":
    if len(df_filtered) > 0:
      st.markdown(
          f"<p style='text-align: center; color: #64748b !important; font-size:"
          f" 0.85rem;'><b>{len(df_filtered)}</b> resultado(s)"
          " encontrado(s)</p>",
          unsafe_allow_html=True,
      )
      st.markdown("---")

      for _, row in df_filtered.iterrows():
        detalles_html = ""
        for col in df.columns:
          val_limpio = limpiar_valor(row[col])
          if val_limpio != "N/A" and "NOMBRE" not in col.upper():
            detalles_html += f"<div class='card-info'><b>{col}:</b> <span>{val_limpio}</span></div>"

        nombre = limpiar_valor(
            next(
                (
                    row[c]
                    for c in df.columns
                    if "NOMBRE" in c.upper() and pd.notna(row[c])
                ),
                "Sin Nombre",
            )
        )

        st.markdown(
            f"""
                <div class="resultado-card">
                    <div class="card-title">👤 {nombre}</div>
                    <div class="card-grid">
                        {detalles_html}
                    </div>
                </div>
                """,
            unsafe_allow_html=True,
        )
    else:
      st.markdown(
          "<p style='text-align: center; color: #ef4444 !important; font-size:"
          " 0.9rem;'>❌ No se encontraron resultados para tu búsqueda.</p>",
          unsafe_allow_html=True,
      )
  else:
    # Ilustración animada del libro abierto
    st.markdown(
        """
        <div class="empty-state">
            <div class="realistic-book">
                <svg width="110" height="70" viewBox="0 0 120 75" fill="none" xmlns="http://www.w3.org/2000/svg">
                    <path d="M12 63C35 66 57 63 60 63C63 63 85 66 108 63V12C85 15 63 12 60 12C57 12 35 15 12 12V63Z" fill="#1e293b" stroke="#38bdf8" stroke-width="2.5" stroke-linejoin="round"/>
                    <path d="M60 12V63" stroke="#38bdf8" stroke-width="2.5"/>
                    <path d="M15 15C35 17 55 15 58 15V60C55 60 35 62 15 60V15Z" fill="#f1f5f9"/>
                    <line x1="20" y1="24" x2="48" y2="24" stroke="#94a3b8" stroke-width="2" stroke-linecap="round"/>
                    <line x1="20" y1="33" x2="44" y2="33" stroke="#94a3b8" stroke-width="2" stroke-linecap="round"/>
                    <line x1="20" y1="42" x2="38" y2="42" stroke="#94a3b8" stroke-width="2" stroke-linecap="round"/>
                    <path d="M105 15C85 17 65 15 62 15V60C65 60 85 62 105 60V15Z" fill="#f1f5f9"/>
                    <line x1="72" y1="24" x2="100" y2="24" stroke="#94a3b8" stroke-width="2" stroke-linecap="round"/>
                    <line x1="72" y1="33" x2="96" y2="33" stroke="#94a3b8" stroke-width="2" stroke-linecap="round"/>
                    <line x1="72" y1="42" x2="90" y2="42" stroke="#94a3b8" stroke-width="2" stroke-linecap="round"/>
                    <g class="animated-page">
                        <path d="M60 15C75 15 95 17 105 15V60C95 62 75 60 60 60V15Z" fill="#cbd5e1" opacity="0.9"/>
                    </g>
                </svg>
            </div>
            <p style="color: #64748b !important; font-size: 0.85rem; margin-top: 15px;">📖 Escribe un nombre, área, DNI o cargo para consultar la agenda...</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

except Exception as e:
  st.error(f"Error al cargar el archivo de Excel: {e}")
