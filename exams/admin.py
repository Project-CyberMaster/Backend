from django.contrib import admin
from .models import *

class ChoiceInline(admin.TabularInline):
    model=MCQChoice

class QuestionAdmin(admin.ModelAdmin):
    inlines=[ChoiceInline]

admin.site.register(Exam)
admin.site.register(ExamAttempt)
admin.site.register(MCQChoice)
admin.site.register(Question,QuestionAdmin)