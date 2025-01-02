import sqlite3

def store_memory(memory):
    conn = sqlite3.connect('memory.db')
    c = conn.cursor()
    c.execute('CREATE TABLE IF NOT EXISTS memory (memory TEXT)')
    c.execute('INSERT INTO memory VALUES (?)', (memory,))
    conn.commit()
    conn.close()

def get_memory():
    conn = sqlite3.connect('memory.db')
    c = conn.cursor()
    c.execute('SELECT * FROM memory')
    memory = c.fetchone()
    conn.close()