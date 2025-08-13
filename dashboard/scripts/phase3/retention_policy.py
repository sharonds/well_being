#!/usr/bin/env python3
"""
Retention policy for telemetry and quarantine data.
Prevents unbounded disk usage by pruning old files.
"""

import os
import sys
import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Tuple

# Add dashboard to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from config import Config


class RetentionManager:
    """Manages data retention policies for telemetry and quarantine files."""
    
    def __init__(self, retention_days: int = None):
        """
        Initialize retention manager.
        
        Args:
            retention_days: Days to retain data (default from Config)
        """
        self.retention_days = retention_days or getattr(Config, 'RETENTION_DAYS', 30)
        self.cutoff_date = datetime.now() - timedelta(days=self.retention_days)
    
    def get_file_age_days(self, file_path: str) -> int:
        """
        Get age of file in days based on modification time.
        
        Args:
            file_path: Path to file
            
        Returns:
            Age in days
        """
        try:
            mtime = os.path.getmtime(file_path)
            file_date = datetime.fromtimestamp(mtime)
            age = datetime.now() - file_date
            return age.days
        except Exception:
            return 0
    
    def get_jsonl_date_range(self, file_path: str) -> Tuple[datetime, datetime]:
        """
        Get date range of records in JSONL file.
        
        Args:
            file_path: Path to JSONL file
            
        Returns:
            Tuple of (oldest_date, newest_date)
        """
        oldest = None
        newest = None
        
        try:
            with open(file_path, 'r') as f:
                for line in f:
                    if line.strip():
                        try:
                            record = json.loads(line)
                            date_str = record.get('date')
                            if date_str:
                                date = datetime.strptime(date_str, '%Y-%m-%d')
                                if oldest is None or date < oldest:
                                    oldest = date
                                if newest is None or date > newest:
                                    newest = date
                        except (json.JSONDecodeError, ValueError):
                            continue
        except Exception:
            pass
        
        return oldest, newest
    
    def prune_jsonl_file(self, file_path: str, dry_run: bool = False) -> Dict:
        """
        Prune old records from JSONL file.
        
        Args:
            file_path: Path to JSONL file
            dry_run: If True, only report what would be done
            
        Returns:
            Pruning statistics
        """
        stats = {
            'file': file_path,
            'total_records': 0,
            'kept_records': 0,
            'pruned_records': 0,
            'error': None
        }
        
        if not os.path.exists(file_path):
            stats['error'] = 'File not found'
            return stats
        
        try:
            kept_records = []
            pruned_records = []
            
            with open(file_path, 'r') as f:
                for line in f:
                    if line.strip():
                        try:
                            record = json.loads(line)
                            stats['total_records'] += 1
                            
                            # Check record date
                            date_str = record.get('date')
                            if date_str:
                                record_date = datetime.strptime(date_str, '%Y-%m-%d')
                                if record_date >= self.cutoff_date:
                                    kept_records.append(record)
                                else:
                                    pruned_records.append(record)
                            else:
                                # Keep records without dates
                                kept_records.append(record)
                        except (json.JSONDecodeError, ValueError):
                            # Keep malformed records (don't lose data)
                            kept_records.append({'raw': line.strip()})
            
            stats['kept_records'] = len(kept_records)
            stats['pruned_records'] = len(pruned_records)
            
            # Write back if not dry run and there are changes
            if not dry_run and stats['pruned_records'] > 0:
                from utils.file_utils import atomic_write_jsonl
                if not atomic_write_jsonl(kept_records, file_path):
                    stats['error'] = 'Failed to write pruned file'
            
        except Exception as e:
            stats['error'] = str(e)
        
        return stats
    
    def prune_old_files(self, directory: str, pattern: str = '*.jsonl', 
                       dry_run: bool = False) -> List[Dict]:
        """
        Prune old files from directory based on modification time.
        
        Args:
            directory: Directory to scan
            pattern: File pattern to match
            dry_run: If True, only report what would be done
            
        Returns:
            List of pruning actions
        """
        actions = []
        
        if not os.path.exists(directory):
            return actions
        
        path = Path(directory)
        for file_path in path.glob(pattern):
            age_days = self.get_file_age_days(file_path)
            
            if age_days > self.retention_days:
                action = {
                    'file': str(file_path),
                    'age_days': age_days,
                    'action': 'delete',
                    'executed': False
                }
                
                if not dry_run:
                    try:
                        os.unlink(file_path)
                        action['executed'] = True
                    except Exception as e:
                        action['error'] = str(e)
                
                actions.append(action)
        
        return actions
    
    def apply_retention_policy(self, telemetry_dir: str = None, 
                              quarantine_dir: str = None,
                              dry_run: bool = False) -> Dict:
        """
        Apply retention policy to telemetry and quarantine directories.
        
        Args:
            telemetry_dir: Telemetry directory (default: dashboard/data)
            quarantine_dir: Quarantine directory (default: dashboard/data/quarantine)
            dry_run: If True, only report what would be done
            
        Returns:
            Retention report
        """
        report = {
            'timestamp': datetime.now().isoformat(),
            'retention_days': self.retention_days,
            'cutoff_date': self.cutoff_date.isoformat(),
            'dry_run': dry_run,
            'telemetry': {},
            'quarantine': {}
        }
        
        # Default directories
        if telemetry_dir is None:
            telemetry_dir = os.path.join(
                os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
                'data'
            )
        
        if quarantine_dir is None:
            quarantine_dir = os.path.join(telemetry_dir, 'quarantine')
        
        # Process telemetry files
        if os.path.exists(telemetry_dir):
            telemetry_files = list(Path(telemetry_dir).glob('telemetry_*.jsonl'))
            report['telemetry']['files_scanned'] = len(telemetry_files)
            report['telemetry']['files_pruned'] = []
            
            for file_path in telemetry_files:
                stats = self.prune_jsonl_file(str(file_path), dry_run)
                if stats['pruned_records'] > 0:
                    report['telemetry']['files_pruned'].append(stats)
        
        # Process quarantine directory (delete old files entirely)
        if os.path.exists(quarantine_dir):
            quarantine_actions = self.prune_old_files(quarantine_dir, '*.jsonl', dry_run)
            report['quarantine']['files_deleted'] = len([a for a in quarantine_actions if a.get('executed', True)])
            report['quarantine']['actions'] = quarantine_actions
        
        return report


