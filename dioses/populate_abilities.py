from dioses.models import Ability

def populate_abilities():
    # Crear habilidades de Thor
    abilities = [
        {
            "name": "Descarga de trueno",
            "ability_type": "Active 1",
            "description": "Raijin lanza un rayo hacia un enemigo, infligiendo daño directo y aturdiéndolo brevemente. Si el enemigo ya está aturdido, recibirá daño adicional.",
            "range": 50.0,
            "radius": 0.0,
            "image": None
        },
        {
            "name": "Amanecer eléctrico",
            "ability_type": "Active 2",
            "description": "Raijin crea una tormenta eléctrica alrededor de él, causando daño a los enemigos cercanos durante un corto periodo de tiempo.",
            "range": 0.0,
            "radius": 15.0,
            "image": None
        },
        {
            "name": "Cañón de trueno",
            "ability_type": "Active 3",
            "description": "Raijin carga un cañón de trueno, el cual dispara una poderosa onda de energía hacia adelante, causando daño a todos los enemigos en su camino y ralentizándolos brevemente.",
            "range": 40.0,
            "radius": 5.0,
            "image": None
        },
        {
            "name": "Tormenta de tormentas",
            "ability_type": "Active 4",
            "description": "Raijin invoca una tormenta de rayos a gran escala, que afecta a una amplia área, infligiendo daño masivo a todos los enemigos dentro del alcance.",
            "range": 0.0,
            "radius": 30.0,
            "image": None
        },
        {
            "name": "Rayo divino",
            "ability_type": "Passive",
            "description": "Raijin aumenta su daño y la probabilidad de aturdir a los enemigos al usar sus habilidades, acumulando energía que se libera en forma de un rayo más poderoso después de cierto número de habilidades activadas.",
            "range": 0.0,
            "radius": 0.0,
            "image": None
        }
    ]

    for ability_data in abilities:
        Ability.objects.create(**ability_data)
    print("Habilidades de Raijin creadas con éxito.")