from django.db import models
from email.MIMEText import MIMEText
import smtplib

FROM = 'test@dragonpaw.org'
# Set to None if you don't need it.
FROM_PASSWORD = 'test'
SERVER = 'mail.dragonpaw.org'

# Create your models here.
class Message(models.Model):
    """This table contains the individual email messages."""
        
    profile = models.ForeignKey('user.UserProfile')
    body = models.TextField()
    subject = models.CharField(blank=True, max_length=100)
    date = models.DateTimeField(auto_now_add=True)
    order = models.IntegerField(blank=True, null=True)
    from_address = models.EmailField()
    to_address = models.EmailField()
    #headers = models.TextField()
    
    class Meta:
        ordering = ( '-date',)

    class Admin:
        search_fields = ('subject',)
        list_display = ('profile', 'subject',) 
        
    def __unicode__(self):
        return self.subject

    def send_to(self, to):
        # Create a text/plain message
        msg = MIMEText(self.body)

        # me == the sender's email address
        # you == the recipient's email address
        msg['Subject'] = self.subject
        msg['From'] = self.from_address
        msg['To'] = self.to_address

        # Send the message via our own SMTP server, but don't include the
        # envelope header.
        s = smtplib.SMTP(SERVER)
        if FROM_PASSWORD:
            s.login(FROM, FROM_PASSWORD)
            
        s.sendmail(msg['From'], [to], msg.as_string())
        s.close()
