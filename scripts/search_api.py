#!/usr/bin/env python3
"""
search_api.py - CLI tool for searching InDesign 2026 ExtendScript API Database

Usage:
  python scripts/search_api.py --class Document
  python scripts/search_api.py --enum Justification
  python scripts/search_api.py --query exportFile
"""

import sys
import sqlite3
import argparse
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
DB_PATH = ROOT_DIR / "data" / "indesign_api_2026.db"

def get_db():
    if not DB_PATH.exists():
        print(f"Error: Database file not found at {DB_PATH}. Run 'python scripts/parse_webhelp.py' first.")
        sys.exit(1)
    return sqlite3.connect(DB_PATH)

def search_class(class_name):
    conn = get_db()
    cur = conn.cursor()
    
    cur.execute("SELECT name, description FROM classes WHERE name LIKE ?", (class_name,))
    cls = cur.fetchone()
    if not cls:
        print(f"No class found matching '{class_name}'.")
        return
    
    print(f"\n==========================================")
    print(f" CLASS: {cls[0]}")
    print(f"==========================================")
    print(f"Description: {cls[1]}\n")

    # Properties
    cur.execute("SELECT name, type, access, description FROM properties WHERE class_name = ? ORDER BY name", (cls[0],))
    props = cur.fetchall()
    print(f"--- PROPERTIES ({len(props)}) ---")
    for p in props[:30]:  # limit to top 30 if large
        print(f"  • .{p[0]} [{p[1]}] ({p[2]}): {p[3]}")
    if len(props) > 30:
        print(f"  ... and {len(props) - 30} more properties.")

    # Methods
    cur.execute("SELECT name, signature, return_type, description FROM methods WHERE class_name = ? ORDER BY name", (cls[0],))
    methods = cur.fetchall()
    print(f"\n--- METHODS ({len(methods)}) ---")
    for m in methods[:30]:
        print(f"  • {m[1]} -> {m[2]}")
        if m[3]:
            print(f"    {m[3]}")
    if len(methods) > 30:
        print(f"  ... and {len(methods) - 30} more methods.")
    print()

def search_enum(enum_name):
    conn = get_db()
    cur = conn.cursor()
    
    cur.execute("SELECT name, description FROM enums WHERE name LIKE ?", (enum_name,))
    en = cur.fetchone()
    if not en:
        print(f"No enum found matching '{enum_name}'.")
        return
    
    print(f"\n==========================================")
    print(f" ENUM: {en[0]}")
    print(f"==========================================")
    print(f"Description: {en[1]}\n")

    cur.execute("SELECT name, value, description FROM enum_values WHERE enum_name = ? ORDER BY name", (en[0],))
    vals = cur.fetchall()
    print(f"--- VALUES ({len(vals)}) ---")
    for v in vals:
        print(f"  • {v[0]} = {v[1]}")
        if v[2]:
            print(f"    {v[2]}")
    print()

def full_text_search(query):
    conn = get_db()
    cur = conn.cursor()
    
    cur.execute("""
    SELECT kind, parent_name, name, details, description
    FROM api_fts
    WHERE api_fts MATCH ?
    LIMIT 25
    """, (query,))
    results = cur.fetchall()
    
    print(f"\n==========================================")
    print(f" SEARCH RESULTS FOR: '{query}'")
    print(f"==========================================")
    if not results:
        print("No matching API elements found.")
        return
        
    for r in results:
        kind, parent, name, details, desc = r
        if parent:
            item_name = f"{parent}.{name}"
        else:
            item_name = name
        print(f"[{kind.upper()}] {item_name}")
        if details:
            print(f"  Details: {details}")
        if desc:
            print(f"  Description: {desc}")
        print("-" * 40)
    print()

def main():
    parser = argparse.ArgumentParser(description="InDesign 2026 ExtendScript API CLI Search Tool")
    parser.add_argument("--class", dest="class_name", help="Lookup class by name")
    parser.add_argument("--enum", dest="enum_name", help="Lookup enum by name")
    parser.add_argument("--query", "-q", dest="query", help="Full-text search query")

    args = parser.parse_args()

    if args.class_name:
        search_class(args.class_name)
    elif args.enum_name:
        search_enum(args.enum_name)
    elif args.query:
        full_text_search(args.query)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
