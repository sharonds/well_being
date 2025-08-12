// Infrastructure component tests for AC10 coverage
// Tests Clock, PerformanceTimer, ErrorCodes, and MetricProvider
using Toybox.System as Sys;

class InfrastructureTests {
    
    public static function runAllInfrastructureTests() {
        var results = [];
        
        // Clock abstraction tests
        results.add(testClockToday());
        results.add(testClockHour());
        results.add(testClockNowMs());
        
        // PerformanceTimer tests
        results.add(testPerformanceTimerBasic());
        results.add(testPerformanceTimerAverage());
        results.add(testPerformanceTimerClear());
        
        // ErrorCodes constant tests
        results.add(testErrorCodesExist());
        
        // MetricProvider tests
        results.add(testMetricProviderHasMinimum());
        results.add(testMetricProviderStubs());
        
        // Report results
        var passed = 0;
        var total = results.size();
        for (var i = 0; i < results.size(); i++) {
            if (results[i]) {
                passed++;
            }
        }
        
        Sys.println("Infrastructure Tests: " + passed + "/" + total + " passed");
        return passed == total;
    }
    
    // Test Clock.today() returns valid date string format
    public static function testClockToday() {
        try {
            var today = Clock.today();
            var passed = (today != null && today instanceof String && today.length() >= 8);
            Sys.println("Clock today test: " + (passed ? "PASS" : "FAIL"));
            return passed;
        } catch (e) {
            Sys.println("Clock today test: FAIL - " + e.getErrorMessage());
            return false;
        }
    }
    
    // Test Clock.hour() returns valid hour (0-23)
    public static function testClockHour() {
        try {
            var hour = Clock.hour();
            var passed = (hour != null && hour >= 0 && hour <= 23);
            Sys.println("Clock hour test: hour=" + hour + " " + (passed ? "PASS" : "FAIL"));
            return passed;
        } catch (e) {
            Sys.println("Clock hour test: FAIL - " + e.getErrorMessage());
            return false;
        }
    }
    
    // Test Clock.nowMs() returns valid timestamp
    public static function testClockNowMs() {
        try {
            var nowMs = Clock.nowMs();
            var passed = (nowMs != null && nowMs > 0);
            Sys.println("Clock nowMs test: " + (passed ? "PASS" : "FAIL"));
            return passed;
        } catch (e) {
            Sys.println("Clock nowMs test: FAIL - " + e.getErrorMessage());
            return false;
        }
    }
    
    // Test PerformanceTimer basic start/stop functionality
    public static function testPerformanceTimerBasic() {
        try {
            PerformanceTimer.clear();
            PerformanceTimer.start();
            // Simulate some work
            for (var i = 0; i < 1000; i++) { }
            var elapsed = PerformanceTimer.stop();
            var passed = (elapsed != null && elapsed >= 0);
            Sys.println("PerformanceTimer basic: elapsed=" + elapsed + "ms " + (passed ? "PASS" : "FAIL"));
            return passed;
        } catch (e) {
            Sys.println("PerformanceTimer basic test: FAIL - " + e.getErrorMessage());
            return false;
        }
    }
    
    // Test PerformanceTimer average calculation
    public static function testPerformanceTimerAverage() {
        try {
            PerformanceTimer.clear();
            
            // Take multiple measurements
            for (var j = 0; j < 3; j++) {
                PerformanceTimer.start();
                for (var i = 0; i < 500; i++) { } // Some work
                PerformanceTimer.stop();
            }
            
            var average = PerformanceTimer.getAverage();
            var passed = (average != null && average >= 0);
            Sys.println("PerformanceTimer average: avg=" + average + "ms " + (passed ? "PASS" : "FAIL"));
            return passed;
        } catch (e) {
            Sys.println("PerformanceTimer average test: FAIL - " + e.getErrorMessage());
            return false;
        }
    }
    
    // Test PerformanceTimer clear functionality
    public static function testPerformanceTimerClear() {
        try {
            // Take a measurement
            PerformanceTimer.start();
            PerformanceTimer.stop();
            
            // Clear and verify
            PerformanceTimer.clear();
            var averageAfterClear = PerformanceTimer.getAverage();
            
            var passed = (averageAfterClear == null); // Should be null after clear
            Sys.println("PerformanceTimer clear: " + (passed ? "PASS" : "FAIL"));
            return passed;
        } catch (e) {
            Sys.println("PerformanceTimer clear test: FAIL - " + e.getErrorMessage());
            return false;
        }
    }
    
    // Test ErrorCodes constants exist and are strings
    public static function testErrorCodesExist() {
        try {
            var passed = (
                ErrorCodes.METRIC_STEPS instanceof String &&
                ErrorCodes.METRIC_RHR instanceof String &&
                ErrorCodes.PERSIST_SAVE instanceof String &&
                ErrorCodes.COMPUTE_SCORE instanceof String &&
                ErrorCodes.UI_RENDER instanceof String
            );
            Sys.println("ErrorCodes exist test: " + (passed ? "PASS" : "FAIL"));
            return passed;
        } catch (e) {
            Sys.println("ErrorCodes exist test: FAIL - " + e.getErrorMessage());
            return false;
        }
    }
    
    // Test MetricProvider hasMinimumMetrics logic
    public static function testMetricProviderHasMinimum() {
        try {
            var hasMin = MetricProvider.hasMinimumMetrics();
            // Should return boolean regardless of actual metric availability
            var passed = (hasMin == true || hasMin == false);
            Sys.println("MetricProvider hasMinimum: result=" + hasMin + " " + (passed ? "PASS" : "FAIL"));
            return passed;
        } catch (e) {
            Sys.println("MetricProvider hasMinimum test: FAIL - " + e.getErrorMessage());
            return false;
        }
    }
    
    // Test MetricProvider stub methods return reasonable values
    public static function testMetricProviderStubs() {
        try {
            var sleep = MetricProvider.getSleepHours();
            var stress = MetricProvider.getStressLevel();
            var hrv = MetricProvider.getHRV();
            
            var passed = (
                sleep != null && sleep > 0 && sleep <= 12 &&
                stress != null && stress >= 0 && stress <= 100 &&
                (hrv == null || hrv > 0) // HRV can be null or positive
            );
            
            Sys.println("MetricProvider stubs: sleep=" + sleep + " stress=" + stress + " hrv=" + hrv + " " + (passed ? "PASS" : "FAIL"));
            return passed;
        } catch (e) {
            Sys.println("MetricProvider stubs test: FAIL - " + e.getErrorMessage());
            return false;
        }
    }
}