import streamlit as st
import pandas as pd
from api.main import get_all_users, update_user

st.set_page_config(
    page_title="Classement",
    page_icon="🏁",
)

dict = get_all_users()
data = [
    {
        "Joueur": name,
        "Classement": dict[name]["rank"],
        "Nombre de courses": dict[name]["nb_races"],
    }
    for name in dict
]
dataframe = pd.DataFrame(data)
st.dataframe(dataframe, use_container_width=True, hide_index=True)
nb_players = len(dataframe.index)

dataframe = dataframe[['Joueur','Classement','Nombre de courses']].sort_values('Classement', ascending=False)

dataframe['Position']=range(1,nb_players+1)

sorted = dataframe[['Position', 'Joueur','Classement','Nombre de courses']]

st.write(f'Classement de l\'agence')

st.dataframe(sorted, use_container_width=True, hide_index=True)
