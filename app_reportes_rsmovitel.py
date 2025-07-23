
import streamlit as st
import pandas as pd
import json
import os
from datetime import datetime, timedelta

st.set_page_config(page_title="Gestión Comercial RSMovitel", layout="wide")
st.markdown("""<style>
    .main { background-color: #f4f9f4; }
    .stApp { font-family: 'Segoe UI', sans-serif; }
    h1, h2, h3 { color: #006400; }
</style>""", unsafe_allow_html=True)

def cargar_usuarios():
    with open("users.json", "r") as f:
        return json.load(f)

def guardar_usuarios(usuarios):
    with open("users.json", "w") as f:
        json.dump(usuarios, f, indent=4)

def cargar_visitas():
    archivo = "visitas_comercial.csv"
    if os.path.exists(archivo):
        df = pd.read_csv(archivo)
        df["Fecha"] = pd.to_datetime(df["Fecha"], errors='coerce')
        return df
    else:
        return pd.DataFrame(columns=[
            "Fecha", "Nombre Comercial", "Cliente", "Servicio", "Oportunidad", "Presupuesto", "Cerrado",
            "Estado", "Próxima Acción", "Observaciones", "Ofertas Presentadas", "Mejora Luz",
            "Líneas Móviles", "Fibras", "Centralita", "Puestos", "IP Fija"
        ])

def guardar_visitas(df):
    df.to_csv("visitas_comercial.csv", index=False)

usuarios = cargar_usuarios()
visitas = cargar_visitas()

st.title("🔐 Gestión Comercial - RSMovitel")
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
                st.success("Contraseña actualizada. Reinicia sesión.")
                st.session_state.usuario = None
            else:
                st.error("Las contraseñas no coinciden.")
    else:
        user = st.session_state.usuario
        is_admin = user == "admin"

        if user == "COMERCIAL" or is_admin:
            st.success(f"Bienvenido {user}")
            if user == "COMERCIAL":
                filtro_usuario = "COMERCIAL"
            elif is_admin:
                filtro_usuario = st.selectbox("Filtrar por comercial", ["Todos"] + visitas["Nombre Comercial"].dropna().unique().tolist())

            st.subheader("➕ Registrar Nueva Visita Comercial")
            with st.form("registro_visita"):
                fecha = st.date_input("Fecha de visita", value=datetime.today())
                cliente = st.text_input("Nombre del cliente o empresa")
                servicio = st.multiselect("Servicio interesado", ["Telefonía", "Energía", "Alarmas", "Software"])
                oportunidad = st.radio("¿Hubo oportunidad comercial?", ["Sí", "No"], horizontal=True)
                presupuesto = st.radio("¿Se entregó presupuesto?", ["Sí", "No"], horizontal=True)
                cerrado = st.radio("¿Se cerró la venta?", ["Sí", "No"], horizontal=True)
                estado = st.selectbox("Estado actual", ["Pendiente", "Volver a llamar", "Cerrado", "Rechazado"])
                proxima = st.date_input("Próxima acción", value=fecha + timedelta(days=7))
                observaciones = st.text_area("Observaciones")
                ofertas = st.multiselect("Oferta presentada con", ["Vodafone", "Yoigo", "Orange", "O2", "RSmovitel", "Plenitude u otras", "ClassicGes"])

                mejora_luz = ""
                lineas = fibras = puestos = centralita = ip_fija = ""

                if "Energía" in servicio:
                    mejora_luz = st.radio("¿Se puede mejorar la oferta de luz?", ["Sí", "No"], horizontal=True)

                if "Telefonía" in servicio:
                    lineas = st.number_input("Nº Líneas Móviles", 0)
                    fibras = st.number_input("Nº Fibras", 0)
                    centralita = st.radio("¿Tiene centralita?", ["Sí", "No"], horizontal=True)
                    puestos = st.number_input("Nº Puestos Centralita", 0)
                    ip_fija = st.radio("¿Dispone de IP fija?", ["Sí", "No"], horizontal=True)

                submitted = st.form_submit_button("Guardar visita")

                if submitted:
                    nueva_visita = pd.DataFrame([{
                        "Fecha": fecha,
                        "Nombre Comercial": user if not is_admin else "COMERCIAL",
                        "Cliente": cliente,
                        "Servicio": ", ".join(servicio),
                        "Oportunidad": oportunidad,
                        "Presupuesto": presupuesto,
                        "Cerrado": cerrado,
                        "Estado": estado,
                        "Próxima Acción": proxima,
                        "Observaciones": observaciones,
                        "Ofertas Presentadas": ", ".join(ofertas),
                        "Mejora Luz": mejora_luz,
                        "Líneas Móviles": lineas,
                        "Fibras": fibras,
                        "Centralita": centralita,
                        "Puestos": puestos,
                        "IP Fija": ip_fija
                    }])
                    visitas = pd.concat([visitas, nueva_visita], ignore_index=True)
                    guardar_visitas(visitas)
                    st.success("✅ Visita registrada correctamente.")

            st.subheader("📋 Historial y Edición de Visitas")
            fecha_filtro = st.date_input("Filtrar por fecha", value=datetime.today())
            df = visitas.copy()
            if filtro_usuario != "Todos":
                df = df[df["Nombre Comercial"] == filtro_usuario]
            df = df[df["Fecha"] == pd.to_datetime(fecha_filtro)]

            if not df.empty:
                st.dataframe(df)
                selected_cliente = st.selectbox("Selecciona cliente para editar", df["Cliente"].unique())
                row = df[df["Cliente"] == selected_cliente].iloc[0]
                idx = df[df["Cliente"] == selected_cliente].index[0]

                with st.form("edit_form"):
                    cerrado_nuevo = st.radio("¿Se cerró la venta?", ["Sí", "No"], index=0 if row["Cerrado"] == "Sí" else 1)
                    estado_nuevo = st.selectbox("Estado actual", ["Pendiente", "Volver a llamar", "Cerrado", "Rechazado"], index=["Pendiente", "Volver a llamar", "Cerrado", "Rechazado"].index(row["Estado"]))
                    proxima_nueva = st.date_input("Próxima acción", value=pd.to_datetime(row["Próxima Acción"]))
                    observ_nueva = st.text_area("Observaciones", value=row["Observaciones"])
                    if st.form_submit_button("Actualizar Visita"):
                        visitas.at[idx, "Cerrado"] = cerrado_nuevo
                        visitas.at[idx, "Estado"] = estado_nuevo
                        visitas.at[idx, "Próxima Acción"] = proxima_nueva
                        visitas.at[idx, "Observaciones"] = observ_nueva
                        guardar_visitas(visitas)
                        st.success("✅ Visita actualizada correctamente.")
            else:
                st.info("No hay visitas para ese día.")
        else:
            st.info("Acceso solo disponible para COMERCIAL o ADMIN.")
