using Toybox.System as Sys;

// Simple ring buffer logger (Phase 3)
class Logger {
    public const CAPACITY = 20;
    private static var _entries = [];
    private static var _nextIndex = 0; // points to position to overwrite

    // Adds a log entry with level (INFO/WARN/ERROR) and short message
    public static function add(level, msg) {
        try {
            var ts = Sys.getTimer(); // ms since app start (sufficient ordering)
            var entry = { :ts=>ts, :level=>level, :msg=>msg };
            if (_entries.size() < CAPACITY) {
                _entries.add(entry);
            } else {
                _entries[_nextIndex] = entry;
            }
            _nextIndex = (_nextIndex + 1) % CAPACITY;
        } catch(e) {
            // Swallow to avoid cascading failures
        }
    }

    // Returns a copy of current log entries in logical chronological order (oldest first)
    public static function list() {
        var out = [];
        try {
            if (_entries.size() < CAPACITY) {
                // Already chronological
                for (var i=0;i<_entries.size();i++) { out.add(_entries[i]); }
            } else {
                // Start from nextIndex (oldest) and wrap
                for (var j=0;j<CAPACITY;j++) {
                    var idx = (_nextIndex + j) % CAPACITY;
                    out.add(_entries[idx]);
                }
            }
        } catch(e) {}
        return out;
    }
}
