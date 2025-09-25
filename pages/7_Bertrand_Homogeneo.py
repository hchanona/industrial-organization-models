# pages/7_Bertrand_Homogeneo.py
import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

st.title("Bertrand homogéneo (precios)")
st.caption("Demanda P(Q)=a−bQ. Productos idénticos. Costos marginales cᵢ heterogéneos. "
           "Comparamos con Cournot y variamos la asimetría de costos.")

# -----------------------
# Parámetros
# -----------------------
col1, col2 = st.columns(2)
a = col1.number_input("a (intercepto de demanda)", min_value=0.0, value=20.0, step=0.5, format="%.2f")
b = col2.number_input("b (pendiente de demanda >0)", min_value=0.01, value=1.0, step=0.01, format="%.2f")

costs_txt = st.text_input("Costos marginales cᵢ (separados por comas)", value="6, 7.5, 9, 11")
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

regla = st.selectbox(
    "Regla de precio en Bertrand",
    ["Docente simple: p = min cᵢ", "Heterogéneo exacto: p = segundo menor costo"],
    index=1
)

# -----------------------
# Funciones de equilibrio
# -----------------------
def demand_Q(a, b, p):
    return max((a - p) / b, 0.0)

def welfare_pc(a, b, cmin):
    """Bienestar con competencia perfecta (P=cmin)."""
    if a <= cmin:
        return 0.0, 0.0, 0.0  # Qpc=0, TS=0
    Qpc = (a - cmin) / b
    TSpc = 0.5 * (a - cmin) * Qpc  # con CMg constante, PS competitivo = 0
    return Qpc, TSpc, cmin

def bertrand_price_and_alloc(a, b, c_vec, rule="second"):
    """Devuelve p*, Q, q_i, π_i bajo Bertrand homogéneo con c_i heterogéneos.
       rule ∈ {"min", "second"}.
    """
    n = len(c_vec)
    idx_sorted = np.argsort(c_vec)
    c_sorted = c_vec[idx_sorted]
    cmin = c_sorted[0]
    p = cmin if (rule == "min" or n < 2) else c_sorted[1]

    Q = demand_Q(a, b, p)
    q = np.zeros(n)

    # ¿quién atiende?
    winners = np.where(c_vec == cmin)[0]  # los de menor costo
    if Q > 0:
        q_share = Q / len(winners)
        q[winners] = q_share

    pi = (p - c_vec) * q  # (p - c_i) * q_i (los no activos tienen q=0)
    # Bienestar
    CS = 0.5 * Q * (a - p)
    PS = float(np.sum(pi))
    Qpc, TSpc, _ = welfare_pc(a, b, cmin)
    TS = CS + PS
    DWL = max(TSpc - TS, 0.0)
    return p, Q, q, pi, CS, PS, TS, DWL

def cournot_asim(a, b, c_list):
    """Cournot con costos asimétricos (misma fórmula que venimos usando)."""
    c = np.array(c_list, dtype=float)
    n_all = len(c)
    active = list(range(n_all))
    while True:
        N = len(active)
        if N == 0:
            q = np.zeros(n_all); P = a; pi = np.zeros(n_all)
            return q, P, 0.0, pi
        cA = c[active]
        if N == 1:
            qA = np.array([(a - cA[0])/(2*b)])
        else:
            sum_c = float(np.sum(cA))
            cbar_m = (sum_c - cA) / (N - 1)  # \bar c_{-i}
            qA = (a + N*(cbar_m - cA) - cbar_m) / (b*(N + 1))
        keep = qA > 1e-12
        if np.all(keep):
            q = np.zeros(n_all)
            for pos, idx in enumerate(active): q[idx] = qA[pos]
            Q = float(np.sum(qA))
            P = float(a - b*Q)
            pi = (P - c) * q
            return q, P, Q, pi
        active = [idx for k, idx in zip(keep, active) if k]

def metrics_cournot(a, b, q, P, c):
    Q = float(np.sum(q))
    CS = 0.5 * Q * (a - P)
    PS = float(np.sum((P - c) * q))
    cmin = float(np.min(c))
    Qpc, TSpc, _ = welfare_pc(a, b, cmin)
    TS = CS + PS
    DWL = max(TSpc - TS, 0.0)
    return CS, PS, TS, DWL

# -----------------------
# Barrido vs asimetría de costos τ∈[0,1]
# -----------------------
c_sorted0 = np.sort(costs)
cmin0 = float(np.min(costs))

def interpolate_costs(tau):
    """c(τ)=c_min + τ*(c0 - c_min): τ=0 (simétrico en c_min), τ=1 (original)."""
    return cmin0 + tau * (c_sorted0 - cmin0)

grid_pts = 25
tau_grid = np.linspace(0.0, 1.0, grid_pts)

