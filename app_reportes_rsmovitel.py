
import streamlit as st
import pandas as pd
import json
import os
from datetime import datetime

# ===== CONFIGURACIÓN VISUAL =====
st.set_page_config(page_title="Reportes RSMovitel", layout="wide")
st.markdown("""<style>
    .main { background-color: #f4f9f4; }
    .stApp { font-family: 'Segoe UI', sans-serif; }
    h1, h2, h3 { color: #006400; }
</style>""", unsafe_allow_html=True)

# ===== FUNCIONES USUARIOS =====
def cargar_usuarios():
    with open("users.json", "r") as f:
        return json.load(f)

def guardar_usuarios(usuarios):
    with open("users.json", "w") as f:
        json.dump(usuarios, f, indent=4)

usuarios = cargar_usuarios()

# ===== LOGIN =====
st.title("🔐 Acceso al Sistema de Reportes - RSMovitel")

username = st.sidebar.text_input("Usuario")
password = st.sidebar.text_input("Contraseña", type="password")
login_btn = st.sidebar.button("Iniciar Sesión")

if "usuario" not in st.session_state:
    st.session_state.usuario = None

if login_btn:
    if username in usuarios and usuarios[username]["password"] == password:
        st.session_state.usuario = username
        st.session_state.first_login = usuarios[username]["first_login"]
        st.session_state.last_change = usuarios[username]["last_change"]
    else:
        st.error("Credenciales incorrectas")

