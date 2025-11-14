# streamlit_app.py
import streamlit as st
from supabase import create_client, Client
import pandas as pd
from datetime import datetime
from io import BytesIO
from PIL import Image

# ==========================
# CONFIGURACIÓN VISUAL
# ==========================
st.set_page_config(
    page_title="Fundación Cuencas Sagradas",
    page_icon="🌿",
    layout="wide"
)

st.markdown(
    """
    <style>
    .stApp { background-color: #e6f5e6; } /* Verde suave */
    .stButton>button { background-color: #2c7a7b; color: white; }
    </style>
    """,
    unsafe_allow_html=True
)

# -------------------------
# Conexión a Supabase
# -------------------------
SUPABASE_URL = "https://drwnpldlyvkgstzarnij.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImRyd25wbGRseXZrZ3N0emFybmlqIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjMwNjU3MjcsImV4cCI6MjA3ODY0MTcyN30.s1P9znRSL0Os6iOFA4eYp_pPlHjVZAHs6yAWbzRcQcc"
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

TABLE_NAME = "proyectos"

def obtener_registros():
    try:
        response = supabase.table("proyectos").select("*").execute()
        if response.data:
            return pd.DataFrame(response.data)
        else:
            return pd.DataFrame()
    except Exception as e:
        st.error(f"Error obteniendo registros: {e}")
        return pd.DataFrame()

# ==========================
# FUNCIONES CRUD
# ==========================
def insertar_registro(data: dict):
    return supabase.table(TABLE_NAME).insert(data).execute()

def obtener_registros():
    response = supabase.table(TABLE_NAME).select("*").execute()
    if response.data:
        return pd.DataFrame(response.data)
    return pd.DataFrame()

def actualizar_registro(id, data: dict):
    return supabase.table(TABLE_NAME).update(data).eq("id", id).execute()

def eliminar_registro(id):
    return supabase.table(TABLE_NAME).delete().eq("id", id).execute()

# ==========================
# FUNCIONES AUXILIARES
# ==========================
def calcular_total_beneficiarios(h, m, glbti):
    return h + m + glbti

def calcular_duracion(fecha_inicio, fecha_fin):
    return (fecha_fin - fecha_inicio).days if fecha_fin >= fecha_inicio else 0

def calcular_porcentaje(parte, total):
    return (parte / total * 100) if total else 0

def df_to_excel(df: pd.DataFrame):
    output = BytesIO()

    # Usar el contexto "with" evita usar writer.save() o writer.close()
    with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
        df.to_excel(writer, index=False, sheet_name="Proyectos")

    output.seek(0)
    return output.read()

# ==========================
# CARGAR LOGO
# ==========================
def mostrar_logo():
    try:
        logo = Image.open("logo_fundacion.png")
        st.image(logo, width=150)
    except:
        st.warning("No se encontró el logo logo_fundacion.png")

# ==========================
# LOGIN SIMPLE
# ==========================
st.sidebar.title("🔐 Login")

USUARIOS = {
    "usuario": "1234",
    "admin": "admin123"
}

usuario_input = st.sidebar.text_input("Usuario")
clave_input = st.sidebar.text_input("Contraseña", type="password")

if st.sidebar.button("Ingresar"):
    if usuario_input in USUARIOS and USUARIOS[usuario_input] == clave_input:
        st.session_state["logueado"] = True
        st.session_state["usuario"] = usuario_input
        st.success(f"Bienvenido, {usuario_input}")
    else:
        st.session_state["logueado"] = False
        st.error("Usuario o contraseña incorrectos")

if not st.session_state.get("logueado"):
    st.warning("⛔ Por favor ingresa tus credenciales para acceder")
    st.stop()



