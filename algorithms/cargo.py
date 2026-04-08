import time


def fractional_knapsack(items, capacity):
    """
    items: list of dicts with keys 'name', 'weight', 'profit'
    capacity: float
    Returns: selected items with fraction taken, total profit, steps
    """
    start = time.perf_counter()

    for item in items:
        item['ratio'] = item['profit'] / item['weight']

    sorted_items = sorted(items, key=lambda x: x['ratio'], reverse=True)

    total_profit = 0.0
    remaining = capacity
    selected = []
    steps = []

    steps.append(f"Capacity: {capacity}")
    steps.append("Sorted by profit/weight ratio (descending):")
    for item in sorted_items:
        steps.append(f"  {item['name']} -> ratio={item['ratio']:.3f}")

    for item in sorted_items:
        if remaining <= 0:
            break
        if item['weight'] <= remaining:
            fraction = 1.0
            taken_weight = item['weight']
        else:
            fraction = remaining / item['weight']
            taken_weight = remaining

        profit_gained = fraction * item['profit']
        total_profit += profit_gained
        remaining -= taken_weight

        selected.append({
            'name': item['name'],
            'weight': item['weight'],
            'fraction': fraction,
            'profit_gained': profit_gained
        })

        steps.append(
            f"Take {fraction*100:.1f}% of {item['name']} "
            f"(weight={taken_weight:.2f}, profit={profit_gained:.2f})"
        )

    end = time.perf_counter()
    exec_time = (end - start) * 1000

    return {
        'selected': selected,
        'total_profit': total_profit,
        'exec_time_ms': exec_time,
        'steps': steps
    }


def generate_random_items(n=5):
    import random
    names = [f"Item-{chr(65+i)}" for i in range(n)]
    items = []
    for name in names:
        w = round(random.uniform(1, 20), 1)
        p = round(random.uniform(5, 100), 1)
        items.append({'name': name, 'weight': w, 'profit': p})
    return items
