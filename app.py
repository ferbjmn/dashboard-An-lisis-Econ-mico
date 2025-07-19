import streamlit as st
import pandas as pd
import plotly.express as px
import requests
import time
from datetime import datetime
import os
from dotenv import load_dotenv

# Configuración inicial
load_dotenv()
st.set_page_config(layout="wide", page_title="📊 Análisis Económico FMI", page_icon="🌍")

# ======================================
# 1. Configuración de Datos y API
# ======================================

# Diccionario completo de países
PAISES = {
    "USA": {"nombre": "Estados Unidos", "iso2": "US"},
    "MEX": {"nombre": "México", "iso2": "MX"},
    "BRA": {"nombre": "Brasil", "iso2": "BR"},
    "ESP": {"nombre": "España", "iso2": "ES"},
    "ARG": {"nombre": "Argentina", "iso2": "AR"},
    "COL": {"nombre": "Colombia", "iso2": "CO"},
    "CHL": {"nombre": "Chile", "iso2": "CL"},
    "PER": {"nombre": "Perú", "iso2": "PE"},
    "DEU": {"nombre": "Alemania", "iso2": "DE"},
    "FRA": {"nombre": "Francia", "iso2": "FR"},
    "GBR": {"nombre": "Reino Unido", "iso2": "GB"},
    "CHN": {"nombre": "China", "iso2": "CN"}
}

# Todos los indicadores solicitados
INDICADORES = {
    "PIB": {"codigo": "NGDP_R", "unidad": "USD", "tipo": "bar"},
    "PIB_per_capita": {"codigo": "NGDPDPC", "unidad": "USD", "tipo": "bar"},
    "Inflación": {"codigo": "PCPI", "unidad": "%", "tipo": "line"},
    "Exportaciones": {"codigo": "TXG_FOB_USD", "unidad": "USD", "tipo": "bar"},
    "Importaciones": {"codigo": "TMG_CIF_USD", "unidad": "USD", "tipo": "bar"},
    "Cuenta_Corriente": {"codigo": "BCA", "unidad": "% PIB", "tipo": "line"},
    "Reservas": {"codigo": "RAXG", "unidad": "USD", "tipo": "bar"},
    "Tasa_Interés": {"codigo": "FPOLM_PA", "unidad": "%", "tipo": "line"},
    "Deuda_Pública": {"codigo": "GGXWDG", "unidad": "% PIB", "tipo": "bar"},
    "Déficit_Fiscal": {"codigo": "GGXONLB", "unidad": "% PIB", "tipo": "bar"},
    "Gasto_Público": {"codigo": "GGX", "unidad": "% PIB", "tipo": "bar"},
    "Desempleo": {"codigo": "LUR", "unidad": "%", "tipo": "bar"},
    "IED": {"codigo": "FDI", "unidad": "USD", "tipo": "bar"}
}

# ======================================
# 2. Funciones principales
# ======================================

@st.cache_data(ttl=3600)
def obtener_datos_fmi(pais_iso2, indicador_codigo, start_year=2010, end_year=2023):
    try:
        url = f"https://www.imf.org/external/datamapper/api/v1/{indicador_codigo}/{pais_iso2}?periods={start_year}-{end_year}"
        response = requests.get(url)
        response.raise_for_status()
        
        data = response.json()
        series = data["values"][indicador_codigo][pais_iso2]
        
        df = pd.DataFrame.from_dict(series, orient="index", columns=["Valor"])
        df.index = df.index.astype(int)
        df = df.reset_index().rename(columns={"index": "Año"})
        df["Valor"] = pd.to_numeric(df["Valor"], errors="coerce")
        
        time.sleep(0.5)
        return df.dropna()
    
    except Exception as e:
        st.error(f"Error al obtener datos: {str(e)}")
        return pd.DataFrame()

def crear_grafico_comparativo(df, titulo, tipo, unidad, show_table=True):
    if df.empty:
        st.warning(f"No hay datos disponibles para {titulo}")
        return
    
    if tipo == "line":
        fig = px.line(df, x="Año", y="Valor", color="País", 
                     title=f"{titulo} ({unidad})", markers=True)
    else:
        fig = px.bar(df, x="Año", y="Valor", color="País", 
                    title=f"{titulo} ({unidad})", barmode="group")
    
    fig.update_layout(
        hovermode="x unified",
        xaxis_title="Año",
        yaxis_title=unidad,
        legend_title="País"
    )
    st.plotly_chart(fig, use_container_width=True)
    
    if show_table:
        with st.expander("Ver datos tabulares"):
            st.dataframe(df.pivot(index="Año", columns="País", values="Valor"))

