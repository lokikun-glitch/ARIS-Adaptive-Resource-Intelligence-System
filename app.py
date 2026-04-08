import io
import base64

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import networkx as nx
from flask import Flask, jsonify, render_template, request

from algorithms.cargo import fractional_knapsack, generate_random_items
from algorithms.conflict import generate_random_conflict_graph, graph_coloring
from algorithms.network import generate_random_graph, kruskal_mst
from algorithms.scheduling import activity_selection, generate_random_jobs
from algorithms.selector import detect_algorithm

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 1 * 1024 * 1024  # 1 MB request cap

PALETTE = ['#4361ee', '#e63946', '#2ec4b6', '#f4a261', '#7209b7', '#3a0ca3']


def _err(messages):
    """Return a JSON error response."""
    if isinstance(messages, str):
        messages = [messages]
    return jsonify({'error': messages})


def fig_to_b64(fig):
    buf = io.BytesIO()
    fig.savefig(buf, format='png', bbox_inches='tight', dpi=110, facecolor=fig.get_facecolor())
    buf.seek(0)
    data = base64.b64encode(buf.read()).decode('utf-8')
    plt.close(fig)
    return data


def style_ax(ax, fig):
    fig.patch.set_facecolor('#ffffff')
    ax.set_facecolor('#ffffff')
    for spine in ['top', 'right']:
        ax.spines[spine].set_visible(False)
    for spine in ['left', 'bottom']:
        ax.spines[spine].set_color('#dde1e7')
    ax.tick_params(colors='#555', labelsize=9)


# ── Routes ──────────────────────────────────────────────────────────────────

@app.route('/')
def index():
    return render_template('index.html')


# Algorithm Selector
@app.route('/api/selector', methods=['POST'])
def api_selector():
    description = (request.json or {}).get('description', '')
    return jsonify(detect_algorithm(description))


# Cargo Optimization
@app.route('/api/cargo', methods=['POST'])
def api_cargo():
    data = request.json or {}
    items_text = data.get('items', '')
    try:
        capacity = float(data.get('capacity', 50))
        if capacity <= 0:
            return _err('Capacity must be a positive number.')
    except (TypeError, ValueError):
        return _err('Capacity must be a valid number.')

    items, errors = [], []
    for i, line in enumerate(items_text.strip().splitlines()):
        line = line.strip()
        if not line:
            continue
        parts = [p.strip() for p in line.split(',')]
        if len(parts) != 3:
            errors.append(f"Line {i+1}: expected 'name, weight, profit'")
            continue
        name, w_str, p_str = parts
        try:
            w, p = float(w_str), float(p_str)
            if w <= 0 or p <= 0:
                errors.append(f"Line {i+1}: weight and profit must be positive")
                continue
            items.append({'name': name, 'weight': w, 'profit': p})
        except ValueError:
            errors.append(f"Line {i+1}: weight and profit must be numbers")

    if errors:
        return _err(errors)
    if not items:
        return _err('No valid items found.')

    result = fractional_knapsack(items, capacity)
    sel = result['selected']

    fig, ax = plt.subplots(figsize=(6, 3.2))
    style_ax(ax, fig)
    names = [s['name'] for s in sel]
    profits = [s['profit_gained'] for s in sel]
    bars = ax.bar(names, profits, color='#4361ee', edgecolor='#2d4acc', linewidth=0.6, width=0.55)
    ax.set_ylabel("Profit Gained", fontsize=9, color='#555')
    ax.set_title("Profit Distribution", fontsize=10, color='#24292f', pad=8)
    for bar, val in zip(bars, profits):
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.4,
                f"{val:.1f}", ha='center', va='bottom', fontsize=8, color='#333')
    plt.tight_layout()

    return jsonify({
        'selected': result['selected'],
        'total_profit': result['total_profit'],
        'exec_time_ms': result['exec_time_ms'],
        'steps': result['steps'],
        'chart': fig_to_b64(fig),
    })


