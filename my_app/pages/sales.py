import json
import os
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from db_utils import get_local_connection, get_remote_connection, get_docker_connection
import os
# get parent directory


st.set_page_config(page_title="Sales Database", page_icon=":chart_with_upwards_trend:", layout="wide",
                   initial_sidebar_state="collapsed")


def search_track_ids(_db, _selected_option, _music_decision):
    if _music_decision == "Track":
        ids = _db.Track.find(
            {"Track.Name": {"$in": _selected_option}},
            {"_id": 0, "Track.TrackId": 1}
        )
    elif _music_decision == "Album":
        ids = _db.Track.find(
            {"Album.Title": {"$in": _selected_option}},
            {"_id": 0, "Track.TrackId": 1}
        )
    elif _music_decision == "Artist":
        ids = _db.Track.find(
            {"Artist.Name": {"$in": _selected_option}},
            {"_id": 0, "Track.TrackId": 1}
        )
    elif _music_decision == "Genre":
        ids = _db.Track.find(
            {"Genre.Name": {"$in": _selected_option}},
            {"_id": 0, "Track.TrackId": 1}
        )
    else:
        raise ValueError("Invalid music decision")
    df_ids = pd.DataFrame(list(ids))
    ids = [
        _ref['TrackId'] for _ref in df_ids['Track']
    ]
    return ids


def search_employee_ids(_db, _selected_employees):
    first_names = [
        _ref.split(" ")[0] for _ref in _selected_employees
    ]
    last_names = [
        _ref.split(" ")[1] for _ref in _selected_employees
    ]

    ids = _db.Employee.find(
        {"FirstName": {"$in": first_names}, "LastName": {"$in": last_names}},
        {"_id": 0, "Employee.EmployeeId": 1}
    )

    df_ids = pd.DataFrame(list(ids))
    return ids


path = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir, os.pardir))

if os.environ.get('DOCKER_BUILD') == "True":
    db = get_docker_connection()
    print("Docker connection")
else:
    db = get_local_connection()
    print("Local connection")


if "run" not in st.session_state:
    st.session_state.run = False
if "back" not in st.session_state:
    st.session_state.back = False
if "temporal_chart" not in st.session_state:
    st.session_state.temporal_chart = False

st.markdown(
    """
    <h1 style='text-align: center;'>Sales Database</h1>
    """,
    unsafe_allow_html=True
)

fields = {
    "Artist": "Artist.Name",
    "Album": "Album.Title",
    "Track": "Track.Name",
    "Genre": "Genre.Name",
}
decision_map = {
    "Track": "$TrackName",
    "Album": "$AlbumName",
    "Artist": "$ArtistName",
    "Genre": "$GenreName"
}


def run_true():
    st.session_state.run = True


def run_false():
    st.session_state.run = False


central_column_width = 0.4
side_column_width = (1 - central_column_width) / 2
_, central_column, _ = st.columns([side_column_width, central_column_width, side_column_width])

with central_column:
    decision = st.selectbox(
        label="Start by choosing whether to view sales by employee, customer, or music",
        options=("Sales by Employee", "Sales by Customer", "Sales by Music"),
        index=None,
        on_change=run_false
    )
    if decision == "Sales by Music":
        music_decision = st.selectbox(
            label="Now you can choose weather to select a track, an album, an artist or a genre",
            options=("Track", "Album", "Artist", "Genre"),
            index=None,
            on_change=run_false
        )
        if music_decision:
            options = db.Track.distinct(fields[music_decision]) if not None else []
            options = sorted(options)
            options.insert(0, "Select All")
            selected_option = st.multiselect(
                label=f"Select {music_decision}, select multiple options for comparing sales",
                options=options,
                on_change=run_false,
            )
            if "Select All" in selected_option:
                selected_option = options[1:]  # Exclude "Select All" from the selection

            if selected_option:
                st.session_state.run = False
                run = st.button(label="Run Query", use_container_width=True)
                if run:
                    run_true()

    elif decision == "Sales by Employee":
        roles = db.Employee.distinct("Title")
        employee_role = st.multiselect(
            label="Select the role of the employee",
            options=roles,
            on_change=run_false
        )
        if employee_role:
            results = db.Employee.aggregate([
                {
                    "$match": {
                        "Title": {
                            "$in": employee_role
                        }
                    }
                },
                {
                    "$project": {
                        "Fullname": {
                            "$concat": ["$FirstName", " ", "$LastName", " - ", "$Title"]
                        },
                        "EmployeeId": 1,
                        "_id": 0
                    }
                }
            ])
            results = pd.DataFrame(list(results))
            full_names = results["Fullname"].tolist()
            ids_employee = results["EmployeeId"].tolist()
            dict_employee = {
                _ref['Fullname'].split(" - ")[0]: _ref['EmployeeId'] for _ref in results.to_dict(orient="records")
            }
            full_names.insert(0, "Select All")
            selected_employees = st.multiselect(
                label="Select Employees",
                options=full_names,
                on_change=run_false
            )
            if "Select All" in selected_employees:
                selected_employees = full_names[1:]
            selected_employees_ids = [
                dict_employee[opt.split(" - ")[0]] for opt in selected_employees
            ]
            if selected_employees:
                selected_employees = [f.split(" - ")[0] for f in selected_employees]

                run = st.button(label="Run Query", use_container_width=True)
                if run:
                    run_true()

    elif decision == "Sales by Customer":

        result = db.Customer.find(
            {},
            {
                "_id": 0,
                "CustomerId": 1,
                "Name": {
                    "$concat": ["$FirstName", " ", "$LastName"]
                }
            }
        )
        result = pd.DataFrame(list(result))
        id_to_name = {
            _ref['CustomerId']: _ref['Name'] for _ref in result.to_dict(orient="records")
        }
        name_to_id = {
            _ref['Name']: _ref['CustomerId'] for _ref in result.to_dict(orient="records")
        }
        customer_selected = st.multiselect(
            label="Select Customer",
            options=result["Name"].tolist(),
            on_change=run_false
        )
        if customer_selected:
            print(customer_selected)
            run_query = st.button(label="Run Query", use_container_width=True)
            if run_query:
                run_true()









