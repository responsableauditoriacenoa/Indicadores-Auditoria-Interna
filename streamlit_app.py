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

# Estilización CSS Adicional (Premium CEO-Level UX - Light Theme)
st.markdown("""
    <style>
    /* Ocultar elementos por defecto de Streamlit */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}

    /* Contenedor Principal */
    .block-container {
        padding-top: 2rem !important;
        padding-bottom: 2rem !important;
        max-width: 1600px !important;
    }

    /* Títulos Grandes Profesionales */
    h1 {
        font-size: 3rem !important;
        font-weight: 800 !important;
        letter-spacing: -0.5px;
        color: #0f172a !important;
        margin-bottom: 0.5rem !important;
    }
    h2 {
        font-size: 2rem !important;
        font-weight: 700 !important;
        color: #1e293b !important;
        margin-top: 1.5rem !important;
        margin-bottom: 1rem !important;
    }
    h3 {
        font-size: 1.5rem !important;
        font-weight: 600 !important;
        color: #334155 !important;
    }
    .stMarkdown p {
        font-size: 1.2rem !important;
        color: #475569 !important;
        line-height: 1.6;
    }

    /* Sidebar Profesioanl */
    [data-testid="stSidebar"] {
        border-right: 1px solid #e2e8f0;
    }
    .stRadio label, .stRadio div[role="radiogroup"] > label {
        font-size: 1.25rem !important;
        font-weight: 500 !important;
        padding: 0.5rem 0;
        cursor: pointer;
    }

    /* Sobreescribiendo KPIs st.metric nativos - Look Corporativo Claro */
    [data-testid="stMetric"] {
        background-color: #ffffff;
        border: 1px solid #e2e8f0;
        padding: 24px 32px;
        border-radius: 12px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05), 0 2px 4px -1px rgba(0, 0, 0, 0.03);
        margin-bottom: 16px;
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }
    [data-testid="stMetric"]:hover {
        transform: translateY(-2px);
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.08), 0 4px 6px -2px rgba(0, 0, 0, 0.04);
        border-color: #cbd5e1;
    }
    
    [data-testid="stMetricLabel"] {
        font-size: 1.1rem !important;
        font-weight: 600 !important;
        text-transform: uppercase;
        letter-spacing: 1px;
        color: #64748b !important;
    }
    
    [data-testid="stMetricValue"] {
        font-size: 2.3rem !important;
        font-weight: 800 !important;
        line-height: 1.1 !important;
        padding: 8px 0 !important;
        color: #0f172a !important;
    }
    
    [data-testid="stMetricDelta"] {
        font-size: 1.1rem !important;
        font-weight: 600 !important;
    }

    /* DataFrame Corporativo */
    [data-testid="stDataFrame"] {
        border: 1px solid #e2e8f0;
        border-radius: 8px;
        overflow: hidden;
    }
    /* Estilizar celdas de las tablas - Tamaño de letra más grande para CEOs */
    .stDataFrame table {
        font-size: 1.1rem !important;
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
            
        # Parseo de Fechas
        df['Fecha Inicio'] = pd.to_datetime(df['Fecha Inicio'], format='%d/%m/%Y', errors='coerce')
        df['Fecha Fin'] = pd.to_datetime(df['Fecha Fin'], format='%d/%m/%Y', errors='coerce')
        df['FechaVencimiento'] = pd.to_datetime(df['FechaVencimiento'], format='%d/%m/%Y', errors='coerce')

        # Limpieza General
        df['Estado'] = df['Estado'].fillna('Desconocido').astype(str).str.strip().str.capitalize()
        df['Conclusión'] = df['Conclusión'].fillna('Sin Conclusión').astype(str).str.strip().str.capitalize()
        df['Horas Planificadas'] = pd.to_numeric(df['Horas Planificadas'], errors='coerce').fillna(0)
        df['Cantidad Horas'] = pd.to_numeric(df['Cantidad Horas'], errors='coerce').fillna(0)
        
        df['Auditor'] = df['Auditor'].fillna('No Asignado')
        df['Observación'] = df['Observación'].fillna('')
        df['Detalles'] = df['Detalles'].fillna('')

        # Cálculos de Tiempo
        # Lead Time en días
        df['Lead_Time_Dias'] = (df['Fecha Fin'] - df['Fecha Inicio']).dt.days
        # Puntualidad
        def calc_puntualidad(row):
            if pd.isna(row['Fecha Fin']) or pd.isna(row['FechaVencimiento']): return "Sin Datos"
            if row['Fecha Fin'] <= row['FechaVencimiento']: return "A Tiempo"
            else: return "Atrasado"
        df['Entrega'] = df.apply(calc_puntualidad, axis=1)

        return df
    except Exception as e:
        st.error(f"Error al conectar con Google Sheets: {e}")
        return pd.DataFrame()

# ================================
# ESTRUCTURA PRINCIPAL
# ================================

st.title("📊 Grupo Cenoa - Auditoria Interna")
st.markdown("Plataforma interactiva para medición de KPIs Gerenciales y Desempeño Analítico.")

# Spinner mientras carga
with st.spinner("Sincronizando con Google Sheets en vivo..."):
    df = load_data()

if not df.empty:
    
    # ====== NAVEGACION LATERAL (SIDEBAR) ======
    with st.sidebar:
        st.markdown("## 🧭 Navegación")
        seccion = st.radio(
            "Seleccione el Panel de Control:",
            ["🌎 Visión General", "🕵️‍♂️ Desempeño de Auditores"]
        )
        st.markdown("---")
        st.write("Grupo Cenoa © 2026")

    # -------------------------------------------------------------
    # VISTA 1: VISION GENERAL (GERENCIAL Y ACTUAL)
    # -------------------------------------------------------------
    if seccion == "🌎 Visión General":
        st.header("Resumen del Sector")
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
                title="Distribución de Estados Actual",
                hole=0.45,
                color_discrete_sequence=px.colors.qualitative.Pastel
            )
            fig_pie.update_traces(textposition='inside', textinfo='percent+label', textfont_size=14)
            fig_pie.update_layout(title_font_size=22, legend_font_size=14, font=dict(size=14))
            st.plotly_chart(fig_pie, use_container_width=True)
            
        with c2:
            conclusion_counts = df['Conclusión'].value_counts().reset_index()
            conclusion_counts.columns = ['Conclusión', 'Cantidad']
            fig_bar = px.bar(
                conclusion_counts,
                x='Conclusión',
                y='Cantidad',
                title="Clasificación Analítica de Conclusiones",
                color='Conclusión',
                color_discrete_sequence=px.colors.qualitative.Set2
            )
            fig_bar.update_layout(title_font_size=22, xaxis_title="", yaxis_title="Cantidad de Auditorías", font=dict(size=14))
            st.plotly_chart(fig_bar, use_container_width=True)

        # Vista de Datos Dinámica
        st.markdown("---")
        st.subheader("Registro de Datos Generales")
        
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


    # -------------------------------------------------------------
    # VISTA 2: KPIs DE AUDITORES (DESEMPEÑO)
    # -------------------------------------------------------------
    elif seccion == "🕵️‍♂️ Desempeño de Auditores":
        st.header("Métricas y Análisis de Rendimiento por Auditor")
        
        lista_auditores = [a for a in df['Auditor'].unique() if a and str(a).lower() != 'no asignado']
        auditor_seleccionado = st.selectbox("🎯 Filtrar Análisis (Selecciona 'Visión Global' para comparar al equipo):", ["Visión Global del Equipo"] + sorted(lista_auditores))
        
        st.markdown("---")
        
        if auditor_seleccionado == "Visión Global del Equipo":
            # --- VISTA: MÚLTIPLES AUDITORES (LEADERBOARD) ---
            st.subheader("🏆 Leaderboard Global: Efectividad y Carga")
            
            # Grouping stats
            aud_stats = df.groupby('Auditor').agg(
                Totales=('ID Actividad', 'count'),
                Culminadas=('Estado', lambda x: (x == 'Culminado').sum()),
                Hs_Planificadas=('Horas Planificadas', 'sum'),
                Hs_Reales=('Cantidad Horas', 'sum'),
                Puntaje_Promedio=('Puntaje_Num', 'mean'),
            ).reset_index()
            
            # Tasa de Efectividad y Desviación de Horas
            aud_stats['Tasa Efectividad %'] = round((aud_stats['Culminadas'] / aud_stats['Totales']) * 100, 1)
            aud_stats['Desviación Hs'] = aud_stats['Hs_Planificadas'] - aud_stats['Hs_Reales']
            
            # Filtro para ignorar 'No asignado'
            aud_stats = aud_stats[aud_stats['Auditor'] != 'No asignado']

            ac1, ac2 = st.columns(2)
            with ac1:
                # Ranking de Efectividad
                fig_ef = px.bar(
                    aud_stats.sort_values(by='Tasa Efectividad %', ascending=False),
                    x='Auditor', y='Tasa Efectividad %',
                    title='🎖️ Tasa de Efectividad de Cierre (Auditorías Terminadas)',
                    text='Tasa Efectividad %',
                    color='Tasa Efectividad %',
                    color_continuous_scale='teal'
                )
                fig_ef.update_traces(textfont_size=14, textposition="auto")
                fig_ef.update_layout(title_font_size=20, xaxis_title="", font=dict(size=14))
                st.plotly_chart(fig_ef, use_container_width=True)

            with ac2:
                 # Ranking de Eficiencia de Horas (Diferencia)
                fig_hs = px.bar(
                    aud_stats.sort_values(by='Desviación Hs', ascending=False),
                    x='Auditor', y='Desviación Hs',
                    title='⏳ Eficiencia de Horas (Diferencia Plan vs Real)',
                    text='Desviación Hs',
                    color='Desviación Hs',
                    color_continuous_scale='RdYlGn' # Verde es positivo (ahorraron hs), Rojo es consumieron de mas
                )
                fig_hs.update_traces(textfont_size=14, textposition="auto")
                fig_hs.update_layout(title_font_size=20, xaxis_title="", font=dict(size=14))
                st.plotly_chart(fig_hs, use_container_width=True)
                
            st.dataframe(aud_stats, use_container_width=True)

        else:
            # --- VISTA: BOLETA INDIVIDUAL (ONE-PAGER) ---
            df_aud = df[df['Auditor'] == auditor_seleccionado]
            
            st.subheader(f"📊 Boleta Analítica: {auditor_seleccionado}")
            
            # KPIs Avanzados del Plan
            a_totales = len(df_aud)
            a_culminadas = len(df_aud[df_aud['Estado'] == 'Culminado'])
            a_enproceso = len(df_aud[df_aud['Estado'] == 'En proceso'])
            a_efectividad = round((a_culminadas / a_totales)*100, 1) if a_totales > 0 else 0
            
            a_hs_plan = df_aud['Horas Planificadas'].sum()
            a_hs_real = df_aud['Cantidad Horas'].sum()
            a_hs_desviacion = a_hs_plan - a_hs_real # Positivo = ahorró tiempo
            
            a_pts_promedio = df_aud['Puntaje_Num'].mean() * 100
            
            # Lead Time (Promedio dias efectivos)
            a_lead_time = df_aud['Lead_Time_Dias'].mean()
            
            # Puntualidad
            a_entregas_ok = len(df_aud[df_aud['Entrega'] == 'A Tiempo'])
            a_entregas_atrasadas = len(df_aud[df_aud['Entrega'] == 'Atrasado'])
            a_puntualidad_pct = round((a_entregas_ok / (a_entregas_ok + a_entregas_atrasadas)) * 100, 1) if (a_entregas_ok + a_entregas_atrasadas) > 0 else 0
            
            # Detallismo (observaciones llenas)
            a_con_detalles = len(df_aud[ (df_aud['Observación'] != '') | (df_aud['Detalles'] != '') ])
            a_ratio_observaciones = round((a_con_detalles / a_totales) * 100, 1) if a_totales > 0 else 0
            
            # Versatilidad
            a_empresas = df_aud['Empresa'].nunique()
            a_sectores = df_aud['Sector'].nunique()

            # Row 1: Productividad & Tiempo
            st.markdown("##### ⏱️ Módulo de Productividad y Tiempo")
            rc1, rc2, rc3, rc4 = st.columns(4)
            rc1.metric("Tareas Completadas vs Asignadas", f"{a_culminadas} / {a_totales}", f"Eficiencia {a_efectividad}%")
            rc2.metric("En Proceso (Carga Actual)", a_enproceso)
            rc3.metric("Eficiencia Horaria (Ahorro/Exceso)", f"{a_hs_desviacion:,.0f} hs", "Sobró tiempo" if a_hs_desviacion >=0 else "Excedido de tiempo", delta_color="normal" if a_hs_desviacion >=0 else "inverse")
            rc4.metric("Velocidad Ejecución (Lead Time)", f"{a_lead_time:.1f} días" if pd.notna(a_lead_time) else "N/A", "Promedio inicio a fin")
            
            # Row 2: Calidad e Índices
            st.markdown("##### 🎯 Módulo de Calidad y Especialización")
            rc5, rc6, rc7, rc8 = st.columns(4)
            rc5.metric("Severidad Promedio (Puntaje)", f"{a_pts_promedio:.1f}%" if pd.notna(a_pts_promedio) else "N/A", "")
            rc6.metric("Puntualidad en Fechas Límite", f"{a_puntualidad_pct}%", f"{a_entregas_atrasadas} Atrasos reportados", delta_color="normal" if a_entregas_atrasadas == 0 else "inverse")
            rc7.metric("Índice de Reporte (Observaciones)", f"{a_ratio_observaciones}%", f"{a_con_detalles} reg. comentados")
            rc8.metric("Versatilidad Operativa", f"{a_sectores} Sectores", f"Abarca {a_empresas} empresas")
            
            # Gráficos Individuales
            st.markdown("---")
            gc1, gc2 = st.columns(2)
            with gc1:
                # Gauge o Pie Chart de Puntualidad
                if a_totales > 0:
                    fig_ind_pie = px.pie(
                        df_aud[df_aud['Entrega'] != 'Sin Datos'], 
                        names='Entrega',
                        title='Cumplimiento de Plazos (Vencimientos)',
                        hole=0.6,
                        color='Entrega',
                        color_discrete_map={'A Tiempo': '#10b981', 'Atrasado': '#ef4444'}
                    )
                    fig_ind_pie.update_traces(textfont_size=14, textinfo='percent+label')
                    fig_ind_pie.update_layout(title_font_size=20, font=dict(size=14))
                    st.plotly_chart(fig_ind_pie, use_container_width=True)
            with gc2:
                # Distribución de Conclusiones de este Auditor
                conc_aud = df_aud['Conclusión'].value_counts().reset_index()
                conc_aud.columns = ['Conclusión', 'Cantidad']
                if not conc_aud.empty:
                    fig_ind_bar = px.bar(
                        conc_aud, 
                        x='Cantidad', 
                        y='Conclusión',
                        orientation='h',
                        title='Criterio de Evaluación: Conclusiones Dictaminadas',
                        color='Conclusión',
                        color_discrete_sequence=px.colors.qualitative.Pastel2
                    )
                    fig_ind_bar.update_layout(title_font_size=20, yaxis_title="", xaxis_title="N° Resoluciones", font=dict(size=14))
                    st.plotly_chart(fig_ind_bar, use_container_width=True)

else:
    st.warning("No se pudieron cargar los datos o el CSV está vacío.")
