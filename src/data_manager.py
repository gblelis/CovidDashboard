import pandas as pd
from os.path import realpath, dirname, exists, isfile
import os
import json

# Typing hints
from pandas import DataFrame
from typing import Any, Literal

SCRIPT_DIR = dirname(realpath(__file__))
RAW_DATA_DIR = SCRIPT_DIR + '\\data\\raw_data\\'
OUTPUT_PARQUET_DIR = SCRIPT_DIR + '\\data\\parquet\\'

class DataManager:
    """Creates .parquet files to increases perfomance, loads datasets and filters."""

    def __init__(self,) -> None:
        try:
            if not os.path.exists(OUTPUT_PARQUET_DIR):
                os.mkdir(OUTPUT_PARQUET_DIR)
        except Exception as e:
            print('Erro ao criar pasta para arquivos .parquet. Verifique as permissões de usuário da pasta.')
            raise e

        if (
            not os.path.exists(OUTPUT_PARQUET_DIR + 'covid_brasil_full.parquet') or
            not os.path.exists(OUTPUT_PARQUET_DIR + 'covid_brasil_last.parquet') or
            not os.path.exists(OUTPUT_PARQUET_DIR + 'df_grouped_by_city.parquet') or
            not os.path.exists(OUTPUT_PARQUET_DIR + 'df_grouped_by_state.parquet')
        ):
            self._create_parquet()

        self.df = pd.read_parquet(OUTPUT_PARQUET_DIR + 'covid_brasil_full.parquet')
        self.df_last = pd.read_parquet(OUTPUT_PARQUET_DIR + 'covid_brasil_last.parquet')
        self.df_grouped_by_city = pd.read_parquet(OUTPUT_PARQUET_DIR + 'df_grouped_by_city.parquet')
        self.df_grouped_by_state = pd.read_parquet(OUTPUT_PARQUET_DIR + 'df_grouped_by_state.parquet')

        # ----- Column date to type datetime
        self.df['date'] = pd.to_datetime(self.df['date'])

        # ----- "city_ibge_code" comes as float and with some NaNs. This line is intended to correct this.
        self.df_last['city_ibge_code'] = pd.to_numeric(self.df_last['city_ibge_code'], errors='coerce').fillna(0).astype(int).astype(str)

        # ----- Load the GEOJSON
        with open(RAW_DATA_DIR + 'geojson_br_optimized.json', 'r', encoding='utf-8') as file:
            self.geojson = json.load(file)
            
    def _create_parquet(self,) -> None:
        """Creates parquet files.

        Raises:
            Exception: If the Covid dataset download or the compression gets an error.
        """

        url = 'https://data.brasil.io/dataset/covid19/caso_full.csv.gz'

        try:
            df = pd.read_csv(url, compression='gzip')
        except Exception as e:
            print(f"Erro ao baixar dados: {e}")
            raise e

        # ----- Column date to type datetime
        df['date'] = pd.to_datetime(df['date'])

        # ----- Creating column year_month for grouping by later
        df['year-month'] = df['date'].dt.to_period('M').dt.to_timestamp()
        df['day'] = df['date'].dt.day

        # ----- Creating column estimated deaths per 100k inhabitants
        df['last_available_deaths_per_100k_inhabitants'] = (
            df['last_available_deaths'] / df['estimated_population']
        ) * 100000

        df.to_parquet(OUTPUT_PARQUET_DIR + 'covid_brasil_full.parquet')

        # ----- Get the last updates of the dataset
        df_last = df[df['is_last'] == True].copy()

        df_last.to_parquet(OUTPUT_PARQUET_DIR + 'covid_brasil_last.parquet')

        # ----- Grouping by CITY, STATE and DATE, to use later

        filtered_df = df[df['place_type'] == 'city'].copy()

        df_grouped_by_date_n_location = filtered_df[
            ['city', 'state', 'year-month', 'day', 'last_available_confirmed', 'last_available_deaths']
        ].groupby(
            ['city', 'state', 'year-month']
        ).max(['day', 'last_available_confirmed', 'last_available_deaths']).reset_index()

        df_grouped_by_date_n_location.to_parquet(OUTPUT_PARQUET_DIR + 'df_grouped_by_city.parquet')

        # ----- Grouping by STATE and DATE, to use later

        filtered_df = df[df['place_type'] == 'state'].copy()

        df_grouped_by_date_n_location = filtered_df[
            ['state', 'year-month', 'day', 'last_available_confirmed', 'last_available_deaths']
        ].groupby(
            ['state', 'year-month']
        ).max(['day', 'last_available_confirmed', 'last_available_deaths']).reset_index()

        df_grouped_by_date_n_location.to_parquet(OUTPUT_PARQUET_DIR + 'df_grouped_by_state.parquet')