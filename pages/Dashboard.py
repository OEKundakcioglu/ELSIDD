import streamlit as st
from streamlit_extras.switch_page_button import switch_page

from src.visualizer import *

st.set_page_config(page_title="Dashboard", page_icon=":bar_chart:", layout="wide")
hide_streamlit_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            </style>
            """
st.markdown(hide_streamlit_style, unsafe_allow_html=True)


def dashboard():
    st.title(":bar_chart: Dashboard")

    if "solution" not in st.session_state:
        st.warning("Solve the problem first!")

        if st.button("Solver"):
            switch_page("Solver")

        st.stop()

    revenue_col, stores_col, items_col = st.columns([1, 1, 1])

    solution_df = st.session_state.solution_df
    revenue = int(st.session_state.solution["solution"]["revenue"])
    n_store = int(st.session_state.solution["number_of_stores"])
    n_item = int(st.session_state.solution["number_of_items"])
    n_period = int(st.session_state.solution["number_of_periods"])

    with revenue_col:
        st.header(f"Revenue" + f"\n**{revenue}₺**")
    with stores_col:
        st.header("Stores" + f"\n**{n_store}**")
    with items_col:
        st.header("Items" + f"\n**{n_item}**")

    st.markdown("---")

    col1, col2 = st.columns([1, 0.3])

    with col2:
        store_id = st.selectbox("Select store", solution_df['demand']['store'].unique(), key="store")
        items = st.multiselect("Select items", range(n_item))
        starting_period, ending_period = st.slider("Select period range", value=(0, n_period), min_value=0,
                                                   max_value=n_period)

    with col1:
        if len(items) == 0:
            items = range(n_item)
        st.pyplot(inventories_for_store(solution_df, store_id, list(range(starting_period, ending_period + 1)), items))

    col1, col2 = st.columns([1, 1])
    with col1:
        st.pyplot(top_n_produced_item_averages(solution_df, 5, color="tab:blue"))

    with col2:
        st.pyplot(top_n_remaining_inventories(solution_df, 5, color="tab:orange"))

    col1, col2 = st.columns([0.8, 1])
    with col1:
        st.pyplot(item_demand_pie_chart(solution_df, 5))

    with col2:
        st.pyplot(top_n_demand(solution_df, 5, color="tab:cyan"))

    col1, col2, col3 = st.columns([0.25, 1, 0.25])
    with col2:
        st.pyplot(plot_capacity(solution_df))


if __name__ == "__main__":
    dashboard()
