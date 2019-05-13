from django.db import models
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AbstractUser


def generate_url(instance, filename):
    """Generate url for user avatar"""
    file_type = filename.split('.')[-1]  # take file type (png, jpg, ..)
    last_id = UserAccount.objects.all().order_by('id')  # find last user
    if last_id:  # if exists
        last_id = last_id[0].id  # take his id
    if not last_id:  # else
        new_id = 1  # will be 1
    else:  # if exists
        new_id = last_id + 1  # plus 1
    filename = 'image-' + str(new_id) + '.' + file_type  # compare all
    return "avatars/" + filename  # returning url


class UserAccount(AbstractUser):
    """User account. Added fields"""
    def __str__(self):
        return str(self.username)

    @staticmethod
    def get_by_login(login):
        kwargs = {}

        try:
            c = UserAccount.objects.get(id=login, **kwargs)
        except (UserAccount.DoesNotExist, ValueError) as err:
            try:
                c = UserAccount.objects.get(username=login, **kwargs)
            except UserAccount.DoesNotExist:
                c = None
        return c

    class Meta:
        verbose_name = 'Аккаунт пользователя'
        verbose_name_plural = 'Аккаунты пользователей'
