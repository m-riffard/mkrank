# hosted here: https://m-riffard-mkrank-app-vxkl35.streamlit.app/
from __future__ import print_function
import streamlit as st
import pandas as pd

st.set_page_config(
    page_title="Enregistrer une course",
    page_icon="🏁",
)

dataframe = pd.read_excel('ranks.xlsx')

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

def load_data():
    return pd.read_excel('./ranks.xlsx')

def compute_elo_update():
    players_collection=load_data()
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
        player.elo_update = round(
            update_factor
            * (player.actual_score - player.expected_score)
            * (nb_players - 1)
        )
        player.show()
        row = players_collection.loc[players_collection['Joueur'] == player.name]
        index = row.index[0]
        last_column_index = len(row.columns) - 2
        while pd.isnull(row.iloc[0, last_column_index]):
            last_column_index -= 1
        new_elo = players_collection.at[index, players_collection.columns[last_column_index]] + player.elo_update
        players_collection.at[index, players_collection.columns[last_column_index+1]] = new_elo
        players_collection.at[index, players_collection.columns[2]] = new_elo
        players_collection.at[index, players_collection.columns[3]] += 1
    players_collection.drop(columns = players_collection.columns[0], inplace= True) #remove index column that is generated
    reset()
    write_results()
    players_collection.to_excel('./ranks.xlsx')
options=[]
st.session_state.is_submit_disabled=True
players=[]

def retreive_players_from_name():
    for player_name in players_names:
        for row in range(len(players_collection)):
            if player_name == players_collection.iloc[row]['Joueur']:
                players.append(
                    Player(
                        player_name,
                        players_collection.iloc[row]['Classement'],
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
    [player for player in players_collection['Joueur']],
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