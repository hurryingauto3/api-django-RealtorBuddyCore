from django.db import models

# Create your views here.
# day 1 send email (weekends excluded)
# day 5 send email (weekends excluded)
# day 8 send email (weekends excluded)
# day 12 send email (weekends excluded) (maybe)


class client(models.Model):
    id = models.AutoField(primary_key=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField()
    replied_at = models.DateTimeField(null=True, blank=True, default=None)
    last_contacted = models.DateTimeField(null=True, blank=True, default=None)
    contacted_times = models.IntegerField(default=0)

# class emailStageDefinition(models.Model):
#     id = models.AutoField(primary_key=True)
#     name = models.CharField(max_length=100)


# class emailStage(models.Model):
#     id = models.AutoField(primary_key=True)
#     created = models.DateField()
#     updated = models.DateField()
#     stage = models.ForeignKey(emailStageDefinition(), on_delete=models.CASCADE)
#     client = models.ForeignKey(client, on_delete=models.CASCADE)


# class emailStageHistory(models.Model):
#     id = models.AutoField(primary_key=True)
#     created = models.DateField()
#     stage = models.ForeignKey(emailStage, on_delete=models.CASCADE)
#     client = models.ForeignKey(client, on_delete=models.CASCADE)


class clientEmailDefinition(models.Model):
    id = models.AutoField(primary_key=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    key = models.IntegerField()
    weekends = models.BooleanField()
    days_wait = models.IntegerField()
    email_subject = models.CharField(max_length=100)
    email_body = models.TextField()

    def render_email(self, context):
        # Replace placeholders in the subject and body
        subject = str(self.email_subject).format(**context)
        body = str(self.email_body).format(**context)
        return subject, body


class clientEmailOutReachRuleset(models.Model):
    id = models.AutoField(primary_key=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    new_clients_daily = models.IntegerField()
    follow_up_clients_daily = models.IntegerField()


class clientEmailLogs(models.Model):
    id = models.AutoField(primary_key=True)
    created = models.DateTimeField(auto_now_add=True)
    client = models.ForeignKey(client, on_delete=models.CASCADE)
    email = models.ForeignKey(clientEmailDefinition, on_delete=models.CASCADE)
