from rolepermissions.roles import AbstractUserRole

class Manager(AbstractUserRole):
    available_permissions = {
        'view_protected': True,
        
        }

class Veterinarian(AbstractUserRole):
    available_permissions = {
        
        
        }
    
class Warehouseman(AbstractUserRole):
    available_permissions = {
        
        
        }
    
REGISTERED_ROLES = {
    'manager': Manager,
    'veterinarian': Veterinarian,
    'warehouseman': Warehouseman,
}

def get_role_choices():
    return [
        ('manager', 'Менеджер'),
        ('veterinarian', 'Ветеринар'),
        ('warehouseman', 'Кладовщик'),
    ]

def get_role_class(role_code):
    return REGISTERED_ROLES.get(role_code)