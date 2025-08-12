using Toybox.System as Sys;
using Toybox.Time;
using Toybox.Time.Gregorian;

// Real time/date abstraction replacing all stubs (AC2)
class Clock {
    // Returns current date as YYYYMMDD string
    public static function today() {
        var now = Time.now();
        var info = Gregorian.info(now, Time.FORMAT_SHORT);
        return info.year.format("%04d") + info.month.format("%02d") + info.day.format("%02d");
    }
    
    // Returns current hour (0-23)
    public static function hour() {
        var now = Time.now();
        var info = Gregorian.info(now, Time.FORMAT_SHORT);
        return info.hour;
    }
    
    // Returns milliseconds since epoch
    public static function nowMs() {
        return Time.now().value() * 1000;
    }
}