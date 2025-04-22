from django.test import TestCase, Client
from django.urls import reverse
from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile
from dioses.models import God, Ability

#PRUEBAS UNITARIAS DE MODELOS

class AbilityModelTest(TestCase):
    def setUp(self):
        self.ability = Ability.objects.create(
            name="Rayo de Zeus",
            ability_type="Active 1",
            description="Lanza un poderoso rayo",
            range=55.0,
            radius=10.0
        )

    def test_ability_creation(self):
        """Prueba que la habilidad se crea correctamente"""
        self.assertEqual(self.ability.name, "Rayo de Zeus")
        self.assertEqual(self.ability.ability_type, "Active 1")
        self.assertEqual(self.ability.description, "Lanza un poderoso rayo")
        self.assertEqual(self.ability.range, 55.0)
        self.assertEqual(self.ability.radius, 10.0)
        self.assertIsNone(self.ability.image.name)

    def test_ability_string_representation(self):
        """Prueba que el método __str__ devuelve el nombre de la habilidad"""
        self.assertEqual(str(self.ability), "Rayo de Zeus")

    def test_ability_type_choices(self):
        """Prueba que el tipo de habilidad solo puede ser uno de los definidos"""
        invalid_ability = Ability(
            name="Habilidad inválida",
            ability_type="Invalid Type",
            range=10.0,
            radius=5.0
        )
        with self.assertRaises(ValidationError):
            invalid_ability.full_clean()


class GodModelTest(TestCase):
    def setUp(self):
        self.ability1 = Ability.objects.create(
            name="Rayo Celestial",
            ability_type="Active 1",
            description="Lanza un rayo del cielo",
            range=50.0,
            radius=8.0
        )
        
        self.ability2 = Ability.objects.create(
            name="Inmortalidad",
            ability_type="Passive",
            description="Revive después de morir",
            range=0.0,
            radius=0.0
        )
        
        self.god = God.objects.create(
            name="Zeus",
            pantheon="Greek",
            role="Mage",
            difficulty="Medium",
            health="450 (+75)",
            mana="300 (+40)",
            speed="365",
            power="Magical",
            damage="35 (+1.5)",
            attack_speed="0.95 (+0.01)",
            progresion="1/1/1",
            proteccion_fisica="12 (+2.5)",
            proteccion_magica="30 (+0.9)",
            hp5="7 (+0.5)",
            mp5="5 (+0.4)",
            lore="Rey de los dioses del Olimpo"
        )
        self.god.abilities.add(self.ability1, self.ability2)

    def test_god_creation(self):
        """Prueba que el dios se crea correctamente"""
        self.assertEqual(self.god.name, "Zeus")
        self.assertEqual(self.god.pantheon, "Greek")
        self.assertEqual(self.god.role, "Mage")
        self.assertEqual(self.god.difficulty, "Medium")
        self.assertEqual(self.god.health, "450 (+75)")
        self.assertEqual(self.god.power, "Magical")
        self.assertEqual(self.god.lore, "Rey de los dioses del Olimpo")
        
    def test_god_string_representation(self):
        """Prueba que el método __str__ devuelve el nombre del dios"""
        self.assertEqual(str(self.god), "Zeus")
        
    def test_god_abilities_relation(self):
        """Prueba que las habilidades se asignan correctamente al dios"""
        abilities = self.god.abilities.all()
        self.assertEqual(abilities.count(), 2)
        self.assertIn(self.ability1, abilities)
        self.assertIn(self.ability2, abilities)
        
    def test_god_pantheon_choices(self):
        """Prueba que el panteón solo puede ser uno de los definidos"""
        invalid_god = God(
            name="Dios Inválido",
            pantheon="Invalid Pantheon",
            role="Mage",
            difficulty="Medium",
            health="400",
            mana="200",
            speed="370",
            power="Magical",
            damage="30",
            attack_speed="1.0",
            progresion="1/1/1",
            proteccion_fisica="10",
            proteccion_magica="20",
            hp5="5",
            mp5="5"
        )
        with self.assertRaises(ValidationError):
            invalid_god.full_clean()

    def test_unique_god_name(self):
        """Prueba que no se pueden crear dioses con el mismo nombre"""
        duplicate_god = God(
            name="Zeus",  # Nombre duplicado
            pantheon="Greek",
            role="Mage",
            difficulty="Medium",
            health="450",
            mana="300",
            speed="360",
            power="Magical",
            damage="35",
            attack_speed="0.95",
            progresion="1/1/1",
            proteccion_fisica="12",
            proteccion_magica="30",
            hp5="7",
            mp5="5"
        )
        with self.assertRaises(Exception):  # IntegrityError en base de datos real
            duplicate_god.save()

