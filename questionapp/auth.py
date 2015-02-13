from questionapp.models import QUser
from django.shortcuts import render, render_to_response, get_object_or_404
from django.conf import settings

import re

def points_required_to(action):
    return settings.MIN_POINTS[action]


def get_user(user):
    '''
    functions below can be passed a User instance or a QUser instance
    :param user:
    :return:
    '''

    if isinstance(user, QUser):
        return user
    else:
        if user.is_anonymous():
            return False
        else:
            return QUser.objects.get(user=user)
        
def has_action_permission(action, user):

    if re.search( r'VOTE_(.*)_UP', action, re.I):
        return can_vote_up(user)

    if re.search( r'VOTE_(.*)_DOWN', action, re.I):
        return can_vote_down(user)

    if action == "ACCEPT_ANSWER":
        return can_accept_answer(user)

def can_vote_up(user):
    """Determines if a User can vote Questions and Answers up."""
    quser = get_user(user)
    if quser:
        return (
            quser.reputation >= points_required_to("VOTE_UP") or
            quser.user.is_superuser)

def can_flag_offensive(user):
    """Determines if a User can flag Questions and Answers as offensive."""
    quser = get_user(user)
    if quser:
        return (
        quser.reputation >= points_required_to("FLAG_OFFENSIVE") or
        quser.user.is_superuser)

def can_add_comments(user):
    """Determines if a User can add comments to Questions and Answers."""
    quser = get_user(user)
    if quser:
        return (
        quser.reputation >= points_required_to("LEAVE_COMMENTS") or
        quser.user.is_superuser)

def can_vote_down(user):
    """Determines if a User can vote Questions and Answers down."""
    quser = get_user(user)
    if quser:
        return (
        quser.reputation >= points_required_to("VOTE_DOWN") or
        quser.user.is_superuser)

def can_retag_questions(user):
    """Determines if a User can retag Questions."""
    quser = get_user(user)
    if quser:
        return user.is_authenticated() and (
        points_required_to("RETAG_OTHER_QUESTIONS") <= quser.reputation < points_required_to("EDIT_OTHER_POSTS"))

def can_edit_post(user, post):
    """Determines if a User can edit the given Question or Answer."""
    quser = get_user(user)
    if quser:
        return (
        quser.user.id == post.author_id or
        quser.reputation >= points_required_to("EDIT_OTHER_POSTS") or
        quser.user.is_superuser)

def can_accept_answer(user, post):
    quser = get_user(user)
    if quser:
        return (
        quser.user.id == post.author_id or
        quser.user.is_superuser)

def can_delete_comment(user, comment):
    """Determines if a User can delete the given Comment."""
    quser = get_user(user)
    return (
        quser.user.id == comment.user_id or
        quser.reputation >= points_required_to("DELETE_COMMENTS") or
        quser.user.is_superuser)

def can_view_offensive_flags(user):
    """Determines if a User can view offensive flag counts."""
    quser = get_user(user)
    if quser:
        return (
        quser.reputation >= points_required_to("VIEW_OFFENSIVE_FLAGS") or
        quser.user.is_superuser)

def can_close_question(user, question):
    """Determines if a User can close the given Question."""
    quser = get_user(user)
    if quser:
        return  (
        (quser.user.id == question.author_id and
         quser.reputation >= points_required_to("CLOSE_OWN_QUESTIONS")) or
        quser.reputation >= points_required_to("CLOSE_OTHER_QUESTIONS") or
        quser.user.is_superuser)

def can_lock_posts(user):
    """Determines if a User can lock Questions or Answers."""
    quser = get_user(user)
    if quser:
        return quser.reputation >= points_required_to("LOCK_POSTS") or quser.user.is_superuser
