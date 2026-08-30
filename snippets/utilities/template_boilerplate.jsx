/**
 * ExtendScript Boilerplate Template for Adobe InDesign 2026
 * Standard ES3 structure with undo grouping, unit preservation, and error handling.
 */

#target indesign

(function () {
    // 1. Ensure a document is open
    if (app.documents.length === 0) {
        alert("Please open an InDesign document before running this script.");
        return;
    }

    // 2. Wrap execution in app.doScript for a single Undo step
    app.doScript(
        main,
        ScriptLanguage.JAVASCRIPT,
        [],
        UndoModes.ENTIRE_SCRIPT,
        "Execute Script Operation"
    );

    function main() {
        var doc = app.activeDocument;

        // Save original measurement units
        var oldHoriz = doc.viewPreferences.horizontalMeasurementUnits;
        var oldVert = doc.viewPreferences.verticalMeasurementUnits;

        try {
            // Set units to Points for consistent mathematical calculations
            doc.viewPreferences.horizontalMeasurementUnits = MeasurementUnits.POINTS;
            doc.viewPreferences.verticalMeasurementUnits = MeasurementUnits.POINTS;

            // --- YOUR SCRIPT LOGIC HERE ---
            alert("Script executed successfully on document: " + doc.name);

        } catch (e) {
            alert("An error occurred during script execution:\n" + e.message + " (Line " + e.line + ")");
        } finally {
            // Always restore original measurement units
            doc.viewPreferences.horizontalMeasurementUnits = oldHoriz;
            doc.viewPreferences.verticalMeasurementUnits = oldVert;
        }
    }
})();
