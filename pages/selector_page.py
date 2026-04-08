import streamlit as st
from algorithms.selector import detect_algorithm


def render():
    st.title("Algorithm Selector")
    st.markdown("Describe your problem in plain text, and I'll suggest the best algorithm.")
    st.markdown("---")

    description = st.text_area(
        "Problem Description",
        placeholder="e.g., I need to pack items with weights and profits into a cargo hold with limited capacity.",
        height=100,
        key="sel_desc"
    )

    if st.button("Detect Algorithm", key="sel_run"):
        if not description.strip():
            st.warning("Please enter a description.")
            return

        result = detect_algorithm(description)

        st.markdown("---")
        st.subheader("Recommendation")

        if not result['matched']:
            st.error(result['message'])
        else:
            st.success(f"**Module:** {result['module']}")
            st.info(f"**Algorithm:** {result['algorithm']}")
            st.text(f"**Reason:** {result['reason']}")
            st.text(f"**Complexity:** {result['complexity']}")
            st.text(f"**Confidence:** {result['confidence']}")