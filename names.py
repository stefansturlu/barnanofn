import requests
import json
import polars as pl

def get_names_endpoint(initial_letter: str):
    """
    Endpoint found on this site: https://island.is/leit-i-mannanafnaskra
    """
    return f"https://island.is/api/graphql?operationName=GetIcelandicNameByInitialLetter&variables=%7B%22input%22%3A%7B%22initialLetter%22%3A%22{initial_letter}%22%7D%7D&extensions=%7B%22persistedQuery%22%3A%7B%22version%22%3A1%2C%22sha256Hash%22%3A%228547f0b261f87bf6933ed0f9be3644553d3fbe5bf7e677f7b45e3490f50580ad%22%7D%7D"

ALPHABET = "aábcdðeéfghiíjklmnoópqrstuúvwxyýzþæö"
CHANGES = {"ð": "eth", "þ": "thorn"}
SCHEMA = {'id': pl.Int64, 'icelandicName': pl.Utf8, 'type': pl.Utf8, 'status': pl.Utf8, 'verdict': pl.Utf8, 'visible': pl.Boolean, 'description': pl.Utf8, 'url': pl.Utf8, '__typename': pl.Utf8}

def scrape_all_names():
    for l in ALPHABET:
        print(f"Getting names starting with {l}")
        url = get_names_endpoint(l)

        res = requests.get(url).json()
        names_df = pl.DataFrame(res.get("data",{}).get("getIcelandicNameByInitialLetter",{}), schema=SCHEMA) 
        print(f"  number of names: {len(names_df)}")
        
        file_l = CHANGES.get(l,l)
        if len(names_df)>0:
            names_df.write_parquet(file=f"name_files/starting_with_{file_l}.parquet")

def load_name_frequencies():
    """
    Gögn hagstofunnar: https://hagstofan.s3.amazonaws.com/media/public/names.json
    Fengið af þessari síðu: https://hagstofa.is/talnaefni/ibuar/faeddir-og-danir/nofn/
    """
    with open("hagstofa.json") as f:
        hagstofa = json.load(f)
        first_names = {n["Nafn"].capitalize(): int(n["Fjoldi1"]) for n in hagstofa}
        second_names = {n["Nafn"].capitalize(): int(n["Fjoldi2"]) for n in hagstofa}
        return first_names, second_names



def load_all_names(letter = None):
    if letter:
        return pl.read_parquet(source=f"name_files/starting_with_{letter}.parquet")
    names_df = pl.read_parquet(source="name_files/*")
    return names_df




if __name__=="__main__":
    first_names, second_name = load_name_frequencies()
    print(first_names.get("Stefán"))
    print(first_names.get("Unnur"))

    names_df = load_all_names()
    print(names_df)

