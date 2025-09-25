# pages/5_Oligopolio_Cournot_Asimetrico.py
import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

st.title("Oligopolio de Cournot — costos asimétricos")
st.caption("Demanda P(Q)=a−bQ. Cada firma i tiene costo marginal cᵢ (constante). No simétrico.")

# -----------------------
# Parámetros
# -----------------------
col1, col2 = st.columns(2)
a = col1.number_input("Intersección de demanda (a)", min_value=0.0, value=20.0, step=0.5, format="%.2f")
b = col2.number_input("Pendiente de demanda (b>0)", min_value=0.01, value=1.0, step=0.01, format="%.2f")

costs_txt = st.text_input(
    "Costos marginales cᵢ (separados por comas, p.ej. 4, 6, 7.5, 9)",
    value="6, 7.5, 9, 11"
)
# parseo robusto
costs = []
for t in costs_txt.split(","):
    t = t.strip()
    if t:
        try:
            costs.append(float(t))
        except ValueError:
            pass
costs = np.array(costs, dtype=float)
if costs.size == 0:
    st.stop()

# -----------------------
# Equilibrio con tu fórmula (c̄_{-i})
# -----------------------
def cournot_asim(a, b, c_list):
    """
    Equilibrio de Cournot con P(Q)=a-bQ y costos c_i heterogéneos.
    Usa explícitamente:
        q_i = [ a + N*(c̄_{-i} - c_i) - c̄_{-i} ] / [ b*(N+1) ],
    con  c̄_{-i} = (1/(N-1)) * sum_{j≠i} c_j  y  N = |S| (firmas activas).
    Elimina iterativamente firmas con q_i<=0 y recalcula.
    Para N=1: q = (a - c_1)/(2b).
    Retorna: q (con ceros en inactivas), P, Q, π.
    """
    c = np.array(c_list, dtype=float)
    n_all = len(c)
    active_idx = list(range(n_all))

    while True:
        N = len(active_idx)
        if N == 0:
            q = np.zeros(n_all); P = a; pi = np.zeros(n_all)
            return q, P, 0.0, pi

        c_act = c[active_idx]
        if N == 1:
            q_act = np.array([(a - c_act[0])/(2*b)])
        else:
            sum_c = float(np.sum(c_act))
            cbar_minus = (sum_c - c_act) / (N - 1)        # promedio de los otros
            q_act = (a + N*(cbar_minus - c_act) - cbar_minus) / (b*(N + 1))

        # Mantener solo q_i>0
        mask_pos = q_act > 1e-12
        if np.all(mask_pos):
            q = np.zeros(n_all)
            for pos, idx in enumerate(active_idx):
                q[idx] = q_act[pos]
            Q = float(np.sum(q_act))
            P = float(a - b*Q)
            pi = np.zeros(n_all)
            for idx in active_idx:
                pi[idx] = (P - c[idx]) * q[idx]
            return q, P, Q, pi
        else:
            active_idx = [idx for keep, idx in zip(mask_pos, active_idx) if keep]

def welfare_metrics(a, b, q, P, costs):
    Q = float(np.sum(q))
    CS = 0.5 * Q * (a - P)                      # lineal
    PS = float(np.sum((P - costs) * q))
    cmin = float(np.min(costs))
    if a <= cmin:
        TS_pc = 0.0
    else:
        Q_pc = (a - cmin) / b
        TS_pc = 0.5 * (a - cmin) * Q_pc         # PS competitivo = 0 con CMg constante
    TS = CS + PS
    DWL = max(TS_pc - TS, 0.0)
    return CS, PS, TS, DWL

# -----------------------------------------
# Comparativas: variar número de firmas k
# -----------------------------------------
c_sorted = np.sort(costs)
K = len(c_sorted)
k_for_detail = st.slider("Número de firmas activas para el detalle (k)", 1, K, K, step=1)

rows = []
for k in range(1, K + 1):
    c_k = c_sorted[:k]
    q_k, P_k, Q_k, pi_k = cournot_asim(a, b, c_k)
    CS_k, PS_k, TS_k, DWL_k = welfare_metrics(a, b, q_k, P_k, c_k)
    rows.append((k, P_k, CS_k, np.sum(pi_k), DWL_k))

