"""Views for authentication, courses, enrollment, exams, and grading."""
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import HttpResponseBadRequest, HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.urls import reverse

from .models import Choice, Course, Enrollment, Learner, Submission

PASSMARK = 80


def registration_request(request):
    """Create a learner account and sign the new user in."""
    if request.method == "GET":
        return render(request, "onlinecourse/user_registration_bootstrap.html")

    username = request.POST.get("username", "").strip()
    password = request.POST.get("psw", "")
    first_name = request.POST.get("firstname", "").strip()
    last_name = request.POST.get("lastname", "").strip()

    if not username or not password:
        return render(
            request,
            "onlinecourse/user_registration_bootstrap.html",
            {"message": "Username and password are required."},
        )

    if User.objects.filter(username=username).exists():
        return render(
            request,
            "onlinecourse/user_registration_bootstrap.html",
            {"message": "User already exists."},
        )

    user = User.objects.create_user(
        username=username,
        password=password,
        first_name=first_name,
        last_name=last_name,
    )
    Learner.objects.create(user=user)
    login(request, user)
    return HttpResponseRedirect(reverse("onlinecourse:index"))


def login_request(request):
    """Authenticate an existing user."""
    if request.method == "GET":
        return render(request, "onlinecourse/user_login_bootstrap.html")

    user = authenticate(
        username=request.POST.get("username", ""),
        password=request.POST.get("psw", ""),
    )
    if user is not None:
        login(request, user)
        return HttpResponseRedirect(reverse("onlinecourse:index"))

    return render(
        request,
        "onlinecourse/user_login_bootstrap.html",
        {"message": "Invalid username or password."},
    )


def logout_request(request):
    logout(request)
    return HttpResponseRedirect(reverse("onlinecourse:index"))


def course_list(request):
    """Display available courses."""
    courses = Course.objects.order_by("-total_enrollment", "name")
    enrolled_course_ids = set()
    if request.user.is_authenticated:
        enrolled_course_ids = set(
            Enrollment.objects.filter(user=request.user).values_list(
                "course_id", flat=True
            )
        )
    return render(
        request,
        "onlinecourse/course_list_bootstrap.html",
        {"courses": courses, "enrolled_course_ids": enrolled_course_ids},
    )


def course_details(request, course_id):
    """Display the course name, description, lessons, and assessment action."""
    course = get_object_or_404(Course, pk=course_id)
    is_enrolled = (
        request.user.is_authenticated
        and Enrollment.objects.filter(user=request.user, course=course).exists()
    )
    return render(
        request,
        "onlinecourse/course_details_bootstrap.html",
        {"course": course, "is_enrolled": is_enrolled},
    )


@login_required
def enroll(request, course_id):
    """Enroll the current user in a course."""
    course = get_object_or_404(Course, pk=course_id)
    _, created = Enrollment.objects.get_or_create(user=request.user, course=course)
    if created:
        course.total_enrollment += 1
        course.save(update_fields=["total_enrollment"])
        messages.success(request, "Enrollment completed.")
    return HttpResponseRedirect(
        reverse("onlinecourse:course_details", args=[course.id])
    )


@login_required
def take_exam(request, course_id):
    """Render the course assessment for an enrolled learner."""
    course = get_object_or_404(Course, pk=course_id)
    get_object_or_404(Enrollment, user=request.user, course=course)
    questions = course.questions.prefetch_related("choices").all()
    return render(
        request,
        "onlinecourse/exam_bootstrap.html",
        {"course": course, "questions": questions},
    )


def extract_answers(request):
    """Collect submitted checkbox values named choice_<choice_id>."""
    selected = []
    for key in request.POST:
        if key.startswith("choice_"):
            try:
                selected.append(int(key.removeprefix("choice_")))
            except ValueError:
                continue
    return selected


@login_required
def submit(request, course_id):
    """Persist a learner's exam choices and redirect to the result view."""
    if request.method != "POST":
        return HttpResponseBadRequest("Exam submissions must use POST.")

    course = get_object_or_404(Course, pk=course_id)
    enrollment = get_object_or_404(
        Enrollment,
        user=request.user,
        course=course,
    )
    selected_choice_ids = extract_answers(request)

    submission = Submission.objects.create(enrollment=enrollment)
    valid_choices = Choice.objects.filter(
        id__in=selected_choice_ids,
        question__course=course,
    )
    submission.choices.set(valid_choices)

    return HttpResponseRedirect(
        reverse(
            "onlinecourse:show_exam_result",
            args=[course.id, submission.id],
        )
    )


@login_required
def show_exam_result(request, course_id, submission_id):
    """Calculate the score and display detailed exam results."""
    course = get_object_or_404(Course, pk=course_id)
    submission = get_object_or_404(
        Submission.objects.select_related("enrollment"),
        pk=submission_id,
        enrollment__user=request.user,
        enrollment__course=course,
    )

    selected_choice_ids = set(
        submission.choices.values_list("id", flat=True)
    )
    questions = list(course.questions.prefetch_related("choices").all())

    total_grade = sum(question.question_grade for question in questions)
    grade = sum(
        question.question_grade
        for question in questions
        if question.is_get_score(selected_choice_ids)
    )
    score = round((grade / total_grade) * 100) if total_grade else 0
    passed = score >= PASSMARK

    return render(
        request,
        "onlinecourse/exam_result_bootstrap.html",
        {
            "course": course,
            "submission": submission,
            "questions": questions,
            "selected_choice_ids": selected_choice_ids,
            "grade": grade,
            "total_grade": total_grade,
            "score": score,
            "passed": passed,
            "passmark": PASSMARK,
        },
    )
