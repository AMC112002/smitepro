from dioses.models import Ability

def populate_abilities():
    # Crear habilidades de Thor
    abilities = [
        {
            "name": "Trampa enredadora",
            "ability_type": "Active 1",
            "description": "Artemisa coloca una trampa en el suelo que enreda al primer enemigo que la pisa, inmovilizándolo y revelándolo.",
            "range": 35.0,
            "radius": 2.0,
            "image": None
        },
        {
            "name": "Lluvia de flechas",
            "ability_type": "Active 2",
            "description": "Artemisa dispara una serie de flechas al cielo que caen en un área, infligiendo daño a los enemigos dentro de la zona.",
            "range": 50.0,
            "radius": 10.0,
            "image": None
        },
        {
            "name": "Tiro preciso",
            "ability_type": "Active 3",
            "description": "Artemisa realiza un disparo concentrado que inflige daño crítico al primer enemigo alcanzado.",
            "range": 60.0,
            "radius": 0.0,
            "image": None
        },
        {
            "name": "Furia del jabalí",
            "ability_type": "Active 4",
            "description": "Artemisa invoca un jabalí celestial que persigue y aturde a los enemigos cercanos mientras inflige daño en su camino.",
            "range": 40.0,
            "radius": 15.0,
            "image": None
        },
        {
            "name": "Cazadora suprema",
            "ability_type": "Passive",
            "description": "Cada vez que Artemisa golpea a un enemigo con un ataque básico, aumenta su velocidad de ataque y probabilidad de crítico temporalmente.",
            "range": 0.0,
            "radius": 0.0,
            "image": None
        }
    ]

    for ability_data in abilities:
        Ability.objects.create(**ability_data)
    print("Habilidades de Artemisa creadas con éxito.")