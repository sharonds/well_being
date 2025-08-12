using Toybox.System as Sys;
using Toybox.WatchUi as Ui;
using Toybox.Time as Time;

// Main application entry
class WellBeingApp extends Ui.AppBase {
    function initialize() { AppBase.initialize(); }
    function onStart(state) { }
    function onStop(state) { }
    function getInitialView() { return [ new MainView() ]; }
}

// Primary view with Phase 3 auto-refresh and enhanced error handling
class MainView extends Ui.View {
    var score = null; // integer 0-100
    var steps = null;
    var restingHR = null;
    var sleepHrs = null;
    var stressVal = null;
    var hrvVal = null; // Phase 3
    var recommendation = null;
    var lastCompute = 0; // epoch seconds
    var lastScorePersisted = null; // previous day score
    var delta = null; // current score - previous

    function onShow() {
        gLogBuffer.log("MainView onShow");
        // Phase 3: Check for auto-refresh before manual compute
        if (_shouldAutoRefresh()) {
            _performAutoRefresh();
        } else {
            computeIfAllowed(true);
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
        var hrvText = "HRV: " + ((ScoreEngine.ENABLE_HRV && hrvVal != null) ? hrvVal.toString() + "ms" : "--");
        
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
            computeIfAllowed(false);
            return true;
        }
        return false;
    }

    function computeIfAllowed(force) {
        var now = Sys.getTimer();
        if (!force && (now - lastCompute) <= 300000) { // 5 min throttle
            gLogBuffer.log("Compute throttled, last compute too recent");
            return;
        }
        
        gLogBuffer.log("Starting score computation (force=" + force + ")");
        
        // Phase 3: Use enhanced metric fetching with error handling
        var metrics = MetricProvider.fetchAllMetrics();
        steps = metrics[:steps];
        restingHR = metrics[:restingHR];
        sleepHrs = metrics[:sleepHours];
        stressVal = metrics[:stressLevel];
        hrvVal = metrics[:hrv];

        // Compute using enhanced engine with HRV support (Phase 3)
        if (MetricProvider.hasMinimumMetrics()) {
            var dynScore = ScoreEngine.computeScore(steps, restingHR, sleepHrs, stressVal, hrvVal);
            // Fallback to phase1 if dynamic path fails (should not normally)
            score = (dynScore != null) ? dynScore : ScoreEngine.computePhase1(steps, restingHR);
            recommendation = RecommendationMapper.getRecommendation(score);
            _handlePersistence();
            gLogBuffer.log("Score computed: " + score + " (" + recommendation + ")");
        } else {
            score = null;
            recommendation = "Data unavailable";
            gLogBuffer.log("Insufficient metrics for score computation");
        }
        
        // Log any errors encountered
        if (metrics[:errors].size() > 0) {
            for (var i = 0; i < metrics[:errors].size(); i++) {
                gLogBuffer.log("Metric error: " + metrics[:errors][i]);
            }
        }
        
        lastCompute = now;
        Ui.requestUpdate();
    }
    
    // Phase 3: Auto-refresh logic with morning window detection
    function _shouldAutoRefresh() {
        try {
            var now = Time.now();
            var info = Time.Gregorian.info(now, Time.FORMAT_MEDIUM);
            var currentDate = _formatDate(info);
            var currentHour = info.hour;
            
            // Check if we're in the morning window (06:00-08:00)
            if (currentHour < 6 || currentHour >= 8) {
                return false;
            }
            
            // Check if we've already auto-refreshed today
            var lastAutoRefreshDate = Sys.getApp().getProperty("lastAutoRefreshDate");
            if (lastAutoRefreshDate != null && lastAutoRefreshDate.equals(currentDate)) {
                gLogBuffer.log("Auto-refresh already performed today: " + currentDate);
                return false;
            }
            
            // Check if this is a new day (day rollover detected)
            var lastScoreDate = Sys.getApp().getProperty("lastScoreDate");
            if (lastScoreDate != null && !lastScoreDate.equals(currentDate)) {
                gLogBuffer.log("Day rollover detected, auto-refresh needed");
                return true;
            }
            
            // First run of the day in morning window
            if (lastAutoRefreshDate == null) {
                gLogBuffer.log("First auto-refresh of the day");
                return true;
            }
            
            return false;
        } catch (e) {
            gLogBuffer.log("Error in _shouldAutoRefresh: " + e.getErrorMessage());
            return false;
        }
    }
    
    // Phase 3: Perform auto-refresh and update persistence
    function _performAutoRefresh() {
        try {
            var now = Time.now();
            var info = Time.Gregorian.info(now, Time.FORMAT_MEDIUM);
            var currentDate = _formatDate(info);
            
            gLogBuffer.log("Performing auto-refresh for " + currentDate);
            
            // Mark auto-refresh as completed for today
            Sys.getApp().setProperty("lastAutoRefreshDate", currentDate);
            
            // Perform the actual computation
            computeIfAllowed(true); // Force computation for auto-refresh
            
        } catch (e) {
            gLogBuffer.log("Error in _performAutoRefresh: " + e.getErrorMessage());
        }
    }
    
    // Enhanced date formatting helper
    function _formatDate(info) {
        var year = info.year.toString();
        var month = (info.month < 10 ? "0" : "") + info.month.toString();
        var day = (info.day < 10 ? "0" : "") + info.day.toString();
        return year + month + day;
    }
}

// Enhanced persistence helpers (Phase 2 + Phase 3)
function _handlePersistence() {
    try {
        var now = Time.now();
        var info = Time.Gregorian.info(now, Time.FORMAT_MEDIUM);
        var today = _formatDate(info);
        
        var props = Sys.getApp().getProperty("lastScoreDate");
        var prevScore = Sys.getApp().getProperty("lastScore");
        
        if (props != null && prevScore != null && props != today) {
            // Previous day found
            lastScorePersisted = prevScore;
            gLogBuffer.log("Previous day score found: " + prevScore + " from " + props);
        }
        
        // Compute delta if we have previous day
        if (lastScorePersisted != null && score != null) {
            delta = score - lastScorePersisted;
            gLogBuffer.log("Score delta: " + delta);
        } else {
            delta = null;
        }
        
        // Store today's score
        Sys.getApp().setProperty("lastScore", score);
        Sys.getApp().setProperty("lastScoreDate", today);
        
        gLogBuffer.log("Score persisted: " + score + " for " + today);
        
    } catch(e) {
        var errorMsg = "Persist error: " + e.getErrorMessage();
        Sys.println(errorMsg);
        gLogBuffer.log(errorMsg);
    }
}

// Enhanced date formatting helper (global function)
function _formatDate(info) {
    var year = info.year.toString();
    var month = (info.month < 10 ? "0" : "") + info.month.toString();
    var day = (info.day < 10 ? "0" : "") + info.day.toString();
    return year + month + day;
}
