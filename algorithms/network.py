import time


def kruskal_mst(nodes, edges):
    """
    nodes: list of node names (strings)
    edges: list of dicts with keys 'u', 'v', 'weight'
    Returns: MST edges, total weight, steps, exec time
    """
    start_time = time.perf_counter()

    parent = {n: n for n in nodes}
    rank = {n: 0 for n in nodes}

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    def union(a, b):
        ra, rb = find(a), find(b)
        if ra == rb:
            return False
        if rank[ra] < rank[rb]:
            ra, rb = rb, ra
        parent[rb] = ra
        if rank[ra] == rank[rb]:
            rank[ra] += 1
        return True

    sorted_edges = sorted(edges, key=lambda x: x['weight'])
    mst_edges = []
    total_weight = 0
    steps = []

    steps.append("Edges sorted by weight:")
    for e in sorted_edges:
        steps.append(f"  {e['u']} -- {e['v']}  weight={e['weight']}")

    steps.append("\nBuilding MST (Kruskal's):")
    for edge in sorted_edges:
        if union(edge['u'], edge['v']):
            mst_edges.append(edge)
            total_weight += edge['weight']
            steps.append(f"  Added: {edge['u']} -- {edge['v']}  weight={edge['weight']}")
        else:
            steps.append(
                f"  Skipped (cycle): {edge['u']} -- {edge['v']}  weight={edge['weight']}"
            )

        if len(mst_edges) == len(nodes) - 1:
            break

    end_time = time.perf_counter()
    exec_time = (end_time - start_time) * 1000

    return {
        'mst_edges': mst_edges,
        'total_weight': total_weight,
        'exec_time_ms': exec_time,
        'steps': steps
    }


def generate_random_graph(n=5):
    import random
    nodes = [chr(65 + i) for i in range(n)]
    edges = []
    edge_set = set()
    for i in range(n - 1):
        j = random.randint(i + 1, n - 1)
        w = random.randint(1, 20)
        edges.append({'u': nodes[i], 'v': nodes[j], 'weight': w})
        edge_set.add((nodes[i], nodes[j]))

    extra = random.randint(1, n)
    for _ in range(extra):
        i, j = random.sample(range(n), 2)
        u, v = nodes[min(i, j)], nodes[max(i, j)]
        if (u, v) not in edge_set:
            edges.append({'u': u, 'v': v, 'weight': random.randint(1, 20)})
            edge_set.add((u, v))

    return nodes, edges