@app.route('/api/cargo/random')
def api_cargo_random():
    items = generate_random_items(5)
    lines = [f"{it['name']}, {it['weight']}, {it['profit']}" for it in items]
    return jsonify({'text': '\n'.join(lines)})


# Job Scheduling
@app.route('/api/scheduling', methods=['POST'])
def api_scheduling():
    data = request.json or {}
    jobs_text = data.get('jobs', '')

    jobs, errors = [], []
    for i, line in enumerate(jobs_text.strip().splitlines()):
        line = line.strip()
        if not line:
            continue
        parts = [p.strip() for p in line.split(',')]
        if len(parts) != 3:
            errors.append(f"Line {i+1}: expected 'name, start, end'")
            continue
        name, s_str, e_str = parts
        try:
            s, e = int(s_str), int(e_str)
            if s >= e:
                errors.append(f"Line {i+1}: start must be less than end")
                continue
            jobs.append({'name': name, 'start': s, 'end': e})
        except ValueError:
            errors.append(f"Line {i+1}: start and end must be integers")

    if errors:
        return _err(errors)
    if not jobs:
        return _err('No valid jobs found.')

    result = activity_selection(jobs)
    sel = result['selected']
    sel_names = {s['name'] for s in sel}

    fig, ax = plt.subplots(figsize=(8, max(3, len(jobs) * 0.45 + 0.8)))
    style_ax(ax, fig)
    for job in jobs:
        color = '#4361ee' if job['name'] in sel_names else '#c9cfe8'
        ax.barh(job['name'], job['end'] - job['start'], left=job['start'],
                color=color, height=0.55, edgecolor='white', linewidth=0.8)
    ax.set_xlabel("Time", fontsize=9, color='#555')
    ax.set_title("Job Timeline  —  blue = selected", fontsize=10, color='#24292f', pad=8)
    plt.tight_layout()

    return jsonify({
        'selected': result['selected'],
        'total_selected': result['total_selected'],
        'exec_time_ms': result['exec_time_ms'],
        'steps': result['steps'],
        'chart': fig_to_b64(fig),
    })


@app.route('/api/scheduling/random')
def api_scheduling_random():
    jobs = generate_random_jobs(6)
    lines = [f"{j['name']}, {j['start']}, {j['end']}" for j in jobs]
    return jsonify({'text': '\n'.join(lines)})


# Network Optimization
@app.route('/api/network', methods=['POST'])
def api_network():
    data = request.json or {}
    graph_text = data.get('graph', '')

    lines = graph_text.strip().splitlines()
    if not lines:
        return _err('No input provided.')

    nodes = [n.strip() for n in lines[0].split(',') if n.strip()]
    edges, errors = [], []
    for i, line in enumerate(lines[1:], 1):
        parts = [p.strip() for p in line.split(',')]
        if len(parts) != 3:
            errors.append(f"Line {i+1}: expected 'u, v, weight'")
            continue
        u, v, w_str = parts
        try:
            w = float(w_str)
            if w <= 0:
                errors.append(f"Line {i+1}: weight must be positive")
                continue
            edges.append({'u': u, 'v': v, 'weight': w})
        except ValueError:
            errors.append(f"Line {i+1}: weight must be a number")

    if errors:
        return _err(errors)
    if not nodes or not edges:
        return _err('Need at least one node and one edge.')

    result = kruskal_mst(nodes, edges)
    mst = result['mst_edges']

    G = nx.Graph()
    G.add_nodes_from(nodes)
    for e in edges:
        G.add_edge(e['u'], e['v'], weight=e['weight'])
    pos = nx.spring_layout(G, seed=42)
    mst_set = {(e['u'], e['v']) for e in mst} | {(e['v'], e['u']) for e in mst}

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 4))
    fig.patch.set_facecolor('#ffffff')

    for ax, title, node_c, edge_c, edge_list in [
        (ax1, 'Original Graph', '#4361ee', '#c0c8f8', edges),
        (ax2, 'Minimum Spanning Tree', '#2ec4b6', '#2ec4b6', mst),
    ]:
        ax.set_facecolor('#ffffff')
        G2 = nx.Graph()
        G2.add_nodes_from(nodes)
        for e in edge_list:
            G2.add_edge(e['u'], e['v'])
        nx.draw_networkx_nodes(G2, pos, node_color=node_c, node_size=520, ax=ax, alpha=0.95)
        nx.draw_networkx_labels(G2, pos, ax=ax, font_color='white', font_size=9, font_weight='bold')
        nx.draw_networkx_edges(G2, pos, ax=ax, edge_color=edge_c, width=2)
        labels = {(e['u'], e['v']): e['weight'] for e in edge_list}
        nx.draw_networkx_edge_labels(G2, pos, labels, ax=ax, font_size=8, font_color='#444')
        ax.set_title(title, fontsize=10, color='#24292f', pad=8)
        ax.axis('off')

    plt.tight_layout()

    return jsonify({
        'mst_edges': result['mst_edges'],
        'total_weight': result['total_weight'],
        'exec_time_ms': result['exec_time_ms'],
        'steps': result['steps'],
        'chart': fig_to_b64(fig),
    })


