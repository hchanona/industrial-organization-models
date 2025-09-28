import io
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.ticker import MultipleLocator
from matplotlib.lines import Line2D
import streamlit as st

st.set_page_config(page_title="Mixto estricto (2×2)", layout="wide")
st.title("Equilibrio de Nash estrictamente mixto — Juego 2×2")
st.caption("Jugador 1: filas U/D. Jugador 2: columnas L/R.")

# ====================== 1) Entrada de pagos ======================
st.subheader("Pagos del juego")

presets = {
    "Ejemplo (mixto interior)": (
        pd.DataFrame([[3, 1], [0, 2]], index=["U", "D"], columns=["L", "R"]),
        pd.DataFrame([[1, 3], [2, 0]], index=["U", "D"], columns=["L", "R"]),
    ),
    "Coordinación (no hay mixto)": (
        pd.DataFrame([[2, 0], [0, 1]], index=["U", "D"], columns=["L", "R"]),
        pd.DataFrame([[2, 0], [0, 1]], index=["U", "D"], columns=["L", "R"]),
    ),
}
preset = st.selectbox("Plantilla rápida (opcional)", list(presets.keys()), index=0)
A0, B0 = presets[preset]

cU, cV = st.columns(2)
with cU:
    with st.container(border=True):
        st.markdown("**u₁ — Jugador 1 (filas U/D)**")
        A_df = st.data_editor(
            A0.copy(), use_container_width=True, num_rows="fixed", hide_index=False,
            column_config={
                "L": st.column_config.NumberColumn("L", step=0.1, format="%.2f"),
                "R": st.column_config.NumberColumn("R", step=0.1, format="%.2f"),
            },
        )
with cV:
    with st.container(border=True):
        st.markdown("**u₂ — Jugador 2 (columnas L/R)**")
        B_df = st.data_editor(
            B0.copy(), use_container_width=True, num_rows="fixed", hide_index=False,
            column_config={
                "L": st.column_config.NumberColumn("L", step=0.1, format="%.2f"),
                "R": st.column_config.NumberColumn("R", step=0.1, format="%.2f"),
            },
        )

A = A_df.to_numpy(dtype=float)  # pagos J1
B = B_df.to_numpy(dtype=float)  # pagos J2

# ====================== 2) Mixto estricto ======================
# Indiferencias:
#  q* = (a22 - a12) / (a11 - a12 - a21 + a22),   p* = (b22 - b21) / (b11 - b12 - b21 + b22)
den_q = (A[0,0] - A[0,1] - A[1,0] + A[1,1])
den_p = (B[0,0] - B[0,1] - B[1,0] + B[1,1])

has_q = abs(den_q) > 1e-12
has_p = abs(den_p) > 1e-12

q_star = (A[1,1] - A[0,1]) / den_q if has_q else np.nan
p_star = (B[1,1] - B[1,0]) / den_p if has_p else np.nan

# Estrictamente mixto: interior (tolerancia pequeña)
eps = 1e-9
mixed_strict = (
    has_q and has_p
    and (q_star > eps) and (q_star < 1 - eps)
    and (p_star > eps) and (p_star < 1 - eps)
)

# ====================== 3) Resultados ======================
st.subheader("Resultado")

if mixed_strict:
    p_show = round(float(p_star), 2)
    q_show = round(float(q_star), 2)
    # Utilidades esperadas en el punto (indiferencias)
    EU1 = q_star*A[0,0] + (1 - q_star)*A[0,1]
    EU2 = p_star*B[0,0] + (1 - p_star)*B[1,0]
    st.success(f"Equilibrio estrictamente mixto:  p* = {p_show},  q* = {q_show}")
    st.write(f"EU₁(p*,q*) = {round(float(EU1), 2)}   |   EU₂(p*,q*) = {round(float(EU2), 2)}")
else:
    st.info("No existe **equilibrio estrictamente mixto** (interior). "
            "O bien no hay indiferencia (denominador nulo) o p*/q* caen en {0,1}.")

# ====================== 4) Gráficos ======================
st.subheader("Gráficos")

# --- A) Intersección de EU₁ (vs q) ---
q_grid = np.linspace(0, 1, 401)
EU_U = q_grid*A[0,0] + (1 - q_grid)*A[0,1]
EU_D = q_grid*A[1,0] + (1 - q_grid)*A[1,1]

