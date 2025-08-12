using Toybox.System as Sys;
using Toybox.WatchUi as Ui;

// Main application entry
class WellBeingApp extends Ui.AppBase {
    function initialize() { 
        AppBase.initialize(); 
        // Phase 3: Initialize logger on app start
        Logger.initialize();
        Logger.add(Logger.INFO, "WellBeing app initialized");
    }
    function onStart(state) { 
        Logger.add(Logger.INFO, "App started");
    }
    function onStop(state) { 
        Logger.add(Logger.INFO, "App stopped");
    }
    function getInitialView() { return [ new MainView() ]; }
}

// Primary view (Phase 1 minimal UI)
class MainView extends Ui.View {
    var score = null; // integer 0-100
    var steps = null;
    var restingHR = null;
    var sleepHrs = null;
    var stressVal = null;
    var hrvValue = null; // Phase 3: HRV metric
    var recommendation = null;
    var lastCompute = 0; // epoch seconds
    var lastScorePersisted = null; // previous day score
    var delta = null; // current score - previous

    function onShow() {
        Logger.add(Logger.INFO, "MainView shown");
        
        // Phase 3: Check for auto-refresh opportunities
        if (Scheduler.shouldAutoRefresh()) {
            Logger.add(Logger.INFO, "Triggering auto-refresh");
            computeIfAllowed(true, true); // Force auto-refresh
        } else if (Scheduler.shouldRefreshMissedWindow()) {
            Logger.add(Logger.INFO, "Triggering missed window refresh");
            computeIfAllowed(true, true); // Force missed window refresh
        } else {
            // Normal startup - allow manual refresh
            computeIfAllowed(true, false);
        }
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
    var hrvText = "HRV: " + ((ScoreEngine.ENABLE_HRV && hrvValue != null) ? hrvValue.toString() + "ms" : "--");
    
    dc.drawText(w/2, h/2 - 40, Ui.FONT_SMALL, stepsText, Ui.TEXT_JUSTIFY_CENTER);
    dc.drawText(w/2, h/2 - 20, Ui.FONT_SMALL, hrText, Ui.TEXT_JUSTIFY_CENTER);
    dc.drawText(w/2, h/2, Ui.FONT_SMALL, sleepText, Ui.TEXT_JUSTIFY_CENTER);
    dc.drawText(w/2, h/2 + 20, Ui.FONT_SMALL, stressText, Ui.TEXT_JUSTIFY_CENTER);
    dc.drawText(w/2, h/2 + 40, Ui.FONT_SMALL, hrvText, Ui.TEXT_JUSTIFY_CENTER);
        
        // Recommendation (bottom)
        var recText = (recommendation == null) ? "Data unavailable" : recommendation;
        dc.drawText(w/2, 3*h/4, Ui.FONT_MEDIUM, recText, Ui.TEXT_JUSTIFY_CENTER);
    }

    function onKey(evt) {
        if (evt.getType() == Ui.KEY_PRESS && evt.getKey() == Ui.KEY_START) {
            Logger.add(Logger.INFO, "Manual refresh triggered by user");
            computeIfAllowed(false, false); // Manual refresh
            return true;
        }
        return false;
    }

