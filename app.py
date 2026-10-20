import base64
import pandas as pd
import streamlit as st

# Configuración de la página optimizada para celulares y pantallas grandes
st.set_page_config(
    page_title="Directorio UGEL Otuzco 2026", page_icon="📚", layout="centered"
)

# --- ESTILOS CSS RESPONSIVOS PARA MÓVIL ---
st.markdown(
    """
    <style>
    /* Fondo general oscuro elegante */
    .stApp {
        background-color: #0b0f19;
    }
    
    /* Ocultar el texto auxiliar de las cajas de texto */
    .stTextInput small {
        display: none !important;
    }

    /* Contenedor responsivo y centrado para el logo */
    .logo-container {
        display: flex;
        justify-content: center;
        align-items: center;
        margin-top: 10px;
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

    /* Tarjetas de resultados adaptadas para una lectura cómoda en celular */
    .resultado-card {
        background-color: #131c2e;
        border: 1px solid #1e293b;
        padding: 16px;
        border-radius: 12px;
        margin-bottom: 12px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.2);
    }
    
    .card-title {
        color: #f8fafc;
        font-size: 1.1rem;
        font-weight: 600;
        margin-bottom: 6px;
    }

    .card-info {
        color: #94a3b8;
        font-size: 0.9rem;
        margin-bottom: 4px;
        line-height: 1.4;
    }
    
    .badge-area {
        display: inline-block;
        background-color: #1e293b;
        color: #38bdf8;
        padding: 2px 8px;
        border-radius: 6px;
        font-size: 0.75rem;
        font-weight: 500;
        margin-top: 6px;
    }
    </style>
""",
    unsafe_allow_html=True,
)


# Función para limpiar números flotantes (eliminar el .0 al final)
def limpiar_valor(val):
  if pd.isna(val):
    return "N/A"
  s = str(val).strip()
  if s.endswith(".0"):
    s = s[:-2]
  return s


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

  # --- ENCABEZADO CON LOGO CIRCULAR AJUSTADO PARA MÓVIL ---
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

  # Barra de búsqueda adaptada para celulares
  busqueda = st.text_input(
      "Búsqueda",
      placeholder="🔍 Buscar por nombre, DNI, cargo...",
      label_visibility="collapsed",
  )

  # Filtro de área adaptado
  area_col = next(
      (c for c in df.columns if "AREA" in c.upper() or "ÁREA" in c.upper()), None
  )
  if area_col:
    st.markdown("<div style='margin-top: 10px;'></div>", unsafe_allow_html=True)
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
      f"<p style='color: #64748b; font-size: 0.9rem;'><b>{len(df_filtered)}</b>"
      " resultados encontrados</p>",
      unsafe_allow_html=True,
  )
  st.markdown("---")

  # --- RENDERIZAR RESULTADOS LIMPIANDO EL .0 DE LOS NÚMEROS ---
  for _, row in df_filtered.iterrows():
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
    cargo = limpiar_valor(
        next(
            (
                row[c]
                for c in df.columns
                if "CARGO" in c.upper() and pd.notna(row[c])
            ),
            "Sin Cargo",
        )
    )
    dni = limpiar_valor(
        next(
            (row[c] for c in df.columns if "DNI" in c.upper() and pd.notna(row[c])),
            "N/A",
        )
    )
    celular = limpiar_valor(
        next(
            (
                row[c]
                for c in df.columns
                if ("CEL" in c.upper() or "TEL" in c.upper())
                and pd.notna(row[c])
            ),
            "N/A",
        )
    )
    correo = limpiar_valor(
        next(
            (
                row[c]
                for c in df.columns
                if ("CORREO" in c.upper() or "EMAIL" in c.upper())
                and pd.notna(row[c])
            ),
            "N/A",
        )
    )
    area = limpiar_valor(
        row[area_col] if area_col and pd.notna(row[area_col]) else "General"
    )

    st.markdown(
        f"""
        <div class="resultado-card">
            <div class="card-title">👤 {nombre}</div>
            <div class="card-info"><b>Cargo:</b> {cargo}</div>
            <div class="card-info"><b>DNI:</b> {dni} &nbsp;|&nbsp; <b>Celular:</b> {celular}</div>
            <div class="card-info"><b>Correo:</b> {correo}</div>
            <div><span class="badge-area">📁 {area}</span></div>
        </div>
        """,
        unsafe_allow_html=True,
    )

except Exception as e:
  st.error(f"Error al cargar el archivo de Excel: {e}")
