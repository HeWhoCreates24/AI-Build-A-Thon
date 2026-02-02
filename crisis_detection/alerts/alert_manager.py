"""
Alert Manager Module
====================
Handles alert generation, logging, and notification.

Architecture:
- Creates structured alert payloads
- Saves evidence (screenshots, webcam, logs)
- Sends notifications (local log, dashboard, email)
- Maintains alert history

Data Flow:
  Risk Engine (Alert Trigger) → Alert Manager → Evidence Collection → Notification
"""

import json
import logging
from datetime import datetime
from pathlib import Path
import shutil

logger = logging.getLogger(__name__)


class AlertManager:
    """
    Manage crisis alerts and notifications.
    
    Responsibilities:
    - Generate alert payloads
    - Collect evidence (screenshots, webcam)
    - Save alert logs
    - Send notifications to admin
    - Maintain alert history
    """
    
    def __init__(self, config):
        """
        Args:
            config: Configuration with:
                - alert_log_dir: Directory for alert logs
                - evidence_dir: Directory for alert evidence
                - notification_methods: List of methods (log, file, email)
                - admin_email: Email for notifications (optional)
        """
        self.alert_log_dir = Path(config.get('alert_log_dir', 'data/logs/alerts'))
        self.evidence_dir = Path(config.get('evidence_dir', 'data/evidence'))
        self.notification_methods = config.get('notification_methods', ['log', 'file'])
        self.admin_email = config.get('admin_email')
        
        # Ensure directories exist
        self.alert_log_dir.mkdir(parents=True, exist_ok=True)
        self.evidence_dir.mkdir(parents=True, exist_ok=True)
        
        # Alert counter
        self.alert_counter = 0
    
    def trigger_alert(self, risk_score, window_stats, screenshot_paths, webcam_path):
        """
        Create and send an alert.
        
        Args:
            risk_score: Aggregated risk score that triggered alert
            window_stats: Statistics from risk engine
            screenshot_paths: List of recent screenshot paths
            webcam_path: Path to webcam capture
            
        Returns:
            dict: Alert payload
        """
        self.alert_counter += 1
        alert_id = f"ALERT_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{self.alert_counter}"
        
        # Build alert payload
        alert = {
            'alert_id': alert_id,
            'timestamp': datetime.now().isoformat(),
            'risk_score': risk_score,
            'window_stats': window_stats,
            'severity': self._determine_severity(risk_score),
            'evidence': {
                'screenshots': [],
                'webcam': None
            },
            'machine_info': self._get_machine_info(),
            'status': 'NEW'
        }
        
        # Collect evidence
        alert['evidence'] = self._collect_evidence(
            alert_id,
            screenshot_paths,
            webcam_path
        )
        
        # Save alert to disk
        self._save_alert(alert)
        
        # Send notifications
        self._send_notifications(alert)
        
        logger.critical(f"🚨 CRISIS ALERT TRIGGERED: {alert_id} (Risk: {risk_score:.3f})")
        
        return alert
    
    def _determine_severity(self, risk_score):
        """
        Map risk score to severity level.
        
        Args:
            risk_score: 0-1 risk score
            
        Returns:
            str: Severity level
        """
        if risk_score >= 0.85:
            return 'CRITICAL'
        elif risk_score >= 0.70:
            return 'HIGH'
        elif risk_score >= 0.55:
            return 'MEDIUM'
        else:
            return 'LOW'
    
    def _collect_evidence(self, alert_id, screenshot_paths, webcam_path):
        """
        Copy evidence files to alert-specific directory.
        
        Args:
            alert_id: Unique alert identifier
            screenshot_paths: Paths to screenshots
            webcam_path: Path to webcam image
            
        Returns:
            dict: Evidence file paths
        """
        # Create alert evidence directory
        alert_evidence_dir = self.evidence_dir / alert_id
        alert_evidence_dir.mkdir(exist_ok=True)
        
        evidence = {
            'screenshots': [],
            'webcam': None
        }
        
        # Copy screenshots
        for i, screenshot_path in enumerate(screenshot_paths[-5:]):  # Last 5 screenshots
            if Path(screenshot_path).exists():
                dest = alert_evidence_dir / f"screenshot_{i}.png"
                shutil.copy2(screenshot_path, dest)
                evidence['screenshots'].append(str(dest))
        
        # Copy webcam image
        if webcam_path and Path(webcam_path).exists():
            dest = alert_evidence_dir / "webcam.jpg"
            shutil.copy2(webcam_path, dest)
            evidence['webcam'] = str(dest)
        
        logger.info(f"Evidence collected: {len(evidence['screenshots'])} screenshots, webcam: {evidence['webcam'] is not None}")
        
        return evidence
    
    def _get_machine_info(self):
        """
        Get basic machine identification info.
        
        Returns:
            dict: Machine info
        """
        import socket
        import platform
        
        return {
            'hostname': socket.gethostname(),
            'platform': platform.system(),
            'platform_version': platform.version()
        }
    
    def _save_alert(self, alert):
        """
        Save alert to JSON file.
        
        Args:
            alert: Alert payload dict
        """
        alert_file = self.alert_log_dir / f"{alert['alert_id']}.json"
        
        with open(alert_file, 'w') as f:
            json.dump(alert, f, indent=2)
        
        logger.info(f"Alert saved: {alert_file}")
    
    def _send_notifications(self, alert):
        """
        Send alert through configured notification methods.
        
        Args:
            alert: Alert payload
        """
        for method in self.notification_methods:
            if method == 'log':
                self._notify_log(alert)
            elif method == 'file':
                self._notify_file(alert)
            elif method == 'email':
                self._notify_email(alert)
    
    def _notify_log(self, alert):
        """Log alert to system logger."""
        logger.critical(
            f"CRISIS ALERT: {alert['alert_id']} | "
            f"Severity: {alert['severity']} | "
            f"Risk: {alert['risk_score']:.3f} | "
            f"Machine: {alert['machine_info']['hostname']}"
        )
    
    def _notify_file(self, alert):
        """Write alert summary to a consolidated file."""
        summary_file = self.alert_log_dir / "alert_summary.txt"
        
        with open(summary_file, 'a') as f:
            f.write(f"\n{'='*60}\n")
            f.write(f"ALERT: {alert['alert_id']}\n")
            f.write(f"Time: {alert['timestamp']}\n")
            f.write(f"Severity: {alert['severity']}\n")
            f.write(f"Risk Score: {alert['risk_score']:.3f}\n")
            f.write(f"Machine: {alert['machine_info']['hostname']}\n")
            f.write(f"Evidence: {len(alert['evidence']['screenshots'])} screenshots\n")
            f.write(f"{'='*60}\n")
    
    def _notify_email(self, alert):
        """
        Send email notification (placeholder for hackathon).
        
        Real implementation would use SMTP.
        """
        if not self.admin_email:
            logger.warning("Email notification requested but no admin email configured")
            return
        
        # Placeholder: In real system, send email via SMTP
        logger.info(f"[EMAIL PLACEHOLDER] Would send alert to {self.admin_email}")
        
        # Real implementation:
        """
        import smtplib
        from email.mime.text import MIMEText
        
        msg = MIMEText(f"Crisis alert triggered: {alert['alert_id']}")
        msg['Subject'] = f"Crisis Alert - {alert['severity']}"
        msg['From'] = 'crisis-system@university.edu'
        msg['To'] = self.admin_email
        
        # Send via SMTP...
        """


# Example usage:
"""
if __name__ == "__main__":
    config = {
        'alert_log_dir': 'data/logs/alerts',
        'evidence_dir': 'data/evidence',
        'notification_methods': ['log', 'file'],
        'admin_email': 'admin@university.edu'
    }
    
    manager = AlertManager(config)
    
    # Simulate alert
    alert = manager.trigger_alert(
        risk_score=0.87,
        window_stats={
            'sample_count': 12,
            'avg_score': 0.72,
            'max_score': 0.95
        },
        screenshot_paths=['data/screenshots/screenshot_1.png'],
        webcam_path='data/webcam_captures/webcam_1.jpg'
    )
    
    print(f"Alert created: {alert['alert_id']}")
"""
