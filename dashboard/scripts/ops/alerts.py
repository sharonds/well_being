#!/usr/bin/env python3
"""
Alerting system for operational metrics.
Sends alerts when thresholds are breached.
"""

import json
import os
import sys
import urllib.request
import urllib.parse
from datetime import datetime
from typing import Dict, List, Optional

# Add dashboard to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from dashboard.config import Config
from dashboard.scripts.ops.metrics_exporter import MetricsCollector


class AlertManager:
    """Manages alert generation and delivery."""
    
    def __init__(self, webhook_url: str = None, dry_run: bool = False):
        """
        Initialize alert manager.
        
        Args:
            webhook_url: Slack webhook URL (from environment if not provided)
            dry_run: If True, don't actually send alerts
        """
        self.webhook_url = webhook_url or os.getenv('SLACK_WEBHOOK_URL')
        self.dry_run = dry_run
        self.alerts_sent = []
    
    def check_integrity_threshold(self, metrics: Dict) -> Optional[Dict]:
        """Check if integrity failure rate exceeds threshold."""
        integrity = metrics.get('integrity', {})
        failure_rate = integrity.get('failure_rate_14d_pct', 0)
        threshold = Config.INTEGRITY_FAILURE_THRESHOLD_PCT
        
        if integrity.get('alert_triggered', False):
            return {
                'type': 'integrity_breach',
                'severity': 'critical',
                'title': '🚨 Integrity Failure Rate Exceeded',
                'message': f'Integrity failure rate is {failure_rate}% (threshold: {threshold}%)',
                'details': {
                    'failure_rate_7d': integrity.get('failure_rate_7d_pct', 0),
                    'failure_rate_14d': failure_rate,
                    'failure_rate_30d': integrity.get('failure_rate_30d_pct', 0),
                    'failed_records': integrity.get('failed_records', 0),
                    'total_records': integrity.get('records_checked', 0)
                },
                'runbook': 'docs/runbooks/integrity-failures.md'
            }
        return None
    
    def check_auto_run_target(self, metrics: Dict) -> Optional[Dict]:
        """Check if auto-run success rate meets target."""
        auto_run = metrics.get('auto_run', {})
        success_rate = auto_run.get('success_rate_pct', 0)
        target = Config.AUTO_RUN_SUCCESS_TARGET_PCT
        
        if not auto_run.get('meets_target', True):
            return {
                'type': 'auto_run_below_target',
                'severity': 'warning',
                'title': '⚠️ Auto-run Success Rate Below Target',
                'message': f'Auto-run success rate is {success_rate}% (target: {target}%)',
                'details': {
                    'success_rate': success_rate,
                    'target': target,
                    'distinct_days_with_auto': auto_run.get('distinct_days_with_auto', 0),
                    'total_distinct_days': auto_run.get('total_distinct_days', 0)
                },
                'runbook': 'docs/runbooks/auto-run-failures.md'
            }
        return None
    
    def check_ingestion_status(self, metrics: Dict) -> Optional[Dict]:
        """Check if data ingestion is current."""
        ingestion = metrics.get('ingestion', {})
        days_behind = ingestion.get('days_behind', 0)
        
        if days_behind > 2:
            return {
                'type': 'ingestion_stale',
                'severity': 'critical' if days_behind > 7 else 'warning',
                'title': '🔄 Data Ingestion Stale',
                'message': f'Data ingestion is {days_behind} days behind',
                'details': {
                    'latest_date': ingestion.get('latest_date'),
                    'days_behind': days_behind,
                    'total_records': ingestion.get('total_records', 0)
                },
                'runbook': 'docs/runbooks/ingestion-failures.md'
            }
        return None
    
    def check_recent_remediations(self, metrics: Dict) -> Optional[Dict]:
        """Check if there have been many recent remediations."""
        remediation = metrics.get('remediation', {})
        recent_count = remediation.get('recent_remediations_7d', 0)
        
        if recent_count > 10:  # More than 10 remediations in a week is concerning
            return {
                'type': 'high_remediation_rate',
                'severity': 'warning',
                'title': '🔧 High Remediation Activity',
                'message': f'{recent_count} remediations in the last 7 days',
                'details': {
                    'recent_remediations_7d': recent_count,
                    'total_remediations': remediation.get('total_remediations', 0),
                    'last_remediation': remediation.get('last_remediation')
                },
                'runbook': 'docs/runbooks/remediation-activity.md'
            }
        return None
    
    def check_daily_plan_status(self, metrics: Dict) -> Optional[Dict]:
        """Check if daily plan was generated (soft warning)."""
        # Only check if Plan Engine is enabled
        if not Config.ENABLE_PLAN_ENGINE:
            return None
            
        plan_engine = metrics.get('plan_engine', {})
        
        # Check if we have today's plan
        from datetime import date
        import os
        import json
        
        plan_file = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
            'data', 'plan_daily.jsonl'
        )
        
        has_todays_plan = False
        if os.path.exists(plan_file):
            today = date.today().isoformat()
            with open(plan_file, 'r') as f:
                for line in f:
                    try:
                        plan = json.loads(line.strip())
                        if plan.get('date') == today:
                            has_todays_plan = True
                            break
                    except json.JSONDecodeError:
                        continue
        
        if not has_todays_plan:
            return {
                'type': 'missing_daily_plan',
                'severity': 'info',  # Soft warning
                'title': '📋 No Daily Plan Generated',
                'message': f"Today's training plan has not been generated yet",
                'details': {
                    'date': date.today().isoformat(),
                    'plans_generated_total': plan_engine.get('plans_generated', 0),
                    'enabled': Config.ENABLE_PLAN_ENGINE
                },
                'runbook': 'Run: python3 dashboard/scripts/plan_engine.py'
            }
        return None
    
    def generate_alerts(self, metrics: Dict) -> List[Dict]:
        """Generate alerts based on metrics."""
        alerts = []
        
        # Check each threshold
        alert = self.check_integrity_threshold(metrics)
        if alert:
            alerts.append(alert)
        
        alert = self.check_auto_run_target(metrics)
        if alert:
            alerts.append(alert)
        
        alert = self.check_ingestion_status(metrics)
        if alert:
            alerts.append(alert)
        
        alert = self.check_recent_remediations(metrics)
        if alert:
            alerts.append(alert)
        
        # Check Phase 5 plan status (soft warning)
        alert = self.check_daily_plan_status(metrics)
        if alert:
            alerts.append(alert)
        
        return alerts
    
    def format_slack_message(self, alert: Dict) -> Dict:
        """Format alert for Slack."""
        color = {
            'critical': 'danger',
            'warning': 'warning',
            'info': 'good'
        }.get(alert['severity'], 'warning')
        
        fields = []
        for key, value in alert.get('details', {}).items():
            fields.append({
                'title': key.replace('_', ' ').title(),
                'value': str(value),
                'short': True
            })
        
        attachment = {
            'color': color,
            'title': alert['title'],
            'text': alert['message'],
            'fields': fields,
            'footer': f"Runbook: {alert.get('runbook', 'N/A')}",
            'ts': int(datetime.now().timestamp())
        }
        
        return {
            'text': alert['title'],
            'attachments': [attachment]
        }
    
    def send_slack_alert(self, alert: Dict) -> bool:
        """Send alert to Slack."""
        if self.dry_run:
            print(f"[DRY RUN] Would send alert: {alert['title']}")
            return True
        
        if not self.webhook_url:
            print(f"❌ No Slack webhook URL configured")
            return False
        
        try:
            message = self.format_slack_message(alert)
            data = json.dumps(message).encode('utf-8')
            
            req = urllib.request.Request(
                self.webhook_url,
                data=data,
                headers={'Content-Type': 'application/json'}
            )
            
            with urllib.request.urlopen(req) as response:
                if response.status == 200:
                    print(f"✅ Alert sent: {alert['title']}")
                    return True
                else:
                    print(f"❌ Failed to send alert: HTTP {response.status}")
                    return False
                    
        except Exception as e:
            print(f"❌ Error sending alert: {e}")
            return False
    
    def send_console_alert(self, alert: Dict):
        """Send alert to console (fallback)."""
        print(f"\n{'='*60}")
        print(f"{alert['severity'].upper()}: {alert['title']}")
        print(f"{alert['message']}")
        print(f"\nDetails:")
        for key, value in alert.get('details', {}).items():
            print(f"  {key}: {value}")
        print(f"\nRunbook: {alert.get('runbook', 'N/A')}")
        print(f"{'='*60}\n")
    
    def process_alerts(self, metrics: Dict) -> Dict:
        """Process and send all alerts."""
        alerts = self.generate_alerts(metrics)
        
        results = {
            'timestamp': datetime.now().isoformat(),
            'alerts_generated': len(alerts),
            'alerts_sent': 0,
            'alerts_failed': 0,
            'alerts': []
        }
        
        for alert in alerts:
            # Try Slack first
            if self.webhook_url:
                success = self.send_slack_alert(alert)
                if success:
                    results['alerts_sent'] += 1
                else:
                    results['alerts_failed'] += 1
            
            # Always send to console as backup
            self.send_console_alert(alert)
            
            # Record alert
            results['alerts'].append({
                'type': alert['type'],
                'severity': alert['severity'],
                'title': alert['title'],
                'timestamp': datetime.now().isoformat()
            })
        
        # Save alert history
        self.save_alert_history(results)
        
        return results
    
    def save_alert_history(self, results: Dict):
        """Save alert history to file."""
        history_file = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
            'data',
            'alert_history.jsonl'
        )
        
        try:
            with open(history_file, 'a') as f:
                f.write(json.dumps(results) + '\n')
        except Exception as e:
            print(f"⚠️ Failed to save alert history: {e}")


