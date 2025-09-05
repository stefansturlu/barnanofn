import sqlite3
import polars as pl
from names import load_all_names, load_name_frequencies
from enum import Enum

DB_NAME = "name_scores.db"
CONNECTION_STRING = 'sqlite://' + DB_NAME

class Score(Enum):
    NO = -1
    MIDDLE_NAME = 0
    YES = 1


def create_name_tables():
    con = sqlite3.connect(DB_NAME)
    cur = con.cursor()
    cur.execute("CREATE TABLE IF NOT EXISTS name_scores(round, parent, name, gender, score)")


def insert_score(parent: str, name: str, gender: str, score: Score, round: int = 1):
    con = sqlite3.connect(DB_NAME)
    cur = con.cursor()
    ins = f"INSERT INTO name_scores VALUES ({round}, '{parent}', '{name}', '{gender}', {score.value})"
    print(f"Running {ins}" )
    cur.execute(ins)
    con.commit()

def delete_scores_for_parent(parent: str):
    con = sqlite3.connect(DB_NAME)
    cur = con.cursor()
    query = f"DELETE FROM name_scores WHERE parent = '{parent}'"
    row_count = cur.execute(query).rowcount
    print(f"Deleted {row_count} rows for {parent=}")
    con.commit()


def get_all_scores():
    name_scores = pl.read_database_uri("SELECT * FROM name_scores", CONNECTION_STRING)
    return name_scores

def get_not_declined_scores():
    name_scores = pl.read_database_uri("SELECT * FROM name_scores where score>=0 order by name, parent", CONNECTION_STRING)
    return name_scores


if __name__=="__main__":
    print("Running data.py")
    create_name_tables()
    print(get_all_scores())
    print("FIN")
    delete_scores_for_parent("Stefán")
    delete_scores_for_parent("Unnur")





