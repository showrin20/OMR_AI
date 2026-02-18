import sqlite3, json
from pathlib import Path
BASE = Path(__file__).parent
DB = BASE / 'database.db'
conn = sqlite3.connect(DB)
cur = conn.cursor()
cur.execute('CREATE TABLE IF NOT EXISTS exams(id INTEGER PRIMARY KEY, answer_key TEXT)')
# insert sample exam id=1 with 50 answers (A/B/C/D repeating)
answers = {str(i+1): ['A','B','C','D'][i%4] for i in range(50)}
cur.execute('INSERT OR REPLACE INTO exams(id,answer_key) VALUES(?,?)', (1, json.dumps(answers)))
conn.commit()
conn.close()
print('DB initialized:', DB)
