# pages/0_Monopolio.py
import streamlit as st
import numpy as np
import matplotlib.pyplot as plt

st.title("Monopolio (P(Q)=a − bQ, costo marginal c)")
st.caption("Gráfico con CS, ganancias y pérdida de peso muerto; y al lado MR(Q) mostrando Q* con MR=MC.")

# -----------------------
# Parámetros
# -----------------------
col1, col2, col3 = st.columns(3)
a = col1.number_input("a (intercepto de demanda)", min_value=0.0, value=20.0, step=0.5, format="%.2f")
b = col2.number_input("b (pendiente de demanda >0)", min_value=0.01, value=1.0, step=0.01, format="%.2f")
c = col3.number_input("c (costo marginal)", min_value=0.0, value=6.0, step=0.25, format="%.2f")

# -----------------------
# Cálculos básicos
# -----------------------
Q_int = a / b                                # intersección de demanda con eje Q
Q_pc  = max(0.0, (a - c) / b) if a > c else 0.0      # óptimo competitivo: P=MC=c
Q_m   = max(0.0, (a - c) / (2*b)) if a > c else 0.0  # monopolio: MR=a-2bQ=c
P_m   = a - b*Q_m
P_pc  = c

# Áreas
CS_m  = 0.5 * Q_m * (a - P_m)                        # triángulo bajo demanda y sobre P_m
Pi_m  = (P_m - c) * Q_m                              # rectángulo (P_m - c) * Q_m
DWL   = 0.5 * max(Q_pc - Q_m, 0.0) * max(P_m - c, 0.0)   # triángulo entre demanda y MC en [Q_m,Q_pc]

# Para la grilla
Q = np.linspace(0, Q_int, 400)
P_d = a - b*Q                    # demanda inversa
MR  = a - 2*b*Q                  # ingreso marginal
MC  = np.full_like(Q, c)         # costo marginal (constante)

# -----------------------
# Métricas
# -----------------------
m1, m2, m3, m4 = st.columns(4)
m1.metric("Q* monopolio", f"{Q_m:.2f}")
m2.metric("P* monopolio", f"{P_m:.2f}")
m3.metric("CS (monopolio)", f"{CS_m:.2f}")
m4.metric("DWL", f"{DWL:.2f}")

# -----------------------
# Gráficos
# -----------------------
left, right = st.columns(2)

# (A) Diagrama con áreas: demanda, MR y MC
figA, axA = plt.subplots()

# Curvas
axA.plot(Q, P_d, label="Demanda inversa")
axA.plot(Q, MR,  label="Ingreso marginal (MR)")
axA.hlines(c, 0, Q_int, label="Costo marginal (MC)", linestyles="--")

# Sombreado: CS (0→Qm entre demanda y Pm)
if Q_m > 0:
    Q_cs = np.linspace(0, Q_m, 200)
    axA.fill_between(Q_cs, a - b*Q_cs, P_m, alpha=0.25, label="Excedente del consumidor")

# Sombreado: Ganancia del monopolio (rectángulo entre c y Pm, 0→Qm)
if P_m > c and Q_m > 0:
    axA.fill_between([0, Q_m], [c, c], [P_m, P_m], alpha=0.25, label="Ganancias del monopolio")

# Sombreado: DWL (Qm→Qpc entre demanda y c)
if Q_pc > Q_m:
    Q_dwl = np.linspace(Q_m, Q_pc, 200)
    axA.fill_between(Q_dwl, a - b*Q_dwl, c, alpha=0.25, label="Pérdida de peso muerto")

# Guias en Qm y Qpc
axA.axvline(Q_m, linestyle=":", linewidth=1)
axA.axvline(Q_pc, linestyle=":", linewidth=1)
axA.text(Q_m, P_m, "  Q*", va="bottom")
if Q_pc > 0:
    axA.text(Q_pc, c,  "  Q_pc", va="bottom")

axA.set_xlim(0, Q_int)
axA.set_ylim(0, max(a, P_m, c)*1.05)
axA.set_xlabel("Cantidad Q")
axA.set_ylabel("Precio / Costo")
axA.set_title("Monopolio: CS, π y DWL")
axA.legend(loc="best")
left.pyplot(figA, clear_figure=True)

# (B) MR(Q) y condición de máximo (MR=MC)
figB, axB = plt.subplots()
axB.plot(Q, MR, label="MR(Q)")
axB.hlines(c, 0, Q_int, linestyles="--", label="MC=c")
axB.axvline(Q_m, linestyle=":", label="Q* (MR=MC)")
axB.set_xlim(0, Q_int)
axB.set_xlabel("Cantidad Q")
axB.set_ylabel("Ingreso marginal / Costo")
axB.set_title("Ingreso marginal y regla MR = MC")
axB.legend(loc="best")
right.pyplot(figB, clear_figure=True)

with st.expander("Fórmulas"):
    st.markdown(
        r"""
- Demanda inversa: \(P(Q)=a-bQ\).  
- Ingreso marginal: \(MR(Q)=a-2bQ\).  
- Óptimo de monopolio: \(MR(Q^*)=MC=c \Rightarrow Q^*=\dfrac{a-c}{2b}\), \(P^*=a-bQ^*\) (si \(a>c\)).  
- Competencia perfecta: \(P=c \Rightarrow Q^{pc}=\dfrac{a-c}{b}\) (si \(a>c\)).  
- Excedente del consumidor (monopolio): \(CS=\tfrac{1}{2}Q^*(a-P^*)\).  
- Ganancia del monopolio: \(\pi=(P^*-c)Q^*\).  
- Pérdida de peso muerto: triángulo entre demanda y \(MC\) en \([Q^*,Q^{pc}]\):  
  \(\mathrm{DWL}=\tfrac{1}{2}(Q^{pc}-Q^*)(P^*-c)\).
        """
    )
