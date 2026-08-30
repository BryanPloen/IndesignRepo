/**
 * ExtendScript: Document Creation & Page Setup
 * Adobe InDesign 2026 (v21.0)
 */

#target indesign

(function () {
    app.doScript(
        main,
        ScriptLanguage.JAVASCRIPT,
        [],
        UndoModes.ENTIRE_SCRIPT,
        "Create New Document"
    );

    function main() {
        // Create a new document preset configuration
        var doc = app.documents.add();

        // Configure Page Setup & Document Preferences
        with (doc.documentPreferences) {
            pageWidth = "210mm";
            pageHeight = "297mm";
            facingPages = true;
            pageOrientation = PageOrientation.PORTRAIT;
            pagesPerDocument = 4;
        }

        // Set Ruler & Measurement Units
        with (doc.viewPreferences) {
            horizontalMeasurementUnits = MeasurementUnits.MILLIMETERS;
            verticalMeasurementUnits = MeasurementUnits.MILLIMETERS;
            rulerOrigin = RulerOrigin.PAGE_ORIGIN;
        }

        // Configure Margins & Columns on Master Page
        var masterPage = doc.masterSpreads.item(0).pages.item(0);
        with (masterPage.marginPreferences) {
            top = 20;
            bottom = 20;
            left = 15;
            right = 15;
            columnCount = 2;
            columnGutter = 5;
        }

        // Create a Color Swatch
        var brandColor = doc.colors.itemByName("Brand Blue");
        if (!brandColor.isValid) {
            brandColor = doc.colors.add({
                name: "Brand Blue",
                model: ColorModel.PROCESS,
                space: ColorSpace.CMYK,
                colorValue: [100, 80, 0, 0]
            });
        }

        alert("New A4 facing-page document created with 'Brand Blue' swatch.");
    }
})();