if st.session_state.run == True:
    if decision == "Sales by Music":
        # grafico temporale per le vendite di ogni oggetto selezionato
        with open(path + f'/PipelinesMongoDB/SellPer{music_decision}.json') as f:
            pipeline = json.load(f)
        track_ids = search_track_ids(db, selected_option, music_decision)
        for stage in pipeline:
            if "$match" in stage:
                stage["$match"]["InvoiceLines.TrackId"]["$in"] = track_ids
                break
        try:
            result = db.Invoice.aggregate(pipeline)
            df_result = pd.DataFrame(list(result))
            df_result.set_index("_id", inplace=True)
            df_result.index = df_result.index.str[0]

            # aggiungo un istogramma per riassumere le vendite totali
            indexes = df_result.index
            values = df_result.loc[:, "TotalRevenue"].values.flatten()



            if len(selected_option) < len(options):
                ref = {
                    indexes[i]: values[i] for i in range(len(indexes)) if indexes[i] for i in range(len(indexes)) if
                    indexes[i] in selected_option
                }
                for opt in selected_option:
                    if opt not in list(ref.keys()):
                        ref[opt] = 0.0
                indexes = list(ref.keys())
                values = list(ref.values())

            indexes = list(sorted(indexes, key=lambda x: values[indexes.index(x)], reverse=True))
            values = sorted(values, reverse=True)
            values = np.round(values, decimals = 2)

            bar_fig = go.Figure()
            bar_fig.add_trace(
                go.Bar(
                    x=indexes,
                    y=values,
                    text=values,
                    textposition="auto",
                    textfont=dict(size=12),
                    width=0.5,
                )
            )

            bar_fig.update_layout(
                title=dict(
                    text=f"Total Sales by {music_decision}",
                    font=dict(size=20),
                    xanchor="center",
                    x=0.5,
                    yanchor="top",
                ),
                xaxis_title=music_decision,
                yaxis_title="Total Sales ($)",
                showlegend=False,
            )

            st.plotly_chart(bar_fig, use_container_width=True)

            with open(path + f'/PipelinesMongoDB/DatesInvoice{music_decision}.json') as f:
                pipeline = json.load(f)
            track_ids = search_track_ids(db, selected_option, music_decision)
            for stage in pipeline:
                if "$match" in stage:
                    stage["$match"]["InvoiceLines.TrackId"]["$in"] = track_ids
                    break

            result = db.Invoice.aggregate(pipeline)
            df_result_temporal = pd.DataFrame(list(result))
            df_result_temporal["Date"] = pd.to_datetime(df_result_temporal["Date"])
            df_result_temporal.set_index([df_result_temporal.columns[0], df_result_temporal.columns[1]], inplace=True)
            df_result_temporal.sort_index(level=[0, 1], inplace=True)
            min_date = df_result_temporal.index.get_level_values(1).min()
            max_date = df_result_temporal.index.get_level_values(1).max()
            date_range = pd.date_range(min_date, max_date, freq='D')

            df_result_temporal.sort_index(level=[0, 1], inplace=True)
            for genre in df_result_temporal.index.get_level_values(0).unique():
                missing_dates = date_range.difference(df_result_temporal.loc[genre].index)
                df_result_temporal = pd.concat([
                    df_result_temporal,
                    pd.DataFrame(
                        {'TotalRevenue': 0.0},
                        index=pd.MultiIndex.from_product([[genre],
                                                        pd.to_datetime(
                                                            missing_dates)],
                                                        names=df_result_temporal.index.names))])

            df_result_temporal.sort_index(level=[0, 1], inplace=True)
            df_result_temporal = df_result_temporal.groupby(level=0).resample('ME', level=1).sum()

            line_plot = go.Figure()
            for option in selected_option:
                try:
                    indexes = df_result_temporal.loc[pd.IndexSlice[option, :], :].index.get_level_values(1).unique()
                    values = df_result_temporal.loc[pd.IndexSlice[option, :], "TotalRevenue"].values.flatten()

                    line_plot.add_trace(
                        go.Scatter(
                            x=indexes,
                            y=values,
                            mode="markers+lines",
                            name=option,
                            line=dict(width=2),
                        )
                    )
                except KeyError:
                    continue

            line_plot.update_layout(
                title=dict(
                    text=f"Temporal Chart of Sales by {music_decision}",
                    font=dict(size=20),
                    xanchor="center",
                    x=0.5,
                    yanchor="top",
                ),
                xaxis_title="Date",
                yaxis_title="Total Sales ($)",
                showlegend=True,
                legend=dict(
                    orientation="h",
                    yanchor="bottom",
                    y=-0.5,
                    xanchor="center",
                    x=0.5
                ),
            )

            st.plotly_chart(line_plot, use_container_width=True)
        except KeyError:
            st.warning("No results found for the selected music options.")

    elif decision == "Sales by Employee":

        with open(path + '/PipelinesMongoDB/EmployeeSales.json') as f:
            pipeline = json.load(f)
        for stage in pipeline:
            if "$match" in stage:
                stage["$match"]["SupportRepId"]["$in"] = selected_employees_ids
                break
        results = db.Invoice.aggregate(pipeline)
        df_result = pd.DataFrame(list(results))
        
        try:
            df_result['InvoiceDate'] = pd.to_datetime(df_result['InvoiceDate'])
            df_result.set_index(['EmployeeId', 'InvoiceDate'], inplace=True)
            df_result.sort_index(level=[0, 1], inplace=True)
            min_date = df_result.index.get_level_values(1).min()
            max_date = df_result.index.get_level_values(1).max()
            date_range = pd.date_range(start=min_date, end=max_date, freq='D')

            for employee_id in df_result.index.get_level_values(0).unique():
                missing_dates = date_range.difference(df_result.loc[employee_id].index)
                df_result = pd.concat([
                    df_result,
                    pd.DataFrame(
                        {'TotalRevenue': 0.0},
                        index=pd.MultiIndex.from_product(
                            [[employee_id], pd.to_datetime(missing_dates)], names=df_result.index.names)
                    )
                ])
            if len(employee_role) > 1:
                association = db.Employee.find(
                    {"EmployeeId": {"$in": selected_employees_ids}},
                    {
                        "_id": 0,
                        "EmployeeId": 1,
                        "Name": { "$concat": ["$FirstName", " ", "$LastName", " - ", "$Title"] }
                    }
                )
            else:
                association = db.Employee.find(
                    {"EmployeeId": {"$in": selected_employees_ids}},
                    {
                        "_id": 0,
                        "EmployeeId": 1,
                        "Name": { "$concat": ["$FirstName", " ", "$LastName"] }
                    }
                )
            association = pd.DataFrame(list(association))
            association = {
                _ref['EmployeeId']: _ref['Name'] for _ref in association.to_dict(orient="records")
            }


            df_result.sort_index(level=[0, 1], inplace=True)
            df_result = df_result.groupby(level=0).resample('ME', level=1).sum()

            bar_fig = go.Figure()
            values = df_result.groupby(level = 0).sum().values.flatten()
            indexes = [
                association[_ref] for _ref in df_result.index.get_level_values(0).unique()
            ]
            for name in list(association.values()):
                if name not in indexes:
                    indexes.append(name)
                    values = np.append(values, 0.0)

            indexes = [x for _, x in sorted(zip(values, indexes), reverse=True)]
            values = sorted(values, reverse=True)
            bar_fig.add_trace(
                go.Bar(
                    x = indexes,
                    y = values,
                    text = values,
                    textposition="auto",
                    textfont=dict(size=12),
                    width=0.5,
                )
            )

            st.plotly_chart(bar_fig, use_container_width=True)

            # temporal chart

            line_plot = go.Figure()
            for employee in df_result.index.get_level_values(0).unique():
                indexes = df_result.loc[pd.IndexSlice[employee, :], :].index.get_level_values(1).unique()
                values = df_result.loc[pd.IndexSlice[employee, :], "TotalRevenue"].values.flatten()

                line_plot.add_trace(
                    go.Scatter(
                        x=indexes,
                        y=values,
                        mode="markers+lines",
                        name=association[employee],
                        line=dict(width=2),
                    )
                )

            line_plot.update_layout(
                title=dict(
                    text=f"Temporal Chart of Sales by Employee",
                    font=dict(size=20),
                    xanchor="center",
                    x=0.5,
                    yanchor="top",
                ),
                xaxis_title="Date",
                yaxis_title="Total Sales ($)",
                showlegend=True,
                legend=dict(
                    orientation="h",
                    yanchor="bottom",
                    y=-0.5,
                    xanchor="center",
                    x=0.5
                ),
            )

            st.plotly_chart(line_plot, use_container_width=True)
        except KeyError:
            st.warning("No results found for the selected employees.")

    elif decision == "Sales by Customer":
        ids_customer_selected = [
            name_to_id[customer_selected] for customer_selected in customer_selected
        ]
        print(ids_customer_selected)

        # voglio ottenere uno storico degli acquisti diviso per data, con il totale degli acquisti per ogni giorno
        with open(path + '/PipelinesMongoDB/CustomerHistory.json') as f:
            pipeline = json.load(f)
        for stage in pipeline:
            if "$match" in stage:
                stage["$match"]["CustomerId"]["$in"] = ids_customer_selected
        try:
            result = db.Invoice.aggregate(pipeline)
            df_result = pd.DataFrame(list(result))
            df_result['Date'] = pd.to_datetime(df_result['Date'])
            df_result.set_index(['CustomerId', 'Date'], inplace=True)
            df_result.sort_index(level=[0, 1], inplace=True)
            min_date = df_result.index.get_level_values(1).min()
            max_date = df_result.index.get_level_values(1).max()
            date_range = pd.date_range(start=min_date, end=max_date, freq='D')

            for _id in df_result.index.get_level_values(0).unique():
                missing_dates = date_range.difference(df_result.loc[_id].index)
                df_result = pd.concat([
                    df_result,
                    pd.DataFrame(
                        {'TotalRevenue': 0.0},
                        index=pd.MultiIndex.from_product([[_id],
                                                        pd.to_datetime(
                                                            missing_dates)],
                                                        names=df_result.index.names))])

            df_result.sort_index(level=[0, 1], inplace=True)
            df_result = df_result.groupby(level=0).resample('ME', level=1).sum()

            temp_chart = go.Figure()
            for customer in df_result.index.get_level_values(0).unique():
                indexes = df_result.loc[pd.IndexSlice[customer, :], :].index.get_level_values(1).unique()
                values = df_result.loc[pd.IndexSlice[customer, :], "TotalRevenue"].values.flatten()

                temp_chart.add_trace(
                    go.Scatter(
                        x=indexes,
                        y=values,
                        mode="markers+lines",
                        name=id_to_name[customer],
                        line=dict(width=2),
                        legendgroup=id_to_name[customer],
                        hoverinfo="name"
                    )
                )

            temp_chart.update_layout(
                title=dict(
                    text=f"Temporal Chart of Sales by Customer",
                    font=dict(size=20),
                    xanchor="center",
                    x=0.5,
                    yanchor="top",
                ),
                xaxis_title="Date",
                yaxis_title="Total Sales ($)",
                showlegend=True,
                legend=dict(
                    orientation="h",
                    yanchor="bottom",
                    y=-0.5,
                    xanchor="center",
                    x=0.5,
                    itemclick = "toggleothers",
                    itemdoubleclick = "toggle",
                )
            )

            st.plotly_chart(temp_chart, use_container_width=True)

            # grafico a barre per le vendite totali

            bar_fig = go.Figure()
            values = df_result.groupby(level = 0).sum().values.flatten()
            indexes = [
                id_to_name[_ref] for _ref in df_result.index.get_level_values(0).unique()
            ]
            for name in list(customer_selected):
                if name not in indexes:
                    indexes.append(name)
                    values = np.append(values, 0.0)
            indexes = [x for _, x in sorted(zip(values, indexes), reverse=True)]
            values = sorted(values, reverse=True)

            bar_fig.add_trace(
                go.Bar(
                    x = indexes,
                    y = values,
                    text = values,
                    textposition="auto",
                    textfont=dict(size=12),
                    width=0.5,
                )
            )

            bar_fig.update_layout(
                title=dict(
                    text=f"Total Sales by Customer",
                    font=dict(size=20),
                    xanchor="center",
                    x=0.5,
                    yanchor="top",
                ),
                xaxis_title="Customer",
                yaxis_title="Total Sales ($)",
                showlegend=False,
            )

            st.plotly_chart(bar_fig, use_container_width=True)
        except KeyError:
            st.warning("No results found for the selected customers.")