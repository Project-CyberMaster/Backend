from rest_framework import serializers
from .models import *

class CertificationSerializer(serializers.ModelSerializer):
    class Meta:
        model=Certification
        fields=['cert_id','user','course','date','file']
        read_only_fields=['cert_id','user','course','date','file']