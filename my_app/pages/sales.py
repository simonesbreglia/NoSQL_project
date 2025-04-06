import streamlit as st
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from db_utils import get_local_connection, get_remote_connection, get_docker_connection
import requests
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import random
import json
import os

# get parent directory

    


st.set_page_config(page_title="Sales Database", page_icon=":chart_with_upwards_trend:", layout="wide", initial_sidebar_state="collapsed")


path = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir, os.pardir))

db = get_local_connection()

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
        label = "Start by choosing whether to view sales by employee, customer, or music",
        options = ("Sales by Employee", "Sales by Customer", "Sales by Music"),
        index=None,
        on_change=run_false
    )
    if decision == "Sales by Music":
        music_decision = st.selectbox(
            label = "Now you can choose weather to select a track, an album, an artist or a genre",
            options = ("Track", "Album", "Artist", "Genre"),
            index=None,
            on_change=run_false
        )
        if music_decision:
            options = db.Track.distinct(fields[music_decision]) if not None else []
            options = sorted(options)
            options.insert(0, "Select All")
            selected_option = st.multiselect(
                label = f"Select {music_decision}, select multiple options for comparing sales",
                options = options,
                on_change=run_false,
            )
            if "Select All" in selected_option:
                selected_option = options[1:]  # Exclude "Select All" from the selection

            if selected_option:
                st.session_state.run = False
                run = st.button(label = "Run Query", use_container_width=True)
                if run:
                    run_true()

if st.session_state.run == True:
    if decision == "Sales by Music":
        # grafico temporale per le vendite di ogni oggetto selezionato
        with open(path + f'/PipelinesMongoDB/SellPer{music_decision}.json') as f:
            pipeline = json.load(f)
        result = db.Invoice.aggregate(pipeline)
        df_result = pd.DataFrame(list(result))
        df_result.set_index("_id", inplace=True)
        df_result.index = df_result.index.str[0]



        # aggiungo un istogramma per riassumere le vendite totali
        indexes = df_result.index
        values = df_result.loc[:, "TotalRevenue"].values.flatten()
        if len(selected_option) < len(options):
            ref = {
                indexes[i]: values[i] for i in range(len(indexes)) if indexes[i] for i in range(len(indexes)) if indexes[i] in selected_option
            }
            for opt in selected_option:
                if opt not in list(ref.keys()):
                    ref[opt] = 0.0
            indexes = list(ref.keys())
            values = list(ref.values())

        indexes = list(sorted(indexes, key=lambda x: values[indexes.index(x)], reverse=True))
        values = sorted(values, reverse=True)

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
        result = db.Invoice.aggregate(pipeline)
        df_result_temporal = pd.DataFrame(list(result))
        df_result_temporal["Date"] = pd.to_datetime(df_result_temporal["Date"])
        df_result_temporal.set_index([df_result_temporal.columns[0], df_result_temporal.columns[1]], inplace=True)
        # ordina le date
        df_result_temporal.sort_index(level=[0,1], inplace=True)
        min_date = df_result_temporal.index.get_level_values(1).min()
        max_date = df_result_temporal.index.get_level_values(1).max()
        print(min_date, max_date)
        date_range = pd.date_range(min_date, max_date, freq='D')

        df_result_temporal.sort_index(level=[0,1], inplace=True)
        for genre in df_result_temporal.index.get_level_values(0).unique():
            missing_dates = date_range.difference(df_result_temporal.loc[genre].index)
            df_result_temporal = pd.concat([df_result_temporal, pd.DataFrame({'TotalRevenue': 0.0},
                                             index=pd.MultiIndex.from_product([[genre], pd.to_datetime(missing_dates)],
                                                                              names=df_result_temporal.index.names))])
        df_result_temporal = df_result_temporal.groupby(level=0).resample('ME', level=1).sum()
        df_result_temporal.sort_index(level=[0,1], inplace=True)

        line_plot = go.Figure()
        for option in selected_option:
            try:
                indexes = df_result_temporal.loc[pd.IndexSlice[option, :], :].index.get_level_values(1).unique()
                values = df_result_temporal.loc[pd.IndexSlice[option, :], "TotalRevenue"].values.flatten()

                line_plot.add_trace(
                    go.Scatter(
                        x=indexes,
                        y=values,
                        mode = "markers+lines",
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
        )

        st.plotly_chart(line_plot, use_container_width=True)






        



    