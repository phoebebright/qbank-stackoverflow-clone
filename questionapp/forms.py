import datetime
import random
import re
from questionapp.models import *
from django import forms
from django.template.defaultfilters import slugify

tagname_re = re.compile(r'^[-a-z0-9+#.]+$')
tag_split_re = re.compile(r'[ ;,]')

RESERVED_TITLES = (u'answer', u'close', u'edit', u'delete', u'favourite',
                   u'comment', u'flag', u'vote')

class TagnameField(forms.CharField):
    def clean(self, value):
        value = super(TagnameField, self).clean(value)
        if value == u'':
            return value
        tagnames = [name for name in tag_split_re.split(value) if name]
        if len(tagnames) > 5:
            raise forms.ValidationError(u'You may only enter up to 5 tags.')
        for tagname in tagnames:
            if len(tagname) > 24:
                raise forms.ValidationError(u'Each tag may be no more than 24 '
                                            u'characters long.')
            if not tagname_re.match(tagname):
                raise forms.ValidationError(u'Tags may only include the '
                                            u'following characters: '
                                            u'[a-z 0-9 + # - .]')
        if len(tagnames) != len(set(tagnames)):
            raise forms.ValidationError(u'The same tag was entered multiple '
                                        u'times.')
        return u' '.join(tagnames)

class RevisionForm(forms.Form):
    revision = forms.ChoiceField()
    def __init__(self, post, latest_revision, *args, **kwargs):
        super(RevisionForm, self).__init__(*args, **kwargs)
        revisions = post.revisions.all().values_list(
            'revision', 'author__username', 'revised_at', 'summary')
        if (len(revisions) > 1 and
            (revisions[0][2].year == revisions[len(revisions)-1][2].year ==
             datetime.datetime.now().year)):
            # All revisions occured this year, so don't show the revision year
            date_format = '%b %d at %H:%M'
        else:
            date_format = '%b %d %Y at %H:%M'
        self.fields['revision'].choices = [
            (r[0], u'%s - %s (%s) %s' % (r[0], r[1], r[2].strftime(date_format), r[3]))
            for r in revisions]
        self.fields['revision'].initial = latest_revision.revision

class MarkdownTextArea(forms.Textarea):
    class Media:
        js = ('js/wmd/wmd.js',)

def clean_question_title(form):
    if slugify(form.cleaned_data['title']) in RESERVED_TITLES:
        raise forms.ValidationError(
            u'This title is invalid - please choose another.')
    return form.cleaned_data['title']

class EditQuestionForm(forms.Form):
    title   = forms.CharField(max_length=300)
    text    = forms.CharField(widget=MarkdownTextArea())
    tags    = TagnameField()
    summary = forms.CharField(max_length=300, required=False, label=u'Edit Summary')

    def __init__(self, question, revision, *args, **kwargs):
        super(EditQuestionForm, self).__init__(*args, **kwargs)
        self.fields['title'].initial = revision.title
        self.fields['text'].initial = revision.text
        self.fields['tags'].initial = revision.tagnames
        

    clean_title = clean_question_title

class EditAnswerForm(forms.Form):
    text    = forms.CharField(widget=MarkdownTextArea())
    summary = forms.CharField(max_length=300, required=False, label=u'Edit Summary')

    def __init__(self, answer, revision, *args, **kwargs):
        super(EditAnswerForm, self).__init__(*args, **kwargs)
        self.fields['text'].initial = revision.text
        

class AskQuestionForm(forms.Form):
    title = forms.CharField(max_length=300)
    text  = forms.CharField(widget=MarkdownTextArea())
    tags  = TagnameField()
    clean_title = clean_question_title

class AddAnswerForm(forms.Form):
    text = forms.CharField(widget=MarkdownTextArea())

class CloseQuestionForm(forms.Form):
    reason = forms.ChoiceField(choices=Question.CLOSE_REASONS)

class CommentForm(forms.Form):
    comment = forms.CharField(min_length=10, max_length=300, widget=forms.Textarea(attrs={'maxlength': 300, 'cols': 70, 'rows': 2}))
