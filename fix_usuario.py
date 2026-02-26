import sqlite3
conn = sqlite3.connect('microsaas.db')
conn.execute('CREATE TABLE IF NOT EXISTS usuarios (id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT UNIQUE NOT NULL, password TEXT NOT NULL)')
conn.execute('DELETE FROM usuarios')
conn.execute('INSERT INTO usuarios (username, password) VALUES (?, ?)', ('leon', 'leon'))
conn.commit()
conn.close()
print('Usuario leon/leon creado OK')