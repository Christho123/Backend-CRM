from typing import Iterable, Optional
from django.utils import timezone
from ..models.category import Category

def list_active() -> Iterable[Category]:
    return Category.objects.filter(deleted_at__isnull=True).order_by("name")

def get_by_id(pk: int) -> Optional[Category]:
    try:
        return Category.objects.get(pk=pk, deleted_at__isnull=True)
    except Category.DoesNotExist:
        return None

def create(**kwargs) -> Category:
    return Category.objects.create(**kwargs)

def update(instance: Category, **kwargs) -> Category:
    for field_name, value in kwargs.items():
        setattr(instance, field_name, value)
    instance.save()
    return instance

def soft_delete(instance: Category) -> Category:
    instance.deleted_at = timezone.now()
    instance.save(update_fields=["deleted_at"]) 
    return instance




