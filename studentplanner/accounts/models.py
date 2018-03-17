from django.contrib.auth.models import User as AuthUser, PermissionsMixin


class User(AuthUser, PermissionsMixin):
    def __str__(self):
        return "{}".format(self.username)
