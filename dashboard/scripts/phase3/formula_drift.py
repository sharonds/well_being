"""AC5: Formula drift detection and gating."""
import hashlib
import inspect
import json
from pathlib import Path
from typing import Optional

# Import score engine to get formula
try:
    from score.engine import compute_score, BAND_MAP
except ImportError:
    compute_score = None
    BAND_MAP = None

FORMULA_HASH_FILE = Path("dashboard/.formula_hash")

def calculate_formula_hash(formula_code: str) -> str:
    """Calculate SHA256 hash of formula code."""
    return hashlib.sha256(formula_code.encode()).hexdigest()

def check_formula_change(commit_message: str) -> bool:
    """Check if formula change is authorized.
    
    Returns True if [FORMULA-CHANGE] tag present.
    """
    return "[FORMULA-CHANGE]" in commit_message

def get_current_formula_hash() -> str:
    """Get hash of current scoring formula."""
    if compute_score is None:
        return "no-formula"
    
    # Get source code of compute_score function
    formula_code = inspect.getsource(compute_score)
    
    # Add band mapping to hash
    if BAND_MAP:
        formula_code += str(BAND_MAP)
    
    return calculate_formula_hash(formula_code)

def store_formula_hash(hash_value: str) -> None:
    """Store formula hash to file."""
    FORMULA_HASH_FILE.parent.mkdir(exist_ok=True)
    with open(FORMULA_HASH_FILE, 'w') as f:
        json.dump({
            "hash": hash_value,
            "timestamp": str(Path.now()) if hasattr(Path, 'now') else "unknown"
        }, f)

def load_stored_hash() -> Optional[str]:
    """Load stored formula hash."""
    if not FORMULA_HASH_FILE.exists():
        return None
    
    try:
        with open(FORMULA_HASH_FILE, 'r') as f:
            data = json.load(f)
            return data.get('hash')
    except (json.JSONDecodeError, KeyError):
        return None

def validate_formula_integrity() -> tuple[bool, Optional[str]]:
    """Validate formula hasn't changed without authorization.
    
    Returns (is_valid, error_message)
    """
    current_hash = get_current_formula_hash()
    stored_hash = load_stored_hash()
    
    if stored_hash is None:
        # First run, store current hash
        store_formula_hash(current_hash)
        return True, None
    
    if current_hash != stored_hash:
        return False, f"Formula hash mismatch: {current_hash[:8]} != {stored_hash[:8]}"
    
    return True, None
