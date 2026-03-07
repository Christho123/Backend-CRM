from ..models.employee import Employees

def list_active():
    return Employees.objects.filter(deleted_at__isnull=True)

def create(**kwargs):
    return Employees.objects.create(**kwargs)

def update(instance: Employees, **kwargs):
    for k,v in kwargs.items():
        setattr(instance, k, v)
    instance.save()
    return instance

def soft_delete(instance: Employees):
    instance.soft_delete()
    return instance

