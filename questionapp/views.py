# -*- coding: utf-8 -*-
from django.shortcuts import render, render_to_response, get_object_or_404
from django.core.paginator import Paginator, InvalidPage
from django.template import RequestContext
from django.contrib.auth import views as auth_views
import html5lib
from html5lib import sanitizer, serializer, tokenizer, treebuilders, treewalkers
from django.contrib.auth.decorators import login_required
from questionapp import auth
from django.utils.html import strip_tags, mark_safe
from lxml.html.diff import htmldiff
from django.http import HttpResponse,HttpResponseRedirect, Http404, JsonResponse
from django.core.exceptions import PermissionDenied
from django.contrib.auth.decorators import login_required

from questionapp.models import *
from questionapp.forms import *
from taggit.models import Tag, TaggedItem
from questionapp import auth


# Create your views here.
questions_per_page = 10
all_question_views = {
    'newest': {
        'id'          : 'newest',
        'page_title'  : 'Newest Questions',
        'tab_title'   : 'Newest',
        'tab_tooltip' : 'The most recently asked questions',
        'description' : 'sorted by the <strong>date they were asked</strong>. '
                      'The newest, most recently asked questions will appear '
                      'first',
        'ordering'    : ('-added_at',)
    },
    'answer': {
        'id'          : 'answer',
        'page_title'  : 'Most Answered Questions',
        'tab_title'   : 'Hot',
        'tab_tooltip' : 'Questions with most number of answers',
        'description' : 'sorted by <strong>hotness</strong>. Questions with the '
                      'most number of answers will appear first.'
    },
    'votes': {
        'id'          : 'votes',
        'page_title'  : 'Highest Voted Questions',
        'tab_title'   : 'Votes',
        'tab_tooltip' : 'Questions with the most votes',
        'description' : 'sorted by <strong>votes</strong>. The questions with '
                      ' the highest vote scores (up votes minus down votes) '
                      'will appear first.',
        'ordering'    : ('-score', '-added_at'),
    },
    'activity': {
        'id'           : 'activity',
        'page_title'   : 'Recently Active Questions',
        'tab_title'    : 'Activity',
        'tab_tooltip'  : 'Questions that have recent activity',
        'description'  : 'sorted by <strong>activity</strong>. Questions with '
                       'the most recent activity &mdash; either through new '
                       'answers or recent edits &mdash; will appear first.',
        'ordering'     : ('-last_activity_at',),
        'user'         : 'last_activity_by',
        'user_action'  : 'modified',
        'time'         : 'last_activity_at'
    }
}


def home(request):

    sort =  request.GET.get('sort', None)
    questions = Question.objects.live()
    view = all_question_views.get(sort,all_question_views.get('newest',False))
    paginator = Paginator(questions, questions_per_page)
    page = paginator.page(1)
    if sort:
    	questions.order_by(sort)
    context = {
        'title': view.get('page_title'),
        'page': page,
        'questions': page.object_list,
        'current_view': 'new',
        'question_views': all_question_views,
    }
    return render_to_response('index.html', context, context_instance=RequestContext(request))


def question(request, question_id):

    user = request.user

    question = get_object_or_404(Question, id=question_id)

    if not user.is_authenticated():

        favourite = False
    else:

        favourite = question.is_favourite(user)

	question.update_view_count(user)

    if 'showcomments' in request.GET:
        return question_comments(request, question)

    question_vote = 1
    answer_votes = 1

    title = question.title
    if question.closed:
        title = '%s [closed]' % title

    related_questions = list(set(Question.objects.filter(tags__in=question.tags.all()).exclude(id = question.id)))
    if len(related_questions) > 10:
	related_questions = related_questions[:10]

    return render_to_response('question.html', {
        'title': title,
        'question': question,
        'question_vote': question_vote,
        'favourite': favourite,
        'answers': question.answers,
        'answer_votes': answer_votes,

        'answer_sort': 'votes',
        'answer_form': AddAnswerForm(),
        'related_questions':related_questions,
        'tags': question.tags.all(),
    }, context_instance=RequestContext(request))


