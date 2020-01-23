# Solution for Part 3: 
# Part 3: Write a function to pull the correct data from the SQLite DB for each question 
# that the Pokemon services team wants answered.

import sqlite3 
import pandas as pd

conn = sqlite3.connect("./pokemon.db")

# What is the average weight of the pokemon by Pokemon type?
cmd = "select type, avg(weight) from pokemon_weight_table group by type"
print(pd.read_sql_query(cmd, conn))

# List the highest accuracy move by Pokemon type
cmd = "select type, max(accuracy), move from pokemon_move_accuracy_table group by type"
print(pd.read_sql_query(cmd, conn))

# Count the number of moves by Pokemon and order from greatest to least 
cmd = "select name, count(move) as move_number from pokemon_move_list_table group by name order by move_number DESC"
print(pd.read_sql_query(cmd, conn))

conn.close()