from django.test import TestCase
from questionapp.models import *
from questionapp import auth


# Create your tests here.

#python
from datetime import date, datetime, timedelta
import time
# import uuid
# import requests
# import pytz

#django
from django.conf import settings

from django.contrib.auth.models import  Permission, Group, User

from django.test import Client
from django.test import TestCase

from django.utils.timezone import utc
from django.test.client import RequestFactory

from django.test.utils import override_settings

from nose.tools import assert_equal, with_setup, assert_false, eq_, ok_

from django.test import TestCase, override_settings


from .base import add_initial_data, load_lots


TODAY_DT = datetime.utcnow().replace(tzinfo=utc) + timedelta(minutes=1)
YESTERDAY_DT = TODAY_DT - timedelta(days = 1)
TOMORROW_DT = TODAY_DT + timedelta(days = 1)
LASTWEEK_DT = TODAY_DT - timedelta(days = 7)
NEXTWEEK_DT = TODAY_DT + timedelta(days = 7)
LASTMONTH_DT = TODAY_DT - timedelta(days = 31)
NEXTMONTH_DT = TODAY_DT + timedelta(days = 31)

TODAY = date.today()
YESTERDAY = date.today() - timedelta(days = 1)
TOMORROW = date.today() + timedelta(days = 1)
LASTWEEK = date.today() - timedelta(days = 7)
NEXTWEEK = date.today() + timedelta(days = 7)
LASTMONTH = date.today() - timedelta(days = 31)
NEXTMONTH = date.today() + timedelta(days = 31)
NOW = datetime.utcnow().replace(tzinfo=utc) + timedelta(minutes=1)
TODAY_STARTS = NOW.replace(hour=0,minute=0,second=0)
TODAY_ENDS = NOW.replace(hour=23,minute=59,second=59)

@override_settings(AWARD_POINTS = {
    "ACCEPT_ANSWER" : 1,
    "MY_ANSWER_ACCEPTED" : 3,
    "ASK_QUESTION" : 5,
    "VOTE_ANSWER_UP" : 7,
    "VOTE_ANSWER_DOWN" :  11,
    "MY_ANSWER_VOTE_ANSWER_UP" : 13,
    "MY_ANSWER_VOTE_ANSWER_DOWN" : -13,
    "VOTE_QUESTION_UP" : 17,
    "VOTE_QUESTION_DOWN" :  19,
    "MY_QUESTION_VOTE_QUESTION_UP" : 23,
    "MY_QUESTION_VOTE_QUESTION_DOWN" : -23,
    "VOTE_COMMENT_UP" : 29,
    "VOTE_COMMENT_DOWN" :  31,
    "MY_COMMENT_VOTE_COMMENT_UP" : 37,
    "MY_COMMENT_VOTE_COMMENT_DOWN" : -37,

})
class BaseTest(TestCase):
    """
    setup data
    """

    #fixtures = [
    #    'country.json',
    #    ]

    def setUp(self):
        """ running setup """


        print "running setup"

        add_initial_data(None)


        self.user1= User.objects.get(username="user1")
        self.user2= User.objects.get(username="user2")
        self.user3= User.objects.get(username="user3")
        self.user4= User.objects.get(username="user4")
        self.user5= User.objects.get(username="user5")


        self.title1 = "Here is my first Question?"
        self.body1 = """And some HTML with <b> tags</b> and stuff going on
        in the midst of all this.  I suppose markdown is required.
        """
        self.tags1 = "breakfast lunch-and-diinner feast"

        self.title2 = "This is a very long question that goes over the 300 max characters for a question. That's seems excessively long so I think I will reduce the length of the questions string to maybe, well how long is this now only 200 and that's arelady a massively long question so I'm going to reduce to 200"
        self.body2 = """And now for a mamoth question
I am the very model of a modern Major-General,
I've information vegetable, animal, and mineral,
I know the kings of England, and I quote the fights historical
From Marathon to Waterloo, in order categorical;a
I'm very well acquainted, too, with matters mathematical,
I understand equations, both the simple and quadratical,
About binomial theorem I'm teeming with a lot o' news, (bothered for a rhyme)
With many cheerful facts about the square of the hypotenuse.
I'm very good at integral and differential calculus;
I know the scientific names of beings animalculous:
In short, in matters vegetable, animal, and mineral,
I am the very model of a modern Major-General.

1880 poster
I know our mythic history, King Arthur's and Sir Caradoc's;
I answer hard acrostics, I've a pretty taste for paradox,
I quote in elegiacs all the crimes of Heliogabalus,
In conics I can floor peculiarities parabolous;
I can tell undoubted Raphaels from Gerard Dows and Zoffanies,
I know the croaking chorus from The Frogs of Aristophanes!
Then I can hum a fugue of which I've heard the music's din afore, (bothered for a rhyme)b
And whistle all the airs from that infernal nonsense Pinafore.
Then I can write a washing bill in Babylonic cuneiform,
And tell you ev'ry detail of Caractacus's uniform:c
In short, in matters vegetable, animal, and mineral,
I am the very model of a modern Major-General.
In fact, when I know what is meant by "mamelon" and "ravelin",
When I can tell at sight a Mauser rifle from a javelin,d
When such affairs as sorties and surprises I'm more wary at,
And when I know precisely what is meant by "commissariat",
When I have learnt what progress has been made in modern gunnery,
When I know more of tactics than a novice in a nunnery -
In short, when I've a smattering of elemental strategy - (bothered for a rhyme)
You'll say a better Major-General has never sat a gee.e
For my military knowledge, though I'm plucky and adventury,
Has only been brought down to the beginning of the century;
But still, in matters vegetable, animal, and mineral,
I am the very model of a modern Major-General.
        """
        self.tags2 = "breakfast, lunch, dinner, feast"

        self.answer1="a short answer"
        self.answer2 = """
        A British tar is a soaring soul,
As free as a mountain bird,
His energetic fist should be ready to resist
A dictatorial word.

His nose should pant
and his lip should curl,
His cheeks should flame
and his brow should furl,
His bosom should heave
and his heart should glow,
And his fist be ever ready
for a knock-down blow.

Chorus.
His nose should pant
and his lip should curl,
His cheeks should flame
and his brow should furl,
His bosom should heave
and his heart should glow,
And his fist be ever ready
for a knock-down blow.
    """
        self.answer3 = "a couple of lines" \
                       "only"


        time.sleep(2)


