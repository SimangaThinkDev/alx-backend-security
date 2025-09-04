# ip_tracking/middleware.py

from django.http import HttpRequest

LOG_FILE_PATH = "logs.txt"

def simple_middleware(get_response):
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

        # Code to be executed for each request/response after
        # the view is called.

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

        return response

    return middleware

def get_request_ip( request:HttpRequest ):

    x_forwarded_for:str = request.META.get( "HTTP_X_FORWARDED_FOR" )

    if x_forwarded_for:
        ip = x_forwarded_for.split(",")[0] # Where the IP is...
    else:
        ip = request.META.get( "REMOTE_ADDR" )

    return ip
