import altair as alt
import streamlit as st
import pandas as pd
import pydeck as pdk
import matplotlib.pyplot as plt

# This file is intentionally huge. It's meant to be a starting point for teaching Streamlit basics.
# A better approach is to modularize helpers and Streamlit code into separate files.

ORDERED_DAYS_OF_WEEK = [
    "Monday",
    "Tuesday",
    "Wednesday",
    "Thursday",
    "Friday",
    "Saturday",
    "Sunday",
]

# Helpers


def get_unique_stations(df):
    start_stations = df["start_station_name"].unique()
    end_stations = df["end_station_name"].unique()
    all_unique = start_stations.tolist() + end_stations.tolist()
    all_unique = list(set(all_unique))
    all_unique = pd.DataFrame(all_unique, columns=["station_name"])
    all_unique[["lat", "lon"]] = all_unique["station_name"].apply(
        lambda x: pd.Series(find_location(df, x)))
    return all_unique


def get_day_of_week_frequencies(df):
    days_of_week = df["started_at"].dt.day_name()
    days_of_week = days_of_week.value_counts()
    days_of_week = days_of_week.reset_index()
    days_of_week.columns = ["day", "number_of_trips"]
    return days_of_week


def get_hour_of_day_frequencies(df):
    hours_of_day = df["started_at"].dt.hour
    hours_of_day = hours_of_day.value_counts()
    hours_of_day = hours_of_day.reset_index()
    hours_of_day.columns = ["hour", "number_of_trips"]
    return hours_of_day


def get_member_type_frequencies(df):
    member_type = df["member_casual"].value_counts()
    member_type = member_type.reset_index()
    member_type.columns = ["member_type", "number_of_trips"]
    return member_type


def get_average_duration_by_member_type(df):
    df["duration"] = (df["ended_at"] - df["started_at"]
                      ).dt.total_seconds() / 60
    average_duration_for_member_type = df.groupby(
        "member_casual")[["duration"]].mean().reset_index()
    average_duration_for_member_type.columns = [
        "member_type", "average_duration"]
    return average_duration_for_member_type


# Actual Streamlit code


@st.cache_data
def load_data(data_path):
    df = pd.read_csv(data_path)
    df["started_at"] = pd.to_datetime(df["started_at"])
    df["ended_at"] = pd.to_datetime(df["ended_at"])
    df = df.dropna()
    return df


def add_title_and_description():
    st.title("Viajes en bicicleta en Chicago")
    st.write(
        "Este dashboard muestra información sobre viajes en "
        "bicicleta en Chicago durante abril de 2020.")


def show_number_of_trips(df):
    st.write("¿Cuántos viajes quieres ver?")
    number_of_trips = st.slider("Número de viajes", 0, 100, 10, 10)
    st.write(df.head(number_of_trips))


def find_location(df, station_name):
    find_start = df[df["start_station_name"] == station_name]
    if not find_start.empty:
        return find_start.iloc[0]["start_lat"], find_start.iloc[0]["start_lng"]
    find_end = df[df["end_station_name"] == station_name]
    return find_end.iloc[0]["end_lat"], find_end.iloc[0]["end_lng"]


def show_all_stations_in_map(df):
    st.subheader("Mapa de todas las estaciones")
    all_unique = get_unique_stations(df)
    st.map(all_unique)


def create_two_columns():
    return st.columns(2)


def add_station_name_filter(df):
    st.subheader("Filtrar por estación")
    option = st.selectbox(
        'Selecciona una estación de inicio o fin',
        df['start_station_name'].unique())
    if option:
        filtered_df = df[df['start_station_name'] == option]
        return filtered_df
    return df


def plot_days_of_week(df, column):
    column.subheader("Viajes por día de la semana")
    days_of_week_frequencies = get_day_of_week_frequencies(df)
    days_of_week_chart = alt.Chart(
        days_of_week_frequencies
    ).mark_line().encode(
        x=alt.X('day:O', sort=ORDERED_DAYS_OF_WEEK),
        y="number_of_trips",
    )
    column.altair_chart(days_of_week_chart, use_container_width=True)


def plot_hours_of_day(df, column):
    column.subheader("Viajes por hora del día")
    hours_of_day_frequencies = get_hour_of_day_frequencies(df)
    hours_of_day_chart = alt.Chart(
        hours_of_day_frequencies
    ).mark_line().encode(
        x=alt.X('hour:O'),
        y="number_of_trips",
    )
    column.altair_chart(hours_of_day_chart, use_container_width=True)


def plot_member_type(df, column):
    column.subheader("Tipo de usuario")
    member_type_frequencies = get_member_type_frequencies(df)
    fig, ax = plt.subplots()
    ax.pie(member_type_frequencies["number_of_trips"],
           labels=member_type_frequencies["member_type"], autopct='%1.1f%%')
    column.pyplot(fig)


def plot_average_duration_by_member_type(df, column):
    column.subheader("Duración promedio por tipo de usuario (minutos)")
    average_duration_for_member_type = get_average_duration_by_member_type(df)
    average_duration_for_member_type_chart = alt.Chart(
        average_duration_for_member_type
    ).mark_bar().encode(
        x=alt.X('member_type:O'),
        y="average_duration",
    )
    column.altair_chart(average_duration_for_member_type_chart,
                        use_container_width=True)


def plot_routes(df):
    st.subheader("Rutas")
    tooltip = {
        "html": "Start Station: <b>{start_station_name}</b> <br>"
        " End Station: <b>{end_station_name}</b>"}
    start_stations_layer = pdk.Layer(
        "ScatterplotLayer",
        df,
        get_position=["start_lng", "start_lat"],
        get_radius=100,
        get_fill_color=[0, 0, 255],
    )
    end_stations_layer = pdk.Layer(
        "ScatterplotLayer",
        df,
        get_position=["end_lng", "end_lat"],
        get_radius=100,
        get_fill_color=[255, 165, 0],
    )
    arc_layer = pdk.Layer(
        'ArcLayer',
        df,
        get_source_position='[start_lng, start_lat]',
        get_target_position='[end_lng, end_lat]',
        get_source_color=[0, 0, 255, 160],
        get_target_color=[255, 165, 0, 160],
        get_width=1,
        pickable=True,
        auto_highlight=True,
    )

    view_state = pdk.ViewState(
        latitude=41.881832,
        longitude=-87.623177,
        zoom=13,
        bearing=0,
        pitch=45
    )

    st.pydeck_chart(
        pdk.Deck(layers=[start_stations_layer, end_stations_layer, arc_layer],
                 initial_view_state=view_state,
                 tooltip=tooltip))


if __name__ == "__main__":
    df = load_data("202004-divvy-tripdata_clean.csv")
    add_title_and_description()
    show_number_of_trips(df)
    show_all_stations_in_map(df)
    filtered_df = add_station_name_filter(df)
    column_1, column_2 = create_two_columns()
    column_3, column_4 = create_two_columns()
    plot_days_of_week(filtered_df, column_1)
    plot_hours_of_day(filtered_df, column_2)
    plot_member_type(filtered_df, column_3)
    plot_average_duration_by_member_type(filtered_df, column_4)
    plot_routes(filtered_df)
