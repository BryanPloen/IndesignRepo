#!/usr/bin/env python3
"""
generate_graph.py - Comprehensive InDesign DOM Relationship Graph Generator

Parses data/indesign_api_2026.json and SQLite DB to generate:
 1. graphify-out/graph.html (Full D3.js Interactive Relationship Graph with Arrows & Relationship Types)
 2. graphify-out/GRAPH_REPORT.md (Markdown Relationship Breakdown)
 3. graphify-out/graph.json (Graph Dataset)
"""

import sys
import json
import sqlite3
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT_DIR / "data"
DB_PATH = DATA_DIR / "indesign_api_2026.db"
JSON_PATH = DATA_DIR / "indesign_api_2026.json"
GRAPH_OUT_DIR = ROOT_DIR / "graphify-out"

def build_full_relationship_graph():
    GRAPH_OUT_DIR.mkdir(parents=True, exist_ok=True)
    report_file = GRAPH_OUT_DIR / "GRAPH_REPORT.md"
    graph_json_file = GRAPH_OUT_DIR / "graph.json"
    graph_html_file = GRAPH_OUT_DIR / "graph.html"
    
    if not DB_PATH.exists() or not JSON_PATH.exists():
        print("[-] API data not found. Run parse_webhelp.py first.")
        return

    with open(JSON_PATH, "r", encoding="utf-8") as f:
        api_data = json.load(f)

    classes_dict = api_data.get("classes", {})
    enums_dict = api_data.get("enums", {})

    nodes = []
    links = []
    node_set = set()

    def add_node(node_id, group, label, desc=""):
        if node_id not in node_set:
            nodes.append({"id": node_id, "group": group, "label": label, "desc": desc})
            node_set.add(node_id)

    # 1. Primary InDesign Core Hierarchy
    core_relationships = [
        ("Application", "Document", "contains (collection)"),
        ("Application", "Book", "contains (collection)"),
        ("Application", "Font", "references"),
        ("Application", "Color", "default swatches"),
        
        ("Document", "Spread", "contains spreads"),
        ("Document", "MasterSpread", "contains master spreads"),
        ("Document", "Page", "contains pages"),
        ("Document", "Layer", "contains layers"),
        ("Document", "Story", "contains text stories"),
        ("Document", "TextFrame", "contains text frames"),
        ("Document", "Graphic", "contains graphics"),
        ("Document", "ParagraphStyle", "contains styles"),
        ("Document", "CharacterStyle", "contains styles"),
        ("Document", "Color", "contains colors"),
        ("Document", "Swatch", "contains swatches"),
        ("Document", "Link", "tracks file links"),

        ("Spread", "Page", "owns pages"),
        ("Spread", "PageItem", "owns page items"),
        ("Spread", "TextFrame", "contains text frames"),
        ("Spread", "Rectangle", "contains rectangles"),

        ("Page", "PageItem", "contains elements"),
        ("Page", "TextFrame", "contains text frames"),
        ("Page", "Rectangle", "contains shapes"),
        ("Page", "Oval", "contains shapes"),
        ("Page", "Group", "contains groups"),

        ("TextFrame", "Story", "displays story"),
        ("TextFrame", "Paragraph", "contains paragraphs"),
        ("TextFrame", "TextFramePreference", "configured by"),
        ("TextFrame", "BaselineFrameGridOption", "configured by"),

        ("Story", "Paragraph", "contains paragraphs"),
        ("Story", "Line", "contains text lines"),
        ("Story", "Word", "contains words"),
        ("Story", "Character", "contains characters"),
        ("Story", "Table", "embeds tables"),

        ("Table", "Row", "contains rows"),
        ("Table", "Column", "contains columns"),
        ("Table", "Cell", "contains cells"),

        ("Cell", "Paragraph", "contains paragraph text"),
        ("Cell", "Table", "nested table"),
    ]

    for src, tgt, rel in core_relationships:
        add_node(src, "CoreDOM", src, f"Core InDesign Object: {src}")
        add_node(tgt, "DOMObject", tgt, f"InDesign Object: {tgt}")
        links.append({"source": src, "target": tgt, "relation": rel})

    # 2. Extract Property Type relationships from parsed API classes
    important_classes = ["Document", "Page", "TextFrame", "Story", "Paragraph", "CharacterStyle", "ParagraphStyle", "Table", "Cell", "Layer", "PDFExportPreference"]
    
    for cname in important_classes:
        if cname in classes_dict:
            c_info = classes_dict[cname]
            add_node(cname, "CoreDOM" if cname in ["Application", "Document"] else "DOMObject", cname, c_info.get("description", ""))
            
            for prop in c_info.get("properties", []):
                ptype = prop.get("type", "").strip()
                pname = prop.get("name", "")
                
                # Check if property type links to another known Class or Enum
                target_type = ptype.replace("Array of ", "").strip()
                if target_type in classes_dict and target_type != cname:
                    add_node(target_type, "Class", target_type, classes_dict[target_type].get("description", ""))
                    links.append({
                        "source": cname,
                        "target": target_type,
                        "relation": f".{pname} -> {ptype}"
                    })
                elif target_type in enums_dict:
                    add_node(target_type, "Enum", target_type, enums_dict[target_type].get("description", ""))
                    links.append({
                        "source": cname,
                        "target": target_type,
                        "relation": f".{pname} (enum)"
                    })

    # Save JSON Graph Dataset
    graph_data = {"nodes": nodes, "links": links}
    with open(graph_json_file, "w", encoding="utf-8") as f:
        json.dump(graph_data, f, indent=2)

    # Markdown Report
    report_lines = [
        "# InDesign 2026 ExtendScript Object Relationship Report",
        "",
        "## Core Hierarchy Map",
        "```mermaid",
        "graph TD",
        "    Application -- contains --> Document",
        "    Application -- contains --> Book",
        "    Document -- contains --> Spread",
        "    Document -- contains --> Page",
        "    Document -- contains --> Layer",
        "    Document -- contains --> Story",
        "    Spread -- owns --> Page",
        "    Page -- contains --> TextFrame",
        "    Page -- contains --> Rectangle",
        "    TextFrame -- displays --> Story",
        "    Story -- contains --> Paragraph",
        "    Story -- embeds --> Table",
        "    Table -- contains --> Cell",
        "```",
        "",
        "## Total Indexed Graph Entities",
        f"- Total Nodes: {len(nodes)}",
        f"- Total Edge Relationships: {len(links)}",
        "- Interactive Visual Graph: `graphify-out/graph.html`"
    ]
    with open(report_file, "w", encoding="utf-8") as f:
        f.write("\n".join(report_lines))

    # Generate Full D3.js Interactive HTML with Directional Arrows & Edge Labels
    graph_html_content = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>InDesign 2026 ExtendScript API Knowledge Graph</title>
    <script src="https://d3js.org/d3.v7.min.js"></script>
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; background: #0f172a; color: #f8fafc; overflow: hidden; height: 100vh; display: flex; }
        #sidebar { width: 360px; background: #1e293b; border-right: 1px solid #334155; padding: 20px; display: flex; flex-direction: column; gap: 15px; z-index: 10; box-shadow: 4px 0 15px rgba(0,0,0,0.4); }
        h1 { font-size: 1.2rem; font-weight: 700; color: #38bdf8; display: flex; align-items: center; gap: 8px; }
        .subtitle { font-size: 0.8rem; color: #94a3b8; margin-bottom: 5px; }
        input[type="text"] { width: 100%; padding: 10px 14px; background: #0f172a; border: 1px solid #475569; border-radius: 8px; color: #fff; font-size: 0.9rem; outline: none; }
        input[type="text"]:focus { border-color: #38bdf8; }
        .legend { display: flex; flex-direction: column; gap: 8px; font-size: 0.85rem; background: #0f172a; padding: 12px; border-radius: 8px; border: 1px solid #334155; }
        .legend-item { display: flex; align-items: center; gap: 8px; }
        .dot { width: 12px; height: 12px; border-radius: 50%; display: inline-block; }
        #detail-card { background: #0f172a; border: 1px solid #38bdf8; border-radius: 8px; padding: 14px; margin-top: auto; font-size: 0.85rem; line-height: 1.4; }
        #detail-card h3 { color: #38bdf8; margin-bottom: 6px; }
        #detail-card .rel-tag { background: #334155; color: #fbbf24; padding: 2px 6px; border-radius: 4px; font-family: monospace; font-size: 0.75rem; margin-top: 6px; display: inline-block; }
        #main { flex: 1; position: relative; }
        svg { width: 100%; height: 100%; cursor: grab; }
        svg:active { cursor: grabbing; }
        .node circle { stroke: #fff; stroke-width: 1.5px; cursor: pointer; transition: transform 0.2s; }
        .node circle:hover { transform: scale(1.25); }
        .node text { font-size: 11px; fill: #f1f5f9; pointer-events: none; text-anchor: middle; font-weight: 600; text-shadow: 0 1px 3px rgba(0,0,0,0.8); }
        .link { stroke: #64748b; stroke-opacity: 0.6; stroke-width: 1.5px; }
        .link-label { font-size: 9px; fill: #fbbf24; font-family: monospace; pointer-events: none; text-anchor: middle; }
    </style>
</head>
<body>
    <div id="sidebar">
        <div>
            <h1>InDesign API Knowledge Graph</h1>
            <div class="subtitle">Adobe InDesign 2026 (v21.0) Object Relationships</div>
        </div>
        <input type="text" id="search" placeholder="Search entity (e.g. Document, Story)..." oninput="onSearch()">
        <div class="legend">
            <div class="legend-item"><span class="dot" style="background: #ef4444;"></span> Core DOM (Application/Document)</div>
            <div class="legend-item"><span class="dot" style="background: #3b82f6;"></span> DOM Objects (Spread/Page/TextFrame)</div>
            <div class="legend-item"><span class="dot" style="background: #10b981;"></span> Linked Classes</div>
            <div class="legend-item"><span class="dot" style="background: #f59e0b;"></span> Enums</div>
        </div>
        <div id="detail-card">
            <h3 id="card-title">Select any Node or Link</h3>
            <p id="card-desc">Click on any node or edge in the graph to inspect relationship types, parent containers, and descriptions.</p>
            <div id="card-rel" class="rel-tag" style="display:none;"></div>
        </div>
    </div>
    <div id="main">
        <svg id="viz"></svg>
    </div>

    <script>
        const graphData = """ + json.dumps(graph_data) + """;

        const width = window.innerWidth - 360;
        const height = window.innerHeight;

        const svg = d3.select("#viz")
            .attr("width", width)
            .attr("height", height);

        // Define Arrow Markers for Directed Edges
        svg.append("defs").append("marker")
            .attr("id", "arrow")
            .attr("viewBox", "0 -5 10 10")
            .attr("refX", 22)
            .attr("refY", 0)
            .attr("markerWidth", 6)
            .attr("markerHeight", 6)
            .attr("orient", "auto")
            .append("path")
            .attr("d", "M0,-5L10,0L0,5")
            .attr("fill", "#94a3b8");

        const g = svg.append("g");

        const zoom = d3.zoom()
            .scaleExtent([0.1, 4])
            .on("zoom", (event) => g.attr("transform", event.transform));

        svg.call(zoom);

        const colorMap = {
            "CoreDOM": "#ef4444",
            "DOMObject": "#3b82f6",
            "Class": "#10b981",
            "Enum": "#f59e0b"
        };

        const simulation = d3.forceSimulation(graphData.nodes)
            .force("link", d3.forceLink(graphData.links).id(d => d.id).distance(120))
            .force("charge", d3.forceManyBody().strength(-300))
            .force("center", d3.forceCenter(width / 2, height / 2))
            .force("collision", d3.forceCollide().radius(35));

        const link = g.append("g")
            .selectAll("line")
            .data(graphData.links)
            .enter().append("line")
            .attr("class", "link")
            .attr("marker-end", "url(#arrow)");

        const linkLabels = g.append("g")
            .selectAll(".link-label")
            .data(graphData.links)
            .enter().append("text")
            .attr("class", "link-label")
            .text(d => d.relation);

        const node = g.append("g")
            .selectAll(".node")
            .data(graphData.nodes)
            .enter().append("g")
            .attr("class", "node")
            .call(d3.drag()
                .on("start", dragstarted)
                .on("drag", dragged)
                .on("end", dragended));

        node.append("circle")
            .attr("r", d => d.group === "CoreDOM" ? 18 : (d.group === "DOMObject" ? 14 : 10))
            .attr("fill", d => colorMap[d.group] || "#8b5cf6")
            .on("click", (event, d) => showDetail(d));

        node.append("text")
            .attr("dy", 24)
            .text(d => d.label);

        simulation.on("tick", () => {
            link
                .attr("x1", d => d.source.x)
                .attr("y1", d => d.source.y)
                .attr("x2", d => d.target.x)
                .attr("y2", d => d.target.y);

            linkLabels
                .attr("x", d => (d.source.x + d.target.x) / 2)
                .attr("y", d => (d.source.y + d.target.y) / 2 - 4);

            node.attr("transform", d => `translate(${d.x},${d.y})`);
        });

        function dragstarted(event, d) {
            if (!event.active) simulation.alphaTarget(0.3).restart();
            d.fx = d.x;
            d.fy = d.y;
        }

        function dragged(event, d) {
            d.fx = event.x;
            d.fy = event.y;
        }

        function dragended(event, d) {
            if (!event.active) simulation.alphaTarget(0);
            d.fx = null;
            d.fy = null;
        }

        function showDetail(d) {
            const card = document.getElementById("detail-card");
            const title = document.getElementById("card-title");
            const desc = document.getElementById("card-desc");
            const relTag = document.getElementById("card-rel");

            title.innerText = d.label + " (" + d.group + ")";
            desc.innerText = d.desc || "InDesign 2026 API Entity.";
            
            // Find connected nodes & relations
            const connected = graphData.links.filter(l => l.source.id === d.id || l.target.id === d.id);
            if (connected.length > 0) {
                relTag.style.display = "block";
                relTag.innerText = connected.length + " Connected Edge Relationships";
            } else {
                relTag.style.display = "none";
            }
        }

        function onSearch() {
            const val = document.getElementById("search").value.toLowerCase();
            node.selectAll("circle")
                .attr("opacity", d => d.label.toLowerCase().includes(val) ? 1 : 0.15);
            node.selectAll("text")
                .attr("opacity", d => d.label.toLowerCase().includes(val) ? 1 : 0.15);
            link.attr("opacity", d => (d.source.label.toLowerCase().includes(val) || d.target.label.toLowerCase().includes(val)) ? 1 : 0.1);
            linkLabels.attr("opacity", d => (d.source.label.toLowerCase().includes(val) || d.target.label.toLowerCase().includes(val)) ? 1 : 0.1);
        }
    </script>
</body>
</html>"""

    with open(graph_html_file, "w", encoding="utf-8") as f:
        f.write(graph_html_content)

    print(f"[+] Full Relationship Graph successfully updated at {graph_html_file}")

if __name__ == "__main__":
    build_full_relationship_graph()
