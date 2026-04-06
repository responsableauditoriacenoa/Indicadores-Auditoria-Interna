import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# Configuración de página principal
st.set_page_config(
    page_title="Grupo Cenoa - Auditoria Interna",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estilización CSS Adicional
st.markdown("""
    <style>
    .metric-card {
        background-color: rgba(255, 255, 255, 0.05);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 10px;
        padding: 20px;
        text-align: center;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    .metric-value {
        font-size: 2.5rem;
        font-weight: 700;
        margin: 10px 0;
    }
    .metric-label {
        font-size: 1rem;
        color: #8b949e;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    </style>
""", unsafe_allow_html=True)

# URL del google sheet exportado a CSV
SHEET_URL = "https://docs.google.com/spreadsheets/d/1rONfVQVzyXIEnhlj2RZvZM4LqSXQ6DyccH6dLyNePc4/export?format=csv&gid=0"

@st.cache_data(ttl=60)
def load_data():
    try:
        df = pd.read_csv(SHEET_URL)
        
        # Parseo de Puntaje (De 99,85% string a 0.9985 float)
        def parse_puntaje(val):
            if pd.isna(val):
                return None
            val = str(val).strip()
            if val == '': return None
            # Eliminar % y reemplazar comas
            val = val.replace('%', '').replace(',', '.')
            try:
                return float(val) if float(val) <= 1 else float(val)/100
            except:
                return None
                
        if 'Puntaje' in df.columns:
            df['Puntaje_Num'] = df['Puntaje'].apply(parse_puntaje)
            
        # Limpieza General
        df['Estado'] = df['Estado'].fillna('Desconocido').astype(str).str.strip().str.capitalize()
        df['Conclusión'] = df['Conclusión'].fillna('Sin Conclusión').astype(str).str.strip().str.capitalize()
        df['Horas Planificadas'] = pd.to_numeric(df['Horas Planificadas'], errors='coerce').fillna(0)
        df['Cantidad Horas'] = pd.to_numeric(df['Cantidad Horas'], errors='coerce').fillna(0)

        return df
    except Exception as e:
        st.error(f"Error al conectar con Google Sheets: {e}")
        return pd.DataFrame()

# ================================
# ESTRUCTURA PRINCIPAL
# ================================

st.title("📊 Grupo Cenoa - Auditoria Interna")
st.markdown("Desempeño general basado en la Solapa de Seguimiento de Auditoría.")

# Spinner mientras carga
with st.spinner("Sincronizando con Google Sheets en vivo..."):
    df = load_data()

if not df.empty:
    
    # KPIs Cálculos
    total_audits = len(df)
    completed = len(df[df['Estado'].str.contains('Culminado', case=False, na=False)])
    completion_rate = round((completed / total_audits) * 100) if total_audits > 0 else 0
    
    avg_score = df['Puntaje_Num'].mean() * 100 if 'Puntaje_Num' in df.columns else 0
    
    total_hs_plan = df['Horas Planificadas'].sum()
    total_hs_real = df['Cantidad Horas'].sum()

    # Cards (Métricas)
    col1, col2, col3, col4 = st.columns(4)
    
    col1.metric("Total Auditorías", total_audits)
    col2.metric("Tasa de Finalización", f"{completion_rate}%", f"{completed} Terminadas")
    
    trend_score = "Calificación OK" if avg_score >= 80 else "Calificación Baja"
    col3.metric("Desempeño Promedio", f"{avg_score:.1f}%", trend_score, delta_color="normal" if avg_score >= 80 else "inverse")
    
    hs_dif = total_hs_plan - total_hs_real
    col4.metric("Horas Reales / Plan.", f"{int(total_hs_real)} / {int(total_hs_plan)}", f"{int(hs_dif)} Diferencia", delta_color="normal" if hs_dif >= 0 else "inverse")
    
    st.markdown("---")
    
    # Gráficos de Análisis
    st.subheader("Análisis de Estados y Conclusiones")
    
    c1, c2 = st.columns(2)
    
    with c1:
        estado_counts = df['Estado'].value_counts().reset_index()
        estado_counts.columns = ['Estado', 'Cantidad']
        fig_pie = px.pie(
            estado_counts, 
            values='Cantidad', 
            names='Estado', 
            title="Distribución de Estados",
            hole=0.4,
            color_discrete_sequence=px.colors.qualitative.Pastel
        )
        fig_pie.update_traces(textposition='inside', textinfo='percent+label')
        st.plotly_chart(fig_pie, use_container_width=True)
        
    with c2:
        conclusion_counts = df['Conclusión'].value_counts().reset_index()
        conclusion_counts.columns = ['Conclusión', 'Cantidad']
        fig_bar = px.bar(
            conclusion_counts,
            x='Conclusión',
            y='Cantidad',
            title="Distribución de Conclusiones",
            color='Conclusión',
            color_discrete_sequence=px.colors.qualitative.Set2
        )
        st.plotly_chart(fig_bar, use_container_width=True)

    # Vista de Datos Dinámica
    st.markdown("---")
    st.subheader("Registro de Datos")
    
    # Filtros para la tabla
    fcol1, fcol2, fcol3 = st.columns(3)
    empresas = df['Empresa'].dropna().unique().tolist()
    estados = df['Estado'].dropna().unique().tolist()
    
    sel_empresa = fcol1.multiselect("Filtrar por Empresa", empresas, default=empresas[:5] if len(empresas) > 5 else empresas)
    sel_estado = fcol2.multiselect("Filtrar por Estado", estados, default=estados)
    
    df_filtered = df[(df['Empresa'].isin(sel_empresa)) & (df['Estado'].isin(sel_estado))]
    
    cols_to_show = ['Codigo Auditoría', 'Empresa', 'Sucursal', 'Evento Auditoría', 'Auditor', 'Estado', 'Puntaje_Num']
    existing_cols = [c for c in cols_to_show if c in df_filtered.columns]
    
    st.dataframe(df_filtered[existing_cols], use_container_width=True)

else:
    st.warning("No se pudieron cargar los datos o el CSV está vacío.")
