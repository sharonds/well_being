using Toybox.WatchUi as Ui;

class QRView extends Ui.View {
    var packetJson;

    function initialize(jsonStr as String) {
        View.initialize();
        packetJson = jsonStr;
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

        // Placeholder: draw a simple dense grid to aid scanning of compact payloads
        // In production, swap with a real QR encoder (module or pre-rendered image).
        var size = (w < h ? w : h) - 40;
        var cells = 41; // placeholder cell count (not real QR)
        var cell = size / cells;
        var left = (w - size) / 2;
        var top = (h - size) / 2;

        // Pseudo-encoding: toggle cells based on hash of packet
        var hash = _hash(packetJson);
        for (var y = 0; y < cells; y += 1) {
            for (var x = 0; x < cells; x += 1) {
                var bit = ((hash + (x*31 + y*17)) % 3) == 0;
                if (bit) {
                    dc.fillRectangle(left + x*cell, top + y*cell, cell, cell);
                }
            }
        }

    // Footer hint
    dc.drawText(w/2, h-16, Ui.FONT_XTINY, "UP=JSON BACK=Exit", Ui.TEXT_JUSTIFY_CENTER);
    }

    function _hash(s as String) as Number {
        var h = 0;
        for (var i = 0; i < s.length(); i += 1) {
            h = (h * 31 + s.charCodeAt(i)) % 1000003;
        }
        return h;
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
