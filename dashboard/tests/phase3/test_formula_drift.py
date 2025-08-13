"""Tests for AC5: Formula drift detection."""
import sys
import tempfile
from pathlib import Path
sys.path.insert(0, '.')

from scripts.phase3.formula_drift import (
    calculate_formula_hash,
    check_formula_change,
    get_current_formula_hash,
    validate_formula_integrity
)

def test_calculate_formula_hash():
    """Test formula hash calculation."""
    code1 = "def score(x): return x * 2"
    code2 = "def score(x): return x * 3"
    
    hash1 = calculate_formula_hash(code1)
    hash2 = calculate_formula_hash(code2)
    
    # Hashes should be different for different code
    assert hash1 != hash2
    assert len(hash1) == 64  # SHA256 produces 64 hex chars
    assert len(hash2) == 64

def test_check_formula_change():
    """Test formula change authorization check."""
    # Should pass with correct tag
    assert check_formula_change("feat: update scoring [FORMULA-CHANGE]") == True
    assert check_formula_change("[FORMULA-CHANGE] fix scoring bug") == True
    
    # Should fail without tag
    assert check_formula_change("feat: update scoring") == False
    assert check_formula_change("fix: scoring bug") == False

def test_get_current_formula_hash():
    """Test getting current formula hash."""
    hash_value = get_current_formula_hash()
    
    # Should return a valid hash or "no-formula"
    assert isinstance(hash_value, str)
    assert len(hash_value) > 0

def test_validate_formula_integrity():
    """Test formula integrity validation."""
    # This test will validate against the current formula
    is_valid, error = validate_formula_integrity()
    
    # Should be valid on first run (creates hash file)
    assert is_valid == True
    assert error is None