# ==========================
# FORMULARIO DE PROYECTO
# ==========================
def formulario_proyecto(registro=None):
    st.markdown("### 📝 Formulario de Proyecto")
    # --- Información General ---
    with st.expander("Información General"):
        nombre = st.text_input("Nombre del proyecto", value=registro["nombre"] if registro else "")
        pais = st.selectbox(
            "País de intervención",
            ["Ecuador", "Perú", "Biorregional: Ecuador – Perú"],
            index=["Ecuador","Perú","Biorregional: Ecuador – Perú"].index(registro["pais"]) if registro else 0
        )
        provincia = st.text_input("Provincia / Departamento", value=registro["provincia"] if registro else "")
        canton = st.text_input("Cantón / Distrito", value=registro["canton"] if registro else "")
        pueblo = st.text_input("Pueblo / Nacionalidad", value=registro["pueblo"] if registro else "")
        latitud = st.number_input("Latitud (Y)", value=float(registro["latitud"]) if registro else 0.0, format="%.6f")
        longitud = st.number_input("Longitud (X)", value=float(registro["longitud"]) if registro else 0.0, format="%.6f")
    # --- Beneficiarios y Fechas ---
    with st.expander("Beneficiarios y Fechas"):
        benef_hombres = st.number_input("Beneficiarios hombres", min_value=0, step=1, value=int(registro["benef_hombres"]) if registro else 0)
        benef_mujeres = st.number_input("Beneficiarios mujeres", min_value=0, step=1, value=int(registro["benef_mujeres"]) if registro else 0)
        benef_glbti = st.number_input("Beneficiarios GLBTI", min_value=0, step=1, value=int(registro["benef_glbti"]) if registro else 0)
        total_beneficiarios = calcular_total_beneficiarios(benef_hombres, benef_mujeres, benef_glbti)

        fecha_inicio = st.date_input("Fecha de inicio", value=pd.to_datetime(registro["fecha_inicio"]) if registro else datetime.today())
        fecha_fin = st.date_input("Fecha de finalización", value=pd.to_datetime(registro["fecha_fin"]) if registro else datetime.today())
        duracion = calcular_duracion(fecha_inicio, fecha_fin)
    # --- Financiamiento y Planificación ---
    with st.expander("Financiamiento y Planificación"):
        monto_total = st.number_input("Monto total del proyecto", min_value=0.0, step=0.01, value=float(registro["monto_total"]) if registro else 0.0, format="%.2f")
        fuente_financiamiento = st.text_input("Fuente de financiamiento", value=registro["fuente_financiamiento"] if registro else "")
        entidad_ejecutora = st.text_input("Entidad ejecutora", value=registro["entidad_ejecutora"] if registro else "")

        eje_plan_biorregional = st.text_input("Eje Plan Biorregional", value=registro["eje_plan_biorregional"] if registro else "")
        eje_tematico_pb = st.text_input("Eje temático PB", value=registro["eje_tematico_pb"] if registro else "")
        estrategia_pb = st.text_input("Estrategia PB", value=registro["estrategia_pb"] if registro else "")
        accion_pb = st.text_input("Acción PB", value=registro["accion_pb"] if registro else "")
        objetivo_pei = st.text_input("Objetivo PEI", value=registro["objetivo_pei"] if registro else "")
        estrategia_pei = st.text_input("Estrategia PEI", value=registro["estrategia_pei"] if registro else "")
    # --- Indicadores y Metas ---
    with st.expander("Indicadores y Metas"):
        indicador_pb = st.text_input("Indicador PB", value=registro["indicador_pb"] if registro else "")
        unidad_pb = st.text_input("Unidad PB", value=registro["unidad_pb"] if registro else "")
        meta_pb = st.number_input("Meta PB", min_value=0.0, step=0.01, value=float(registro["meta_pb"]) if registro else 0.0, format="%.2f")

        indicador_pei = st.text_input("Indicador PEI", value=registro["indicador_pei"] if registro else "")
        unidad_pei = st.text_input("Unidad PEI", value=registro["unidad_pei"] if registro else "")
        meta_pei = st.number_input("Meta PEI", min_value=0.0, step=0.01, value=float(registro["meta_pei"]) if registro else 0.0, format="%.2f")

        indicador_proy = st.text_input("Indicador del proyecto", value=registro["indicador_proy"] if registro else "")
        unidad_proy = st.text_input("Unidad del proyecto", value=registro["unidad_proy"] if registro else "")
        meta_proy = st.number_input("Meta del proyecto", min_value=0.0, step=0.01, value=float(registro["meta_proy"]) if registro else 0.0, format="%.2f")

        tendencia = st.selectbox("Tendencia", ["Creciente","Decreciente","Horizontal"], index=["Creciente","Decreciente","Horizontal"].index(registro["tendencia"]) if registro else 0)
        ano_meta = st.number_input("Año cumplimiento meta", min_value=1900, max_value=2100, step=1, value=int(registro["ano_meta"]) if registro else datetime.today().year)
        ano_linea_base = st.number_input("Año línea base", min_value=1900, max_value=2100, step=1, value=int(registro["ano_linea_base"]) if registro else datetime.today().year)
        valor_linea_base = st.number_input("Valor línea base", min_value=0.0, step=0.01, value=float(registro["valor_linea_base"]) if registro else 0.0, format="%.2f")
        total_meta_cumplida = st.number_input("Total meta cumplida acumulada", min_value=0.0, step=0.01, value=float(registro["total_meta_cumplida"]) if registro else 0.0, format="%.2f")

        porcentaje_ejecucion_fisica = calcular_porcentaje(total_meta_cumplida, meta_proy)
        presupuesto_programado_total = st.number_input("Presupuesto programado total", min_value=0.0, step=0.01, value=float(registro["presupuesto_programado_total"]) if registro else 0.0, format="%.2f")
        presupuesto_devengado_total = st.number_input("Presupuesto devengado total", min_value=0.0, step=0.01, value=float(registro["presupuesto_devengado_total"]) if registro else 0.0, format="%.2f")
        porcentaje_ejecucion_presupuesto = calcular_porcentaje(presupuesto_devengado_total, presupuesto_programado_total)
    # --- Resultados, Logros y Responsable ---
    with st.expander("Resultados, Logros y Responsable"):
        nudos_criticos = st.text_area("Nudos críticos", value=registro["nudos_criticos"] if registro else "")
        logros_relevantes = st.text_area("Logros relevantes", value=registro["logros_relevantes"] if registro else "")
        aprendizajes = st.text_area("Aprendizajes", value=registro["aprendizajes"] if registro else "")
        medios_verificacion = st.text_area("Medios de verificación", value=registro["medios_verificacion"] if registro else "")

        nombre_responsable = st.text_input("Nombre responsable", value=registro["nombre_responsable"] if registro else "")
        cargo_responsable = st.text_input("Cargo responsable", value=registro["cargo_responsable"] if registro else "")
        correo_responsable = st.text_input("Correo responsable", value=registro["correo_responsable"] if registro else "")
        telefono_responsable = st.text_input("Teléfono responsable", value=registro["telefono_responsable"] if registro else "")

    data = {
        "nombre": nombre,
        "pais": pais,
        "provincia": provincia,
        "canton": canton,
        "pueblo": pueblo,
        "latitud": latitud,
        "longitud": longitud,
        "benef_hombres": benef_hombres,
        "benef_mujeres": benef_mujeres,
        "benef_glbti": benef_glbti,
        "total_beneficiarios": total_beneficiarios,
        "fecha_inicio": fecha_inicio.isoformat(),
        "fecha_fin": fecha_fin.isoformat(),
        "duracion": duracion,
        "monto_total": monto_total,
        "fuente_financiamiento": fuente_financiamiento,
        "entidad_ejecutora": entidad_ejecutora,
        "eje_plan_biorregional": eje_plan_biorregional,
        "eje_tematico_pb": eje_tematico_pb,
        "estrategia_pb": estrategia_pb,
        "accion_pb": accion_pb,
        "objetivo_pei": objetivo_pei,
        "estrategia_pei": estrategia_pei,
        "indicador_pb": indicador_pb,
        "unidad_pb": unidad_pb,
        "meta_pb": meta_pb,
        "indicador_pei": indicador_pei,
        "unidad_pei": unidad_pei,
        "meta_pei": meta_pei,
        "indicador_proy": indicador_proy,
        "unidad_proy": unidad_proy,
        "meta_proy": meta_proy,
        "tendencia": tendencia,
        "ano_meta": ano_meta,
        "ano_linea_base": ano_linea_base,
        "valor_linea_base": valor_linea_base,
        "total_meta_cumplida": total_meta_cumplida,
        "porcentaje_ejecucion_fisica": porcentaje_ejecucion_fisica,
        "presupuesto_programado_total": presupuesto_programado_total,
        "presupuesto_devengado_total": presupuesto_devengado_total,
        "porcentaje_ejecucion_presupuesto": porcentaje_ejecucion_presupuesto,
        "nudos_criticos": nudos_criticos,
        "logros_relevantes": logros_relevantes,
        "aprendizajes": aprendizajes,
        "medios_verificacion": medios_verificacion,
        "nombre_responsable": nombre_responsable,
        "cargo_responsable": cargo_responsable,
        "correo_responsable": correo_responsable,
        "telefono_responsable": telefono_responsable
    }

    return data

