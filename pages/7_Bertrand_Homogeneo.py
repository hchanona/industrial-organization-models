# pages/7_Bertrand_Homogeneo.py
import streamlit as st
import numpy as np
import matplotlib.pyplot as plt

st.title("Duopolio de Bertrand — producto homogéneo")
st.caption(
    "Demanda P(Q)=a−bQ. Costos marginales c₁ y c₂ (posiblemente asimétricos). "
    "Regla didáctica: si c₁≠c₂, p* = max{c₁,c₂} y vende la firma de menor costo; "
    "si c₁=c₂, p* = c y se reparten la demanda."
)

# -----------------------
# Parámetros
# -----------------------
col1, col2, col3, col4 = st.columns(4)
a  = col1.number_input("a (intercepto demanda)", min_value=0.0, value=20.0, step=0.5, format="%.2f")
b  = col2.number_input("b (pendiente >0)", min_value=0.01, value=1.0, step=0.01, format="%.2f")
c1 = col3.number_input("c₁ (costo marginal 1)", min_value=0.0, value=6.0, step=0.25, format="%.2f")
c2 = col4.number_input("c₂ (costo marginal 2)", min_value=0.0, value=9.0, step=0.25, format="%.2f")

# -----------------------
# Cálculos de equilibrio (regla didáctica)
# -----------------------
c_min = min(c1, c2)
c_max = max(c1, c2)
p_star = c_max if not np.isclose(c1, c2) else c_min       # precio de equilibrio
Q_star = max((a - p_star) / b, 0.0)

if np.isclose(c1, c2):
    q1 = q2 = Q_star / 2.0
    winner = "Empate: ambas firmas venden (p* = c₁ = c₂)."
elif c1 < c2:
    q1, q2 = Q_star, 0.0
    winner = "Vende la firma 1 (c₁ < c₂)."
else:
    q1, q2 = 0.0, Q_star
    winner = "Vende la firma 2 (c₂ < c₁)."

pi1 = (p_star - c1) * q1
pi2 = (p_star - c2) * q2
PI  = pi1 + pi2
CS  = 0.5 * Q_star * (a - p_star)
TS  = CS + PI

# Benchmark competitivo (P = c_min)
if a > c_min:
    Q_pc = (a - c_min) / b
    TS_pc = 0.5 * (a - c_min) * Q_pc
else:
    Q_pc = 0.0
    TS_pc = 0.0
DWL = max(TS_pc - TS, 0.0)

# -----------------------
# Métricas
# -----------------------
m1, m2, m3, m4 = st.columns(4)
m1.metric("p* (Bertrand)", f"{p_star:.2f}")
m2.metric("Q*", f"{Q_star:.2f}")
m3.metric("CS", f"{CS:.2f}")
m4.metric("DWL", f"{DWL:.2f}")
n1, n2 = st.columns(2)
n1.metric("π₁", f"{pi1:.2f}")
n2.metric("π₂", f"{pi2:.2f}")
st.info(winner)
if Q_star <= 0:
    st.warning("A este precio de equilibrio, la demanda es nula (Q*=0).")

# -----------------------
# Gráfico 1: Demanda inversa con CS, π y DWL
# -----------------------
left, right = st.columns(2)

Q_int = a / b if b > 0 else 0.0
Qmax_plot = max(Q_int, Q_pc, Q_star)
Q = np.linspace(0, max(Qmax_plot, 1e-9), 400)
P_d = a - b * Q

figA, axA = plt.subplots()
axA.plot(Q, P_d, label="Demanda inversa P(Q)=a−bQ")
axA.hlines(p_star, 0, max(Q_star, Q_pc), linestyles="--", label="p* (Bertrand)")
axA.hlines(c_min,  0, max(Q_star, Q_pc), linestyles=":",  label="c_min (benchmark competitivo)")
axA.axvline(Q_star, linestyle=":", linewidth=1)
axA.axvline(Q_pc,   linestyle=":", linewidth=1)
if Q_star > 0:
    Q_cs = np.linspace(0, Q_star, 200)
    axA.fill_between(Q_cs, a - b*Q_cs, p_star, alpha=0.30, label="Excedente del consumidor")
if Q_star > 0 and p_star > c_min:
    axA.fill_between([0, Q_star], [c_min, c_min], [p_star, p_star], alpha=0.30, label="Ganancias del vendedor")
if Q_pc > Q_star:
    Q_dwl = np.linspace(Q_star, Q_pc, 200)
    axA.fill_between(Q_dwl, a - b*Q_dwl, c_min, alpha=0.25, label="Pérdida de peso muerto")
