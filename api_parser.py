import requests
import pandas as pd
from tqdm import tqdm
import concurrent.futures
import math

api_key = "********************************"
class APIParser:
    def __init__(self, api_key, league_id):
        self.league_id = league_id
        self.api_key = api_key
        self.session = requests.Session()
        self.headers = {
            "X-RapidAPI-Key": self.api_key,
            "X-RapidAPI-Host": "api-football-v1.p.rapidapi.com"
        }
        self.season_list = [str(i) for i in self.get_all_seasons()['year'].to_list()]
        self.figure_list = self.get_all_fixtures_info().fixture_id.to_list()
        self.country_list = self.get_all_countries().name.unique().tolist()

    def replace_period(self, df):
        df.columns = df.columns.str.replace('.', '_', regex=False)
        return df

    def get_response_df(self, url, querystring=None):
        response = self.session.get(
            url, headers=self.headers, params=querystring)
        response_dic = response.json()['response']
        df_response = pd.json_normalize(response_dic)
        return df_response

    def get_all_countries(self):
        url = "https://api-football-v1.p.rapidapi.com/v3/countries"
        response = self.get_response_df(url)
        return response

    def get_all_seasons(self):
        url = f"https://api-football-v1.p.rapidapi.com/v3/leagues/{self.league_id}"
        df_seasons = self.get_response_df(url)
        df_all_seasons = pd.DataFrame(df_seasons['seasons'].tolist()).explode(
            'seasons').reset_index(drop=True)
        df_all_seasons = self.replace_period(df_all_seasons)
        return df_all_seasons

    def get_all_teams(self):
        url = "https://api-football-v1.p.rapidapi.com/v3/teams"
        frames = []
        for season in tqdm(self.season_list, desc="Fetching teams", unit="season"):
            querystring = {"league": self.league_id, "season": season}
            df_temp = self.get_response_df(url, querystring)
            df_temp.insert(0, 'season', int(season))
            df_temp.insert(0, 'league_id', self.league_id)
            frames.append(df_temp)
        df_teams_info = pd.concat(frames).reset_index(drop=True)
        df_teams_info = self.replace_period(df_teams_info)
        return df_teams_info

    def get_all_fixtures_info(self):
        url = "https://api-football-v1.p.rapidapi.com/v3/fixtures"
        frames = []
        for season in tqdm(self.season_list, desc="Fetching fixtures", unit="season"):
            querystring = {"league": self.league_id, "season": season}
            df_temp = self.get_response_df(url, querystring)
            df_temp.insert(0, 'season', int(season))
            df_temp.insert(0, 'league_id', self.league_id)
            frames.append(df_temp)
        df_fixtures_info = pd.concat(frames).reset_index(drop=True)
        df_fixtures_info = self.replace_period(df_fixtures_info)
        return df_fixtures_info

    def get_df_stats_raw(self):
        breakdown_list = ['-'.join(map(str, self.figure_list[i:i+20]))
                          for i in range(0, len(self.figure_list), 20)]
        df_stats = pd.DataFrame()

        def process_fixtures(fixtures):
            url = "https://api-football-v1.p.rapidapi.com/v3/fixtures"
            querystring = {"ids": fixtures}
            response = self.session.get(
                url, headers=self.headers, params=querystring)
            response_dic = response.json()['response']
            df_temp = pd.json_normalize(response_dic)
            df_temp.columns = df_temp.columns.str.replace(
                '.', '_', regex=False)
            return df_temp[['fixture_id', 'fixture_date', 'events', 'lineups', 'statistics', 'players']]

        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(process_fixtures, fixtures)
                       for fixtures in breakdown_list]
            for future in tqdm(concurrent.futures.as_completed(futures), total=len(futures), desc="Processing raw fixtures"):
                df_temp = future.result()
                df_stats = pd.concat([df_stats, df_temp], ignore_index=True)

        return df_stats

    def get_all_lineups_general_stats(self):
        df_stats = self.get_df_stats_raw()
        all_lineups_raw_stats = self.json_decomposer(
            df_stats, ['fixture_id', 'fixture_date'], 'lineups')
        all_lineups_general_stats = all_lineups_raw_stats[[
            i for i in all_lineups_raw_stats.columns if i not in ['startXI', 'substitutes']]]
        return all_lineups_general_stats

    def all_lineups_start_stats(self):
        lineups_frames = []
        df_stats = self.get_df_stats_raw()
        df_lineups = self.json_decomposer(
            df_stats, ['fixture_id', 'fixture_date'], 'lineups')
        lineups_frames.append(df_lineups)
        all_lineups_raw_stats = pd.concat(
            lineups_frames).reset_index(drop=True)
        l = ['fixture_id', 'fixture_date', 'formation', 'team_id', 'team_name']
        r = 'startXI'
        all_lineups_start_stats = self.json_decomposer(
            all_lineups_raw_stats, l, r)
        return all_lineups_start_stats

    def all_lineups_substitutes_stats(self):
        lineups_frames = []
        df_stats = self.get_df_stats_raw()
        df_lineups = self.json_decomposer(
            df_stats, ['fixture_id', 'fixture_date'], 'lineups')
        all_lineups_general_stats = self.get_all_lineups_general_stats()
        lineups_frames.append(df_lineups)
        all_lineups_raw_stats = pd.concat(
            lineups_frames).reset_index(drop=True)
        l = ['fixture_id', 'fixture_date', 'formation', 'team_id', 'team_name']
        r = 'substitutes'
        all_lineups_substitutes_stats = self.json_decomposer(
            all_lineups_raw_stats, l, r)
        return all_lineups_substitutes_stats

    def get_all_injuries(self):
        frames = []
        url = "https://api-football-v1.p.rapidapi.com/v3/injuries"

        for season in tqdm(self.season_list, desc="Fetching injuries", unit="season"):
            querystring = {"league": self.league_id, "season": season}
            response = self.session.get(
                url, headers=self.headers, params=querystring)
            df_temp = self.replace_period(
                pd.json_normalize(response.json()['response']))
            df_temp.insert(0, 'season', int(season))
            frames.append(df_temp)

        df_injuries = pd.concat(frames).reset_index(drop=True)
        return df_injuries

    def get_all_transfers(self, players_list):
        frames = []

        def fetch_transfers(player_id):
            url = "https://api-football-v1.p.rapidapi.com/v3/transfers"
            querystring = {"player": str(player_id)}
            response = self.session.get(
                url, headers=self.headers, params=querystring)
            response_dic = response.json()['response']
            df_temp = self.replace_period(pd.json_normalize(response_dic))
            df_temp1 = self.json_decomposer(
                df_temp, ['player_id', 'player_name'], 'transfers')
            if df_temp1 is not None:
                frames.append(df_temp1)

        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(fetch_transfers, player_id)
                       for player_id in players_list]
            for future in tqdm(concurrent.futures.as_completed(futures), total=len(futures), desc="Processing transfers"):
                pass  # Wait for completion

        if frames:
            df_transfers = pd.concat(frames).reset_index(drop=True)
        else:
            print("No data to concatenate")

        return df_transfers

    def get_all_players(self):
        def fetch_player_data(season, page_number):
            params = {"league": self.league_id,
                      "season": season, "page": str(page_number)}
            response = self.session.get(
                'https://api-football-v1.p.rapidapi.com/v3/players', params=params)
            return pd.DataFrame(response.json()['response']) if response.status_code == 200 else None

        player_frames = []
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            for season in tqdm(self.season_list, desc="Fetching players", unit="season"):
                params = {"league": self.league_id,
                          "season": season, "page": "1"}
                total_pages = self.session.get(
                    'https://api-football-v1.p.rapidapi.com/v3/players', params=params).json()['paging']['total']
                fetch_job = [executor.submit(
                    fetch_player_data, season, i) for i in range(1, total_pages + 1)]
                data_frames = [f.result()
                               for f in concurrent.futures.as_completed(fetch_job)]
                data_frames = [df for df in data_frames if df is not None]
                if data_frames:
                    df_all_players = pd.concat(
                        data_frames).reset_index(drop=True)
                    frames = [pd.concat([pd.json_normalize(df_all_players['player'].iloc[i]), pd.json_normalize(
                        df_all_players['statistics'].iloc[i])], axis=1) for i in range(len(df_all_players))]
                    df_all_players_xxxx = pd.concat(
                        frames).reset_index(drop=True)
                    df_all_players_xxxx.columns = df_all_players_xxxx.columns.str.replace(
                        '.', '_', regex=False)
                    df_all_players_xxxx.insert(0, 'season', int(season))
                    player_frames.append(df_all_players_xxxx)

        final_df = pd.concat(player_frames).reset_index(drop=True)
        final_df = final_df.dropna(subset=['id'])
        final_df['id'] = final_df['id'].astype(int).astype(str)
        return final_df

    def get_all_sidelined(self, players_list):
        frames = []
        for player_id in tqdm(players_list, desc="Processing players"):
            url = "https://api-football-v1.p.rapidapi.com/v3/sidelined"
            querystring = {"player": str(player_id)}
            response = self.session.get(
                url, headers=self.headers, params=querystring)
            response_dic = response.json()['response']
            df_temp = pd.json_normalize(response_dic)
            df_temp.insert(0, 'player_id', str(player_id))
            frames.append(df_temp)

        if frames:
            df_sidelined = pd.concat(frames).reset_index(drop=True)
        else:
            print("No data to concatenate")
        return df_sidelined

    def get_all_coaches(self, coach_list):
        def fetch_data(coach_id):
            url = "https://api-football-v1.p.rapidapi.com/v3/coachs"
            querystring = {"id": str(coach_id)}
            response = self.session.get(
                url, headers=self.headers, params=querystring)
            response_dic = response.json()['response']
            df_temp = pd.json_normalize(response_dic)
            df_temp1 = self.json_decomposer(
                df_temp, [i for i in df_temp.columns if i != 'career'], 'career')
            return df_temp1

        frames = []
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            for coach_id in tqdm(coach_list, desc="Processing coaches"):
                future = executor.submit(fetch_data, coach_id)
                df_temp = future.result()
                if df_temp is not None:
                    frames.append(df_temp)

        if frames:
            df_coaches = pd.concat(frames).reset_index(drop=True)
        else:
            print("No data to concatenate")

        columns_to_rename = {
            'team_id': 'career_team_id',
            'team_name': 'career_team_name',
            'team_logo': 'career_team_logo'
        }
        df_coaches = df_coaches.iloc[:, :-3]
        df_r = df_coaches.iloc[:, -3:].rename(columns=columns_to_rename)
        df_coaches = pd.concat([df_coaches, df_r], axis=1)
        df_coaches['career_team_id'] = df_coaches['career_team_id'].astype(
            int).astype(str)
        return df_coaches

    def json_decomposer(self, df, left_cols, right_cols):
        frames = []
        for i, row in df.iterrows():
            left = pd.DataFrame([row[left_cols]] * len(row[right_cols]))
            right = pd.json_normalize(row[right_cols])
            df_combined = pd.concat([left, right], axis=1)
            frames.append(df_combined)
        if frames:
            df_final = pd.concat(frames).reset_index(drop=True)
            df_final.columns = df_final.columns.str.replace(
                '.', '_', regex=False)
            return df_final
        else:
            print("No data to decompose")
            return None


parser = APIParser(api_key=api_key, league_id='39')
