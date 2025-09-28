import io
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.ticker import MultipleLocator
from matplotlib.lines import Line2D
import streamlit as st

st.set_page_config(page_title="Equilibrios mixtos (2×2)", layout="wide")
st.title("Equilibrios de Nash en estrategias mixtas — Juego 2×2")
st.caption("Ingresa los pagos (u₁, u₂) para cada casilla. Detecta NEs puros y, si aplica, el NE mixto.")

# ---------- Entrada de la matriz de pagos ----------
st.subheader("Pagos del juego (Jugador 1: filas; Jugador 2: columnas)")

# Etiquetas
c1, c2, c3, c4, c5 = st.columns([1.2, 1.2, 1.2, 1.2, 1.2])
c1.markdown("**Estrategias**")
c2.markdown("**L (col 1)**")
c3.markdown("**R (col 2)**")
c4.markdown("**L (col 1)**")
c5.markdown("**R (col 2)**")

r1c1_1 = st.number_input("u₁(U,L)", value=3.0, key="a11")
r1c2_1 = st.number_input("u₁(U,R)", value=1.0, key="a12")
r2c1_1 = st.number_input("u₁(D,L)", value=0.0, key="a21")
r2c2_1 = st.number_input("u₁(D,R)", value=2.0, key="a22")

r1c1_2 = st.number_input("u₂(U,L)", value=1.0, key="b11")
r1c2_2 = st.number_input("u₂(U,R)", value=3.0, key="b12")
r2c1_2 = st.number_input("u₂(D,L)", value=2.0, key="b21")
r2c2_2 = st.number_input("u₂(D,R)", value=0.0, key="b22")

# Reempaquetar
A = np.array([[r1c1_1, r1c2_1],
              [r2c1_1, r2c2_1]], dtype=float)
B = np.array([[r1c1_2, r1c2_2],
              [r2c1_2, r2c2_2]], dtype=float)

# ---------- Utilidades esperadas y BRs ----------
# Jugador 1: p = Prob(U). Jugador 2: q = Prob(L).
# Indiferencias:
#  q* = (a22 - a12) / (a11 - a12 - a21 + a22)  si denom != 0
#  p* = (b22 - b21) / (b11 - b12 - b21 + b22)  si denom != 0

den_q = (A[0,0] - A[0,1] - A[1,0] + A[1,1])
den_p = (B[0,0] - B[0,1] - B[1,0] + B[1,1])

has_q = abs(den_q) > 1e-12
has_p = abs(den_p) > 1e-12

if has_q:
    q_star = (A[1,1] - A[0,1]) / den_q
else:
    q_star = np.nan

if has_p:
    p_star = (B[1,1] - B[1,0]) / den_p
else:
    p_star = np.nan

# Mejor respuesta por tramos (para pintar el cuadrado)
def br1(q):  # BR de jugador 1 dada q
    uU = q*A[0,0] + (1-q)*A[0,1]
    uD = q*A[1,0] + (1-q)*A[1,1]
    if abs(uU - uD) <= 1e-12: return "mix"   # indiferente
    return "U" if uU > uD else "D"

def br2(p):  # BR de jugador 2 dada p
    vL = p*B[0,0] + (1-p)*B[1,0]
    vR = p*B[0,1] + (1-p)*B[1,1]
    if abs(vL - vR) <= 1e-12: return "mix"
    return "L" if vL > vR else "R"

# ---------- NEs puros ----------
# Un perfil (i,j) es NE puro si:
#   i maximiza fila i para la columna j (para Jug1) y
#   j maximiza columna j para la fila i (para Jug2).
pure_NE = []
# Jug 1 mejores respuestas por columna
best_rows_col1 = np.argwhere(A[:,0] == np.max(A[:,0])).flatten().tolist()
best_rows_col2 = np.argwhere(A[:,1] == np.max(A[:,1])).flatten().tolist()
# Jug 2 mejores respuestas por fila
best_cols_rowU = np.argwhere(B[0,:] == np.max(B[0,:])).flatten().tolist()
best_cols_rowD = np.argwhere(B[1,:] == np.max(B[1,:])).flatten().tolist()

