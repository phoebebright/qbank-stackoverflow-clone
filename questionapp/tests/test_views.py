
from django.conf import settings

from django.http import HttpRequest
from django.test.client import Client

from django.contrib.auth.models import  Permission, Group, User
from django.test import TestCase
from django.core.urlresolvers import reverse
from django.contrib.auth.models import AnonymousUser

from nose.tools import assert_equal, with_setup, assert_false, eq_, ok_
from nose.plugins.attrib import attr
from pyquery import PyQuery as pq

from .base import add_initial_data, load_lots

from djet import assertions, testcases


from questionapp.models import *
from questionapp.views import *

class BaseTest(testcases.ViewTestCase):
    """
    setup data
    """

    def setUp(self):
        """ running setup """


        print "running setup"

        add_initial_data(None)
        load_lots()

        self.anon = AnonymousUser()
        self.user1= User.objects.get(username="user1")
        self.user2= User.objects.get(username="user2")
        self.user3= User.objects.get(username="user3")
        self.user4= User.objects.get(username="user4")
        self.user5= User.objects.get(username="user5")

        self.client = Client()

    # def test_redirect_on_not_logged_in(self):
    #     request = self.factory.get(user=self.anon)
    #     r = self.view(request, **self.view_kwargs)
    #     self.assertRedirects(r, reverse('account_login'))


class HomeViewTest(BaseTest):
    view_function = home

    def test_view_nologin(self):

        request = self.factory.get(user=self.anon)

        r = self.view(request)

        doc = pq(r.content)

        ok_(doc('#main'))

    def test_view_login(self):
        request = self.factory.post(data={'next': '/'}, user=self.user1)

        r = self.view(request)

        doc = pq(r.content)

        ok_(doc('#main'))

class QuestionViewTest(BaseTest):
    view_function = question
    view_kwargs = {'question_id': 1}

    def test_view_nologin(self):

        request = self.factory.get(user=self.anon)
        r = self.view(request, **self.view_kwargs)
        doc = pq(r.content)
        ok_(doc('#question'))

    def test_view_login(self):

        request = self.factory.post(data={'next': '/'}, user=self.user1)
        r = self.view(request, **self.view_kwargs)
        doc = pq(r.content)
        ok_(doc('#question'))


    def test_view_count(self):
        q = Question.objects.get(id=self.view_kwargs['question_id'])

        eq_(q.view_count, 0)
        request = self.factory.post(data={'next': '/'}, user=self.user1)
        r = self.view(request, **self.view_kwargs)


        q = Question.objects.get(id=self.view_kwargs['question_id'])
        eq_(q.view_count, 1)


class QuestionCloseViewTest(BaseTest):
    view_function = close_question
    view_kwargs = {'question_id': 1}

    # def test_redirect_on_not_logged_in(self):
    #     super(QuestionCloseViewTest, self).test_redirect_on_not_logged_in()

    def test_view_nologin(self):

        request = self.factory.get(user=self.anon)
        r = self.view(request, **self.view_kwargs)
        self.assertRedirects(r, reverse('account_login'))

    def test_view_login(self):

        request = self.factory.post(data={'next': '/'}, user=self.user1)
        r = self.view(request, **self.view_kwargs)
        doc = pq(r.content)
        ok_(doc('#close-question'))


'''
TODO
if a question is closed it doesn't appear in question list, unless you are the author
test close and reopen screens

users
user

'''