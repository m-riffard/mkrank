# hosted here: https://m-riffard-mkrank-app-vxkl35.streamlit.app/
from __future__ import print_function
import os.path
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import streamlit as st

st.set_page_config(
    page_title="Enregistrer une course",
    page_icon="🏁",
)

# If modifying these scopes, delete the file token.json.
SCOPES = ["https://www.googleapis.com/auth/spreadsheets.readonly"]

SAMPLE_SPREADSHEET_ID = "1LwOH-BoqVVmKPAQzrWVnL-SgLkFrtYvyp5SikbeCPGo"
SAMPLE_RANGE_NAME = "Players!A2:A"

NB_PLAYERS_RANGE = "NewMatch!A3"
NB_RACES_RANGE = "NewMatch!B3"
PLAYERS_RANGE = "NewMatch!B6:E6"
LADDER_RANGE = "NewMatch!B7:E7"
USERS_RANGE = "Players!A2:B"

EXPONENTIAL_FACTOR_REWARD = 1.5
UPDATE_RATE = 32


class Player:
    expected_score: int = 0
    actual_score: float = 0
    position: int = 0
    elo_update: int = 0
    name: str = ""
    elo: int = 0
    row: int = 0

    def __init__(self, name, elo, row, position):
        self.name = name
        self.elo = int(elo)
        self.row = row
        self.position = int(position)

    def __str__(self):
        return self.name + " " + str(self.elo) + " n°" + str(self.row)

    def __repr__(self):
        return self.name + " " + str(self.elo) + " n°" + str(self.row)

    def show(self):
        print(
            self.name
            + " ---> elo : "
            + str(self.elo)
            + ", expected_score : "
            + str(self.expected_score)
            + ", position : "
            + str(self.position)
            + ", actual score based on position : "
            + str(self.actual_score)
            + ", elo_update : "
            + str(self.elo_update)
        )

@st.cache_data
def load_data():
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open("token.json", "w") as token:
            token.write(creds.to_json())

    try:
        service = build("sheets", "v4", credentials=creds)

        # Call the Sheets API
        sheet = service.spreadsheets()

        nb_players = int(
            sheet.values()
            .get(spreadsheetId=SAMPLE_SPREADSHEET_ID, range=NB_PLAYERS_RANGE)
            .execute()
            .get("values", [])[0][0]
        )

        all_players_elo = (
            sheet.values()
            .get(spreadsheetId=SAMPLE_SPREADSHEET_ID, range=USERS_RANGE)
            .execute()
            .get("values", [])
        )

        return all_players_elo
    except HttpError as err:
        print(err)

def compute_elo_update():
    retreive_players_from_name()
    update_factor = nb_races / 10 * UPDATE_RATE
    print('--------- CALCULATING ------------')
    print('nombre de courses', nb_races)
    print('update factor basé sur le nb de courses : ', update_factor)
    for player in players:
        player.expected_score = sum(
            [
                1 / (1 + 10 ** ((opponent.elo - player.elo) / 400))
                for opponent in players
                if opponent != player
            ]
        ) / (nb_players * (nb_players - 1) / 2)
        player.actual_score = (
            pow(EXPONENTIAL_FACTOR_REWARD, nb_players - player.position) - 1
        ) / sum(
            [
                pow(EXPONENTIAL_FACTOR_REWARD, nb_players - player.position) - 1
                for player in players
            ]
        )
        player.elo_update = (
            update_factor
            * (player.actual_score - player.expected_score)
            * (nb_players - 1)
        )
        player.show()
    reset()
    write_results()
options=[]
st.session_state.is_submit_disabled=True
players=[]

def retreive_players_from_name():
    for player_name in players_names:
        for row in range(len(players_collection)):
            if player_name == players_collection[row][0]:
                players.append(
                    Player(
                        player_name,
                        players_collection[row][1],
                        row,
                        len(players)+1,
                    )
                )

def handle_select():
    if nb_players==0:
        st.session_state.is_submit_disabled=True
    if nb_players>0:
        st.write(f'{players_names[0]} 1er 🏆')
        st.session_state.is_submit_disabled=True
    if nb_players>1:
        st.write(f'\n{players_names[1]} 2e 🥈')
        st.session_state.is_submit_disabled=False
    if nb_players>2:
        st.write(f'\n{players_names[2]} 3e 🥉')
    if nb_players>3:
        st.write(f'\n{players_names[3]} 4e 🏅')

players_collection = load_data()

st.write('NOUVELLE COURSE')
players_names = st.multiselect(
    'Selectionner les joueurs dans l\'ordre',
    [player[0] for player in players_collection],
    key="selected_players",
    max_selections=4,
    )
nb_players=len(players_names)
handle_select()
nb_races = st.selectbox(
    'Nombre de courses:',
    [4,6,8,12,16,20,24,32,48],
    key="nb_races_selected",
    )
submit = st.button("Sauvegarder la course", disabled=st.session_state.is_submit_disabled, on_click=compute_elo_update)


def reset():
    st.session_state.selected_players=[]
    st.session_state.nb_races_selected=4
    
def write_results():
    st.write('RESULTATS')
    for player in players:
        if player.elo_update > 0:
            st.write(player.name, 'gagne', round(player.elo_update))
        else:
            st.write(player.name, 'perd', -round(player.elo_update))
    st.write('-----------------------------')