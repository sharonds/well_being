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
    var sleepHrs = null;
    var stressVal = null;
    var recommendation = null;
    var lastCompute = 0; // epoch seconds
    var lastScorePersisted = null; // previous day score
    var delta = null; // current score - previous
    var autoRefreshDate = null; // date string of last auto refresh
    var lastRunMode = null; // 'auto' or 'manual'

    function onShow() {
        computeIfAllowed(true, true); // treat onShow as force check but allow auto logic
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
    var sleepText = "Sleep: " + ((ScoreEngine.ENABLE_SLEEP && sleepHrs != null) ? sleepHrs.toString() + "h" : "--");
    var stressText = "Stress: " + ((ScoreEngine.ENABLE_STRESS && stressVal != null) ? stressVal.toString() : "--");
    dc.drawText(w/2, h/2 - 30, Ui.FONT_SMALL, stepsText, Ui.TEXT_JUSTIFY_CENTER);
    dc.drawText(w/2, h/2 - 10, Ui.FONT_SMALL, hrText, Ui.TEXT_JUSTIFY_CENTER);
    dc.drawText(w/2, h/2 + 10, Ui.FONT_SMALL, sleepText, Ui.TEXT_JUSTIFY_CENTER);
    dc.drawText(w/2, h/2 + 30, Ui.FONT_SMALL, stressText, Ui.TEXT_JUSTIFY_CENTER);
        
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

    function computeIfAllowed(force, isShow) {
        var now = Sys.getTimer();
        if (!force && (now - lastCompute) <= 300000) { return; }

        // Phase 3 auto-refresh scheduling logic (simplified due to limited time APIs)
        var today = _currentDateStr();
        var hour = _currentHourStub(); // returns fixed 7 for now (inside window)
        var propsAuto = Sys.getApp().getProperty("autoRefreshDate");
        var manualRunToday = (Sys.getApp().getProperty("lastRunMode") == "manual" && Sys.getApp().getProperty("lastScoreDate") == today);
        var shouldAuto = false;
        if (isShow) {
            // Decide if we should auto-run; reuse Scheduler functions for testability
            shouldAuto = Scheduler.shouldAuto(today, hour, Sys.getApp().getProperty("lastScoreDate"), propsAuto, manualRunToday, lastCompute, now);
            if (!shouldAuto) {
                var late = Scheduler.shouldLateCompute(today, hour, Sys.getApp().getProperty("lastScoreDate"), manualRunToday);
                if (late) { shouldAuto = true; }
            }
        }
        
        // Fetch metrics through interface
        steps = MetricProvider.getSteps();
        restingHR = MetricProvider.getRestingHeartRate();
        sleepHrs = MetricProvider.getSleepHours();
        stressVal = MetricProvider.getStressLevel();
        var hrv = MetricProvider.getHRV();

        // Compute using dynamic engine (Phase 2). Feature flags ensure backward compatibility.
        if (MetricProvider.hasMinimumMetrics()) {
            var dyn = ScoreEngine.computeScoreV3(steps, restingHR, sleepHrs, stressVal, hrv);
            // Fallback to phase1 if dynamic path fails (should not normally)
            score = (dyn != null) ? dyn : ScoreEngine.computePhase1(steps, restingHR);
            recommendation = RecommendationMapper.getRecommendation(score);
            _handlePersistence(shouldAuto ? "auto" : (force ? "manual" : "manual"));
        } else {
            score = null;
            recommendation = "Data unavailable";
        }
        
        lastCompute = now;
        Ui.requestUpdate();
    }
}

// Persistence helpers (Phase 2 minimal) stored at app level
function _handlePersistence() { _handlePersistence("manual"); }

function _handlePersistence(runMode) {
    try {
        var today = _currentDateStr();
        var props = Sys.getApp().getProperty("lastScoreDate");
        var prevScore = Sys.getApp().getProperty("lastScore");
        if (props != null && prevScore != null && props != today) {
            // Previous day found
            lastScorePersisted = prevScore;
        }
        // Compute delta if we have previous day
        if (lastScorePersisted != null && score != null) { delta = score - lastScorePersisted; } else { delta = null; }
        // Store today
        Sys.getApp().setProperty("lastScore", score);
        Sys.getApp().setProperty("lastScoreDate", today);
        Sys.getApp().setProperty("lastRunMode", runMode);
        if (runMode == "auto") { Sys.getApp().setProperty("autoRefreshDate", today); }
    } catch(e) {
        Sys.println("Persist error: " + e.getErrorMessage());
        Logger.add("ERROR", "Persist fail");
    }
}

function _currentDateStr() {
    // Placeholder: Without full date API context, return fixed stub or derive from system if available.
    // TODO Phase 2 refine with actual date retrieval.
    return "20250812"; // stub date; replace with real date formatting logic.
}

// Phase 3 stub hour function (returns 7 to simulate morning window); replace with real clock hour retrieval.
function _currentHourStub() { return 7; }
