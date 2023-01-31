from django.contrib.auth.management.commands import createsuperuser
from django.core.management import CommandError


class Command(createsuperuser.Command):
    help = 'Create a superuser with a password non-interactively'

    def add_arguments(self, parser):
        super(Command, self).add_arguments(parser)
        parser.add_argument(
            '--password', dest='password', default=None,
            help='Specifies the password for the superuser.',
        )

    def handle(self, *args, **options):
        options.setdefault('interactive', False)
        database = options.get('database')
        password = options.get('password')
        phone_number = options.get('phone_number')

        if not password or not phone_number:
            raise CommandError(
                    " --phone_number and --password are required options")

        user_data = {
            'phone_number': phone_number,
            'password': password,
        }

        self.UserModel._default_manager.db_manager(
                database).create_superuser(**user_data)

        if options.get('verbosity', 0) >= 1:
            self.stdout.write("Superuser created successfully.")