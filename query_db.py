import sqlite3

def run_query(script_path: str = 'update_table.sql'):
    conn = sqlite3.connect('./instance/portal.sqlite')
    cursor = conn.cursor()
    
    with open(script_path, 'r') as f:
        script_str = ''.join(f.readlines())

    cursor.execute(script_str)

    try:
        rows = cursor.fetchall()
        for row in rows: print(row)
    except:
        print("error runinng script")

    conn.commit()
    conn.close()

    print(f"Ran query:\n{script_str}")


if __name__ == "__main__":

    insert_values = 'insert_values.sql'
    select = 'select_query.sql'
    run_query(insert_values)