# ==========================
# MENÚ STREAMLIT
# ==========================
mostrar_logo()
st.title("Fundación Cuencas Sagradas")
st.subheader("Sistema Indígena de Monitoreo, Seguimiento, Evaluación y Aprendizaje")

menu = ["Crear Proyecto", "Ver / Editar Proyectos", "Buscar y Exportar"]
choice = st.sidebar.selectbox("Menú", menu)

# ==========================
# OPCIONES DEL MENU
# ==========================
if choice == "Crear Proyecto":
    data = formulario_proyecto()
    if st.button("💾 Guardar Proyecto"):
        resultado = insertar_registro(data)
        if resultado:
            st.success("✅ Proyecto guardado correctamente")
        else:
            st.error("❌ Error al guardar el proyecto")

elif choice == "Ver / Editar Proyectos":
    df = obtener_registros()
    if not df.empty:
        st.markdown("### 📊 Tabla de Proyectos")
        st.dataframe(df.style.highlight_max(axis=0, color="#d4f0f0"))

        selected_id = st.selectbox("Selecciona ID para editar o eliminar", df["id"])
        action = st.radio("Acción", ["Actualizar", "Eliminar"])

        if action == "Actualizar":
            registro = df[df["id"] == selected_id].iloc[0].to_dict()
            data = formulario_proyecto(registro=registro)
            if st.button("💾 Guardar Cambios"):
                actualizar_registro(selected_id, data)
                st.success("✅ Proyecto actualizado correctamente")

        elif action == "Eliminar":
            if st.button("🗑️ Eliminar proyecto"):
                eliminar_registro(selected_id)
                st.warning("Proyecto eliminado correctamente")
    else:
        st.info("No hay proyectos registrados.")

