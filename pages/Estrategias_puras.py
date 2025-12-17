import streamlit as st
import numpy as np
import pandas as pd

st.set_page_config(page_title="Juego bimatricial", layout="wide")
st.title("Juego en forma normal (2 jugadores): mejores respuestas y equilibrios puros")

# -----------------------------
# Helpers
# -----------------------------
def parse_commas(text, default_prefix, k):
    parts = [x.strip() for x in text.split(",") if x.strip() != ""]
    out = parts[:k]
    while len(out) < k:
        out.append(f"{default_prefix}{len(out)+1}")
    return out

def best_responses(U1, U2, row_names, col_names):
    n, m = U1.shape

    BR1_by_col = []
    for j in range(m):
        col_vals = U1[:, j]
        mx = np.max(col_vals)
        BR1_by_col.append([row_names[i] for i in range(n) if col_vals[i] == mx])

    BR2_by_row = []
    for i in range(n):
        row_vals = U2[i, :]
        mx = np.max(row_vals)
        BR2_by_row.append([col_names[j] for j in range(m) if row_vals[j] == mx])

    NE = []
    for i in range(n):
        for j in range(m):
            if (row_names[i] in BR1_by_col[j]) and (col_names[j] in BR2_by_row[i]):
                NE.append((i, j))

    return BR1_by_col, BR2_by_row, NE

def payoff_table(U1, U2, row_names, col_names, decimals=2):
    tbl = pd.DataFrame(index=row_names, columns=col_names)
    for i, r in enumerate(row_names):
        for j, c in enumerate(col_names):
            tbl.loc[r, c] = f"({round(float(U1[i,j]),decimals)}, {round(float(U2[i,j]),decimals)})"
    return tbl

def style_marks(row_names, col_names, BR1_by_col, BR2_by_row, NE):
    n, m = len(row_names), len(col_names)

    br1_cells = set()
    for j in range(m):
        for r in BR1_by_col[j]:
            i = row_names.index(r)
            br1_cells.add((i, j))

    br2_cells = set()
    for i in range(n):
        for c in BR2_by_row[i]:
            j = col_names.index(c)
            br2_cells.add((i, j))

    ne_cells = set(NE)

    def styler(df):
        styles = pd.DataFrame("", index=df.index, columns=df.columns)
        for i in range(n):
            for j in range(m):
                if (i, j) in ne_cells:
                    styles.iloc[i, j] = "background-color: #d4edda; font-weight: 700;"  # NE
                elif (i, j) in br1_cells and (i, j) in br2_cells:
                    styles.iloc[i, j] = "background-color: #fff3cd;"  # BR1 & BR2
                elif (i, j) in br1_cells:
                    styles.iloc[i, j] = "background-color: #e8f4ff;"  # BR1
                elif (i, j) in br2_cells:
                    styles.iloc[i, j] = "background-color: #f6e8ff;"  # BR2
        return styles

    return styler

# -----------------------------
# Inputs: dimensions + names
# -----------------------------
colA, colB, colC = st.columns([1, 1, 1])
with colA:
    n = int(st.number_input("Estrategias Jugador 1 (filas)", min_value=1, max_value=10, value=2, step=1))
with colB:
    m = int(st.number_input("Estrategias Jugador 2 (columnas)", min_value=1, max_value=10, value=2, step=1))
with colC:
    decimals = int(st.slider("Redondeo (decimales)", min_value=0, max_value=4, value=2))

st.divider()

left, right = st.columns(2)
with left:
    st.subheader("Nombres de estrategias (separados por comas)")
    p1_text = st.text_input("Jugador 1 (filas)", value=",".join([f"P1{i+1}" for i in range(n)]))
with right:
    st.subheader(" ")
    p2_text = st.text_input("Jugador 2 (columnas)", value=",".join([f"P2{j+1}" for j in range(m)]))

row_names = parse_commas(p1_text, "P1", n)
col_names = parse_commas(p2_text, "P2", m)

# -----------------------------
# Payoff matrices editors (U1 and U2)
# -----------------------------
st.subheader("Ingresar pagos")
st.caption("Edita las dos matrices: U1 = pagos de Jugador 1, U2 = pagos de Jugador 2.")

key_u1 = f"U1_{n}x{m}"
key_u2 = f"U2_{n}x{m}"

if key_u1 not in st.session_state:
    st.session_state[key_u1] = pd.DataFrame(np.zeros((n, m)), index=row_names, columns=col_names)
if key_u2 not in st.session_state:
    st.session_state[key_u2] = pd.DataFrame(np.zeros((n, m)), index=row_names, columns=col_names)

# Reindex to follow name changes
st.session_state[key_u1] = st.session_state[key_u1].reindex(index=row_names, columns=col_names, fill_value=0.0)
st.session_state[key_u2] = st.session_state[key_u2].reindex(index=row_names, columns=col_names, fill_value=0.0)

c1, c2 = st.columns(2)
with c1:
    st.markdown("**U1 (pagos de Jugador 1)**")
    U1_df = st.data_editor(
        st.session_state[key_u1],
        key="editor_u1",
        use_container_width=True,
        num_rows="fixed",
    )
with c2:
    st.markdown("**U2 (pagos de Jugador 2)**")
    U2_df = st.data_editor(
        st.session_state[key_u2],
        key="editor_u2",
        use_container_width=True,
        num_rows="fixed",
    )

st.session_state[key_u1] = U1_df
st.session_state[key_u2] = U2_df

U1 = U1_df.to_numpy(dtype=float)
U2 = U2_df.to_numpy(dtype=float)

# -----------------------------
# Compute + display results
# -----------------------------
BR1_by_col, BR2_by_row, NE = best_responses(U1, U2, row_names, col_names)

st.divider()
st.subheader("Resultados")

r1, r2 = st.columns([1, 1])
with r1:
    st.markdown("**Mejores respuestas de Jugador 1 (filas) ante cada estrategia de Jugador 2 (columna):**")
    for j, c in enumerate(col_names):
        st.write(f"- Ante **{c}**: {BR1_by_col[j]}")

with r2:
    st.markdown("**Mejores respuestas de Jugador 2 (columnas) ante cada estrategia de Jugador 1 (fila):**")
    for i, r in enumerate(row_names):
        st.write(f"- Ante **{r}**: {BR2_by_row[i]}")

st.markdown("**Equilibrios puros de Nash:**")
if len(NE) == 0:
    st.write("No hay equilibrios puros.")
else:
    for (i, j) in NE:
        st.write(
            f"- (**{row_names[i]}**, **{col_names[j]}**) con pagos "
            f"({round(float(U1[i,j]),decimals)}, {round(float(U2[i,j]),decimals)})"
        )

st.subheader("Tabla de pagos (u1,u2) con marcas")
tbl = payoff_table(U1, U2, row_names, col_names, decimals=decimals)
styler_fn = style_marks(row_names, col_names, BR1_by_col, BR2_by_row, NE)

st.caption("Verde = equilibrio puro; azul = BR de J1; morado = BR de J2; amarillo = ambos BR.")
st.dataframe(tbl.style.apply(styler_fn, axis=None), use_container_width=True)
