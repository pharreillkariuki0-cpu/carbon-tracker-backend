def calculate_footprint(data):
    # Emission factors (kg CO₂ per year)
    factors = {
        'commute': {
            'car': 1200,
            'transit': 400,
            'bike': 50,
            'walk': 10
        },
        'flights': {
            '0': 0,
            '1': 400,
            '2': 800,
            '3': 1200,
            '4': 1600
        },
        'diet': {
            'meat-heavy': 2000,
            'mixed': 1200,
            'veg': 600,
            'vegan': 300
        },
        'electricity': {
            'low': 300,
            'medium': 700,
            'high': 1200
        },
        'shopping': {
            'monthly': 800,
            'few-months': 400,
            'yearly': 150,
            'rarely': 50
        },
        'waste': {
            'lot': 500,
            'average': 250,
            'little': 80
        }
    }
    
    # Calculate each category
    transport = factors['commute'].get(data.get('commute_mode', 'car'), 0)
    transport += factors['flights'].get(str(data.get('flights_per_year', 0)), 0)
    
    food = factors['diet'].get(data.get('diet_type', 'mixed'), 0)
    home = factors['electricity'].get(data.get('electricity_bill', 'medium'), 0)
    
    shopping = factors['shopping'].get(data.get('shopping_frequency', 'few-months'), 0)
    shopping += factors['waste'].get(data.get('waste_amount', 'average'), 0)
    
    total = transport + food + home + shopping
    
    return {
        'transport_kg': transport,
        'food_kg': food,
        'home_kg': home,
        'shopping_kg': shopping,
        'total_kg': total
    }