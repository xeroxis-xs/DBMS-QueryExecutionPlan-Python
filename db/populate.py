import psycopg2
from psycopg2 import sql
import os
from dotenv import load_dotenv
import create_script
load_dotenv()


class Database:
    def __init__(self):
        self.db_name = os.getenv('DB_NAME')
        self.db_user = os.getenv('DB_USER')
        self.db_password = os.getenv('DB_PASSWORD')
        self.db_host = os.getenv('DB_HOST')
        self.db_port = os.getenv('DB_PORT')

    # Connect to the database
    def connect(self):
        conn = psycopg2.connect(
            dbname=self.db_name,
            user=self.db_user,
            password=self.db_password,
            host=self.db_host,
            port=self.db_port
        )
        return conn

    # Drop all tables
    def drop_table(self):
        conn = self.connect()
        cursor = conn.cursor()
        for table in create_script.script_dict.keys():
            cursor.execute(sql.SQL("DROP TABLE IF EXISTS {} CASCADE").format(sql.Identifier(table)))
            print(f"Table {table} dropped")
        conn.commit()
        conn.close()

    # Create tables
    # Reference: https://docs.verdictdb.org/tutorial/tpch/#postgresql
    def create_table(self):
        conn = self.connect()
        cursor = conn.cursor()
        for i in range(len(create_script.script_dict)):
            query = list(create_script.script_dict.values())[i]
            cursor.execute(query)
            print(f"Table {list(create_script.script_dict.keys())[i]} created")
        conn.commit()
        conn.close()

    # Insert data
    def insert_data(self):

        # Data dictionary
        tables = {
            'region': os.path.abspath('db/tbl/region.tbl'),
            'nation': os.path.abspath('db/tbl/nation.tbl'),
            'customer': os.path.abspath('db/tbl/customer.tbl'),
            'supplier': os.path.abspath('db/tbl/supplier.tbl'),
            'part': os.path.abspath('db/tbl/part.tbl'),
            'partsupp': os.path.abspath('db/tbl/partsupp.tbl'),
            'orders': os.path.abspath('db/tbl/orders.tbl'),
            'lineitem': os.path.abspath('db/tbl/lineitem.tbl')
        }

        conn = self.connect()

        try:
            with conn.cursor() as cursor:
                for table, path in tables.items():
                    # Open each file in read mode
                    with open(path, 'r') as file:
                        query = f"COPY {table} FROM STDIN DELIMITER '|' CSV"
                        cursor.copy_expert(sql=query, file=file)

                    print('Data inserted into', table)
        except Exception as e:
            print(f"Error inserting data: {e}")
            conn.rollback()
        finally:
            conn.commit()
            conn.close()


if __name__ == '__main__':
    print('Connecting to the database...')
    db = Database()
    db.connect()
    print('Connected')
    db.drop_table()
    db.create_table()
    print('Tables created')
    db.insert_data()
