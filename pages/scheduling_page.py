import streamlit as st
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use("Agg")

from algorithms.scheduling import activity_selection, generate_random_jobs


def parse_jobs_text(text):
    jobs = []
    errors = []
    for i, line in enumerate(text.strip().splitlines()):
        line = line.strip()
        if not line:
            continue
        parts = [p.strip() for p in line.split(',')]
        if len(parts) != 3:
            errors.append(f"Line {i+1}: expected 'name,start,end' got '{line}'")
            continue
        name, s_str, e_str = parts
        try:
            s = int(s_str)
            e = int(e_str)
            if s >= e:
                errors.append(f"Line {i+1}: start must be less than end")
                continue
            jobs.append({'name': name, 'start': s, 'end': e})
        except ValueError:
            errors.append(f"Line {i+1}: start and end must be integers")
    return jobs, errors


def render():
    st.title("Job Scheduling")
    st.markdown("**Algorithm:** Activity Selection — Greedy  |  **Complexity:** O(n log n)")
    st.markdown("---")

    col1, col2 = st.columns([2, 1])

    with col1:
        st.subheader("Input")
        default_text = "Job1, 1, 4\nJob2, 3, 5\nJob3, 0, 6\nJob4, 5, 7\nJob5, 3, 9\nJob6, 5, 9"
        jobs_text = st.text_area(
            "Jobs (name, start, end — one per line)",
            value=default_text,
            height=160,
            key="sched_jobs"
        )

    with col2:
        st.subheader("Options")
        st.markdown(" ")
        if st.button("Random Input", key="sched_rand"):
            rand_jobs = generate_random_jobs(6)
            lines = [f"{j['name']}, {j['start']}, {j['end']}" for j in rand_jobs]
            st.session_state['sched_jobs'] = "\n".join(lines)
            st.rerun()

    show_steps = st.checkbox("Show steps", value=False, key="sched_steps_toggle")

    if st.button("Run Scheduling", key="sched_run"):
        jobs, errors = parse_jobs_text(jobs_text)

        if errors:
            for e in errors:
                st.error(e)
            return

        if not jobs:
            st.warning("No valid jobs found.")
            return

        result = activity_selection(jobs)

        st.markdown("---")
        st.subheader("Output")

        sel = result['selected']
        if not sel:
            st.info("No jobs selected.")
        else:
            lines = []
            for s in sel:
                lines.append(f"  {s['name']:8s}  [{s['start']}, {s['end']}]")

            st.text("Selected Jobs:")
            st.code("\n".join(lines), language=None)
            st.text(f"Total Selected: {result['total_selected']}")
            st.text(f"Time Taken:     {result['exec_time_ms']:.4f} ms")

        # Simple visualization: timeline
        fig, ax = plt.subplots(figsize=(8, 4))
        for job in jobs:
            ax.plot([job['start'], job['end']], [0, 0], 'o-', label=job['name'], markersize=6)
        for s in sel:
            ax.plot([s['start'], s['end']], [1, 1], 'ro-', linewidth=3, markersize=8)
        ax.set_yticks([0, 1])
        ax.set_yticklabels(['All Jobs', 'Selected'])
        ax.set_xlabel("Time")
        ax.grid(True, alpha=0.3)
        plt.tight_layout()
        st.pyplot(fig)
        plt.close(fig)

        if show_steps:
            st.subheader("Steps")
            st.code("\n".join(result['steps']), language=None)