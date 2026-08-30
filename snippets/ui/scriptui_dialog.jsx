/**
 * ExtendScript: ScriptUI Modal Dialog Builder
 * Adobe InDesign 2026 (v21.0)
 */

#target indesign

(function () {
    // Build Modal Window
    var dialog = new Window("dialog", "InDesign Automation Options");
    dialog.orientation = "column";
    dialog.alignChildren = ["fill", "top"];
    dialog.spacing = 10;
    dialog.margins = 16;

    // 1. Text Input Group
    var nameGroup = dialog.add("group");
    nameGroup.add("statictext", undefined, "Project Name:");
    var nameInput = nameGroup.add("edittext", undefined, "My Catalog");
    nameInput.characters = 20;

    // 2. Dropdown Select Group
    var exportGroup = dialog.add("group");
    exportGroup.add("statictext", undefined, "Export Quality:");
    var qualityDropdown = exportGroup.add("dropdownlist", undefined, ["High Quality Print", "Press Quality", "Smallest File Size"]);
    qualityDropdown.selection = 0;

    // 3. Checkbox Option
    var optionsGroup = dialog.add("panel", undefined, "Options");
    optionsGroup.alignChildren = ["left", "top"];
    var chkIncludeBleed = optionsGroup.add("checkbox", undefined, "Include Document Bleed Settings");
    var chkOpenAfter = optionsGroup.add("checkbox", undefined, "Open PDF After Export");
    chkOpenAfter.value = true;

    // 4. Action Buttons
    var btnGroup = dialog.add("group");
    btnGroup.alignment = ["right", "bottom"];
    var btnCancel = btnGroup.add("button", undefined, "Cancel", { name: "cancel" });
    var btnOK = btnGroup.add("button", undefined, "OK", { name: "ok" });

    // Show Dialog & Handle Results
    if (dialog.show() === 1) {
        alert(
            "User Selected Options:\n" +
            "- Project Name: " + nameInput.text + "\n" +
            "- Preset: " + qualityDropdown.selection.text + "\n" +
            "- Include Bleed: " + chkIncludeBleed.value + "\n" +
            "- Open After Export: " + chkOpenAfter.value
        );
    } else {
        alert("Operation cancelled by user.");
    }
})();
