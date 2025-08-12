using Toybox.System as Sys;
using Toybox.Time as Time;

// Logging ring buffer for Phase 3 diagnostics
// Capacity: 20 entries, oldest overwritten when full
// Entry format: {timestamp, level, message}
class Logger {
    // Log levels
    public const INFO = "INFO";
    public const WARN = "WARN";
    public const ERROR = "ERROR";
    
    // Ring buffer implementation
    private static var buffer = new [20]; // Array of 20 entries
    private static var writeIndex = 0;    // Next write position
    private static var count = 0;         // Number of entries (max 20)
    private static var isInitialized = false;
    
    // Initialize ring buffer (call once at app start)
    public static function initialize() {
        if (!isInitialized) {
            for (var i = 0; i < 20; i++) {
                buffer[i] = null;
            }
            writeIndex = 0;
            count = 0;
            isInitialized = true;
            add(INFO, "Logger initialized");
        }
    }
    
    // Add log entry (level should be INFO, WARN, or ERROR)
    public static function add(level, message) {
        if (!isInitialized) {
            initialize();
        }
        
        try {
            var timestamp = _getCurrentTimestamp();
            var entry = {
                :timestamp => timestamp,
                :level => level,
                :message => message
            };
            
            // Add to ring buffer
            buffer[writeIndex] = entry;
            writeIndex = (writeIndex + 1) % 20; // Wrap around
            
            if (count < 20) {
                count++;
            }
            
            // Also print to system log for debugging
            Sys.println("[" + level + "] " + message);
            
        } catch(e) {
            // Failsafe: if logging fails, print directly to avoid infinite recursion
            Sys.println("Logger error: " + e.getErrorMessage());
        }
    }
    
    // Get all log entries (for future debug screen)
    // Returns array of entries ordered from oldest to newest
    public static function getEntries() {
        if (!isInitialized) {
            return [];
        }
        
        var result = new [count];
        var readIndex = (count < 20) ? 0 : writeIndex; // Start from oldest
        
        for (var i = 0; i < count; i++) {
            result[i] = buffer[(readIndex + i) % 20];
        }
        
        return result;
    }
    
    // Get entry count
    public static function getCount() {
        return count;
    }
    
    // Clear all entries (for testing)
    public static function clear() {
        for (var i = 0; i < 20; i++) {
            buffer[i] = null;
        }
        writeIndex = 0;
        count = 0;
    }
    
    // Helper to get current timestamp string
    private static function _getCurrentTimestamp() {
        try {
            var now = Time.now();
            var info = Time.Gregorian.info(now, Time.FORMAT_SHORT);
            
            // Format: YYYY-MM-DD HH:MM:SS
            return Sys.format("$1$-$2$-$3$ $4$:$5$:$6$", [
                info.year,
                _pad(info.month),
                _pad(info.day),
                _pad(info.hour),
                _pad(info.min),
                _pad(info.sec)
            ]);
        } catch(e) {
            // Fallback to system timer if Time API fails
            return "T+" + (Sys.getTimer() / 1000).toString();
        }
    }
    
    // Helper to pad single digits with leading zero
    private static function _pad(num) {
        return (num < 10) ? "0" + num.toString() : num.toString();
    }
}