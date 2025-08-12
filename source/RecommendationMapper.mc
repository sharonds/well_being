using Toybox.System as Sys;

class RecommendationMapper {
    // Map score to recommendation text according to PRD bands
    // Range 0-39: "Take it easy"
    // Range 40-69: "Maintain" 
    // Range 70-100: "Go for it"
    public static function getRecommendation(score) {
        if (score == null || score < 0 || score > 100) {
            return "Data unavailable";
        }
        
        if (score <= 39) {
            return "Take it easy";
        } else if (score <= 69) {
            return "Maintain";
        } else {
            return "Go for it";
        }
    }
}