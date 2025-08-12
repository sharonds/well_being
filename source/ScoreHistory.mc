using Toybox.Application as App;
using Toybox.System as Sys;

// 7-day circular buffer for score history persistence (AC6)
class ScoreHistory {
    const MAX_DAYS = 7;
    
    private var scores = new [MAX_DAYS];
    private var dates = new [MAX_DAYS]; 
    private var currentIndex = 0;
    private var count = 0;
    
    public function initialize() {
        load();
    }
    
    // Add new score to circular buffer
    public function addScore(score, date) {
        if (score == null || date == null) { return; }
        
        // Check if we already have an entry for this date
        for (var i = 0; i < count; i++) {
            if (dates[i] != null && dates[i].equals(date)) {
                // Update existing entry for same date
                scores[i] = score;
                save();
                return;
            }
        }
        
        // Add new entry
        scores[currentIndex] = score;
        dates[currentIndex] = date;
        
        // Advance circular buffer
        currentIndex = (currentIndex + 1) % MAX_DAYS;
        if (count < MAX_DAYS) {
            count++;
        }
        
        save();
    }
    
    // Get most recent score for delta calculation
    public function getLastScore() {
        if (count == 0) { return null; }
        
        var lastIndex = (currentIndex - 1 + MAX_DAYS) % MAX_DAYS;
        return scores[lastIndex];
    }
    
    // Get previous day's score (for "Yesterday: 72" display)
    public function getPreviousScore() {
        if (count < 2) { return null; }
        
        var prevIndex = (currentIndex - 2 + MAX_DAYS) % MAX_DAYS;
        return scores[prevIndex];
    }
    
    // Get full history ordered from oldest to newest
    public function getHistory() {
        var history = [];
        
        if (count == 0) { return history; }
        
        var startIndex = (count < MAX_DAYS) ? 0 : currentIndex;
        
        for (var i = 0; i < count; i++) {
            var index = (startIndex + i) % MAX_DAYS;
            if (scores[index] != null && dates[index] != null) {
                history.add({
                    "score" => scores[index],
                    "date" => dates[index]
                });
            }
        }
        
        return history;
    }
    
    // Calculate delta from most recent score
    public function getDelta(currentScore) {
        var lastScore = getLastScore();
        if (lastScore == null || currentScore == null) { return null; }
        return currentScore - lastScore;
    }
    
    // Load from persistent storage
    private function load() {
        try {
            var app = App.getApp();
            var savedScores = app.getProperty("historyScores");
            var savedDates = app.getProperty("historyDates");
            var savedIndex = app.getProperty("historyIndex");
            var savedCount = app.getProperty("historyCount");
            
            if (savedScores != null && savedDates != null) {
                scores = savedScores;
                dates = savedDates;
                currentIndex = (savedIndex != null) ? savedIndex : 0;
                count = (savedCount != null) ? savedCount : 0;
            }
        } catch (e) {
            // Reset on any loading error
            scores = new [MAX_DAYS];
            dates = new [MAX_DAYS];
            currentIndex = 0;
            count = 0;
        }
    }
    
    // Save to persistent storage
    private function save() {
        try {
            var app = App.getApp();
            app.setProperty("historyScores", scores);
            app.setProperty("historyDates", dates);
            app.setProperty("historyIndex", currentIndex);
            app.setProperty("historyCount", count);
        } catch (e) {
            // Silently fail - non-critical for app functionality
        }
    }
    
    // Clear all history (for testing)
    public function clear() {
        scores = new [MAX_DAYS];
        dates = new [MAX_DAYS];
        currentIndex = 0;
        count = 0;
        save();
    }
}