rows = []
for tau in tau_grid:
    c_tau = interpolate_costs(tau)
    # Bertrand
    rule_key = "second" if regla.startswith("Heterogéneo") else "min"
    pB, QB, qB, piB, CSB, PSB, TSB, DWLB = bertrand_price_and_alloc(a, b, c_tau, rule=rule_key)
    # Cournot
    qC, PC, QC, piC = cournot_asim(a, b, c_tau)
    CSC, PSC, TSC, DWLC = metrics_cournot(a, b, qC, PC, c_tau)
    rows.append((tau, pB, CSB, np.sum(piB), DWLB, PC, CSC, np.sum(piC), DWLC))

arr = np.array(rows)
taus = arr[:,0]
P_B, CS_B, PI_B, DWL_B = arr[:,1], arr[:,2], arr[:,3], arr[:,4]
P_C, CS_C, PI_C, DWL_C = arr[:,5], arr[:,6], arr[:,7], arr[:,8]

# -----------------------
# Gráficas vs asimetría (Bertrand vs Cournot)
# -----------------------
c1, c2 = st.columns(2)

def plot_vs_tau(yB, yC, ylabel, title):
    fig, ax = plt.subplots()
    ax.plot(taus, yB, label="Bertrand")
    ax.plot(taus, yC, label="Cournot")
    ax.set_xlabel("Asimetría de costos (τ)")
    ax.set_ylabel(ylabel)
    ax.set_title(title)
    ax.legend()
    st.pyplot(fig, clear_figure=True)

with c1:
    plot_vs_tau(P_B, P_C, "Precio", "Precio vs asimetría (τ)")
with c2:
    plot_vs_tau(CS_B, CS_C, "Excedente del consumidor", "CS vs asimetría (τ)")
with c1:
    plot_vs_tau(PI_B, PI_C, "Ganancias totales (∑π)", "Ganancias vs asimetría (τ)")
with c2:
    plot_vs_tau(DWL_B, DWL_C, "DWL", "Pérdida de peso muerto vs asimetría (τ)")

st.divider()

# -----------------------
# Detalle para τ elegido: métricas y barras de márgenes (Bertrand)
# -----------------------
tau_det = st.slider("Asimetría para el detalle (τ)", 0.0, 1.0, 1.0, step=0.01)
c_tau = interpolate_costs(tau_det)
rule_key = "second" if regla.startswith("Heterogéneo") else "min"

pB, QB, qB, piB, CSB, PSB, TSB, DWLB = bertrand_price_and_alloc(a, b, c_tau, rule=rule_key)
qC, PC, QC, piC = cournot_asim(a, b, c_tau)
CSC, PSC, TSC, DWLC = metrics_cournot(a, b, qC, PC, c_tau)

m1, m2, m3, m4 = st.columns(4)
m1.metric("Precio (Bertrand)", f"{pB:.2f}")
m2.metric("CS (Bertrand)", f"{CSB:.2f}")
m3.metric("∑π (Bertrand)", f"{np.sum(piB):.2f}")
m4.metric("DWL (Bertrand)", f"{DWLB:.2f}")

n1, n2, n3, n4 = st.columns(4)
n1.metric("Precio (Cournot)", f"{PC:.2f}")
n2.metric("CS (Cournot)", f"{CSC:.2f}")
n3.metric("∑π (Cournot)", f"{np.sum(piC):.2f}")
n4.metric("DWL (Cournot)", f"{DWLC:.2f}")

# Barras de márgenes por firma (Bertrand, τ_det)
margenes = np.maximum(pB - c_tau, 0.0)   # margen por unidad de los que venden
labels = [f"F{i+1}\n(c={c_tau[i]:.2f})" for i in range(len(c_tau))]

fig_bar, ax_bar = plt.subplots()
ax_bar.bar(labels, margenes)
ax_bar.set_ylabel("Margen por unidad (max(p−cᵢ,0))")
ax_bar.set_title("Márgenes por firma (Bertrand, τ seleccionado)")
st.pyplot(fig_bar, clear_figure=True)

# Tabla de detalle
df = pd.DataFrame({
    "cᵢ": c_tau,
    "qᵢ Bertrand": qB,
    "πᵢ Bertrand": piB,
    "qᵢ Cournot": qC,
    "πᵢ Cournot": piC
})
st.dataframe(df.style.format({"cᵢ":"{:.2f}", "qᵢ Bertrand":"{:.3f}", "πᵢ Bertrand":"{:.2f}",
                              "qᵢ Cournot":"{:.3f}", "πᵢ Cournot":"{:.2f}"}),
             use_container_width=True)

with st.expander("Notas rápidas (reacción “undercut”)"):
    st.markdown(
        """
- Con productos **idénticos** y costos **constantes**, cualquier firma que cobre por encima del costo de un rival **puede ser subcotizada** (undercut) y perder toda la demanda.
- Si los costos son **iguales**, el equilibrio es **p = c** (como competencia perfecta).
- Con costos **distintos**, en el modelo exacto el precio de equilibrio es el **segundo menor costo** y **vende**(n) la(s) firma(s) de costo mínimo.
- Aquí puedes alternar entre la regla **docente** (*p = min cᵢ*) y la versión **exacta** (*p = segundo menor*).
        """
    )

