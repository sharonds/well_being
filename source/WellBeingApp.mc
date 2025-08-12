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
    var steps = null;
    var restingHR = null;
    var recommendation = null;
    var lastCompute = 0; // epoch seconds

    function onShow() {
        computeIfAllowed(true);
    }

    function onUpdate(dc) {
        var w = dc.getWidth();
        var h = dc.getHeight();
        dc.clear();
        dc.setColor(Ui.COLOR_WHITE, Ui.COLOR_BLACK);
        
        // Score (top, large)
        var scoreText = (score == null) ? "--" : score.toString();
        dc.drawText(w/2, h/4, Ui.FONT_XLARGE, scoreText, Ui.TEXT_JUSTIFY_CENTER);
        
        // Metrics (middle)
        var stepsText = "Steps: " + ((steps == null) ? "--" : steps.toString());
        var hrText = "RestHR: " + ((restingHR == null) ? "--" : restingHR.toString());
        dc.drawText(w/2, h/2 - 20, Ui.FONT_SMALL, stepsText, Ui.TEXT_JUSTIFY_CENTER);
        dc.drawText(w/2, h/2 + 10, Ui.FONT_SMALL, hrText, Ui.TEXT_JUSTIFY_CENTER);
        
        // Recommendation (bottom)
        var recText = (recommendation == null) ? "Data unavailable" : recommendation;
        dc.drawText(w/2, 3*h/4, Ui.FONT_MEDIUM, recText, Ui.TEXT_JUSTIFY_CENTER);
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
        
        // Fetch metrics through interface
        steps = MetricProvider.getSteps();
        restingHR = MetricProvider.getRestingHeartRate();
        
        // Compute score if we have minimum required metrics
        if (MetricProvider.hasMinimumMetrics()) {
            score = ScoreEngine.computePhase1(steps, restingHR);
            recommendation = RecommendationMapper.getRecommendation(score);
        } else {
            score = null;
            recommendation = "Data unavailable";
        }
        
        lastCompute = now;
        Ui.requestUpdate();
    }
}
