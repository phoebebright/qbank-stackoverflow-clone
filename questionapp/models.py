from django.db import models
from django.db.models import F

import datetime
from django.contrib.contenttypes import generic
from django.core.urlresolvers import reverse
from django.db import connection, models, transaction
from django.template.defaultfilters import slugify
from django.db.models import Q
from django.core.exceptions import ValidationError, PermissionDenied, ObjectDoesNotExist

from django.contrib.contenttypes.models import ContentType
from django.db.models.signals import post_delete, post_save, pre_save
from django.utils.translation import ugettext_lazy as _
from django.conf import settings

from taggit.managers import TaggableManager
from taggit.utils import edit_string_for_tags, parse_tags





import collections
import datetime
import hashlib
import re

from django.contrib.auth.models import User


'''
assume that django user is going to be used, if want to use a customer user then there are issues with setting up the post_save_connect signal

'''

#TODO: add question and answer revisions using django-simple-history
#TODO: additional features
'''
django-taggit-suggest: Provides support for defining keyword and regular expression rules for suggesting new tags for content. This used to be available at taggit.contrib.suggest. Available on github.
django-taggit-templatetags: Provides several templatetags, including one for tag clouds, to expose various taggit APIs directly to templates. Available on github.
'''


class QuestionManager(models.Manager):
    # def update_tags(self, question, tagnames, user):
    #     current_tags = list(question.tags.all())
    #     current_tagnames = set(t.name for t in current_tags)
    #     updated_tagnames = set(t for t in tagnames.split(' ') if t)
    #     modified_tags = []
    #
    #     removed_tags = [t for t in current_tags
    #                     if t.name not in updated_tagnames]
    #     if removed_tags:
    #         modified_tags.extend(removed_tags)
    #         question.tags.remove(*removed_tags)
    #
    #     added_tagnames = updated_tagnames - current_tagnames
    #     if added_tagnames:
    #         added_tags = Tag.objects.get_or_create_multiple(added_tagnames,
    #                                                         user)
    #         modified_tags.extend(added_tags)
    #         question.tags.add(*added_tags)
    #
    #     if modified_tags:
    #         Tag.objects.update_use_counts(modified_tags)
    #         return True
    #
    #     return False

    pass


class QuestionQuerySet(models.QuerySet):

    def unanswered(self):
        return self.filter(accepted_answer__isnull = True)

    def answered(self):
        return self.filter(accepted_answer__isnull = False)

    def live(self):
        return self.filter(closed_at__isnull = True)


