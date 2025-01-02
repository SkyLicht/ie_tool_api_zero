def calculate_work_plan_residuals(target_oee: float, uph: int,planned_hours: int):
    """
    Calculate the residuals of the work plan
    :param target_oee: target iee
    :param uph: unit per hour
    :param planned_hours: planned hours
    :return: (uph_target, commit)
    """
    if target_oee <= 0 or uph <= 0 or planned_hours <= 0:
        return 0, 0, 0


    uph_target = target_oee * uph
    commit = uph_target * planned_hours
    cycle_time = 3600 / uph

    return round(uph_target,0), round(commit) , round(cycle_time,2)