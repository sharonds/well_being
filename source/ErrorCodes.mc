// Structured error codes for logging (Issue #9 AC4)
class ErrorCodes {
    // Metric fetch errors
    public const METRIC_STEPS = "METRIC_STEPS";
    public const METRIC_RHR = "METRIC_RHR"; 
    public const METRIC_SLEEP = "METRIC_SLEEP";
    public const METRIC_STRESS = "METRIC_STRESS";
    public const METRIC_HRV = "METRIC_HRV";
    
    // Persistence errors
    public const PERSIST_SAVE = "PERSIST_SAVE";
    public const PERSIST_LOAD = "PERSIST_LOAD";
    public const PERSIST_HISTORY = "PERSIST_HISTORY";
    
    // Computation errors
    public const COMPUTE_SCORE = "COMPUTE_SCORE";
    public const COMPUTE_RECOMMENDATION = "COMPUTE_RECOMMENDATION";
    
    // UI errors
    public const UI_RENDER = "UI_RENDER";
    public const UI_INPUT = "UI_INPUT";
}
