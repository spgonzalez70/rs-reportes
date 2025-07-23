
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
        filtro_usuario = user if not is_admin else st.selectbox("Filtrar por comercial", ["Todos"] + visitas["Nombre Comercial"].dropna().unique().tolist())

        if user == "COMERCIAL" or is_admin:
            st.success(f"Bienvenido {user}")

            if user == "COMERCIAL":
                st.subheader("📌 Ofertas Pendientes")
                pendientes = visitas[(visitas["Nombre Comercial"] == "COMERCIAL") & (visitas["Estado"] == "Pendiente")]
                if not pendientes.empty:
                    st.dataframe(pendientes)
                    st.markdown("### ✏️ Editar una oferta pendiente")
                    selected = st.selectbox("Selecciona cliente para editar", pendientes["Cliente"].unique())
                    row = pendientes[pendientes["Cliente"] == selected].iloc[0]
                    idx = pendientes[pendientes["Cliente"] == selected].index[0]

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
                    st.info("No hay visitas pendientes actualmente.")

            st.subheader("🔎 Buscar Visitas por Estado")
            estados = visitas["Estado"].dropna().unique().tolist()
            estado_filtro = st.selectbox("Filtrar por estado", estados)
            df = visitas[(visitas["Estado"] == estado_filtro)]
            if not is_admin:
                df = df[df["Nombre Comercial"] == user]
            st.dataframe(df)
        else:
            st.info("Acceso solo disponible para COMERCIAL o ADMIN.")
