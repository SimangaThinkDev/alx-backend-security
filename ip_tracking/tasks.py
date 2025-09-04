from celery import shared_task
from django.utils import timezone
from datetime import timedelta
from .models import RequestLog, SuspiciousIP

SENSITIVE_PATHS = ["/admin", "/login"]


@shared_task
def flag_suspicious_ips():
    """
    Run hourly: flag IPs exceeding 100 requests/hour
    or hitting sensitive paths (/admin, /login).
    """
    one_hour_ago = timezone.now() - timedelta(hours=1)

    # Get all recent requests
    recent_logs = RequestLog.objects.filter(timestamp__gte=one_hour_ago)

    # Count requests per IP
    ip_counts = {}
    for log in recent_logs:
        ip_counts[log.ip_address] = ip_counts.get(log.ip_address, 0) + 1

        # Check sensitive path access
        if any(log.path.startswith(p) for p in SENSITIVE_PATHS):
            SuspiciousIP.objects.get_or_create(
                ip_address=log.ip_address,
                defaults={"reason": f"Accessed sensitive path {log.path}"}
            )

    # Check excessive requests
    for ip, count in ip_counts.items():
        if count > 100:
            SuspiciousIP.objects.get_or_create(
                ip_address=ip,
                defaults={"reason": f"Excessive requests: {count} in last hour"}
            )
