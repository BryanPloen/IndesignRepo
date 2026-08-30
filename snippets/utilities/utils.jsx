/**
 * ExtendScript Utility Library for Adobe InDesign 2026 (v21.0)
 *
 * Production-grade helper functions for math, color creation, text frames,
 * paragraph styling, and layout geometry.
 *
 * Usage in scripts:
 *   #include "../snippets/utilities/utils.jsx"
 *   or:
 *   Utils.Math.map(val, 0, 100, 0, 500);
 */

#target indesign

var Utils = (function () {

    // ==========================================
    // 1. MATHEMATICAL & RANDOM UTILITIES
    // ==========================================

    function norm(value, min, max) {
        if (max === min) return 0;
        return (value - min) / (max - min);
    }

    function lerp(normVal, min, max) {
        return (max - min) * normVal + min;
    }

    function map(value, sourceMin, sourceMax, destMin, destMax, clampResult) {
        var n = norm(value, sourceMin, sourceMax);
        var res = lerp(n, destMin, destMax);
        if (clampResult) {
            return clamp(res, Math.min(destMin, destMax), Math.max(destMin, destMax));
        }
        return res;
    }

    function clamp(value, min, max) {
        var lower = Math.min(min, max);
        var upper = Math.max(min, max);
        return Math.min(Math.max(value, lower), upper);
    }

    function getRandomArbitrary(min, max) {
        var lower = Math.min(min, max);
        var upper = Math.max(min, max);
        return Math.random() * (upper - lower) + lower;
    }

    function getRandomInt(min, max) {
        var lower = Math.ceil(Math.min(min, max));
        var upper = Math.floor(Math.max(min, max));
        return Math.floor(Math.random() * (upper - lower + 1)) + lower;
    }

    function rndFromArray(arr) {
        if (!arr || arr.length === 0) {
            return null;
        }
        var index = Math.floor(Math.random() * arr.length);
        return arr[index];
    }

    function shuffleArray(arr) {
        if (!arr || !arr.length) return arr;
        for (var i = arr.length - 1; i > 0; i--) {
            var j = Math.floor(Math.random() * (i + 1));
            var temp = arr[i];
            arr[i] = arr[j];
            arr[j] = temp;
        }
        return arr;
    }

    // ==========================================
    // 2. DOCUMENT & ENVIRONMENT GUARDS
    // ==========================================

    function getTargetDoc(doc) {
        if (doc && doc.isValid) {
            return doc;
        }
        if (app.documents.length > 0) {
            return app.activeDocument;
        }
        return null;
    }

    function getDocumentSettings(doc) {
        var targetDoc = getTargetDoc(doc);
        if (!targetDoc) return null;

        var prefs = targetDoc.documentPreferences;
        var firstPage = targetDoc.pages.length > 0 ? targetDoc.pages[0] : null;
        var margins = firstPage ? firstPage.marginPreferences : null;

        return {
            pageWidth: prefs.pageWidth,
            pageHeight: prefs.pageHeight,
            pageOrientation: prefs.pageOrientation,
            pagesPerDocument: prefs.pagesPerDocument,
            mTop: margins ? margins.top : 0,
            mBottom: margins ? margins.bottom : 0,
            mLeft: margins ? margins.left : 0,
            mRight: margins ? margins.right : 0,
            columnCount: margins ? margins.columnCount : 1,
            columnGutter: margins ? margins.columnGutter : 0
        };
    }

    // ==========================================
    // 3. COLOR CREATION UTILITIES
    // ==========================================

    function colorRGB(arg1, arg2, arg3) {
        var targetDoc, name, rgb;

        if (typeof arg1 === "number" && typeof arg2 === "number" && typeof arg3 === "number") {
            // Signature: colorRGB(r, g, b)
            targetDoc = getTargetDoc();
            name = "R=" + Math.round(arg1) + " G=" + Math.round(arg2) + " B=" + Math.round(arg3);
            rgb = [Math.round(arg1), Math.round(arg2), Math.round(arg3)];
        } else if (typeof arg1 === "string" && (arg2 instanceof Array)) {
            // Signature: colorRGB(name, [r, g, b])
            targetDoc = getTargetDoc();
            name = arg1;
            rgb = arg2;
        } else if (arg1 && arg1.colors && typeof arg2 === "string" && (arg3 instanceof Array)) {
            // Signature: colorRGB(doc, name, [r, g, b])
            targetDoc = arg1;
            name = arg2;
            rgb = arg3;
        } else {
            targetDoc = getTargetDoc();
            name = "Custom RGB";
            rgb = [0, 0, 0];
        }

        if (!targetDoc) return null;

        var color = targetDoc.colors.itemByName(name);
        if (color.isValid) {
            return color;
        }

        return targetDoc.colors.add({
            name: name,
            model: ColorModel.PROCESS,
            space: ColorSpace.RGB,
            colorValue: rgb
        });
    }

    function colorCMYK(arg1, arg2, arg3) {
        var targetDoc, name, cmyk;

        if (typeof arg1 === "string" && (arg2 instanceof Array)) {
            // Signature: colorCMYK(name, [c, m, y, k])
            targetDoc = getTargetDoc();
            name = arg1;
            cmyk = arg2;
        } else if (arg1 && arg1.colors && typeof arg2 === "string" && (arg3 instanceof Array)) {
            // Signature: colorCMYK(doc, name, [c, m, y, k])
            targetDoc = arg1;
            name = arg2;
            cmyk = arg3;
        } else {
            targetDoc = getTargetDoc();
            name = "Custom CMYK";
            cmyk = [0, 0, 0, 100];
        }

        if (!targetDoc) return null;

        var color = targetDoc.colors.itemByName(name);
        if (color.isValid) {
            return color;
        }

        return targetDoc.colors.add({
            name: name,
            model: ColorModel.PROCESS,
            space: ColorSpace.CMYK,
            colorValue: cmyk
        });
    }

    function colorHSB(arg1, arg2, arg3) {
        var targetDoc, name, hsb;

        if (typeof arg1 === "string" && (arg2 instanceof Array)) {
            // Signature: colorHSB(name, [h, s, b])
            targetDoc = getTargetDoc();
            name = arg1;
            hsb = arg2;
        } else if (arg1 && arg1.colors && typeof arg2 === "string" && (arg3 instanceof Array)) {
            // Signature: colorHSB(doc, name, [h, s, b])
            targetDoc = arg1;
            name = arg2;
            hsb = arg3;
        } else {
            targetDoc = getTargetDoc();
            name = "Custom HSB";
            hsb = [0, 0, 0];
        }

        if (!targetDoc) return null;

        var color = targetDoc.colors.itemByName(name);
        if (color.isValid) {
            return color;
        }

        return targetDoc.colors.add({
            name: name,
            model: ColorModel.PROCESS,
            space: ColorSpace.HSB,
            colorValue: hsb
        });
    }

    // ==========================================
    // 4. GRAPHICS & TEXT CREATION UTILITIES
    // ==========================================

    function addRectangle(page, bounds, colorSpec) {
        if (!page || !page.isValid) return null;

        var doc = page.parent ? page.parent : getTargetDoc();
        var fillColorVal = "None";

        if (colorSpec) {
            if (typeof colorSpec === "string") {
                if (doc) {
                    var sw = doc.swatches.itemByName(colorSpec);
                    if (sw.isValid) {
                        fillColorVal = sw;
                    } else {
                        var col = doc.colors.itemByName(colorSpec);
                        if (col.isValid) fillColorVal = col;
                    }
                }
            } else if (colorSpec.isValid) {
                fillColorVal = colorSpec;
            }
        }

        return page.rectangles.add({
            geometricBounds: bounds,
            fillColor: fillColorVal,
            strokeWeight: 0
        });
    }

    function addTextFrame(page, bounds, pointSize, content, fontSpec) {
        if (!page || !page.isValid) return null;

        var frame = page.textFrames.add({
            geometricBounds: bounds
        });

        if (content !== undefined && content !== null) {
            frame.contents = String(content);
        }

        if (pointSize) {
            try { frame.paragraphs[0].pointSize = pointSize; } catch (ePS) {}
        }

        if (fontSpec) {
            var fontObj = null;
            if (typeof fontSpec === "string") {
                fontObj = app.fonts.itemByName(fontSpec);
            } else if (fontSpec.isValid) {
                fontObj = fontSpec;
            }

            if (fontObj && fontObj.isValid) {
                try { frame.paragraphs[0].appliedFont = fontObj; } catch (eF) {}
            }
        }

        return frame;
    }

    function addParagraphStyle(arg1, arg2, arg3, arg4, arg5) {
        var targetDoc, name, point, leadingRatio, fontSpec;

        if (typeof arg1 === "string") {
            // Signature: addParagraphStyle(name, point, leadingRatio, fontSpec)
            targetDoc = getTargetDoc();
            name = arg1;
            point = arg2 || 10;
            leadingRatio = arg3 || 1.2;
            fontSpec = arg4;
        } else if (arg1 && arg1.paragraphStyles) {
            // Signature: addParagraphStyle(doc, name, point, leadingRatio, fontSpec)
            targetDoc = arg1;
            name = arg2;
            point = arg3 || 10;
            leadingRatio = arg4 || 1.2;
            fontSpec = arg5;
        } else {
            targetDoc = getTargetDoc();
            name = "Custom Style";
            point = 10;
            leadingRatio = 1.2;
        }

        if (!targetDoc) return null;

        var pStyle = targetDoc.paragraphStyles.itemByName(name);
        if (pStyle.isValid) {
            return pStyle;
        }

        var styleProps = {
            name: name,
            pointSize: point,
            leading: point * leadingRatio
        };

        if (fontSpec) {
            var fontObj = null;
            if (typeof fontSpec === "string") {
                fontObj = app.fonts.itemByName(fontSpec);
            } else if (fontSpec.isValid) {
                fontObj = fontSpec;
            }
            if (fontObj && fontObj.isValid) {
                styleProps.appliedFont = fontObj;
            }
        }

        return targetDoc.paragraphStyles.add(styleProps);
    }

    function removeParagraphStyles(doc) {
        var targetDoc = getTargetDoc(doc);
        if (!targetDoc) return;

        var styles = targetDoc.paragraphStyles;
        for (var i = styles.length - 1; i >= 0; i--) {
            var sName = styles[i].name;
            // Never remove default system paragraph styles
            if (sName !== "[No Paragraph Style]" && sName !== "[Basic Paragraph]") {
                try {
                    styles[i].remove();
                } catch (e) {}
            }
        }
    }

    // Export Public API Namespace
    return {
        Math: {
            norm: norm,
            lerp: lerp,
            map: map,
            clamp: clamp,
            randomInt: getRandomInt,
            randomArbitrary: getRandomArbitrary,
            randomChoice: rndFromArray,
            shuffle: shuffleArray
        },
        Color: {
            rgb: colorRGB,
            cmyk: colorCMYK,
            hsb: colorHSB
        },
        Text: {
            addFrame: addTextFrame,
            getOrCreateStyle: addParagraphStyle,
            removeAllCustomStyles: removeParagraphStyles
        },
        Graphics: {
            addRectangle: addRectangle
        },
        Doc: {
            getSettings: getDocumentSettings,
            getTargetDoc: getTargetDoc
        },
        // Top-level aliases for direct access
        norm: norm,
        lerp: lerp,
        map: map,
        clamp: clamp,
        getRandomArbitrary: getRandomArbitrary,
        getRandomInt: getRandomInt,
        rndFromArray: rndFromArray,
        shuffleArray: shuffleArray,
        colorRGB: colorRGB,
        colorCMYK: colorCMYK,
        colorHSB: colorHSB,
        addTextFrame: addTextFrame,
        addRectangle: addRectangle,
        addParagraphStyle: addParagraphStyle,
        getDocumentSettings: getDocumentSettings,
        removeParagraphStyles: removeParagraphStyles
    };

})();

// Global alias exposure for legacy scripts included via #include
var norm = Utils.norm;
var lerp = Utils.lerp;
var map = Utils.map;
var clamp = Utils.clamp;
var getRandomArbitrary = Utils.getRandomArbitrary;
var getRandomInt = Utils.getRandomInt;
var rndFromArray = Utils.rndFromArray;
var shuffleArray = Utils.shuffleArray;
var colorRGB = Utils.colorRGB;
var colorCMYK = Utils.colorCMYK;
var colorHSB = Utils.colorHSB;
var addTextFrame = Utils.addTextFrame;
var addRectangle = Utils.addRectangle;
var addParagraphStyle = Utils.addParagraphStyle;
var getDocumentSettings = Utils.getDocumentSettings;
var removeParagraphStyles = Utils.removeParagraphStyles;
