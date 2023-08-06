import json
import math
import random

import polars as pl
import requests

ALPHABET = "aábcdðeéfghiíjklmnoópqrstuúvwxyýzþæö"
CHANGES = {"ð": "eth", "þ": "thorn"}
SCHEMA = {
    "id": pl.Int64,
    "icelandicName": pl.Utf8,
    "type": pl.Utf8,
    "status": pl.Utf8,
    "verdict": pl.Utf8,
    "visible": pl.Boolean,
    "description": pl.Utf8,
    "url": pl.Utf8,
    "__typename": pl.Utf8,
}


def _get_names_endpoint(initial_letter: str):
    """
    Endpoint found on this site: https://island.is/leit-i-mannanafnaskra
    """
    return f"https://island.is/api/graphql?operationName=GetIcelandicNameByInitialLetter&variables=%7B%22input%22%3A%7B%22initialLetter%22%3A%22{initial_letter}%22%7D%7D&extensions=%7B%22persistedQuery%22%3A%7B%22version%22%3A1%2C%22sha256Hash%22%3A%228547f0b261f87bf6933ed0f9be3644553d3fbe5bf7e677f7b45e3490f50580ad%22%7D%7D"


def scrape_all_names():
    for l in ALPHABET:
        print(f"Getting names starting with {l}")
        url = _get_names_endpoint(l)

        res = requests.get(url).json()
        names_df = pl.DataFrame(res.get("data", {}).get("getIcelandicNameByInitialLetter", {}), schema=SCHEMA)
        print(f"  number of names: {len(names_df)}")

        file_l = CHANGES.get(l, l)
        if len(names_df) > 0:
            names_df.write_parquet(file=f"name_files/mannanafnaskra/starting_with_{file_l}.parquet")


def load_name_frequencies() -> tuple[dict[str,int],dict[str,int]]:
    """
    curl https://hagstofan.s3.amazonaws.com/media/public/names.json > name_files/hagstofan.json
    Gögn hagstofunnar: https://hagstofan.s3.amazonaws.com/media/public/names.json
    Fengið af þessari síðu: https://hagstofa.is/talnaefni/ibuar/faeddir-og-danir/nofn/
    Skilar tuple af dictionaries, þar sem lyklarnir eru nöfn, gildin er fjöldi
    """
    with open("name_files/hagstofa.json") as f:
        hagstofa = json.load(f)
        first_names = {n["Nafn"].capitalize(): int(n["Fjoldi1"]) for n in hagstofa}
        second_names = {n["Nafn"].capitalize(): int(n["Fjoldi2"]) for n in hagstofa}
        return first_names, second_names


def load_all_names(letter=None) -> pl.DataFrame:
    if letter:
        return pl.read_parquet(source=f"name_files/mannanafnaskra/starting_with_{letter}.parquet")
    return pl.read_parquet(source="name_files/mannanafnaskra/*")


def weighted_shuffle(items, weights: dict, weight_power: float):
    order = sorted(items, key=lambda w: random.random() ** (1.0 / math.pow(weights.get(w, 0) + 1, weight_power)))
    return order


def get_random_name(
    names: list[str],
    first_weights: list[float] | None = None,
    second_weights: list[float] | None = None,
    p_two_names: float = 0.5,
    weight_power: float = 1.0,
) -> tuple[str, str]:
    fyrstanafn = (
        weighted_shuffle(names, weights=first_weights, weight_power=weight_power)[-1] if first_weights else random.choice(names)
    )
    millinafn = ""
    if random.random() < p_two_names:
        millinafn = (
            weighted_shuffle(names, weights=second_weights, weight_power=weight_power)[-1]
            if second_weights
            else random.choice(names)
        )

    return fyrstanafn, millinafn


if __name__ == "__main__":
    pl.Config.set_fmt_str_lengths(100)
    pl.Config.set_tbl_cols(len(SCHEMA))
    df = load_all_names()
    print("Gögn mannanafnanefndar")
    print(df)

    print("Number of unique values in each column")
    df_nunique = df.select(pl.all().n_unique())
    print(df_nunique)

    print("Number of names in each type-status-visible group")
    pl.Config.set_tbl_rows(25)
    print(df.groupby(["type", "status", "visible"]).agg(pl.count()).sort(by=["type", "status", "visible"]))

    # print(df.filter(pl.col("visible") == False).filter(pl.col("status") == "Sam"))
