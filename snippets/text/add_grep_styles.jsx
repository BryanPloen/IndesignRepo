/**
 * ExtendScript Snippet: GREP- und Zeichenformate zu Absatzformat hinzufügen
 * Adobe InDesign 2026 (v21.0)
 *
 * Erstellt automatisch Zeichenformate und weist GREP-Regeln einem frei wählbaren Absatzformat zu.
 */

#target indesign

(function () {
    if (app.documents.length === 0) {
        alert("Bitte öffnen Sie ein InDesign-Dokument, bevor Sie dieses Skript ausführen.");
        return;
    }

    app.doScript(
        main,
        ScriptLanguage.JAVASCRIPT,
        [],
        UndoModes.ENTIRE_SCRIPT,
        "GREP-Formate Snippet"
    );

    function isNoParagraphStyle(style) {
        if (!style || !style.isValid) return true;
        var name = style.name;
        if (name === "[No Paragraph Style]" || name === "[Kein Absatzformat]" ||
            name === "[Aucun style de paragraphe]" || name === "[Sin estilo de párrafo]") {
            return true;
        }
        return false;
    }

    function main() {
        var doc = app.activeDocument;

        // Alle gültigen Absatzformate (ohne Stammformat [Kein Absatzformat]) auflisten
        var validStyles = [];
        var styleNames = [];
        for (var p = 0; p < doc.allParagraphStyles.length; p++) {
            var st = doc.allParagraphStyles[p];
            if (!isNoParagraphStyle(st)) {
                validStyles.push(st);
                styleNames.push(st.name);
            }
        }

        if (validStyles.length === 0) {
            alert("Keine gültigen Absatzformate im Dokument vorhanden.");
            return;
        }

        // Vorauswahl aus Textauswahl ermitteln (falls vorhanden)
        var defaultIndex = 0;
        if (app.selection && app.selection.length > 0 && app.selection[0].appliedParagraphStyle) {
            var selName = app.selection[0].appliedParagraphStyle.name;
            for (var idx = 0; idx < styleNames.length; idx++) {
                if (styleNames[idx] === selName) {
                    defaultIndex = idx;
                    break;
                }
            }
        }

        // Dialog zur Auswahl des Absatzformats anzeigen
        var win = new Window("dialog", "Absatzformat für GREP-Regeln auswählen");
        win.alignChildren = ["fill", "top"];

        var panel = win.add("panel", undefined, "Wählen Sie das Ziel-Absatzformat aus:");
        panel.alignChildren = ["fill", "top"];
        var dropdown = panel.add("dropdownlist", undefined, styleNames);
        dropdown.selection = defaultIndex;

        var btnGroup = win.add("group");
        btnGroup.alignment = ["right", "center"];
        btnGroup.add("button", undefined, "Abbrechen", { name: "cancel" });
        btnGroup.add("button", undefined, "GREP-Formate anwenden", { name: "ok" });

        if (win.show() !== 1) {
            return; // Abgebrochen
        }

        var targetStyle = validStyles[dropdown.selection.index];

        // Typografische GREP-Regeln auf Deutsch
        var rules = [
            {
                name: "Kein Umbruch",
                props: { noBreak: true },
                grep: "\\s(?=\\S+$)" // Schusterjunge/Hurenkind (letztes Wort vor Zeilenumbruch schützen)
            },
            {
                name: "Kein Umbruch",
                props: { noBreak: true },
                grep: "\\d+\\s?[xX×]\\s?\\d+" // Multiplikation / Mal-Zeichen (z.B. 2x3, 2 x 3, 10 × 15) vor Umbruch schützen
            },
            {
                name: "Klammern Optik",
                props: { baselineShift: 0.5, tracking: 10 },
                grep: "[\\[\\](){}]" // Optischer Klammer-Ausgleich
            },
            {
                name: "Brüche",
                props: { otfFraction: true },
                grep: "\\d+/\\d+" // Automatische OpenType-Brüche
            },
            {
                name: "Tiefstellung",
                props: { position: Position.SUBSCRIPT },
                grep: "(?i)\\b(H|CO|O|N|CH|NH|SO|NO|PO|Fe|Ca|Na|Cl|K|Mg)\\K\\d+" // Präzise chemische Tiefstellung (z. B. H2O, CO2, O2, N2, CH4, NH3, SO2, NO2, Fe2O3)
            },
            {
                name: "Hochstellung",
                props: { position: Position.SUPERSCRIPT },
                grep: "(?<=\\d)(st|nd|rd|th|ste|er|re)" // Ordinalien
            }
        ];

        var appliedCount = 0;
        for (var i = 0; i < rules.length; i++) {
            var r = rules[i];

            // 1. Zeichenformat abrufen oder erstellen
            var charStyle = doc.characterStyles.itemByName(r.name);
            if (!charStyle.isValid) {
                charStyle = doc.characterStyles.add({ name: r.name });
            }
            charStyle.properties = r.props;

            // 2. GREP-Stil hinzufügen, falls noch nicht vorhanden
            if (!hasGrepStyle(targetStyle, r.grep, charStyle)) {
                targetStyle.nestedGrepStyles.add({
                    grepExpression: r.grep,
                    appliedCharacterStyle: charStyle
                });
                appliedCount++;
            }
        }

        alert(appliedCount + " GREP-Regel(n) erfolgreich dem Absatzformat '" + targetStyle.name + "' zugewiesen.");
    }

    function hasGrepStyle(paraStyle, grepExpr, charStyle) {
        var grepStyles = paraStyle.nestedGrepStyles;
        for (var k = 0; k < grepStyles.length; k++) {
            var g = grepStyles[k];
            if (g.grepExpression === grepExpr) {
                var applied = g.appliedCharacterStyle;
                if (applied && (applied === charStyle || applied.name === charStyle.name)) {
                    return true;
                }
            }
        }
        return false;
    }
})();
