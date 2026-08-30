#!/usr/bin/env python3
"""
parse_webhelp.py - InDesign 2026 ExtendScript API Parser

Parses Oxygen WebHelp HTML topic files in webhelp/ into:
 1. data/indesign_api_2026.json (Structured JSON document)
 2. data/indesign_api_2026.db (SQLite database with FTS5 search index)
"""

import os
import re
import json
import sqlite3
import sys
from pathlib import Path
from html.parser import HTMLParser

ROOT_DIR = Path(__file__).resolve().parent.parent
WEBHELP_DIR = ROOT_DIR / "webhelp"
DATA_DIR = ROOT_DIR / "data"
JSON_OUT = DATA_DIR / "indesign_api_2026.json"
DB_OUT = DATA_DIR / "indesign_api_2026.db"

SKIP_FILES = {
    "index.html", "index_frames.html", "about.html", "indexterms.html",
    "toc.html", "search.html", "undefined.html"
}

class SimpleHTMLTextExtractor(HTMLParser):
    def __init__(self):
        super().__init__()
        self.text_parts = []
    def handle_data(self, data):
        self.text_parts.append(data)
    def get_text(self):
        return "".join(self.text_parts).strip()

def strip_tags(html_content):
    parser = SimpleHTMLTextExtractor()
    parser.feed(html_content)
    text = parser.get_text()
    return re.sub(r'\s+', ' ', text)

def parse_html_file(file_path):
    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
        html = f.read()

    # Extract title
    title_match = re.search(r'<h1 class="title topictitle1">\s*<span class="keyword">(.*?)</span>\s*</h1>', html, re.DOTALL)
    if not title_match:
        return None
    topic_name = title_match.group(1).strip()

    # Extract main topic description
    desc_match = re.search(r'<p class="p description">(.*?)</p>', html, re.DOTALL)
    topic_desc = strip_tags(desc_match.group(1)) if desc_match else ""

    # Check if Enum topic
    if '<h2 class="title sectiontitle">Values</h2>' in html:
        return parse_enum_topic(topic_name, topic_desc, html)
    else:
        return parse_class_topic(topic_name, topic_desc, html)

def parse_enum_topic(enum_name, enum_desc, html):
    values = []
    values_sec = re.search(r'<h2 class="title sectiontitle">Values</h2>.*?(<tbody.*?>.*?</tbody>)', html, re.DOTALL)
    if values_sec:
        tbody = values_sec.group(1)
        rows = re.findall(r'<tr class="row">(.*?)</tr>', tbody, re.DOTALL)
        for row in rows:
            tds = re.findall(r'<td.*?>(.*?)</td>', row, re.DOTALL)
            if len(tds) >= 3:
                val_name = strip_tags(tds[0])
                val_desc = strip_tags(tds[1])
                val_num = strip_tags(tds[2])
                values.append({
                    "name": val_name,
                    "description": val_desc,
                    "value": val_num
                })
    return {
        "type": "enum",
        "name": enum_name,
        "description": enum_desc,
        "values": values
    }

