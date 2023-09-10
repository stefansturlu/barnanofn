import polars as pl
import streamlit as st

from names import get_random_name, load_all_names, load_name_frequencies
from data import insert_score, Score, get_all_scores

# Top controls
col1, col2, col3 = st.columns(3)
player = col1.radio("Foreldri", options=["Unnur", "Stefán", "blablabla"])
gender = col2.radio("Kyn", options=["DR", "ST"], format_func=lambda x: "Drengur" if x == "DR" else "Stúlka")
m_radio = col3.radio("Millinafn", options=["Nei", "Já", "Slembið"])
p_two_names = 1 if m_radio == "Já" else 0.5 if m_radio == "Slembið" else 0
surname = "Stefánsson" if gender == "DR" else "Stefánsdóttir"
weight_power = st.slider("Algengi", 0, 100, value=50) / 50

STATUS = "Sam"  # Sam or Haf
NAMES_KEY = f"names_key_{gender}"
if NAMES_KEY not in st.session_state:
    names_df = load_all_names()
    boys_series = names_df.filter(pl.col("type") == gender).filter(pl.col("visible")).filter(pl.col("status") == STATUS)
    names = [s.capitalize() for s in list(boys_series["icelandicName"])]
    st.session_state[NAMES_KEY] = names
else:
    names = st.session_state[NAMES_KEY]

FREQUENCY_KEY = "frequency_key"
if FREQUENCY_KEY not in st.session_state:
    first_names, second_names = load_name_frequencies()
    st.session_state[FREQUENCY_KEY] = first_names, second_names
else:
    first_names, second_names = st.session_state[FREQUENCY_KEY]

if STATUS == "Haf":
    first_names = {}
    second_names = {}

ALREADY_RATED_KEY = "already_rated_key"
if ALREADY_RATED_KEY not in st.session_state:
    all_scores_df = get_all_scores()
    df_grouped = all_scores_df.groupby("parent").agg(pl.col("name"))
    print("df_grouped")
    print(df_grouped)
    already_rated = {row[0]: set(row[1]) for row in df_grouped.iter_rows()}
    print(already_rated)
    st.session_state[ALREADY_RATED_KEY] = already_rated
else:
    already_rated = st.session_state[ALREADY_RATED_KEY]

def _insert_score(*args):
    if args[0] not in already_rated:    
        already_rated[args[0]] = set()
    already_rated[args[0]].add(args[1])
    insert_score(*args)

names = [n for n in names if n not in already_rated.get(player,set()) and first_names.get(n,0)>1]
print(f"Það eru {len(names)} nöfn eftir hjá {player}")
if len(names)==0:
    print(f"{player} búin með öll nöfn")
    st.success(f"{player} búin/n með öll nöfn")
    st.stop()

for foo, bar in already_rated.items():
    print(f"Already rated: {foo} - {len(bar)}")
first_name, second_name = get_random_name(names, first_names, second_names, p_two_names=p_two_names, weight_power=weight_power)
given_names = " ".join((n for n in [first_name, second_name] if n))
st.markdown(f"## Nafn: {given_names}")
st.markdown(f"Fullt nafn: **{given_names}** {surname}")

if not second_name and st.checkbox("Give scores", value=True):
    st.markdown(f"**{player}** gefur atkvæði:")
    col1, col2, col3, col4 = st.columns(4)
    col1.button("Neibbs", type="secondary", on_click=_insert_score, args=(player, first_name, gender, Score.NO))
    col2.button("Já, mögulega", type="secondary", on_click=_insert_score, args=(player, first_name, gender, Score.YES))
    col3.button("Bara millinafn", type="secondary", on_click=_insert_score, args=(player, first_name, gender, Score.MIDDLE_NAME))
    col4.button("Ákveða síðar", type="secondary")
else:
    st.button("Nýtt nafn")


if second_name:
    st.markdown(f"Algengi fyrsta nafns: {first_names.get(first_name,0)}")
    st.markdown(f"Algengi annars nafns: {second_names.get(second_name,0)}")
else:
    st.markdown(f"Algengi nafns: {first_names.get(first_name,0)}")

