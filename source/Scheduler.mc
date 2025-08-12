// Pure helper for deciding auto-refresh eligibility (Phase 3)
// This isolates logic for unit tests without UI dependencies.
class Scheduler {
    // Returns true if we should perform an auto-refresh now.
    // Inputs:
    //   currentDate (string yyyymmdd)
    //   currentHour (int 0-23)
    //   lastScoreDate (string or null)
    //   autoRefreshDate (string or null) -- date we already auto-refreshed
    //   manualRunToday (boolean) -- whether user manually refreshed today
    //   lastComputeMs (number) -- last compute timestamp ms
    //   nowMs (number) -- current time ms
    // Constraints:
    //   - Auto only within 06:00-08:00 inclusive window (hour 6 or 7)
    //   - Only once per day (autoRefreshDate != currentDate)
    //   - Skip if manual run already produced today's score
    //   - Respect 5 min throttle (now-lastComputeMs > 300000)
    public static function shouldAuto(currentDate, currentHour, lastScoreDate, autoRefreshDate, manualRunToday, lastComputeMs, nowMs) {
        if (currentDate == null) { return false; }
        if (manualRunToday) { return false; }
        if (autoRefreshDate != null && autoRefreshDate == currentDate) { return false; }
        if (currentHour < 6 || currentHour >= 8) { return false; } // hours 6-7
        if ((nowMs - lastComputeMs) <= 300000) { return false; }
        return true;
    }

    // Late open scenario: if user opens after window and no score yet today, compute immediately.
    public static function shouldLateCompute(currentDate, currentHour, lastScoreDate, manualRunToday) {
        if (currentDate == null) { return false; }
        if (manualRunToday) { return false; }
        if (lastScoreDate != null && lastScoreDate == currentDate) { return false; }
        if (currentHour >= 8) { return true; }
        return false;
    }
}
