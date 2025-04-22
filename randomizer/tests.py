from django.test import TestCase, RequestFactory, Client
from django.urls import reverse
from django.contrib.auth.models import User, AnonymousUser
from django.contrib.messages.storage.fallback import FallbackStorage
from django.contrib.sessions.middleware import SessionMiddleware
from unittest import mock

from randomizer.models import RandomizerHistory
from randomizer.views import randomizer_view, create_random_build, randomizer_result
from randomizer.forms import RandomizerForm
from dioses.models import God, Ability
from objetos.models import Item, ItemCategory
from builds.models import Build

class RandomizerModelTest(TestCase):
    """Tests para el modelo RandomizerHistory"""
    
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='12345')
        
        # Crear habilidad
        self.ability = Ability.objects.create(
            name="Test Ability",
            ability_type="Active 1",
            range=30.0,
            radius=15.0
        )
        
        # Crear dios
        self.god = God.objects.create(
            name="Zeus",
            pantheon="Greek",
            role="Mage",
            difficulty="Medium",
            health="450 (+75)",
            mana="300 (+50)",
            speed="365",
            power="Magical",
            damage="35 (+1.5)",
            attack_speed="1.0 (+0.01)",
            progresion="Normal",
            proteccion_fisica="12 (+3)",
            proteccion_magica="30 (+0.9)",
            hp5="7 (+0.5)",
            mp5="5 (+0.4)"
        )
        self.god.abilities.add(self.ability)
        
        # Crear categorías de objetos
        self.cat_inicial = ItemCategory.objects.create(name="Inicial")
        self.cat_pasivo = ItemCategory.objects.create(name="Objeto Pasivo")
        self.cat_reliquia = ItemCategory.objects.create(name="Reliquia")
        self.cat_poder_magico = ItemCategory.objects.create(name="Poder Mágico")
        
        # Crear objetos
        self.starter_item = Item.objects.create(name="Bluestone Pendant", price=800, tier=2)
        self.starter_item.categories.add(self.cat_inicial)
        
        # Crear build
        self.build = Build.objects.create(
            user=self.user,
            god=self.god,
            starter_item=self.starter_item,
            is_random=True
        )
        
        # Crear historia de randomizer
        self.history = RandomizerHistory.objects.create(
            user=self.user,
            god=self.god,
            build=self.build
        )
    
    def test_randomizer_history_creation(self):
        """Test que verifica la creación correcta de un registro en el historial"""
        self.assertEqual(self.history.user, self.user)
        self.assertEqual(self.history.god, self.god)
        self.assertEqual(self.history.build, self.build)
        self.assertTrue(self.history.created_at)
    
    def test_randomizer_history_str(self):
        """Test que verifica el método __str__ del modelo"""
        expected_str = f"Selección aleatoria para {self.user.username} - {self.history.created_at.strftime('%d/%m/%Y %H:%M')}"
        self.assertEqual(str(self.history), expected_str)
    
    def test_anonymous_user_str(self):
        """Test que verifica el método __str__ con usuario anónimo"""
        anon_history = RandomizerHistory.objects.create(
            god=self.god,
            build=self.build
        )
        expected_str = f"Selección aleatoria para Anónimo - {anon_history.created_at.strftime('%d/%m/%Y %H:%M')}"
        self.assertEqual(str(anon_history), expected_str)


