using Toybox.System as Sys;
using Toybox.Time as Time;

// Scheduler for Phase 3 auto-refresh functionality
// Handles morning window detection and single daily auto-refresh
class Scheduler {
    // Morning auto-refresh window: 06:00-08:00 local time
    public const AUTO_REFRESH_START_HOUR = 6;  // 06:00
    public const AUTO_REFRESH_END_HOUR = 8;    // 08:00 (exclusive)
    
    // Check if we should trigger auto-refresh
    // Returns true if auto-refresh should run now
    public static function shouldAutoRefresh() {
        try {
            var now = Time.now();
            var info = Time.Gregorian.info(now, Time.FORMAT_SHORT);
            
            // Check if we're in the morning window (06:00-07:59)
            if (info.hour < AUTO_REFRESH_START_HOUR || info.hour >= AUTO_REFRESH_END_HOUR) {
                return false;
            }
            
            // Check if we've already auto-refreshed today
            var today = _formatDate(info);
            var lastAutoRefreshDate = Sys.getApp().getProperty("autoRefreshDate");
            
            if (lastAutoRefreshDate != null && lastAutoRefreshDate.equals(today)) {
                Logger.add(Logger.INFO, "Auto-refresh already done today: " + today);
                return false;
            }
            
            Logger.add(Logger.INFO, "Auto-refresh triggered for: " + today);
            return true;
            
        } catch(e) {
            Logger.add(Logger.ERROR, "shouldAutoRefresh error: " + e.getErrorMessage());
            return false;
        }
    }
    
    // Check if we missed the auto-refresh window and should refresh immediately
    // This handles the case where user opens app after 08:00 but hasn't refreshed today
    public static function shouldRefreshMissedWindow() {
        try {
            var now = Time.now();
            var info = Time.Gregorian.info(now, Time.FORMAT_SHORT);
            
            // Only check if we're past the morning window
            if (info.hour < AUTO_REFRESH_END_HOUR) {
                return false;
            }
            
            // Check if we've auto-refreshed today
            var today = _formatDate(info);
            var lastAutoRefreshDate = Sys.getApp().getProperty("autoRefreshDate");
            
            if (lastAutoRefreshDate == null || !lastAutoRefreshDate.equals(today)) {
                Logger.add(Logger.INFO, "Missed window refresh triggered for: " + today);
                return true;
            }
            
            return false;
            
        } catch(e) {
            Logger.add(Logger.ERROR, "shouldRefreshMissedWindow error: " + e.getErrorMessage());
            return false;
        }
    }
    
    // Mark that auto-refresh has been completed for today
    public static function markAutoRefreshCompleted() {
        try {
            var now = Time.now();
            var info = Time.Gregorian.info(now, Time.FORMAT_SHORT);
            var today = _formatDate(info);
            
            Sys.getApp().setProperty("autoRefreshDate", today);
            Sys.getApp().setProperty("lastRunMode", "auto");
            
            Logger.add(Logger.INFO, "Auto-refresh completed and marked for: " + today);
            
        } catch(e) {
            Logger.add(Logger.ERROR, "markAutoRefreshCompleted error: " + e.getErrorMessage());
        }
    }
    
    // Mark that manual refresh has been completed
    public static function markManualRefreshCompleted() {
        try {
            Sys.getApp().setProperty("lastRunMode", "manual");
            Logger.add(Logger.INFO, "Manual refresh completed");
            
        } catch(e) {
            Logger.add(Logger.ERROR, "markManualRefreshCompleted error: " + e.getErrorMessage());
        }
    }
    
    // Get current date string in YYYYMMDD format
    public static function getCurrentDateString() {
        try {
            var now = Time.now();
            var info = Time.Gregorian.info(now, Time.FORMAT_SHORT);
            return _formatDate(info);
        } catch(e) {
            Logger.add(Logger.ERROR, "getCurrentDateString error: " + e.getErrorMessage());
            return "20250812"; // Fallback date
        }
    }
    
    // Get last run mode (auto/manual/null)
    public static function getLastRunMode() {
        return Sys.getApp().getProperty("lastRunMode");
    }
    
    // Check if we're currently in the auto-refresh window
    public static function inAutoRefreshWindow() {
        try {
            var now = Time.now();
            var info = Time.Gregorian.info(now, Time.FORMAT_SHORT);
            return (info.hour >= AUTO_REFRESH_START_HOUR && info.hour < AUTO_REFRESH_END_HOUR);
        } catch(e) {
            Logger.add(Logger.ERROR, "inAutoRefreshWindow error: " + e.getErrorMessage());
            return false;
        }
    }
    
    // Helper to format date as YYYYMMDD
    private static function _formatDate(info) {
        return Sys.format("$1$$2$$3$", [
            info.year,
            _pad(info.month),
            _pad(info.day)
        ]);
    }
    
    // Helper to pad single digits with leading zero
    private static function _pad(num) {
        return (num < 10) ? "0" + num.toString() : num.toString();
    }
}