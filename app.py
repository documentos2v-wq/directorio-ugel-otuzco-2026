import pandas as pd
import streamlit as st

# Configuración de la página
st.set_page_config(
    page_title="Directorio UGEL Otuzco 2026", page_icon="📚", layout="centered"
)

# --- ESTILOS CSS CON ANIMACIÓN DE LIBRO ABIERTO REALISTA ---
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

    /* Contenedor y animación fluida del libro abierto frontal */
    .empty-state {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        margin-top: 35px;
        text-align: center;
    }

    .realistic-book {
        position: relative;
        width: 120px;
        height: 75px;
        margin-bottom: 15px;
    }

    /* Animación de la hoja pasando de derecha a izquierda */
    .animated-page {
        transform-origin: 60px 35px;
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

  # Renderizar tarjeta o animación de libro abierto simétrico frontal
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
    # Ilustración vectorial frontal de libro abierto con hojas proporcionadas y animación fluida
    st.markdown(
        """
        <div class="empty-state">
            <div class="realistic-book">
                <svg width="120" height="75" viewBox="0 0 120 75" fill="none" xmlns="http://www.w3.org/2000/svg">
                    <!-- Tapa exterior y lomo inferior -->
                    <path d="M12 63C35 66 57 63 60 63C63 63 85 66 108 63V12C85 15 63 12 60 12C57 12 35 15 12 12V63Z" fill="#1e293b" stroke="#38bdf8" stroke-width="2.5" stroke-linejoin="round"/>
                    <!-- Lomo central -->
                    <path d="M60 12V63" stroke="#38bdf8" stroke-width="2.5"/>
                    <!-- Página fija izquierda -->
                    <path d="M15 15C35 17 55 15 58 15V60C55 60 35 62 15 60V15Z" fill="#f1f5f9"/>
                    <line x1="20" y1="24" x2="48" y2="24" stroke="#94
