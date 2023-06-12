# hosted here: https://m-riffard-mkrank-app-vxkl35.streamlit.app/

import streamlit as st

with st.form("my_form"):
   options = st.multiselect(
    'Select the players in the order',
    ['Green', 'Yellow', 'Red', 'Blue'],
    ['Yellow', 'Red'])

   st.write(f'{options[0]} 1er 🏆\n{options[1]} 2e 🏆\n')
   # Every form must have a submit button.
   submitted = st.form_submit_button("Submit")
   if submitted:
       st.write("slider", slider_val, "checkbox", checkbox_val)

st.write("Outside the form")