@login_required
def close_question(request, question_id):

    question = get_object_or_404(Question, id=question_id)

    if question.closed:
        return HttpResponseRedirect(reverse('reopen_question', kwargs={'question_id' : question_id}))

    user = request.user
    if not auth.can_close_question(user, question):
        raise PermissionDenied()


    if request.method == 'POST' and 'close' in request.POST:
        form = CloseQuestionForm(request.POST)
        if form.is_valid():
            question.close(user,form.cleaned_data['reason'] )

            if request.is_ajax():
                return JsonResponse({'success': True})
            else:
                return HttpResponseRedirect(question.get_absolute_url())
        elif request.is_ajax():
            return JsonResponse({'success': False, 'errors': form.errors})
    else:
        if request.is_ajax():
            raise Http404
        form = CloseQuestionForm()
    return render_to_response('close_question.html', {
        'title': u'Close Question',
        'question': question,
        'form': form,
    }, context_instance=RequestContext(request))

@login_required
def reopen_question(request, question_id):

    question = get_object_or_404(Question, id=question_id)

    if not question.closed:
        return HttpResponseRedirect(reverse('open_question', kwargs={'question_id' : question_id}))

    user = request.user
    if not auth.can_close_question(user, question):
        raise PermissionDenied()


    if request.method == 'POST' and 'reopen' in request.POST:
        question.reopen(user)
        if request.is_ajax():
            return JsonResponse({'success': True})
        else:
            return HttpResponseRedirect(question.get_absolute_url())
    if request.is_ajax():
        raise Http404
    return render_to_response('reopen_question.html', {
        'title': u'Reopen Question',
        'question': question,
    }, context_instance=RequestContext(request))


def search(request):
    query = request.GET.get('q','')
    sort =  request.GET.get('sort', None)
    questions = Question.objects.filter(title__contains=query)
    view = all_question_views.get(sort,all_question_views.get('newest',False))
    paginator = Paginator(questions, questions_per_page)
    page = paginator.page(1)
    if sort:
    	questions.order_by(sort)
    context = {
        'title': view.get('page_title'),
        'page': page,
        'questions': page.object_list,
        'current_view': {'id':'new'},
        'question_views': all_question_views,
    }
    return render_to_response('questions.html', context, context_instance=RequestContext(request))

def tags(request):

    tags = Tag.objects.all().order_by('-use_count', 'name')
    name_filter = request.GET.get('filter', '')
    if name_filter:
        tags = tags.filter(name__icontains=name_filter)
    paginator = Paginator(tags, 50)
    page = get_page(request, paginator)
    return render_to_response('tags.html', {
        'title': u'Tags',
        'tags': page.object_list,
        'page': page,
        'sort': 'popular',
        'filter': name_filter,
    }, context_instance=RequestContext(request))

def tag(request, tag_name):
    tag = Tag.objects.filter(name = tag_name)[0]
    questions = Question.objects.filter(tags__in=[tag])
    sort =  request.GET.get('sort', None)
    view = all_question_views.get(sort,all_question_views.get('newest',False))
    paginator = Paginator(questions, questions_per_page)
    page = paginator.page(1)
    if sort:
    	questions.order_by(sort)
    context = {
        'title': view.get('page_title'),
        'page': page,
        'questions': page.object_list,
        'current_view': {'id':'new'},
        'question_views': all_question_views,
    }
    return render_to_response('questions.html', context, context_instance=RequestContext(request))

def users(request):
    users = QUser.objects.all().order_by('-reputation', '-user__date_joined')
    name_filter = request.GET.get('filter', '')
    if name_filter:
        users = users.filter(username__icontains=name_filter)
    users = users.values('user__id', 'user__username', 'gravatar',  'reputation')
    paginator = Paginator(users, 20)
    page = get_page(request, paginator)
    return render_to_response('users.html', {
        'title': u'Users',
        'users': page.object_list,
        'page': page,
        'sort': 'reputation',
        'filter': name_filter,
    }, context_instance=RequestContext(request))

def user_profile(request, user_id):
    """Displays a User and various information about them."""
    user = get_object_or_404(User, id=user_id)
    return render_to_response('user.html', {
        'title': user.username,
        'user': user
    }, context_instance=RequestContext(request))

