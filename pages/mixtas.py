import io
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.ticker import MultipleLocator
from matplotlib.lines import Line2D
import streamlit as st

st.set_page_config(page_title="Equilibrios mixtos (2×2)", layout="wide")
st.title("Equilibrios de Nash en estrategias mixtas — Juego 2×2")
st.caption("Jugador 1: filas U/D. Jugador 2: columnas L/R.")

# ============================================================
# 1) Entrada de pagos (dos matrices 2×2 editables)
# ============================================================
st.subheader("Pagos del juego")

presets = {
    "Ejemplo (mixto interior)": (
        pd.DataFrame([[3, 1], [0, 2]], index=["U", "D"], columns=["L", "R"]),
        pd.DataFrame([[1, 3], [2, 0]], index=["U", "D"], columns=["L", "R"]),
    ),
    "Coordinación (2 puros)": (
        pd.DataFrame([[2, 0], [0, 1]], index=["U", "D"], columns=["L", "R"]),
        pd.DataFrame([[2, 0], [0, 1]], index=["U", "D"], columns=["L", "R"]),
    ),
    "Cara-Cruz (anticoord.)": (
        pd.DataFrame([[1, -1], [-1, 1]], index=["U", "D"], columns=["L", "R"]),
        pd.DataFrame([[-1, 1], [1, -1]], index=["U", "D"], columns=["L", "R"]),
    ),
}
preset = st.selectbox("Plantilla rápida (opcional)", list(presets.keys()), index=0)

A0, B0 = presets[preset]
cU, cV = st.columns(2)

with cU:
    with st.container(border=True):
        st.markdown("**u₁ — Jugador 1 (filas U/D)**")
        A_df = st.data_editor(
            A0.copy(),
            use_container_width=True,
            num_rows="fixed",
            hide_index=False,
            column_config={
                "L": st.column_config.NumberColumn("L", step=0.1, format="%.2f"),
                "R": st.column_config.NumberColumn("R", step=0.1, format="%.2f"),
            },
        )

with cV:
    with st.container(border=True):
        st.markdown("**u₂ — Jugador 2 (columnas L/R)**")
        B_df = st.data_editor(
            B0.copy(),
            use_container_width=True,
            num_rows="fixed",
            hide_index=False,
            column_config={
                "L": st.column_config.NumberColumn("L", step=0.1, format="%.2f"),
                "R": st.column_config.NumberColumn("R", step=0.1, format="%.2f"),
            },
        )

st.caption("Tip: edita las celdas directamente. Estrategias: U/D (filas), L/R (columnas).")

# Convertir a numpy
A = A_df.to_numpy(dtype=float)  # pagos de J1
B = B_df.to_numpy(dtype=float)  # pagos de J2

# ============================================================
# 2) Cálculos: NEs puros y mixto
# ============================================================
# Indiferencias (condiciones de mezcla)
# q* hace indiferente a J1 entre U y D
# p* hace indiferente a J2 entre L y R
den_q = (A[0, 0] - A[0, 1] - A[1, 0] + A[1, 1])
den_p = (B[0, 0] - B[0, 1] - B[1, 0] + B[1, 1])

has_q = abs(den_q) > 1e-12
has_p = abs(den_p) > 1e-12

q_star = (A[1, 1] - A[0, 1]) / den_q if has_q else np.nan
p_star = (B[1, 1] - B[1, 0]) / den_p if has_p else np.nan

mixed_exists = (
    has_q and has_p
    and (q_star >= -1e-12) and (q_star <= 1 + 1e-12)
    and (p_star >= -1e-12) and (p_star <= 1 + 1e-12)
)

# NEs puros: mejores respuestas cruzadas
pure_NE = []
# BR de J1 por columna
best_rows_col1 = np.argwhere(A[:, 0] == np.max(A[:, 0])).flatten().tolist()
best_rows_col2 = np.argwhere(A[:, 1] == np.max(A[:, 1])).flatten().tolist()
# BR de J2 por fila
best_cols_rowU = np.argwhere(B[0, :] == np.max(B[0, :])).flatten().tolist()
best_cols_rowD = np.argwhere(B[1, :] == np.max(B[1, :])).flatten().tolist()

if 0 in best_rows_col1 and 0 in best_cols_rowU: pure_NE.append(("U", "L"))
if 0 in best_rows_col2 and 1 in best_cols_rowU: pure_NE.append(("U", "R"))
if 1 in best_rows_col1 and 0 in best_cols_rowD: pure_NE.append(("D", "L"))
if 1 in best_rows_col2 and 1 in best_cols_rowD: pure_NE.append(("D", "R"))

# ============================================================
# 3) Resultados numéricos
# ============================================================
st.subheader("Resultados")

colL, colR, colC = st.columns([1.2, 1.2, 1.2])
with colL:
    st.markdown("**Equilibrios puros**")
    if len(pure_NE) == 0:
        st.info("No hay NE puros.")
    else:
        st.success(" • ".join([f"({i},{j})" for (i, j) in pure_NE]))

with colR:
    st.markdown("**Equilibrio mixto (si aplica)**")
    if mixed_exists:
        p_show = round(float(np.clip(p_star, 0, 1)), 2)
        q_show = round(float(np.clip(q_star, 0, 1)), 2)
        st.success(f"p* = {p_show},  q* = {q_show}")
    else:
        st.info("No existe (o queda fuera de [0,1]).")

with colC:
    if mixed_exists:
        # EU en el punto mixto
        EU1 = q_star * A[0, 0] + (1 - q_star) * A[0, 1]  # = EU con D también
        EU2 = p_star * B[0, 0] + (1 - p_star) * B[1, 0]  # = EV con R también
        st.markdown("**Utilidades esperadas en (p*, q*)**")
        st.write(f"EU₁ = {round(float(EU1), 2)}")
        st.write(f"EU₂ = {round(float(EU2), 2)}")

