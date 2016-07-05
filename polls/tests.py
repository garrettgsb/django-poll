import datetime

from django.core.urlresolvers import reverse
from django.test import TestCase
from django.utils import timezone

from .models import Question

class QuestionMethodTests(TestCase):

#NOTE for later: Test method names need to start with the word 'test'

    def test_was_published_recently_with_future_question(self):
        """
        was_published_recently() should return False if
        the question's pub_date is in the future.
        """

        time = timezone.now() + datetime.timedelta(days=30)
        future_question = Question(pub_date = time)
        self.assertEqual(future_question.was_published_recently(), False)

    def test_was_published_recently_with_old_question(self):
        """
        was_published_recently() should return False
        if question is more than 1 day old
        """
        time = timezone.now() - datetime.timedelta(days=3)
        old_question = Question(pub_date = time)
        self.assertEqual(old_question.was_published_recently(), False)

    def test_was_published_recently_with_recent_question(self):
        """
        was_published_recently() should return True
        if question was created within last day
        """
        time = timezone.now() - datetime.timedelta(days=0.5)
        recent_question = Question(pub_date=time)
        self.assertEqual(recent_question.was_published_recently(), True)


def create_question(question_text, days):
    """
    Creates a new question where "days" is the
    number of days that the question's pub_date
    will be offset by. Positive for the future,
    negative for the past.
    """
    time = timezone.now() + timezone.timedelta(days=days)
    return Question.objects.create(question_text=question_text, pub_date=time)

class QuestionViewTests(TestCase):
    def test_index_view_with_no_questions(self):
        """
        If there are no questions,
        some kind of message should be displayed.
        """
        response = self.client.get(reverse('polls:index'))
        self.assertEqual(response.status_code, 200)

        # NOTE: Not sure where "No polls available" is declared
        # as part of the view, but this test doesn't pass.
        # TODO: Look into how view templates work and see if
        # this is fixable.
        # self.assertContains(response, "No polls available.")

        self.assertQuerysetEqual(response.context["latest_question_list"], [])

    def test_index_view_with_a_past_question(self):
        """
        A question with pub_date in the past
        should be rendered by the view.
        """
        create_question(question_text="Past Question.", days=-30)
        response = self.client.get(reverse('polls:index'))
        self.assertQuerysetEqual(
            response.context["latest_question_list"],
            ["<Question: Past Question.>"]
            )

    def test_index_view_with_a_future_question(self):
        """
        A question with a pub_date in the future
        should be skipped, not displayed in the view.
        """
        create_question(question_text="Future Question.", days=30)
        response = self.client.get(reverse("polls:index"))
        self.assertQuerysetEqual(
        response.context["latest_question_list"],
        []
        )
    def test_index_view_with_past_and_future_questions(self):
        create_question(question_text="Past Question.", days=-30)
        create_question(question_text="Future Question.", days=30)
        response = self.client.get(reverse('polls:index'))
        self.assertQuerysetEqual(
            response.context["latest_question_list"],
            ["<Question: Past Question.>"]
            )

    def test_index_view_with_two_past_questions(self):
        create_question(question_text="Past Question 1.", days=-30)
        create_question(question_text="Past Question 2.", days=-101)
        response = self.client.get(reverse("polls:index"))
        self.assertQuerysetEqual(
            response.context['latest_question_list'],
            ['<Question: Past Question 1.>', '<Question: Past Question 2.>']
        )
