using Toybox.System as Sys;
using Toybox.WatchUi as Ui;

// Main application entry
class WellBeingApp extends Ui.AppBase {
    function initialize() { AppBase.initialize(); }
    function onStart(state) { }
    function onStop(state) { }
    function getInitialView() { return [ new MainView() ]; }
}

// Primary view with enhanced UI (AC5)
class MainView extends Ui.View {
    var score = null; // integer 0-100
    var steps = null;
    var restingHR = null;
    var sleepHrs = null;
    var stressVal = null;
    var recommendation = null;
    var lastCompute = 0; // epoch seconds
    var scoreHistory = null; // ScoreHistory instance for 7-day tracking
    var delta = null; // current score - previous
    var previousScore = null; // yesterday's score for display
    var lastRunMode = "manual"; // 'auto' or 'manual' for indicator
    var lastPacket = null; // cached JSON string for QR

    function initialize() {
        View.initialize();
        scoreHistory = new ScoreHistory();
    }

    function onShow() {
        computeIfAllowed(true, true); // treat onShow as force check but allow auto logic
    }

    function onUpdate(dc) {
        var w = dc.getWidth();
        var h = dc.getHeight();
        dc.clear();
        dc.setColor(Ui.COLOR_WHITE, Ui.COLOR_BLACK);
        
        // Score with delta (top, large)
        var scoreText = (score == null) ? "--" : score.toString();
        dc.drawText(w/2, h/4 - 15, Ui.FONT_XLARGE, scoreText, Ui.TEXT_JUSTIFY_CENTER);
        
        // Delta and previous score (below main score)
        if (delta != null && previousScore != null) {
            var deltaText = (delta >= 0 ? "+" : "") + delta.toString();
            var prevText = "(Yesterday: " + previousScore.toString() + ")";
            dc.drawText(w/2, h/4 + 10, Ui.FONT_SMALL, deltaText + " " + prevText, Ui.TEXT_JUSTIFY_CENTER);
        }
        
        // Auto/Manual indicator (top right)
        var modeText = (lastRunMode.equals("auto")) ? "A" : "M";
        dc.drawText(w - 15, 15, Ui.FONT_SMALL, modeText, Ui.TEXT_JUSTIFY_CENTER);
        
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
        if (evt.getType() == Ui.KEY_PRESS) {
            var key = evt.getKey();
            if (key == Ui.KEY_START) {
                computeIfAllowed(false);
                return true;
            }
            // Quick toggle: UP shows QR if packet cached
            if (key == Ui.KEY_UP) {
                showQrIfAvailable();
                return true;
            }
        }
        return false;
    }

    function computeIfAllowed(force, isShow) {
        var now = Sys.getTimer();
        if (!force && (now - lastCompute) <= 300000) { return; }

        // Phase 3 auto-refresh scheduling logic (simplified due to limited time APIs)
        var today = Clock.today();
        var hour = Clock.hour();
        var propsAuto = Sys.getApp().getProperty("autoRefreshDate");
        var manualRunToday = (Sys.getApp().getProperty("lastRunMode") == "manual" && Sys.getApp().getProperty("lastScoreDate") == today);
        var shouldAuto = false;
        var isLateCompute = false;
        
        if (isShow) {
            // Check if we should auto-refresh (7-11am window)
            shouldAuto = Scheduler.shouldAuto(today, hour, Sys.getApp().getProperty("lastScoreDate"), propsAuto, manualRunToday, lastCompute, now);
            
            // Check if we should do late compute (after 11am, no score today)
            if (!shouldAuto) {
                isLateCompute = Scheduler.shouldLateCompute(today, hour, Sys.getApp().getProperty("lastScoreDate"), manualRunToday);
                shouldAuto = isLateCompute; // Both count as auto-triggered
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
            // Determine run mode based on how computation was triggered
            var runMode;
            if (shouldAuto && !force) {
                runMode = "auto";
                Logger.add("INFO", "Auto-refresh triggered: " + (isLateCompute ? "late compute" : "morning window") + " at hour " + hour);
            } else {
                runMode = "manual";
                if (force) {
                    Logger.add("INFO", "Manual refresh triggered");
                }
            }
            
            lastRunMode = runMode;
            handlePersistence(runMode);
        } else {
            score = null;
            recommendation = "Data unavailable";
        }
        
        lastCompute = now;
    buildPacketIfPossible();
        Ui.requestUpdate();
    }
    
    function handlePersistence(runMode) {
        try {
            var today = Clock.today();
            
            // Get previous score for delta calculation
            previousScore = scoreHistory.getLastScore();
            delta = scoreHistory.getDelta(score);
            
            // Add current score to history
            if (score != null) {
                scoreHistory.addScore(score, today);
            }
            
            // Store run mode and auto-refresh date
            Sys.getApp().setProperty("lastRunMode", runMode);
            if (runMode == "auto") { 
                Sys.getApp().setProperty("autoRefreshDate", today); 
            }
        } catch(e) {
            Logger.add("ERROR", ErrorCodes.PERSIST + ": " + e.getErrorMessage());
        }
    }

    function buildPacketIfPossible() {
        try {
            if (score == null) { return; }
            var today = Clock.today();
            var band = recommendation; // map already computed
            var pkt = InsightPacket.buildPlanPacket(today, score, band, delta);
            if (pkt != null) { lastPacket = pkt; }
        } catch(e) {
            // ignore
        }
    }

    function showQrIfAvailable() {
        if (lastPacket == null) {
            // Best effort: try building on-demand
            buildPacketIfPossible();
        }
        var json = (lastPacket == null) ? null : lastPacket;
        Ui.pushView(new QRView(json), Ui.SLIDE_LEFT);
    }
}

// Note: Persistence moved to MainView.handlePersistence()
// Date/time functions replaced with Clock.today() and Clock.hour() throughout