arr = np.array(rows)
k_grid, P_grid, CS_grid, PI_grid, DWL_grid = arr.T

# -----------------------
# Gráficas: P, CS, ∑π, DWL
# -----------------------
c1, c2 = st.columns(2)

figP, axP = plt.subplots()
axP.plot(k_grid, P_grid, marker="o")
axP.set_xlabel("Número de firmas activas (k)")
axP.set_ylabel("Precio P")
axP.set_title("Precio vs número de firmas")
c1.pyplot(figP, clear_figure=True)

figCS, axCS = plt.subplots()
axCS.plot(k_grid, CS_grid, marker="o")
axCS.set_xlabel("Número de firmas activas (k)")
axCS.set_ylabel("Excedente del consumidor")
axCS.set_title("Excedente del consumidor vs k")
c2.pyplot(figCS, clear_figure=True)

figPI, axPI = plt.subplots()
axPI.plot(k_grid, PI_grid, marker="o")
axPI.set_xlabel("Número de firmas activas (k)")
axPI.set_ylabel("Ganancias totales (∑π)")
axPI.set_title("Ganancias de las empresas vs k")
c1.pyplot(figPI, clear_figure=True)

figDWL, axDWL = plt.subplots()
axDWL.plot(k_grid, DWL_grid, marker="o")
axDWL.set_xlabel("Número de firmas activas (k)")
axDWL.set_ylabel("Pérdida de peso muerto (DWL)")
axDWL.set_title("DWL vs k (óptimo: P=c_min)")
c2.pyplot(figDWL, clear_figure=True)

st.divider()

# -----------------------
# Detalle del escenario seleccionado (k_for_detail)
# -----------------------
st.subheader("Detalle del escenario seleccionado")
c_k = c_sorted[:k_for_detail]
q_k, P_k, Q_k, pi_k = cournot_asim(a, b, c_k)
CS_k, PS_k, TS_k, DWL_k = welfare_metrics(a, b, q_k, P_k, c_k)

m1, m2, m3, m4 = st.columns(4)
m1.metric("Precio P", f"{P_k:.2f}")
m2.metric("Cantidad total Q", f"{Q_k:.2f}")
m3.metric("CS", f"{CS_k:.2f}")
m4.metric("DWL", f"{DWL_k:.2f}")

# Pie de participaciones de mercado (por cantidades)
shares = (q_k / q_k.sum()) if q_k.sum() > 0 else np.zeros_like(q_k)
labels = [f"Firma {i+1} (c={c_k[i]:.2f})" for i in range(len(c_k))]

figPie, axPie = plt.subplots()
axPie.pie(shares, labels=labels, autopct=lambda p: f"{p:.1f}%" if p > 0 else "")
axPie.set_title("Participaciones de mercado (por cantidad)")
st.pyplot(figPie, clear_figure=True)

# Tabla de detalle
df = pd.DataFrame({
    "costo cᵢ": c_k,
    "qᵢ": q_k,
    "participación (qᵢ/Q)": shares,
    "πᵢ": pi_k
})
st.dataframe(
    df.style.format({"costo cᵢ":"{:.2f}", "qᵢ":"{:.3f}", "participación (qᵢ/Q)":"{:.2%}", "πᵢ":"{:.2f}"}),
    use_container_width=True
)

with st.expander("Fórmulas usadas"):
    st.markdown(
        r"""
- **Cerrada con costos asimétricos y \(N\) firmas activas**:  
  \[
  q_i=\frac{a+N(\bar c_{-i}-c_i)-\bar c_{-i}}{b(N+1)},\qquad
  \bar c_{-i}=\frac{1}{N-1}\sum_{j\ne i} c_j.
  \]
  Si \(q_i\le0\), la firma sale del conjunto activo y se recalcula.
- **Precio**: \( P = a - bQ \).  
- **CS**: \( \tfrac{1}{2}Q(a-P) \).  
- **Ganancia i**: \( \pi_i = (P-c_i)q_i \).  
- **Óptimo competitivo**: \( P=c_{\min}\Rightarrow Q^{pc}=\frac{a-c_{\min}}{b}\) (si \(a>c_{\min}\)).  
- **DWL**: \( \text{DWL} = TS^{pc} - (CS + \sum_i \pi_i)\).
        """
    )
