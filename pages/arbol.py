# -*- coding: utf-8 -*-

import io, textwrap
import matplotlib.pyplot as plt
import matplotlib.patheffects as pe
import streamlit as st
from dataclasses import dataclass, field
from typing import Dict, List, Tuple

# -------------------- Tema / constantes --------------------
THEME = {
    "node_radius": 0.40, "name_font_size": 9, "name_max_chars": 10,
    "node_alpha": 0.95, "node_edge_color": "black",
    "edge_lw": 2.5, "edge_lw_marked": 4.0,
    "x_gap": 2.8, "y_gap": 2.2,
    "action_font_size": 12, "payoff_font_size": 13,
    "wrap_chars": 12, "wrap_lines": 2, "label_perp_offset": 0.25,
}

PALETTE = ["#2a9d8f","#e76f51","#264653","#8ab17d","#e9c46a",
           "#457b9d","#f4a261","#7b2cbf","#2b9348","#bb3e03"]
def default_color(i:int)->str: return PALETTE[(i-1)%len(PALETTE)]

# -------------------- Modelo --------------------
@dataclass
class Node:
    player: int
    actions: List[Dict]  # [{label:str, to:int|str, mark:bool}]

@dataclass
class GameState:
    n_players: int = 2
    player_names: Dict[int,str] = field(default_factory=lambda:{1:"Jugador1",2:"Jugador2"})
    player_colors: Dict[int,str] = field(default_factory=lambda:{1:default_color(1),2:default_color(2)})
    nodes: Dict[int,Node] = field(default_factory=lambda:{1: Node(player=1, actions=[])} )
    terminals: Dict[str,Dict] = field(default_factory=dict)
    next_node: int = 2
    next_term: int = 1

    def edges(self):
        es=[]
        for u, nd in self.nodes.items():
            for a in nd.actions: es.append((u, a["to"], a["label"], bool(a.get("mark"))))
        return es

    def get_root(self)->int:
        nodes=set(self.nodes.keys())
        children=set(v for (u,v,_,_) in self.edges() if isinstance(v,int) and v in nodes)
        roots=list(nodes-children)
        return sorted(roots)[0] if roots else sorted(nodes)[0]

    def resize_players(self, n:int):
        self.n_players=int(n)
        for i in range(1,self.n_players+1):
            self.player_names.setdefault(i,f"Jugador{i}")
            self.player_colors.setdefault(i, default_color(i))
        for k in list(self.player_names.keys()):
            if k>self.n_players: self.player_names.pop(k)
        for k in list(self.player_colors.keys()):
            if k>self.n_players: self.player_colors.pop(k)

    def set_node_player(self, node_id:int, player_id:int):
        if node_id in self.nodes and 1<=player_id<=self.n_players:
            self.nodes[node_id].player=int(player_id)

    def add_child(self, from_node:int, label:str, child_player:int, mark:bool=False)->int:
        v=self.next_node; self.next_node+=1
        self.nodes[v]=Node(player=int(child_player), actions=[])
        self.nodes[from_node].actions.append({"label":label, "to":v, "mark":bool(mark)})
        return v

    def add_terminal(self, from_node:int, label:str, payoff:Tuple[float,...], mark:bool=False)->str:
        tid=f"T{self.next_term}"; self.next_term+=1
        self.terminals[tid]={"payoff": tuple(payoff)}
        self.nodes[from_node].actions.append({"label":label, "to":tid, "mark":bool(mark)})
        return tid

    def delete_subtree(self, u:int):
        if u not in self.nodes: return
        if u==self.get_root():
            n=self.n_players; names=self.player_names.copy(); colors=self.player_colors.copy()
            self.__init__(n_players=n, player_names=names, player_colors=colors); return
        def collect(x, nodes=set(), terms=set()):
            if isinstance(x,str): terms.add(x); return nodes,terms
            nodes.add(x)
            for a in self.nodes[x].actions: collect(a["to"], nodes, terms)
            return nodes,terms
        nodes_del, terms_del = collect(u, set(), set())
        for k, nd in self.nodes.items():
            if k in nodes_del: continue
            nd.actions=[a for a in nd.actions if not ((isinstance(a["to"],int) and a["to"] in nodes_del) or (isinstance(a["to"],str) and a["to"] in terms_del))]
        for k in list(nodes_del): self.nodes.pop(k,None)
        for t in list(terms_del): self.terminals.pop(t,None)

