"""
Django management command to import INEP Censo Escolar data from CSV.

Usage:
    python manage.py import_inep /path/to/microdados_ed_basica_2024.csv
"""
import csv
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from inep.models import Escola


class Command(BaseCommand):
    help = 'Import school data from INEP Censo Escolar CSV file'

    def add_arguments(self, parser):
        parser.add_argument(
            'csv_file',
            type=str,
            help='Path to the CSV file to import'
        )
        parser.add_argument(
            '--batch-size',
            type=int,
            default=1000,
            help='Number of records to process in each batch (default: 1000)'
        )
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear existing data before importing'
        )

    def handle(self, *args, **options):
        csv_file = options['csv_file']
        batch_size = options['batch_size']
        clear_data = options['clear']

        # Verify file exists
        try:
            with open(csv_file, 'r', encoding='latin-1') as f:
                pass
        except FileNotFoundError:
            raise CommandError(f'CSV file not found: {csv_file}')
        except Exception as e:
            raise CommandError(f'Error opening CSV file: {e}')

        # Clear existing data if requested
        if clear_data:
            self.stdout.write(self.style.WARNING('Clearing existing data...'))
            count = Escola.objects.count()
            Escola.objects.all().delete()
            self.stdout.write(self.style.SUCCESS(f'Deleted {count} existing records'))

        # Import data
        self.stdout.write(self.style.SUCCESS(f'Starting import from: {csv_file}'))
        
        schools_to_create = []
        schools_to_update = []
        total_processed = 0
        total_created = 0
        total_updated = 0
        errors = 0

        try:
            with open(csv_file, 'r', encoding='latin-1') as f:
                # The CSV uses semicolon as delimiter
                reader = csv.DictReader(f, delimiter=';')
                
                for row_num, row in enumerate(reader, start=2):  # start at 2 (header is line 1)
                    try:
                        # Extract and clean the data
                        co_entidade = self._get_int_value(row.get('CO_ENTIDADE'))
                        
                        if not co_entidade:
                            self.stdout.write(
                                self.style.WARNING(f'Row {row_num}: Missing CO_ENTIDADE, skipping')
                            )
                            errors += 1
                            continue

                        # Check if school already exists
                        try:
                            escola = Escola.objects.get(co_entidade=co_entidade)
                            # Update existing
                            escola.no_entidade = self._clean_string(row.get('NO_ENTIDADE', ''), 100)
                            escola.no_municipio = self._clean_string(row.get('NO_MUNICIPIO', ''), 150)
                            escola.sg_uf = self._clean_string(row.get('SG_UF', ''), 2)
                            escola.tp_dependencia = self._get_int_value(row.get('TP_DEPENDENCIA'))
                            escola.ds_endereco = self._clean_string(row.get('DS_ENDERECO', ''), 100)
                            escola.nu_endereco = self._clean_string(row.get('NU_ENDERECO', ''), 10)
                            escola.ds_complemento = self._clean_string(row.get('DS_COMPLEMENTO', ''), 20)
                            escola.no_bairro = self._clean_string(row.get('NO_BAIRRO', ''), 50)
                            escola.co_cep = self._clean_string(row.get('CO_CEP', ''), 8)
                            escola.nu_ddd = self._clean_string(row.get('NU_DDD', ''), 8)
                            escola.nu_telefone = self._clean_string(row.get('NU_TELEFONE', ''), 8)
                            schools_to_update.append(escola)
                        except Escola.DoesNotExist:
                            # Create new
                            escola = Escola(
                                co_entidade=co_entidade,
                                no_entidade=self._clean_string(row.get('NO_ENTIDADE', ''), 100),
                                no_municipio=self._clean_string(row.get('NO_MUNICIPIO', ''), 150),
                                sg_uf=self._clean_string(row.get('SG_UF', ''), 2),
                                tp_dependencia=self._get_int_value(row.get('TP_DEPENDENCIA')),
                                ds_endereco=self._clean_string(row.get('DS_ENDERECO', ''), 100),
                                nu_endereco=self._clean_string(row.get('NU_ENDERECO', ''), 10),
                                ds_complemento=self._clean_string(row.get('DS_COMPLEMENTO', ''), 20),
                                no_bairro=self._clean_string(row.get('NO_BAIRRO', ''), 50),
                                co_cep=self._clean_string(row.get('CO_CEP', ''), 8),
                                nu_ddd=self._clean_string(row.get('NU_DDD', ''), 8),
                                nu_telefone=self._clean_string(row.get('NU_TELEFONE', ''), 8),
                            )
                            schools_to_create.append(escola)

                        total_processed += 1

                        # Batch insert/update
                        if len(schools_to_create) >= batch_size:
                            with transaction.atomic():
                                Escola.objects.bulk_create(schools_to_create, ignore_conflicts=False)
                                total_created += len(schools_to_create)
                            schools_to_create = []
                            self.stdout.write(f'Processed {total_processed} records...')

                        if len(schools_to_update) >= batch_size:
                            with transaction.atomic():
                                Escola.objects.bulk_update(
                                    schools_to_update,
                                    [
                                        'no_entidade', 'no_municipio', 'sg_uf', 'tp_dependencia',
                                        'ds_endereco', 'nu_endereco', 'ds_complemento', 'no_bairro',
                                        'co_cep', 'nu_ddd', 'nu_telefone'
                                    ]
                                )
                                total_updated += len(schools_to_update)
                            schools_to_update = []
                            self.stdout.write(f'Processed {total_processed} records...')

                    except Exception as e:
                        self.stdout.write(
                            self.style.ERROR(f'Error processing row {row_num}: {e}')
                        )
                        errors += 1
                        continue

                # Insert/update remaining records
                if schools_to_create:
                    with transaction.atomic():
                        Escola.objects.bulk_create(schools_to_create, ignore_conflicts=False)
                        total_created += len(schools_to_create)

                if schools_to_update:
                    with transaction.atomic():
                        Escola.objects.bulk_update(
                            schools_to_update,
                            [
                                'no_entidade', 'no_municipio', 'sg_uf', 'tp_dependencia',
                                'ds_endereco', 'nu_endereco', 'ds_complemento', 'no_bairro',
                                'co_cep', 'nu_ddd', 'nu_telefone'
                            ]
                        )
                        total_updated += len(schools_to_update)

        except Exception as e:
            raise CommandError(f'Error reading CSV file: {e}')

        # Summary
        self.stdout.write(self.style.SUCCESS('\n=== Import Summary ==='))
        self.stdout.write(self.style.SUCCESS(f'Total processed: {total_processed}'))
        self.stdout.write(self.style.SUCCESS(f'Created: {total_created}'))
        self.stdout.write(self.style.SUCCESS(f'Updated: {total_updated}'))
        if errors > 0:
            self.stdout.write(self.style.WARNING(f'Errors: {errors}'))
        self.stdout.write(self.style.SUCCESS('\nImport completed successfully!'))

    def _get_int_value(self, value):
        """Convert value to integer, return None if invalid."""
        if not value or value.strip() == '':
            return None
        try:
            return int(value.strip())
        except (ValueError, AttributeError):
            return None

    def _clean_string(self, value, max_length):
        """Clean and truncate string value."""
        if not value:
            return ''
        value = str(value).strip()
        if len(value) > max_length:
            return value[:max_length]
        return value
