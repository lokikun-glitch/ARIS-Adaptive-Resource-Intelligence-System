import time


def activity_selection(jobs):
    """
    jobs: list of dicts with keys 'name', 'start', 'end'
    Returns: selected jobs, steps, exec time
    """
    start_time = time.perf_counter()

    sorted_jobs = sorted(jobs, key=lambda x: x['end'])

    selected = []
    steps = []
    last_end = 0

    steps.append("Sorted jobs by finish time:")
    for j in sorted_jobs:
        steps.append(f"  {j['name']} [{j['start']}, {j['end']}]")

    steps.append("\nSelecting non-overlapping activities:")
    for job in sorted_jobs:
        if job['start'] >= last_end:
            selected.append(job)
            last_end = job['end']
            steps.append(f"  Selected: {job['name']} [{job['start']}, {job['end']}]")
        else:
            steps.append(
                f"  Skipped:  {job['name']} [{job['start']}, {job['end']}]"
                f" (conflicts with last end={last_end})"
            )

    end_time = time.perf_counter()
    exec_time = (end_time - start_time) * 1000

    return {
        'selected': selected,
        'total_selected': len(selected),
        'exec_time_ms': exec_time,
        'steps': steps
    }


def generate_random_jobs(n=6):
    import random
    jobs = []
    for i in range(n):
        s = random.randint(0, 18)
        e = s + random.randint(1, 5)
        jobs.append({'name': f"Job-{i+1}", 'start': s, 'end': e})
    return jobs