if 0 in best_rows_col1 and 0 in best_cols_rowU: pure_NE.append(("U","L"))
if 0 in best_rows_col2 and 1 in best_cols_rowU: pure_NE.append(("U","R"))
if 1 in best_rows_col1 and 0 in best_cols_rowD: pure_NE.append(("D","L"))
if 1 in best_rows_col2 and 1 in best_cols_rowD: pure_NE.append(("D","R"))

# ---------- NE mixto: condiciones ----------
mixed_exists = (has_q and has_p and (q_star >= -1e-12) and (q_star <= 1+1e-12)
                and (p_star >= -1e-12) and (p_star <= 1+1e-12))

# ---------- Resultados numéricos ----------
st.subheader("Resultados")
colL, colR = st.columns(2)

with colL:
    st.markdown("**Equilibrios puros**")
    if len(pure_NE) == 0:
        st.info("No hay NE puros.")
    else:
        st.success(" • ".join([f"({i},{j})" for (i,j) in pure_NE]))

with colR:
    st.markdown("**Equilibrio mixto (si aplica)**")
    if mixed_exists:
        p_show = round(float(np.clip(p_star,0,1)), 2)
        q_show = round(float(np.clip(q_star,0,1)), 2)
        st.success(f"p* = {p_show},  q* = {q_show}")
    else:
        st.info("No existe (o no está en [0,1]).")

# ---------- Gráfico A: intersecciones de EU ----------
st.subheader("Gráficos")

q_grid = np.linspace(0, 1, 401)
p_grid = np.linspace(0, 1, 401)

EU_U = q_grid*A[0,0] + (1-q_grid)*A[0,1]
EU_D = q_grid*A[1,0] + (1-q_grid)*A[1,1]

EV_L = p_grid*B[0,0] + (1-p_grid)*B[1,0]
EV_R = p_grid*B[0,1] + (1-p_grid)*B[1,1]

gA, axA = plt.subplots(figsize=(6.5,4.5), dpi=140)
axA.plot(q_grid, EU_U, label=r"$EU_1(U,q)$", linewidth=2)
axA.plot(q_grid, EU_D, label=r"$EU_1(D,q)$", linewidth=2, linestyle="--")
if mixed_exists:
    y_int = q_star*A[0,0] + (1-q_star)*A[0,1]
    axA.scatter([q_star], [y_int], zorder=5, color="black")
axA.set_xlabel("q"); axA.set_ylabel("EU₁"); axA.set_xlim(0,1)
axA.grid(alpha=0.3); axA.legend(); gA.tight_layout()

# ---------- Gráfico B: BR en el cuadrado ----------
c_trab = "tab:blue"    # BR Jug 1 (U/D)
c_jefe = "tab:purple"  # BR Jug 2 (L/R)
lw = 3.0
gB, axB = plt.subplots(figsize=(6.5,6.5), dpi=140)
# borde
axB.plot([0,1,1,0,0],[0,0,1,1,0], color="black", lw=1.3, zorder=1)

# BR Jug 1 (sobre q; líneas horizontales)
if has_p: pass  # solo para simetría visual del código
if mixed_exists:
    axB.hlines(y=0, xmin=0, xmax=p_star, color=c_trab, lw=lw, zorder=9)   # p<p* -> q=0
    axB.vlines(x=p_star, ymin=0, ymax=1, color=c_trab, lw=lw, zorder=9)   # p=p* -> q∈[0,1]
    axB.hlines(y=1, xmin=p_star, xmax=1, color=c_trab, lw=lw, zorder=9)   # p>p* -> q=1