@app.route('/api/network/random')
def api_network_random():
    nodes, edges = generate_random_graph(5)
    lines = [','.join(nodes)]
    for e in edges:
        lines.append(f"{e['u']},{e['v']},{e['weight']}")
    return jsonify({'text': '\n'.join(lines)})


# Conflict Resolution
@app.route('/api/conflict', methods=['POST'])
def api_conflict():
    data = request.json or {}
    graph_text = data.get('graph', '')
    try:
        max_colors = int(data.get('max_colors', 4))
        if max_colors < 1:
            return _err('Max colors must be at least 1.')
    except (TypeError, ValueError):
        return _err('Max colors must be a valid integer.')

    lines = graph_text.strip().splitlines()
    if not lines:
        return _err('No input provided.')

    nodes = [n.strip() for n in lines[0].split(',') if n.strip()]
    edges, errors = [], []
    for i, line in enumerate(lines[1:], 1):
        parts = [p.strip() for p in line.split(',')]
        if len(parts) != 2:
            errors.append(f"Line {i+1}: expected 'u, v'")
            continue
        edges.append((parts[0], parts[1]))

    if errors:
        return _err(errors)
    if not nodes:
        return _err('Need at least one node.')

    result = graph_coloring(nodes, edges, max_colors)

    G = nx.Graph()
    G.add_nodes_from(nodes)
    G.add_edges_from(edges)
    pos = nx.spring_layout(G, seed=42)
    node_colors = [
        PALETTE[(result['coloring'].get(n, 1) - 1) % len(PALETTE)]
        if n in result.get('coloring', {}) else '#ccc'
        for n in nodes
    ]

    fig, ax = plt.subplots(figsize=(6, 4.5))
    fig.patch.set_facecolor('#ffffff')
    ax.set_facecolor('#ffffff')
    nx.draw_networkx_nodes(G, pos, node_color=node_colors, node_size=580, ax=ax, alpha=0.95)
    nx.draw_networkx_labels(G, pos, ax=ax, font_color='white', font_size=9, font_weight='bold')
    nx.draw_networkx_edges(G, pos, ax=ax, edge_color='#c5cae9', width=1.8)
    ax.set_title("Graph Coloring", fontsize=10, color='#24292f', pad=8)
    ax.axis('off')
    plt.tight_layout()

    return jsonify({
        'coloring': result['coloring'],
        'colors_used': result['colors_used'],
        'success': result['success'],
        'exec_time_ms': result['exec_time_ms'],
        'steps': result['steps'],
        'chart': fig_to_b64(fig),
    })


@app.route('/api/conflict/random')
def api_conflict_random():
    nodes, edges = generate_random_conflict_graph(5)
    lines = [','.join(nodes)]
    for u, v in edges:
        lines.append(f"{u},{v}")
    return jsonify({'text': '\n'.join(lines)})


if __name__ == '__main__':
    app.run(debug=True, port=5000)