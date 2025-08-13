using Toybox.WatchUi as Ui;

class JsonView extends Ui.View {
    var text;

    function initialize(s as String) {
        View.initialize();
        text = s;
    }

    function onUpdate(dc) {
        var w = dc.getWidth();
        var h = dc.getHeight();
        dc.clear();
        dc.setColor(Ui.COLOR_WHITE, Ui.COLOR_BLACK);
        dc.drawText(w/2, 12, Ui.FONT_XTINY, "Packet JSON (preview)", Ui.TEXT_JUSTIFY_CENTER);

        var display = (text == null) ? "(no data)" : _truncate(text, 600);
        _drawWrapped(dc, display, 10, 28, w - 20, Ui.FONT_XTINY);

        dc.drawText(w/2, h-12, Ui.FONT_XTINY, "BACK to return", Ui.TEXT_JUSTIFY_CENTER);
    }

    function _truncate(s as String, max as Number) as String {
        if (s == null) return "";
        if (s.length() <= max) return s;
        return s.substring(0, max) + "…";
    }

    function _drawWrapped(dc, s as String, x as Number, y as Number, maxW as Number, font) {
        var line = "";
        for (var i = 0; i < s.length(); i += 1) {
            var ch = s.substring(i, i+1);
            var trial = line + ch;
            var size = dc.getTextDimensions(font, trial);
            if (size[0] > maxW || ch == "\n") {
                dc.drawText(x, y, font, line, Ui.TEXT_JUSTIFY_LEFT);
                y += size[1] + 2;
                line = (ch == "\n") ? "" : ch;
            } else {
                line = trial;
            }
        }
        if (line.length() > 0) dc.drawText(x, y, font, line, Ui.TEXT_JUSTIFY_LEFT);
    }
}
