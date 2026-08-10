"""Django admin configuration for the OnlineCourse application."""
from django.contrib import admin

# The assignment explicitly expects seven imported application classes here.
from .models import Choice, Course, Instructor, Learner, Lesson, Question, Submission


class ChoiceInline(admin.TabularInline):
    """Edit choices directly from a Question admin page."""

    model = Choice
    extra = 4


class QuestionInline(admin.StackedInline):
    """Edit assessment questions directly from a Course admin page."""

    model = Question
    extra = 1


class LessonInline(admin.StackedInline):
    model = Lesson
    extra = 1


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    """Question administration with inline choices."""

    inlines = [ChoiceInline]
    list_display = ("question_text", "course", "question_grade")
    list_filter = ("course",)
    search_fields = ("question_text",)


@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    """Lesson administration grouped by course."""

    list_display = ("title", "course", "order")
    list_filter = ("course",)
    search_fields = ("title", "content")


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    inlines = [LessonInline, QuestionInline]
    list_display = ("name", "pub_date", "total_enrollment")
    search_fields = ("name", "description")


@admin.register(Instructor)
class InstructorAdmin(admin.ModelAdmin):
    list_display = ("user", "full_time", "total_learners")


@admin.register(Learner)
class LearnerAdmin(admin.ModelAdmin):
    list_display = ("user", "occupation")


admin.site.register(Choice)
admin.site.register(Submission)
