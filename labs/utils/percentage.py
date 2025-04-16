
from labs.models import *


def calculate_solve_percentages(user):
    solved_labs = SolvedLab.objects.filter(user=user).select_related('lab__category')

    offensive_total = Lab.objects.filter(category__category_type__in=['offensive', 'both']).count()
    defensive_total = Lab.objects.filter(category__category_type__in=['defensive', 'both']).count()

    offensive_solved = 0
    defensive_solved = 0

    for entry in solved_labs:
        cat_type = entry.lab.category.category_type
        if cat_type in ['offensive', 'both']:
            offensive_solved += 1
        if cat_type in ['defensive', 'both']:
            defensive_solved += 1

    return {
        "offensive_percent": round((offensive_solved / offensive_total) * 100, 2) if offensive_total else 0,
        "defensive_percent": round((defensive_solved / defensive_total) * 100, 2) if defensive_total else 0,
    }
