import psycopg2
import json
import time


class Database:
    def __init__(self, host, port, dbname, user, password):
        self.db_name = dbname
        self.db_user = user
        self.db_password = password
        self.db_host = host
        self.db_port = port
        self.conn = None
        self.cursor = None

    def connect(self):
        """
        Connect to the database
        """
        self.conn = psycopg2.connect(
            dbname=self.db_name,
            user=self.db_user,
            password=self.db_password,
            host=self.db_host,
            port=self.db_port
        )
        self.cursor = self.conn.cursor()

    def close(self):
        """
        Close the database connection
        """
        if self.cursor:
            self.cursor.close()
        if self.conn:
            self.conn.close()

    def execute_query(self, query, params=None):
        """
        Execute a query and return the result
        """
        try:
            start_time = time.time()
            self.cursor.execute(query, params)

            if self.cursor.description:
                result = self.cursor.fetchall()
                row_count = self.cursor.rowcount
            else:
                self.conn.commit()
                result = None
                row_count = 0

            execution_time = time.time() - start_time
            return result, execution_time, None, row_count
        except psycopg2.Error as e:
            print(f"Error executing query: {e}")
            return None, 0, str(e), 0


    def list_all_tables(self):
        """
        List all tables in the database
        """
        query = """
            SELECT table_schema, table_name
            FROM information_schema.tables
            WHERE table_type = 'BASE TABLE' AND table_schema NOT IN ('pg_catalog', 'information_schema')
            ORDER BY table_schema, table_name;
        """
        return self.execute_query(query)

    def list_columns(self, schema, table):
        """
        List all columns in a table
        """
        query = """
            SELECT column_name
            FROM information_schema.columns
            WHERE table_schema = %s AND table_name = %s
            ORDER BY ordinal_position;
        """
        return self.execute_query(query, (schema, table))

    def get_rows(self, schema, table):
        """
        Get the number of rows in a table
        """
        start_time = time.time()
        query = f"SELECT COUNT(*) FROM {schema}.{table};"
        self.cursor.execute(query)
        row_count = self.cursor.fetchone()[0]
        execution_time = time.time() - start_time
        return row_count, execution_time

    def analyze(self):
        """
        Analyze the database
        """
        query = "ANALYZE;"
        return self.execute_query(query)

    def get_qep(self, query):
        """
        Get the query execution plan (QEP) for a query
        """
        query = f"EXPLAIN (FORMAT JSON) {query}"
        result, execution_time, error, _ = self.execute_query(query)
        # Extract the total cost of the top-level plan
        qep_cost = None
        qep_rows = None
        if result is not None:
            qep_cost = result[0][0][0]["Plan"]["Total Cost"]
            qep_rows = result[0][0][0]["Plan"]["Plan Rows"]
        return json.dumps(result[0][0], indent=2), qep_cost, qep_rows, execution_time, error