class Question(models.Model):
    CLOSE_REASONS = (
        (1, u'Exact duplicate'),
        (2, u'Off topic'),
        (3, u'Not a real question'),
        (4, u'No longer relevant'),
        (5, u'Spam'),
    )

    title = models.CharField(max_length=200, help_text=_("Enter a descriptive title that contains words likely to be searched"))
    author   = models.ForeignKey(User, related_name='questions')
    added_at = models.DateTimeField(auto_now_add=True)
    accepted_answer = models.ForeignKey('Answer', blank=True, null=True, related_name="accepted_answer")
    closed_by = models.ForeignKey(User, null=True, blank=True, related_name='closed_questions')
    closed_at = models.DateTimeField(null=True, blank=True)
    close_reason = models.SmallIntegerField(choices=CLOSE_REASONS, null=True, blank=True)
    score = models.IntegerField(default=0)
    answer_count   = models.PositiveIntegerField(default=0)
    comment_count  = models.PositiveIntegerField(default=0)
    view_count  = models.PositiveIntegerField(default=0)
    favourite_count = models.PositiveIntegerField(default=0)
    last_edited_at = models.DateTimeField(null=True, blank=True)
    last_edited_by = models.ForeignKey(User, null=True, blank=True, related_name='last_edited_questions')
    last_activity_at  = models.DateTimeField(auto_now_add=True)
    last_activity_by  = models.ForeignKey(User, related_name='last_active_in_questions')
    summary  = models.CharField(max_length=180)
    body  = models.TextField()

    objects =  QuestionManager.from_queryset(QuestionQuerySet)()

    tags = TaggableManager()

    def save(self, **kwargs):
        initial_addition = (self.id is None)

        # defaults
        if initial_addition:
            self.title = self.title[:199]
            self.last_activity_by = self.author
            self.summary = self.html[:179]

        super(Question, self).save(**kwargs)


    def __unicode__(self):
        return self.title

    def get_absolute_url(self):
        return '%s%s/' % (reverse('question', args=[self.id]),
                          slugify(self.title))

    def get_revision_url(self):
        return reverse('question_revisions', args=[self.id])

    def get_latest_revision(self):
        return self.revisions.all()[0]


    @property
    def html(self):
        return self.body

    @classmethod
    def ask(cls, user, title, body, tag_string):

        obj = cls.objects.create(author=user,
                                 title=title,
                                 body=body)
        obj.tags.add(*parse_tags(tag_string))

        award_points(user, "ASK_QUESTION")

        return obj

    def add_answer(self):
        self.answer_count += 1
        self.save()

    def remove_answer(self):
        self.answer_count -= 1
        self.save()

    def update_view_count(self, user):
        #TODO: hold user in memory for a bit so view count is not updated for another hour
        self.view_count += 1
        self.save()


    def vote(self, user, votes=1):
        return vote_on_obj(self, user, votes)

    def voted(self, user):
        return voted(self, user)

    def answer(self, user, body):

        a = Answer.objects.create(question=self, author=user, body=body)
        self.last_activity_at = datetime.datetime.now()
        self.last_activity_by = user
        self.save()

        self.add_answer()

        return a

    @property
    def live_answers(self):
        return Answer.objects.live().filter(question=self)


    def make_favourite(self, user):

        FavouriteQuestion.objects.get_or_create(question=self, user=user)


    def unmake_favourite(self, user):

        obj = FavouriteQuestion.objects.get(question=self, user=user)
        obj.delete()

    def is_favourite(self, user):

        try:
            FavouriteQuestion.objects.get(question=self, user=user)
            return True
        except FavouriteQuestion.DoesNotExist:
            return False

    def close(self, user, reason):
        from questionapp import auth  # here to avoid circular import

        if auth.can_close_question(user, self):
            self.closed_at = datetime.datetime.now()
            self.closed_by = user
            self.close_reason = reason
            self.save()
        else:
            raise PermissionDenied

    def reopen(self, user):
        from questionapp import auth  # here to avoid circular import

        if auth.can_close_question(user, self):
            self.closed_at = None
            self.closed_by = None
            self.close_reason = None
            self.save()
        else:
            raise PermissionDenied

    @property
    def closed(self):
        return self.closed_at is not None

# class AnswerManager(models.Manager):
#     def for_question(self, question, user=None):
#         if user is None or not user.is_authenticated():
#             return self.filter(question=question, deleted=False)
#         else:
#             return self.filter(Q(question=question),
#                                Q(deleted=False) | Q(deleted_by=user))

class AnswerQuerySet(models.QuerySet):
    def live(self):
        return self.filter(deleted=False)


