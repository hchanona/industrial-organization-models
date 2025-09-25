
import streamlit as st

st.set_page_config(page_title="IO Lab — Modelos de Competencia", layout="wide")
st.title("IO Lab — Modelos de Competencia")

st.markdown(
    """
Bienvenido/a. Este es un *multipágina* en Streamlit con una página de inicio y dos modelos:

- **Duopolio de Cournot** (cantidades simultáneas).
- **Stackelberg (líder–seguidor)** (cantidades secuenciales).

Usa el menú lateral (☰) o la lista de páginas (arriba a la izquierda) para navegar.
Cada página tiene su propia barra lateral con parámetros.

"""
)