class setupTests(BaseTest) :

    def test_initialdata(self):

        # check setup for testing has create data correctly
        print 'test_initialdata'


        # users created with their profiles

        user1_profile = QUser.objects.get(user=self.user1)
        user2_profile = QUser.objects.get(user=self.user2)



# @modify_settings(AWARD_POINTS = {
#     "ACCEPT_ANSWER" : 1,
#     "MY_ANSWER_ACCEPTED" : 3,
#     "ASK_QUESTION" : 5,
#     "VOTE_ANSWER_UP" : 7,
#     "VOTE_ANSWER_DOWN" :  11,
#     "MY_ANSWER_VOTE_ANSWER_UP" : 13,
#     "MY_ANSWER_VOTE_ANSWER_DOWN" : -13,
#     "VOTE_QUESTION_UP" : 17,
#     "VOTE_QUESTION_DOWN" :  19,
#     "MY_QUESTION_VOTE_QUESTION_UP" : 23,
#     "MY_QUESTION_VOTE_QUESTION_DOWN" : -23,
#     "VOTE_COMMENT_UP" : 29,
#     "VOTE_COMMENT_DOWN" :  31,
#     "MY_COMMENT_VOTE_COMMENT_UP" : 37,
#     "MY_COMMENT_VOTE_COMMENT_DOWN" : -37,
#
# })
class Questions(BaseTest):

    def test_askquestion(self):

        q = Question.ask(self.user1, self.title1, self.body1, self.tags1)
        q1 = Question.objects.get(id=q.id)
        eq_(Question.objects.all().count(), 1)
        eq_(q1.author, self.user1)
        eq_(q1.title, self.title1)
        eq_(q1.body, self.body1)
        eq_(q1.summary, self.body1)
        eq_(q1.tags.all().count(), 3)


        q = Question.ask(self.user2, self.title2, self.body2, self.tags2)
        q2 = Question.objects.get(id=q.id)
        eq_(Question.objects.all().count(), 2)
        eq_(q2.author, self.user2)
        eq_(q2.title, self.title2[:199])
        eq_(q2.body, self.body2)
        eq_(q2.summary, self.body2[:179])
        eq_(q2.tags.all().count(), 4)

    def test_answer(self):


        q = Question.ask(self.user1, self.title1, self.body1, self.tags1)


        q.answer(self.user2, "Here is the answer")

        eq_(Answer.objects.all().count(), 1)
        a1 = Answer.objects.get(question=q)
        eq_(a1.author, self.user2)
        eq_(a1.body, "Here is the answer")
        eq_(a1.question.answer_count, 1)

        #ok for the same user to add more than one answer
        a = q.answer(self.user2, "Here is another answer")
        eq_(Answer.objects.all().count(), 2)
        a1 = Answer.objects.get(id = a.id)
        eq_(a1.author, self.user2)
        eq_(a1.body, "Here is another answer")
        eq_(a1.question.answer_count, 2)
        eq_(q.answers.count(), 2)


        # but user2 then decides to delete the second answer
        a1.delete(self.user2)
        a2 = Answer.objects.get(id = a.id)
        eq_(a2.question.answer_count, 1)
        eq_(a2.question.answers.count(), 2)  # all answers
        eq_(a2.question.live_answers.count(), 1)  # not deleted answers


        # user3 now has a go
        a = q.answer(self.user3, self.answer2)
        eq_(Answer.objects.all().count(), 3)
        a3 = Answer.objects.get(id = a.id)
        eq_(a3.author, self.user3)
        eq_(a3.body, self.answer2)
        #eq_(a3.question.answer_count, 2)
        eq_(a3.question.live_answers.count(), 2)

        # user 2 tries to accept this answer, but is not allowed
        ok_(a3.accept(self.user2) is False)

        # by user1 can accept as author of the question, but first zero reputations so can check awarded easily
        # set user 1 reputations as they will be checked later
        u1 = QUser.objects.get(user=self.user1)
        u1.reputation = 0
        u1.save()

        ok_(a3.accept(self.user1) is True)

        u1 = QUser.objects.get(user=self.user1)
        eq_(u1.reputation, settings.AWARD_POINTS["ACCEPT_ANSWER"])

        qq = Question.objects.get(id=q.id)
        eq_(qq.accepted_answer, a3)

    def test_unaward(self):

        load_lots()

        '''    # q4 has two answers and no votes
    q4 = Question.ask(user3, "How brown is the mud","really brown?", "mineral" )
    q4.answer(user1, "more green")
    q4.answer(user2, "with yellow")
    '''
        # set user3 reputations as they will be checked later
        zero_reputation(self.user3)

        q = Question.objects.get(id=4)
        a1 = Answer.objects.get(body="more green")
        a2 = Answer.objects.get(body="with yellow")

        # user accepts answer 1
        ok_(a1.accept(self.user3) is True)

        u = QUser.objects.get(user=self.user3)
        eq_(u.reputation, settings.AWARD_POINTS["ACCEPT_ANSWER"])

        # another user tries to accept a different answer
        ok_(a2.accept(self.user2) is False)

        # user changes their mind and accepts answer 2
        ok_(a2.accept(self.user3) is True)

        # and this does not change their reputations
        u = QUser.objects.get(user=self.user3)
        eq_(u.reputation, settings.AWARD_POINTS["ACCEPT_ANSWER"])


    def test_favourites(self):

        load_lots()

        # user 2 likes the 3rd question
        q3 = Question.objects.get(id=3)
        self.assertFalse(q3.is_favourite(self.user2))
        q3.make_favourite(self.user2)
        self.assertTrue(q3.is_favourite(self.user2))

        # and then changes their mind
        q3.unmake_favourite(self.user2)
        self.assertFalse(q3.is_favourite(self.user2))

        #TODO: can a user favourite their own question?




    def test_question_votes(self):

        load_lots()

        # user 2 votes up 3rd question
        q = Question.objects.get(id=4)

        questioner = self.user3
        voter = self.user4
        zero_reputation(voter)
        zero_reputation(questioner)

        # no votes placed yet
        eq_(q.voted(voter), None)
        eq_(q.score, 0)

        # voter has no reputations so no votes applied
        eq_(q.vote(voter), 0)
        eq_(q.voted(voter), None)
        eq_(q.score, 0)

        # give user reputation so can vote
        u = set_reputation(voter,auth.points_required_to("VOTE_UP") + 1 )

        ok_(auth.can_vote_up(voter) is True)

        # user up votes answer by default (1)
        q.vote(voter)

        # question 3 now has 1 vote
        q = Question.objects.get(id=q.id)
        eq_(q.score, 1)

        # voters reputation has gone up
        u = QUser.objects.get(user=voter)
        eq_(u.reputation, auth.points_required_to("VOTE_UP") + 1 + pointed_awarded_for(voter, "VOTE_QUESTION_UP"))

        # 1 vote for this answer
        v = q.voted(voter)
        eq_(v.votes, 1)

        # and answerer1 reputation has also gone up
        au =  QUser.objects.get(user=questioner)
        eq_(au.reputation, pointed_awarded_for(au, "MY_QUESTION_VOTE_QUESTION_UP"))

        # user 2 up votes question 3 again, this time by 2
        # a new vote replaces a previous one
        q.vote(voter, 2)

        # so the question now has a score of 2
        q = Question.objects.get(id=q.id)
        eq_(q.score, 2)

        # but reputation hasn't changed
        eq_(u.reputation, auth.points_required_to("VOTE_UP") + 1 + pointed_awarded_for(voter, "VOTE_QUESTION_UP"))
        v = q.voted(voter)
        eq_(v.votes, 2)

        # and then changes their mind
        # q3.unmake_favourite(voter)
        # self.assertFalse(q3.is_favourite(voter))


        #TODO: can a user vote their own question?




    def test_answer_votes(self):
        '''
        q4 = Question.ask(user3, "How brown is the mud","really brown?", "mineral" )
        q4.answer(user1, "more green")
        q4.answer(user2, "with yellow")
        '''
        load_lots()

        # user 2 votes up 3rd question
        q = Question.objects.get(id=4)
        a = Answer.objects.filter(question=q)[0]
        questioner = self.user3
        answerer1 = self.user1
        answerer2 = self.user2
        voter = self.user4
        zero_reputation(voter)
        zero_reputation(answerer1)

        # no votes placed yet
        eq_(a.voted(voter), None)
        eq_(a.score, 0)

        # voter has no reputations so no votes applied
        eq_(a.vote(voter), 0)
        eq_(a.voted(voter), None)
        eq_(a.score, 0)

        # give user reputation so can vote
        u = set_reputation(voter,auth.points_required_to("VOTE_UP") + 1 )

        ok_(auth.can_vote_up(voter) is True)

        # user up votes answer by default (1)
        a.vote(voter)

        # question 3 now has 1 vote
        a = Answer.objects.get(id=a.id)
        eq_(a.score, 1)

        # voters reputation has gone up
        u = QUser.objects.get(user=voter)
        eq_(u.reputation, auth.points_required_to("VOTE_UP") + 1 + pointed_awarded_for(voter, "VOTE_ANSWER_UP"))

        # 1 vote for this answer
        v = a.voted(voter)
        eq_(v.votes, 1)

        # and answerer1 reputation has also gone up
        au =  QUser.objects.get(user=answerer1)
        eq_(au.reputation, pointed_awarded_for(au, "MY_ANSWER_VOTE_ANSWER_UP"))

        # user 2 up votes answer 3 again, this time by 2
        # a new vote replaces a previous one
        a.vote(voter, 2)

        # so the answer now has a score of 2
        a = Answer.objects.get(id=a.id)
        eq_(a.score, 2)

        # but reputation hasn't changed
        eq_(u.reputation, auth.points_required_to("VOTE_UP") + 1 + pointed_awarded_for(voter, "VOTE_ANSWER_UP"))
        v = a.voted(voter)
        eq_(v.votes, 2)

        # and then changes their mind
        # q3.unmake_favourite(voter)
        # self.assertFalse(q3.is_favourite(voter))

        #TODO: can a user vote their own answer?

    def test_award_points(self):

        # try awarding points for an undefined action

        with self.assertRaises(ValidationError):
            award_points(self.user1, "DO STUFF")


    def test_close_question(self):

        load_lots()

        q = Question.objects.get(id=4)

        zero_reputation(self.user2)
        zero_reputation(self.user3)

        # user2 tries to close someone elses question
        with self.assertRaises(PermissionDenied):
            q.close(self.user2, 3)
        ok_(q.closed is False)

        # but author can close once they have the reputations
        with self.assertRaises(PermissionDenied):
            q.close(self.user3, 3)

        set_reputation(self.user3,auth.points_required_to("CLOSE_OWN_QUESTIONS"))
        q.close(self.user3, 3)
        ok_(q.closed is True)
        eq_(q.closed_by, self.user3)
        eq_(q.close_reason, 3)

        # now try reopening it

        # user2 failes
        with self.assertRaises(PermissionDenied):
            q.reopen(self.user2)
        ok_(q.closed is True)

        # but author can reopen
        q.reopen(self.user3)
        ok_(q.closed is False)
        ok_(q.closed_by is None)
        ok_(q.close_reason is None)


        # can't reopen an open question
        q = Question.objects.get(id=3)
        ok_(q.closed is False)
        q.reopen(self.user3)
        ok_(q.closed is False)
        ok_(q.closed_by is None)
        ok_(q.close_reason is None)

def zero_reputation(user):
    ''' set reputation to zero to make testing reputation values easier
    :param user:
    :return:
    '''
    u = QUser.objects.get(user=user)
    u.reputation = 0
    u.save()
    return u

def set_reputation(user, points):

    u = QUser.objects.get(user=user)
    u.reputation = points
    u.save()
    return u