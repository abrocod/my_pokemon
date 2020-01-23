# Solution for Part 2:
# Part 2: Using the API and your language of choice, write a function that 
# pulls the data and loads it into the SQLite database.

import pokepy
import pandas as pd
import sqlite3 


def expand_row_list(df, target_col, target_name):
    """ expand target colum which contains list as element into multiple rows
    """
    new_col = df.apply(lambda x: pd.Series(x[target_col]),axis=1).stack().reset_index(level=1, drop=True)
    new_col.name = target_name
    return df.drop(target_col, axis=1).join(new_col)


def get_pokemons(num):
    """ download first num of pokemons """
    return [client.get_pokemon(i) for i in range(1, num + 1)]


def create_pokemon_weight_table(pokemons):
    """ create table for query 1, with column pokemon, pokemon_type and weights 
        If pokemon has more than 1 types, make each type a unique row 
    """
    pokemon_dict = {} 
    for pokemon in pokemons:
        pokemon_dict[pokemon.name] = [pokemon.weight, [t.type.name for t in pokemon.types]]

    pokemon_weight_df = pd.DataFrame.from_dict(pokemon_dict, orient="index", columns = ["weight", "types"])
    pokemon_weight_df.index.name = "name"
    pokemon_weight_df.reset_index(inplace=True)
    pokemon_weight_df = expand_row_list(pokemon_weight_df, "types", "type")
    return pokemon_weight_df
    

def create_pokemon_move_accuracy_table(pokemons):
    """ create table for query 2, with column pokemon, pokemon_type, move, move_accuracy 
        if pokemon has more than 1 types or moves, make each type, move combination a unique row 
    """
    pokemon_dict = {} 
    for pokemon in pokemons:
        pokemon_dict[pokemon.name] = [[t.type.name for t in pokemon.types], 
                                      [move.move.name for move in pokemon.moves]]

    pokemon_df = pd.DataFrame.from_dict(pokemon_dict, orient="index", columns = ["types", "moves"])
    pokemon_df.index.name = "name"
    pokemon_df = expand_row_list(pokemon_df, "types", "type")
    pokemon_df = expand_row_list(pokemon_df, "moves", "move")
    pokemon_df.reset_index(inplace=True)
    
    # extract all moves from API (only 728 moves available on this API)
    moves = [] 
    for i in range(1, 729):
        moves.append(client.get_move(i))
    move_dict = {}
    for move in moves:
        move_dict[move.name] = [move.accuracy]
    move_df = pd.DataFrame.from_dict(move_dict, orient="index", columns = ["accuracy"])
    move_df.index.name = "move_name"
    move_df.reset_index(inplace=True)
    return pd.merge(pokemon_df, move_df, how="left", left_on="move", right_on="move_name")
    

def create_pokemon_move_list_table(pokemons):
    """ create table for query 3: columns pokemon, move 
        Make each move a unique row
    """
    pokemon_dict = {} 
    for pokemon in pokemons:
        pokemon_dict[pokemon.name] = [[move.move.name for move in pokemon.moves]]

    pokemon_df = pd.DataFrame.from_dict(pokemon_dict, orient="index", columns = ["moves"])
    pokemon_df.index.name = "name"
    pokemon_df.reset_index(inplace=True)
    pokemon_df = expand_row_list(pokemon_df, "moves", "move")
    return pokemon_df
    
    
def load_table_to_sqlite(db, df, table_name):
    """ load dataframe to sqlite database
    """
    conn = sqlite3.connect(db)
    df.to_sql(table_name, conn, if_exists="replace", index=False)


if __name__ == "__main__":
    # use Pokemon Python client:
    client = pokepy.V2Client()
    pokemons = get_pokemons(num=15)
    pokemon_weight_df = create_pokemon_weight_table(pokemons)
    pokemon_move_accuracy_df = create_pokemon_move_accuracy_table(pokemons)
    pokemon_move_list_df = create_pokemon_move_list_table(pokemons)
    
    load_table_to_sqlite(db="./pokemon.db", df=pokemon_weight_df, table_name="pokemon_weight_table")
    load_table_to_sqlite(db="./pokemon.db", df=pokemon_move_accuracy_df, table_name="pokemon_move_accuracy_table")
    load_table_to_sqlite(db="./pokemon.db", df=pokemon_move_list_df, table_name="pokemon_move_list_table")