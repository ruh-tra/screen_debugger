import sqlite3
import json

with open('config.json', 'r', encoding = 'utf-8') as file:
    info_dic = json.load(file)

tables = {
    'log' : ['Event', 'Metadata', 'Aktivitetshanteraren'],
    'stats' : ['Statistik'] 
}

class Table:
    def __init__(self, rows, cols, table):
        self.rows = rows
        self.cols = cols
        self.table = table

def write_to_table(file_name, table, input_data, overwrite = False):
    table_name = info_dic[table]['name']
    metadata = info_dic[table]['dic']

    conn = sqlite3.connect(file_name)
    cur = conn.cursor()

    if overwrite:
        cur.execute(f'DELETE FROM "{table_name}"')

    col_def = ', '.join(f'"{col}" {dtype}' for col, dtype in metadata.items())

    col_key = col_def.replace('INTEGER', '').replace('TEXT', '')

    in_parenthesis = (len(metadata) * f'?, ')[0:-2]

    cur.execute(f'''CREATE TABLE IF NOT EXISTS "{table_name}"(
          {col_def}
          );
    ''')

    if table == 'events':
        for data in input_data:
            cur.execute(f'''INSERT OR REPLACE INTO "{table_name}"({col_key})
                VALUES ({in_parenthesis}); 
                ''', data.get_attributes()
            )
    
    else:
        cur.execute(f'''INSERT OR REPLACE INTO "{table_name}"({col_key})
            VALUES ({in_parenthesis}); 
            ''', input_data
        )

    conn.commit()
    conn.close()

def read_columns(file, table):
    conn = sqlite3.connect(file)
    cur = conn.cursor()
    cur.execute(f'SELECT * FROM "{table}"')
    rows = cur.fetchall()
    conn.close()

    if not rows:
        return []
    
    return rows