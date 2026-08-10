"""Tests for the assessment scoring workflow."""
from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from .models import Choice, Course, Enrollment, Question, Submission


class AssessmentTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="learner", password="pass12345")
        self.course = Course.objects.create(name="Test Course", description="Testing")
        self.enrollment = Enrollment.objects.create(user=self.user, course=self.course)
        self.question = Question.objects.create(
            course=self.course,
            question_text="Select both correct choices",
            question_grade=100,
        )
        self.correct_a = Choice.objects.create(
            question=self.question, choice_text="A", is_correct=True
        )
        self.correct_b = Choice.objects.create(
            question=self.question, choice_text="B", is_correct=True
        )
        self.wrong = Choice.objects.create(
            question=self.question, choice_text="C", is_correct=False
        )

    def test_question_scores_only_exact_correct_set(self):
        self.assertTrue(
            self.question.is_get_score([self.correct_a.id, self.correct_b.id])
        )
        self.assertFalse(self.question.is_get_score([self.correct_a.id]))
        self.assertFalse(
            self.question.is_get_score(
                [self.correct_a.id, self.correct_b.id, self.wrong.id]
            )
        )

    def test_submit_creates_submission_and_redirects(self):
        self.client.login(username="learner", password="pass12345")
        response = self.client.post(
            reverse("onlinecourse:submit", args=[self.course.id]),
            {
                f"choice_{self.correct_a.id}": "on",
                f"choice_{self.correct_b.id}": "on",
            },
        )
        self.assertEqual(response.status_code, 302)
        submission = Submission.objects.get()
        self.assertEqual(submission.choices.count(), 2)

    def test_result_page_shows_congratulations_for_passing_score(self):
        submission = Submission.objects.create(enrollment=self.enrollment)
        submission.choices.set([self.correct_a, self.correct_b])
        self.client.login(username="learner", password="pass12345")
        response = self.client.get(
            reverse(
                "onlinecourse:show_exam_result",
                args=[self.course.id, submission.id],
            )
        )
        self.assertContains(response, "Congratulations!")
        self.assertContains(response, "100%")
        self.assertContains(response, "Exam Results")