class Answer(models.Model):
    question = models.ForeignKey(Question, related_name='answers')
    author   = models.ForeignKey(User, related_name='answers')
    added_at = models.DateTimeField(auto_now_add=True)
    accepted    = models.BooleanField(default=False)
    accepted_by    = models.ForeignKey(User, null=True, blank=True, related_name='accepted_answers')
    deleted     = models.BooleanField(default=False)
    deleted_by  = models.ForeignKey(User, null=True, blank=True, related_name='deleted_answers')
    locked      = models.BooleanField(default=False)
    locked_by   = models.ForeignKey(User, null=True, blank=True, related_name='locked_answers')
    locked_at   = models.DateTimeField(null=True, blank=True)
    score                = models.IntegerField(default=0)
    comment_count        = models.PositiveIntegerField(default=0)
    offensive_flag_count = models.SmallIntegerField(default=0)
    last_edited_at       = models.DateTimeField(auto_now_add=True)
    last_edited_by       = models.ForeignKey(User, null=True, blank=True, related_name='last_edited_answers')
    body                 = models.TextField()

    objects = AnswerQuerySet.as_manager()


    def __unicode__(self):
        return self.body[:100]

    def get_absolute_url(self):
        return reverse('answer', args=[self.id])

    def save(self, **kwargs):
        initial_addition = (self.id is None)

        # defaults
        if initial_addition:
            self.last_edited_by = self.author


        super(Answer, self).save(**kwargs)

    def delete(self, user=None, **kwargs):
        self.question.remove_answer()

        self.deleted_by = user
        self.deleted = True
        self.save()

    def get_latest_revision(self):
        return self.revisions.all()[0]

    @property
    def html(self):
        return self.body


    def vote(self, voter, votes=1):
        # if vote not accepted changed_votes = 0
        # if new vote for this object, changed_votes == votes
        # if changing vote, then changed_votes is difference between old and new votes

        return vote_on_obj(self, voter, votes)



    def voted(self, user):
        return voted(self, user)

    def user_can_accept(self, user):

        return user == self.question.author

    def can_change_accept(self, user):
        #TODO: probably not indefinately?

        return True
    def accept(self, user):
        '''
        accept an answer
        if another answer previously accepted, then override
        :param user:
        :return:
        '''
        accept_answer = False
        changing_answer = False
        if self.user_can_accept(user):
            if self.question.accepted_answer:
                if self.can_change_accept(user):
                    self.question.accepted_answer.unaccept()
                    changing_answer = True
                    accept_answer = True
            else:
                accept_answer = True

            if accept_answer:
                # update answer
                self.accepted = True
                self.accepted_by = user
                self.save()

                # update question
                self.question.accepted_answer = self
                self.question.save()

                # update user reputations
                if not changing_answer:
                    award_points(user, "ACCEPT_ANSWER")
                    award_points(self.author, "MY_ANSWER_ACCEPTED")


            return True
        else:
            return False

    def unaccept(self):

        award_points(self.author, "MY_ANSWER_ACCEPTED", reverse=True)

        self.accepted = False
        self.accepted_by = None
        self.save()

        #TODO: update reputations





class FavouriteQuestion(models.Model):
    question      = models.ForeignKey(Question)
    user          = models.ForeignKey(User)
    favourited_at = models.DateTimeField(default=datetime.datetime.now)

def update_question_favourite_count(instance, **kwargs):
    """
    Updates the favourite count for the Question related to the given
    FavouriteQuestion.
    """
    if kwargs.get('raw', False):
        return
    cursor = connection.cursor()
    cursor.execute(
        'UPDATE questionapp_question SET favourite_count = ('
        'SELECT COUNT(*) from questionapp_favouritequestion '
        'WHERE questionapp_favouritequestion.question_id = questionapp_question.id'
        ') '
        'WHERE id = %s', [instance.question_id])


post_save.connect(update_question_favourite_count, sender=FavouriteQuestion)
post_delete.connect(update_question_favourite_count, sender=FavouriteQuestion)

class VoteManager(models.Manager):
    def get_for_question_and_answers(self, user, question, answers):
        question_vote = None
        answer_votes = collections.defaultdict(lambda: None)
        # No need to check the database for anonymous users
        if not user.is_authenticated():
            return question_vote, answer_votes

        question_ct = ContentType.objects.get_for_model(Question)

        # Simpler case when only retrieving votes for a Question
        if not answers:
            try:
                question_vote = self.get(
                    content_type = question_ct,
                    object_id    = question.id,
                    user         = user
                )
            except Vote.DoesNotExist:
                pass
            return question_vote, answer_votes

        answer_ct = ContentType.objects.get_for_model(Answer)
        votes = self.filter(
            Q(content_type=question_ct, object_id=question.id) |
            Q(content_type=answer_ct,
              object_id__in=[answer.id for answer in answers]),
            user = user
        )

        for vote in votes:
            if vote.content_type_id == answer_ct.id:
                answer_votes[vote.object_id] = votes
            else:
                question_vote = votes
        return question_vote, answer_votes

class Vote(models.Model):

    content_type   = models.ForeignKey(ContentType)
    object_id      = models.PositiveIntegerField()
    content_object = generic.GenericForeignKey('content_type', 'object_id')
    user           = models.ForeignKey(User, related_name='votes')
    votes = models.SmallIntegerField(default=0)
    action = models.CharField(max_length=30)
    last_updated = models.DateTimeField(auto_now=True)

    objects = VoteManager()

    class Meta:
        unique_together = ('content_type', 'object_id', 'user')


    def __unicode__(self):
        return self.user


    def is_upvote(self):
        return self.votes > 0

    def is_downvote(self):
        return self.votes < 0

