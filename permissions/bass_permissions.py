from gyms.models import GymMembership


# فقط برای سریالایزر کریت اینرولمنت ه بفهمه نقشش چیه 
def is_gym_employee(user):
    """
    Return True if user has an active
    Owner, Manager, or Staff role in any gym.
    """

    if not user.is_authenticated:
        return False

    return GymMembership.objects.filter(
        user=user,
        role__in=[
            GymMembership.Role.OWNER,
            GymMembership.Role.MANAGER,
            GymMembership.Role.STAFF,
        ],
        is_active=True,
    ).exists()