gA, axA = plt.subplots(figsize=(6.8, 4.6), dpi=140)
axA.plot(q_grid, EU_U, label=r"$EU_1(U,q)$", linewidth=2)
axA.plot(q_grid, EU_D, label=r"$EU_1(D,q)$", linewidth=2, linestyle="--")
if mixed_strict:
    y_int = q_star*A[0,0] + (1 - q_star)*A[0,1]
    axA.scatter([q_star], [y_int], zorder=5)
axA.set_xlabel("q"); axA.set_ylabel("EU₁"); axA.set_xlim(0,1)
axA.grid(alpha=0.3); axA.legend(); gA.tight_layout()

# --- B) Diagrama BR (solo si hay mixto estricto) ---
c_1, c_2, lw = "tab:blue", "tab:purple", 3.0
gB, axB = plt.subplots(figsize=(6.8, 6.8), dpi=140)
axB.plot([0,1,1,0,0],[0,0,1,1,0], color="black", lw=1.3, zorder=1)

if mixed_strict:
    # BR J1 (p | q): verticales por tramos usando q*
    axB.vlines(x=0, ymin=0, ymax=q_star, color=c_1, lw=lw, zorder=9)
    axB.hlines(y=q_star, xmin=0, xmax=1, color=c_1, lw=lw, zorder=9)  # guía de indiferencia
    axB.vlines(x=1, ymin=q_star, ymax=1, color=c_1, lw=lw, zorder=9)
    # BR J2 (q | p): horizontales por tramos usando p*
    axB.hlines(y=0, xmin=0, xmax=p_star, color=c_2, lw=lw, zorder=10)
    axB.vlines(x=p_star, ymin=0, ymax=1, color=c_2, lw=lw, zorder=10)  # guía de indiferencia
    axB.hlines(y=1, xmin=p_star, xmax=1, color=c_2, lw=lw, zorder=10)
    axB.scatter([p_star], [q_star], s=70, color="black", zorder=11)
else:
    axB.text(0.5, 0.5, "No hay mixto interior", ha="center", va="center", alpha=0.4)

axB.set_xlim(0,1); axB.set_ylim(0,1); axB.set_aspect("equal","box")
axB.xaxis.set_major_locator(MultipleLocator(0.1))
axB.yaxis.set_major_locator(MultipleLocator(0.1))
axB.xaxis.set_minor_locator(MultipleLocator(0.05))
axB.yaxis.set_minor_locator(MultipleLocator(0.05))
axB.tick_params(which="major", length=5); axB.tick_params(which="minor", length=3)
axB.grid(False)
handles = [Line2D([0,1],[0,0], color=c_1, lw=lw),
           Line2D([0,1],[0,0], color=c_2, lw=lw)]
axB.legend(handles, ["BR J1 (p|q)", "BR J2 (q|p)"], loc="lower right")
axB.set_xlabel("p"); axB.set_ylabel("q")
gB.tight_layout()

# Mostrar lado a lado
col1, col2 = st.columns(2)
with col1: st.pyplot(gA, use_container_width=True); plt.close(gA)
with col2: st.pyplot(gB, use_container_width=True); plt.close(gB)

# ====================== 5) Export PNG (solo si existe) ======================
st.markdown("---")
if mixed_strict:
    buf = io.BytesIO()
    gB2, axB2 = plt.subplots(figsize=(7,7), dpi=220)
    axB2.plot([0,1,1,0,0],[0,0,1,1,0], color="black", lw=1.3, zorder=1)
    axB2.vlines(x=0, ymin=0, ymax=q_star, color=c_1, lw=lw, zorder=9)
    axB2.hlines(y=q_star, xmin=0, xmax=1, color=c_1, lw=lw, zorder=9)
    axB2.vlines(x=1, ymin=q_star, ymax=1, color=c_1, lw=lw, zorder=9)
    axB2.hlines(y=0, xmin=0, xmax=p_star, color=c_2, lw=lw, zorder=10)
    axB2.vlines(x=p_star, ymin=0, ymax=1, color=c_2, lw=lw, zorder=10)
    axB2.hlines(y=1, xmin=p_star, xmax=1, color=c_2, lw=lw, zorder=10)
    axB2.scatter([p_star], [q_star], s=70, color="black", zorder=11)
    axB2.set_xlim(0,1); axB2.set_ylim(0,1); axB2.set_aspect("equal","box")
    axB2.set_xlabel("p"); axB2.set_ylabel("q")
    gB2.tight_layout()
    gB2.savefig(buf, format="png", bbox_inches="tight"); plt.close(gB2); buf.seek(0)
    st.download_button("Descargar PNG del diagrama BR",
        data=buf, file_name="BR_mixto_estricto_2x2.png",
        mime="image/png", use_container_width=True)
```
