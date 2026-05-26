from flask import Flask, request, jsonify, send_file
import sqlite3
import json
import os
from datetime import datetime

app = Flask(__name__)

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "intake_reports.db")

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS reports (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP,
        input TEXT,
        corrected_text TEXT,
        classification_type TEXT,
        classification_confidence INTEGER,
        template TEXT,
        priority_level TEXT,
        priority_score INTEGER,
        tasks TEXT,
        variables TEXT,
        gaps TEXT,
        entities TEXT,
        markdown TEXT,
        raw TEXT,
        profile TEXT
    )''')
    conn.commit()
    conn.close()

init_db()

@app.route("/", methods=["GET"])
def root():
    return send_file('intake-offline.html')

@app.route("/health", methods=["GET"])
def health():
    return jsonify({"ok": True, "module": "intake-decoder", "version": "2.0"})

@app.route("/api/reports", methods=["GET"])
def list_reports():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('SELECT id, created_at, classification_type, priority_level, priority_score, template, input FROM reports ORDER BY id DESC')
    rows = c.fetchall()
    conn.close()
    reports = []
    for row in rows:
        reports.append({
            "id": row[0],
            "created_at": row[1],
            "classification_type": row[2],
            "priority_level": row[3],
            "priority_score": row[4],
            "template": row[5],
            "preview": (row[6] or "")[:120]
        })
    return jsonify({"reports": reports, "count": len(reports)})

@app.route("/api/reports", methods=["POST"])
def save_report():
    data = request.get_json() or {}
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''INSERT INTO reports 
        (input, corrected_text, classification_type, classification_confidence, 
         template, priority_level, priority_score, tasks, variables, gaps, 
         entities, markdown, raw, profile)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
        (
            data.get('input', ''),
            data.get('corrected_text', ''),
            data.get('classification_type', ''),
            data.get('classification_confidence', 0),
            data.get('template', ''),
            data.get('priority_level', ''),
            data.get('priority_score', 0),
            json.dumps(data.get('tasks', [])),
            json.dumps(data.get('variables', [])),
            json.dumps(data.get('gaps', [])),
            json.dumps(data.get('entities', {})),
            data.get('markdown', ''),
            data.get('raw', ''),
            json.dumps(data.get('profile', {}))
        ))
    conn.commit()
    report_id = c.lastrowid
    conn.close()
    return jsonify({"ok": True, "id": report_id})

@app.route("/api/reports/<int:report_id>", methods=["GET"])
def get_report(report_id):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('SELECT * FROM reports WHERE id = ?', (report_id,))
    row = c.fetchone()
    conn.close()
    if not row:
        return jsonify({"error": "Not found"}), 404
    return jsonify({
        "id": row[0],
        "created_at": row[1],
        "input": row[2],
        "corrected_text": row[3],
        "classification_type": row[4],
        "classification_confidence": row[5],
        "template": row[6],
        "priority_level": row[7],
        "priority_score": row[8],
        "tasks": json.loads(row[9] or '[]'),
        "variables": json.loads(row[10] or '[]'),
        "gaps": json.loads(row[11] or '[]'),
        "entities": json.loads(row[12] or '{}'),
        "markdown": row[13],
        "raw": row[14],
        "profile": json.loads(row[15] or '{}')
    })

@app.route("/api/reports/<int:report_id>", methods=["DELETE"])
def delete_report(report_id):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('DELETE FROM reports WHERE id = ?', (report_id,))
    conn.commit()
    deleted = c.rowcount
    conn.close()
    return jsonify({"ok": deleted > 0, "deleted": deleted})

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    app.run(host="0.0.0.0", port=port)
