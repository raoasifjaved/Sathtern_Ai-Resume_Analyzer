import json
import sqlite3
from datetime import datetime, timezone

class ResumeDB:
    def __init__(self, path: str):
        self.path = path
        self._init_db()
    def _connect(self):
        c = sqlite3.connect(self.path); c.row_factory = sqlite3.Row; return c
    def _init_db(self):
        c = self._connect()
        c.execute("CREATE TABLE IF NOT EXISTS resumes (id INTEGER PRIMARY KEY AUTOINCREMENT, filename TEXT NOT NULL, target_role TEXT NOT NULL, raw_text TEXT NOT NULL, analysis_json TEXT NOT NULL, created_at TEXT NOT NULL)")
        c.commit(); c.close()
    def save_resume(self, filename, target_role, raw_text, analysis):
        c = self._connect(); cur = c.execute("INSERT INTO resumes(filename,target_role,raw_text,analysis_json,created_at) VALUES (?,?,?,?,?)", (filename,target_role,raw_text,json.dumps(analysis,ensure_ascii=False),datetime.now(timezone.utc).isoformat())); c.commit(); rid = cur.lastrowid; c.close(); return rid
    def list_resumes(self, limit=10):
        c = self._connect(); rows = c.execute("SELECT id,filename,target_role,created_at FROM resumes ORDER BY id DESC LIMIT ?",(limit,)).fetchall(); c.close(); return [dict(r) for r in rows]
    def get_resume(self, resume_id):
        c = self._connect(); row = c.execute("SELECT * FROM resumes WHERE id=?",(resume_id,)).fetchone(); c.close(); return dict(row) if row else None
