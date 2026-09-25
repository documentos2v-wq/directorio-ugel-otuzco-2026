import pandas as pd
import streamlit as st

# Configuración de la página
st.set_page_config(
    page_title="Directorio UGEL Otuzco 2026", page_icon="📚", layout="wide"
)

# Título principal
st.title("📌 Directorio de Servidores - UGEL Otuzco 2026")
st.markdown(
    "Herramienta automatizada para la consulta rápida del directorio institucional."
)


# Cargar los datos desde el archivo Excel
@st.cache_data
def cargar_datos():
  excel_path = "DIRECTORIO UGEL OTUZCO 2026.xlsx"
  # Leemos el archivo sin cabecera fija para buscar la fila de nombres de columna
  df_raw = pd.read_excel(excel_path, header=None)

  header_row_index = None
  for idx, row in df_raw.iterrows():
    # Buscamos la fila donde aparezca 'NOMBRES Y APELLIDOS'
    if any(
        isinstance(v, str) and 'NOMBRES Y APELLIDOS' in v.upper()
        for v in row.values
    ):
      header_row_index = idx
      break

  if header_row_index is not None:
    df = pd.read_excel(excel_path, header=header_row_index)
  else:
    # Por defecto si no se encuentra, usamos la fila 7 (índice 7)
    df = pd.read_excel(excel_path, header=7)

  # Limpiamos nombres de columnas quitando espacios sobrantes
  df.columns = [str(c).strip() for c in df.columns]

  # Buscamos las columnas clave independientemente de mayúsculas/minúsculas
  col_num = next(
      (c for c in df.columns if 'Nº' in c or 'N°' in c or 'NUM' in c.upper()),
      df.columns[0],
  )
  col_nombre = next(
      (c for c in df.columns if 'NOMBRE' in c.upper()), df.columns[1]
  )

  # Eliminamos filas vacías o subtítulos de áreas
  df = df.dropna(subset=[col_nombre], how='any')
  df = df[df[col_num].notna()]

  return df


try:
  df = cargar_datos()

  # Barra lateral de filtros
  st.sidebar.header('🔍 Filtros de Búsqueda')
  busqueda = st.sidebar.text_input('Buscar por Nombre, DNI o Cargo:')

  # Filtro por Área si la columna existe
  area_col = next(
      (c for c in df.columns if 'AREA' in c.upper() or 'ÁREA' in c.upper()), None
  )
  if area_col:
    areas = ['Todas'] + list(df[area_col].dropna().unique())
    area_seleccionada = st.sidebar.selectbox('Filtrar por Área:', areas)
    if area_seleccionada != 'Todas':
      df = df[df[area_col] == area_seleccionada]

  # Aplicar búsqueda de texto
  if busqueda:
    df_filtered = df[
        df.astype(str)
        .apply(lambda x: x.str.contains(busqueda, case=False, na=False))
        .any(axis=1)
    ]
  else:
    df_filtered = df

  # Mostrar métricas rápidas
  st.metric(label='Total de Servidores Mostrados', value=len(df_filtered))

  # Mostrar la tabla interactiva
  st.dataframe(df_filtered, use_container_width=True, hide_index=True)

  # Botón de descarga
  csv = df_filtered.to_csv(index=False).encode('utf-8')
  st.download_button(
      label='📥 Descargar Directorio Filtrado en CSV',
      data=csv,
      file_name='directorio_ugel_otuzco_filtrado.csv',
      mime='text/csv',
  )

except Exception as e:
  st.error(f'Error al cargar el archivo de Excel: {e}')
