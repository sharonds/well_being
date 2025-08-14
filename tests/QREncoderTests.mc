using Toybox.Test;
using Toybox.System as Sys;

class QREncoderTests {
    
    // Test that QR encoder can handle basic alphanumeric text
    function testQREncoderBasic(logger) {
        var testText = "TEST123";
        var matrix = QREncoder.encode(testText);
        
        Test.assertNotNull(matrix, "QR matrix should not be null for simple text");
        Test.assertEqual(matrix.size(), QREncoder.SIZE, "Matrix should be correct size");
        Test.assertEqual(matrix[0].size(), QREncoder.SIZE, "Matrix rows should be correct size");
        
        return true;
    }
    
    // Test that QR encoder handles JSON packet correctly
    function testQREncoderJsonPacket(logger) {
        // Create a sample JSON packet
        var jsonPacket = InsightPacket.buildPlanPacket("2024-01-15", 75, "Maintain", 2);
        
        if (jsonPacket != null) {
            var matrix = QREncoder.encode(jsonPacket);
            Test.assertNotNull(matrix, "QR matrix should not be null for JSON packet");
            
            // Verify matrix has proper QR structure (finder patterns)
            // Top-left finder pattern check
            Test.assertEqual(matrix[0][0], true, "Top-left corner should be dark");
            Test.assertEqual(matrix[6][6], true, "Finder pattern inner should be dark");
            
            // Verify timing patterns exist
            Test.assertEqual(matrix[6][8], true, "Timing pattern should alternate");
        }
        
        return true;
    }
    
    // Test that QR payload content matches JSON fallback payload
    function testQRPayloadMatchesJson(logger) {
        var dateStr = "2024-01-15";
        var score = 75;
        var band = "Maintain";
        var delta = 2;
        
        // Build the packet using InsightPacket
        var jsonPacket = InsightPacket.buildPlanPacket(dateStr, score, band, delta);
        
        if (jsonPacket != null) {
            // Initialize QRView with the JSON packet
            var qrView = new QRView(jsonPacket);
            
            // The QRView should have the same JSON packet stored
            Test.assertEqual(qrView.packetJson, jsonPacket, 
                           "QR view should store exact JSON packet");
            
            // If QR generation succeeded, matrix should be created
            if (qrView.qrMatrix != null) {
                logger.debug("QR matrix generated successfully");
            } else {
                logger.warning("QR matrix generation failed, fallback to JSON");
            }
            
            // Verify JsonView gets the same packet
            var jsonView = new JsonView(jsonPacket);
            Test.assertEqual(jsonView.text, jsonPacket, 
                           "JSON view should have identical packet text");
        }
        
        return true;
    }
    
    // Test error handling for null/empty input
    function testQREncoderErrorHandling(logger) {
        // Test null input
        var matrix = QREncoder.encode(null);
        Test.assertNull(matrix, "Should return null for null input");
        
        // Test empty string
        matrix = QREncoder.encode("");
        // Empty string might still generate a QR (with just padding)
        // so we just verify it doesn't crash
        
        // Test very long string (should handle gracefully)
        var longText = "";
        for (var i = 0; i < 1000; i++) {
            longText = longText + "A";
        }
        matrix = QREncoder.encode(longText);
        // Should handle without crashing (may return null if too long)
        
        return true;
    }
    
    // Test that QR encoder handles special characters with byte mode
    function testQREncoderByteMode(logger) {
        var textWithSpecial = "{\"test\":\"value\",\"emoji\":\"☺\"}";
        var matrix = QREncoder.encode(textWithSpecial);
        
        // Should fall back to byte mode for non-alphanumeric
        Test.assertNotNull(matrix, "Should handle special chars with byte mode");
        
        if (matrix != null) {
            Test.assertEqual(matrix.size(), QREncoder.SIZE, "Byte mode matrix size correct");
        }
        
        return true;
    }
}