def main():
    """CLI interface for alerting."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Check metrics and send alerts')
    parser.add_argument('--webhook-url', help='Slack webhook URL')
    parser.add_argument('--dry-run', action='store_true',
                       help="Don't actually send alerts")
    parser.add_argument('--data-dir', help='Data directory')
    parser.add_argument('--test', action='store_true',
                       help='Send test alert')
    
    args = parser.parse_args()
    
    # Create alert manager
    manager = AlertManager(webhook_url=args.webhook_url, dry_run=args.dry_run)
    
    if args.test:
        # Send test alert
        test_alert = {
            'type': 'test',
            'severity': 'info',
            'title': '🧪 Test Alert',
            'message': 'This is a test alert to verify alerting is working',
            'details': {
                'timestamp': datetime.now().isoformat(),
                'dry_run': args.dry_run
            },
            'runbook': 'N/A'
        }
        
        if manager.webhook_url:
            success = manager.send_slack_alert(test_alert)
            print(f"Test alert {'sent' if success else 'failed'}")
        else:
            manager.send_console_alert(test_alert)
        
        return 0
    
    # Collect metrics
    collector = MetricsCollector(data_dir=args.data_dir)
    metrics = collector.collect_all_metrics()
    
    # Process alerts
    results = manager.process_alerts(metrics)
    
    # Print summary
    print(f"\n📊 Alert Summary:")
    print(f"  Generated: {results['alerts_generated']}")
    print(f"  Sent: {results['alerts_sent']}")
    print(f"  Failed: {results['alerts_failed']}")
    
    # Exit with error if critical alerts
    critical_count = sum(1 for a in results['alerts'] if a['severity'] == 'critical')
    return 1 if critical_count > 0 else 0


if __name__ == '__main__':
    sys.exit(main())