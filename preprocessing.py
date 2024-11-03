import psycopg2
from psycopg2 import sql
import query_tree



def connect_to_postgres(dbname, user, password, host='localhost', port=5432):
    """Connect to a PostgreSQL database and return the connection and cursor."""
    try:
        # Establish a connection to the database
        connection = psycopg2.connect(
            dbname=dbname,
            user=user,
            password=password,
            host=host,
            port=port
        )
        
        # Create a cursor to execute queries
        cursor = connection.cursor()
        
        print("Connection to PostgreSQL database successful.")
        return connection, cursor

    except Exception as e:
        print(f"The error '{e}' occurred")
        return None, None

def get_query_execution_plan( query: str, cur):
    explain_query = 'EXPLAIN ' + query
    cur.execute(explain_query)
    result = cur.fetchall()
    qtree = query_tree.create_query_tree(result)
    return qtree


# Example usage:
if __name__ == "__main__":
    dbname = "TPC-H"
    user = "postgres"
    password = "anu8903"
    host = "localhost"  # or your host, e.g., "127.0.0.1"
    port = 5432  # default PostgreSQL port

    conn, cur = connect_to_postgres( dbname, user, password, host, port)

    # Don't forget to close the connection when done
    if conn is not None:
        try:
             result_qtree = get_query_execution_plan("SELECT o_custkey, COUNT(o_orderkey) FROM orders, lineitem WHERE o_orderstatus = 'O' AND l_linestatus = 'N' GROUP BY o_custkey;", cur)
             query_tree.query_tree.print_query_tree(result_qtree.head_node)
        except Exception as e:
            print(f"The error '{e}' occurred")
        cur.close()
        conn.close()


                            