import time

# Safety caps to prevent exponential blowup on the server
MAX_NODES = 25
MAX_STEPS = 1000


def graph_coloring(nodes, edges, max_colors=None):
    """
    nodes: list of node names
    edges: list of (u, v) tuples
    max_colors: optional limit; if None uses len(nodes)
    Returns: coloring dict, colors used, steps, exec time
    """
    if len(nodes) > MAX_NODES:
        return {
            'coloring': {},
            'colors_used': 0,
            'success': False,
            'exec_time_ms': 0,
            'steps': [f'Input rejected: too many nodes ({len(nodes)}). Limit is {MAX_NODES}.'],
            'error': f'Graph coloring is limited to {MAX_NODES} nodes to prevent server timeout.'
        }

    start_time = time.perf_counter()

    if max_colors is None:
        max_colors = len(nodes)

    adj = {n: set() for n in nodes}
    for u, v in edges:
        if u in adj and v in adj:
            adj[u].add(v)
            adj[v].add(u)

    coloring = {}
    steps = []
    step_count = [0]   # mutable counter accessible in nested function
    limit_hit = [False]

    steps.append(f"Nodes: {nodes}")
    steps.append(f"Max colors allowed: {max_colors}")
    steps.append("\nBacktracking coloring:")

    def is_safe(node, color):
        return all(coloring.get(neighbor) != color for neighbor in adj[node])

    def backtrack(idx):
        if limit_hit[0]:
            return False
        if idx == len(nodes):
            return True
        node = nodes[idx]
        for color in range(1, max_colors + 1):
            if is_safe(node, color):
                coloring[node] = color
                step_count[0] += 1
                if step_count[0] <= MAX_STEPS:
                    steps.append(f"  Assign {node} -> Color {color}")
                elif step_count[0] == MAX_STEPS + 1:
                    steps.append(f"  ... (step log truncated after {MAX_STEPS} steps)")
                if backtrack(idx + 1):
                    return True
                del coloring[node]
                step_count[0] += 1
                if step_count[0] <= MAX_STEPS:
                    steps.append(f"  Backtrack: unassign {node}")
        return False

    success = backtrack(0)
    end_time = time.perf_counter()
    exec_time = (end_time - start_time) * 1000

    colors_used = len(set(coloring.values())) if coloring else 0

    return {
        'coloring': coloring,
        'colors_used': colors_used,
        'success': success,
        'exec_time_ms': exec_time,
        'steps': steps
    }


def generate_random_conflict_graph(n=5):
    import random
    nodes = [f"T{i+1}" for i in range(n)]
    edges = set()
    for i in range(n):
        for j in range(i + 1, n):
            if random.random() < 0.4:
                edges.add((nodes[i], nodes[j]))
    return nodes, list(edges)