def badges(request):
    return render_to_response('badges.html', {
        'title': u'Badges',
        'badges': [],
    }, context_instance=RequestContext(request))

def get_page(request, paginator, page_param='page'):
    try:
        page = int(request.GET.get(page_param, '1'))
    except ValueError:
        page = 1
    try:
        return paginator.page(page)
    except EmptyPage:
        return paginator.page(paginator.num_pages)

def profile(request):

    user = request.user

    return render_to_response('user.html', {
        'title': user.username,
        'user': user
    }, context_instance=RequestContext(request))

def questions(request):
    sort =  request.GET.get('sort', None)
    questions = Question.objects.all()
    view = all_question_views.get(sort,all_question_views.get('newest',False))
    paginator = Paginator(questions, questions_per_page)
    page = paginator.page(1)
    if sort:
    	questions.order_by(sort)
    context = {
        'title': view.get('page_title'),
        'page': page,
        'questions': page.object_list,
        'current_view': {'id':'new'},
        'question_views': all_question_views,
    }
    return render_to_response('questions.html', context, context_instance=RequestContext(request))

def unanswered(request):
    sort =  request.GET.get('sort', None)
    questions = Question.objects.filter(answer_count = 0)
    view = all_question_views.get(sort,all_question_views.get('newest',False))
    paginator = Paginator(questions, questions_per_page)
    page = paginator.page(1)
    if sort:
    	questions.order_by(sort)
    context = {
        'title': 'Unanswered Questions',
        'page': page,
        'questions': page.object_list,
        'current_view':{'id':'new'},
        'question_views': all_question_views,
    }
    return render_to_response('unanswered.html', context, context_instance=RequestContext(request))

class HTMLSanitizerMixin(sanitizer.HTMLSanitizerMixin):
    acceptable_elements = ('a', 'abbr', 'acronym', 'address', 'b', 'big',
        'blockquote', 'br', 'caption', 'center', 'cite', 'code', 'col',
        'colgroup', 'dd', 'del', 'dfn', 'dir', 'div', 'dl', 'dt', 'em', 'font',
        'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'hr', 'i', 'img', 'ins', 'kbd',
        'li', 'ol', 'p', 'pre', 'q', 's', 'samp', 'small', 'span', 'strike',
        'strong', 'sub', 'sup', 'table', 'tbody', 'td', 'tfoot', 'th', 'thead',
        'tr', 'tt', 'u', 'ul', 'var')

    acceptable_attributes = ('abbr', 'align', 'alt', 'axis', 'border',
        'cellpadding', 'cellspacing', 'char', 'charoff', 'charset', 'cite',
        'cols', 'colspan', 'datetime', 'dir', 'frame', 'headers', 'height',
        'href', 'hreflang', 'hspace', 'lang', 'longdesc', 'name', 'nohref',
        'noshade', 'nowrap', 'rel', 'rev', 'rows', 'rowspan', 'rules', 'scope',
        'span', 'src', 'start', 'summary', 'title', 'type', 'valign', 'vspace',
        'width')

    allowed_elements = acceptable_elements
    allowed_attributes = acceptable_attributes
    allowed_css_properties = ()
    allowed_css_keywords = ()
    allowed_svg_properties = ()

class HTMLSanitizer(tokenizer.HTMLTokenizer, HTMLSanitizerMixin):
    def __init__(self, stream, encoding=None, parseMeta=True, useChardet=True,
                 lowercaseElementName=True, lowercaseAttrName=True):
        tokenizer.HTMLTokenizer.__init__(self, stream, encoding, parseMeta,
                                         useChardet, lowercaseElementName,
                                         lowercaseAttrName)

    def __iter__(self):
        for token in tokenizer.HTMLTokenizer.__iter__(self):
            token = self.sanitize_token(token)
            if token:
                yield token

