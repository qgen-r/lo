from django.db import models


class CustomerLoc(models.Model):
    phone = models.CharField(max_length=20, blank=True, default="")
    ip_lat = models.FloatField(null=True, blank=True)
    ip_lon = models.FloatField(null=True, blank=True)
    ip_city = models.CharField(max_length=100, blank=True, null=True)
    gps_lat = models.FloatField(null=True, blank=True)
    gps_lon = models.FloatField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    is_verified = models.BooleanField(default=False)
    all_info = models.TextField(blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        # format timestamp if present
        if self.timestamp:
            ts = self.timestamp.strftime("%Y-%m-%d %H:%M:%S")
        else:
            ts = "[pending timestamp]"

        # Build a readable log
        self.all_info = (
            f"IP Loc:   {self.ip_lat}, {self.ip_lon}\n"
            f"GPS Loc:  {self.gps_lat}, {self.gps_lon}\n"
            f"Phone:    {self.phone or '[none]'}\n"
            f"Verified: {self.is_verified}\n"
            f"Device UA:{self.user_agent}\n"
            f"On:       {ts}"
        )
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.phone or '-'} @ {self.timestamp or '[no timestamp]'}"
