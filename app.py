import os
import pickle
import streamlit as st
import pandas as pd
import plotly
import plotly.express as px
import matplotlib.pyplot as plt
from PIL import Image
from streamlit_option_menu import option_menu

st.set_page_config(
    page_title="TBC Dashboard",
    page_icon="🦠",
    layout="wide",
    initial_sidebar_state="auto",
)

st.markdown(
    """
    <style>
    .main .block-container {
        padding: 1.5rem 1.5rem;
    }
    .css-1lcbmhc.e1fqkh3o1 {
        padding: 0rem 0rem;
    }
    .css-1kyxreq.e1fqkh3o3 {
        padding: 0rem 0rem;
    }
    .stApp {
        height: 100vh;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        overflow: hidden;
    }

    </style>
    """,
    unsafe_allow_html=True
)

st.markdown("<h1 style='text-align: center;'>TBC Dashboard</h1>", unsafe_allow_html=True)

# Load data
df = pd.read_csv('datasetfixtbc.csv')

# Sidebar menu
with st.sidebar:
    theme = st.sidebar.selectbox(
    "Pilih Tema Visualisasi", 
    ["Plotly", "Seaborn", "GGPlot", "SimpleWhite", "Dark2", "Viridis", "Cividis", "Inferno", "Plasma"]
    )

    # Define theme to color palette mapping
    theme_color_palettes = {
        "Plotly": px.colors.qualitative.Plotly,
        "Seaborn": px.colors.sequential.Sunset,
        "GGPlot": px.colors.qualitative.G10,
        "SimpleWhite": px.colors.diverging.Spectral,
        "Dark2": px.colors.qualitative.Dark2,
        "Viridis": px.colors.sequential.Viridis,
        "Cividis": px.colors.sequential.Cividis,
        "Inferno": px.colors.sequential.Inferno,
        "Plasma": px.colors.sequential.Plasma
    }
    selected = option_menu(
        'Dashboard',
        ['Home', 'Visualisasi'],
        menu_icon='globe',
        icons=['house', 'activity'],
        default_index=0
    )
    if selected == 'Visualisasi':
        country = st.multiselect('Country', df['Country'].unique())

        year_range = st.slider("Pilih Rentang Tahun:", min_value=int(df["Year"].min()), max_value=int(df["Year"].max()), value=(int(df["Year"].min()), int(df["Year"].max())))

if selected == 'Home':
    st.markdown("""
        <style>
        .main {
            background-color: #f5f5f5;
            layout: centered;
        }
        .header {
            font-size: 48px;
            color: #2E86C1;
            text-align: center;
            font-weight: bold;
        }
        .subheader {
            font-size: 24px;
            color: #5D6D7E;
            text-align: center;
        }
        .text {
            font-size: 18px;
            color: #2C3E50;
            text-align: justify;
            line-height: 1.6;
        }
        .footer {
            font-size: 14px;
            color: #839192;
            text-align: center;
            margin-top: 50px;
        }
        .image {
            display: block;
            margin-left: auto;
            margin-right: auto;
            width: 50%;
        }
        </style>
        """, unsafe_allow_html=True)

    # Main text
    st.markdown("""
        <div class="text">
            Tuberculosis (TBC) adalah penyakit menular yang disebabkan oleh bakteri Mycobacterium tuberculosis. 
            Penyakit ini terutama menyerang paru-paru, tetapi juga bisa menyerang bagian tubuh lainnya. 
            Di Indonesia, TBC masih menjadi masalah kesehatan utama, dengan banyak kasus baru yang ditemukan setiap tahunnya.
            <br><br>
            Melalui platform ini, kami menyediakan informasi terkini mengenai TBC di seluruh dunia.
            Silakan menuju menu visualisasi untuk melihat informasi terkait TBC.
        </div>
        """, unsafe_allow_html=True)

    # Footer
    st.markdown("""
        <div class="footer">
            © 2024 TBC Dashboard | All Rights Reserved
        </div>
        """, unsafe_allow_html=True)

if selected == 'Visualisasi':
    # Main page content
    filtered_df = df[(df['Year'].between(year_range[0], year_range[1])) & (df['Country'].isin(country) if country else df['Country'])]

    # Fungsi untuk mengonversi jumlah kematian ke teks
    def format_number(num):
        if num >= 1000000:
            if num % 1000000 == 0:
                return f'{num // 1000000} M'
            return f'{round(num / 1000000, 1)} M'
        if num >= 1000:
            if num % 1000 == 0:
                return f'{num // 1000} K'
            return f'{round(num / 1000, 1)} K'
        return str(num)

    # Fungsi untuk menghitung perbedaan kematian dalam rentang tahun tertentu
    def calculate_population_difference(input_df, start_year, end_year):
        start_year_data = input_df[input_df['Year'] == start_year].reset_index()
        end_year_data = input_df[input_df['Year'] == end_year].reset_index()
        end_year_data['deaths_difference'] = end_year_data['Deaths'].sub(start_year_data['Deaths'], fill_value=0)
        end_year_data['Country'] = start_year_data['Country']  
        return end_year_data.sort_values(by="deaths_difference", ascending=False)

    # Mengelompokkan data berdasarkan negara dan tahun
    df_grouped = df.groupby(['Country', 'Year']).sum().reset_index()

    col = st.columns((1, 5), gap='medium')

    with col[0]:
        st.subheader('TBC Deaths')

        start_year = year_range[0]
        end_year = year_range[1]
        df_population_difference_sorted = calculate_population_difference(df_grouped[df_grouped['Country'].isin(country)], start_year, end_year)

        for cntry in country:
            if cntry in df_population_difference_sorted['Country'].values:
                country_data = df_population_difference_sorted[df_population_difference_sorted['Country'] == cntry]
                if not country_data.empty:
                    state_name = country_data['Country'].values[0]
                    total_population = filtered_df[filtered_df['Country'] == cntry]['Deaths'].sum()
                    state_population = format_number(total_population)
                    state_delta = format_number(country_data['deaths_difference'].values[0])
                else:
                    state_name = '-'
                    state_population = '-'
                    state_delta = ''
                st.metric(label=state_name, value=state_population, delta=state_delta)

    # Visualisasi Line Chart
    with col[1]:
        fig_line = px.line(
            filtered_df,
            x="Year",
            y="Incidence",
            color="Country",
            title="Incidence Over Years",
            labels={"Incidence": "Incidence Cases"},
            color_discrete_sequence=theme_color_palettes[theme]
        )
        st.plotly_chart(fig_line)

    col1 = st.columns((4, 4), gap='medium')
    # Visualisasi Bar Chart
    with col1[0]:
        fig_bar = px.bar(
            filtered_df,
            x="Country",
            y="Incidence_cases",
            color="Region",
            title="Incidence Cases by Country",
            labels={"Incidence Cases": "Total Cases"},
            color_discrete_sequence=theme_color_palettes[theme]
        )
        st.plotly_chart(fig_bar)

    with col1[1]:
        fig_map = px.choropleth(
            data_frame=filtered_df,
            locations="ISO_3",
            color="Prevalence",
            hover_name="Country",
            color_continuous_scale=px.colors.sequential.Plasma,
            title="Prevalence",
            color_discrete_sequence=theme_color_palettes[theme]
        )
        st.plotly_chart(fig_map)
 