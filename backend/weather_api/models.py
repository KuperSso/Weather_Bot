from django.db import models

class UserLog(models.Model):
    user_id = models.BigIntegerField()
    command_request = models.CharField(max_length=255)
    timestamp = models.DateTimeField(auto_now_add=True)
    response = models.TextField()

    class Meta:
        db_table = "UserLog"

    def __str__(self):
        return f"Log(id={self.id}, user_id={self.user_id}, command={self.command_request}, timestamp={self.timestamp})"

class UserSettings(models.Model):
    user_id = models.BigIntegerField(unique=True)
    fixed_city = models.CharField(max_length=100)
    
    class Meta:
        db_table = "UserSettings"

    def __str__(self):
        return f"UserSettings(user_id={self.user_id}, preferred_city={self.fixed_city})"
