from django.test import TestCase, Client
from django.urls import reverse, NoReverseMatch
from django.contrib.auth.models import User
from .models import TierList, Tier, TierListComment
from dioses.models import God  # Asumiendo que tienes este modelo
from .forms import TierListForm, TierForm
from unittest.mock import patch


class TierListModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='12345')
        self.tierlist = TierList.objects.create(
            user=self.user,
            name='Test Tier List',
            description='Test Description',
            is_public=True
        )
        # Crear un dios para usar en pruebas
        self.god = God.objects.create(name='Zeus', pantheon='Greek')
        self.tier = Tier.objects.create(
            tierlist=self.tierlist,
            god=self.god,
            tier='S'
        )

    def test_tierlist_creation(self):
        """Test que la tierlist se crea correctamente"""
        self.assertEqual(self.tierlist.name, 'Test Tier List')
        self.assertEqual(self.tierlist.description, 'Test Description')
        self.assertTrue(self.tierlist.is_public)
        self.assertEqual(self.tierlist.user, self.user)

    def test_tierlist_str_method(self):
        """Test del método __str__ de TierList"""
        self.assertEqual(str(self.tierlist), 'Test Tier List - testuser')

    def test_tierlist_get_absolute_url(self):
        """Test del método get_absolute_url"""
        self.assertEqual(
            self.tierlist.get_absolute_url(),
            reverse('tierlist_detail', kwargs={'pk': self.tierlist.pk})
        )

    def test_tierlist_get_tier_counts(self):
        """Test del método get_tier_counts"""
        counts = self.tierlist.get_tier_counts()
        self.assertEqual(counts['S'], 1)
        self.assertEqual(counts['A'], 0)


class TierModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='12345')
        self.tierlist = TierList.objects.create(
            user=self.user,
            name='Test Tier List',
            description='Test Description'
        )
        self.god = God.objects.create(name='Zeus', pantheon='Greek')
        self.tier = Tier.objects.create(
            tierlist=self.tierlist,
            god=self.god,
            tier='S',
            notes='Very powerful'
        )

    def test_tier_creation(self):
        """Test que el tier se crea correctamente"""
        self.assertEqual(self.tier.tier, 'S')
        self.assertEqual(self.tier.notes, 'Very powerful')
        self.assertEqual(self.tier.tierlist, self.tierlist)
        self.assertEqual(self.tier.god, self.god)

    def test_tier_str_method(self):
        """Test del método __str__ de Tier"""
        self.assertEqual(str(self.tier), 'Zeus - S Tier')


class TierListCommentModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='12345')
        self.tierlist = TierList.objects.create(
            user=self.user,
            name='Test Tier List',
            description='Test Description'
        )
        self.comment = TierListComment.objects.create(
            tierlist=self.tierlist,
            user=self.user,
            text='This is a test comment'
        )

    def test_comment_creation(self):
        """Test que el comentario se crea correctamente"""
        self.assertEqual(self.comment.text, 'This is a test comment')
        self.assertEqual(self.comment.tierlist, self.tierlist)
        self.assertEqual(self.comment.user, self.user)

    def test_comment_str_method(self):
        """Test del método __str__ de TierListComment"""
        self.assertEqual(str(self.comment), 'Comentario por testuser en Test Tier List')


class TierListFormTest(TestCase):
    def test_tierlist_form_valid(self):
        """Test que el formulario de TierList es válido con datos correctos"""
        form_data = {
            'name': 'New Tier List',
            'description': 'New Description',
            'is_public': True
        }
        form = TierListForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_tierlist_form_empty_name(self):
        """Test que el formulario de TierList es inválido con nombre vacío"""
        form_data = {
            'name': '',
            'description': 'New Description',
            'is_public': True
        }
        form = TierListForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('name', form.errors)


class TierFormTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='12345')
        self.tierlist = TierList.objects.create(
            user=self.user,
            name='Test Tier List'
        )
        self.god = God.objects.create(name='Zeus', pantheon='Greek')

    def test_tier_form_valid(self):
        """Test que el formulario de Tier es válido con datos correctos"""
        form_data = {
            'tier': 'S',
            'god': self.god.id,
            'notes': 'Very powerful'
        }
        form = TierForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_tier_form_invalid_tier(self):
        """Test que el formulario de Tier es inválido con un tier incorrecto"""
        form_data = {
            'tier': 'X',  # No es una opción válida
            'god': self.god.id,
            'notes': 'Very powerful'
        }
        form = TierForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('tier', form.errors)


class CommunityTierlistsViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        # Configurar datos de prueba una vez para todos los tests
        cls.user = User.objects.create_user(username='testuser', password='12345')
        cls.tierlist1 = TierList.objects.create(
            user=cls.user,
            name='Public Tier List 1',
            description='Public Description 1',
            is_public=True
        )
        cls.tierlist2 = TierList.objects.create(
            user=cls.user,
            name='Public Tier List 2',
            description='Public Description 2',
            is_public=True
        )
        cls.private_tierlist = TierList.objects.create(
            user=cls.user,
            name='Private Tier List',
            description='Private Description',
            is_public=False
        )

    def setUp(self):
        self.client = Client()
        self.url = reverse('community_tierlists')


class MyTierlistsViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        # Configurar datos de prueba una vez para todos los tests
        cls.user = User.objects.create_user(username='testuser', password='12345')
        cls.other_user = User.objects.create_user(username='otheruser', password='12345')
        
        # Tierlists del usuario de prueba
        cls.tierlist1 = TierList.objects.create(
            user=cls.user,
            name='My Tier List 1',
            description='My Description 1',
        )
        cls.tierlist2 = TierList.objects.create(
            user=cls.user,
            name='My Tier List 2',
            description='My Description 2',
        )
        
        # Tierlist de otro usuario
        cls.other_tierlist = TierList.objects.create(
            user=cls.other_user,
            name='Other User Tier List',
            description='Other Description',
        )

    def setUp(self):
        self.client = Client()
        self.url = reverse('my_tierlists')

    def test_my_tierlists_login_required(self):
        """Test que se requiere login para ver mis tierlists"""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)  # Redirige a login
        self.assertTrue(response.url.startswith('/accounts/login/'))


class CreateTierlistViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='12345')
        self.god1 = God.objects.create(name='Zeus', pantheon='Greek')
        self.god2 = God.objects.create(name='Thor', pantheon='Norse')
        self.url = reverse('create_tierlist')

    def test_create_tierlist_login_required(self):
        """Test que se requiere login para crear tierlists"""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)  # Redirige a login
        self.assertTrue(response.url.startswith('/accounts/login/'))

    @patch('django.shortcuts.redirect')
    def test_create_tierlist_post(self, mock_redirect):
        """Test de la creación de una tierlist"""
        # Configurar el mock para que redirect funcione
        mock_redirect.return_value = "Redirected"
        
        self.client.login(username='testuser', password='12345')
        form_data = {
            'name': 'New Tier List',
            'description': 'New Description',
            'is_public': True,
            f'god_tier_{self.god1.id}': 'S',
            f'god_tier_{self.god2.id}': 'A',
        }
        response = self.client.post(self.url, form_data)
        
        # Verificar que se creó la tierlist
        self.assertEqual(TierList.objects.count(), 1)
        new_tierlist = TierList.objects.first()
        self.assertEqual(new_tierlist.name, 'New Tier List')
        
        # Verificar que se crearon los tiers
        self.assertEqual(Tier.objects.filter(tierlist=new_tierlist).count(), 2)
        self.assertEqual(Tier.objects.get(tierlist=new_tierlist, god=self.god1).tier, 'S')
        self.assertEqual(Tier.objects.get(tierlist=new_tierlist, god=self.god2).tier, 'A')


class TierlistDetailViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='12345')
        self.tierlist = TierList.objects.create(
            user=self.user,
            name='Test Tier List',
            description='Test Description'
        )
        self.god1 = God.objects.create(name='Zeus', pantheon='Greek')
        self.god2 = God.objects.create(name='Thor', pantheon='Norse')
        
        self.tier1 = Tier.objects.create(tierlist=self.tierlist, god=self.god1, tier='S')
        self.tier2 = Tier.objects.create(tierlist=self.tierlist, god=self.god2, tier='A')
        
        self.url = reverse('tierlist_detail', kwargs={'pk': self.tierlist.pk})

    def test_tierlist_detail_login_required(self):
        """Test que se requiere login para ver detalles de tierlist"""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)  # Redirige a login
        self.assertTrue(response.url.startswith('/accounts/login/'))



class EditTierlistViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='12345')
        self.other_user = User.objects.create_user(username='otheruser', password='12345')
        
        self.tierlist = TierList.objects.create(
            user=self.user,
            name='Test Tier List',
            description='Test Description'
        )
        
        self.god1 = God.objects.create(name='Zeus', pantheon='Greek')
        self.god2 = God.objects.create(name='Thor', pantheon='Norse')
        
        self.tier1 = Tier.objects.create(tierlist=self.tierlist, god=self.god1, tier='S')
        
        self.url = reverse('edit_tierlist', kwargs={'pk': self.tierlist.pk})

    def test_edit_tierlist_login_required(self):
        """Test que se requiere login para editar tierlist"""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)  # Redirige a login
        self.assertTrue(response.url.startswith('/accounts/login/'))

    def test_edit_tierlist_forbidden_for_other_users(self):
        """Test que solo el propietario puede editar una tierlist"""
        self.client.login(username='otheruser', password='12345')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 403)  # Forbidden


    @patch('django.shortcuts.redirect')
    def test_edit_tierlist_post(self, mock_redirect):
        """Test de la edición de una tierlist"""
        # Configurar el mock para que redirect funcione
        mock_redirect.return_value = "Redirected"
        
        self.client.login(username='testuser', password='12345')
        form_data = {
            'name': 'Updated Tier List',
            'description': 'Updated Description',
            'is_public': False,
            f'god_tier_{self.god1.id}': 'A',  # Cambio de S a A
            f'god_tier_{self.god2.id}': 'B',  # Añadir nuevo dios
        }
        response = self.client.post(self.url, form_data)
        
        # Verificar que se actualizó la tierlist
        self.tierlist.refresh_from_db()
        self.assertEqual(self.tierlist.name, 'Updated Tier List')
        self.assertEqual(self.tierlist.description, 'Updated Description')
        self.assertFalse(self.tierlist.is_public)
        
        # Verificar cambios en los tiers
        tiers = Tier.objects.filter(tierlist=self.tierlist)
        self.assertEqual(tiers.count(), 2)
        self.assertEqual(tiers.get(god=self.god1).tier, 'A')
        self.assertEqual(tiers.get(god=self.god2).tier, 'B')


class DeleteTierlistViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='12345')
        self.other_user = User.objects.create_user(username='otheruser', password='12345')
        
        self.tierlist = TierList.objects.create(
            user=self.user,
            name='Test Tier List',
            description='Test Description'
        )
        
        self.url = reverse('delete_tierlist', kwargs={'pk': self.tierlist.pk})

    def test_delete_tierlist_login_required(self):
        """Test que se requiere login para eliminar tierlist"""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)  # Redirige a login
        self.assertTrue(response.url.startswith('/accounts/login/'))

    def test_delete_tierlist_forbidden_for_other_users(self):
        """Test que solo el propietario puede eliminar una tierlist"""
        self.client.login(username='otheruser', password='12345')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 403)  # Forbidden

    @patch('django.shortcuts.redirect')
    def test_delete_tierlist_post(self, mock_redirect):
        """Test de la eliminación de una tierlist"""
        # Configurar el mock para que redirect funcione
        mock_redirect.return_value = "Redirected"
        
        self.client.login(username='testuser', password='12345')
        response = self.client.post(self.url)
        
        # Verificar que se eliminó la tierlist
        self.assertEqual(TierList.objects.count(), 0)