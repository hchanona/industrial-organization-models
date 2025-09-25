import streamlit as st

# --- Página de inicio ---
def instrucciones():
    st.set_page_config(page_title="IO Lab — Modelos de Competencia", layout="wide")
    st.title("Instrucciones:")
    st.markdown(
        """
Bienvenido/a. Este es un *multipágina* en Streamlit con una página de inicio y cinco modelos:

- **Duopolio de Cournot** (cantidades simultáneas).
- **Stackelberg (líder–seguidor)** (cantidades secuenciales).
- **Colusión Cournot** (gatillo y comparación).
- **Hotelling lineal** (precios entregados, ganancias y bienestar).
- **Oligopolio Cournot (asim.)** (costos heterogéneos, bienestar y cuotas).

Usa el menú lateral (☰) o la lista de páginas (arriba a la izquierda) para navegar.
Cada página tiene su propia barra lateral con parámetros.
        """
    )

# --- Definir páginas del multipágina con títulos personalizados ---
home       = st.Page(instrucciones, title="Instrucciones:")
monopolio = st.Page("pages/0_Monopolio.py", title="0. Monopolio")
cournot    = st.Page("pages/1_Duopolio_de_Cournot.py",          title="Duopolio de Cournot")
oligo_asim = st.Page("pages/5_Oligopolio_Cournot_Asimetrico.py", title="Oligopolio de Cournot")
stack      = st.Page("pages/2_Stackelberg_Duopolio.py",         title="Duopolio de Stackelberg")
hotelling  = st.Page("pages/4_Hotelling_Lineal.py",             title="Hotelling lineal")
colusion   = st.Page("pages/3_Colusion.py",                     title="Colusión Cournot")
bertrand   = st.Page("pages/7_Bertrand_Homogeneo.py",           title="Bertrand homogéneo")

# --- Router ---
st.navigation([home, monopolio, cournot, oligo_asim, bertrand, stack, hotelling, colusion]).run()
