# core/management/commands/import_members.py
from django.core.management.base import BaseCommand
from core.utils.csv_import import import_members_from_csv

class Command(BaseCommand):
    help = 'Import members from CSV file'

    def add_arguments(self, parser):
        parser.add_argument('csv_file', type=str, help='Path to the CSV file')

    def handle(self, *args, **options):
        csv_file = options['csv_file']
        
        self.stdout.write(f"Starting import from {csv_file}...")
        
        try:
            members_created, members_updated = import_members_from_csv(csv_file)
            
            self.stdout.write(
                self.style.SUCCESS(
                    f'Successfully imported members!\n'
                    f'Created: {members_created}\n'
                    f'Updated: {members_updated}'
                )
            )
        except FileNotFoundError:
            self.stdout.write(
                self.style.ERROR(f'File {csv_file} not found!')
            )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error during import: {str(e)}')
            )