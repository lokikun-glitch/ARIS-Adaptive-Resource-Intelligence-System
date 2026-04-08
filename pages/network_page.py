import streamlit as st
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use("Agg")
import networkx as nx

from algorithms.network import kruskal_mst, generate_random_graph


def parse_graph_text(text):
    lines = text.strip().splitlines()
    if not lines:
        return [], [], ["No input provided"]
    try:
        nodes_line = lines[0].strip()
        nodes = [n.strip() for n in nodes_line.split(',') if n.strip()]
        edges = []
        for i, line in enumerate(lines[1:], 1):
            parts = [p.strip() for p in line.split(',')]
            if len(parts) != 3:
                return nodes, edges, [f"Line {i+1}: expected 'u,v,weight' got '{line}'"]
            u, v, w_str = parts
            try:
                w = float(w_str)
                if w <= 0:
                    return nodes, edges, [f"Line {i+1}: weight must be positive"]
                edges.append({'u': u, 'v': v, 'weight': w})
            except ValueError:
                return nodes, edges, [f"Line {i+1}: weight must be number"]
        return nodes, edges, []
    except Exception as e:
        return [], [], [str(e)]


def render():
    st.title("Network Optimization")
    st.markdown("**Algorithm:** Kruskal's MST — Graph  |  **Complexity:** O(E log E)")
    st.markdown("---")

    col1, col2 = st.columns([2, 1])

    with col1:
        st.subheader("Input")
        default_text = "A,B,C,D,E\nA,B,4\nA,C,1\nB,C,2\nB,D,5\nC,D,3\nC,E,6\nD,E,7"
        graph_text = st.text_area(
            "Graph (first line: nodes, then edges u,v,weight — one per line)",
            value=default_text,
            height=200,
            key="net_graph"
        )

    with col2:
        st.subheader("Options")
        st.markdown(" ")
        if st.button("Random Input", key="net_rand"):
            rand_nodes, rand_edges = generate_random_graph(5)
            lines = [','.join(rand_nodes)]
            for e in rand_edges:
                lines.append(f"{e['u']},{e['v']},{e['weight']}")
            st.session_state['net_graph'] = "\n".join(lines)
            st.rerun()

    show_steps = st.checkbox("Show steps", value=False, key="net_steps_toggle")

    if st.button("Run MST", key="net_run"):
        nodes, edges, errors = parse_graph_text(graph_text)

        if errors:
            for e in errors:
                st.error(e)
            return

        if not nodes or not edges:
            st.warning("Need at least nodes and edges.")
            return

        result = kruskal_mst(nodes, edges)

        st.markdown("---")
        st.subheader("Output")

        mst = result['mst_edges']
        if not mst:
            st.info("No MST found.")
        else:
            lines = []
            for e in mst:
                lines.append(f"  {e['u']} -- {e['v']}  weight={e['weight']}")

            st.text("MST Edges:")
            st.code("\n".join(lines), language=None)
            st.text(f"Total Weight:  {result['total_weight']}")
            st.text(f"Time Taken:    {result['exec_time_ms']:.4f} ms")

        # Simple graph visualization
        fig, ax = plt.subplots(figsize=(6, 4))
        G = nx.Graph()
        G.add_nodes_from(nodes)
        for e in edges:
            G.add_edge(e['u'], e['v'], weight=e['weight'])
        pos = nx.spring_layout(G, seed=42)
        nx.draw(G, pos, with_labels=True, node_color='lightblue', node_size=500, ax=ax)
        edge_labels = {(e['u'], e['v']): e['weight'] for e in edges}
        nx.draw_networkx_edge_labels(G, pos, edge_labels, ax=ax)
        ax.set_title("Original Graph")
        plt.axis('off')
        st.pyplot(fig)
        plt.close(fig)

        if mst:
            fig2, ax2 = plt.subplots(figsize=(6, 4))
            G2 = nx.Graph()
            G2.add_nodes_from(nodes)
            for e in mst:
                G2.add_edge(e['u'], e['v'], weight=e['weight'])
            nx.draw(G2, pos, with_labels=True, node_color='lightgreen', node_size=500, ax=ax2)
            edge_labels_mst = {(e['u'], e['v']): e['weight'] for e in mst}
            nx.draw_networkx_edge_labels(G2, pos, edge_labels_mst, ax=ax2)
            ax2.set_title("MST")
            plt.axis('off')
            st.pyplot(fig2)
            plt.close(fig2)

        if show_steps:
            st.subheader("Steps")
            st.code("\n".join(result['steps']), language=None)