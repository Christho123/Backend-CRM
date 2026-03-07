from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from pathlib import Path
import csv

from products_configurations.models import Brand
from ubi_geo.models import Country


def getv(row, *cands):
    """Devuelve el primer valor no vacío encontrado en las columnas dadas."""
    for k in cands:
        if k in row:
            v = (row.get(k) or "").strip()
            if v != "":
                return v
    return ""


class Command(BaseCommand):
    help = "Importa marcas (Brand) desde un archivo CSV delimitado por ';'."

    def add_arguments(self, parser):
        parser.add_argument(
            "--path",
            type=str,
            default="db/brands.csv",
            help="Ruta del archivo CSV con las marcas (por defecto: db/brands.csv)",
        )
        parser.add_argument(
            "--truncate",
            action="store_true",
            help="Borra todas las marcas antes de importar.",
        )

    def handle(self, *args, **opt):
        csv_path = Path(opt["path"]).resolve()

        if not csv_path.exists():
            raise CommandError(f"No se encontró el archivo: {csv_path}")

        if opt["truncate"]:
            self.stdout.write(self.style.WARNING("Eliminando todas las marcas existentes..."))
            Brand.objects.all().delete()

        self.stdout.write(f"Importando marcas desde {csv_path}…")

        with csv_path.open(encoding="utf-8", newline="") as f:
            reader = csv.DictReader(f, delimiter=";")
            created = updated = skipped = 0

            with transaction.atomic():
                for row in reader:
                    name = getv(row, "name", "Name")
                    description = getv(row, "description", "Description")
                    country_id = getv(row, "country_id", "Country_id", "country")

                    if not name or not country_id:
                        skipped += 1
                        continue

                    try:
                        country = Country.objects.get(id=country_id)
                    except Country.DoesNotExist:
                        self.stdout.write(self.style.WARNING(f"País con id={country_id} no encontrado, omitiendo {name}"))
                        skipped += 1
                        continue

                    obj, created_flag = Brand.objects.update_or_create(
                        name=name,
                        defaults={
                            "description": description,
                            "country": country,
                        },
                    )

                    if created_flag:
                        created += 1
                    else:
                        updated += 1

        self.stdout.write(self.style.SUCCESS(
            f"Importación completada ✔  Nuevas: {created} | Actualizadas: {updated} | Omitidas: {skipped}"
        ))
