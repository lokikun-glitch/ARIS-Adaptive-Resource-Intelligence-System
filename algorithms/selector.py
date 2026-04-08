"""
Rule-based algorithm selector for ARIS.
Detects problem type from keywords and recommends algorithm.

Scoring:
  - Each matched single keyword → 1 point
  - Each matched multi-word phrase → 2 points (higher signal)
Confidence: High (≥4), Medium (2-3), Low (1)
Ambiguity: flagged when top two candidates are within 1 point of each other.
"""

RULES = [
    {
        'keywords': [
            'cargo', 'knapsack', 'item', 'weight', 'profit', 'load', 'pack',
            'bag', 'capacity', 'value', 'carry', 'haul', 'goods', 'shipment'
        ],
        'phrases': [
            'weight limit', 'maximum weight', 'profit maximization',
            'carry items', 'pack items', 'limited capacity', 'load items'
        ],
        'module': 'Cargo Optimization',
        'algorithm': 'Fractional Knapsack (Greedy)',
        'reason': 'Problem involves selecting items with weights and profits under a capacity constraint.',
        'complexity': 'O(n log n)',
    },
    {
        'keywords': [
            'job', 'schedule', 'task', 'meeting', 'activity', 'interval',
            'slot', 'appointment', 'event', 'booking', 'deadline', 'overlap',
            'timetable', 'calendar'
        ],
        'phrases': [
            'time slot', 'non-overlapping', 'start time', 'finish time',
            'maximum tasks', 'maximum jobs', 'no overlap'
        ],
        'module': 'Job Scheduling',
        'algorithm': 'Activity Selection (Greedy)',
        'reason': 'Problem involves selecting the maximum number of non-overlapping time intervals.',
        'complexity': 'O(n log n)',
    },
    {
        'keywords': [
            'network', 'connect', 'cable', 'wire', 'pipe', 'link', 'spanning',
            'graph', 'route', 'node', 'edge', 'infrastructure', 'cost',
            'minimum', 'topology', 'road', 'path'
        ],
        'phrases': [
            'minimum cost', 'spanning tree', 'connect all', 'minimum spanning',
            'total cost', 'network design', 'connect nodes', 'lay cable'
        ],
        'module': 'Network Optimization',
        'algorithm': "Kruskal's MST (Graph)",
        'reason': 'Problem involves connecting all nodes at minimum total edge cost.',
        'complexity': 'O(E log E)',
    },
    {
        'keywords': [
            'conflict', 'color', 'assign', 'clash', 'frequency', 'register',
            'exam', 'resource', 'allocate', 'interference', 'constraint',
            'channel', 'map', 'distinct'
        ],
        'phrases': [
            'no two', 'same resource', 'same color', 'no conflict',
            'resource allocation', 'exam scheduling', 'frequency assignment',
            'register allocation'
        ],
        'module': 'Conflict Resolution',
        'algorithm': 'Graph Coloring (Backtracking)',
        'reason': 'Problem involves assigning resources so no two conflicting entities share the same resource.',
        'complexity': 'O(m^n)',
    },
]


def detect_algorithm(description: str) -> dict:
    description_lower = description.lower()
    scores = []

    for rule in RULES:
        keyword_hits = [kw for kw in rule['keywords'] if kw in description_lower]
        phrase_hits = [ph for ph in rule['phrases'] if ph in description_lower]
        total = len(keyword_hits) + len(phrase_hits) * 2
        scores.append({
            'score': total,
            'rule': rule,
            'keyword_hits': keyword_hits,
            'phrase_hits': phrase_hits,
        })

    scores.sort(key=lambda x: x['score'], reverse=True)
    best = scores[0]

    if best['score'] == 0:
        return {
            'matched': False,
            'message': (
                'Could not determine problem type. '
                'Try using keywords like: cargo/weight, schedule/task, '
                'network/connect, or conflict/assign.'
            ),
        }

    # Confidence tier
    s = best['score']
    if s >= 4:
        tier = 'High'
    elif s >= 2:
        tier = 'Medium'
    else:
        tier = 'Low'

    # Ambiguity: second-best within 1 point
    runner_up = scores[1] if len(scores) > 1 else None
    ambiguous = runner_up and runner_up['score'] > 0 and (s - runner_up['score']) <= 1

    all_hits = best['keyword_hits'] + best['phrase_hits']
    confidence_parts = [f"{tier} confidence"]
    confidence_parts.append(f"{s} signal{'s' if s != 1 else ''} matched")
    if ambiguous:
        confidence_parts.append(f"also consider: {runner_up['rule']['module']}")

    return {
        'matched': True,
        'module': best['rule']['module'],
        'algorithm': best['rule']['algorithm'],
        'reason': best['rule']['reason'],
        'complexity': best['rule']['complexity'],
        'confidence': ' · '.join(confidence_parts),
        'matched_signals': all_hits,
    }