# ============================================================
# 4) Gráficos
# ============================================================
st.subheader("Gráficos")

# --- Gráfico A: intersección de EU de J1 (en función de q) ---
q_grid = np.linspace(0, 1, 401)
EU_U = q_grid * A[0, 0] + (1 - q_grid) * A[0, 1]
EU_D = q_grid * A[1, 0] + (1 - q_grid) * A[1, 1]

gA, axA = plt.subplots(figsize=(6.8, 4.6), dpi=140)
axA.plot(q_grid, EU_U, label=r"$EU_1(U,q)$", linewidth=2)
axA.plot(q_grid, EU_D, label=r"$EU_1(D,q)$", linewidth=2, linestyle="--")
if mixed_exists:
    y_int = q_star * A[0, 0] + (1 - q_star) * A[0, 1]
    axA.scatter([q_star], [y_int], zorder=5)
axA.set_xlabel("q")
axA.set_ylabel("EU₁")
axA.set_xlim(0, 1)
axA.grid(alpha=0.3)
axA.legend()
gA.tight_layout()

# --- Gráfico B: diagrama de mejores respuestas (cuadrado p–q) ---
c_1 = "tab:blue"     # BR J1 (q)
c_2 = "tab:purple"   # BR J2 (p)
lw = 3.0
gB, axB = plt.subplots(figsize=(6.8, 6.8), dpi=140)
# borde
axB.plot([0, 1, 1, 0, 0], [0, 0, 1, 1, 0], color="black", lw=1.3, zorder=1)

# Tramos si existe mixto interior
if mixed_exists:
    # BR J1: horizontal por tramos (en función de p*)
    axB.hlines(y=0, xmin=0, xmax=p_star, color=c_1, lw=lw, zorder=9)
    axB.vlines(x=p_star, ymin=0, ymax=1, color=c_1, lw=lw, zorder=9)
    axB.hlines(y=1, xmin=p_star, xmax=1, color=c_1, lw=lw, zorder=9)

    # BR J2: vertical por tramos (en función de q*)
    axB.vlines(x=0, ymin=0, ymax=q_star, color=c_2, lw=lw, zorder=10)
    axB.hlines(y=q_star, xmin=0, xmax=1, color=c_2, lw=lw, zorder=10)
    axB.vlines(x=1, ymin=q_star, ymax=1, color=c_2, lw=lw, zorder=10)

    # Intersección
    axB.scatter([p_star], [q_star], s=70, color="black", zorder=11)
else:
    # Sin mixto interior: mostramos mensaje orientativo
    axB.text(0.5, 0.5, "Sin tramo mixto interior", ha="center", va="center", alpha=0.4)

axB.set_xlim(0, 1)
axB.set_ylim(0, 1)
axB.set_aspect("equal", adjustable="box")
axB.xaxis.set_major_locator(MultipleLocator(0.1))
axB.yaxis.set_major_locator(MultipleLocator(0.1))
axB.xaxis.set_minor_locator(MultipleLocator(0.05))
axB.yaxis.set_minor_locator(MultipleLocator(0.05))
axB.tick_params(which="major", length=5)
axB.tick_params(which="minor", length=3)
axB.grid(False)
handles = [
    Line2D([0, 1], [0, 0], color=c_1, lw=lw),
    Line2D([0, 1], [0, 0], color=c_2, lw=lw),
]
axB.legend(handles, ["BR jugador 1 (q)", "BR jugador 2 (p)"], loc="lower right")
axB.set_xlabel("p")
axB.set_ylabel("q")
gB.tight_layout()

# Mostrar gráficos lado a lado
col1, col2 = st.columns(2)
with col1:
    st.pyplot(gA, use_container_width=True)
    plt.close(gA)
with col2:
    st.pyplot(gB, use_container_width=True)
    plt.close(gB)

# ============================================================
# 5) Exportar PNG del diagrama BR
# ============================================================
st.markdown("---")
buf = io.BytesIO()
gB2, axB2 = plt.subplots(figsize=(7, 7), dpi=220)
# Redibujo minimal para exportar limpio
axB2.plot([0, 1, 1, 0, 0], [0, 0, 1, 1, 0], color="black", lw=1.3, zorder=1)
if mixed_exists:
    axB2.hlines(y=0, xmin=0, xmax=p_star, color=c_1, lw=lw, zorder=9)
    axB2.vlines(x=p_star, ymin=0, ymax=1, color=c_1, lw=lw, zorder=9)
    axB2.hlines(y=1, xmin=p_star, xmax=1, color=c_1, lw=lw, zorder=9)
    axB2.vlines(x=0, ymin=0, ymax=q_star, color=c_2, lw=lw, zorder=10)
    axB2.hlines(y=q_star, xmin=0, xmax=1, color=c_2, lw=lw, zorder=10)
    axB2.vlines(x=1, ymin=q_star, ymax=1, color=c_2, lw=lw, zorder=10)
    axB2.scatter([p_star], [q_star], s=70, color="black", zorder=11)
axB2.set_xlim(0, 1)
axB2.set_ylim(0, 1)
axB2.set_aspect("equal", adjustable="box")
axB2.set_xlabel("p")
axB2.set_ylabel("q")
gB2.tight_layout()
gB2.savefig(buf, format="png", bbox_inches="tight")
plt.close(gB2)
buf.seek(0)
st.download_button(
    "Descargar PNG del diagrama BR",
    data=buf,
    file_name="BR_mixto_2x2.png",
    mime="image/png",
    use_container_width=True,
)

