import polars as pl
import streamlit as st

from names import get_random_name, load_all_names, load_name_frequencies
from data import insert_score, Score, get_all_scores

col1, col2, col3 = st.columns(3)
player = col1.radio("Foreldri", options=["Stefán", "Unnur"])
gender = col2.radio("Kyn", options=["DR", "ST"], format_func=lambda x: "Drengur" if x == "DR" else "Stúlka")
m_radio = col3.radio("Millinafn", options=["Já", "Nei", "Slembið"])
p_two_names = 1 if m_radio == "Já" else 0.5 if m_radio == "Slembið" else 0
surname = "Stefánsson" if gender == "DR" else "Stefánsdóttir"

STATUS = "Sam"  # Sam or Haf
NAMES_KEY = f"names_key_{gender}"
if NAMES_KEY not in st.session_state:
    names_df = load_all_names()
    boys_series = names_df.filter(pl.col("type") == gender).filter(pl.col("visible")).filter(pl.col("status") == STATUS)
    boys = [s.capitalize() for s in list(boys_series["icelandicName"])]
    st.session_state[NAMES_KEY] = boys
else:
    boys = st.session_state[NAMES_KEY]

FREQUENCY_KEY = "frequency_key"
if FREQUENCY_KEY not in st.session_state:
    first_names, second_names = load_name_frequencies()
    st.session_state[FREQUENCY_KEY] = first_names, second_names
else:
    first_names, second_names = st.session_state[FREQUENCY_KEY]

weight_power = st.slider("Algengi", 0, 100, value=50) / 50

if STATUS == "Haf":
    first_names = {}
    second_names = {}

first_name, second_name = get_random_name(boys, first_names, second_names, p_two_names=p_two_names, weight_power=weight_power)
full_name = " ".join((n for n in [first_name, second_name, surname] if n))
st.markdown(f"## {full_name}")

if st.checkbox("Give scores") and not second_name:
    print(f"{first_name=}")
    col1, col2, col3 = st.columns([1,1,1])
    col1.button("Nei", type="secondary", on_click=insert_score, args=(player, first_name, gender, Score.NO))
    col2.button("Já", type="secondary", on_click=insert_score, args=(player, first_name, gender, Score.YES))
    col3.button("Kannski", type="secondary", on_click=insert_score, args=(player, first_name, gender, Score.MAYBE))
else:
    st.button("Nýtt nafn")


if second_name:
    st.markdown(f"Algengi fyrsta nafns: {first_names.get(first_name,0)}")
    st.markdown(f"Algengi annars nafns: {second_names.get(second_name,0)}")
else:
    st.markdown(f"Algengi nafns: {first_names.get(first_name,0)}")

with st.expander("Atkvæði"):
    st.table(get_all_scores())