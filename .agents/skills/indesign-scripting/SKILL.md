---
name: indesign-scripting
description: Use when writing, debugging, or querying Adobe InDesign 2026 (v21.0) ExtendScript scripts (.jsx). Provides guidelines for ES3 syntax, object model lookups, unit conversions, and snippet recipes.
---

# InDesign 2026 ExtendScript Development Skill

This skill provides complete reference rules and query interfaces for writing production-grade ExtendScript (`.jsx`) scripts for Adobe InDesign 2026.

## Critical ExtendScript Rules (ECMAScript 3)

1. **Syntax Constraints:**
   - Use `var` only. Do NOT use `let`, `const`, or arrow functions (`=>`).
   - Do NOT use ES6 template literals (`` `text ${var}` ``). Use string concatenation (`"text " + variable`).
   - Do NOT use modern array methods like `.forEach()`, `.map()`, `.filter()`, or `.includes()`. Use traditional `for` loops.

2. **Script Structure:**
   - Always wrap main code in an IIFE `(function() { ... })();` to avoid polluting global namespace.
   - Wrap operations in a `try...catch(e)` block with user-friendly `alert()` reporting.
   - For multi-step operations, group into a single undo step using `app.doScript(main, ScriptLanguage.JAVASCRIPT, [], UndoModes.ENTIRE_SCRIPT, "Script Name");`.

3. **Measurement Units:**
   - Save and restore ruler units before modifying coordinates (`doc.viewPreferences.horizontalMeasurementUnits`).

---

## Fast API Lookup CLI Commands

Use the local python search tool to verify signatures before writing code:

- **Lookup Class Properties & Methods:**
  ```bash
  python scripts/search_api.py --class Document
  python scripts/search_api.py --class TextFrame
  ```

- **Lookup Enum Values:**
  ```bash
  python scripts/search_api.py --enum Justification
  python scripts/search_api.py --enum FitOptions
  ```

- **Full-Text API Search:**
  ```bash
  python scripts/search_api.py --query exportFile
  ```

---

## Core Object Model Hierarchy

- `app` (`Application`)
  - `.documents` (`Document`)
    - `.spreads` (`Spread`)
    - `.pages` (`Page`)
      - `.textFrames` (`TextFrame`)
      - `.rectangles` (`Rectangle`)
      - `.ovals` (`Oval`)
      - `.graphicLines` (`GraphicLine`)
    - `.stories` (`Story`)
      - `.paragraphs` (`Paragraph`)
      - `.lines` (`Line`)
      - `.words` (`Word`)
      - `.characters` (`Character`)
      - `.tables` (`Table`)
    - `.paragraphStyles` (`ParagraphStyle`)
    - `.characterStyles` (`CharacterStyle`)
    - `.colors` (`Color`)
    - `.swatches` (`Swatch`)
