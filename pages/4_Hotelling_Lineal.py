# pages/4_Hotelling_Lineal.py
import streamlit as st
import numpy as np
import matplotlib.pyplot as plt

st.title("Hotelling lineal (dos firmas en 0 y 1)")
st.caption("Demanda unitaria. Graficamos: ganancias por ubicación, superávit del consumidor y el mapa de precios entregados.")

# -------------------------
# Parámetros
# -------------------------
colA, colB, colC = st.columns(3)
S  = colA.number_input("Valor de reserva S", min_value=0.0, value=10.0, step=0.1, format="%.2f")
t  = colB.number_input("Costo de transporte t", min_value=0.01, value=1.0, step=0.01, format="%.2f")
c1 = colC.number_input("Costo marginal c₁", min_value=0.0, value=1.0, step=0.1, format="%.2f")
c2 = colC.number_input("Costo marginal c₂", min_value=0.0, value=1.0, step=0.1, format="%.2f")

modo = st.radio("Precios", ["Equilibrio de Nash (cobertura total)", "Elegir manualmente"], horizontal=True)
if modo.startswith("Equilibrio"):
    # Equilibrio estándar con cobertura total:
    # p1* = (2c1 + c2 + 3t)/3,  p2* = (c1 + 2c2 + 3t)/3
    p1 = (2*c1 + c2 + 3*t) / 3
    p2 = (c1 + 2*c2 + 3*t) / 3
    st.info(f"Precios de equilibrio: p₁* = {p1:.2f}, p₂* = {p2:.2f}")
else:
    colp1, colp2 = st.columns(2)
    p1 = colp1.number_input(
        "Precio p₁", min_value=0.0,
        value=float(round((2*c1 + c2 + 3*t)/3, 2)), step=0.1, format="%.2f"
    )
    p2 = colp2.number_input(
        "Precio p₂", min_value=0.0,
        value=float(round((c1 + 2*c2 + 3*t)/3, 2)), step=0.1, format="%.2f"
    )

# -------------------------
# Cálculos
# -------------------------
n = 2001
x = np.linspace(0.0, 1.0, n)

# Precios entregados
P1x = p1 + t*x
P2x = p2 + t*(1 - x)

# Elección del consumidor (rompe empates hacia la firma 1)
buy1 = (P1x <= P2x) & (S - P1x > 0)
buy2 = (P2x <  P1x) & (S - P2x > 0)

q1 = buy1.mean()  # longitud atendida por firma 1
q2 = buy2.mean()  # longitud atendida por firma 2
no_buy = 1.0 - (q1 + q2)

# Punto indiferente x^ entre firmas (geometría de las rectas)
x_star = np.clip((p2 - p1 + t) / (2*t), 0.0, 1.0)

# Márgenes y ganancias
m1 = max(p1 - c1, 0.0)
m2 = max(p2 - c2, 0.0)
pi1 = m1 * q1
pi2 = m2 * q2

# Superávit del consumidor por ubicación (envolvente truncada en 0)
Pmin = np.minimum(P1x, P2x)
cs_density = np.maximum(S - Pmin, 0.0)
CS = float(np.trapz(cs_density, x))

# Cortes de cobertura con S: S = p1 + t*a  y  S = p2 + t*(1 - (1-b))
a = np.clip((S - p1)/t, 0.0, 1.0)
one_minus_b = np.clip(1 - (S - p2)/t, 0.0, 1.0)

# -------------------------
# Métricas
# -------------------------
mcol1, mcol2, mcol3, mcol4 = st.columns(4)
mcol1.metric("x̂ (indiferente)", f"{x_star:.2f}")
mcol2.metric("Cuotas q₁ / q₂", f"{q1:.2f} / {q2:.2f}")
mcol3.metric("Ganancias π₁ / π₂", f"{pi1:.2f} / {pi2:.2f}")
mcol4.metric("CS total", f"{CS:.2f}")
if no_buy > 1e-6:
    st.warning(f"Mercado **no cubierto**: {no_buy:.2f} no compra.")

# -------------------------
# (1) Ganancias por ubicación — coloreado por firma
# -------------------------
fig1, ax1 = plt.subplots()

g1 = np.where(buy1, m1, 0.0)
g2 = np.where(buy2, m2, 0.0)

ax1.fill_between(x, 0, g1, alpha=0.35, label="π₁ por ubicación")
ax1.fill_between(x, 0, g2, alpha=0.35, label="π₂ por ubicación")

# Guías: márgenes y partición
ax1.axvline(x_star, linestyle="--", linewidth=1)
if m1 > 0: ax1.hlines(m1, 0, x_star, linestyles=":")
if m2 > 0: ax1.hlines(m2, x_star, 1, linestyles=":")

ax1.set_ylim(bottom=0)
ax1.set_xlabel("Ubicación x ∈ [0,1]")
ax1.set_ylabel("Ganancia por consumidor")
ax1.set_title("Ganancias de las empresas a lo largo de la línea")
ax1.legend()
st.pyplot(fig1, clear_figure=True)

# -------------------------
# (2) Superávit del consumidor por ubicación
# -------------------------
fig2, ax2 = plt.subplots()
ax2.plot(x, cs_density, linewidth=2)
ax2.fill_between(x, 0, cs_density, alpha=0.3)
ax2.axvline(x_star, linestyle="--", linewidth=1)
ax2.set_xlabel("Ubicación x ∈ [0,1]")
ax2.set_ylabel("Superávit del consumidor")
ax2.set_title("Superávit del consumidor (S - precio entregado)")
st.pyplot(fig2, clear_figure=True)

# -------------------------
# (3) Mapa de precios entregados, a y 1-b
# -------------------------
fig3, ax3 = plt.subplots()

ax3.plot(x, P1x, linewidth=2, label="p₁ + t·x")
ax3.plot(x, P2x, linewidth=2, label="p₂ + t·(1-x)")

# Envolvente (precio mínimo) resaltada donde S permite compra
mask_buy = (Pmin <= S)
ax3.plot(x[mask_buy], Pmin[mask_buy], linewidth=3)

# Líneas verticales en a, 1-b y x^
ax3.axvline(a, linewidth=1, color="k")
ax3.axvline(one_minus_b, linewidth=1, color="k")
ax3.axvline(x_star, linestyle="--", linewidth=1)

# Horizontales punteadas en p1 y p2
ax3.hlines(p1, 0, 1, linestyles="dashed")
ax3.hlines(p2, 0, 1, linestyles="dashed")

# Etiquetas de a y 1-b
ymin, ymax = ax3.get_ylim()
y_txt = ymin + 0.05*(ymax - ymin)
ax3.text(a, y_txt, "a", ha="center", va="bottom")
ax3.text(one_minus_b, y_txt, "1 - b", ha="center", va="bottom")

# Sombrear zona de no compra (si existe un hueco entre cortes)
gap_L = min(a, x_star)
gap_R = max(one_minus_b, x_star)
if gap_R > gap_L:
    ax3.axvspan(gap_L, gap_R, alpha=0.10)

ax3.set_xlabel("x")
ax3.set_ylabel("Precio entregado")
ax3.set_title("Precios entregados y región de cobertura (estilo figura)")
ax3.legend()
st.pyplot(fig3, clear_figure=True)



