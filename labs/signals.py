from django.db.models.signals import pre_delete, post_save
from django.dispatch import receiver
from .models import Lab, SolvedLab
from users.models import Profile, CustomUser

@receiver(pre_delete, sender=Lab)
def handle_lab_deletion(sender, instance, **kwargs):
    """
    Combined signal to handle lab deletion:
    1. Subtract points from profiles of users who solved this lab
    2. Update team percentages for all affected users
    """
    # Get all users who solved this lab
    solved_labs = SolvedLab.objects.filter(lab=instance)
    affected_users = set()
    
    # Subtract points from each user who solved this lab
    for solved_lab in solved_labs:
        affected_users.add(solved_lab.user)
        try:
            profile = Profile.objects.get(user=solved_lab.user)
            # Subtract points
            profile.points = max(0, profile.points - instance.points)
            profile.save()
        except Profile.DoesNotExist:
            continue
    
    # Update team percentages for all affected users
    # Using the same calculation method as in calculate_solve_percentages()
    for user in affected_users:
        from .views import calculate_solve_percentages  # Import here to avoid circular imports
        calculate_solve_percentages(user)

# Optional: Add a signal for when labs are created or updated
@receiver(post_save, sender=Lab)
def handle_lab_save(sender, instance, **kwargs):
    """
    When a lab is created or updated, recalculate percentages for users
    who might be affected (especially when category_type changes)
    """
   
    users_to_update = CustomUser.objects.filter(
        id__in=SolvedLab.objects.values('user')
    ).distinct()
    
   
    for user in users_to_update:
        from .views import calculate_solve_percentages  
        calculate_solve_percentages(user)