from django.conf.urls import *
from questionapp.models import Answer, Question
from django.views.generic.base import RedirectView



urlpatterns = patterns('questionapp.views',

    url(r'^$','home',name='home'),
    url(r'^search/$','search',name='search'),
    url(r'^questions/(?P<object_id>\d+)/vote/$',         'vote',               name='vote_on_question', kwargs={'model': Question}),
    url(r'^questions/(?P<question_id>\d+)/favourite/$',  'favourite_question', name='favourite_question'),
    url(r'^questions/$','questions',name='questions'),
    url(r'^questions/ask/$','ask_question',name='ask_question'),
    url(r'^questions/tagged/(?P<tag_name>[^/]+)/$','tag',name='tag'),
    url(r'^questions/(?P<question_id>\d+)/revisions/$','question_revisions',name='question_revisions'),
    url(r'^questions/(?P<question_id>\d+)/answer/$','add_answer',name='add_answer'),
    url(r'^answers/(?P<answer_id>\d+)/edit/$','edit_answer',name='edit_answer'),
    url(r'^questions/(?P<question_id>\d+)/edit/$','edit_question',name='edit_question'),
    url(r'^questions/(?P<question_id>\d+)/close/$','close_question',name='close_question'),
    url(r'^questions/(?P<question_id>\d+)/reopen/$','reopen_question',name='reopen_question'),
    url(r'^questions/(?P<question_id>\d+)/(?:[^/]+/)?$','question',name='question'),
    url(r'^tags/$','tags',name='tags'),
    url(r'^users/$','users',name='users'),
    url(r'^users/(?P<user_id>\d+)/(?:[^/]+/)?$','user_profile',name='user'),
    url(r'^users/(?:[^/]+/)?$','profile',name='profile'),
    url(r'^badges/$','badges',name='badges'),
    url(r'^unanswered/$','unanswered',name='unanswered'),
    url(r'^answers/(?P<object_id>\d+)/vote/$','vote',name='vote_on_answer',kwargs={'model': Answer}),
    url(r'^answers/(?P<answer_id>\d+)/accept/$','accept_answer',name='accept_answer'),
    url(r'^answers/(?P<answer_id>\d+)/$','answer_comments',name='answer'),
    url(r'^questions/(?P<object_id>\d+)/comment/$','add_comment',name='add_question_comment',kwargs={'model': Question}),
    url(r'^answers/(?P<object_id>\d+)/comment/$','add_comment',name='add_answer_comment', kwargs={'model': Answer}),
    

    
)
