
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
            "Estado", "Próxima Acción", "Observaciones", "Oferta Compañía", "Mejora Luz",
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
    elif st.session_state.usuario == "COMERCIAL":
        st.success(f"Bienvenido {st.session_state.usuario}")

        st.subheader("📆 Visitas Pendientes o en Seguimiento")
        if not visitas.empty:
            pendientes = visitas[(visitas["Cerrado"] == "No") & (visitas["Nombre Comercial"] == "COMERCIAL")]
            if not pendientes.empty:
                st.dataframe(pendientes[["Fecha", "Cliente", "Servicio", "Estado", "Próxima Acción", "Observaciones"]])
            else:
                st.info("No hay visitas pendientes o en seguimiento.")
        else:
            st.info("No hay registros aún.")

        st.subheader("➕ Registrar Nueva Visita Comercial")
        with st.form("registro_visita"):
            fecha = st.date_input("Fecha de visita", value=datetime.today())
            cliente = st.text_input("Nombre del cliente o empresa")
            servicio = st.selectbox("Servicio interesado", ["Telefonía", "Energía", "Alarmas", "Software"])
            oportunidad = st.radio("¿Hubo oportunidad comercial?", ["Sí", "No"], horizontal=True)
            presupuesto = st.radio("¿Se entregó presupuesto?", ["Sí", "No"], horizontal=True)
            cerrado = st.radio("¿Se cerró la venta?", ["Sí", "No"], horizontal=True)
            estado = st.selectbox("Estado actual", ["Pendiente", "Volver a llamar", "Cerrado", "Rechazado"])
            proxima = st.date_input("Próxima acción (si aplica)", value=fecha + timedelta(days=7))
            observaciones = st.text_area("Observaciones")
            compania = st.selectbox("Oferta presentada con:", ["Vodafone", "Yoigo", "Orange", "O2", "RSmovitel", "Ninguna"])

            # Campos específicos
            mejora_luz = ""
            lineas = fibras = puestos = centralita = ip_fija = ""
            if servicio == "Energía":
                mejora_luz = st.radio("¿Se puede mejorar la oferta?", ["Sí", "No"], horizontal=True)
            elif servicio == "Telefonía":
                lineas = st.number_input("Nº Líneas Móviles", 0)
                fibras = st.number_input("Nº Fibras", 0)
                centralita = st.radio("¿Tiene centralita?", ["Sí", "No"], horizontal=True)
                puestos = st.number_input("Nº Puestos Centralita", 0)
                ip_fija = st.radio("¿Dispone de IP fija?", ["Sí", "No"], horizontal=True)

            submitted = st.form_submit_button("Guardar visita")

            if submitted:
                nueva_visita = pd.DataFrame([{
                    "Fecha": fecha,
                    "Nombre Comercial": "COMERCIAL",
                    "Cliente": cliente,
                    "Servicio": servicio,
                    "Oportunidad": oportunidad,
                    "Presupuesto": presupuesto,
                    "Cerrado": cerrado,
                    "Estado": estado,
                    "Próxima Acción": proxima,
                    "Observaciones": observaciones,
                    "Oferta Compañía": compania,
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

        st.subheader("📋 Historial Diario de Visitas")
        fecha_filtro = st.date_input("Filtrar por fecha", value=datetime.today())
        visitas_dia = visitas[(visitas["Fecha"] == pd.to_datetime(fecha_filtro)) & (visitas["Nombre Comercial"] == "COMERCIAL")]

        if not visitas_dia.empty:
            st.dataframe(visitas_dia)
        else:
            st.info("No hay visitas registradas en esa fecha.")
