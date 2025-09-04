from django.db import models

class RequestLog( models.Model ):

    ip_address = models.CharField( max_length=40 )
    path = models.CharField( max_length=255 )
    timestamp = models.DateTimeField( auto_now_add=True )

    def __str__(self):
        return f"Ip_Address: {self.ip_address} \n\
            Timestamp: {self.timestamp} \n\
            Path: {self.path}\n"
    

class BlockedIP( models.Model ):

    ip_address = models.CharField( max_length=40 )

    def __str__(self):
        return f"IP-Address: {self.ip_address}"
    
