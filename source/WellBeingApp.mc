using Toybox.System as Sys;
using Toybox.WatchUi as Ui;

// Main application entry
class WellBeingApp extends Ui.AppBase {
    function initialize() { AppBase.initialize(); }
    function onStart(state) { }
    function onStop(state) { }
    function getInitialView() { return [ new MainView() ]; }
}

// Primary view (Phase 1 minimal UI)
class MainView extends Ui.View {
    var score = null; // integer 0-100
    var lastCompute = 0; // epoch seconds

    function onShow() {
        computeIfAllowed(true);
    }

    function onUpdate(dc) {
        var w = dc.getWidth();
        var h = dc.getHeight();
        dc.clear();
        dc.setColor(Ui.COLOR_WHITE, Ui.COLOR_BLACK);
        var text = (score == null) ? "--" : score.toString();
        dc.drawText(w/2, h/2, Ui.FONT_XLARGE, text, Ui.TEXT_JUSTIFY_CENTER);
    }

    function onKey(evt) {
        if (evt.getType() == Ui.KEY_PRESS && evt.getKey() == Ui.KEY_START) {
            computeIfAllowed(false);
            return true;
        }
        return false;
    }

    function computeIfAllowed(force) {
        var now = Sys.getTimer();
        if (!force && (now - lastCompute) <= 300000) { // 5 min throttle
            return;
        }
        // Phase 1: use test vector A values
        score = ScoreEngine.computePhase1(8000, 55); // steps, restingHR
        lastCompute = now;
        Ui.requestUpdate();
    }
}
