from optparse import make_option

from django.core.management.base import BaseCommand
from django.core.management.base import CommandError

from petri.mail.utils import sync_all
from petri.mail.utils import sync_lists
from petri.mail.utils import sync_proxies

class Command(BaseCommand):
    option_list = BaseCommand.option_list + (
        make_option('--proxy',
            action='store_true',
            dest='proxy',
            default=False,
            help='Sync all user email proxies'),
        make_option('--lists',
            action='store_true',
            dest='lists',
            default=False,
            help='Sync all mailing lists and routes')
        )

    help = 'Sync email configuration with remote provider'

    def handle(self, *args, **options):
        print "Syncing email configuration..."

        if options['proxy']:
            sync_proxies(silent=False)
            return

        if options['lists']:
            sync_lists(silent=False)
            return
        
        sync_all(silent=False)
