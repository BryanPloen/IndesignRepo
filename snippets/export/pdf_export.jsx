/**
 * ExtendScript: Export Document to PDF
 * Adobe InDesign 2026 (v21.0)
 */

#target indesign

(function () {
    if (app.documents.length === 0) {
        alert("Please open a document before exporting.");
        return;
    }

    var doc = app.activeDocument;
    if (!doc.saved) {
        alert("Please save your document before exporting to PDF.");
        return;
    }

    var pdfFile = new File(doc.fullName.fsName.replace(/\.indd$/i, ".pdf"));

    try {
        // Choose PDF Export Preset (e.g. "[High Quality Print]")
        var preset = app.pdfExportPresets.itemByName("[High Quality Print]");
        if (!preset.isValid) {
            preset = app.pdfExportPresets.item(0); // Fallback to first available preset
        }

        // Configure Export Options
        app.pdfExportPreferences.pageRange = PageRange.ALL_PAGES;
        app.pdfExportPreferences.viewPDF = true; // Open PDF after export

        // Export File
        doc.exportFile(ExportFormat.PDF_TYPE, pdfFile, false, preset);

        alert("PDF successfully exported to:\n" + pdfFile.fsName);

    } catch (e) {
        alert("Failed to export PDF:\n" + e.message);
    }
})();
