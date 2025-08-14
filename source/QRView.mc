using Toybox.WatchUi as Ui;

class QRView extends Ui.View {
    var packetJson;
    var qrMatrix;

    function initialize(jsonStr as String) {
        View.initialize();
        packetJson = jsonStr;
        qrMatrix = null;
        
        // Generate QR code matrix
        if (packetJson != null) {
            try {
                qrMatrix = QREncoder.encode(packetJson);
                if (qrMatrix == null) {
                    Logger.add(Logger.WARNING, "QR generation failed, falling back to JSON");
                }
            } catch (e) {
                Logger.add(Logger.ERROR, "QR encoding error: " + e.getErrorMessage());
                qrMatrix = null;
            }
        }
    }

    function onUpdate(dc) {
        var w = dc.getWidth();
        var h = dc.getHeight();
        dc.clear();
        dc.setColor(Ui.COLOR_WHITE, Ui.COLOR_BLACK);
        dc.drawText(w/2, 16, Ui.FONT_SMALL, "Send to Web (QR)", Ui.TEXT_JUSTIFY_CENTER);

        if (packetJson == null) {
            dc.drawText(w/2, h/2, Ui.FONT_MEDIUM, "No data", Ui.TEXT_JUSTIFY_CENTER);
            return;
        }

        // Draw QR code or show fallback
        if (qrMatrix != null) {
            drawQRCode(dc, qrMatrix, w, h);
        } else {
            // Fallback to JSON view hint if QR generation failed
            dc.drawText(w/2, h/2, Ui.FONT_SMALL, "QR failed", Ui.TEXT_JUSTIFY_CENTER);
            dc.drawText(w/2, h/2 + 20, Ui.FONT_XTINY, "Press UP for JSON", Ui.TEXT_JUSTIFY_CENTER);
        }

        // Footer hint
        dc.drawText(w/2, h-16, Ui.FONT_XTINY, "UP=JSON BACK=Exit", Ui.TEXT_JUSTIFY_CENTER);
    }
    
    function drawQRCode(dc, matrix, screenW, screenH) {
        var matrixSize = matrix.size();
        var availableSize = (screenW < screenH ? screenW : screenH) - 50;
        var cellSize = availableSize / matrixSize;
        
        // Ensure cell size is at least 1 pixel
        if (cellSize < 1) {
            cellSize = 1;
            availableSize = matrixSize;
        }
        
        var qrSize = cellSize * matrixSize;
        var left = (screenW - qrSize) / 2;
        var top = (screenH - qrSize) / 2;
        
        // Draw white background with border
        dc.setColor(Ui.COLOR_WHITE, Ui.COLOR_BLACK);
        var borderSize = 4;
        dc.fillRectangle(left - borderSize, top - borderSize, 
                         qrSize + 2 * borderSize, qrSize + 2 * borderSize);
        
        // Draw QR modules
        dc.setColor(Ui.COLOR_BLACK, Ui.COLOR_WHITE);
        for (var y = 0; y < matrixSize; y++) {
            for (var x = 0; x < matrixSize; x++) {
                if (matrix[y][x]) {
                    dc.fillRectangle(left + x * cellSize, top + y * cellSize, 
                                    cellSize, cellSize);
                }
            }
        }
    }

    function onKey(evt) {
        if (evt.getType() == Ui.KEY_PRESS) {
            var key = evt.getKey();
            if (key == Ui.KEY_UP) {
                Ui.pushView(new JsonView(packetJson), Ui.SLIDE_LEFT);
                return true;
            }
        }
        return false;
    }
}