def sanitize_html(html):
    return html

    #TODO: Fails on parseFragment - for now assume html is text
    p = html5lib.HTMLParser(tokenizer=HTMLSanitizer,
                            tree=treebuilders.getTreeBuilder("dom"))
    dom_tree = p.parseFragment(html)
    walker = treewalkers.getTreeWalker("dom")
    stream = walker(dom_tree)
    s = serializer.HTMLSerializer(omit_optional_tags=False,
                                  quote_attr_values=True)
    output_generator = s.serialize(stream)
    return u''.join(output_generator)

def edit_answer(request, answer_id):

    user = request.user

    answer = get_object_or_404(Answer, id=answer_id)
    latest_revision = answer.get_latest_revision()
    preview = None
    revision_form = None
    if request.method == 'POST':
        if 'select_revision' in request.POST:
            revision_form = RevisionForm(answer, latest_revision, request.POST)
            if revision_form.is_valid():
                form = EditAnswerForm(answer,
                    AnswerRevision.objects.get(answer=answer,
                        revision=revision_form.cleaned_data['revision']))
            else:
                form = EditAnswerForm(answer, latest_revision, request.POST)
        else:
            form = EditAnswerForm(answer, latest_revision, request.POST)
            if form.is_valid():
                html = sanitize_html(form.cleaned_data['text'])
                if 'preview' in request.POST:
                    preview = mark_safe(html)
                elif 'submit' in request.POST:
                    if form.has_changed():
                        edited_at = datetime.datetime.now()
                        updated_fields = {
                            'last_edited_at': edited_at,
                            'last_edited_by': user,
                            'html': html,
                        }
                        Answer.objects.filter(
                            id=answer.id).update(**updated_fields)
                        revision = AnswerRevision(
                            answer = answer,
                            author = user,
                            revised_at = edited_at,
                            text = form.cleaned_data['text']
                        )
                        if form.cleaned_data['summary']:
                            revision.summary = form.cleaned_data['summary']
                        else:
                            revision.summary = 'not specified'
                        revision.save()
                    return HttpResponseRedirect(answer.question.get_absolute_url())
    else:
        revision_form = RevisionForm(answer, latest_revision)
        form = EditAnswerForm(answer, latest_revision)
    if revision_form is None:
        revision_form = RevisionForm(answer, latest_revision, request.POST)
    return render_to_response('edit_answer.html', {
        'title': u'Edit Answer',
        'question': answer.question,
        'answer': answer,
        'revision_form': revision_form,
        'form': form,
        'preview': preview,
    }, context_instance=RequestContext(request))

def edit_question(request, question_id):
    user = request.user
    question = get_object_or_404(Question, id=question_id)
    if auth.can_edit_post(user, question):
        return _edit_question(request, question)
    elif auth.can_retag_questions(user):
        return _retag_question(request, question)
    else:
        raise Http404

def _edit_question(request, question):

    user = request.user
    latest_revision = question.get_latest_revision()
    preview = None
    revision_form = None
    if request.method == 'POST':
        # if 'select_revision' in request.POST:
        #     revision_form = RevisionForm(question, latest_revision, request.POST)
        #     if revision_form.is_valid():
        #         form = EditQuestionForm(question,
        #             QuestionRevision.objects.get(question=question,
        #                 revision=revision_form.cleaned_data['revision']))
        #     else:
        #         form = EditQuestionForm(question, latest_revision, request.POST)
        # else:
            form = EditQuestionForm(question, latest_revision, request.POST)
            if form.is_valid():
                html = sanitize_html(form.cleaned_data['text'])
                if 'preview' in request.POST:
                    preview = mark_safe(html)
                elif 'submit' in request.POST:
                    if form.has_changed():
                        edited_at = datetime.datetime.now()
                        tags_changed = (latest_revision.tagnames !=
                                        form.cleaned_data['tags'])
                        tags_updated = False
                        updated_fields = {
                            'title': form.cleaned_data['title'],
                            'last_edited_at': edited_at,
                            'last_edited_by': user,
                            'last_activity_at': edited_at,
                            'last_activity_by': user,
                            'tagnames': form.cleaned_data['tags'],
                            'summary': strip_tags(html)[:180],
                            'html': html,
                        }
                        Question.objects.filter(
                            id=question.id).update(**updated_fields)
                        if tags_changed:
                            tags_updated = Question.objects.update_tags(
                                question, question.tagnames, user)
                        # revision = QuestionRevision(
                        #     question   = question,
                        #     title      = form.cleaned_data['title'],
                        #     author     = user,
                        #     revised_at = edited_at,
                        #     tagnames   = form.cleaned_data['tags'],
                        #     text       = form.cleaned_data['text']
                        # )
                        # if form.cleaned_data['summary']:
                        #     revision.summary = form.cleaned_data['summary']
                        # else:
                        #     revision.summary ='not specified'
                        # revision.save()
                    return HttpResponseRedirect(question.get_absolute_url())
    else:
        if 'revision' in request.GET:
            revision_form = RevisionForm(question, latest_revision, request.GET)
            # if revision_form.is_valid():
            #     form = EditQuestionForm(question,
            #         QuestionRevision.objects.get(question=question,
            #             revision=revision_form.cleaned_data['revision']))
        else:
            revision_form = RevisionForm(question, latest_revision)
            form = EditQuestionForm(question, latest_revision)
    if revision_form is None:
        revision_form = RevisionForm(question, latest_revision, request.POST)
    return render_to_response('edit_question.html', {
        'title': u'Edit Question',
        'question': question,
        'revision_form': revision_form,
        'form': form,
        'preview': preview,
    }, context_instance=RequestContext(request))

