using Toybox.System as Sys;
using Toybox.Json as Json;
using Toybox.Time as Time;

class InsightPacket {
    // Build plan_daily insight packet JSON string or null if required fields missing
    static function buildPlanPacket(dateStr as String, score as Number, band as String, delta as Number) as String {
        try {
            if (score == null || dateStr == null || band == null) { return null; }

            var now = Time.now();
            // Simple ISO8601 approximation (seconds resolution, Zulu)
            var createdAt = _iso8601(now);

            var planType = _mapBandToPlanType(band);
            var minutesRange = _mapPlanMinutes(planType);
            var addons = [ "core10", "breath10" ];

            var env = {
                "version" => "v1",
                "type" => "plan_daily",
                "device_id" => _deviceId(),
                "created_at" => createdAt,
                "payload" => {
                    "date" => dateStr,
                    "band" => band,
                    "score" => score,
                    "delta" => (delta == null ? 0 : delta),
                    "plan" => {
                        "type" => planType,
                        "minutes_range" => minutesRange,
                        "addons" => addons
                    },
                    "why" => [],
                    "schema_version" => "v1.0.0"
                }
            };

            return Json.toJson(env);
        } catch(e) {
            return null;
        }
    }

    static function _mapBandToPlanType(band as String) as String {
        if (band == null) return "maintain";
        if (band.equals("Go for it")) return "hard";
        if (band.equals("Maintain")) return "maintain";
        return "easy"; // Take it easy or others
    }

    static function _mapPlanMinutes(planType as String) as String {
        if (planType.equals("hard")) return "50-70";
        if (planType.equals("maintain")) return "45-60";
        return "30-40"; // easy
    }

    static function _deviceId() as String {
        // Best-effort device hint; avoid PII
        try {
            var ds = Sys.getDeviceSettings();
            if (ds != null && ds has :partNumber) { return ds[:partNumber]; }
        } catch(e) {}
        return "watch";
    }

    static function _iso8601(epochSeconds as Number) as String {
        // Minimal ISO8601: YYYY-MM-DDThh:mm:ssZ using System.getClockTime()
        try {
            var t = Time.Gregorian.info(Time.now(), Time.FORMAT_SHORT);
            var year = t[:year];
            var month = t[:month];
            var day = t[:day];
            var hour = t[:hour];
            var min = t[:min];
            var sec = t[:sec];
            return _pad(year,4) + "-" + _pad(month,2) + "-" + _pad(day,2) + "T" + _pad(hour,2) + ":" + _pad(min,2) + ":" + _pad(sec,2) + "Z";
        } catch(e) {
            return "";
        }
    }

    static function _pad(n as Number, width as Number) as String {
        var s = n.format("%d");
        while (s.length() < width) { s = "0" + s; }
        return s;
    }
}
