def calculate_fare(distance, eco_mode=False, is_electric=False):
    BASE_FARE = 50
    PER_KM_RATE = 15
    
    fare = BASE_FARE + (distance * PER_KM_RATE)
    
    if eco_mode:
        fare *= 0.9
    if is_electric:
        fare *= 0.95
    
    return round(fare, 2)
