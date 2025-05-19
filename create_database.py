import sqlite3
import os

def create_database():
    os.makedirs('database', exist_ok=True)
    conn = sqlite3.connect('database/database.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS USERS (
            ID INTEGER PRIMARY KEY AUTOINCREMENT,
            LOGIN VARCHAR(32) UNIQUE NOT NULL,
            PASSWORD VARCHAR(60) NOT NULL,
            FIO VARCHAR(150)
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS JWT_BLACKLIST (
            ID INTEGER PRIMARY KEY AUTOINCREMENT,
            JTI VARCHAR(36) NOT NULL UNIQUE,
            CREATED_AT TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    conn.commit()
    conn.close()

if __name__ == '__main__':
    create_database()