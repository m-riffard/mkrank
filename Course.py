# hosted here: https://m-riffard-mkrank-app-vxkl35.streamlit.app/
from __future__ import print_function
from datetime import datetime
import streamlit as st

from api.main import get_all_users, update_user

st.set_page_config(
    page_title="Enregistrer une course",
    page_icon="🏁",
)

EXPONENTIAL_FACTOR_REWARD = 1.5
UPDATE_RATE = 32

if "is_submit_disabled" not in st.session_state:
    st.session_state["is_submit_disabled"] = True

players_collection: dict = get_all_users()


def get_players_collection():
    return players_collection


def update_players_collection():
    players_collection = get_all_users()
    return players_collection


class Player:
    expected_score: int = 0
    actual_score: float = 0
    position: int = 0
    elo_update: int = 0
    name: str = ""
    elo: int = 0
    nb_races: int = 0

    def __init__(self, name, elo, position, nb_races):
        self.name = name
        self.elo = int(elo)
        self.position = int(position)
        self.nb_races = nb_races

    def __str__(self):
        return self.name + " " + str(self.elo)

    def __repr__(self):
        return self.name + " " + str(self.elo)

    def to_string(self):
        return (
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

    def show(self):
        print(self.to_string())


def compute_elo_update():
    players_in_game = retreive_players_from_name(players_names)
    update_factor = nb_races / 10 * UPDATE_RATE
    print("--------- CALCULATING ------------")
    print("nombre de courses :", nb_races)
    print("update factor basé sur le nb de courses : ", update_factor)
    for player in players_in_game:
        player.expected_score = sum(
            [
                1 / (1 + 10 ** ((opponent.elo - player.elo) / 400))
                for opponent in players_in_game
                if opponent != player
            ]
        ) / (nb_players * (nb_players - 1) / 2)
        player.actual_score = (
            pow(EXPONENTIAL_FACTOR_REWARD, nb_players - player.position) - 1
        ) / sum(
            [
                pow(EXPONENTIAL_FACTOR_REWARD, nb_players - player.position) - 1
                for player in players_in_game
            ]
        )
        player.elo_update = round(
            update_factor
            * (player.actual_score - player.expected_score)
            * (nb_players - 1)
        )
        player.show()
        update_user(
            name=player.name,
            rank=player.elo + player.elo_update,
            nb_races=player.nb_races + 1,
        )
    reset()
    write_results(players_in_game)


def retreive_players_from_name(players_names: [str]) -> [Player]:
    players_list = []
    for player_name in players_names:
        player = retreive_player_from_name(player_name)
        player.position = players_names.index(player_name) + 1
        players_list.append(player)
    return players_list


def retreive_player_from_name(player_name: str):
    player = players_collection.get(player_name)
    if player is None:
        raise ValueError(f"Player {player_name} not found in the database")
    return Player(player_name, player["rank"], 0, player["nb_races"])


def handle_select():
    if nb_players == 0:
        st.session_state.is_submit_disabled = True
    if nb_players > 0:
        st.write(f"{players_names[0]} 1er 🏆")
        st.session_state.is_submit_disabled = True
    if nb_players > 1:
        st.write(f"\n{players_names[1]} 2e 🥈")
        st.session_state.is_submit_disabled = False
    if nb_players > 2:
        st.write(f"\n{players_names[2]} 3e 🥉")
    if nb_players > 3:
        st.write(f"\n{players_names[3]} 4e 🏅")


st.write("NOUVELLE COURSE")
players_names = st.multiselect(
    "Selectionner les joueurs dans l'ordre",
    [player for player in players_collection],
    key="selected_players",
    max_selections=4,
)
nb_players = len(players_names)
handle_select()
nb_races = st.selectbox(
    "Nombre de courses:",
    [4, 6, 8, 12, 16, 20, 24, 32, 48],
    key="nb_races_selected",
)
submit = st.button(
    "Sauvegarder la course",
    disabled=st.session_state.is_submit_disabled,
    on_click=compute_elo_update,
)


def reset():
    st.session_state.selected_players = []
    st.session_state.nb_races_selected = 4


def write_results(players_in_game: [Player]):
    st.write("RESULTATS")
    for player in players_in_game:
        if player.elo_update > 0:
            st.write(player.name, "gagne", round(player.elo_update))
        else:
            st.write(player.name, "perd", -round(player.elo_update))
    st.write("-----------------------------")
