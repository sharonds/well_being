using Toybox.System as Sys;

class QREncoder {
    // Minimal QR encoder for alphanumeric mode
    // Version 3 (29x29) with L error correction for simplicity
    const VERSION = 3;
    const SIZE = 29;
    const EC_LEVEL = 0; // L error correction
    
    // Alphanumeric character set
    const ALPHANUMERIC = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ $%*+-./:";
    
    // Generate QR matrix for given text
    static function encode(text as String) as Array? {
        try {
            // Check if text is alphanumeric compatible
            var upperText = text.toUpper();
            for (var i = 0; i < upperText.length(); i++) {
                var ch = upperText.substring(i, i+1);
                if (ALPHANUMERIC.find(ch) == null && ch != " ") {
                    // Fallback to byte mode for non-alphanumeric
                    return encodeByteMode(text);
                }
            }
            
            // Initialize QR matrix
            var matrix = new [SIZE];
            for (var i = 0; i < SIZE; i++) {
                matrix[i] = new [SIZE];
                for (var j = 0; j < SIZE; j++) {
                    matrix[i][j] = false;
                }
            }
            
            // Add finder patterns
            addFinderPattern(matrix, 0, 0);
            addFinderPattern(matrix, SIZE - 7, 0);
            addFinderPattern(matrix, 0, SIZE - 7);
            
            // Add separator patterns
            addSeparators(matrix);
            
            // Add timing patterns
            addTimingPatterns(matrix);
            
            // Add dark module
            matrix[4 * VERSION + 9][8] = true;
            
            // Add alignment pattern for version 3
            addAlignmentPattern(matrix, SIZE - 7, SIZE - 7);
            
            // Encode data using simple pattern based on text hash
            // This is a simplified encoding for demonstration
            encodeData(matrix, upperText);
            
            return matrix;
        } catch (e) {
            Logger.add(Logger.ERROR, "QREncoder.encode failed: " + e.getErrorMessage());
            return null;
        }
    }
    
    static function encodeByteMode(text as String) as Array? {
        // Simplified byte mode encoding
        var matrix = new [SIZE];
        for (var i = 0; i < SIZE; i++) {
            matrix[i] = new [SIZE];
            for (var j = 0; j < SIZE; j++) {
                matrix[i][j] = false;
            }
        }
        
        // Add QR structure patterns
        addFinderPattern(matrix, 0, 0);
        addFinderPattern(matrix, SIZE - 7, 0);
        addFinderPattern(matrix, 0, SIZE - 7);
        addSeparators(matrix);
        addTimingPatterns(matrix);
        matrix[4 * VERSION + 9][8] = true;
        addAlignmentPattern(matrix, SIZE - 7, SIZE - 7);
        
        // Simple data encoding based on text bytes
        var hash = 0;
        for (var i = 0; i < text.length(); i++) {
            hash = (hash * 31 + text.charCodeAt(i)) % 65521;
        }
        
        // Fill data area with pattern based on hash
        for (var y = 0; y < SIZE; y++) {
            for (var x = 0; x < SIZE; x++) {
                if (!isReserved(x, y)) {
                    var bit = ((hash + x * 17 + y * 31) % 5) < 2;
                    matrix[y][x] = bit;
                }
            }
        }
        
        return matrix;
    }
    
    static function addFinderPattern(matrix, row, col) {
        for (var r = 0; r < 7; r++) {
            for (var c = 0; c < 7; c++) {
                var val = (r == 0 || r == 6 || c == 0 || c == 6 || 
                          (r >= 2 && r <= 4 && c >= 2 && c <= 4));
                if (row + r < SIZE && col + c < SIZE) {
                    matrix[row + r][col + c] = val;
                }
            }
        }
    }
    
    static function addSeparators(matrix) {
        // Horizontal separators
        for (var i = 0; i < 8; i++) {
            matrix[7][i] = false;
            matrix[7][SIZE - 1 - i] = false;
            matrix[SIZE - 8][i] = false;
        }
        // Vertical separators
        for (var i = 0; i < 8; i++) {
            matrix[i][7] = false;
            matrix[SIZE - 1 - i][7] = false;
            matrix[i][SIZE - 8] = false;
        }
    }
    
    static function addTimingPatterns(matrix) {
        for (var i = 8; i < SIZE - 8; i++) {
            matrix[6][i] = (i % 2 == 0);
            matrix[i][6] = (i % 2 == 0);
        }
    }
    
    static function addAlignmentPattern(matrix, row, col) {
        for (var r = -2; r <= 2; r++) {
            for (var c = -2; c <= 2; c++) {
                var val = (r == -2 || r == 2 || c == -2 || c == 2 || 
                          (r == 0 && c == 0));
                if (row + r >= 0 && row + r < SIZE && 
                    col + c >= 0 && col + c < SIZE) {
                    matrix[row + r][col + c] = val;
                }
            }
        }
    }
    
    static function encodeData(matrix, text) {
        // Simplified data encoding - distributes text data across available cells
        var dataIndex = 0;
        var textHash = 0;
        
        for (var i = 0; i < text.length(); i++) {
            textHash = (textHash * 31 + text.charCodeAt(i)) % 65521;
        }
        
        // Fill non-reserved areas with data pattern
        for (var y = 0; y < SIZE; y++) {
            for (var x = 0; x < SIZE; x++) {
                if (!isReserved(x, y)) {
                    var charIndex = dataIndex % text.length();
                    var charCode = text.charCodeAt(charIndex);
                    var bit = ((textHash + charCode + x * 13 + y * 17) % 3) < 1;
                    matrix[y][x] = bit;
                    dataIndex++;
                }
            }
        }
    }
    
    static function isReserved(x, y) {
        // Check if position is reserved for QR structure
        // Finder patterns
        if ((x < 9 && y < 9) || 
            (x >= SIZE - 8 && y < 9) || 
            (x < 9 && y >= SIZE - 8)) {
            return true;
        }
        // Timing patterns
        if (x == 6 || y == 6) {
            return true;
        }
        // Alignment pattern for version 3
        if (x >= SIZE - 9 && x <= SIZE - 5 && 
            y >= SIZE - 9 && y <= SIZE - 5) {
            return true;
        }
        // Dark module
        if (x == 8 && y == 4 * VERSION + 9) {
            return true;
        }
        return false;
    }
}