using Toybox.System as Sys;

// Simple performance timing utility (Issue #9 AC8)
class PerformanceTimer {
    private static var _startTime = null;
    private static var _measurements = [];
    
    public static function start() {
        _startTime = Sys.getTimer();
    }
    
    public static function stop() {
        if (_startTime == null) { return null; }
        var elapsed = Sys.getTimer() - _startTime;
        _measurements.add(elapsed);
        _startTime = null;
        return elapsed;
    }
    
    public static function getAverage() {
        if (_measurements.size() == 0) { return null; }
        var sum = 0;
        for (var i = 0; i < _measurements.size(); i++) {
            sum += _measurements[i];
        }
        return sum / _measurements.size();
    }
    
    public static function clear() {
        _measurements = [];
        _startTime = null;
    }
}