else:
    # Si no hay mezcla: determina en qué lado cae cada tramo (con 3 puntos guía)
    for p in [0.0, 0.5, 1.0]:
        choice = br1(q=0.0)  # placeholder; BR1 depende de q. Seccionamos usando q* numérico si hubiera.
    # Para no confundir, mostramos solo la leyenda si no hay mezcla.
    axB.text(0.5, 0.5, "Sin tramo mixto\n(J1)", ha="center", va="center", alpha=0.35)

# BR Jug 2 (sobre p; líneas verticales)
if mixed_exists:
    axB.vlines(x=0, ymin=0, ymax=q_star, color=c_jefe, lw=lw, zorder=10)
    axB.hlines(y=q_star, xmin=0, xmax=1, color=c_jefe, lw=lw, zorder=10)
    axB.vlines(x=1, ymin=q_star, ymax=1, color=c_jefe, lw=lw, zorder=10)
else:
    axB.text(0.5, 0.45, "Sin tramo mixto\n(J2)", ha="center", va="center", alpha=0.35)

# Intersección
if mixed_exists:
    axB.scatter([p_star],[q_star], s=70, color="black", zorder=11)

axB.set_xlim(0,1); axB.set_ylim(0,1); axB.set_aspect("equal","box")
axB.xaxis.set_major_locator(MultipleLocator(0.1))
axB.yaxis.set_major_locator(MultipleLocator(0.1))
axB.xaxis.set_minor_locator(MultipleLocator(0.05))
axB.yaxis.set_minor_locator(MultipleLocator(0.05))
axB.tick_params(which="major", length=5)
axB.tick_params(which="minor", length=3)
axB.grid(False)
handles = [Line2D([0,1],[0,0], color=c_trab, lw=lw),
           Line2D([0,1],[0,0], color=c_jefe, lw=lw)]
axB.legend(handles, ["BR jugador 1 (q)", "BR jugador 2 (p)"], loc="lower right")
axB.set_xlabel("p"); axB.set_ylabel("q")
gB.tight_layout()

# Mostrar gráficos
col1, col2 = st.columns(2)
with col1: st.pyplot(gA, use_container_width=True); plt.close(gA)
with col2: st.pyplot(gB, use_container_width=True); plt.close(gB)

# ---------- Exportar imagen del diagrama BR ----------
st.markdown("---")
buf = io.BytesIO()
gB2, axB2 = plt.subplots(figsize=(7,7), dpi=220)
axB2.axis("off")
# Re-dibujar el diagrama BR para exportación (misma lógica que arriba)
# borde
axB2.plot([0,1,1,0,0],[0,0,1,1,0], color="black", lw=1.3, zorder=1)
if mixed_exists:
    axB2.hlines(y=0, xmin=0, xmax=p_star, color=c_trab, lw=lw, zorder=9)
    axB2.vlines(x=p_star, ymin=0, ymax=1, color=c_trab, lw=lw, zorder=9)
    axB2.hlines(y=1, xmin=p_star, xmax=1, color=c_trab, lw=lw, zorder=9)
    axB2.vlines(x=0, ymin=0, ymax=q_star, color=c_jefe, lw=lw, zorder=10)
    axB2.hlines(y=q_star, xmin=0, xmax=1, color=c_jefe, lw=lw, zorder=10)
    axB2.vlines(x=1, ymin=q_star, ymax=1, color=c_jefe, lw=lw, zorder=10)
    axB2.scatter([p_star],[q_star], s=70, color="black", zorder=11)
axB2.set_xlim(0,1); axB2.set_ylim(0,1); axB2.set_aspect("equal","box")
axB2.set_xlabel("p"); axB2.set_ylabel("q")
gB2.tight_layout()
gB2.savefig(buf, format="png", bbox_inches="tight")
plt.close(gB2); buf.seek(0)
st.download_button("Descargar PNG del diagrama BR", data=buf, file_name="BR_mixto_2x2.png", mime="image/png", use_container_width=True)