# -------------------- Render --------------------
import textwrap
def _short_name(s, max_chars): s=str(s); return s if len(s)<=max_chars else (s[:max_chars-1]+"…")
def _wrap(text, width, lines):
    s=str(text).strip()
    if not s: return s
    ll=textwrap.wrap(s, width=width, break_long_words=True, break_on_hyphens=True)
    if len(ll)>lines:
        ll=ll[:lines]; ll[-1]= (ll[-1][:-1]+"…") if len(ll[-1])>=1 else "…"
    return "\n".join(ll)
def _fmt_num(x):
    try:
        xi=int(x)
        if abs(x-xi)<1e-9: return str(xi)
    except: pass
    return f"{x:.3f}".rstrip("0").rstrip(".")
def _fmt_payoff(payoff): return "("+", ".join(_fmt_num(x) for x in payoff)+")"

def _assign_positions(state: GameState, theme):
    pos={}; x_cur=0.0; x_gap=theme["x_gap"]; y_gap=theme["y_gap"]
    def dfs(u, depth):
        nonlocal x_cur
        if isinstance(u,str):
            pos[u]=(x_cur,-depth*y_gap); x_cur+=x_gap; return
        xs=[]
        for a in state.nodes[u].actions:
            dfs(a["to"], depth+1); xs.append(pos[a["to"]][0])
        pos[u]=((sum(xs)/len(xs)) if xs else x_cur, -depth*y_gap)
        if not xs: x_cur+=x_gap
    dfs(state.get_root(),0); return pos

def render(state: GameState, theme, ax=None, title=None):
    if ax is None: _, ax = plt.subplots(figsize=(11,7))
    pos=_assign_positions(state, theme)

    for (u,v,lab,mk) in state.edges():
        x1,y1=pos[u]; x2,y2=pos[v]
        lw = theme["edge_lw_marked"] if mk else theme["edge_lw"]
        col= "black" if mk else "0.45"
        ax.annotate("", (x2,y2), (x1,y1), arrowprops=dict(arrowstyle="-|>", lw=lw, color=col))
        xm,ym=(x1+x2)/2,(y1+y2)/2
        dx,dy=x2-x1,y2-y1; norm=(dx*dx+dy*dy)**0.5 or 1.0
        nx,ny=-dy/norm, dx/norm
        xlab = xm + theme["label_perp_offset"]*nx
        ylab = ym + theme["label_perp_offset"]*ny
        ax.text(xlab, ylab, _wrap(lab, theme["wrap_chars"], theme["wrap_lines"]),
                fontsize=theme["action_font_size"], ha="center", va="center",
                bbox=dict(boxstyle="round,pad=0.15", facecolor="white", alpha=.85, edgecolor="0.85"),
                path_effects=[pe.withStroke(linewidth=2.5, foreground="white")])

    R=theme["node_radius"]
    for u, nd in state.nodes.items():
        x,y=pos[u]; pid=nd.player
        face = state.player_colors.get(pid, "#2a9d8f")
        name = _short_name(state.player_names.get(pid,f"J{pid}"), theme["name_max_chars"])
        ax.add_patch(plt.Circle((x,y), R, fc=face, ec=theme["node_edge_color"], lw=2.5, alpha=theme["node_alpha"]))
        ax.text(x,y,name,fontsize=theme["name_font_size"],color="white",ha="center",va="center")
        ax.text(x-R*0.6, y+R*0.8, str(u), fontsize=9, ha="right")

    for t, td in state.terminals.items():
        x,y=pos[t]; ax.scatter(x,y,s=60,color="0.1")
        ax.text(x+.18,y-.06,_fmt_payoff(td["payoff"]),
                fontsize=theme["payoff_font_size"],ha="left",va="center",
                bbox=dict(boxstyle="round,pad=0.15", facecolor="white", alpha=.9, edgecolor="0.85"))

    ax.set_xticks([]); ax.set_yticks([])
    xs=[p[0] for p in pos.values()]; ys=[p[1] for p in pos.values()]
    ax.set_xlim(min(xs)-1.6, max(xs)+1.6); ax.set_ylim(min(ys)-1.6, max(ys)+1.6)
    if title: ax.set_title(title, fontsize=20, fontweight="bold")
    ax.axis("off"); return ax

# -------------------- Streamlit (layout 2 columnas) --------------------
st.set_page_config(page_title="Game Tree Designer", layout="wide")
st.title("Construye tu árbol secuencial")

