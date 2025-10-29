import sqlite3

def main():
    db_path = input("Enter path to SQLite .db file: ").strip()
    try:
        conn = sqlite3.connect(db_path)
    except Exception as e:
        print(f"Error connecting to database: {e}")
        return

    print("Connected to database. Type SQL commands to execute, or 'exit' to quit.")
    cursor = conn.cursor()
    while True:
        cmd = input("sqlite> ").strip()
        if cmd.lower() in ('exit', 'quit'):
            break
        if not cmd:
            continue
        try:
            cursor.execute(cmd)
            if cmd.lower().startswith("select"):
                rows = cursor.fetchall()
                for row in rows:
                    print(row)
            else:
                conn.commit()
                print("Command executed successfully.")
        except Exception as e:
            print(f"Error: {e}")

    cursor.close()
    conn.close()
    print("Connection closed.")

if __name__ == "__main__":
    main()


