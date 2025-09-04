# ip_tracking/middleware.py

from django.http import HttpRequest
from .models import RequestLog
from datetime import datetime

LOG_FILE_PATH = "logs.txt"

def log_requests(get_response):
    # One-time configuration and initialization.

    def middleware(request:HttpRequest):
        # Code to be executed for each request before
        # the view (and later middleware) are called.

        response = get_response(request)

        method = request.method
        cookies = request.COOKIES
        user = request.user
        is_authenticated:bool = user.is_authenticated
        ip:str = get_request_ip(request=request)
        body = request.body
        content_type = request.content_type
        files = request.FILES
        path = request.path

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
            
        log_db = RequestLog( ip_address=ip, path=path )

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