class Comment(models.Model):
    content_type   = models.ForeignKey(ContentType)
    object_id      = models.PositiveIntegerField()
    content_object = generic.GenericForeignKey('content_type', 'object_id')
    author           = models.ForeignKey(User, related_name='comments')
    comment        = models.CharField(max_length=300)
    added_at       = models.DateTimeField(default=datetime.datetime.now)

    class Meta:
        ordering = ('-added_at',)

def update_post_comment_count(instance, **kwargs):
    """
    Updates the comment count for the Question or Answer related to the
    given Comment.
    """
    pass
#     if kwargs.get('raw', False):
#         return
#     cursor = connection.cursor()
#     cursor.execute(
#         'UPDATE %(post_table)s SET comment_count = ('
#             'SELECT COUNT(*) from questionapp_comment '
#             'WHERE questionapp_comment.content_type_id = %%s '
#               'AND questionapp_comment.object_id = %(post_table)s.id'
#         ') '
#         'WHERE id = %%s' % {
#             'post_table': instance.content_type.model_class()._meta.db_table,
#         }, [instance.content_type_id, instance.object_id])

#
# post_save.connect(update_post_comment_count, sender=Comment)
# post_delete.connect(update_post_comment_count, sender=Comment)

def update_post_score(instance, **kwargs):
    pass
#     if kwargs.get('raw', False):
#         return
#     cursor = connection.cursor()
#     cursor.execute(
#         'UPDATE %(post_table)s SET score = ('
#             'SELECT COALESCE(SUM(vote), 0) from questionapp_vote '
#             'WHERE questionapp_vote.content_type_id = %%s '
#               'AND questionapp_vote.object_id = %(post_table)s.id'
#         ') '
#         'WHERE id = %%s' % {
#             'post_table': instance.content_type.model_class()._meta.db_table,
#         }, [instance.content_type_id, instance.object_id])
#     transaction.commit_unless_managed()
#
# post_save.connect(update_post_score, sender=Vote)
# post_delete.connect(update_post_score, sender=Vote)


def update_reputation(manager, changes):
    pass
    # change_count = len(changes)
    # cursor = connection.cursor()
    # cursor.execute(
    #     'UPDATE auth_user SET reputation = CASE %s ELSE reputation END '
    #     'WHERE id IN (%s)' % (
    #     ' '.join(['WHEN id = %s THEN MAX(1, reputation + %s)'] * change_count),
    #     ','.join(['%s'] * change_count)),
    #     flatten(changes) + [c[0] for c in changes])



class QUser(models.Model):
    ''' this is a multiprofile user model
    must have field called user as primary key
    all other fields must have defaults or be nullable
    '''

    user = models.OneToOneField(User, primary_key=True,)
    reputation = models.PositiveIntegerField(default=1)
    gravatar = models.CharField(max_length=64)
    last_seen = models.DateTimeField(default=datetime.datetime.now)


    def __unicode__(self):
        return self.user


    def save(self, **kwargs):

        # defaults
        if not self.gravatar:
            self.gravatar = self.calculate_gravatar_hash()

        super(QUser, self).save(**kwargs)

    def calculate_gravatar_hash(self, **kwargs):
        """Calculates a User's gravatar hash from their email address."""
        if kwargs.get('raw', False):
            return
        return hashlib.md5(self.user.email).hexdigest()

    def award_points(self, points):
        self.points += points
        self.save()
        return self.points

    def update_reputation(self, amount):
        self.reputation += amount
        self.save()
        return self.reputation

    def get_profile_url(self):
        return '%s%s/' % (reverse('user', args=[self.id]), self.username)

    @property
    def favorite_questions(self):

        return FavouriteQuestion.objects.filter(user=self.user)

def create_profile(sender, **kw):

    user = kw["instance"]
    if kw["created"]:
        up = QUser(user=user)
        up.save()


post_save.connect(create_profile, sender=User)

#UserManager.update_reputation = update_reputation

