from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager
from django.contrib.auth.models import PermissionsMixin
from django.core.validators import RegexValidator
from django.db import models

# Create your models here.

# class MyUserManager(UserManager):
#     def create_superuser(self, phone_number=None, password=None, **extra_fields):
#         extra_fields.setdefault('is_staff', True)
#         extra_fields.setdefault('is_superuser', True)
#         extra_fields.setdefault('is_active', True)
#         extra_fields.setdefault('phone_number', phone_number)
#
#         if extra_fields.get('is_staff') is not True:
#             raise ValueError('Superuser must have is_staff=True.')
#         if extra_fields.get('is_superuser') is not True:
#             raise ValueError('Superuser must have is_superuser=True.')
#
#         return self.create_user(phone_number, password=password, **extra_fields)


# class MyUser(User):
#     phone_number = models.CharField(max_length=20, unique=True)
#     objects = MyUserManager()
#     USERNAME_FIELD = 'phone_number'
from django.utils import timezone
from django.utils.translation import gettext_lazy as _


class CustomUserManager(BaseUserManager):

    def create_user(self, phone_number, password=None):

        if phone_number is None:
            raise TypeError('Users must have an phone number.')

        user = self.model(phone_number=phone_number)
        user.set_password(password)
        user.save()

        return user

    def create_superuser(self, phone_number, password):

        if password is None:
            raise TypeError('Superusers must have a password.')

        user = self.create_user(phone_number, password)
        user.is_superuser = True
        user.is_staff = True
        user.save()

        return user


class User(AbstractBaseUser, PermissionsMixin):
    phone_regex = RegexValidator(regex=r'^\+?1?\d{9,15}$', message="Phone number must be entered in the format: "
                                                                   "'+999999999'. Up to 15 digits allowed.")
    phone_number = models.CharField(validators=[phone_regex], max_length=17, blank=False, unique=True)
    updated_at = models.DateTimeField(auto_now=True)
    USERNAME_FIELD = 'phone_number'
    first_name = models.CharField(_("first name"), max_length=150, blank=True)
    last_name = models.CharField(_("last name"), max_length=150, blank=True)
    email = models.EmailField(_("email address"), blank=True)
    is_staff = models.BooleanField(
        _("staff status"),
        default=False,
        help_text=_("Designates whether the user can log into this admin site."),
    )
    is_active = models.BooleanField(
        _("active"),
        default=True,
        help_text=_(
            "Designates whether this user should be treated as active. "
            "Unselect this instead of deleting accounts."
        ),
    )
    date_joined = models.DateTimeField(_("date joined"), default=timezone.now)

    objects = CustomUserManager()

    EMAIL_FIELD = "email"
    REQUIRED_FIELDS = []

    class Meta:
        verbose_name = _("user")
        verbose_name_plural = _("users")
        abstract = False

    def clean(self):
        super().clean()

    def get_full_name(self):
        """
        Return the first_name plus the last_name, with a space in between.
        """
        full_name = "%s %s" % (self.first_name, self.last_name)
        return full_name.strip()

    def get_short_name(self):
        """Return the short name for the user."""
        return self.first_name


class Account(models.Model):
    account_id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    status = [
        ('Active', 'Active'),
        ('Closed', 'Closed'),
    ]
    current_status = models.CharField(max_length=16, choices=status, default='Active')

    def __str__(self):
        return self.user.phone_number


class Balance(models.Model):
    account = models.ForeignKey(Account, primary_key=True, on_delete=models.CASCADE)
    balance = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=3, blank=True)

    # def get_balance(self):
    #     return self.balance  # It should always comes like 200.50, 20.00, that
    #
    # @staticmethod
    # def get_current_balance(account):
    #     balance = Transactions.objects.filter(receiver=account).aggregate(total=Sum('amount'))['total']
    #     return balance


class Method(models.Model):
    id = models.AutoField(primary_key=True)
    type = [
        ('CC', 'CC'),
        ('CASH', 'Cash'),
        ('UPI', 'UPI'),
    ]
    payment_type = models.CharField(max_length=16, choices=type, default='Online')

    def __str__(self):
        return self.payment_type


class Transactions(models.Model):
    transaction_id = models.AutoField(primary_key=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    sender = models.ForeignKey(Account, related_name="sender", on_delete=models.CASCADE)
    receiver = models.ForeignKey(Account, related_name="receiver", on_delete=models.CASCADE)
    created_at = models.DateTimeField(default=timezone.now)

    # method = models.ForeignKey(Method, on_delete=models.CASCADE)
