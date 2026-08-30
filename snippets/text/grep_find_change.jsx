/**
 * ExtendScript: Advanced GREP Find/Change
 * Adobe InDesign 2026 (v21.0)
 */

#target indesign

(function () {
    if (app.documents.length === 0) {
        alert("Please open a document before running GREP find/change.");
        return;
    }

    app.doScript(
        main,
        ScriptLanguage.JAVASCRIPT,
        [],
        UndoModes.ENTIRE_SCRIPT,
        "Execute GREP Find/Change"
    );

    function main() {
        var doc = app.activeDocument;

        // Clear existing GREP search preferences
        app.findGrepPreferences = NothingEnum.NOTHING;
        app.changeGrepPreferences = NothingEnum.NOTHING;

        try {
            // Example: Clean multiple consecutive spaces to a single space
            app.findGrepPreferences.findWhat = "[ ]{2,}";
            app.changeGrepPreferences.changeTo = " ";

            var spaceResults = doc.changeGrep();

            // Example: Find email addresses and apply character style
            var emailStyle = doc.characterStyles.itemByName("Email Link");
            if (!emailStyle.isValid) {
                emailStyle = doc.characterStyles.add({ name: "Email Link", underline: true });
            }

            app.findGrepPreferences = NothingEnum.NOTHING;
            app.changeGrepPreferences = NothingEnum.NOTHING;

            app.findGrepPreferences.findWhat = "(?i)[a-z0-9._%+-]+@[a-z0-9.-]+\\.[a-z]{2,}";
            app.changeGrepPreferences.appliedCharacterStyle = emailStyle;

            var emailResults = doc.changeGrep();

            alert(
                "GREP Find/Change Complete:\n" +
                "- Multiple spaces cleaned: " + spaceResults.length + "\n" +
                "- Emails styled: " + emailResults.length
            );

        } catch (e) {
            alert("Error running GREP find/change: " + e.message);
        } finally {
            // Reset preferences
            app.findGrepPreferences = NothingEnum.NOTHING;
            app.changeGrepPreferences = NothingEnum.NOTHING;
        }
    }
})();
