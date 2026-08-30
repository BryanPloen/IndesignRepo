#!/usr/bin/env python3
"""
generate_dom_visualizer.py - Dedicated InDesign Object Model Visualizer

Generates graphify-out/indesign_dom_model.html:
A clean, interactive D3 collapsible mindmap & object browser focusing EXCLUSIVELY
on the InDesign 2026 ExtendScript Object Model (no repo code files!).
"""

import json
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
DATA_PATH = ROOT_DIR / "data" / "indesign_api_2026.json"
OUT_HTML = ROOT_DIR / "graphify-out" / "indesign_dom_model.html"

def main():
    if not DATA_PATH.exists():
        print(f"[-] Data file {DATA_PATH} not found. Run parse_webhelp.py first.")
        return

    with open(DATA_PATH, "r", encoding="utf-8") as f:
        api_data = json.load(f)

    classes_dict = api_data.get("classes", {})

    dom_tree = {
        "name": "Application",
        "type": "Root",
        "children": [
            {
                "name": "Document",
                "type": "Core",
                "children": [
                    {
                        "name": "Layout & Pages",
                        "type": "Category",
                        "children": [
                            {"name": "MasterSpread", "type": "Class"},
                            {
                                "name": "Spread",
                                "type": "Class",
                                "children": [
                                    {"name": "Page", "type": "Class"}
                                ]
                            },
                            {"name": "Layer", "type": "Class"},
                            {"name": "Section", "type": "Class"},
                            {"name": "Guide", "type": "Class"}
                        ]
                    },
                    {
                        "name": "Page Items & Frames",
                        "type": "Category",
                        "children": [
                            {
                                "name": "TextFrame",
                                "type": "Class",
                                "children": [
                                    {
                                        "name": "Story",
                                        "type": "Class",
                                        "children": [
                                            {"name": "Paragraph", "type": "Class"},
                                            {"name": "Line", "type": "Class"},
                                            {"name": "Word", "type": "Class"},
                                            {"name": "Character", "type": "Class"},
                                            {
                                                "name": "Table",
                                                "type": "Class",
                                                "children": [
                                                    {"name": "Row", "type": "Class"},
                                                    {"name": "Column", "type": "Class"},
                                                    {"name": "Cell", "type": "Class"}
                                                ]
                                            }
                                        ]
                                    }
                                ]
                            },
                            {"name": "Rectangle", "type": "Class"},
                            {"name": "Oval", "type": "Class"},
                            {"name": "Polygon", "type": "Class"},
                            {"name": "GraphicLine", "type": "Class"},
                            {"name": "Group", "type": "Class"},
                            {
                                "name": "Graphic",
                                "type": "Class",
                                "children": [
                                    {"name": "Image", "type": "Class"},
                                    {"name": "PDF", "type": "Class"},
                                    {"name": "EPS", "type": "Class"}
                                ]
                            }
                        ]
                    },
                    {
                        "name": "Styles & Formatting",
                        "type": "Category",
                        "children": [
                            {"name": "ParagraphStyle", "type": "Class"},
                            {"name": "CharacterStyle", "type": "Class"},
                            {"name": "ObjectStyle", "type": "Class"},
                            {"name": "TableStyle", "type": "Class"},
                            {"name": "CellStyle", "type": "Class"}
                        ]
                    },
                    {
                        "name": "Colors & Swatches",
                        "type": "Category",
                        "children": [
                            {"name": "Color", "type": "Class"},
                            {"name": "Swatch", "type": "Class"},
                            {"name": "Tint", "type": "Class"},
                            {"name": "Gradient", "type": "Class"},
                            {"name": "Ink", "type": "Class"}
                        ]
                    },
                    {
                        "name": "Links & Assets",
                        "type": "Category",
                        "children": [
                            {"name": "Link", "type": "Class"},
                            {"name": "Font", "type": "Class"}
                        ]
                    },
                    {
                        "name": "Preferences & Output",
                        "type": "Category",
                        "children": [
                            {"name": "MarginPreference", "type": "Class"},
                            {"name": "TextFramePreference", "type": "Class"},
                            {"name": "PDFExportPreference", "type": "Class"},
                            {"name": "PrintPreference", "type": "Class"}
                        ]
                    }
                ]
            },
            {
                "name": "Book",
                "type": "Core",
                "children": [
                    {"name": "BookContent", "type": "Class"}
                ]
            }
        ]
    }

    tree_json_str = json.dumps(dom_tree)
    classes_json_str = json.dumps(classes_dict)

    html_content = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>Adobe InDesign 2026 ExtendScript Object Model</title>
  <script src="https://d3js.org/d3.v7.min.js"></script>
  <style>
    * { box-sizing: border-box; margin: 0; padding: 0; }
    body {
      font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
      background: #f8fafc;
      color: #0f172a;
      height: 100vh;
      overflow: hidden;
      display: flex;
    }
    #header {
      position: absolute;
      top: 16px;
      left: 20px;
      z-index: 10;
      background: rgba(255, 255, 255, 0.95);
      padding: 12px 20px;
      border-radius: 10px;
      box-shadow: 0 4px 12px rgba(0,0,0,0.08);
      border: 1px solid #e2e8f0;
    }
    #header h1 { font-size: 1.25rem; color: #0284c7; font-weight: 700; }
    #header p { font-size: 0.8rem; color: #64748b; margin-top: 2px; }

    #main { flex: 1; height: 100%; position: relative; }
    svg { width: 100%; height: 100%; cursor: grab; }
    svg:active { cursor: grabbing; }

    .node circle {
      fill: #fff;
      stroke-width: 2.5px;
      cursor: pointer;
      transition: r 0.2s, fill 0.2s;
    }
    .node circle:hover { r: 9; }
    .node text {
      font-size: 12px;
      font-weight: 600;
      fill: #1e293b;
      font-family: inherit;
    }
    .link {
      fill: none;
      stroke: #cbd5e1;
      stroke-width: 2px;
    }

    #sidebar {
      width: 420px;
      background: #ffffff;
      border-left: 1px solid #e2e8f0;
      display: flex;
      flex-direction: column;
      box-shadow: -4px 0 15px rgba(0,0,0,0.05);
      z-index: 10;
    }
    .sidebar-header {
      padding: 20px;
      border-bottom: 1px solid #e2e8f0;
      background: #f8fafc;
    }
    .sidebar-header h2 { font-size: 1.2rem; color: #0f172a; }
    .sidebar-header p { font-size: 0.85rem; color: #64748b; margin-top: 4px; }
    .sidebar-body {
      padding: 20px;
      overflow-y: auto;
      flex: 1;
      font-size: 0.85rem;
    }
    .section-title {
      font-weight: 700;
      color: #0284c7;
      text-transform: uppercase;
      font-size: 0.75rem;
      letter-spacing: 0.05em;
      margin-top: 15px;
      margin-bottom: 8px;
      border-bottom: 1px solid #e2e8f0;
      padding-bottom: 4px;
    }
    .item-list { display: flex; flex-direction: column; gap: 6px; }
    .item-row {
      background: #f1f5f9;
      padding: 8px 10px;
      border-radius: 6px;
      display: flex;
      justify-content: space-between;
      align-items: center;
    }
    .item-name { font-weight: 600; color: #334155; font-family: monospace; }
    .item-type { font-size: 0.75rem; color: #64748b; background: #e2e8f0; padding: 2px 6px; border-radius: 4px; }
  </style>
</head>
<body>
  <div id="header">
    <h1>InDesign 2026 Object Model</h1>
    <p>Interactive ExtendScript Hierarchy (Click nodes to inspect Properties & Methods)</p>
  </div>

  <div id="main">
    <svg id="tree-svg"></svg>
  </div>

  <div id="sidebar">
    <div class="sidebar-header">
      <h2 id="side-title">Select an Object</h2>
      <p id="side-desc">Click any node in the tree diagram to view details.</p>
    </div>
    <div class="sidebar-body" id="side-content">
      <p style="color: #94a3b8; text-align: center; margin-top: 40px;">Select an InDesign object (e.g. Document, TextFrame, Story) to view its API specification.</p>
    </div>
  </div>

  <script>
    const treeData = """ + tree_json_str + """;
    const classesData = """ + classes_json_str + """;

    const width = window.innerWidth - 420;
    const height = window.innerHeight;

    const svg = d3.select("#tree-svg")
      .attr("width", width)
      .attr("height", height);

    const g = svg.append("g").attr("transform", "translate(80, 0)");

    const zoom = d3.zoom()
      .scaleExtent([0.3, 3])
      .on("zoom", (event) => g.attr("transform", event.transform));

    svg.call(zoom);

    const tree = d3.tree().size([height - 60, width - 250]);
    const root = d3.hierarchy(treeData);

    tree(root);

    // Links
    g.selectAll(".link")
      .data(root.links())
      .enter().append("path")
      .attr("class", "link")
      .attr("d", d3.linkHorizontal()
        .x(d => d.y)
        .y(d => d.x));

    // Nodes
    const node = g.selectAll(".node")
      .data(root.descendants())
      .enter().append("g")
      .attr("class", "node")
      .attr("transform", d => `translate(${d.y},${d.x})`);

    const colorMap = {
      "Root": "#ef4444",
      "Core": "#0284c7",
      "Category": "#64748b",
      "Class": "#10b981"
    };

    node.append("circle")
      .attr("r", d => d.data.type === "Root" ? 9 : (d.data.type === "Core" ? 8 : 6))
      .attr("stroke", d => colorMap[d.data.type] || "#10b981")
      .attr("fill", d => colorMap[d.data.type] || "#10b981")
      .on("click", (event, d) => inspectNode(d.data.name));

    node.append("text")
      .attr("dy", "0.31em")
      .attr("x", d => d.children ? -12 : 12)
      .attr("text-anchor", d => d.children ? "end" : "start")
      .text(d => d.data.name);

    function inspectNode(name) {
      const sideTitle = document.getElementById("side-title");
      const sideDesc = document.getElementById("side-desc");
      const sideContent = document.getElementById("side-content");

      sideTitle.innerText = name;

      if (classesData[name]) {
        const c = classesData[name];
        sideDesc.innerText = c.description || "InDesign ExtendScript DOM Class";

        let html = "";
        
        // Properties
        if (c.properties && c.properties.length > 0) {
          html += '<div class="section-title">Properties (' + c.properties.length + ')</div>';
          html += '<div class="item-list">';
          c.properties.forEach(p => {
            html += '<div class="item-row"><div><span class="item-name">.' + p.name + '</span><br><span style="font-size:0.75rem; color:#64748b;">' + p.description + '</span></div><span class="item-type">' + p.type + '</span></div>';
          });
          html += '</div>';
        }

        // Methods
        if (c.methods && c.methods.length > 0) {
          html += '<div class="section-title">Methods (' + c.methods.length + ')</div>';
          html += '<div class="item-list">';
          c.methods.forEach(m => {
            html += '<div class="item-row"><div><span class="item-name">' + m.name + '()</span><br><span style="font-size:0.75rem; color:#64748b;">' + m.description + '</span></div><span class="item-type">' + m.return_type + '</span></div>';
          });
          html += '</div>';
        }

        sideContent.innerHTML = html;
      } else {
        sideDesc.innerText = "InDesign DOM Category Container";
        sideContent.innerHTML = '<p style="color: #64748b;">Select a specific class node (e.g. Document, Spread, Page, TextFrame, Story) to view properties and methods.</p>';
      }
    }
  </script>
</body>
</html>"""

    OUT_HTML.parent.mkdir(parents=True, exist_ok=True)
    with open(OUT_HTML, "w", encoding="utf-8") as f:
        f.write(html_content)

    print(f"[+] InDesign Object Model Visualizer created at {OUT_HTML}")

if __name__ == "__main__":
    main()
