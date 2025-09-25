# pages/7_Bertrand_Duopolio_Homogeneo.py
import streamlit as st
import numpy as np
import matplotlib.pyplot as plt

st.title("Duopolio de Bertrand — producto homogéneo")
st.caption("Demanda P(Q)=a−bQ. Costos marginales c₁ y c₂ (posiblemente asimétricos). "
           "Regla didáctica: p* = max{c₁,c₂}; vende la firma de menor costo.")

# -----------------------
# Parámetros
# -----------------------
col1, col2, col3 = st.columns(3)
a  = col1.number_input("a (intercepto de demanda)", min_value=0.0, value=20.0, step=0.5, format="%.2f")
b  = col2.number_input("b (pendiente de demanda >0)", min_value=0.01, value=1.0, step=0.01, format="%.2f")
c1 = col3.number_input("c₁ (costo marginal firma 1)", min_value=0.0, value=6.0, step=0.25, format="%.2f")
c2 = col3.number_input("c₂ (costo marginal firma 2)", min_value=0.0, value=9.0, step=0.25, format="%.2f")

# -----------------------
# Cálculos
# -----------------------
c_min = min(c1, c2)
c_max = max(c1, c2)

# Precio de equilibrio (regla didáctica)
p_star = c_max if not np.isclose(c1, c2) else c_min

# Cantidad demandada a p*
Q_star = max((a - p_star) / b, 0.0)
# Asignación por firma
if np.isclose(c1, c2):
    q1 = q2 = Q_star / 2.0
    winner = "Empate: ambas firmas venden"
elif c1 < c2:
    q1, q2 = Q_star, 0.0
    winner = "Vende la firma 1 (c₁<c₂)"
else:
    q1, q2 = 0.0, Q_star
    winner = "Vende la firma 2 (c₂<c₁)"

# Ganancias
pi1 = (p_star - c1) * q1
pi2 = (p_star - c2) * q2
PI  = pi1 + pi2

# Bienestar con Bertrand
CS = 0.5 * Q_star * (a - p_star)  # triángulo bajo demanda y sobre p*
TS = CS + PI

# Benchmark competitivo (P = c_min)
if a > c_min:
    Q_pc = (a - c_min) / b
    TS_pc = 0.5 * (a - c_min) * Q_pc  # con CMg constante, PS competitivo = 0
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

# -----------------------
# Gráficos
# -----------------------
left, right = st.columns(2)

# (A) Demanda inversa con CS, π y DWL
Q_int = a / b if b > 0 else 0.0
Q = np.linspace(0, max(Q_int, Q_pc, Q_star), 400)
P_d = a - b * Q

figA, axA = plt.subplots()

# Curva de demanda
axA.plot(Q, P_d, label="Demanda inversa P(Q)=a−bQ")

# Líneas de referencia
axA.hlines(p_star, 0, max(Q_star, Q_pc), linestyles="--", label="p* (Bertrand)")
axA.hlines(c_min,  0, max(Q_star, Q_pc), linestyles=":",  label="c_min (benchmark competitivo)")
axA.axvline(Q_star, linestyles=":", linewidth=1)
axA.axvline(Q_pc,   linestyles=":", linewidth=1)

# Sombreado: CS (0→Q*, entre demanda y p*)
if Q_star > 0:
    Q_cs = np.linspace(0, Q_star, 200)
    axA.fill_between(Q_cs, a - b*Q_cs, p_star, alpha=0.30, label="Excedente del consumidor")

# Sombreado: Ganancia de la(s) firma(s) que venden (rectángulo entre c_del vendedor y p*)
if Q_star > 0 and p_star > c_min:
    axA.fill_between([0, Q_star], [c_min, c_min], [p_star, p_star], alpha=0.30, label="Ganancias del vendedor")

# Sombreado: DWL (Q*→Q_pc, entre demanda y c_min)
if Q_pc > Q_star:
    Q_dwl = np.linspace(Q_star, Q_pc, 200)
    axA.fill_between(Q_dwl, a - b*Q_dwl, c_min, alpha=0.25, label="Pérdida de peso muerto")

# Etiquetas y límites
axA.set_xlim(0, max(Q_int, Q_pc, Q_star)*1.02)
axA.set_ylim(0, max(a, p_star, c_min)*1.05)
axA.set_xlabel("Cantidad Q")
axA.set_ylabel("Precio / Costo")
axA.set_title("Bertrand (duopolio): CS, π y DWL")
axA.legend(loc="best")

left.pyplot(figA, clear_figure=True)

# (B) Barras de ganancias por firma
figB, axB = plt.subplots()
axB.bar(["Firma 1", "Firma 2"], [pi1, pi2])
axB.set_ylabel("Ganancia πᵢ")
axB.set_title("Ganancias por firma")
right.pyplot(figB, clear_figure=True)

# -----------------------
# Notas
# -----------------------
with st.expander("Notas / reacción 'undercut'"):
    st.markdown(
        """
- Con producto **idéntico** y costos **constantes**, una firma con costo más bajo puede **subcotizar** (undercut) a la otra
  y captar toda la demanda; en el límite, el precio puede igualar el **costo alto**.
- Si los costos son **iguales**, el equilibrio es \(p^*=c\) y las firmas se reparten la cantidad.
- Usamos como benchmark competitivo \(P=c_{min}\); con CMg constante, el **excedente del productor** competitivo es 0, por eso
  \(TS^{pc}=\tfrac12(a-c_{min})Q^{pc}\).
        """
    )