class RandomizerViewTest(TestCase):
    """Tests para las vistas del randomizer"""
    
    def setUp(self):
        self.factory = RequestFactory()
        self.client = Client()
        
        # Crear usuario
        self.user = User.objects.create_user(username='testuser', password='12345')
        
        # Crear habilidad
        self.ability = Ability.objects.create(
            name="Test Ability",
            ability_type="Active 1",
            range=30.0,
            radius=15.0
        )
        
        # Crear dioses
        self.god_zeus = God.objects.create(
            name="Zeus",
            pantheon="Greek",
            role="Mage",
            difficulty="Medium",
            health="450 (+75)",
            mana="300 (+50)",
            speed="365",
            power="Magical",
            damage="35 (+1.5)",
            attack_speed="1.0 (+0.01)",
            progresion="Normal",
            proteccion_fisica="12 (+3)",
            proteccion_magica="30 (+0.9)",
            hp5="7 (+0.5)",
            mp5="5 (+0.4)"
        )
        self.god_zeus.abilities.add(self.ability)
        
        self.god_thor = God.objects.create(
            name="Thor",
            pantheon="Norse",
            role="Assassin",
            difficulty="Medium",
            health="480 (+80)",
            mana="240 (+45)",
            speed="375",
            power="Physical",
            damage="39 (+2.0)",
            attack_speed="1.0 (+0.012)",
            progresion="Normal",
            proteccion_fisica="15 (+3.2)",
            proteccion_magica="30 (+0.9)",
            hp5="8 (+0.6)",
            mp5="4.5 (+0.4)"
        )
        self.god_thor.abilities.add(self.ability)
        
        # Crear categorías de objetos
        self.cat_inicial = ItemCategory.objects.create(name="Inicial")
        self.cat_pasivo = ItemCategory.objects.create(name="Objeto Pasivo")
        self.cat_reliquia = ItemCategory.objects.create(name="Reliquia")
        self.cat_poder_magico = ItemCategory.objects.create(name="Poder Mágico")
        self.cat_poder_fisico = ItemCategory.objects.create(name="Poder Físico")
        
        # Crear objetos iniciales
        self.starter_item1 = Item.objects.create(name="Bluestone Pendant", price=800, tier=2)
        self.starter_item1.categories.add(self.cat_inicial)
        
        self.starter_item2 = Item.objects.create(name="Death's Toll", price=800, tier=2)
        self.starter_item2.categories.add(self.cat_inicial)
        
        # Crear objetos pasivos
        for i in range(1, 7):
            passive_item = Item.objects.create(name=f"Passive Item {i}", price=2500, tier=3)
            passive_item.categories.add(self.cat_pasivo)
            if i <= 3:
                passive_item.categories.add(self.cat_poder_magico)
            else:
                passive_item.categories.add(self.cat_poder_fisico)
        
        # Crear reliquias
        for i in range(1, 4):
            relic = Item.objects.create(name=f"Relic {i}", price=0, tier=3)
            relic.categories.add(self.cat_reliquia)
    
    def _add_session_to_request(self, request):
        """Helper para añadir sesión al request"""
        middleware = SessionMiddleware(lambda x: None)
        middleware.process_request(request)
        request.session.save()
        
        # Para los mensajes
        messages = FallbackStorage(request)
        setattr(request, '_messages', messages)
        
        return request

    @mock.patch('django.template.Template.render')
    @mock.patch('django.contrib.messages.api.add_message')
    def test_randomizer_view_post_no_results(self, mock_add_message, mock_render):
        """Test que verifica el comportamiento cuando no hay dioses disponibles para los filtros"""
        # Mockear el render para evitar el error
        mock_render.return_value = ""
        
        # Crear un request directamente y procesar la vista
        request = self.factory.post('/randomizer/', {
            'pantheon': 'Chinese',  # No hay dioses chinos en nuestros datos de prueba
            'role': '',
            'difficulty': ''
        })
        request.user = self.user
        
        # Añadir sesión al request
        request = self._add_session_to_request(request)
        
        # Ejecutar la vista directamente
        response = randomizer_view(request)
        
        # Verificar que se añadió un mensaje de error
        mock_add_message.assert_called_once()
        
        # Verificar que la respuesta es una redirección
        self.assertEqual(response.status_code, 302)
    


class RandomizerFormTest(TestCase):
    """Tests para el formulario RandomizerForm"""
    
    def setUp(self):
        # Crear pantheons, roles y dificultades para probar las opciones del formulario
        God.objects.create(
            name="Zeus",
            pantheon="Greek",
            role="Mage",
            difficulty="Medium",
            health="450 (+75)",
            mana="300 (+50)",
            speed="365",
            power="Magical",
            damage="35 (+1.5)",
            attack_speed="1.0 (+0.01)",
            progresion="Normal",
            proteccion_fisica="12 (+3)",
            proteccion_magica="30 (+0.9)",
            hp5="7 (+0.5)",
            mp5="5 (+0.4)"
        )
        
        God.objects.create(
            name="Thor",
            pantheon="Norse",
            role="Assassin",
            difficulty="Hard",
            health="480 (+80)",
            mana="240 (+45)",
            speed="375",
            power="Physical",
            damage="39 (+2.0)",
            attack_speed="1.0 (+0.012)",
            progresion="Normal",
            proteccion_fisica="15 (+3.2)",
            proteccion_magica="30 (+0.9)",
            hp5="8 (+0.6)",
            mp5="4.5 (+0.4)"
        )
    
    def test_form_fields(self):
        """Test que verifica los campos del formulario"""
        form = RandomizerForm()
        
        # Verificar que el formulario tiene los campos esperados
        self.assertIn('pantheon', form.fields)
        self.assertIn('role', form.fields)
        self.assertIn('difficulty', form.fields)
        
        # Verificar que los campos no son requeridos
        self.assertFalse(form.fields['pantheon'].required)
        self.assertFalse(form.fields['role'].required)
        self.assertFalse(form.fields['difficulty'].required)
    
    def test_form_choices(self):
        """Test que verifica las opciones disponibles en el formulario"""
        form = RandomizerForm()
        
        # Verificar opciones de panteón
        pantheon_choices = [choice[0] for choice in form.fields['pantheon'].choices if choice[0]]
        self.assertIn('Greek', pantheon_choices)
        self.assertIn('Norse', pantheon_choices)
        
        # Verificar opciones de rol
        role_choices = [choice[0] for choice in form.fields['role'].choices if choice[0]]
        self.assertIn('Mage', role_choices)
        self.assertIn('Assassin', role_choices)
        
        # Verificar opciones de dificultad
        difficulty_choices = [choice[0] for choice in form.fields['difficulty'].choices if choice[0]]
        self.assertIn('Medium', difficulty_choices)
        self.assertIn('Hard', difficulty_choices)
    
    def test_form_validation(self):
        """Test que verifica la validación del formulario"""
        # Formulario vacío es válido porque ningún campo es requerido
        form = RandomizerForm(data={})
        self.assertTrue(form.is_valid())
        
        # Formulario con datos válidos
        form = RandomizerForm(data={
            'pantheon': 'Greek',
            'role': 'Mage',
            'difficulty': 'Medium'
        })
        self.assertTrue(form.is_valid())
        
        # Formulario con datos inválidos (opciones que no existen)
        form = RandomizerForm(data={
            'pantheon': 'InvalidPantheon',
            'role': 'InvalidRole',
            'difficulty': 'InvalidDifficulty'
        })
        self.assertFalse(form.is_valid())