def main():
    """CLI interface for retention policy."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Apply data retention policy')
    parser.add_argument('--days', type=int, help='Days to retain (default from Config)')
    parser.add_argument('--telemetry-dir', help='Telemetry directory')
    parser.add_argument('--quarantine-dir', help='Quarantine directory')
    parser.add_argument('--dry-run', action='store_true', help='Show what would be done without making changes')
    parser.add_argument('--json', action='store_true', help='Output as JSON')
    
    args = parser.parse_args()
    
    # Create retention manager
    manager = RetentionManager(retention_days=args.days)
    
    # Apply retention policy
    report = manager.apply_retention_policy(
        telemetry_dir=args.telemetry_dir,
        quarantine_dir=args.quarantine_dir,
        dry_run=args.dry_run
    )
    
    if args.json:
        print(json.dumps(report, indent=2))
    else:
        print(f"📅 Retention Policy Report")
        print(f"   Retention: {report['retention_days']} days")
        print(f"   Cutoff: {report['cutoff_date']}")
        print(f"   Mode: {'DRY RUN' if report['dry_run'] else 'APPLIED'}")
        
        # Telemetry summary
        tel = report['telemetry']
        if 'files_scanned' in tel:
            print(f"\n📊 Telemetry:")
            print(f"   Files scanned: {tel['files_scanned']}")
            print(f"   Files with pruned records: {len(tel.get('files_pruned', []))}")
            
            total_pruned = sum(f['pruned_records'] for f in tel.get('files_pruned', []))
            if total_pruned > 0:
                print(f"   Total records pruned: {total_pruned}")
        
        # Quarantine summary
        quar = report['quarantine']
        if 'files_deleted' in quar:
            print(f"\n🔒 Quarantine:")
            print(f"   Files deleted: {quar['files_deleted']}")
        
        if report['dry_run']:
            print(f"\n💡 This was a dry run. Use without --dry-run to apply changes.")
    
    return 0


if __name__ == '__main__':
    sys.exit(main())