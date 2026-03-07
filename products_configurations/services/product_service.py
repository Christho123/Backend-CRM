from ..models.product import Product

def list_active():
    return Product.objects.filter(deleted_at__isnull=True)

def create(**kwargs):
    return Product.objects.create(**kwargs)

def update(instance: Product, **kwargs):
    for k,v in kwargs.items():
        setattr(instance, k, v)
    instance.save()
    return instance

def soft_delete(instance: Product):
    instance.soft_delete()
    return instance