# ======================================
# 3. Interfaz de Usuario
# ======================================

st.title("🌍 Análisis Económico Completo (Datos FMI)")

# Sidebar
with st.sidebar:
    st.header("⚙️ Configuración")
    
    paises_seleccionados = st.multiselect(
        "Seleccionar países:",
        options=list(PAISES.keys()),
        format_func=lambda x: PAISES[x]["nombre"],
        default=["MEX", "USA", "BRA"]
    )
    
    año_inicio, año_fin = st.slider(
        "Rango de años:",
        min_value=1990,
        max_value=datetime.now().year,
        value=(2010, 2023)
    )

# ======================================
# 4. Visualización de Todos los Gráficos
# ======================================

# Gráfico 1: PIB
st.header("📈 1. Producto Interno Bruto (PIB)")
datos_pib = []
for pais in paises_seleccionados:
    df = obtener_datos_fmi(PAISES[pais]["iso2"], "NGDP_R", año_inicio, año_fin)
    if not df.empty:
        df["País"] = PAISES[pais]["nombre"]
        datos_pib.append(df)

if datos_pib:
    crear_grafico_comparativo(pd.concat(datos_pib), "Evolución del PIB", "bar", "USD")

# Gráfico 2: PIB per cápita
st.header("📊 2. PIB per cápita")
datos_pib_per_capita = []
for pais in paises_seleccionados:
    df = obtener_datos_fmi(PAISES[pais]["iso2"], "NGDPDPC", año_inicio, año_fin)
    if not df.empty:
        df["País"] = PAISES[pais]["nombre"]
        datos_pib_per_capita.append(df)

if datos_pib_per_capita:
    crear_grafico_comparativo(pd.concat(datos_pib_per_capita), "PIB per cápita", "bar", "USD")

# Gráfico 3: Inflación
st.header("📉 3. Inflación Anual")
datos_inflacion = []
for pais in paises_seleccionados:
    df = obtener_datos_fmi(PAISES[pais]["iso2"], "PCPI", año_inicio, año_fin)
    if not df.empty:
        df["País"] = PAISES[pais]["nombre"]
        datos_inflacion.append(df)

if datos_inflacion:
    crear_grafico_comparativo(pd.concat(datos_inflacion), "Tasa de Inflación", "line", "%")

# Gráfico 4: Balanza Comercial (Último año disponible)
st.header("🔄 4. Balanza Comercial (Último Año)")
if paises_seleccionados:
    año_actual = año_fin
    datos_balanza = []
    
    for pais in paises_seleccionados:
        df_export = obtener_datos_fmi(PAISES[pais]["iso2"], "TXG_FOB_USD", año_actual, año_actual)
        df_import = obtener_datos_fmi(PAISES[pais]["iso2"], "TMG_CIF_USD", año_actual, año_actual)
        
        if not df_export.empty and not df_import.empty:
            datos_balanza.append({
                "País": PAISES[pais]["nombre"],
                "Exportaciones": df_export["Valor"].values[0],
                "Importaciones": df_import["Valor"].values[0]
            })
    
    if datos_balanza:
        df_balanza = pd.DataFrame(datos_balanza)
        fig = px.bar(df_balanza.melt(id_vars="País", var_name="Tipo", value_name="Valor"), 
                     x="País", y="Valor", color="Tipo", barmode="group",
                     title=f"Balanza Comercial ({año_actual})")
        st.plotly_chart(fig, use_container_width=True)

# Gráfico 5: Cuenta Corriente
st.header("💳 5. Cuenta Corriente (% PIB)")
datos_cuenta = []
for pais in paises_seleccionados:
    df = obtener_datos_fmi(PAISES[pais]["iso2"], "BCA", año_inicio, año_fin)
    if not df.empty:
        df["País"] = PAISES[pais]["nombre"]
        datos_cuenta.append(df)

