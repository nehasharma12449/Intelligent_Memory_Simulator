import streamlit as st
import pandas as pd
import plotly.express as px

# ==========================================
# PAGE CONFIGURATION
# ==========================================

st.set_page_config(
    page_title="Intelligent Memory Management Simulator",
    page_icon="💻",
    layout="wide"
)

# ==========================================
# CUSTOM DESIGN
# ==========================================

st.title("🖥️ Intelligent Memory Management")
st.subheader("Page Replacement Simulator")

st.write(
    "An interactive platform to simulate, visualize "
    "and compare different page replacement algorithms."
)

st.divider()

# ==========================================
# DASHBOARD
# ==========================================

col1, col2, col3 = st.columns(3)

with col1:
    st.metric("Algorithms", "3")

with col2:
    st.metric("Simulation", "Interactive")

with col3:
    st.metric("Technology", "Python")

st.divider()

# ==========================================
# MEMORY INPUT
# ==========================================

st.header("⚙️ Memory Configuration")

col1, col2 = st.columns(2)

with col1:
    frames = st.number_input(
        "Number of Memory Frames",
        min_value=1,
        max_value=10,
        value=3
    )

with col2:
    reference_input = st.text_input(
        "Page Reference String",
        "7, 0, 1, 2, 0, 3, 0, 4"
    )

# ==========================================
# FIFO ALGORITHM
# ==========================================

def fifo(pages, frame_count):

    memory = [None] * frame_count
    pointer = 0

    history = []
    faults = 0
    hits = 0

    for step, page in enumerate(pages, start=1):

        replaced = "-"
        explanation = ""

        if page in memory:

            status = "Hit"
            hits += 1

            explanation = (
                f"Page {page} is already present in memory."
            )

        else:

            status = "Fault"
            faults += 1

            if None in memory:

                index = memory.index(None)
                memory[index] = page

                explanation = (
                    f"Page {page} loaded into an empty frame."
                )

            else:

                removed = memory[pointer]
                replaced = removed

                memory[pointer] = page

                explanation = (
                    f"Page {removed} replaced by page {page} "
                    "because it entered memory first."
                )

                pointer = (pointer + 1) % frame_count

        history.append({
            "Step": step,
            "Requested Page": page,
            **{
                f"Frame {i+1}": memory[i]
                for i in range(frame_count)
            },
            "Status": status,
            "Replaced Page": replaced,
            "Explanation": explanation
        })

    return history, faults, hits


# ==========================================
# LRU ALGORITHM
# ==========================================

def lru(pages, frame_count):

    memory = [None] * frame_count
    last_used = {}

    history = []
    faults = 0
    hits = 0

    for step, page in enumerate(pages, start=1):

        replaced = "-"
        explanation = ""

        if page in memory:

            status = "Hit"
            hits += 1

            explanation = (
                f"Page {page} is already present in memory."
            )

        else:

            status = "Fault"
            faults += 1

            if None in memory:

                index = memory.index(None)
                memory[index] = page

                explanation = (
                    f"Page {page} loaded into an empty frame."
                )

            else:

                least_recent_page = min(
                    memory,
                    key=lambda x: last_used[x]
                )

                index = memory.index(least_recent_page)

                replaced = least_recent_page

                memory[index] = page

                explanation = (
                    f"Page {least_recent_page} replaced by "
                    f"page {page} because it was least recently used."
                )

        last_used[page] = step

        history.append({
            "Step": step,
            "Requested Page": page,
            **{
                f"Frame {i+1}": memory[i]
                for i in range(frame_count)
            },
            "Status": status,
            "Replaced Page": replaced,
            "Explanation": explanation
        })

    return history, faults, hits


# ==========================================
# OPTIMAL ALGORITHM
# ==========================================

def optimal(pages, frame_count):

    memory = [None] * frame_count

    history = []
    faults = 0
    hits = 0

    for i, page in enumerate(pages):

        replaced = "-"
        explanation = ""

        if page in memory:

            status = "Hit"
            hits += 1

            explanation = (
                f"Page {page} is already present in memory."
            )

        else:

            status = "Fault"
            faults += 1

            if None in memory:

                index = memory.index(None)
                memory[index] = page

                explanation = (
                    f"Page {page} loaded into an empty frame."
                )

            else:

                future_pages = pages[i + 1:]

                future_positions = []

                for current_page in memory:

                    if current_page in future_pages:

                        position = future_pages.index(
                            current_page
                        )

                        future_positions.append(position)

                    else:

                        future_positions.append(float("inf"))

                index = future_positions.index(
                    max(future_positions)
                )

                replaced = memory[index]

                memory[index] = page

                explanation = (
                    f"Page {replaced} replaced by page {page} "
                    "because it will not be needed soonest "
                    "(or will not be needed again)."
                )

        history.append({
            "Step": i + 1,
            "Requested Page": page,
            **{
                f"Frame {j+1}": memory[j]
                for j in range(frame_count)
            },
            "Status": status,
            "Replaced Page": replaced,
            "Explanation": explanation
        })

    return history, faults, hits


# ==========================================
# START SIMULATION
# ==========================================

