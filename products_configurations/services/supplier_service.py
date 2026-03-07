from ..models.supplier import Supplier

def list_active():
    return Supplier.objects.filter(deleted_at__isnull=True)

def create(**kwargs):
    return Supplier.objects.create(**kwargs)

def update(instance: Supplier, **kwargs):
    for k,v in kwargs.items():
        setattr(instance, k, v)
    instance.save()
    return instance

def soft_delete(instance: Supplier):
    instance.soft_delete()
    return instance
