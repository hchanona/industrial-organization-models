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
# Equilibrio "docente"
# -----------------------
c_min, c_max = min(c1, c2), max(c1, c2)
p_star = c_max if not np.isclose(c1, c2) else c_min
Q_star = max((a - p_star) / b, 0.0)

if np.isclose(c1, c2):
    q1 = q2 = Q_star / 2.0
    winner = "Empate: ambas venden (p* = c₁ = c₂)."
elif c1 < c2:
    q1, q2, winner = Q_star, 0.0, "Vende la firma 1 (c₁ < c₂)."
else:
    q1, q2, winner = 0.0, Q_star, "Vende la firma 2 (c₂ < c₁)."

pi1 = (p_star - c1) * q1
pi2 = (p_star - c2) * q2
PI  = pi1 + pi2
CS  = 0.5 * Q_star * (a - p_star)
TS  = CS + PI

# Benchmark competitivo (P=c_min)
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
st.info(winner)
if Q_star <= 0:
    st.warning("A este precio de equilibrio, la demanda es nula (Q*=0).")

# -----------------------
# Gráficos (arriba: izquierda demanda; derecha mejores respuestas)
# -----------------------
left, right = st.columns(2)

# (A) Demanda inversa con CS, π y DWL (izquierda)
Q_int = a / b if b > 0 else 0.0
Qmax_plot = max(Q_int, Q_pc, Q_star)
Q = np.linspace(0, max(Qmax_plot, 1e-9), 400)
P_d = a - b * Q

figA, axA = plt.subplots()
axA.plot(Q, P_d, label="Demanda inversa P(Q)=a−bQ")
axA.hlines(p_star, 0, max(Q_star, Q_pc), linestyles="--", label="p* (Bertrand)")
axA.hlines(c_min,  0, max(Q_star, Q_pc), linestyles=":",  label="c_min (competencia)")
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

# (B) Mejores respuestas (derecha) con separación interna ε
p1_max = (a + c1) / 2.0
p2_max = (a + c2) / 2.0
p_lo   = 0.0
p_hi   = max(a, p1_max, p2_max, c1, c2, p_star) * 1.05

# ε interno: pequeño y proporcional al rango de la figura
eps = max(0.02 * (p_hi - p_lo), 0.1)   # 2% del rango, mínimo 0.1

figC, axC = plt.subplots()

# RF1: vertical en x=c1 hasta y=c1
axC.plot([c1, c1], [p_lo, c1], color="#1f77b4", linewidth=3, label="RF₁: p₁*(p₂)")

# RF1: tramo “diagonal” con undercut estricto: y = x + ε, hasta justo antes de (p*,p*)
x1_start = c1
x1_end_theoretical = p1_max - eps
x1_end = min(x1_end_theoretical, p_star - 1e-9)
if x1_end > x1_start:
    x_mid = np.linspace(x1_start, x1_end, 200)
    y_mid = x_mid + eps
    axC.plot(x_mid, y_mid, color="#1f77b4", linewidth=3)

# RF1: vertical en x=p1_max desde y=p1_max
axC.plot([p1_max, p1_max], [p1_max, p_hi], color="#1f77b4", linewidth=3)

# RF2: horizontal en y=c2 hasta x=c2
axC.plot([p_lo, c2], [c2, c2], color="#2ca02c", linewidth=3, label="RF₂: p₂*(p₁)")

# RF2: tramo “diagonal” con undercut estricto: y = x − ε
x2_start = c2 + eps
x2_end_theoretical = p2_max
x2_end = min(x2_end_theoretical, p_star - 1e-9)
if x2_end > x2_start:
    x_mid2 = np.linspace(x2_start, x2_end, 200)
    y_mid2 = x_mid2 - eps
    axC.plot(x_mid2, y_mid2, color="#2ca02c", linewidth=3)

# RF2: horizontal en y=p2_max desde x=p2_max
axC.plot([p2_max, p_hi], [p2_max, p2_max], color="#2ca02c", linewidth=3)

# Referencias y punto (p*,p*)
axC.plot([p_lo, p_hi], [p_lo, p_hi], linestyle="--", color="gray", linewidth=1)  # diagonal
axC.axvline(p1_max, linestyle=":", color="#1f77b4", linewidth=1)
axC.axhline(p2_max, linestyle=":", color="#2ca02c", linewidth=1)
axC.axvline(c1,     linestyle="-", color="#1f77b4", linewidth=2, alpha=0.25)
axC.axhline(c2,     linestyle="-", color="#2ca02c", linewidth=2, alpha=0.25)

# Equilibrio: ambas RF pasan por (p*,p*)
axC.scatter([p_star], [p_star], marker="x", s=80, color="black", zorder=5)
axC.annotate("  (p*, p*)", (p_star, p_star), va="center")

axC.set_xlim(p_lo, p_hi)
axC.set_ylim(p_lo, p_hi)
axC.set_xlabel("Precio p₁")
axC.set_ylabel("Precio p₂")
axC.set_title("Funciones de reacción en precios (duopolio Bertrand)")
axC.legend(loc="lower right")
right.pyplot(figC, clear_figure=True)

# -----------------------
# Notas
# -----------------------
with st.expander("Notas / reacción 'undercut'"):
    st.markdown(
        r"""
- En el tramo intermedio, la mejor respuesta es **estricta**: 1 responde con \(p_1 \approx p_2-\varepsilon\) y 2 con \(p_2 \approx p_1-\varepsilon\).
- Por eso las curvas quedan **paralelas** a la diagonal (separadas por \(\varepsilon\)) y **solo coinciden** con la diagonal en el **equilibrio** \((p^*,p^*)\).
- \(p_i^{\max}=\frac{a+c_i}{2}\) y los otros tramos permanecen verticales/horizontales en \(MC_i\) y \(p_i^{\max}\).
        """
    )


