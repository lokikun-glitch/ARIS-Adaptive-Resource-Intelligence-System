import streamlit as st
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use("Agg")
import networkx as nx

from algorithms.conflict import graph_coloring, generate_random_conflict_graph


def parse_conflict_text(text):
    lines = text.strip().splitlines()
    if not lines:
        return [], [], ["No input provided"]
    try:
        nodes_line = lines[0].strip()
        nodes = [n.strip() for n in nodes_line.split(',') if n.strip()]
        edges = []
        for i, line in enumerate(lines[1:], 1):
            parts = [p.strip() for p in line.split(',')]
            if len(parts) != 2:
                return nodes, edges, [f"Line {i+1}: expected 'u,v' got '{line}'"]
            u, v = parts
            edges.append((u, v))
        return nodes, edges, []
    except Exception as e:
        return [], [], [str(e)]


def render():
    st.title("Conflict Resolution")
    st.markdown("**Algorithm:** Graph Coloring — Backtracking  |  **Complexity:** O(m^n)")
    st.markdown("---")

    col1, col2 = st.columns([2, 1])

    with col1:
        st.subheader("Input")
        default_text = "T1,T2,T3,T4,T5\nT1,T2\nT1,T3\nT2,T4\nT3,T4\nT3,T5\nT4,T5"
        conflict_text = st.text_area(
            "Conflicts (first line: nodes, then edges u,v — one per line)",
            value=default_text,
            height=200,
            key="conf_graph"
        )

    with col2:
        st.subheader("Options")
        max_colors = st.number_input("Max colors", min_value=1, value=4, step=1, key="conf_maxc")
        st.markdown(" ")
        if st.button("Random Input", key="conf_rand"):
            rand_nodes, rand_edges = generate_random_conflict_graph(5)
            lines = [','.join(rand_nodes)]
            for u, v in rand_edges:
                lines.append(f"{u},{v}")
            st.session_state['conf_graph'] = "\n".join(lines)
            st.rerun()

    show_steps = st.checkbox("Show steps", value=False, key="conf_steps_toggle")

    if st.button("Run Coloring", key="conf_run"):
        nodes, edges, errors = parse_conflict_text(conflict_text)

        if errors:
            for e in errors:
                st.error(e)
            return

        if not nodes:
            st.warning("Need at least nodes.")
            return

        result = graph_coloring(nodes, edges, max_colors)

        st.markdown("---")
        st.subheader("Output")

        if not result['success']:
            st.error("No valid coloring found with given max colors.")
            st.text(f"Time Taken: {result['exec_time_ms']:.4f} ms")
        else:
            coloring = result['coloring']
            lines = []
            for node, color in coloring.items():
                lines.append(f"  {node}: Color {color}")

            st.text("Coloring:")
            st.code("\n".join(lines), language=None)
            st.text(f"Colors Used:   {result['colors_used']}")
            st.text(f"Time Taken:    {result['exec_time_ms']:.4f} ms")

        # Simple graph visualization
        fig, ax = plt.subplots(figsize=(6, 4))
        G = nx.Graph()
        G.add_nodes_from(nodes)
        G.add_edges_from(edges)
        pos = nx.spring_layout(G, seed=42)
        colors_list = ['red', 'blue', 'green', 'orange', 'purple', 'brown']
        node_colors = []
        for node in nodes:
            if node in result.get('coloring', {}):
                c = result['coloring'][node] - 1
                node_colors.append(colors_list[c % len(colors_list)])
            else:
                node_colors.append('gray')
        nx.draw(G, pos, with_labels=True, node_color=node_colors, node_size=500, ax=ax)
        ax.set_title("Graph Coloring")
        plt.axis('off')
        st.pyplot(fig)
        plt.close(fig)

        if show_steps:
            st.subheader("Steps")
            st.code("\n".join(result['steps']), language=None)