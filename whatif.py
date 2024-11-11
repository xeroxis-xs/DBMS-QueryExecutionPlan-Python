<<<<<<< HEAD
<<<<<<< HEAD
from  db.db import Database

commands = []

#commands for default postgresql settings
reset_commands = [
    "SET enable_bitmapscan = on;",
    "SET enable_gathermerge = on;",
    "SET enable_hashagg = on;",
    "SET enable_hashjoin = on;",
    "SET enable_indexscan = on;",
    "SET enable_indexonlyscan = on;",
    "SET enable_material = on;",
    "SET enable_mergejoin = on;",
    "SET enable_nestloop = on;",
    "SET enable_seqscan = on;",
    "SET enable_sort = on;",
    "SET enable_tidscan = on;"
]

def execute_commands(db : Database, commands : list[str]):
    #return if there are no commands
    if not commands:
        return
    #loop through each command and execute them
    for command in commands:
        db.cursor.execute(command)
    #commit the changes
    db.conn.commit()

def whatif_query(db : Database, query : str, join : str | None, scan : str | None, aggregate: str | None):
    #check for whatif queries regarding join
    if join is not None:
        #disable all other joins apart from hash join
        if join == "hash":
            commands.extend(["SET enable_mergejoin = off;", "SET enable_nestloop = off;"])
        #disable all other joins apart from merge join
        elif join == "merge":
            commands.extend(["SET enable_hashjoin = off;", "SET enable_nestloop = off;"])
        #disable all other joins apart from nested loop join
        elif join == "nested":
            commands.extend(["SET enable_mergejoin = off;", "SET enable_hashjoin = off;"])
    #check for whatif queries regarding scan
    if scan is not None:
        #disable all other scan options apart from seqscan
        if scan == "seq":
            commands.extend(["SET enable_indexscan = off;", "SET enable_indexonlyscan = off;", "SET enable_bitmapscan = off;", "SET enable_tidscan = off;"])
        #disable all other scan options apart from index scan
        elif scan == "index":
            commands.extend(["SET enable_seqscan = off;", "SET enable_bitmapscan = off;", "SET enable_tidscan = off;"])
        #disable all other scan options apart from bitmap scan
        elif scan == "bitmap":
            commands.extend(["SET enable_indexscan = off;", "SET enable_indexonlyscan = off;", "SET enable_seqscan = off;", "SET enable_tidscan = off;"])
    #check for whatif queries regarding aggregation
    if aggregate is not None:
        #disable hash aggregation
        if aggregate == "disable_hash":
            commands.append("SET enable_hashagg = off;")
    #configure the new settings
    execute_commands(db, commands)

    #get qep with the new configurations
    qep, qep_cost, qep_rows, execution_time, error = db.get_qep(query)

    #restore default settings
    execute_commands(db, reset_commands)

    return qep, qep_cost, qep_rows, execution_time, error

=======
class WhatIf:
    pass
>>>>>>> 777c8ce86c01011e80c9c68680c910b10e7bb198
=======
class WhatIf:
    pass
>>>>>>> e9a121c037c897a96cfdeb4a8770c9b1bd77a82d