elif choice == "Buscar y Exportar":

    df = obtener_registros()   # ← CARGA REAL DE SUPABASE

    if not df.empty:

        st.subheader("🔍 Filtros de búsqueda")

        col1, col2, col3 = st.columns(3)

        with col1:
            nombre_filtro = st.text_input("Nombre del proyecto")

        with col2:
            provincia_filtro = st.text_input("Provincia / Departamento")

        with col3:
            import datetime
            ano_actual = datetime.datetime.now().year
            ano_filtro = st.number_input(
                "Año de cumplimiento de meta",
                min_value=1900,
                max_value=2100,
                step=1,
                value=ano_actual
            )

        # ---- Filtros ----
        df_filtrado = df.copy()

        if nombre_filtro:
            df_filtrado = df_filtrado[
                df_filtrado["nombre"].str.contains(nombre_filtro, case=False, na=False)
            ]

        if provincia_filtro:
            df_filtrado = df_filtrado[
                df_filtrado["provincia"].str.contains(provincia_filtro, case=False, na=False)
            ]

        if ano_filtro:
            df_filtrado = df_filtrado[df_filtrado["ano_meta"] == int(ano_filtro)]

        st.markdown("### 📋 Resultados filtrados")
        st.dataframe(df_filtrado)

        # --- Exportar ---
        if not df_filtrado.empty:
            excel_data = df_to_excel(df_filtrado)

            st.download_button(
                label="📥 Exportar a Excel",
                data=excel_data,
                file_name="proyectos_filtrados.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
        else:
            st.info("No se encontraron resultados con los filtros seleccionados.")

    else:
        st.warning("No existen registros en Supabase.")