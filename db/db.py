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

    # Connect to the database
    def connect(self):
        self.conn = psycopg2.connect(
            dbname=self.db_name,
            user=self.db_user,
            password=self.db_password,
            host=self.db_host,
            port=self.db_port
        )
        self.cursor = self.conn.cursor()

    def close(self):
        if self.cursor:
            self.cursor.close()
        if self.conn:
            self.conn.close()

    def execute_query(self, query, params=None):
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
        query = """
            SELECT table_schema, table_name
            FROM information_schema.tables
            WHERE table_type = 'BASE TABLE' AND table_schema NOT IN ('pg_catalog', 'information_schema')
            ORDER BY table_schema, table_name;
        """
        return self.execute_query(query)

    def list_columns(self, schema, table):
        query = """
            SELECT column_name
            FROM information_schema.columns
            WHERE table_schema = %s AND table_name = %s
            ORDER BY ordinal_position;
        """
        return self.execute_query(query, (schema, table))

    def get_rows(self, schema, table):
        start_time = time.time()
        query = f"SELECT COUNT(*) FROM {schema}.{table};"
        self.cursor.execute(query)
        row_count = self.cursor.fetchone()[0]
        execution_time = time.time() - start_time
        return row_count, execution_time

    def analyze(self):
        query = "ANALYZE;"
        return self.execute_query(query)

    def get_qep(self, query):
        """
        Get the query execution plan for a given SQL query in JSON format
        :param query: SQL query
        :return: JSON formatted query execution plan
        """
        query = f"EXPLAIN (FORMAT JSON) {query}"
        result, execution_time, error, _ = self.execute_query(query)
        return json.dumps(result[0][0], indent=2), execution_time, error

    def manipulate_qep(self, qep, changes):

        plan_tree = json.loads(qep)['Plan']

        self.apply_changes_to_plan(plan_tree, changes)

        return json.dumps(plan_tree, indent=2)

    def apply_changes_to_plan(self, plan_tree, changes):

        # Change the node type of Hash Join to Merge Join
        if 'Node Type' in plan_tree and plan_tree['Node Type'] == 'Hash Join' and 'change_to_merge_join' in changes:
            for key, value in changes.items():
                plan_tree[key] = value

        # Recursively apply changes to the child nodes
        if 'Plans' in plan_tree:
            for plan in plan_tree['Plans']:
                self.apply_changes_to_plan(plan, changes)