from django.contrib import admin
from django import forms
from .models import *

class ExamAdminForm(forms.ModelForm):
    class Meta:
        model = Exam
        fields = '__all__'
        help_texts = {
            'duration': 'Format: HH:MM:SS (e.g., 01:30:00 for 1 hour and 30 minutes)',
        }

class ChoiceInline(admin.TabularInline):
    model = MCQChoice

class QuestionAdmin(admin.ModelAdmin):
    inlines = [ChoiceInline]

class ExamAdmin(admin.ModelAdmin):
    form = ExamAdminForm
    list_display = ('title', 'course', 'duration', 'passing_score')

class ExamAttemptAdmin(admin.ModelAdmin):
    list_display = ('user', 'exam', 'score', 'started_at', 'is_finished', 'cert_ready')
    list_filter = ('is_finished', 'cert_ready')
    search_fields = ('user__username', 'exam__title')

class AnswerAdmin(admin.ModelAdmin):
    list_display = ('exam_attempt', 'question', 'is_correct')
    list_filter = ('is_correct',)

admin.site.register(Exam, ExamAdmin)
admin.site.register(ExamAttempt, ExamAttemptAdmin)
admin.site.register(MCQChoice)
admin.site.register(Question, QuestionAdmin)
admin.site.register(Answer, AnswerAdmin)