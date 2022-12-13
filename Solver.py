import json
import pickle

import pandas as pd
import streamlit as st
from streamlit_extras.switch_page_button import switch_page
from src.data import Parameters
from src.simple_heuristic import SimpleHeuristic
from src.model import Model

st.set_page_config(page_title="Solver", page_icon=":bar_chart:")
hide_streamlit_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            </style>
            """
st.markdown(hide_streamlit_style, unsafe_allow_html=True)


def convert_json(solution):
    temp_solution = {"number_of_items": int(solution["number_of_items"]),
                "number_of_stores": int(solution["number_of_stores"]),
                "number_of_periods": int(solution["number_of_periods"]),

                "solution": {
                    "D": {
                        (int(solution["solution"]["D"][i]["dim0"]),
                         int(solution["solution"]["D"][i]["dim1"]),
                         int(solution["solution"]["D"][i]["dim2"])): float(solution["solution"]["D"][i]["value"])
                        for i in range(len(solution["solution"]["D"]))
                    },

                    "I": {
                        (int(solution["solution"]["I"][i]["dim0"]),
                            int(solution["solution"]["I"][i]["dim1"]),
                            int(solution["solution"]["I"][i]["dim2"])): float(solution["solution"]["I"][i]["value"])
                        for i in range(len(solution["solution"]["I"]))
                    },

                    "I_total": {
                        (int(solution["solution"]["I_total"][i]["dim0"]),
                            int(solution["solution"]["I_total"][i]["dim1"])): float(solution["solution"]["I_total"][i]["value"])
                        for i in range(len(solution["solution"]["I_total"]))
                    },

                    "x": {
                        (int(solution["solution"]["x"][i]["dim0"]),
                            int(solution["solution"]["x"][i]["dim1"])): float(solution["solution"]["x"][i]["value"])
                        for i in range(len(solution["solution"]["x"]))
                    },

                    "z": {
                        (int(solution["solution"]["z"][i]["dim0"]),
                            int(solution["solution"]["z"][i]["dim1"]),
                            int(solution["solution"]["z"][i]["dim2"])): float(solution["solution"]["z"][i]["value"])
                        for i in range(len(solution["solution"]["z"]))
                    },

                    "Z": {
                        (int(solution["solution"]["Z"][i]["dim0"]),
                            int(solution["solution"]["Z"][i]["dim1"])): float(solution["solution"]["Z"][i]["value"])
                        for i in range(len(solution["solution"]["Z"]))
                    },

                    "U": {
                        (int(solution["solution"]["U"][i]["dim0"]),
                            int(solution["solution"]["U"][i]["dim1"]),
                            int(solution["solution"]["U"][i]["dim2"])): float(solution["solution"]["U"][i]["value"])
                        for i in range(len(solution["solution"]["U"]))
                    },

                    "x_binary": {
                        (int(solution["solution"]["x_binary"][i]["dim0"]),
                            int(solution["solution"]["x_binary"][i]["dim1"])): float(solution["solution"]["x_binary"][i]["value"])
                        for i in range(len(solution["solution"]["x_binary"]))
                    },

                    "Z_binary": {
                        (int(solution["solution"]["Z_binary"][i]["dim0"]),
                            int(solution["solution"]["Z_binary"][i]["dim1"])): float(solution["solution"]["Z_binary"][i]["value"])
                        for i in range(len(solution["solution"]["Z_binary"]))
                    },

                    "revenue": float(solution["solution"]["revenue"])
                },
                }

    return temp_solution


def get_solution_as_dict_dataframe(solution):
    data = {}

    for key, value in solution["solution"].items():
        if key == "I":
            key = "inventory_store"
            columns = ["item", "store", "period", "inventory"]
        elif key == "I_total":
            key = "inventory_total"
            columns = ["item", "period", "inventory"]
        elif key == "x":
            key = "production"
            columns = ["item", "period", "production"]
        elif key == "z":
            key = "renewal"
            columns = ["item", "store", "period", "renewal"]
        elif key == "Z":
            key = "renewal_total"
            columns = ["item", "period", "renewal"]
        elif key == "D":
            key = "demand"
            columns = ["item", "store", "period", "demand"]
        elif key == "U":
            key = "inventory_after_renewal"
            columns = ["item", "store", "period", "inventory"]
        elif key == "x_binary":
            continue
        elif key == "Z_binary":
            continue
        elif key == "revenue":
            continue
        else:
            st.write(key)
            raise ValueError(f"Unknown key")

        df = pd.Series(data=value).reset_index()
        df.columns = columns
        data[key] = df

    return data


def main_page():
    st.title("Solver")

    solution_approach = st.radio("***Select Solution Approach***", ["Heuristic", "MILP", "Import"])

    if solution_approach == "Heuristic":
        problem = st.file_uploader("Upload Problem File")
        n_decomposition = st.slider("Decomposition", 1, 10, 1)
        time_limit = int(st.text_input("Enter time limit for each problem (seconds)", value=50))
        st.session_state["n_decomposition"] = n_decomposition

        col1, col2 = st.columns([0.12, 1])
        with col1:
            solve_button = st.button("Solve")
        with col2:
            stop_button = st.button("Stop")

        if solve_button:
            if problem is None:
                st.error("Please upload a problem file!")
                st.stop()

            parameters = Parameters(file=problem)
            st.session_state.parameters = parameters

            simple_heuristic = SimpleHeuristic(parameters, n_decomposition=n_decomposition)
            simple_heuristic.solve(time_limit=time_limit)

            solution = simple_heuristic.import_solution_to_json("solution.json")
            st.session_state.solution = convert_json(solution)
            st.session_state.solution_df = simple_heuristic.solution_df
            st.session_state.revenue = int(simple_heuristic.revenue)

            st.success("Solved!")

        if stop_button:
            st.warning("**Program Stopped!**")
            st.stop()

    if solution_approach == "Import":
        file = st.file_uploader("Upload Solution File")

        if file is not None:
            solution = json.load(file)
            solution = convert_json(solution)
            solution_df = get_solution_as_dict_dataframe(solution)

            st.session_state.solution = solution
            st.session_state.solution_df = solution_df

    if solution_approach == "MILP":
        st.markdown("Heuristic")
        problem = st.file_uploader("Upload Problem File")
        time_limit = int(st.text_input("Enter time limit (seconds)", value=50))

        col1, col2 = st.columns([0.12, 1])

        with col1:
            solve_button = st.button("Solve")
        with col2:
            stop_button = st.button("Stop")

        if solve_button:
            if problem is None:
                st.error("Please upload a problem file!")
                st.stop()

            parameters = Parameters(file=problem)
            st.session_state.parameters = parameters

            model = Model(parameters)
            model.create(initial_factory_inventories={(item, -1): 0 for item in parameters.items},
                         initial_store_inventories={(item, store, -1): 0 for item in parameters.items
                                                    for store in parameters.stores})
            with st.spinner("Solving..."):
                model.solve(time_limit)

            solution = model.export_solution_to_json("solution.json")
            st.session_state.solution = convert_json(solution)
            st.session_state.solution_df = model.get_solution_as_dict_dataframe()
            st.session_state.revenue = model.mdl.solution.objective_value

            st.success("Solved!")

        if stop_button:
            st.warning("**Program Stopped!**")
            st.stop()

    if st.button("Go to Dashboard"):
        switch_page("Dashboard")


if __name__ == "__main__":
    main_page()
