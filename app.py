import pandas as pd
import streamlit as st

# Configuración de la página
st.set_page_config(
    page_title="Directorio UGEL Otuzco 2026", page_icon="📚", layout="wide"
)

# --- ESTILOS CSS PERSONALIZADOS (Diseño Institucional + Ocultar aviso de Enter) ---
st.markdown(
    """
    <style>
    /* Fondo general de la página con degradado azul/celeste */
    .stApp {
        background: linear-gradient(135deg, #f0f4f8 0%, #d9e2ec 100%);
    }
    
    /* Títulos principales */
    h1 {
        color: #102a43;
        font-family: 'Helvetica Neue', sans-serif;
        font-weight: 700;
    }
    
    p {
        color: #334e68;
        font-size: 1.1rem;
    }

    /* Ocultar el texto auxiliar "Press Enter to apply" de las cajas de texto */
    .stTextInput small {
        display: none !important;
    }

    /* Tarjetas de métricas */
    div[data-testid="metric-container"] {
        background-color: #ffffff;
        border: 1px solid #bcccdc;
        padding: 15px;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
    }
    
    div[data-testid="metric-container"] label {
        color: #486581 !important;
        font-weight: 600;
    }
    
    div[data-testid="metric-container"] div[data-testid="stMetricValue"] {
        color: #0b69a3 !important;
    }

    /* Estilo de la tabla de datos */
    div[data-testid="stDataFrame"] {
        border-radius: 10px;
        overflow: hidden;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
        border: 1px solid #bcccdc;
    }
    </style>
""",
    unsafe_allow_html=True,
)

# Título principal
st.title("📌 Directorio de Servidores - UGEL Otuzco 2026")
st.markdown(
    "Herramienta automatizada para la consulta rápida del directorio"
    " institucional."
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

  # --- FILTROS VISIBLES EN LA PARTE SUPERIOR ---
  st.markdown("---")
  col1, col2 = st.columns([2, 1])

  with col1:
    # Input reactivo directo
    busqueda = st.text_input(
        "🔍 Buscar por Nombre, DNI, Cargo o Celular:",
        placeholder="Escribe aquí y se filtra al instante...",
    )

  area_col = next(
      (c for c in df.columns if "AREA" in c.upper() or "ÁREA" in c.upper()), None
  )
  if area_col:
    with col2:
      areas = ["Todas"] + list(df[area_col].dropna().unique())
      area_seleccionada = st.selectbox("📂 Filtrar por Área:", areas)
      if area_seleccionada != "Todas":
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

  # Mostrar métricas rápidas
  st.metric(label="Total de Servidores Mostrados", value=len(df_filtered))

  # Mostrar la tabla interactiva (sin botón de descarga)
  st.dataframe(df_filtered, use_container_width=True, hide_index=True)

except Exception as e:
  st.error(f"Error al cargar el archivo de Excel: {e}")
