from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model
from django.conf import settings

class MultiModelBackend(ModelBackend):
    """
    Authenticates against settings.AUTH_USER_MODEL.
    """

    def authenticate(self, username=None, password=None, **kwargs):
        user = super(MultiModelBackend, self).authenticate(username=username, password=password, **kwargs)

        # if user successfully logged in
        if user:
            # check each app with a profile has an instance
            for app in settings.PROFILE_MODELS:
                module_name, model_name = app.rsplit('.', 1)
                module = __import__(module_name)
                profile = getattr(module.models, model_name)

                p, _created = profile.objects.get_or_create(user=user)

                # any clever way to add attributes to the user object?

        return user