import streamlit as st

# --- Página de inicio ---
def instrucciones():
    st.set_page_config(page_title="IO Lab — Modelos de Competencia", layout="wide")
    st.title("Instrucciones:")

    st.markdown(
        """
Bienvenido/a. Este es un *multipágina* en Streamlit con **siete** modelos.  
Usa el menú lateral (☰) o la lista de páginas (arriba a la izquierda) para navegar.  
Cada página tiene su propia barra lateral con parámetros.

### Modelos incluidos
- **Monopolio**: demanda lineal `P(Q)=a−bQ`; áreas **CS**, **π** y **DWL**; gráfico de **ingreso total** con regiones *inelástica* / *elástica*.
- **Duopolio de Cournot**: cantidades simultáneas; precio, **CS**, **∑π**, **DWL** y pie de **cuotas**.
- **Duopolio de Bertrand homogéneo**: competencia en **precios** con costos **c₁, c₂** (posiblemente asimétricos); bienestar y **funciones de reacción** (**RF₁**, **RF₂**).
- **Oligopolio de Cournot (asim.)**: **N** firmas con costos heterogéneos; precio, **CS**, **∑π**, **DWL** y **cuotas**.
- **Hotelling lineal**: precios entregados **p₁+tx** y **p₂+t(1−x)**; punto indiferente **x̂**; límites **a** y **1−b**; **CS** agregado y **mapa de precios**.
- **Duopolio de Stackelberg**: líder–seguidor (cantidades secuenciales) y comparación con Cournot.
- **Colusión Cournot**: regla de gatillo y comparación de bienestar frente a Cournot no cooperativo.

**Tip**: si aparecen `Q=0` o áreas nulas, revisa que **a > c** (o **a > p**) y que los parámetros sean consistentes.
        """
    )

# --- Definir páginas del multipágina con títulos personalizados ---
home       = st.Page(instrucciones, title="Instrucciones:")
monopolio = st.Page("pages/0_Monopolio.py",                         title="Monopolio")
cournot    = st.Page("pages/1_Duopolio_de_Cournot.py",              title="Duopolio de Cournot")
oligo_asim = st.Page("pages/5_Oligopolio_Cournot_Asimetrico.py",    title="Oligopolio de Cournot")
stack      = st.Page("pages/2_Stackelberg_Duopolio.py",             title="Duopolio de Stackelberg")
hotelling  = st.Page("pages/4_Hotelling_Lineal.py",                 title="Hotelling lineal")
colusion   = st.Page("pages/3_Colusion.py",                         title="Colusión Cournot")
bertrand   = st.Page("pages/7_Bertrand_Homogeneo.py",               title="Duopolio de Bertrand homogéneo")

# --- Router ---
st.navigation([home, monopolio, cournot, bertrand, oligo_asim, hotelling, stack, colusion]).run()