axA.set_xlim(0, max(Qmax_plot, 1e-9)*1.02)
axA.set_ylim(0, max(a, p_star, c_min)*1.05)
axA.set_xlabel("Cantidad Q")
axA.set_ylabel("Precio / Costo")
axA.set_title("Bertrand (duopolio): CS, π y DWL")
axA.legend(loc="best")
left.pyplot(figA, clear_figure=True)

# -----------------------
# Gráfico 2: Barras de ganancias por firma
# -----------------------
figB, axB = plt.subplots()
axB.bar(["Firma 1", "Firma 2"], [pi1, pi2])
axB.set_ylabel("Ganancia πᵢ")
axB.set_title("Ganancias por firma")
right.pyplot(figB, clear_figure=True)

# -----------------------
# Gráfico 3: Funciones de reacción (mejores respuestas)
# -----------------------
st.subheader("Mejores respuestas (funciones de reacción)")
# Precios 'monopolio' con mercado entero para cada firma (máx. de su propio π)
p1_max = (a + c1) / 2.0
p2_max = (a + c2) / 2.0

# Dominio de la figura
p_lo = 0.0
p_hi = max(a, p1_max, p2_max, c1, c2, p_star) * 1.05

# RF1: p1*(p2)
p2_vals = np.linspace(p_lo, p_hi, 600)
def rf1(p2):
    if p2 <= c1:          # rival muy barato -> no vale la pena bajar de costo
        return c1
    elif p2 < p1_max:     # subcotiza (en el límite p1≈p2)
        return p2
    else:                 # rival muy caro -> mejor su precio monopolio
        return p1_max
p1_star_vals = np.array([rf1(p2) for p2 in p2_vals])

# RF2: p2*(p1)
p1_vals = np.linspace(p_lo, p_hi, 600)
def rf2(p1):
    if p1 <= c2:
        return c2
    elif p1 < p2_max:
        return p1
    else:
        return p2_max
p2_star_vals = np.array([rf2(p1) for p1 in p1_vals])

figC, axC = plt.subplots()
# RF1: (x=p1*(p2), y=p2)
axC.plot(p1_star_vals, p2_vals, color="#1f77b4", linewidth=2.5, label="RF₁: p₁*(p₂)")
# RF2: (x=p1, y=p2*(p1))
axC.plot(p1_vals, p2_star_vals, color="#2ca02c", linewidth=2.5, label="RF₂: p₂*(p₁)")

# Referencias: diagonal p1=p2, líneas en p1_max y p2_max
axC.plot([p_lo, p_hi], [p_lo, p_hi], linestyle="--", color="gray", linewidth=1)
axC.axvline(p1_max, linestyle=":", color="#1f77b4", linewidth=1)
axC.axhline(p2_max, linestyle=":", color="#2ca02c", linewidth=1)

# Equilibrio (p*,p*)
axC.scatter([p_star], [p_star], marker="x", s=80, color="k", zorder=5)
axC.annotate("  (p*, p*)", (p_star, p_star), va="center")

# Marcas de MC
axC.axvline(c1, linestyle="-", color="#1f77b4", linewidth=3, alpha=0.35)
axC.axhline(c2, linestyle="-", color="#2ca02c", linewidth=3, alpha=0.35)
axC.text(c1, p_lo + 0.02*(p_hi-p_lo), "MC₁", ha="center", va="bottom", color="#1f77b4")
axC.text(p_lo + 0.02*(p_hi-p_lo), c2, "MC₂", va="center", color="#2ca02c")

axC.set_xlim(p_lo, p_hi)
axC.set_ylim(p_lo, p_hi)
axC.set_xlabel("Precio p₁")
axC.set_ylabel("Precio p₂")
axC.set_title("Funciones de reacción en precios (duopolio Bertrand)")
axC.legend(loc="lower right", frameon=True)
st.pyplot(figC, clear_figure=True)

# -----------------------
# Notas
# -----------------------
with st.expander("Notas / reacción 'undercut'"):
    st.markdown(
        r"""
- **RF₁** (mejor respuesta de la firma 1):  
  \[
  p_1^*(p_2)=
  \begin{cases}
  c_1, & p_2\le c_1,\\
  p_2, & c_1<p_2<p_1^{\max},\\
  p_1^{\max}=\frac{a+c_1}{2}, & p_2\ge p_1^{\max}.
  \end{cases}
  \]
  Análogo para **RF₂** con \(c_2\) y \(p_2^{\max}=\frac{a+c_2}{2}\).
- La **intersección** típica es \((p^*,p^*)=(\max\{c_1,c_2\},\max\{c_1,c_2\})\) (con la regla didáctica).
- Si \(c_1=c_2\), \(p^*=c\) y cualquier punto sobre la diagonal **en** \(p=c\) con reparto de demanda es consistente.
        """
    )