if st.button(
    "🚀 Start Simulation",
    use_container_width=True
):

    try:

        if not reference_input.strip():

            st.error("Please enter a page reference string.")

        else:

            parts = reference_input.split(",")

            if any(not part.strip() for part in parts):
                raise ValueError

            pages = [
                int(part.strip())
                for part in parts
            ]

            if any(page < 0 for page in pages):

                st.error("Page numbers cannot be negative.")

            else:

                # RUN ALGORITHMS

                results = {
                    "FIFO": fifo(pages, int(frames)),
                    "LRU": lru(pages, int(frames)),
                    "Optimal": optimal(pages, int(frames))
                }

                st.divider()

                # ==================================
                # COMPARISON
                # ==================================

                st.header("📊 Algorithm Comparison")

                comparison = []

                for name, result in results.items():

                    history, faults, hits = result

                    comparison.append({

                        "Algorithm": name,

                        "Page Faults": faults,

                        "Page Hits": hits,

                        "Hit Ratio (%)": round(
                            hits / len(pages) * 100, 2
                        ),

                        "Fault Ratio (%)": round(
                            faults / len(pages) * 100, 2
                        )
                    })

                df = pd.DataFrame(comparison)

                best = df.loc[
                    df["Page Faults"].idxmin()
                ]

                # ==================================
                # METRICS
                # ==================================

                col1, col2, col3 = st.columns(3)

                with col1:

                    st.metric(
                        "Best Algorithm",
                        best["Algorithm"]
                    )

                with col2:

                    st.metric(
                        "Minimum Page Faults",
                        int(best["Page Faults"])
                    )

                with col3:

                    st.metric(
                        "Maximum Page Hits",
                        int(df["Page Hits"].max())
                    )

                st.dataframe(
                    df,
                    use_container_width=True,
                    hide_index=True
                )

                # ==================================
                # GRAPHS
                # ==================================

                st.subheader("Page Fault Comparison")

                fig = px.bar(
                    df,
                    x="Algorithm",
                    y="Page Faults",
                    color="Algorithm",
                    text="Page Faults",
                    title="Comparison of Page Faults"
                )

                st.plotly_chart(
                    fig,
                    use_container_width=True
                )

                st.subheader("Page Hit Comparison")

                fig2 = px.bar(
                    df,
                    x="Algorithm",
                    y="Page Hits",
                    color="Algorithm",
                    text="Page Hits",
                    title="Comparison of Page Hits"
                )

                st.plotly_chart(
                    fig2,
                    use_container_width=True
                )

                # ==================================
                # VISUAL MEMORY SIMULATION
                # ==================================

                st.divider()

                st.header("🧠 Visual Memory Simulation")

                st.write(
                    "See how memory frames change after "
                    "every page request."
                )

                selected_algorithm = st.selectbox(
                    "Select Algorithm",
                    ["FIFO", "LRU", "Optimal"]
                )

                history = results[selected_algorithm][0]

                for record in history:

                    st.markdown(
                        f"### Step {record['Step']} "
                        f"| Requested Page: "
                        f"{record['Requested Page']}"
                    )

                    memory_cols = st.columns(int(frames))

                    for i in range(int(frames)):

                        frame_value = record[f"Frame {i+1}"]

                        with memory_cols[i]:

                            st.markdown(
                                f"**Frame {i+1}**"
                            )

                            if frame_value is None:
                                st.info("Empty")

                            else:
                                st.metric(
                                    "Page",
                                    frame_value
                                )

                    if record["Status"] == "Hit":

                        st.success("🟢 PAGE HIT")

                    else:

                        st.error("🔴 PAGE FAULT")

                    st.write(
                        "**Replaced Page:**",
                        record["Replaced Page"]
                    )

                    st.info(record["Explanation"])

                    st.divider()

                # ==================================
                # DETAILED TABLES
                # ==================================

                st.header("📋 Detailed Simulation Tables")

                for name, result in results.items():

                    history, faults, hits = result

                    with st.expander(
                        f"{name} Algorithm - Full Details"
                    ):

                        detail_df = pd.DataFrame(history)

                        st.dataframe(
                            detail_df,
                            use_container_width=True,
                            hide_index=True
                        )

                        st.write(
                            "Total Page Faults:", faults
                        )

                        st.write(
                            "Total Page Hits:", hits
                        )

                # ==================================
                # INTELLIGENT ANALYSIS
                # ==================================

                st.divider()

                st.header("🔍 Intelligent Analysis")

                minimum_faults = df["Page Faults"].min()

                winners = df[
                    df["Page Faults"] == minimum_faults
                ]["Algorithm"].tolist()

                if len(winners) == 1:

                    st.success(
                        f"{winners[0]} is the best-performing "
                        f"algorithm for this input with "
                        f"{int(minimum_faults)} page faults."
                    )

                else:

                    st.success(
                        "The following algorithms achieved "
                        f"the lowest page faults: "
                        f"{', '.join(winners)}."
                    )

                st.write(
                    "The simulator evaluates all three "
                    "algorithms using the same page reference "
                    "string and memory frame count."
                )

    except ValueError:

        st.error(
            "Invalid input! Enter valid page numbers "
            "separated by commas."
        )


# ==========================================
# FOOTER
# ==========================================

st.divider()

st.caption(
    "Intelligent Memory Management and Page Replacement "
    "Simulator | MCA Project"
)