import streamlit as st
import math
import polars as pl
import random
from names import load_all_names, load_name_frequencies


col1, col2, col3 = st.columns(3)
player = col1.radio("Foreldri", options=["Stefán", "Unnur"])
gender = col2.radio("Kyn", options=["DR", "ST"], format_func=lambda x: "Drengur" if x=="DR" else "Stúlka")
m_radio = col3.radio("Millinafn", options=["Já", "Nei", "Slembið"])
p_two_names = 1 if m_radio=="Já" else 0.5 if m_radio=="Slembið" else 0 
surname = "Stefánsson" if gender=="DR" else "Stefánsdóttir"

def get_name(first: str, middle: str = "", surname = ""):
    if middle:
        return f"{first} {middle} {surname}"
    return f"{first} {surname}"

STATUS = "Sam" # Sam or Haf
NAMES_KEY = f"names_key_{gender}"
if NAMES_KEY not in st.session_state:
    names_df = load_all_names()
    boys_series = names_df.filter(pl.col("type")==gender).filter(pl.col("status")==STATUS)
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

weight_power = st.slider("Algengi", 0, 100, value=100)/100

def weighted_shuffle(items, weights: dict):
    order = sorted(items, key=lambda w: random.random() ** (1.0 / math.pow(weights.get(w,0)+1,weight_power)))
    return order

def get_random_name(names: list[str], first_weights: list[float] | None = None,
                     second_weights: list[float] | None = None, p_two_names: float = 0.5):
    fyrstanafn = weighted_shuffle(names, weights=first_weights)[-1] if first_weights else random.choice(names)
    millinafn = ""
    if random.random()<p_two_names:
        millinafn = weighted_shuffle(names, weights=second_weights)[-1] if second_weights else random.choice(names)

    return get_name(fyrstanafn, millinafn, surname)

if STATUS=="Haf":
    first_names = {}
    second_names = {}
name = get_random_name(boys, first_names, second_names, p_two_names=p_two_names)
st.markdown(f"## {name}")

col1, col2, col3 = st.columns([1,1,1])
if col1.button("Nei", type="secondary"):
    st.experimental_rerun()
if col2.button("Já", type="secondary"):
    st.experimental_rerun()
if col3.button("Kannski", type="secondary"):
    st.experimental_rerun()

st.markdown("Fletta upp algengi nafns:")
input_name = st.text_input("Nafn")
st.markdown(f"Sem fyrsta nafn: {first_names.get(input_name,0)}")
st.markdown(f"Sem annað nafn: {second_names.get(input_name,0)}")