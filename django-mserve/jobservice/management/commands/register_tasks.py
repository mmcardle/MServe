from django.core.management.base import BaseCommand, CommandError

class Command(BaseCommand):
    args = '<app_id app_id ...>'
    help = 'Closes the specified poll for voting'

    def handle(self, *args, **options):
        for app_id in args:
            try:
                struct = __import__(app_id)
                from jobservice import register_task_description
                if 'task_descriptions' in dir(struct):
                    for k in struct.task_descriptions.keys():
                        register_task_description(k, struct.task_descriptions.get(k))
                    self.stdout.write('Successfully registered tasks for: %s\n' % app_id)
                else:
                    raise CommandError("Could not register tasks for: %s - module has no task_descriptions defined " % app_id)
            except ImportError, e:
                raise CommandError("Could not register tasks for: %s - %s" % (app_id, e))