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
        .block-title { font-weight: bold; font-size: 1.2em; margin-top: 1.2em; }
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
            if st.button("➕ Nueva visita"):
                st.session_state.nuevo_registro = True
                st.session_state.editar_cliente = None
        with col2:
            cliente_editable = st.selectbox("Selecciona cliente para editar", pendientes["Cliente"].unique() if not pendientes.empty else [])
            if st.button("✏️ Editar visita"):
                st.session_state.editar_cliente = cliente_editable
                st.session_state.nuevo_registro = False

        if st.session_state.nuevo_registro:
            st.markdown('<div class="block-title">🗂️ Datos Generales</div>', unsafe_allow_html=True)
            with st.form("nuevo_form"):
                fecha = st.date_input("Fecha de visita", value=datetime.today())
                cliente = st.text_input("Nombre del cliente o empresa")
                if cliente in visitas["Cliente"].values:
                    st.warning("⚠️ Ya existe una visita registrada con este nombre. Considera editarla en lugar de duplicarla.")
                servicio = st.multiselect("Servicios interesados", ["Telefonía", "Energía", "Alarmas", "Software"])
                oportunidad = st.radio("¿Hubo oportunidad comercial?", ["Sí", "No"], horizontal=True)
                presupuesto = st.radio("¿Se entregó presupuesto?", ["Sí", "No"], horizontal=True)
                cerrado = st.radio("¿Se cerró la venta?", ["Sí", "No"], horizontal=True)
                estado = st.selectbox("Estado actual", ["Pendiente", "Volver a llamar", "Cerrado", "Rechazado"])
                proxima = st.date_input("Próxima acción", value=fecha + timedelta(days=7))

                st.markdown('<div class="block-title">📝 Ofertas presentadas</div>', unsafe_allow_html=True)
                ofertas = st.multiselect(
                    "Ofertas presentadas con",
                    ["Vodafone", "Yoigo", "Orange", "O2", "RSmovitel", "Plenitude u otras", "ClassicGes"]
                )

                if "Telefonía" in servicio:
                    st.markdown('<div class="block-title">📱 Datos Telefonía</div>', unsafe_allow_html=True)
                    lineas = st.number_input("Nº Líneas Móviles", 0)
                    fibras = st.number_input("Nº Fibras", 0)
                    centralita = st.radio("¿Tiene centralita?", ["Sí", "No"], horizontal=True)
                    puestos = st.number_input("Nº Puestos Centralita", 0)
                    ip_fija = st.radio("¿Dispone de IP fija?", ["Sí", "No"], horizontal=True)
                else:
                    lineas = fibras = puestos = centralita = ip_fija = ""

                if "Energía" in servicio:
                    st.markdown('<div class="block-title">⚡ Datos Energía</div>', unsafe_allow_html=True)
                    mejora_luz = st.radio("¿Se puede mejorar la oferta de luz?", ["Sí", "No"], horizontal=True)
                else:
                    mejora_luz = ""

                st.markdown('<div class="block-title">🗒️ Observaciones</div>', unsafe_allow_html=True)
                observaciones = st.text_area("Observaciones")

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
            row = visitas[(visitas["Cliente"] == st.session_state.editar_cliente) & (visitas["Nombre Comercial"] == "COMERCIAL")].iloc[0]
            idx = visitas[(visitas["Cliente"] == row["Cliente"]) & (visitas["Fecha"] == row["Fecha"])].index[0]
            # Preparar valores robustos
            servicios_val = row["Servicio"]
            if not isinstance(servicios_val, str):
                servicios_val = ""
            servicios_actuales = [s.strip() for s in servicios_val.split(",") if s.strip()]

            ofertas_val = row["Ofertas Presentadas"]
            if not isinstance(ofertas_val, str):
                ofertas_val = ""
            ofertas_actuales = [o.strip() for o in ofertas_val.split(",") if o.strip()]

            st.markdown('<div class="block-title">🗂️ Datos Generales</div>', unsafe_allow_html=True)
            with st.form("editar_form"):
                fecha = st.date_input("Fecha de visita", value=pd.to_datetime(row["Fecha"]))
                cliente = st.text_input("Nombre del cliente o empresa", value=row["Cliente"], disabled=True)
                servicio = st.multiselect("Servicios interesados", ["Telefonía", "Energía", "Alarmas", "Software"], default=servicios_actuales)
                oportunidad = st.radio("¿Hubo oportunidad comercial?", ["Sí", "No"], index=0 if row["Oportunidad"] == "Sí" else 1, horizontal=True)
                presupuesto = st.radio("¿Se entregó presupuesto?", ["Sí", "No"], index=0 if row["Presupuesto"] == "Sí" else 1, horizontal=True)
                cerrado = st.radio("¿Se cerró la venta?", ["Sí", "No"], index=0 if row["Cerrado"] == "Sí" else 1, horizontal=True)
                estado = st.selectbox("Estado actual", ["Pendiente", "Volver a llamar", "Cerrado", "Rechazado"], index=["Pendiente", "Volver a llamar", "Cerrado", "Rechazado"].index(row["Estado"]))
                proxima = st.date_input("Próxima acción", value=pd.to_datetime(row["Próxima Acción"]))

                st.markdown('<div class="block-title">📝 Ofertas presentadas</div>', unsafe_allow_html=True)
                ofertas = st.multiselect(
                    "Ofertas presentadas con",
                    ["Vodafone", "Yoigo", "Orange", "O2", "RSmovitel", "Plenitude u otras", "ClassicGes"],
                    default=ofertas_actuales
                )

                if "Telefonía" in servicio:
                    st.markdown('<div class="block-title">📱 Datos Telefonía</div>', unsafe_allow_html=True)
                    lineas = st.number_input("Nº Líneas Móviles", 0, value=int(row["Líneas Móviles"]) if not pd.isna(row["Líneas Móviles"]) and str(row["Líneas Móviles"]).isdigit() else 0)
                    fibras = st.number_input("Nº Fibras", 0, value=int(row["Fibras"]) if not pd.isna(row["Fibras"]) and str(row["Fibras"]).isdigit() else 0)
                    centralita = st.radio("¿Tiene centralita?", ["Sí", "No"], index=0 if row["Centralita"] == "Sí" else 1, horizontal=True)
                    puestos = st.number_input("Nº Puestos Centralita", 0, value=int(row["Puestos"]) if not pd.isna(row["Puestos"]) and str(row["Puestos"]).isdigit() else 0)
                    ip_fija = st.radio("¿Dispone de IP fija?", ["Sí", "No"], index=0 if row["IP Fija"] == "Sí" else 1, horizontal=True)
                else:
                    lineas = fibras = puestos = centralita = ip_fija = ""

                if "Energía" in servicio:
                    st.markdown('<div class="block-title">⚡ Datos Energía</div>', unsafe_allow_html=True)
                    mejora_luz = st.radio("¿Se puede mejorar la oferta de luz?", ["Sí", "No"], index=0 if row["Mejora Luz"] == "Sí" else 1, horizontal=True)
                else:
                    mejora_luz = ""

                st.markdown('<div class="block-title">🗒️ Observaciones</div>', unsafe_allow_html=True)
                observaciones = st.text_area("Observaciones", value="" if pd.isna(row["Observaciones"]) else row["Observaciones"])

                if st.form_submit_button("Actualizar visita"):
                    visitas.at[idx, "Fecha"] = fecha
                    visitas.at[idx, "Servicio"] = ", ".join(servicio)
                    visitas.at[idx, "Oportunidad"] = oportunidad
                    visitas.at[idx, "Presupuesto"] = presupuesto
                    visitas.at[idx, "Cerrado"] = cerrado
                    visitas.at[idx, "Estado"] = estado
                    visitas.at[idx, "Próxima Acción"] = proxima
                    visitas.at[idx, "Observaciones"] = observaciones
                    visitas.at[idx, "Ofertas Presentadas"] = ", ".join(ofertas)
                    visitas.at[idx, "Mejora Luz"] = mejora_luz
                    visitas.at[idx, "Líneas Móviles"] = lineas
                    visitas.at[idx, "Fibras"] = fibras
                    visitas.at[idx, "Centralita"] = centralita
                    visitas.at[idx, "Puestos"] = puestos
                    visitas.at[idx, "IP Fija"] = ip_fija
                    guardar_visitas(visitas)
                    st.success("✅ Visita actualizada correctamente.")
                    st.session_state.editar_cliente = None
