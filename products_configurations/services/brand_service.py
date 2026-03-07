from typing import Iterable, Optional
from django.utils import timezone
from ..models.brand import Brand

def list_active():
    return Brand.objects.filter(deleted_at__isnull=True)

def create(**kwargs):
    return Brand.objects.create(**kwargs)

def update(instance: Brand, **kwargs):
    for k,v in kwargs.items():
        setattr(instance, k, v)
    instance.save()
    return instance

def soft_delete(instance: Brand):
    instance.soft_delete()
    return instance