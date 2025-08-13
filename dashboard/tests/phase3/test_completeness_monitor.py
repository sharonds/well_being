"""Tests for AC7: Completeness delta monitoring."""
import json
import sys
import tempfile
from datetime import datetime, timedelta
sys.path.insert(0, '.')

from scripts.phase3.completeness_monitor import (
    calculate_completeness_pct,
    filter_records_by_days,
    calculate_avg_completeness,
    check_completeness_regression,
    generate_completeness_report
)

def create_test_record(date: str, metrics_mask: int = 15, completeness_pct: float = None):
    """Create a test telemetry record."""
    record = {
        'date': date,
        'score': 65,
        'band': 'Maintain',
        'metrics_mask': metrics_mask,
        'auto_run': 1
    }
    if completeness_pct is not None:
        record['completeness_pct'] = completeness_pct
    return record

def test_calculate_completeness_from_mask():
    """Test completeness calculation from metrics_mask."""
    # All metrics present (mask = 15 = 1111 binary)
    record = create_test_record('2025-08-01', metrics_mask=15)
    assert calculate_completeness_pct(record) == 100.0
    
    # 3 metrics present (mask = 14 = 1110 binary)
    record = create_test_record('2025-08-01', metrics_mask=14)
    assert calculate_completeness_pct(record) == 75.0
    
    # 1 metric present (mask = 1 = 0001 binary)
    record = create_test_record('2025-08-01', metrics_mask=1)
    assert calculate_completeness_pct(record) == 25.0
    
    # No metrics present (mask = 0)
    record = create_test_record('2025-08-01', metrics_mask=0)
    assert calculate_completeness_pct(record) == 0.0

def test_calculate_completeness_from_field():
    """Test completeness calculation from explicit field."""
    record = create_test_record('2025-08-01', completeness_pct=78.5)
    assert calculate_completeness_pct(record) == 78.5

def test_filter_records_by_days():
    """Test filtering records by date range."""
    today = datetime.now()
    records = [
        create_test_record((today - timedelta(days=1)).strftime('%Y-%m-%d')),  # 1 day ago
        create_test_record((today - timedelta(days=5)).strftime('%Y-%m-%d')),  # 5 days ago
        create_test_record((today - timedelta(days=10)).strftime('%Y-%m-%d')), # 10 days ago
        create_test_record((today - timedelta(days=20)).strftime('%Y-%m-%d')), # 20 days ago
    ]
    
    # Filter to last 7 days
    filtered_7d = filter_records_by_days(records, 7)
    assert len(filtered_7d) == 2  # Only first 2 records within 7 days
    
    # Filter to last 15 days
    filtered_15d = filter_records_by_days(records, 15)
    assert len(filtered_15d) == 3  # First 3 records within 15 days

def test_calculate_avg_completeness():
    """Test average completeness calculation."""
    records = [
        create_test_record('2025-08-01', completeness_pct=100.0),
        create_test_record('2025-08-02', completeness_pct=75.0),
        create_test_record('2025-08-03', completeness_pct=50.0),
    ]
    
    avg = calculate_avg_completeness(records)
    assert avg == 75.0  # (100 + 75 + 50) / 3

def test_no_regression_scenario():
    """Test scenario with no completeness regression."""
    # Create records with stable completeness
    today = datetime.now()
    records = []
    
    # Last 7 days: 100% completeness
    for i in range(7):
        date = (today - timedelta(days=i+1)).strftime('%Y-%m-%d')
        records.append(create_test_record(date, completeness_pct=100.0))
    
    # Days 8-30: 90% completeness
    for i in range(7, 30):
        date = (today - timedelta(days=i+1)).strftime('%Y-%m-%d')
        records.append(create_test_record(date, completeness_pct=90.0))
    
    result = check_completeness_regression(records, threshold_pct=20.0)
    
    assert result['alert'] == False
    assert result['avg_7d'] == 100.0
    assert abs(result['avg_30d'] - 92.3) < 0.1  # Allow for rounding (7*100 + 23*90) / 30

def test_regression_scenario():
    """Test scenario with completeness regression triggering alert."""
    today = datetime.now()
    records = []
    
    # Last 7 days: 50% completeness (poor recent data)
    for i in range(7):
        date = (today - timedelta(days=i+1)).strftime('%Y-%m-%d')
        records.append(create_test_record(date, completeness_pct=50.0))
    
    # Days 8-30: 90% completeness (good historical data)
    for i in range(7, 30):
        date = (today - timedelta(days=i+1)).strftime('%Y-%m-%d')
        records.append(create_test_record(date, completeness_pct=90.0))
    
    result = check_completeness_regression(records, threshold_pct=20.0)
    
    assert result['alert'] == True  # Should trigger alert
    assert result['avg_7d'] == 50.0
    assert result['avg_30d'] > 80.0  # Should be around 83.33
    assert result['drop_percentage'] > 30.0  # Significant drop

def test_generate_report():
    """Test full report generation."""
    # Create temporary test file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.jsonl', delete=False) as f:
        # Write test records
        records = [
            create_test_record('2025-08-01', completeness_pct=100.0),
            create_test_record('2025-08-02', completeness_pct=75.0),
            create_test_record('2025-08-03', completeness_pct=80.0),
        ]
        for record in records:
            f.write(json.dumps(record) + '\n')
        temp_file = f.name
    
    try:
        report = generate_completeness_report(temp_file)
        
        assert 'timestamp' in report
        assert report['total_records'] == 3
        assert 'regression_check' in report
        assert 'overall_stats' in report
        assert report['overall_stats']['avg_completeness'] == 85.0  # (100+75+80)/3
    finally:
        # Clean up
        import os
        os.unlink(temp_file)

def test_edge_cases():
    """Test edge cases and boundary conditions."""
    # Empty records
    result = check_completeness_regression([], threshold_pct=20.0)
    assert result['alert'] == False
    assert result['avg_7d'] == 0.0
    assert result['avg_30d'] == 0.0
    
    # Single record (from a week ago, so it won't be in 7-day filter)
    from datetime import datetime, timedelta
    week_ago = (datetime.now() - timedelta(days=8)).strftime('%Y-%m-%d')
    records = [create_test_record(week_ago, completeness_pct=75.0)]
    result = check_completeness_regression(records, threshold_pct=20.0)
    assert result['alert'] == False  # No regression when 7d is empty
    assert result['avg_7d'] == 0.0   # No records in last 7 days
    assert result['avg_30d'] == 75.0  # But record is in 30-day window