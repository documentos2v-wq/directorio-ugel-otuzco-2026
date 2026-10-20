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

  # Carga segura del logo con st.image centrado
  col_izq, col_centro, col_der = st.columns([3, 1, 3])
  with col_centro:
    try:
      st.image("UGEL - LOGO.jpg", width=85)
    except Exception:
      try:
        st.image("logo.jpg", width=85)
      except Exception:
        pass

  st.markdown(
      "<h1 style='text-align: center; color: #f8fafc; font-size: 1.6rem;"
      " margin-top: 5px;'>UGEL - OTUZCO</h1>",
      unsafe_allow_html=True,
  )
  st.markdown(
      "<p style='text-align: center; color: #94a3b8; font-size: 0.95rem;"
      " margin-bottom: 20px;'>Directorio de Servidores - 2026</p>",
      unsafe_allow_html=True,
  )

  # Barra de búsqueda principal
  busqueda = st.text_input(
      "Búsqueda",
      placeholder="🔍 Escribe un nombre (ej. amdres), DNI, cargo...",
      label_visibility="collapsed",
  )

  # Lógica de filtrado (Limitado estrictamente a 1 resultado)
  if busqueda and busqueda.strip() != "":
    palabras = busqueda.strip().lower().split()
    if palabras:

      def safe_join(row):
        return " ".join([str(val) for val in row.values if pd.notna(val)])

      texto_completo = df.apply(safe_join, axis=1).str.lower()

      condicion = texto_completo.str.contains(palabras[0], na=False)
      for palabra in palabras[1:]:
        condicion = condicion | texto_completo.str.contains(palabra, na=False)

      df_filtered = df[condicion].head(1)
    else:
      df_filtered = pd.DataFrame(columns=df.columns)
  else:
    df_filtered = pd.DataFrame(columns=df.columns)

  st.markdown("<br>", unsafe_allow_html=True)

  # Renderizar tarjeta o animación de búsqueda interactiva
  if busqueda and busqueda.strip() != "":
    if len(df_filtered) > 0:
      st.markdown(
          "<p style='text-align: center; color: #64748b; font-size:"
          " 0.9rem;'><b>1</b> resultado encontrado</p>",
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
          "<p style='text-align: center; color: #ef4444; font-size:"
          " 0.95rem;'>❌ No se encontraron resultados para tu búsqueda.</p>",
          unsafe_allow_html=True,
      )
  else:
    # Animación SVG vectorial de la agenda con movimiento
    st.markdown(
        """
        <div class="empty-state">
            <div class="pixel-book-container">
                <svg width="90" height="70" viewBox="0 0 64 48" fill="none" xmlns="http://www.w3.org/2000/svg">
                    <rect x="8" y="8" width="48" height="34" rx="3" fill="#1e293b" stroke="#38bdf8" stroke-width="2"/>
                    <line x1="32" y1="8" x2="32" y2="42" stroke="#38bdf8" stroke-width="2"/>
                    <circle cx="32" cy="12" r="1.5" fill="#f8fafc"/>
                    <circle cx="32" cy="22" r="1.5" fill="#f8fafc"/>
                    <circle cx="32" cy="32" r="1.5" fill="#f8fafc"/>
                    <path class="page-flip" d="M32 10C32 10 44 14 48 25C52 36 32 40 32 40V10Z" fill="#38bdf8" opacity="0.7"/>
                    <line x1="12" y1="16" x2="24" y2="16" stroke="#94a3b8" stroke-width="1.5" stroke-linecap="round"/>
                    <line x1="12" y1="22" x2="22" y2="22" stroke="#94a3b8" stroke-width="1.5" stroke-linecap="round"/>
                    <line x1="12" y1="28" x2="20" y2="28" stroke="#94a3b8" stroke-width="1.5" stroke-linecap="round"/>
                </svg>
            </div>
            <p style="color: #64748b; font-size: 0.9rem; margin-top: 15px;">📖 Escribe un nombre, DNI o cargo para buscar en la agenda...</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

except Exception as e:
  st.error(f"Error al cargar el archivo de Excel: {e}")