    function computeIfAllowed(force, isAutoRefresh) {
        var startTime = Sys.getTimer(); // Phase 3: Performance timing
        var now = startTime;
        
        if (!force && (now - lastCompute) <= 300000) { // 5 min throttle
            Logger.add(Logger.INFO, "Refresh throttled (< 5 min since last)");
            return;
        }
        
        Logger.add(Logger.INFO, "Starting score computation" + (isAutoRefresh ? " (auto)" : " (manual)"));
        
        // Phase 3: Enhanced error handling - fetch metrics with individual try-catch
        var metricsAvailable = [];
        
        try {
            steps = MetricProvider.getSteps();
            if (steps != null) { metricsAvailable.add("steps"); }
        } catch(e) {
            Logger.add(Logger.ERROR, "Steps fetch failed: " + e.getErrorMessage());
            steps = null;
        }
        
        try {
            restingHR = MetricProvider.getRestingHeartRate();
            if (restingHR != null) { metricsAvailable.add("resting_hr"); }
        } catch(e) {
            Logger.add(Logger.ERROR, "RestingHR fetch failed: " + e.getErrorMessage());
            restingHR = null;
        }
        
        try {
            sleepHrs = MetricProvider.getSleepHours();
            if (ScoreEngine.ENABLE_SLEEP && sleepHrs != null) { metricsAvailable.add("sleep"); }
        } catch(e) {
            Logger.add(Logger.ERROR, "Sleep fetch failed: " + e.getErrorMessage());
            sleepHrs = null;
        }
        
        try {
            stressVal = MetricProvider.getStressLevel();
            if (ScoreEngine.ENABLE_STRESS && stressVal != null) { metricsAvailable.add("stress"); }
        } catch(e) {
            Logger.add(Logger.ERROR, "Stress fetch failed: " + e.getErrorMessage());
            stressVal = null;
        }
        
        try {
            hrvValue = MetricProvider.getHRV();
            if (ScoreEngine.ENABLE_HRV && hrvValue != null) { metricsAvailable.add("hrv"); }
        } catch(e) {
            Logger.add(Logger.ERROR, "HRV fetch failed: " + e.getErrorMessage());
            hrvValue = null;
        }

        // Compute using dynamic engine (Phase 2+3). Feature flags ensure backward compatibility.
        if (MetricProvider.hasMinimumMetrics()) {
            try {
                var dyn = ScoreEngine.computeScore(steps, restingHR, sleepHrs, stressVal, hrvValue);
                // Fallback to phase1 if dynamic path fails (should not normally)
                score = (dyn != null) ? dyn : ScoreEngine.computePhase1(steps, restingHR);
                recommendation = RecommendationMapper.getRecommendation(score);
                
                Logger.add(Logger.INFO, "Score computed: " + score + " with metrics: " + metricsAvailable.toString());
                
                _handlePersistence(isAutoRefresh);
            } catch(e) {
                Logger.add(Logger.ERROR, "Score computation failed: " + e.getErrorMessage());
                score = null;
                recommendation = "Computation error";
            }
        } else {
            Logger.add(Logger.WARN, "Insufficient metrics for score computation");
            score = null;
            recommendation = "Data unavailable";
        }
        
        lastCompute = now;
        
        // Phase 3: Performance measurement
        var elapsedMs = Sys.getTimer() - startTime;
        Logger.add(Logger.INFO, "Score computation completed in " + elapsedMs + "ms");
        
        if (elapsedMs > 50) {
            Logger.add(Logger.WARN, "Performance threshold exceeded: " + elapsedMs + "ms > 50ms");
        }
        
        Ui.requestUpdate();
    }
}

// Persistence helpers (Phase 2 minimal) stored at app level
function _handlePersistence(isAutoRefresh) {
    try {
        var today = Scheduler.getCurrentDateString();
        var props = Sys.getApp().getProperty("lastScoreDate");
        var prevScore = Sys.getApp().getProperty("lastScore");
        if (props != null && prevScore != null && props != today) {
            // Previous day found
            lastScorePersisted = prevScore;
        }
        // Compute delta if we have previous day
        if (lastScorePersisted != null && score != null) {
            delta = score - lastScorePersisted;
        } else {
            delta = null;
        }
        // Store today
        Sys.getApp().setProperty("lastScore", score);
        Sys.getApp().setProperty("lastScoreDate", today);
        
        // Phase 3: Mark refresh completion and set run mode
        if (isAutoRefresh) {
            Scheduler.markAutoRefreshCompleted();
        } else {
            Scheduler.markManualRefreshCompleted();
        }
        
        Logger.add(Logger.INFO, "Persistence updated for " + today + " (mode: " + (isAutoRefresh ? "auto" : "manual") + ")");
        
    } catch(e) {
        Logger.add(Logger.ERROR, "Persist error: " + e.getErrorMessage());
    }
}
