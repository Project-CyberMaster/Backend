import base64
from io import BytesIO
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from django.template.loader import render_to_string
from django.core.files.base import ContentFile
from certs.serializers import CertificationSerializer
from .models import *
from courses.models import Enrollment
from exams.models import *
import segno
from playwright.sync_api import sync_playwright

def render_pdf(html, buffer):
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        page.set_content(html)
        pdf_content = page.pdf(
            print_background=True,
            margin={"top":"0","bottom":"0","left":"0","right":"0"},
            scale=1.0,
            landscape=True,
            format="A4",
            prefer_css_page_size=True,
        )
        buffer.write(pdf_content)
        browser.close()

class GetCert(APIView):
    permission_classes=[IsAuthenticated]

    def get(self,request,pk):
        course = get_object_or_404(Course,pk=pk)
        enrollment=get_object_or_404(Enrollment,user=request.user,course=course)
        exam=get_object_or_404(Exam,course=course)
        passing_attempt=ExamAttempt.objects.filter(
            user=request.user,
            exam=exam,
            cert_ready=True
        ).first()

        if passing_attempt:
            cert, _ = Certification.objects.get_or_create(
                user=request.user,
                course = course,
            )
            serializer = CertificationSerializer(cert)
            if not cert.file:
                qr = segno.make(f"cybermaster.com/verify/{cert.cert_id}")
                buffer=BytesIO()
                qr.save(buffer,kind='png',
                        scale=10,
                        dark="#FFFFFF",
                        light="#FFFFFF00",
                        data_dark="#FFFFFF",
                        data_light="#FFFFFF00",
                )
                
                image_str=base64.b64encode(buffer.getvalue()).decode('utf-8')
                data_uri=f'data:image/png;base64,{image_str}'

                html_content = render_to_string("certificate.html",{
                    'recipient_name':cert.user.username,
                    'course':cert.course,
                    'completion_date':cert.date,
                    'certificate_id':cert.cert_id,
                    'ceo_name':"Alia Chouaib",
                    'qrcode':data_uri
                })

                html_buffer=BytesIO()
                render_pdf(html_content, html_buffer)
                cert.file.save(f'{cert.user.username}_{cert.cert_id}.pdf',ContentFile(html_buffer.getvalue()),save=True)
            return Response(serializer.data)
        
        else:
            return Response({
                'detail':'certification not ready'
            }, status=400)
        
class Validate(APIView):
    def get(self,request,id):
        cert = Certification.objects.filter(cert_id=id).first()
        if not cert:
            return Response({"status":"Invalid"})
        
        return Response({
            "status":"Valid",
            "cert_id":cert.cert_id,
            "username":cert.user.username,
            "course":cert.course.title,
            "date":cert.date
        })