if st.session_state.usuario:
    dias_transcurridos = (datetime.today().date() - datetime.strptime(st.session_state.last_change, "%Y-%m-%d").date()).days
    if st.session_state.first_login or dias_transcurridos > 180:
        st.warning("⚠️ Debes cambiar tu contraseña antes de continuar.")
        new_pass = st.text_input("Nueva Contraseña", type="password")
        confirm_pass = st.text_input("Confirmar Contraseña", type="password")
        if st.button("Actualizar Contraseña"):
            if new_pass == confirm_pass and new_pass.strip() != "":
                usuarios[st.session_state.usuario]["password"] = new_pass
                usuarios[st.session_state.usuario]["first_login"] = False
                usuarios[st.session_state.usuario]["last_change"] = str(datetime.today().date())
                guardar_usuarios(usuarios)
                st.success("Contraseña actualizada correctamente. Reinicia sesión.")
                st.session_state.usuario = None
            else:
                st.error("Las contraseñas no coinciden o son inválidas.")
    else:
        st.success(f"Bienvenido, {st.session_state.usuario}")
        es_admin = st.session_state.usuario == "admin"
        tipo_reporte = "Comercial" if st.session_state.usuario == "COMERCIAL" else "Backoffice"

        tabs = st.tabs(["📋 Registrar Reporte", "📈 Ver Reportes"])

        # ========== FORMULARIOS ==========
        with tabs[0]:
            if es_admin:
                st.info("🔎 Los administradores no rellenan reportes. Usa la pestaña 'Ver Reportes'.")
            elif tipo_reporte == "Comercial":
                st.header("🧑‍💼 Reporte Comercial Diario")
                with st.form("form_comercial"):
                    fecha = st.date_input("Fecha", value=datetime.today())
                    nombre = st.text_input("Nombre del Comercial", st.session_state.usuario)
                    zona = st.text_input("Zona / Territorio")
                    dias_activo = st.number_input("Días Activos en Calle", 0, 7)
                    visitas = st.number_input("Visitas Presenciales", 0)
                    llamadas = st.number_input("Llamadas Comerciales", 0)
                    oportunidades = st.number_input("Oportunidades Detectadas", 0)
                    presupuestos = st.number_input("Presupuestos Entregados", 0)
                    cierres = st.number_input("Cierres Realizados", 0)
                    ratio = st.number_input("Ratio Cierre / Oportunidades (%)", 0.0, 100.0)
                    importe = st.number_input("Importe Total Ventas (€)", 0.0)
                    comision = st.number_input("Comisión Estimada (€)", 0.0)
                    tlf = st.number_input("Ventas Telefonía (unidades)", 0)
                    marca = st.number_input("Altas Marca Propia (líneas)", 0)
                    energia = st.number_input("Contratos Energía", 0)
                    alarmas = st.number_input("Instalaciones Alarmas", 0)
                    software = st.number_input("Licencias Software", 0)
                    observaciones = st.text_area("Clientes destacables / Objeciones / Soporte requerido")
                    submit = st.form_submit_button("Guardar")
                    if submit:
                        nuevo = pd.DataFrame([{
                            "Fecha": str(fecha), "Nombre Comercial": nombre, "Zona / Territorio": zona,
                            "Días Activos en Calle": dias_activo, "Visitas Presenciales": visitas,
                            "Llamadas Comerciales": llamadas, "Oportunidades Detectadas": oportunidades,
                            "Presupuestos Entregados": presupuestos, "Cierres Realizados": cierres,
                            "Ratio Cierre/Oportunidades (%)": ratio, "Importe Total Ventas (€)": importe,
                            "Comisión Estimada (€)": comision, "Ventas Telefonía (uds)": tlf,
                            "Altas Marca Propia (líneas)": marca, "Contratos Energía": energia,
                            "Instalaciones Alarmas": alarmas, "Licencias Software": software,
                            "Clientes destacables / Objeciones / Soporte requerido": observaciones
                        }])
                        archivo = "reportes_comercial.csv"
                        if not os.path.exists(archivo):
                            nuevo.to_csv(archivo, index=False)
                        else:
                            antiguo = pd.read_csv(archivo)
                            pd.concat([antiguo, nuevo]).to_csv(archivo, index=False)
                        st.success("✅ Reporte comercial guardado correctamente.")

            elif tipo_reporte == "Backoffice":
                st.header("🗂️ Reporte Backoffice Diario")
                with st.form("form_backoffice"):
                    fecha = st.date_input("Fecha", value=datetime.today())
                    nombre = st.text_input("Nombre del Empleado", st.session_state.usuario)
                    dias = st.number_input("Días Trabajados", 0, 7)
                    horas = st.number_input("Horas Totales", 0.0)
                    tlf = st.number_input("Tramitaciones Telefonía", 0)
                    energia = st.number_input("Tramitaciones Energía", 0)
                    alarmas = st.number_input("Tramitaciones Alarmas", 0)
                    software = st.number_input("Tramitaciones Software", 0)
                    correctas = st.number_input("Altas Correctas a la Primera (%)", 0.0, 100.0)
                    tiempo = st.number_input("Tiempo Medio Tramitación (min)", 0.0)
                    incidencias = st.number_input("Incidencias Internas", 0)
                    soporte = st.number_input("Soporte a Colaboradores (nº)", 0)
                    carga = st.slider("Carga Emocional (1-5)", 1, 5)
                    observaciones = st.text_area("Observaciones / Recomendaciones")
                    submit = st.form_submit_button("Guardar")
                    if submit:
                        nuevo = pd.DataFrame([{
                            "Fecha": str(fecha), "Nombre Empleado": nombre, "Días Trabajados": dias,
                            "Horas Totales": horas, "Tramitaciones Telefonía": tlf,
                            "Tramitaciones Energía": energia, "Tramitaciones Alarmas": alarmas,
                            "Tramitaciones Software": software,
                            "Altas Correctas a la Primera (%)": correctas,
                            "Tiempo Medio Tramitación (min)": tiempo, "Incidencias Internas": incidencias,
                            "Soporte a Colaboradores (nº)": soporte, "Carga Emocional (1-5)": carga,
                            "Observaciones / Recomendaciones": observaciones
                        }])
                        archivo = "reportes_backoffice.csv"
                        if not os.path.exists(archivo):
                            nuevo.to_csv(archivo, index=False)
                        else:
                            antiguo = pd.read_csv(archivo)
                            pd.concat([antiguo, nuevo]).to_csv(archivo, index=False)
                        st.success("✅ Reporte backoffice guardado correctamente.")

        # ========== VISUALIZACIÓN ==========
        with tabs[1]:
            st.header("📊 Visualización de Reportes")
            col1, col2 = st.columns(2)
            with col1:
                tipo_vista = st.selectbox("Tipo de Reporte", ["Comercial", "Backoffice"])
            with col2:
                fechas = st.date_input("Filtrar por Fecha (puedes seleccionar rango)", [])

            archivo = "reportes_comercial.csv" if tipo_vista == "Comercial" else "reportes_backoffice.csv"

            if os.path.exists(archivo):
                df = pd.read_csv(archivo)
                if fechas:
                    if isinstance(fechas, list) and len(fechas) == 2:
                        inicio, fin = fechas
                        df["Fecha"] = pd.to_datetime(df["Fecha"])
                        df = df[(df["Fecha"] >= pd.to_datetime(inicio)) & (df["Fecha"] <= pd.to_datetime(fin))]
                st.dataframe(df, use_container_width=True)
            else:
                st.info("No hay reportes registrados todavía.")
