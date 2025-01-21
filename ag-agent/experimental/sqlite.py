import sqlite3

class SQLiteDB:
    def __init__(self, db_file=None):
        self.conn = None
        self.cursor = None
        if db_file:
            self.connect_with_db_file(db_file)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.conn:
            self.conn.close()

    def connect_with_db_file(self, db_file):
        self.conn = sqlite3.connect(db_file)
        self.cursor = self.conn.cursor()

    def connect_with_url(self, url):
        raise NotImplementedError("SQLite does not support connection via URL")

    def upsert(self, table_name, _dict):
        columns = ', '.join(_dict.keys())
        placeholder = ', '.join('?' * len(_dict))
        sql = f"INSERT OR REPLACE INTO {table_name} {{columns}}  VALUES {{placeholder}}"
        self.cursor.execute(sql, list(_dict.values()))
        self.conn.commit()

    def delete(self, table_name, _id):
        sql = f'DELETE FROM {table_name} WHERE id = ?'
        self.cursor.execute(sql, (_id))
        self.conn.commit()

    def get(self, table_name, _id):
        sql = f'SELECT * FROM {table_name} WHERE id =?'
        self.cursor.execute(sql, (_id))
        return self.cursor.fetchone()

    def get_all(self, table_name):
        sql = 'SELECT * FROM {}'.format(table_name)
        return self.cursor.execute(sql).fetchall()

    def run_sql(self, sql):
        print('\n\n----- Entered into the run_sql --------\n\n')
        return self.cursor.execute(sql).fetchall()

    def get_table_definitions(self, table_name):
        sql = f"SELECT sql FROM sqlite_master  WHERE type='table'  AND name=? "
        self.cursor.execute(sql, (table_name,))
        return self.cursor.fetchone()[0]

    def get_all_table_names(self):
        self.cursor.execute("SELECT name FROM sqlite_master WHERE type= 'table'")
        return [row[0] for row in self.cursor.fetchall()]

    def get_table_definitions_for_prompt(self):
        table_names = self.get_all_table_names()
        table_definitions = [self.get_table_definitions(table_name) for table_name in table_names]
        return '\n'.join(table_definitions)