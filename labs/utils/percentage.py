
from labs.models import *


def calculate_solve_percentages(user):
    # Get all available labs by category type
    offensive_labs = Lab.objects.filter(category__category_type__in=['offensive', 'both']).count()
    defensive_labs = Lab.objects.filter(category__category_type__in=['defensive', 'both']).count()
    
    # Get all solved labs for this user
    solved_labs = SolvedLab.objects.filter(user=user).select_related('lab__category')
    
    # Count solved labs by type
    offensive_solved = sum(1 for sl in solved_labs 
                         if sl.lab.category.category_type in ['offensive', 'both'])
    defensive_solved = sum(1 for sl in solved_labs 
                         if sl.lab.category.category_type in ['defensive', 'both'])
    
    # Calculate percentages - handle division by zero
    offensive_percent = (offensive_solved / offensive_labs) * 100 if offensive_labs > 0 else 0
    defensive_percent = (defensive_solved / defensive_labs) * 100 if defensive_labs > 0 else 0
    
    # Round and update user fields
    user.red_team_percent = round(offensive_percent)
    user.blue_team_percent = round(defensive_percent)
    user.save(update_fields=['red_team_percent', 'blue_team_percent'])
    
    return {
        "offensive_percent": round(offensive_percent, 2),
        "defensive_percent": round(defensive_percent, 2)
    }