def parse_class_topic(class_name, class_desc, html):
    properties = []
    methods = []
    
    # 1. Parse Properties Table
    props_sec = re.search(r'<h2 class="title sectiontitle">Property Listing</h2>.*?(<tbody.*?>.*?</tbody>)', html, re.DOTALL)
    if props_sec:
        tbody = props_sec.group(1)
        rows = re.findall(r'<tr class="row">(.*?)</tr>', tbody, re.DOTALL)
        for row in rows:
            tds = re.findall(r'<td.*?>(.*?)</td>', row, re.DOTALL)
            if len(tds) >= 4:
                p_name = strip_tags(tds[0]).lstrip('.')
                p_type = strip_tags(tds[1])
                p_access = strip_tags(tds[2])
                p_desc = strip_tags(tds[3])
                properties.append({
                    "name": p_name,
                    "type": p_type,
                    "access": p_access,
                    "description": p_desc
                })

    # 2. Parse Method Listing
    methods_sec = re.search(r'<h2 class="title sectiontitle">Method Listing</h2>(.*)', html, re.DOTALL)
    if methods_sec:
        m_content = methods_sec.group(1)
        m_blocks = re.split(r'<p class="p methodName"', m_content)[1:]
        for block in m_blocks:
            full_block = '<p class="p methodName"' + block
            
            p_mname_match = re.search(r'<p class="p methodName".*?>(.*?)</p>', full_block, re.DOTALL)
            if not p_mname_match:
                continue
            
            raw_sig_html = p_mname_match.group(1)
            raw_sig_text = strip_tags(raw_sig_html)
            
            name_match = re.search(r'class="ph b clip_button">(.*?)</strong>', raw_sig_html)
            if not name_match:
                name_match = re.search(r'class="ph b">(.*?)</strong>', raw_sig_html)
            m_name = name_match.group(1).strip() if name_match else raw_sig_text.split('(')[0].split()[-1]
            
            return_type = "void"
            ret_match = re.search(r'^\s*<a.*?>\s*(.*?)\s*</a>', raw_sig_html)
            if ret_match:
                return_type = strip_tags(ret_match.group(1))
            else:
                tokens = raw_sig_text.split()
                if tokens and tokens[0] != m_name:
                    return_type = tokens[0]

            m_desc_match = re.search(r'<p class="p description">(.*?)</p>', full_block, re.DOTALL)
            m_desc = strip_tags(m_desc_match.group(1)) if m_desc_match else ""
            
            params = []
            param_tbl = re.search(r'<table.*?class="table parameterTable".*?<tbody.*?>(.*?)</tbody>', full_block, re.DOTALL)
            if param_tbl:
                p_rows = re.findall(r'<tr class="row">(.*?)</tr>', param_tbl.group(1), re.DOTALL)
                for pr in p_rows:
                    ptds = re.findall(r'<td.*?>(.*?)</td>', pr, re.DOTALL)
                    if len(ptds) >= 3:
                        params.append({
                            "name": strip_tags(ptds[0]),
                            "type": strip_tags(ptds[1]),
                            "description": strip_tags(ptds[2])
                        })

            methods.append({
                "name": m_name,
                "signature": raw_sig_text,
                "return_type": return_type,
                "description": m_desc,
                "parameters": params
            })

    return {
        "type": "class",
        "name": class_name,
        "description": class_desc,
        "properties": properties,
        "methods": methods
    }