'''
User.add_to_class('reputation', models.PositiveIntegerField(default=1))
User.add_to_class('gravatar', models.CharField(max_length=64))
User.add_to_class('favourite_questions',
                  models.ManyToManyField(Question, through=FavouriteQuestion,
                                         related_name='favourited_by'))
User.add_to_class('last_seen',
                  models.DateTimeField(default=datetime.datetime.now))

def get_profile_url(self):
    return '%s%s/' % (reverse('user', args=[self.id]), self.username)

User.add_to_class('get_profile_url', get_profile_url)

def calculate_gravatar_hash(instance, **kwargs):
    """Calculates a User's gravatar hash from their email address."""
    if kwargs.get('raw', False):
        return
    instance.gravatar = hashlib.md5(instance.email).hexdigest()
pre_save.connect(calculate_gravatar_hash, sender=User)
'''

def _vote(obj, voter, votes=1):
    '''

    add votes to the obj passed
    :param obj: object eg. Question, Answer or Comment
    :param voter: User object
    :param votes: number of votes, positive or negative, defaults to 1
    :return: the amount the object's scores should be adjusted by:
        if the voter does not have rights to vote, this will be zero
        if this is a new vote then adj_votes will be the same as vote
        if this is an update to an existing vote, then it's new vote - old vote
        if the votes down match the previous votes up then delete Vote
    '''
    from questionapp import auth  # here to avoid circular import
    content_type = ContentType.objects.get_for_model(obj)
    model = str(content_type).upper()

    # get the voter profile in QUser
    quser = auth.get_user(voter)


    if votes > 0:
        action = "VOTE_%s_UP" % model

    elif votes < 0:
        action = "VOTE_%s_DOWN" % model
    else:
        return 0



    v = None
    try:
	    v = Vote.objects.get(content_type=content_type, object_id=obj.id, user=voter)
    except Vote.DoesNotExist:
        pass


    # handle special case where voting down same amount as previously voted up
    if v and action == "VOTE_DOWN" and v.action == "VOTE_UP":
        award_points(voter, "VOTE_UP", reverse=True)
        award_points(obj.user, "MY_%s_VOTED_UP" % model, reverse=True)
        v.delete()
        return 0
    else:
        adj_votes = votes
        if auth.has_action_permission(action, quser):

            if v:
                # if exists, no change to reputations
                adj_votes = votes - v.votes
                v.votes = votes
                v.save()
            else:
                v = Vote.objects.create(content_type=content_type, object_id=obj.id, user=voter, votes=votes)
                award_points(voter, action)
                award_points(obj.author, "MY_%s_%s" % (model, action))

        else:
            # don't have permission
            return 0


    return adj_votes

def vote_on_obj(obj, user, votes=1):
    '''
    votes are added/subtracted provided user has rights to vote
    adj_votes is the amount by which the score should be changed.
    if the user does not have rights to vote, this will be zero
    if this is a new vote then adj_votes will be the same as vote
    if this is an update to an existing vote, then it's new vote - old vote
    NOTE: this function will fail silently if user cannot vote.
    '''
    adj_votes = _vote(obj, user, votes)
    if adj_votes != 0:
        obj.score += adj_votes
        obj.save()

    return adj_votes

def voted(obj, user):
    '''
    return Vote object
    '''

    content_type = ContentType.objects.get_for_model(obj)

    try:
        return Vote.objects.get(content_type=content_type, object_id=obj.id, user=user)

    except Vote.DoesNotExist:
        return None


def award_points(user, action, reverse=False):
    '''
    can be passed a User instance or a QUser instance
    :param reverse: remove points, eg. if an answer is unaccepted
    :return:
    '''
    #TODO: add audit log of points awarded and removed

    if action not in settings.AWARD_POINTS:
        raise ValidationError("Invalid action for awarding points %s" % action)

    if isinstance(user, QUser):
        quser = user
    else:
        quser = QUser.objects.get(user=user)

    points = pointed_awarded_for(quser, action)
    if reverse:
        points = points * -1

    quser.update_reputation(points)


def pointed_awarded_for(user, action):
    '''
    user not currently used
    :param user:
    :param action:
    :return:
    '''

    return settings.AWARD_POINTS[action]