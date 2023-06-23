import streamlit as st
import pandas as pd

st.set_page_config(
    page_title="Classement",
    page_icon="🏁",
)

dataframe = pd.read_excel('./ranks.xlsx')

nb_players = len(dataframe.index)

dataframe = dataframe[['Joueur','Classement','Nombre de courses']].sort_values('Classement', ascending=False)

dataframe['Position']=range(1,nb_players+1)

sorted = dataframe[['Position', 'Joueur','Classement','Nombre de courses']]

st.write(f'Classement de l\'agence')

st.dataframe(sorted, use_container_width=True, hide_index=True)