def main():
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    print(f"[*] Scanning WebHelp HTML files in {WEBHELP_DIR}...")
    
    classes = {}
    enums = {}
    
    html_files = [f for f in os.listdir(WEBHELP_DIR) if f.endswith(".html") and f not in SKIP_FILES]
    print(f"[*] Found {len(html_files)} topic HTML files.")

    for filename in html_files:
        filepath = WEBHELP_DIR / filename
        data = parse_html_file(filepath)
        if not data:
            continue
        
        if data["type"] == "enum":
            enums[data["name"]] = data
        elif data["type"] == "class":
            classes[data["name"]] = data

    print(f"[+] Successfully parsed {len(classes)} classes/objects and {len(enums)} enumerations.")

    # Save JSON
    output_json_data = {
        "metadata": {
            "version": "Adobe InDesign 2026 (21.0.0.192)",
            "classes_count": len(classes),
            "enums_count": len(enums)
        },
        "classes": classes,
        "enums": enums
    }
    with open(JSON_OUT, "w", encoding="utf-8") as f:
        json.dump(output_json_data, f, indent=2)
    print(f"[+] Saved structured JSON to {JSON_OUT}")

    # Build SQLite Database
    if DB_OUT.exists():
        os.remove(DB_OUT)
        
    conn = sqlite3.connect(DB_OUT)
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE classes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT UNIQUE NOT NULL,
        description TEXT
    );
    """)

    cur.execute("""
    CREATE TABLE properties (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        class_name TEXT,
        name TEXT,
        type TEXT,
        access TEXT,
        description TEXT,
        FOREIGN KEY(class_name) REFERENCES classes(name)
    );
    """)

    cur.execute("""
    CREATE TABLE methods (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        class_name TEXT,
        name TEXT,
        signature TEXT,
        return_type TEXT,
        description TEXT,
        FOREIGN KEY(class_name) REFERENCES classes(name)
    );
    """)

    cur.execute("""
    CREATE TABLE method_params (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        method_id INTEGER,
        name TEXT,
        type TEXT,
        description TEXT,
        FOREIGN KEY(method_id) REFERENCES methods(id)
    );
    """)

    cur.execute("""
    CREATE TABLE enums (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT UNIQUE NOT NULL,
        description TEXT
    );
    """)

    cur.execute("""
    CREATE TABLE enum_values (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        enum_name TEXT,
        name TEXT,
        value TEXT,
        description TEXT,
        FOREIGN KEY(enum_name) REFERENCES enums(name)
    );
    """)

    # FTS Search Index
    cur.execute("""
    CREATE VIRTUAL TABLE api_fts USING fts5(
        kind,
        parent_name,
        name,
        details,
        description
    );
    """)

    # Populate Classes
    for c_name, c_data in classes.items():
        cur.execute("INSERT INTO classes (name, description) VALUES (?, ?)", (c_name, c_data["description"]))
        cur.execute("INSERT INTO api_fts (kind, parent_name, name, details, description) VALUES (?, ?, ?, ?, ?)",
                    ("class", "", c_name, "", c_data["description"]))

        for prop in c_data["properties"]:
            cur.execute("""
            INSERT INTO properties (class_name, name, type, access, description)
            VALUES (?, ?, ?, ?, ?)
            """, (c_name, prop["name"], prop["type"], prop["access"], prop["description"]))
            cur.execute("INSERT INTO api_fts (kind, parent_name, name, details, description) VALUES (?, ?, ?, ?, ?)",
                        ("property", c_name, prop["name"], f"Type: {prop['type']} | Access: {prop['access']}", prop["description"]))

        for meth in c_data["methods"]:
            cur.execute("""
            INSERT INTO methods (class_name, name, signature, return_type, description)
            VALUES (?, ?, ?, ?, ?)
            """, (c_name, meth["name"], meth["signature"], meth["return_type"], meth["description"]))
            m_id = cur.lastrowid
            cur.execute("INSERT INTO api_fts (kind, parent_name, name, details, description) VALUES (?, ?, ?, ?, ?)",
                        ("method", c_name, meth["name"], f"Return: {meth['return_type']} | Signature: {meth['signature']}", meth["description"]))

            for param in meth["parameters"]:
                cur.execute("""
                INSERT INTO method_params (method_id, name, type, description)
                VALUES (?, ?, ?, ?)
                """, (m_id, param["name"], param["type"], param["description"]))

    # Populate Enums
    for e_name, e_data in enums.items():
        cur.execute("INSERT INTO enums (name, description) VALUES (?, ?)", (e_name, e_data["description"]))
        cur.execute("INSERT INTO api_fts (kind, parent_name, name, details, description) VALUES (?, ?, ?, ?, ?)",
                    ("enum", "", e_name, "", e_data["description"]))

        for evalue in e_data["values"]:
            cur.execute("""
            INSERT INTO enum_values (enum_name, name, value, description)
            VALUES (?, ?, ?, ?)
            """, (e_name, evalue["name"], evalue["value"], evalue["description"]))
            cur.execute("INSERT INTO api_fts (kind, parent_name, name, details, description) VALUES (?, ?, ?, ?, ?)",
                        ("enum_value", e_name, evalue["name"], f"Value: {evalue['value']}", evalue["description"]))

    conn.commit()
    conn.close()
    print(f"[+] SQLite database created successfully at {DB_OUT}")

if __name__ == "__main__":
    main()
