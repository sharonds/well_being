"""
Schema utilities for version normalization and validation.
Addresses duplicate guard vulnerability identified in ChatGPT-5 review.
"""

import re
from typing import Optional


def normalize_schema_version(version: Optional[str]) -> str:
    """
    Normalize schema version to consistent format.
    
    Addresses the duplicate guard vulnerability where different version formats
    (v1.0.0 vs 2.0.0) allow duplicate records for the same date.
    
    Args:
        version: Schema version string (e.g., "v1.0.0", "2.0.0", "1.0", etc.)
        
    Returns:
        Normalized version string in "major.minor.patch" format
        
    Examples:
        normalize_schema_version("v1.0.0") -> "1.0.0"
        normalize_schema_version("2.0.0") -> "2.0.0"  
        normalize_schema_version("1.0") -> "1.0.0"
        normalize_schema_version("v3") -> "3.0.0"
        normalize_schema_version(None) -> "0.0.0"
        normalize_schema_version("invalid") -> "0.0.0"
    """
    if not version:
        return "0.0.0"
    
    # Strip leading 'v' if present
    clean_version = version.lstrip('vV')
    
    # Match semantic version pattern (major.minor.patch)
    # Allow missing minor/patch components
    match = re.match(r'^(\d+)(?:\.(\d+))?(?:\.(\d+))?', clean_version)
    
    if not match:
        # Invalid format, return default
        return "0.0.0"
    
    major = match.group(1) or "0"
    minor = match.group(2) or "0" 
    patch = match.group(3) or "0"
    
    return f"{major}.{minor}.{patch}"


def compare_schema_versions(version1: str, version2: str) -> int:
    """
    Compare two normalized schema versions.
    
    Args:
        version1: First version string
        version2: Second version string
        
    Returns:
        -1 if version1 < version2
         0 if version1 == version2  
         1 if version1 > version2
    """
    v1_normalized = normalize_schema_version(version1)
    v2_normalized = normalize_schema_version(version2)
    
    v1_parts = [int(x) for x in v1_normalized.split('.')]
    v2_parts = [int(x) for x in v2_normalized.split('.')]
    
    if v1_parts < v2_parts:
        return -1
    elif v1_parts > v2_parts:
        return 1
    else:
        return 0


def is_compatible_schema_version(version: str, min_version: str = "1.0.0") -> bool:
    """
    Check if schema version is compatible with minimum required version.
    
    Args:
        version: Schema version to check
        min_version: Minimum required version
        
    Returns:
        True if version >= min_version
    """
    return compare_schema_versions(version, min_version) >= 0


if __name__ == '__main__':
    # Test normalization
    test_cases = [
        ("v1.0.0", "1.0.0"),
        ("2.0.0", "2.0.0"),
        ("v3", "3.0.0"),
        ("1.0", "1.0.0"),
        (None, "0.0.0"),
        ("invalid", "0.0.0"),
        ("V2.1.5", "2.1.5")
    ]
    
    print("Schema Version Normalization Tests:")
    for input_version, expected in test_cases:
        result = normalize_schema_version(input_version)
        status = "✅" if result == expected else "❌"
        print(f"{status} {input_version!r} -> {result} (expected {expected})")