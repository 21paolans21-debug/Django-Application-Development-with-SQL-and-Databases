"""Create deterministic demo data for the assignment screenshots."""
from datetime import date

from django.contrib.auth.models import User
from django.core.management.base import BaseCommand

from onlinecourse.models import (
    Choice,
    Course,
    Enrollment,
    Instructor,
    Learner,
    Lesson,
    Question,
)


class Command(BaseCommand):
    help = "Create demo admin, learner, course, lessons, and assessment questions."

    def handle(self, *args, **options):
        admin, _ = User.objects.get_or_create(username="admin")
        admin.is_staff = True
        admin.is_superuser = True
        admin.set_password("Admin123!")
        admin.save()

        learner_user, _ = User.objects.get_or_create(username="student")
        learner_user.set_password("Student123!")
        learner_user.save()
        Learner.objects.get_or_create(user=learner_user)

        instructor_user, _ = User.objects.get_or_create(username="instructor")
        instructor_user.set_password("Instructor123!")
        instructor_user.save()
        instructor, _ = Instructor.objects.get_or_create(
            user=instructor_user,
            defaults={"full_time": True, "total_learners": 1},
        )

        course, _ = Course.objects.get_or_create(
            name="Django Application Development",
            defaults={
                "description": (
                    "Build database-backed web applications with Django models, "
                    "views, templates, authentication, and Bootstrap."
                ),
                "pub_date": date.today(),
                "total_enrollment": 1,
            },
        )
        course.instructors.add(instructor)
        Enrollment.objects.get_or_create(user=learner_user, course=course)

        lessons = [
            (1, "Django Models and ORM", "Create data models and work with relational data through Django ORM."),
            (2, "Views and Templates", "Build views and render dynamic pages with the Django template language."),
            (3, "Authentication and Bootstrap", "Secure the application and create responsive user interfaces."),
        ]
        for order, title, content in lessons:
            Lesson.objects.update_or_create(
                course=course,
                order=order,
                defaults={"title": title, "content": content},
            )

        question_data = [
            (
                "Which Django component maps Python classes to database tables?",
                50,
                [
                    ("Model", True),
                    ("Template", False),
                    ("URL dispatcher", False),
                    ("Static file", False),
                ],
            ),
            (
                "Which features are provided by Django? Select all that apply.",
                50,
                [
                    ("ORM", True),
                    ("Authentication", True),
                    ("Admin site", True),
                    ("A mandatory JavaScript frontend framework", False),
                ],
            ),
        ]

        for text, grade, choices in question_data:
            question, _ = Question.objects.update_or_create(
                course=course,
                question_text=text,
                defaults={"question_grade": grade},
            )
            for choice_text, is_correct in choices:
                Choice.objects.update_or_create(
                    question=question,
                    choice_text=choice_text,
                    defaults={"is_correct": is_correct},
                )

        self.stdout.write(self.style.SUCCESS("Demo data created successfully."))
        self.stdout.write("Admin:   admin / Admin123!")
        self.stdout.write("Learner: student / Student123!")
        self.stdout.write(f"Course ID: {course.id}")
