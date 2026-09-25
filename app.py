import pandas as pd
import streamlit as st

# Configuración de la página
st.set_page_config(
    page_title="Directorio UGEL Otuzco 2026", page_icon="📚", layout="wide"
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
    busqueda = st.text_input(
        "🔍 Buscar por Nombre, DNI, Cargo o Celular:",
        placeholder="Ej. Wilmer Otuzco...",
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

  # --- BÚSQUEDA FLEXIBLE (CUALQUIER PALABRA COINCIDE) ---
  if busqueda:
    palabras = busqueda.strip().split()
    if palabras:
      # Convertimos todo el DataFrame a texto de forma segura llenando vacíos
      texto_completo = (
          df.fillna("").astype(str).agg(" ".join, axis=1).str.lower()
      )

      # Buscamos si CUALQUIERA de las palabras escritas está presente en el registro
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

  # Mostrar la tabla interactiva
  st.dataframe(df_filtered, use_container_width=True, hide_index=True)

  # Botón de descarga
  csv = df_filtered.to_csv(index=False).encode("utf-8")
  st.download_button(
      label="📥 Descargar Directorio Filtrado en CSV",
      data=csv,
      file_name="directorio_ugel_otuzco_filtrado.csv",
      mime="text/csv",
  )

except Exception as e:
  st.error(f"Error al cargar el archivo de Excel: {e}")
