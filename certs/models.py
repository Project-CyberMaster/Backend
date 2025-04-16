import random
import string
from django.db import models
from users.models import CustomUser
from courses.models import Course
from django.db.models.functions import Now

class Certification(models.Model):
    cert_id=models.CharField(max_length=13,primary_key=True)
    user=models.ForeignKey(CustomUser,related_name="certifications",on_delete=models.CASCADE)
    course=models.ForeignKey(Course,related_name="certifications",on_delete=models.CASCADE)
    date=models.DateField(db_default=Now())
    file=models.FileField(upload_to='certs/',blank=True,null=True)

    unique_together = ("course","user")

    def generate_id(self):
        return f"CYBR-{''.join(random.choices(string.ascii_uppercase+string.digits,k=8))}"
    
    def save(self,*args,**kwargs):
        if not self.cert_id:
            self.cert_id = self.generate_id()
        super().save(*args,**kwargs)

    def __str__(self):
        return "Cert for user " + self.user.username + " with id " + self.cert_id