#PRUEBAS UNITARIAS DE VISTAS

class HomeViewTest(TestCase):
    def test_home_view(self):
        """Prueba que la vista home carga correctamente"""
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'home/home.html')

class GodsByPantheonViewTest(TestCase):
    def setUp(self):
        # Crear dioses para diferentes panteones
        self.zeus = God.objects.create(
            name="Zeus",
            pantheon="Greek",
            role="Mage",
            difficulty="Medium",
            health="450",
            mana="300",
            speed="365",
            power="Magical",
            damage="35",
            attack_speed="0.95",
            progresion="1/1/1",
            proteccion_fisica="12",
            proteccion_magica="30",
            hp5="7",
            mp5="5"
        )
        
        self.ra = God.objects.create(
            name="Ra",
            pantheon="Egyptian",
            role="Mage",
            difficulty="Easy",
            health="400",
            mana="350",
            speed="370",
            power="Magical",
            damage="30",
            attack_speed="0.90",
            progresion="1/1/1",
            proteccion_fisica="10",
            proteccion_magica="35",
            hp5="6",
            mp5="6"
        )

    def test_gods_by_pantheon_view(self):
        """Prueba que la vista de dioses por panteón carga correctamente"""
        response = self.client.get(reverse('gods_by_pantheon'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'dioses/gods_by_pantheon.html')
        
        # Verificar que los panteones están en el contexto
        self.assertIn('gods_by_pantheon', response.context)
        gods_by_pantheon = response.context['gods_by_pantheon']
        
        # Verificar que solo se muestran panteones con dioses
        self.assertIn('Griego', gods_by_pantheon)
        self.assertIn('Egipcio', gods_by_pantheon)
        
        # Verificar que los dioses están correctamente asignados a sus panteones
        self.assertIn(self.zeus, gods_by_pantheon['Griego'])
        self.assertIn(self.ra, gods_by_pantheon['Egipcio'])

class GodDetailViewTest(TestCase):
    def setUp(self):
        # Crear un dios con habilidades
        self.god = God.objects.create(
            name="Thor",
            pantheon="Norse",
            role="Warrior",
            difficulty="Medium",
            health="500",
            mana="250",
            speed="375",
            power="Physical",
            damage="40",
            attack_speed="1.0",
            progresion="1/1/1.5",
            proteccion_fisica="15",
            proteccion_magica="25",
            hp5="8",
            mp5="4"
        )
        
        # Crear habilidades para Thor
        self.passive = Ability.objects.create(
            name="Resistencia",
            ability_type="Passive",
            description="Gana resistencia física",
            range=0.0,
            radius=0.0
        )
        
        self.active1 = Ability.objects.create(
            name="Mjolnir",
            ability_type="Active 1",
            description="Lanza su martillo",
            range=40.0,
            radius=5.0
        )
        
        self.active2 = Ability.objects.create(
            name="Tormenta",
            ability_type="Active 2",
            description="Invoca una tormenta",
            range=30.0,
            radius=15.0
        )
        
        # Asignar habilidades a Thor
        self.god.abilities.add(self.passive, self.active1, self.active2)

    def test_god_detail_view(self):
        """Prueba que la vista de detalle de un dios carga correctamente"""
        response = self.client.get(reverse('god_detail', args=[self.god.id]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'dioses/god_detail.html')
        
        # Verificar que el dios está en el contexto
        self.assertEqual(response.context['god'], self.god)
        
        # Verificar que las habilidades están en el contexto y en el orden correcto
        abilities = response.context['abilities']
        self.assertEqual(abilities.count(), 3)
        
        # Verificar el orden: primero pasivas, luego activas en orden
        abilities_list = list(abilities)
        self.assertEqual(abilities_list[0], self.passive)
        self.assertEqual(abilities_list[1], self.active1)
        self.assertEqual(abilities_list[2], self.active2)

#PRUEBAS DE INTEGRACION

class DiosesFunctionalityTest(TestCase):
    def setUp(self):
        self.client = Client()
        
        # Crear habilidades
        self.passive = Ability.objects.create(
            name="Bendición Solar",
            ability_type="Passive",
            description="Aumenta el poder mágico",
            range=0.0,
            radius=0.0
        )
        
        self.active1 = Ability.objects.create(
            name="Rayo Solar",
            ability_type="Active 1",
            description="Lanza un rayo de luz solar",
            range=50.0,
            radius=5.0
        )
        
        # Crear dioses de diferentes panteones
        self.apollo = God.objects.create(
            name="Apollo",
            pantheon="Greek",
            role="Hunter",
            difficulty="Medium",
            health="400",
            mana="200",
            speed="375",
            power="Physical",
            damage="38",
            attack_speed="1.0",
            progresion="1/1/1",
            proteccion_fisica="10",
            proteccion_magica="30",
            hp5="6",
            mp5="5",
            lore="Dios del sol y la música"
        )
        self.apollo.abilities.add(self.passive, self.active1)
        
        self.horus = God.objects.create(
            name="Horus",
            pantheon="Egyptian",
            role="Warrior",
            difficulty="Hard",
            health="475",
            mana="250",
            speed="370",
            power="Physical",
            damage="35",
            attack_speed="0.95",
            progresion="1/1/1.25",
            proteccion_fisica="18",
            proteccion_magica="28",
            hp5="7",
            mp5="4",
            lore="Dios del cielo"
        )
        
    def test_navigation_flow(self):
        """Prueba el flujo de navegación completo desde home a god detail"""
        # 1. Visitar home
        home_response = self.client.get(reverse('home'))
        self.assertEqual(home_response.status_code, 200)
        
        # 2. Ir a la página de dioses por panteón
        gods_response = self.client.get(reverse('gods_by_pantheon'))
        self.assertEqual(gods_response.status_code, 200)
        
        # Verificar que los dioses están agrupados por panteón
        self.assertIn('gods_by_pantheon', gods_response.context)
        pantheons = gods_response.context['gods_by_pantheon']
        self.assertIn('Griego', pantheons)
        self.assertIn('Egipcio', pantheons)
        
        # 3. Visitar la página de detalle de Apollo
        apollo_response = self.client.get(reverse('god_detail', args=[self.apollo.id]))
        self.assertEqual(apollo_response.status_code, 200)
        
        # Verificar que la información de Apollo es correcta
        self.assertEqual(apollo_response.context['god'], self.apollo)
        self.assertEqual(apollo_response.context['god'].name, "Apollo")
        self.assertEqual(apollo_response.context['god'].pantheon, "Greek")
        
        # Verificar que las habilidades se muestran
        abilities = apollo_response.context['abilities']
        self.assertEqual(abilities.count(), 2)
        self.assertIn(self.passive, abilities)
        self.assertIn(self.active1, abilities)
        
    def test_pantheon_filtering(self):
        """Prueba que los panteones sin dioses no aparecen en la vista"""
        # No hay dioses en el panteón Norse
        response = self.client.get(reverse('gods_by_pantheon'))
        pantheons = response.context['gods_by_pantheon']
        
        # Verificar que los panteones con dioses están en el contexto
        self.assertIn('Griego', pantheons)
        self.assertIn('Egipcio', pantheons)
        
        # Verificar que un panteón sin dioses no está en el contexto
        self.assertNotIn('Nórdico', pantheons)
        
    def test_error_handling_nonexistent_god(self):
        """Prueba el manejo de errores cuando se solicita un dios que no existe"""
        # Intentar acceder a un dios que no existe (ID 999)
        response = self.client.get(reverse('god_detail', args=[999]))
        self.assertEqual(response.status_code, 404)

