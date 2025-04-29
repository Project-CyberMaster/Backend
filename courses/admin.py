from django.contrib import admin
from .models import Course,Chapter,Lesson,Enrollment

admin.site.register(Course)
admin.site.register(Enrollment)
admin.site.register(Chapter)
admin.site.register(Lesson)