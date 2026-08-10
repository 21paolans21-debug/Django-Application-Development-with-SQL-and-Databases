"""Database models for courses, lessons, enrollment, and assessments."""
from django.contrib.auth.models import User
from django.db import models
from django.utils.timezone import now


class Instructor(models.Model):
    """Additional profile information for a course instructor."""

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    full_time = models.BooleanField(default=True)
    total_learners = models.IntegerField(default=0)

    def __str__(self):
        return self.user.username


class Learner(models.Model):
    """Learner profile associated with Django's built-in User model."""

    STUDENT = "student"
    DEVELOPER = "developer"
    DATA_SCIENTIST = "data_scientist"
    DATABASE_ADMIN = "dba"

    OCCUPATION_CHOICES = [
        (STUDENT, "Student"),
        (DEVELOPER, "Developer"),
        (DATA_SCIENTIST, "Data Scientist"),
        (DATABASE_ADMIN, "Database Admin"),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    occupation = models.CharField(
        max_length=20,
        choices=OCCUPATION_CHOICES,
        default=STUDENT,
    )

    def __str__(self):
        return f"{self.user.username} ({self.get_occupation_display()})"


class Course(models.Model):
    """An online course containing lessons and assessment questions."""

    name = models.CharField(max_length=100, default="Online Course")
    image = models.ImageField(upload_to="course_images/", blank=True, null=True)
    description = models.TextField(max_length=1000)
    pub_date = models.DateField(null=True, blank=True)
    instructors = models.ManyToManyField(Instructor, blank=True)
    users = models.ManyToManyField(User, through="Enrollment", related_name="courses")
    total_enrollment = models.IntegerField(default=0)

    def __str__(self):
        return self.name


class Lesson(models.Model):
    """A lesson belonging to a course."""

    title = models.CharField(max_length=200, default="Lesson")
    order = models.PositiveIntegerField(default=0)
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name="lessons",
    )
    content = models.TextField()

    class Meta:
        ordering = ["order", "id"]

    def __str__(self):
        return self.title


class Enrollment(models.Model):
    """Connects a user to a course."""

    AUDIT = "audit"
    HONOR = "honor"
    BETA = "beta"
    COURSE_MODES = [
        (AUDIT, "Audit"),
        (HONOR, "Honor"),
        (BETA, "Beta"),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    date_enrolled = models.DateField(default=now)
    mode = models.CharField(max_length=5, choices=COURSE_MODES, default=AUDIT)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["user", "course"],
                name="unique_user_course_enrollment",
            )
        ]

    def __str__(self):
        return f"{self.user.username} - {self.course.name}"


class Question(models.Model):
    """Assessment question attached to a course."""

    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name="questions",
    )
    question_text = models.CharField(max_length=200)
    question_grade = models.PositiveIntegerField(default=10)

    def __str__(self):
        return self.question_text

    def is_get_score(self, selected_ids):
        """Return True only when every correct choice and no wrong choice is selected."""
        selected_ids = set(selected_ids)
        correct_ids = set(
            self.choices.filter(is_correct=True).values_list("id", flat=True)
        )
        selected_for_question = set(
            self.choices.filter(id__in=selected_ids).values_list("id", flat=True)
        )
        return bool(correct_ids) and selected_for_question == correct_ids


class Choice(models.Model):
    """A possible answer for a Question."""

    question = models.ForeignKey(
        Question,
        on_delete=models.CASCADE,
        related_name="choices",
    )
    choice_text = models.CharField(max_length=200)
    is_correct = models.BooleanField(default=False)

    def __str__(self):
        return self.choice_text


class Submission(models.Model):
    """Stores a learner's selected answers for an exam attempt."""

    enrollment = models.ForeignKey(
        Enrollment,
        on_delete=models.CASCADE,
        related_name="submissions",
    )
    choices = models.ManyToManyField(Choice, blank=True)
    submitted_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Submission {self.pk} - {self.enrollment}"
