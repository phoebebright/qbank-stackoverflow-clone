from django.conf import settings
from datetime import datetime
from questionapp.models import QUser

def get_quser(request):
    """
    add quser to templates
    """

    if request.user:
        if request.user.is_anonymous():
            quser = None
        else:
            if request.user.id:
                  quser = QUser.objects.get(user=request.user)

    else:
        quser = None

    return {'user': request.user,
        'quser': quser,
    }
