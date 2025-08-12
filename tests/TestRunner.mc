// Unit tests for ScoreEngine and RecommendationMapper
// These tests validate the examples from the PRD
using Toybox.System as Sys;

class TestRunner {
    public static function runAllTests() {
        var results = [];
        
        // Test ScoreEngine examples from PRD
        results.add(testScoreEngineExampleA());
        results.add(testScoreEngineExampleC()); 
        results.add(testScoreEngineBounds());
        
        // Test RecommendationMapper bands
        results.add(testRecommendationBands());
        results.add(testRecommendationEdgeCases());
        
        // Report results
        var passed = 0;
        var total = results.size();
        for (var i = 0; i < results.size(); i++) {
            if (results[i]) {
                passed++;
            }
        }
        
        Sys.println("Tests: " + passed + "/" + total + " passed");
        return passed == total;
    }
    
    // PRD Example A: Steps=8,000; RestingHR=55 => Expected Score=65
    public static function testScoreEngineExampleA() {
        var score = ScoreEngine.computePhase1(8000, 55);
        var expected = 65;
        var passed = (score == expected);
        Sys.println("Example A: score=" + score + " expected=" + expected + " " + (passed ? "PASS" : "FAIL"));
        return passed;
    }
    
    // PRD Example C: Steps=3,000; RestingHR=70 => Expected Score=25  
    public static function testScoreEngineExampleC() {
        var score = ScoreEngine.computePhase1(3000, 70);
        var expected = 25;
        var passed = (score == expected);
        Sys.println("Example C: score=" + score + " expected=" + expected + " " + (passed ? "PASS" : "FAIL"));
        return passed;
    }
    
    // Test bounds enforcement (0-100)
    public static function testScoreEngineBounds() {
        // Test extreme values
        var scoreMin = ScoreEngine.computePhase1(0, 80); // Should be very low
        var scoreMax = ScoreEngine.computePhase1(15000, 40); // Should cap at 100
        
        var boundsOk = (scoreMin >= 0 && scoreMin <= 100 && scoreMax >= 0 && scoreMax <= 100);
        Sys.println("Bounds test: min=" + scoreMin + " max=" + scoreMax + " " + (boundsOk ? "PASS" : "FAIL"));
        return boundsOk;
    }
    
    // Test recommendation bands from PRD
    public static function testRecommendationBands() {
        var rec39 = RecommendationMapper.getRecommendation(39);  // "Take it easy"
        var rec40 = RecommendationMapper.getRecommendation(40);  // "Maintain"  
        var rec69 = RecommendationMapper.getRecommendation(69);  // "Maintain"
        var rec70 = RecommendationMapper.getRecommendation(70);  // "Go for it"
        
        var bandsOk = (rec39.equals("Take it easy") && 
                      rec40.equals("Maintain") &&
                      rec69.equals("Maintain") && 
                      rec70.equals("Go for it"));
        
        Sys.println("Bands test: 39=" + rec39 + " 40=" + rec40 + " 69=" + rec69 + " 70=" + rec70 + " " + (bandsOk ? "PASS" : "FAIL"));
        return bandsOk;
    }
    
    // Test edge cases for recommendations
    public static function testRecommendationEdgeCases() {
        var recNull = RecommendationMapper.getRecommendation(null);
        var recNeg = RecommendationMapper.getRecommendation(-1);
        var recHigh = RecommendationMapper.getRecommendation(101);
        
        var edgesOk = (recNull.equals("Data unavailable") &&
                      recNeg.equals("Data unavailable") &&
                      recHigh.equals("Data unavailable"));
        
        Sys.println("Edge cases test: null=" + recNull + " -1=" + recNeg + " 101=" + recHigh + " " + (edgesOk ? "PASS" : "FAIL"));
        return edgesOk;
    }
}