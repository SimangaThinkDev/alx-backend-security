# ip_tracking/middleware.py

from django.http import HttpRequest, HttpResponseForbidden
from .models import RequestLog, BlockedIP
from django_ip_geolocation.decorators import with_ip_geolocation
from django_ratelimit.decorators import ratelimit
from django.core.cache import cache


LOG_FILE_PATH = "logs.txt"

def rate_for_user(group, request: HttpRequest):
    if request.user.is_authenticated:
        return '10/m'  # Authenticated users
    return '5/m'      # Anonymous users

# Key function (optional, default 'user' or 'ip')
def key_for_user(group, request: HttpRequest):
    if request.user.is_authenticated:
        return str(request.user.id)
    return request.META.get('REMOTE_ADDR', 'anon')

def log_requests(get_response):

    @ratelimit(group=None, key=key_for_user, rate=rate_for_user, method=None, block=True)
    def middleware(request:HttpRequest):
        # Validate incoming IP
        ip:str = get_request_ip(request=request)

        # Get IP's from blocked IP's
        blocked_addresses = list( BlockedIP.objects.values_list( 
            "ip_address", 
            flat=True
            ) )

        if ip in blocked_addresses:
            return HttpResponseForbidden( "Your IP has been blocked from accessing this site due to malicious activity." )

        response = get_response(request)

        # Define attributes to log
        method = request.method
        cookies = request.COOKIES
        user = request.user
        is_authenticated:bool = user.is_authenticated
        body = request.body
        content_type = request.content_type
        files = request.FILES
        path = request.path
        
        geoloc_obj = request.geolocation
        country = geoloc_obj['country']
        city = geoloc_obj['city']

        # So I have two loggers

        with open( LOG_FILE_PATH, "a" ) as logfile:
            logfile.write( f"""
[ Method ] : {method.__str__}
[ Cookies ] : {cookies}
[ User ] : {user.__str__}
[ IsAuthenticated ] : {is_authenticated}
[ IP ] : {ip}
[ Body ] : {body.__str__}
[ ContentType ] : {content_type}
[ Files ] : {files}
""" )
            
        log_db = RequestLog( ip_address=ip, path=path, country=country, city=city )

        # Unclear on what to cache. So I picked these two...
        cache.set("blocked_ips", blocked_addresses, timeout=24*60*60)
        cache.set("geoloc_results", geoloc_obj, timeout=24*60*60)

        log_db.save()

        return response

    return middleware


def get_request_ip( request:HttpRequest ):

    x_forwarded_for:str = request.META.get( "HTTP_X_FORWARDED_FOR" )

    if x_forwarded_for:
        ip = x_forwarded_for.split(",")[0] # Where the IP is...
    else:
        ip = request.META.get( "REMOTE_ADDR" )

    return ip