if datos_cuenta:
    crear_grafico_comparativo(pd.concat(datos_cuenta), "Cuenta Corriente", "line", "% PIB")

# Gráfico 6: Reservas Internacionales
st.header("💰 6. Reservas Internacionales")
datos_reservas = []
for pais in paises_seleccionados:
    df = obtener_datos_fmi(PAISES[pais]["iso2"], "RAXG", año_inicio, año_fin)
    if not df.empty:
        df["País"] = PAISES[pais]["nombre"]
        datos_reservas.append(df)

if datos_reservas:
    crear_grafico_comparativo(pd.concat(datos_reservas), "Reservas Internacionales", "bar", "USD")

# Gráfico 7: Tasas de Interés
st.header("📊 7. Tasas de Interés de Política Monetaria")
datos_tasas = []
for pais in paises_seleccionados:
    df = obtener_datos_fmi(PAISES[pais]["iso2"], "FPOLM_PA", año_inicio, año_fin)
    if not df.empty:
        df["País"] = PAISES[pais]["nombre"]
        datos_tasas.append(df)

if datos_tasas:
    crear_grafico_comparativo(pd.concat(datos_tasas), "Tasas de Interés", "line", "%")

# Gráfico 8: Deuda Pública
st.header("🏛️ 8. Deuda Pública (% PIB)")
datos_deuda = []
for pais in paises_seleccionados:
    df = obtener_datos_fmi(PAISES[pais]["iso2"], "GGXWDG", año_inicio, año_fin)
    if not df.empty:
        df["País"] = PAISES[pais]["nombre"]
        datos_deuda.append(df)

if datos_deuda:
    crear_grafico_comparativo(pd.concat(datos_deuda), "Deuda Pública", "bar", "% PIB")

# Gráfico 9: Déficit Fiscal
st.header("📉 9. Déficit Fiscal (% PIB)")
datos_deficit = []
for pais in paises_seleccionados:
    df = obtener_datos_fmi(PAISES[pais]["iso2"], "GGXONLB", año_inicio, año_fin)
    if not df.empty:
        df["País"] = PAISES[pais]["nombre"]
        datos_deficit.append(df)

if datos_deficit:
    crear_grafico_comparativo(pd.concat(datos_deficit), "Déficit Fiscal", "bar", "% PIB")

# Gráfico 10: Gasto Público
st.header("🏦 10. Gasto Público (% PIB)")
datos_gasto = []
for pais in paises_seleccionados:
    df = obtener_datos_fmi(PAISES[pais]["iso2"], "GGX", año_inicio, año_fin)
    if not df.empty:
        df["País"] = PAISES[pais]["nombre"]
        datos_gasto.append(df)

if datos_gasto:
    crear_grafico_comparativo(pd.concat(datos_gasto), "Gasto Público", "bar", "% PIB")

# Gráfico 11: Desempleo
st.header("🧑‍💼 11. Tasa de Desempleo (%)")
datos_desempleo = []
for pais in paises_seleccionados:
    df = obtener_datos_fmi(PAISES[pais]["iso2"], "LUR", año_inicio, año_fin)
    if not df.empty:
        df["País"] = PAISES[pais]["nombre"]
        datos_desempleo.append(df)

if datos_desempleo:
    crear_grafico_comparativo(pd.concat(datos_desempleo), "Tasa de Desempleo", "bar", "%")

# Gráfico 12: Inversión Extranjera Directa
st.header("🌐 12. Inversión Extranjera Directa (USD)")
datos_ied = []
for pais in paises_seleccionados:
    df = obtener_datos_fmi(PAISES[pais]["iso2"], "FDI", año_inicio, año_fin)
    if not df.empty:
        df["País"] = PAISES[pais]["nombre"]
        datos_ied.append(df)

if datos_ied:
    crear_grafico_comparativo(pd.concat(datos_ied), "Inversión Extranjera Directa", "bar", "USD")

# ======================================
# 5. Pie de Página
# ======================================
st.markdown("---")
st.info("""
**Fuente de datos:** [Fondo Monetario Internacional (FMI)](https://www.imf.org)  
**Última actualización:** {date}  
**Nota:** Los datos pueden tener rezagos de hasta 6 meses dependiendo del indicador
""".format(date=datetime.now().strftime("%Y-%m-%d")))
