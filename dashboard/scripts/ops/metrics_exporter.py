#!/usr/bin/env python3
"""
Operational metrics exporter for wellness dashboard.
Collects and exports key metrics for monitoring and alerting.
"""

import json
import os
import sys
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from pathlib import Path

# Add dashboard to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from dashboard.config import Config
from dashboard.scripts.phase3.integrity_monitor import calculate_integrity_failure_rate, load_telemetry_records
from dashboard.scripts.phase3.auto_run_tracker import calculate_success_rate
# Note: completeness metrics are handled within completeness_monitor when needed.
# No direct import required here to avoid tight coupling.


class MetricsCollector:
    """Collects operational metrics from various sources."""
    
    def __init__(self, data_dir: str = None):
        """Initialize metrics collector."""
        self.data_dir = data_dir or os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
            'data'
        )
        self.metrics_file = os.path.join(self.data_dir, 'ops_metrics.json')
        self.timestamp = datetime.now()
    
    def collect_integrity_metrics(self, days: int = 14) -> Dict:
        """Collect integrity monitoring metrics."""
        try:
            # Find most recent telemetry file
            telemetry_files = sorted(Path(self.data_dir).glob('telemetry_*.jsonl'))
            if not telemetry_files:
                telemetry_files = sorted(Path(self.data_dir).glob('*.jsonl'))
            
            if not telemetry_files:
                return {
                    'status': 'no_data',
                    'failure_rate_pct': 0,
                    'records_checked': 0
                }
            
            latest_file = str(telemetry_files[-1])
            records = load_telemetry_records(latest_file)
            
            # Calculate metrics for different windows
            result_7d = calculate_integrity_failure_rate(records, 7)
            result_14d = calculate_integrity_failure_rate(records, 14)
            result_30d = calculate_integrity_failure_rate(records, 30)
            
            return {
                'status': 'ok',
                'failure_rate_7d_pct': result_7d['failure_rate_pct'],
                'failure_rate_14d_pct': result_14d['failure_rate_pct'],
                'failure_rate_30d_pct': result_30d['failure_rate_pct'],
                'records_checked': result_14d['total_records'],
                'failed_records': result_14d['failed_records'],
                'alert_triggered': result_14d['alert'],
                'threshold_pct': Config.INTEGRITY_FAILURE_THRESHOLD_PCT
            }
        except Exception as e:
            return {
                'status': 'error',
                'error': str(e),
                'failure_rate_pct': 0,
                'records_checked': 0
            }
    
    def collect_auto_run_metrics(self, days: int = 14) -> Dict:
        """Collect auto-run success metrics."""
        try:
            # Load records
            telemetry_files = sorted(Path(self.data_dir).glob('*.jsonl'))
            all_records = []
            
            for file_path in telemetry_files:
                with open(file_path, 'r') as f:
                    for line in f:
                        if line.strip():
                            try:
                                record = json.loads(line)
                                all_records.append(record)
                            except json.JSONDecodeError:
                                continue
            
            if not all_records:
                return {
                    'status': 'no_data',
                    'success_rate_pct': 0,
                    'distinct_days': 0
                }
            
            # Calculate success rate
            success_rate = calculate_success_rate(all_records, days)
            
            # Count distinct days
            dates_with_auto = set()
            all_dates = set()
            for record in all_records:
                date = record.get('date')
                if date:
                    all_dates.add(date)
                    if record.get('auto_run') == 1:
                        dates_with_auto.add(date)
            
            return {
                'status': 'ok',
                'success_rate_pct': success_rate,
                'distinct_days_with_auto': len(dates_with_auto),
                'total_distinct_days': len(all_dates),
                'target_pct': Config.AUTO_RUN_SUCCESS_TARGET_PCT,
                'meets_target': success_rate >= Config.AUTO_RUN_SUCCESS_TARGET_PCT
            }
        except Exception as e:
            return {
                'status': 'error',
                'error': str(e),
                'success_rate_pct': 0,
                'distinct_days': 0
            }
    
    def collect_remediation_metrics(self) -> Dict:
        """Collect remediation activity metrics."""
        try:
            # Check for remediation logs
            remediation_log = os.path.join(self.data_dir, 'remediation_log.json')
            
            if os.path.exists(remediation_log):
                with open(remediation_log, 'r') as f:
                    log_data = json.load(f)
                
                # Count recent remediations (last 7 days)
                recent_count = 0
                week_ago = datetime.now() - timedelta(days=7)
                
                for entry in log_data.get('remediations', []):
                    timestamp = datetime.fromisoformat(entry.get('timestamp', ''))
                    if timestamp >= week_ago:
                        recent_count += 1
                
                return {
                    'status': 'ok',
                    'total_remediations': len(log_data.get('remediations', [])),
                    'recent_remediations_7d': recent_count,
                    'last_remediation': log_data.get('last_remediation'),
                    'quarantine_enabled': Config.QUARANTINE_ENABLED
                }
            else:
                return {
                    'status': 'no_history',
                    'total_remediations': 0,
                    'recent_remediations_7d': 0,
                    'quarantine_enabled': Config.QUARANTINE_ENABLED
                }
        except Exception as e:
            return {
                'status': 'error',
                'error': str(e),
                'total_remediations': 0
            }
    
    def collect_ingestion_metrics(self) -> Dict:
        """Collect data ingestion metrics."""
        try:
            # Check for recent ingestion
            jsonl_files = sorted(Path(self.data_dir).glob('*.jsonl'))
            
            if not jsonl_files:
                return {
                    'status': 'no_data',
                    'total_files': 0,
                    'total_records': 0
                }
            
            total_records = 0
            latest_date = None
            oldest_date = None
            
            for file_path in jsonl_files:
                with open(file_path, 'r') as f:
                    for line in f:
                        if line.strip():
                            try:
                                record = json.loads(line)
                                total_records += 1
                                date = record.get('date')
                                if date:
                                    if latest_date is None or date > latest_date:
                                        latest_date = date
                                    if oldest_date is None or date < oldest_date:
                                        oldest_date = date
                            except json.JSONDecodeError:
                                continue
            
            # Check if ingestion is current
            if latest_date:
                latest = datetime.strptime(latest_date, '%Y-%m-%d')
                days_behind = (datetime.now() - latest).days
                is_current = days_behind <= 1
            else:
                days_behind = -1
                is_current = False
            
            return {
                'status': 'ok',
                'total_files': len(jsonl_files),
                'total_records': total_records,
                'latest_date': latest_date,
                'oldest_date': oldest_date,
                'days_behind': days_behind,
                'is_current': is_current
            }
        except Exception as e:
            return {
                'status': 'error',
                'error': str(e),
                'total_files': 0,
                'total_records': 0
            }
    
    def collect_plan_metrics(self) -> Dict:
        """Collect Phase 5 plan engine metrics."""
        try:
            plan_file = os.path.join(self.data_dir, 'plan_daily.jsonl')
            adherence_file = os.path.join(self.data_dir, 'adherence_daily.jsonl')
            
            # Count plans generated
            plans_generated = 0
            plans_skipped_missing_data = 0
            if os.path.exists(plan_file):
                with open(plan_file, 'r') as f:
                    for line in f:
                        if line.strip():
                            try:
                                plan = json.loads(line)
                                plans_generated += 1
                                if 'conservative' in plan.get('plan_text', '').lower():
                                    plans_skipped_missing_data += 1
                            except json.JSONDecodeError:
                                continue
            
            # Count adherence logged
            adherence_logged = 0
            avg_adherence_pct = 0
            avg_energy = 0
            if os.path.exists(adherence_file):
                adherence_records = []
                with open(adherence_file, 'r') as f:
                    for line in f:
                        if line.strip():
                            try:
                                record = json.loads(line)
                                adherence_records.append(record)
                                adherence_logged += 1
                            except json.JSONDecodeError:
                                continue
                
                if adherence_records:
                    total_adherence = sum(r.get('adherence_pct', 0) for r in adherence_records)
                    avg_adherence_pct = round(total_adherence / len(adherence_records), 1)
                    
                    energy_ratings = [r.get('energy_rating') for r in adherence_records if r.get('energy_rating')]
                    if energy_ratings:
                        avg_energy = round(sum(energy_ratings) / len(energy_ratings), 1)
            
            return {
                'status': 'ok',
                'plans_generated': plans_generated,
                'plans_skipped_missing_data': plans_skipped_missing_data,
                'adherence_logged': adherence_logged,
                'avg_adherence_pct': avg_adherence_pct,
                'avg_energy_rating': avg_energy,
                'enabled': Config.ENABLE_PLAN_ENGINE
            }
        except Exception as e:
            return {
                'status': 'error',
                'error': str(e),
                'plans_generated': 0,
                'adherence_logged': 0,
                'enabled': Config.ENABLE_PLAN_ENGINE
            }
    
    def collect_all_metrics(self) -> Dict:
        """Collect all operational metrics."""
        metrics = {
            'timestamp': self.timestamp.isoformat(),
            'integrity': self.collect_integrity_metrics(),
            'auto_run': self.collect_auto_run_metrics(),
            'remediation': self.collect_remediation_metrics(),
            'ingestion': self.collect_ingestion_metrics(),
            'config': {
                'integrity_threshold_pct': Config.INTEGRITY_FAILURE_THRESHOLD_PCT,
                'auto_run_target_pct': Config.AUTO_RUN_SUCCESS_TARGET_PCT,
                'retention_days': Config.RETENTION_DAYS,
                'battery_min_pct': Config.BATTERY_MIN_PERCENT,
                'quarantine_enabled': Config.QUARANTINE_ENABLED
            }
        }
        
        # Add Phase 5 plan metrics if enabled
        if Config.ENABLE_PLAN_ENGINE:
            metrics['plan_engine'] = self.collect_plan_metrics()
        
        return metrics
    
    def export_metrics(self, format: str = 'json') -> str:
        """Export metrics in specified format."""
        metrics = self.collect_all_metrics()
        
        if format == 'json':
            return json.dumps(metrics, indent=2)
        
        elif format == 'prometheus':
            # Convert to Prometheus format
            lines = []
            lines.append(f'# HELP wellness_integrity_failure_rate_pct Integrity failure rate percentage')
            lines.append(f'# TYPE wellness_integrity_failure_rate_pct gauge')
            lines.append(f'wellness_integrity_failure_rate_pct{{window="7d"}} {metrics["integrity"]["failure_rate_7d_pct"]}')
            lines.append(f'wellness_integrity_failure_rate_pct{{window="14d"}} {metrics["integrity"]["failure_rate_14d_pct"]}')
            lines.append(f'wellness_integrity_failure_rate_pct{{window="30d"}} {metrics["integrity"]["failure_rate_30d_pct"]}')
            
            lines.append(f'# HELP wellness_auto_run_success_rate_pct Auto-run success rate percentage')
            lines.append(f'# TYPE wellness_auto_run_success_rate_pct gauge')
            lines.append(f'wellness_auto_run_success_rate_pct {metrics["auto_run"]["success_rate_pct"]}')
            
            lines.append(f'# HELP wellness_remediation_count_total Total remediation count')
            lines.append(f'# TYPE wellness_remediation_count_total counter')
            lines.append(f'wellness_remediation_count_total {metrics["remediation"]["total_remediations"]}')
            
            lines.append(f'# HELP wellness_ingestion_records_total Total ingested records')
            lines.append(f'# TYPE wellness_ingestion_records_total counter')
            lines.append(f'wellness_ingestion_records_total {metrics["ingestion"]["total_records"]}')
            
            lines.append(f'# HELP wellness_ingestion_days_behind Days behind in data ingestion')
            lines.append(f'# TYPE wellness_ingestion_days_behind gauge')
            lines.append(f'wellness_ingestion_days_behind {metrics["ingestion"].get("days_behind", -1)}')
            
            return '\n'.join(lines)
        
        else:
            raise ValueError(f"Unsupported format: {format}")
    
    def save_metrics(self):
        """Save metrics to file."""
        metrics = self.collect_all_metrics()
        
        # Save to JSON file
        with open(self.metrics_file, 'w') as f:
            json.dump(metrics, f, indent=2)
        
        # Also append to metrics history
        history_file = os.path.join(self.data_dir, 'metrics_history.jsonl')
        with open(history_file, 'a') as f:
            f.write(json.dumps(metrics) + '\n')
        
        return metrics


def main():
    """CLI interface for metrics export."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Export operational metrics')
    parser.add_argument('--format', choices=['json', 'prometheus'], default='json',
                       help='Output format')
    parser.add_argument('--save', action='store_true',
                       help='Save metrics to file')
    parser.add_argument('--data-dir', help='Data directory')
    
    args = parser.parse_args()
    
    # Create collector
    collector = MetricsCollector(data_dir=args.data_dir)
    
    # Export metrics
    output = collector.export_metrics(format=args.format)
    print(output)
    
    # Save if requested
    if args.save:
        metrics = collector.save_metrics()
        print(f"\n📊 Metrics saved to {collector.metrics_file}", file=sys.stderr)
        
        # Print summary
        print(f"\n📈 Summary:", file=sys.stderr)
        print(f"  Integrity: {metrics['integrity']['failure_rate_14d_pct']}% failure rate", file=sys.stderr)
        print(f"  Auto-run: {metrics['auto_run']['success_rate_pct']}% success rate", file=sys.stderr)
        print(f"  Ingestion: {metrics['ingestion']['total_records']} records", file=sys.stderr)
    
    return 0


if __name__ == '__main__':
    sys.exit(main())