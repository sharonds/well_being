using Toybox.System as Sys;

// Ring buffer for in-memory logging (Phase 3)
// Max 20 entries, FIFO, timestamped for diagnostics
class LogBuffer {
    private var entries;
    private var maxEntries;
    private var currentIndex;
    private var isFull;
    
    function initialize() {
        maxEntries = 20;
        entries = new Array[maxEntries];
        currentIndex = 0;
        isFull = false;
    }
    
    // Add a timestamped log entry
    public function log(message) {
        if (message == null) { return; }
        
        try {
            var timestamp = Sys.getTimer() / 1000; // Convert to seconds
            var entry = {
                :time => timestamp,
                :message => message.toString()
            };
            
            entries[currentIndex] = entry;
            currentIndex = (currentIndex + 1) % maxEntries;
            
            if (currentIndex == 0) {
                isFull = true;
            }
        } catch (e) {
            // Silent failure to avoid infinite recursion
            // if logging itself fails
        }
    }
    
    // Get all log entries in chronological order (oldest first)
    public function getEntries() {
        var result = [];
        
        if (!isFull && currentIndex == 0) {
            return result; // No entries yet
        }
        
        try {
            var startIndex = isFull ? currentIndex : 0;
            var count = isFull ? maxEntries : currentIndex;
            
            for (var i = 0; i < count; i++) {
                var index = (startIndex + i) % maxEntries;
                var entry = entries[index];
                if (entry != null) {
                    result.add(entry);
                }
            }
        } catch (e) {
            // Return partial results on error
        }
        
        return result;
    }
    
    // Get latest N entries (most recent first)
    public function getLatest(n) {
        if (n <= 0) { return []; }
        
        var allEntries = getEntries();
        var result = [];
        var start = allEntries.size() > n ? allEntries.size() - n : 0;
        
        for (var i = allEntries.size() - 1; i >= start; i--) {
            result.add(allEntries[i]);
        }
        
        return result;
    }
    
    // Clear all entries
    public function clear() {
        try {
            for (var i = 0; i < maxEntries; i++) {
                entries[i] = null;
            }
            currentIndex = 0;
            isFull = false;
        } catch (e) {
            // Silent failure
        }
    }
    
    // Get formatted log dump for debugging
    public function getFormattedDump() {
        var entries = getLatest(10); // Last 10 entries
        var result = "=== Log Buffer (last 10) ===\n";
        
        for (var i = 0; i < entries.size(); i++) {
            var entry = entries[i];
            if (entry != null) {
                result += "[" + entry[:time] + "] " + entry[:message] + "\n";
            }
        }
        
        return result;
    }
}

// Global singleton instance
var gLogBuffer = new LogBuffer();