if "state" not in st.session_state:
    st.session_state.state = GameState()
S: GameState = st.session_state.state

# 💡 aquí va la magia del layout
left, right = st.columns([1, 1.25], gap="large")

# ----- Columna izquierda: panel de edición -----
with left:
    with st.expander("1) Configuración", expanded=True):
        cols = st.columns([1,2,2,2])
        with cols[0]:
            n = st.number_input("Jugadores", min_value=1, max_value=9, value=S.n_players, step=1)
            if st.button("Aplicar", use_container_width=True):
                S.resize_players(n)

        st.write("Nombres y colores")
        rows = []
        for i in range(1, S.n_players+1):
            c1,c2 = st.columns([3,2])
            with c1:
                name = st.text_input(f"J{i} nombre", S.player_names.get(i,f"Jugador{i}"), key=f"name{i}")
            with c2:
                color = st.color_picker(f"Color J{i}", S.player_colors.get(i, default_color(i)), key=f"color{i}")
            rows.append((name, color))
        if st.button("Guardar nombres y colores"):
            for i,(nm,col) in enumerate(rows, start=1):
                S.player_names[i]  = nm.strip() or f"Jugador{i}"
                S.player_colors[i] = col or default_color(i)

    with st.expander("2) Nodos", expanded=True):
        keys = sorted(S.nodes.keys()) or [1]
        c1,c2,c3,c4 = st.columns([2,2,2,2])
        with c1:
            node = st.selectbox("Nodo", keys, key="node_edit")
        with c2:
            who  = st.selectbox("J mueve", list(range(1,S.n_players+1)), format_func=lambda i: S.player_names[i])
        with c3:
            if st.button("Asignar jugador"):
                S.set_node_player(node, who)
        with c4:
            if st.button("Eliminar nodo (subárbol)", type="primary"):
                S.delete_subtree(node)

        st.divider()
        c1,c2,c3,c4,c5 = st.columns([2,2,2,2,2])
        with c1:
            parent = st.selectbox("Padre", keys, key="parent_add")
        with c2:
            lab_child = st.text_input("Etiqueta", "a", key="lab_child")
        with c3:
            who_child = st.selectbox("J (hijo)", list(range(1,S.n_players+1)), format_func=lambda i: S.player_names[i], key="who_child")
        with c4:
            mark_child = st.checkbox("Resaltar", key="mark_child")
        with c5:
            if st.button("Añadir nodo hijo"):
                if lab_child.strip():
                    S.add_child(parent, lab_child.strip(), int(who_child), bool(mark_child))

    with st.expander("3) Elegir acciones terminales y pagos", expanded=True):
        keys = sorted(S.nodes.keys()) or [1]
        c1,c2,c3,c4 = st.columns([2,3,3,2])
        with c1:
            from_node = st.selectbox("Desde", keys, key="from_action")
        with c2:
            lab = st.text_input("Etiqueta", "a", key="lab_term")
        with c3:
            payoff_text = st.text_input("Pago→ (coma-separado)", "1,1", key="payoff")
        with c4:
            mark = st.checkbox("Resaltar", key="mark_term")

        if st.button("Añadir acción (terminal)"):
            parts = [p.strip() for p in payoff_text.split(",")]
            if len(parts)==S.n_players:
                try:
                    payoff = tuple(float(x) for x in parts)
                    S.add_terminal(from_node, lab.strip(), payoff, bool(mark))
                except ValueError:
                    st.error("Pago inválido (usa números, separados por comas).")
            else:
                st.error(f"Debes ingresar {S.n_players} números (uno por jugador).")

# ----- Columna derecha: vista y exportación -----
with right:
    st.subheader("Vista previa")
    fig, ax = plt.subplots(figsize=(11,7))
    render(S, THEME, ax=ax)   # sin título en preview
    st.pyplot(fig, use_container_width=True)
    plt.close(fig)

    st.markdown("---")
    c1, c2 = st.columns([3,1])
    with c1:
        png_title = st.text_input("Título opcional para el PNG", "")
    with c2:
        buf = io.BytesIO()
        fig2, ax2 = plt.subplots(figsize=(11,7))
        render(S, THEME, ax=ax2, title=(png_title.strip() or None))
        fig2.savefig(buf, format="png", dpi=220, bbox_inches="tight")
        plt.close(fig2); buf.seek(0)
        st.download_button("Descargar PNG", data=buf, file_name="arbol.png",
                           mime="image/png", use_container_width=True)
