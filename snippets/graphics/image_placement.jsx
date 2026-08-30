/**
 * ExtendScript: Placing & Fitting Graphics
 * Adobe InDesign 2026 (v21.0)
 */

#target indesign

(function () {
    if (app.documents.length === 0) {
        alert("Please open a document before placing graphics.");
        return;
    }

    // Prompt user to select an image file
    var imageFile = File.openDialog("Select an image to place:", "Image Files:*.png;*.jpg;*.jpeg;*.tif;*.pdf;*.ai;*.eps");
    if (!imageFile) {
        return; // User cancelled
    }

    app.doScript(
        main,
        ScriptLanguage.JAVASCRIPT,
        [],
        UndoModes.ENTIRE_SCRIPT,
        "Place Graphic"
    );

    function main() {
        var doc = app.activeDocument;
        var page = doc.layoutWindows[0].activePage;

        // Create Rectangle Frame
        var rect = page.rectangles.add({
            geometricBounds: [30, 30, 130, 180]
        });

        // Place File
        rect.place(imageFile);

        // Apply Frame Fitting Options
        rect.fit(FitOptions.FILL_PROPORTIONALLY);
        rect.fit(FitOptions.CENTER_CONTENT);

        alert("Graphic placed and centered proportionally: " + imageFile.name);
    }
})();
