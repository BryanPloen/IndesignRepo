/**
 * ExtendScript: Table Creation & Formatting
 * Adobe InDesign 2026 (v21.0)
 */

#target indesign

(function () {
    if (app.documents.length === 0) {
        alert("Please open a document before creating a table.");
        return;
    }

    app.doScript(
        main,
        ScriptLanguage.JAVASCRIPT,
        [],
        UndoModes.ENTIRE_SCRIPT,
        "Create & Format Table"
    );

    function main() {
        var doc = app.activeDocument;
        var page = doc.layoutWindows[0].activePage;

        // Create Text Frame for the table
        var tf = page.textFrames.add({
            geometricBounds: [20, 20, 150, 190]
        });

        // Add Table (4 rows, 3 columns)
        var table = tf.tables.add({
            bodyRowCount: 3,
            headerRowCount: 1,
            columnCount: 3
        });

        // Set Headers
        table.rows.item(0).cells.item(0).contents = "Item";
        table.rows.item(0).cells.item(1).contents = "Quantity";
        table.rows.item(0).cells.item(2).contents = "Price";

        // Format Header Row
        var headerRow = table.rows.item(0);
        headerRow.fillColor = doc.swatches.itemByName("Black");
        for (var i = 0; i < headerRow.cells.length; i++) {
            headerRow.cells.item(i).paragraphs.item(0).fillColor = doc.swatches.itemByName("Paper");
            headerRow.cells.item(i).paragraphs.item(0).justification = Justification.CENTER_ALIGN;
        }

        // Add Sample Data
        var sampleData = [
            ["InDesign License", "10", "$350.00"],
            ["Photoshop License", "5", "$175.00"],
            ["Illustrator License", "8", "$280.00"]
        ];

        for (var r = 0; r < sampleData.length; r++) {
            var rowObj = table.rows.item(r + 1);
            for (var c = 0; c < 3; c++) {
                rowObj.cells.item(c).contents = sampleData[r][c];
            }
        }

        alert("Table created and formatted successfully.");
    }
})();