def question_revisions(request, question_id):
    question = get_object_or_404(Question, id=question_id)
    revisions = list(question.revisions.all())
    # populate_foreign_key_caches(User, ((revisions, ('author',)),),
    #      fields=('username', 'gravatar', 'reputation', 'gold', 'silver',
    #              'bronze'))
    for i, revision in enumerate(revisions):
        revision.html = QUESTION_REVISION_TEMPLATE % {
            'title': revision.title,
            'html': sanitize_html(revision.text),
            'tags': ' '.join(['<a class="tag">%s</a>' % tag
                              for tag in revision.tagnames.split(' ')]),
        }
        if i > 0:
            revisions[i - 1].diff = htmldiff(revision.html,
                                             revisions[i - 1].html)
    return render_to_response('question_revisions.html', {
        'title': u'Question Revisions',
        'question': question,
        'revisions': revisions,
    }, context_instance=RequestContext(request))



def _retag_question(request, question):

    user = request.user

    if request.method == 'POST':
        form = RetagQuestionForm(question, request.POST)
        if form.is_valid():
            if form.has_changed():
                latest_revision = question.get_latest_revision()
                retagged_at = datetime.datetime.now()
                Question.objects.filter(id=question.id).update(
                    tagnames         = form.cleaned_data['tags'],
                    last_edited_at   = retagged_at,
                    last_edited_by   = user,
                    last_activity_at = retagged_at,
                    last_activity_by = user
                )
                tags_updated = Question.objects.update_tags(question,
                    form.cleaned_data['tags'], user)
                # QuestionRevision.objects.create(
                #     question   = question,
                #     title      = latest_revision.title,
                #     author     = user,
                #     revised_at = retagged_at,
                #     tagnames   = form.cleaned_data['tags'],
                #     summary    = u'modified tags',
                #     text       = latest_revision.text
                #)
            return HttpResponseRedirect(question.get_absolute_url())
    else:
        form = RetagQuestionForm(question)
    return render_to_response('retag_question.html', {
        'title': u'Edit Tags',
        'question': question,
        'form': form,
    }, context_instance=RequestContext(request))



@login_required
def vote(request, model, object_id):

    user = request.user

    if request.method != 'POST':
        raise Http404
    vote_type = request.POST.get('type', None)

    obj = get_object_or_404(model, id=object_id)

    if vote_type == 'up':
        votes = 1
    else:
        votes = -1

    vote_on_obj(obj, user, votes)

    return HttpResponseRedirect(obj.get_absolute_url())

