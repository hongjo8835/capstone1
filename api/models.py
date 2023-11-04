from django.db import models
from django.contrib.auth.models import BaseUserManager, AbstractBaseUser


# Create your models here.
class UserManager(BaseUserManager):
    def create_user(self, userid, username, email, password=None):
        user = self.model(
            userid=userid,
            username=username,
            email=email,
        )

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, userid, email, name, password):
        user = self.create_user(
            userid=userid,
            email=email,
            name=name,
            password=password,
        )

        user.is_admin = True
        user.save(using=self._db)
        return user


class User(AbstractBaseUser):
    email = models.EmailField(
        verbose_name='email',
        max_length=254,
    )
    userid = models.CharField(max_length=30, unique=True)
    username = models.CharField(max_length=30)
    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)

    objects = UserManager()

    USERNAME_FIELD = 'userid'
    REQUIRED_FIELDS = ['username', 'email']

    def __str__(self):
        return self.email

    def has_perm(self, perm, obj=None):
        return True

    def has_module_perms(self, app_label):
        return True

    @property
    def is_staff(self):
        return self.is_admin

    class Meta:
        db_table = 'user'


class Board(models.Model):
    title = models.CharField(max_length=200, null=False, default='')
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=False, default='')
    content = models.TextField(null=False, default='')
    date = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'board'


class FoodList(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=False, default='')
    name = models.CharField(max_length=50, null=False, default='')
    memo = models.CharField(max_length=200, null=False, default='')
    count = models.IntegerField(null=False, default='0')
    manufacture_date = models.DateField(null=True, blank=True)  # 제조일자
    expiration_date = models.DateField(null=True, blank=True)  # 유통기한

    class Meta:
        db_table = 'foodlist'


class Comment(models.Model):
    board = models.ForeignKey(Board, related_name='comments', on_delete=models.SET_NULL, null=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=False, default='')
    content = models.TextField(null=False, default='')
    parent_comment = models.ForeignKey('self', null=True, blank=True, on_delete=models.CASCADE, related_name='replies')

    class Meta:
        db_table = 'comment'


class BarcodeData(models.Model):
    barnum = models.CharField(max_length=255, unique=True)
    data = models.JSONField()
    created_at = models.DateTimeField(auto_now_add=True)
