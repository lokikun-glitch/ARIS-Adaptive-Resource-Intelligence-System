import streamlit as st
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use("Agg")

from algorithms.cargo import fractional_knapsack, generate_random_items


def parse_items_text(text):
    items = []
    errors = []
    for i, line in enumerate(text.strip().splitlines()):
        line = line.strip()
        if not line:
            continue
        parts = [p.strip() for p in line.split(',')]
        if len(parts) != 3:
            errors.append(f"Line {i+1}: expected 'name,weight,profit' got '{line}'")
            continue
        name, w_str, p_str = parts
        try:
            w = float(w_str)
            p = float(p_str)
            if w <= 0 or p <= 0:
                errors.append(f"Line {i+1}: weight and profit must be positive")
                continue
            items.append({'name': name, 'weight': w, 'profit': p})
        except ValueError:
            errors.append(f"Line {i+1}: weight and profit must be numbers")
    return items, errors


def render():
    st.title("Cargo Optimization")
    st.markdown("**Algorithm:** Fractional Knapsack — Greedy  |  **Complexity:** O(n log n)")
    st.markdown("---")

    col1, col2 = st.columns([2, 1])

    with col1:
        st.subheader("Input")
        default_text = "ItemA, 10, 60\nItemB, 20, 100\nItemC, 30, 120"
        items_text = st.text_area(
            "Items (name, weight, profit — one per line)",
            value=default_text,
            height=160,
            key="cargo_items"
        )

    with col2:
        st.subheader("Capacity")
        capacity = st.number_input("Max capacity", min_value=0.1, value=50.0, step=1.0, key="cargo_cap")
        st.markdown(" ")
        if st.button("Random Input", key="cargo_rand"):
            rand_items = generate_random_items(5)
            lines = [f"{it['name']}, {it['weight']}, {it['profit']}" for it in rand_items]
            st.session_state['cargo_items'] = "\n".join(lines)
            st.rerun()

    show_steps = st.checkbox("Show steps", value=False, key="cargo_steps_toggle")

    if st.button("Run Knapsack", key="cargo_run"):
        items, errors = parse_items_text(items_text)

        if errors:
            for e in errors:
                st.error(e)
            return

        if not items:
            st.warning("No valid items found.")
            return

        result = fractional_knapsack(items, capacity)

        st.markdown("---")
        st.subheader("Output")

        sel = result['selected']
        if not sel:
            st.info("No items selected.")
        else:
            lines = []
            for s in sel:
                frac_str = "100%" if s['fraction'] == 1.0 else f"{s['fraction']*100:.1f}%"
                lines.append(
                    f"  {s['name']:12s}  weight={s['weight']:.1f}  taken={frac_str}  profit={s['profit_gained']:.2f}"
                )

            st.text("Selected Items:")
            st.code("\n".join(lines), language=None)
            st.text(f"Total Profit:   {result['total_profit']:.2f}")
            st.text(f"Time Taken:     {result['exec_time_ms']:.4f} ms")

        fig, ax = plt.subplots(figsize=(6, 3))
        names = [s['name'] for s in sel]
        profits = [s['profit_gained'] for s in sel]
        bars = ax.bar(names, profits, color='#3a7abf', edgecolor='#1e4e7c', linewidth=0.8)
        ax.set_ylabel("Profit Gained")
        ax.set_title("Selected Items — Profit Distribution")
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        for bar, val in zip(bars, profits):
            ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.5,
                    f"{val:.1f}", ha='center', va='bottom', fontsize=9)
        plt.tight_layout()
        st.pyplot(fig)
        plt.close(fig)

        if show_steps:
            st.subheader("Steps")
            st.code("\n".join(result['steps']), language=None)