def add_comment(request, model, object_id):

    user = request.user

    obj = get_object_or_404(model, id=object_id)
    if request.method == "POST":
        form = CommentForm(request.POST)
        if form.is_valid():
            Comment.objects.create(
                content_type = ContentType.objects.get_for_model(model),
                object_id    = object_id,
                author       = user,
                added_at     = datetime.datetime.now(),
                comment      = form.cleaned_data['comment']
            )
            if request.is_ajax():
                return JsonResponse({'success': True})
            else:
                return HttpResponseRedirect(obj.get_absolute_url())
        elif request.is_ajax():
            return JsonResponse({'success': False, 'errors': form.errors})
    else:
        form = CommentForm()

    if model is Question:
        return question_comments(request, obj, form=form)
    elif model is Answer:
        return answer_comments(request, object_id, answer=obj, form=form)

def answer_comments(request, answer_id, answer=None, form=None):
    if answer is None:
        answer = get_object_or_404(Answer, id=answer_id)
    content_type = ContentType.objects.get_for_model(Answer)
    comments = Comment.objects.filter(content_type=content_type,
                                      object_id=answer.id)
    if form is None:
        form = CommentForm()
    return render_to_response('answer.html', {
        'title': u'Answer Comments',
        'answer': answer,
        'comments': comments,
        'comment_form': form,
    }, context_instance=RequestContext(request))

def accept_answer(request, answer_id):

    user = request.user

    answer = get_object_or_404(Answer, id=answer_id)
    answer.accept(user)
    return HttpResponseRedirect(answer.question.get_absolute_url())


def add_answer(request, question_id):

    user = request.user

    question = get_object_or_404(Question, id=question_id)
    preview = None
    if request.method == 'POST':
        form = AddAnswerForm(request.POST)
        if form.is_valid():
            html = sanitize_html(form.cleaned_data['text'])
            if 'preview' in request.POST:
                preview = mark_safe(html)
            elif 'submit' in request.POST:
                answer = question.answer(user, html)

                return HttpResponseRedirect(question.get_absolute_url())
    else:
        form = AddAnswerForm()
    return render_to_response('add_answer.html', {
        'title': u'Post an Answer',
        'question': question,
        'form': form,
        'preview': preview,
    }, context_instance=RequestContext(request))

@login_required
def ask_question(request):

    user = request.user
    quser = QUser.objects.get(user=user)

    preview = None
    if request.method == 'POST':
        form = AskQuestionForm(request.POST)
        if form.is_valid():
            html = sanitize_html(form.cleaned_data['text'])
            if 'preview' in request.POST:
                preview = mark_safe(html)
            elif 'submit' in request.POST:

                question = Question.ask(user, form.cleaned_data['title'], html, form.cleaned_data['tags'])

                # QuestionRevision.objects.create(
                #     question   = question,
                #     revision   = 1,
                #     title      = question.title,
                #     author     = user,
                #     revised_at = added_at,
                #     tagnames   = question.tagnames,
                #     summary    = u'asked question',
                #     text       = form.cleaned_data['text']
                # )




                return HttpResponseRedirect(question.get_absolute_url())
    else:
        	form = AskQuestionForm()
    return render_to_response('ask_question.html', {
        'title': u'Ask a Question',
        'form': form,
        'preview': preview,
    }, context_instance=RequestContext(request))

def question_comments(request, question, form=None):
    content_type = ContentType.objects.get_for_model(Question)
    comments = Comment.objects.filter(content_type=content_type,
                                      object_id=question.id)

    if form is None:
        form = CommentForm()

    return render_to_response('question.html', {
        'title': u'Comments on %s' % question.title,
        'question': question,
        'tags': question.tags.all(),
        'comments': comments,
        'comment_form': form,
    }, context_instance=RequestContext(request))

def update_user_reputation(request, user, score):

    quser = QUser.objects.get(user=request.user)
    quser.reputation =  quser.reputation +score
    user.save()
    return True

@login_required
def favourite_question(request, question_id):

    user = request.user
    if request.method != 'POST':
        raise Http404

    question = get_object_or_404(Question, id=question_id)
    favourite, created = FavouriteQuestion.objects.get_or_create(
        user=user, question=question)
    if not created:
        favourite.delete()
    if request.is_ajax():
        return JsonResponse({'success': True, 'favourited': created})
    else:
        return HttpResponseRedirect(question.get_absolute_url())

