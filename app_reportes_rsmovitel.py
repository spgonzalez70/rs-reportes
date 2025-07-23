import streamlit as st
import pandas as pd
import json
import os
from datetime import datetime, timedelta

st.set_page_config(page_title="Gestión Comercial RSMovitel", layout="wide")
st.markdown("""
    <style>
        .main { background-color: #f4f9f4; }
        .stApp { font-family: 'Segoe UI', sans-serif; }
        h1, h2, h3 { color: #006400; }
    </style>
""", unsafe_allow_html=True)

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
    st.session_state.nuevo_registro = False
    st.session_state.editar_cliente = None

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
        st.success("Bienvenido, COMERCIAL")

        st.subheader("📌 Ofertas Pendientes")
        pendientes = visitas[(visitas["Nombre Comercial"] == "COMERCIAL") & (visitas["Estado"] == "Pendiente")]
        if not pendientes.empty:
            st.dataframe(pendientes)
        else:
            st.info("No hay visitas pendientes.")

        col1, col2 = st.columns(2)
        with col1:
            if st.button("➕ Nuevo Registro"):
                st.session_state.nuevo_registro = True
                st.session_state.editar_cliente = None
        with col2:
            cliente_editable = st.selectbox("Selecciona cliente para editar", pendientes["Cliente"].unique() if not pendientes.empty else [])
            if st.button("✏️ Editar Registro"):
                st.session_state.editar_cliente = cliente_editable
                st.session_state.nuevo_registro = False

        if st.session_state.nuevo_registro:
            st.subheader("📝 Nuevo Registro de Visita")
            with st.form("nuevo_form"):
                fecha = st.date_input("Fecha de visita", value=datetime.today())
                cliente = st.text_input("Nombre del cliente o empresa")
                if cliente in visitas["Cliente"].values:
                    st.warning("⚠️ Ya existe una visita registrada con este nombre. Considera editarla en lugar de duplicarla.")
                servicio = st.multiselect("Servicio interesado", ["Telefonía", "Energía", "Alarmas", "Software"])
                oportunidad = st.radio("¿Hubo oportunidad comercial?", ["Sí", "No"], horizontal=True)
                presupuesto = st.radio("¿Se entregó presupuesto?", ["Sí", "No"], horizontal=True)
                cerrado = st.radio("¿Se cerró la venta?", ["Sí", "No"], horizontal=True)
                estado = st.selectbox("Estado actual", ["Pendiente", "Volver a llamar", "Cerrado", "Rechazado"])
                proxima = st.date_input("Próxima acción", value=fecha + timedelta(days=7))
                observaciones = st.text_area("Observaciones")
                ofertas = st.multiselect("Oferta presentada con", ["Vodafone", "Yoigo", "Orange", "O2", "RSmovitel", "Plenitude u otras", "ClassicGes"])
                mejora_luz = lineas = fibras = puestos = centralita = ip_fija = ""

                if "Energía" in servicio:
                    mejora_luz = st.radio("¿Se puede mejorar la oferta de luz?", ["Sí", "No"], horizontal=True)
                if "Telefonía" in servicio:
                    lineas = st.number_input("Nº Líneas Móviles", 0)
                    fibras = st.number_input("Nº Fibras", 0)
                    centralita = st.radio("¿Tiene centralita?", ["Sí", "No"], horizontal=True)
                    puestos = st.number_input("Nº Puestos Centralita", 0)
                    ip_fija = st.radio("¿Dispone de IP fija?", ["Sí", "No"], horizontal=True)

                if st.form_submit_button("Guardar visita"):
                    nueva_visita = pd.DataFrame([{
                        "Fecha": fecha,
                        "Nombre Comercial": "COMERCIAL",
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
                    st.session_state.nuevo_registro = False

        if st.session_state.editar_cliente:
            st.subheader(f"✏️ Editar visita de: {st.session_state.editar_cliente}")
            row = visitas[(visitas["Cliente"] == st.session_state.editar_cliente) & (visitas["Nombre Comercial"] == "COMERCIAL")].iloc[0]
            idx = visitas[(visitas["Cliente"] == row["Cliente"]) & (visitas["Fecha"] == row["Fecha"])].index[0]
            with st.form("editar_form"):
                servicios_actuales = [s.strip() for s in row["Servicio"].split(",") if s.strip()]
                ofertas_actuales = [o.strip() for o in row["Ofertas Presentadas"].split(",") if o.strip()]
                servicios_editar = st.multiselect("Servicio interesado", ["Telefonía", "Energía", "Alarmas", "Software"], default=servicios_actuales)
                ofertas_editar = st.multiselect("Ofertas Presentadas", ["Vodafone", "Yoigo", "Orange", "O2", "RSmovitel", "Plenitude u otras", "ClassicGes"], default=ofertas_actuales)
                cerrado_nuevo = st.radio("¿Se cerró la venta?", ["Sí", "No"], index=0 if row["Cerrado"] == "Sí" else 1)
                estado_nuevo = st.selectbox("Estado actual", ["Pendiente", "Volver a llamar", "Cerrado", "Rechazado"], index=["Pendiente", "Volver a llamar", "Cerrado", "Rechazado"].index(row["Estado"]))
                proxima_nueva = st.date_input("Próxima acción", value=pd.to_datetime(row["Próxima Acción"]))
                observ_nueva = st.text_area("Observaciones", value="" if pd.isna(row["Observaciones"]) else row["Observaciones"])
                if st.form_submit_button("Actualizar visita"):
                    visitas.at[idx, "Servicio"] = ", ".join(servicios_editar)
                    visitas.at[idx, "Ofertas Presentadas"] = ", ".join(ofertas_editar)
                    visitas.at[idx, "Cerrado"] = cerrado_nuevo
                    visitas.at[idx, "Estado"] = estado_nuevo
                    visitas.at[idx, "Próxima Acción"] = proxima_nueva
                    visitas.at[idx, "Observaciones"] = observ_nueva
                    guardar_visitas(visitas)
                    st.success("✅ Visita actualizada correctamente.")
                    st.session_state.editar_cliente = None
