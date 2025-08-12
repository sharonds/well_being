// Unit tests for ScoreEngine and RecommendationMapper
// These tests validate the examples from the PRD
using Toybox.System as Sys;

class TestRunner {
    public static function runAllTests() {
        var results = [];
        
        // Test ScoreEngine examples from PRD
        results.add(testScoreEngineExampleA());
        results.add(testScoreEngineExampleC()); 
    results.add(testScoreEngineExampleBFull());
    results.add(testRedistributionPermutationMissingSleep());
        results.add(testScoreEngineBounds());
    results.add(testBackwardCompatibilityPhase1());
        
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

    // PRD Example B: Steps=12500; RestHR=48; Sleep=7h; Stress=35 => Expected 88 when both feature flags enabled
    public static function testScoreEngineExampleBFull() {
        // Enable flags
        ScoreEngine.ENABLE_SLEEP = true; ScoreEngine.ENABLE_STRESS = true;
        var score = ScoreEngine.computeScore(12500, 48, 7, 35);
        var expected = 88;
        var passed = (score == expected);
        Sys.println("Example B: score=" + score + " expected=" + expected + " " + (passed ? "PASS" : "FAIL"));
        return passed;
    }

    // Redistribution permutation: Missing sleep only (stress disabled or null)
    // Provide steps & rhr & stress (flag off) => weights should redistribute between steps & rhr only producing Phase1 logic
    public static function testRedistributionPermutationMissingSleep() {
        ScoreEngine.ENABLE_SLEEP = false; ScoreEngine.ENABLE_STRESS = false;
        var scoreDyn = ScoreEngine.computeScore(8000, 55, null, null);
        var scoreP1 = ScoreEngine.computePhase1(8000, 55);
        var passed = (scoreDyn == scoreP1 && scoreDyn == 65);
        Sys.println("Redistrib missing sleep: dyn=" + scoreDyn + " phase1=" + scoreP1 + " " + (passed ? "PASS" : "FAIL"));
        return passed;
    }

    // Backward compatibility: When flags disabled, computeScore should match Phase1 for any inputs ignoring sleep/stress
    public static function testBackwardCompatibilityPhase1() {
        ScoreEngine.ENABLE_SLEEP = false; ScoreEngine.ENABLE_STRESS = false;
        var scoreDyn = ScoreEngine.computeScore(3000, 70, 7, 35); // Extra metrics provided but flags off
        var scoreP1 = ScoreEngine.computePhase1(3000, 70);
        var passed = (scoreDyn == scoreP1 && scoreDyn == 25);
        Sys.println("Backward compat: dyn=" + scoreDyn + " phase1=" + scoreP1 + " " + (passed ? "PASS" : "FAIL"));
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