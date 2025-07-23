
import streamlit as st
import pandas as pd
import os

st.set_page_config(page_title="Reportes RSMovitel", layout="wide")

st.title("📊 Sistema de Reportes Semanales - RSMovitel")

tipo_reporte = st.sidebar.selectbox("Selecciona tipo de reporte", ["Comercial", "Backoffice"])

if tipo_reporte == "Comercial":
    st.header("🧑‍💼 Reporte Comercial")
    with st.form("form_comercial"):
        semana = st.text_input("Semana")
        nombre = st.text_input("Nombre del Comercial")
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
                "Semana": semana, "Nombre Comercial": nombre, "Zona / Territorio": zona,
                "Días Activos en Calle": dias_activo, "Visitas Presenciales": visitas,
                "Llamadas Comerciales": llamadas, "Oportunidades Detectadas": oportunidades,
                "Presupuestos Entregados": presupuestos, "Cierres Realizados": cierres,
                "Ratio Cierre/Oportunidades (%)": ratio, "Importe Total Ventas (€)": importe,
                "Comisión Estimada (€)": comision, "Ventas Telefonía (uds)": tlf,
                "Altas Marca Propia (líneas)": marca, "Contratos Energía": energia,
                "Instalaciones Alarmas": alarmas, "Licencias Software": software,
                "Clientes destacables / Objeciones / Soporte requerido": observaciones
            }])
            if not os.path.exists("reportes_comercial.csv"):
                nuevo.to_csv("reportes_comercial.csv", index=False)
            else:
                antiguo = pd.read_csv("reportes_comercial.csv")
                pd.concat([antiguo, nuevo]).to_csv("reportes_comercial.csv", index=False)
            st.success("Reporte comercial guardado correctamente.")

else:
    st.header("🗂️ Reporte Backoffice")
    with st.form("form_backoffice"):
        semana = st.text_input("Semana")
        nombre = st.text_input("Nombre del Empleado")
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
                "Semana": semana, "Nombre Empleado": nombre, "Días Trabajados": dias,
                "Horas Totales": horas, "Tramitaciones Telefonía": tlf, "Tramitaciones Energía": energia,
                "Tramitaciones Alarmas": alarmas, "Tramitaciones Software": software,
                "Altas Correctas a la Primera (%)": correctas, "Tiempo Medio Tramitación (min)": tiempo,
                "Incidencias Internas": incidencias, "Soporte a Colaboradores (nº)": soporte,
                "Carga Emocional (1-5)": carga, "Observaciones / Recomendaciones": observaciones
            }])
            if not os.path.exists("reportes_backoffice.csv"):
                nuevo.to_csv("reportes_backoffice.csv", index=False)
            else:
                antiguo = pd.read_csv("reportes_backoffice.csv")
                pd.concat([antiguo, nuevo]).to_csv("reportes_backoffice.csv", index=False)
            st.success("Reporte backoffice guardado correctamente.")
