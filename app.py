import base64
import pandas as pd
import streamlit as st

# Configuración de la página
st.set_page_config(
    page_title="Directorio UGEL Otuzco 2026", page_icon="📚", layout="centered"
)

# --- ESTILOS CSS MODERNOS ---
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

    /* Tarjetas de resultados compactas y completas */
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

  # 1. LOGO EN CÍRCULO SUPERIOR
  try:
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

  # 4. BÚSQUEDA SENSIBLE / FLEXIBLE
  if busqueda:
    palabras = busqueda.strip().lower().split()
    if palabras:

      def safe_join(row):
        return " ".join([str(val) for val in row.values if pd.notna(val)])

      texto_completo = df.apply(safe_join, axis=1).str.lower()

      condicion = texto_completo.str.contains(palabras[0], na=False)
      for palabra in palabras[1:]:
        condicion = condicion | texto_completo.str.contains(palabra, na=False)

      df_filtered = df[condicion]
    else:
      df_filtered = df
  else:
    df_filtered = df

  st.markdown("<br>", unsafe_allow_html=True)
  st.markdown(
      f"<p style='color: #64748b; font-size: 0.9rem;'><b>{len(df_filtered)}</b>"
      " resultados encontrados</p>",
      unsafe_allow_html=True,
  )
  st.markdown("---")

  # 3. RENDERIZAR CADA PERSONA EN UNA SOLA TARJETA CON TODA SU INFORMACIÓN
  for _, row in df_filtered.iterrows():
    # Extraer todos los campos disponibles en la fila del DataFrame
    detalles_html = ""
    for col in df.columns:
      val_limpio = limpiar_valor(row[col])
      # Omitir columnas vacías o de índice numérico si se prefiere, o mostrarlas todas
      if val_limpio != "N/A" and "NOMBRE" not in col.upper():
        detalles_html += (
            f"<div class='card-info'><b>{col}:</b> <span>{val_limpio}</span></div>"
        )

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

except Exception as e:
  st.error(f"Error al cargar el archivo de Excel: {e}")
