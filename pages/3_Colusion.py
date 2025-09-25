# pages/3_Colusion.py
import streamlit as st
import numpy as np
import matplotlib.pyplot as plt

st.title("Colusión (gatillo) desde Cournot — simple")

with st.sidebar:
    st.header("Demanda")
    a = st.number_input("Intercepto a", value=100.0, step=1.0, min_value=0.0, format="%.2f")
    b = st.number_input("Pendiente b (>0)", value=1.0, step=0.1, min_value=0.0001, format="%.4f")

    st.header("Mercado")
    N = st.number_input("Número de firmas N", value=2, min_value=2, max_value=20, step=1)

    st.subheader("Costos marginales por firma")
    cs = []
    default_c = 20.0
    for i in range(int(N)):
        cs.append(st.number_input(f"c{i+1}", value=default_c, step=1.0, min_value=0.0, format="%.2f", key=f"c{i+1}"))

# ---------- Cournot (N asimétrico) ----------
cs_arr = np.array(cs, dtype=float)
S = cs_arr.sum()
qN = (a - (N+1)*cs_arr + S) / ((N+1)*b)           # puede dar negativos si no hay interior
qN = np.maximum(qN, 0.0)
QN = qN.sum()
PN = a - b*QN
piN = np.maximum(PN - cs_arr, 0.0) * qN

# ---------- Cartel simple: reparto igual de cantidades ----------
cbar = S / N
QC = max((a - cbar) / (2*b), 0.0)
PC = a - b*QC
qC = np.array([QC / N] * int(N))
piC = np.maximum(PC - cs_arr, 0.0) * qC

# ---------- Desviación uniperiodo de i contra cartel (los demás cumplen) ----------
Q_others_C = QC * (N - 1) / N
qD = np.maximum((a - cs_arr - b * Q_others_C) / (2*b), 0.0)
PD = a - b * (qD + Q_others_C)
piD = np.maximum(PD - cs_arr, 0.0) * qD

# ---------- Umbrales delta_i* y delta* ----------
# Evitar divisiones raras: si denom <= 0, ponemos delta_i*=1 (no se puede sostener con gatillo)
den = (piD - piN)
num = (piD - piC)
delta_i = np.where(den > 1e-12, num / den, 1.0)
# recorte a [0, 1.0] para presentación
delta_i = np.clip(delta_i, 0.0, 1.0)
delta_star = float(np.max(delta_i)) if int(N) > 0 else 1.0

# ---------- UI: métricas ----------
c1, c2, c3, c4 = st.columns(4)
c1.metric("δ* (umbral cartel)", f"{delta_star:.2f}")
c2.metric("Qᴺ", f"{QN:.2f}")
c3.metric("Pᴺ", f"{PN:.2f}")
c4.metric("Qᶜ", f"{QC:.2f}")

st.caption("Regla: la colusión con gatillo es sostenible si δ ≥ δ*. (Castigo = Cournot para siempre).")

# ---------- Tabla por firma ----------
import pandas as pd
df = pd.DataFrame({
    "Firma": [f"i={i+1}" for i in range(int(N))],
    "c_i": np.round(cs_arr, 2),
    "q_i^N": np.round(qN, 2),
    "π_i^N": np.round(piN, 2),
    "q_i^C": np.round(qC, 2),
    "π_i^C": np.round(piC, 2),
    "q_i^D": np.round(qD, 2),
    "π_i^D": np.round(piD, 2),
    "δ_i*": np.round(delta_i, 2),
})
st.dataframe(df, use_container_width=True)
