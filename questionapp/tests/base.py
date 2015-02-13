from django.contrib.auth import get_user_model
from questionapp.models import *
from django.conf import settings

from django.contrib.sites.models import Site

def add_initial_data(sender, **kwargs):

        print "add_initial_data"
        User = get_user_model()



        # add system users
        try:
            User.objects.get(username='pbright')
        except User.DoesNotExist:
            User.objects.create_superuser('pbright', 'phoebebright@spamcop.net', 'cabbage')

        # add default site

        try:
            Site.objects.get(id=1)
        except Site.DoesNotExist:
            Site.objects.create(id=1, domain=settings.SITE_URL[8:], name='CCC')


        User.objects.create_user('user1','user1@greenmyday.com', 'PASS' )
        User.objects.create_user('user2','user2@greenmyday.com', 'PASS' )
        User.objects.create_user('user3','user3@greenmyday.com', 'PASS' )
        User.objects.create_user('user4','user4@greenmyday.com', 'PASS' )
        User.objects.create_user('user5','user5@greenmyday.com', 'PASS' )



def load_lots():

    user1= User.objects.get(username="user1")
    user2= User.objects.get(username="user2")
    user3= User.objects.get(username="user3")
    user4= User.objects.get(username="user4")
    user5= User.objects.get(username="user5")

    q1 = Question.ask(user1, "How hot is the sun","really hot?", "mineral" )
    q2 = Question.ask(user2, "How cold is the moon","really cold?", "mineral" )
    q3 = Question.ask(user3, "How green is the grass","really green?", "vegetable" )

    # q4 has two answers and no votes
    q4 = Question.ask(user3, "How brown is the mud","really brown?", "mineral" )
    q4.answer(user1, "more green")
    q4.answer(user2, "with yellow")