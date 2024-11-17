from db.db import Database
import re

# Commands for default postgresql settings
reset_commands = [
    "SET enable_bitmapscan = on;\n",
    "SET enable_gathermerge = on;\n",
    "SET enable_hashagg = on;\n",
    "SET enable_hashjoin = on;\n",
    "SET enable_indexscan = on;\n",
    "SET enable_indexonlyscan = on;\n",
    "SET enable_material = on;\n",
    "SET enable_mergejoin = on;\n",
    "SET enable_nestloop = on;\n",
    "SET enable_seqscan = on;\n",
    "SET enable_sort = on;\n",
    "SET enable_tidscan = on;\n",
    'RESET join_collapse_limit;\n'
]


# Function to execute a list of commands
def execute_commands(db: Database, commands: list[str]):
    # return if there are no commands
    if not commands:
        return
    # loop through each command and execute them
    for command in commands:
        db.cursor.execute(command)
    # commit the changes
    db.conn.commit()


# Function to get the list of tables that can be modified
def get_modifiable_list(query_string: str):
    regex = r"\bFROM\b\s+([a-zA-Z_][a-zA-Z0-9_]*(?:\s*,\s*[a-zA-Z_][a-zA-Z0-9_]*)*)"

    matches = re.findall(regex, query_string, re.IGNORECASE)
    print(matches)
    matches = [match for match in matches if len(re.findall(',', match)) > 0]
    return matches


# Function to modify the join order of the query
def modify_join_order(query_string: str, join_order: list[list]):
    regex = r"\bFROM\b\s+([a-zA-Z_][a-zA-Z0-9_]*(?:\s*,\s*[a-zA-Z_][a-zA-Z0-9_]*)*)"

    matches = re.findall(regex, query_string, re.IGNORECASE)
    matches = [match for match in matches if len(re.findall(',', match)) > 0]
    join_str = [" NATURAL JOIN ".join(join_order_tables) for join_order_tables in join_order]
    for i in range(len(matches)):
        query_string = query_string.replace(matches[i], join_str[i], 1)
    return query_string


    

    
# Function to execute a whatif query
def whatif_query(db: Database, query: str, join: str, scan: str, aggregate: str, change_order : bool):
    commands = []
    if change_order:
        commands.append('SET join_collapse_limit = 1;\n')
    # check for whatif queries regarding join
    if join != 'none':
        # disable all other joins apart from hash join
        if join == "hash":
            commands.extend(["SET enable_mergejoin = off;\n", "SET enable_nestloop = off;\n"])
        # disable all other joins apart from merge join
        elif join == "merge":
            commands.extend(["SET enable_hashjoin = off;\n", "SET enable_nestloop = off;\n"])
        # disable all other joins apart from nested loop join
        elif join == "nested":
            commands.extend(["SET enable_mergejoin = off;\n", "SET enable_hashjoin = off;\n"])
    # check for whatif queries regarding scan
    if scan != 'none':
        # disable all other scan options apart from seqscan
        if scan == "seq":
            commands.extend(
                ["SET enable_indexscan = off;\n", "SET enable_indexonlyscan = off;\n", "SET enable_bitmapscan = off;\n",
                 "SET enable_tidscan = off;\n"])
        # disable all other scan options apart from index scan
        elif scan == "index":
            commands.extend(["SET enable_seqscan = off;\n", "SET enable_bitmapscan = off;\n", "SET enable_tidscan = off;\n"])
        # disable all other scan options apart from bitmap scan
        elif scan == "bitmap":
            commands.extend(
                ["SET enable_indexscan = off;\n", "SET enable_indexonlyscan = off;\n", "SET enable_seqscan = off;\n",
                 "SET enable_tidscan = off;\n"])
    # check for whatif queries regarding aggregation
    if aggregate != 'hash':
        # disable hash aggregation
        if aggregate == "no_hash":
            commands.append("SET enable_hashagg = off;\n")
    # configure the new settings
    execute_commands(db, commands)

    # Get qep with the new configurations
    try:
        qep, qep_cost, qep_rows, execution_time, error = db.get_qep(query)
    except Exception as e:
        raise(e)

    # restore default settings
    execute_commands(db, reset_commands)
    new_query = "".join(commands) + query

    return qep, qep_cost, qep_rows, execution_time, error, new_query


if __name__ == '__main__':
    query = 'SELECT * FROM a, b, c WHERE a.id = b.id AND b.name > (SELECT c.name FROM c , d JOIN e where c.id = d.id)'
    #query = 'SELECT * FROM customer C, orders O WHERE C.c_custkey = O.o_custkey'
    join_order = [['b', 'c', 'a'], ['c', 'd']]
    modified_query = modify_join_order(query, join_order)
    print(get_modifiable_list(query))