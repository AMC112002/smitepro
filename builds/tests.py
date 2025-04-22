import unittest
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from builds.models import Build, BuildRating
from dioses.models import God
from objetos.models import Item, ItemCategory
from django.db.models import Avg
from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile
import os


class BuildModelTest(TestCase):
    def setUp(self):
        # Create test user
        self.user = User.objects.create_user(username='testuser', password='testpass')
        
        # Create test categories
        self.starter_category = ItemCategory.objects.create(name='Inicial')
        self.passive_category = ItemCategory.objects.create(name='Objeto Pasivo')
        self.relic_category = ItemCategory.objects.create(name='Reliquia')
        self.physical_category = ItemCategory.objects.create(name='Poder Físico')
        self.magical_category = ItemCategory.objects.create(name='Poder Mágico')
        
        # Create test god
        self.god = God.objects.create(name='Test God', power='Physical')
        
        # Create test items - añadimos el campo price
        self.starter_item = Item.objects.create(name='Test Starter', tier=2, price=500)
        self.starter_item.categories.add(self.starter_category)
        
        self.passive_item1 = Item.objects.create(name='Test Passive 1', tier=3, price=2500)
        self.passive_item1.categories.add(self.passive_category)
        self.passive_item1.categories.add(self.physical_category)
        
        self.passive_item2 = Item.objects.create(name='Test Passive 2', tier=3, price=2700)
        self.passive_item2.categories.add(self.passive_category)
        
        self.relic_item = Item.objects.create(name='Test Relic', tier=3, price=0)
        self.relic_item.categories.add(self.relic_category)
        
        # Create test build
        self.build = Build.objects.create(
            user=self.user,
            god=self.god,
            starter_item=self.starter_item,
            is_random=False
        )
        self.build.passive_items.add(self.passive_item1, self.passive_item2)
        self.build.relics.add(self.relic_item)

    def test_build_creation(self):
        """Test that a build can be created with correct relationships"""
        self.assertEqual(self.build.user.username, 'testuser')
        self.assertEqual(self.build.god.name, 'Test God')
        self.assertEqual(self.build.starter_item.name, 'Test Starter')
        self.assertEqual(self.build.passive_items.count(), 2)
        self.assertEqual(self.build.relics.count(), 1)
        self.assertFalse(self.build.is_random)

    def test_build_string_representation(self):
        """Test the string representation of a Build"""
        self.assertEqual(str(self.build), "Test God - testuser")

    def test_average_rating_without_ratings(self):
        """Test average_rating method returns 0 when no ratings exist"""
        self.assertEqual(self.build.average_rating(), 0)

    def test_average_rating_with_ratings(self):
        """Test average_rating method returns correct average with ratings"""
        # Create test ratings
        BuildRating.objects.create(build=self.build, user=self.user, rating=4)
        
        # Create another user and rating
        user2 = User.objects.create_user(username='testuser2', password='testpass')
        BuildRating.objects.create(build=self.build, user=user2, rating=2)
        
        self.assertEqual(self.build.average_rating(), 3.0)

    def test_total_ratings(self):
        """Test total_ratings method returns correct count"""
        self.assertEqual(self.build.total_ratings(), 0)
        
        # Create test ratings
        BuildRating.objects.create(build=self.build, user=self.user, rating=4)
        
        self.assertEqual(self.build.total_ratings(), 1)


class BuildRatingModelTest(TestCase):
    def setUp(self):
        # Create test users
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.user2 = User.objects.create_user(username='testuser2', password='testpass')
        
        # Create test god
        self.god = God.objects.create(name='Test God', power='Physical')
        
        # Create test item with price
        self.starter_item = Item.objects.create(name='Test Starter', tier=2, price=500)
        
        # Create test build
        self.build = Build.objects.create(
            user=self.user,
            god=self.god,
            starter_item=self.starter_item
        )

    def test_build_rating_creation(self):
        """Test that a build rating can be created"""
        rating = BuildRating.objects.create(
            build=self.build,
            user=self.user2,  # Different user from build creator
            rating=5,
            comment="Great build!"
        )
        
        self.assertEqual(rating.rating, 5)
        self.assertEqual(rating.comment, "Great build!")
        self.assertEqual(rating.user.username, 'testuser2')
        self.assertEqual(rating.build.god.name, 'Test God')

    def test_unique_user_build_constraint(self):
        """Test that a user can only rate a build once"""
        # Create first rating
        BuildRating.objects.create(
            build=self.build,
            user=self.user2,
            rating=4
        )
        
        # Attempt to create second rating with same user and build
        with self.assertRaises(Exception):
            BuildRating.objects.create(
                build=self.build,
                user=self.user2,
                rating=5
            )

    def test_rating_string_representation(self):
        """Test the string representation of a BuildRating"""
        rating = BuildRating.objects.create(
            build=self.build,
            user=self.user2,
            rating=3
        )
        
        self.assertEqual(str(rating), "testuser2 - Test God - 3")


class BuildViewsTest(TestCase):
    def setUp(self):
        # Create test client
        self.client = Client()

        tests_dir = os.path.join('static', 'tests')

        # Asegurar que el directorio existe
        if not os.path.exists(tests_dir):
            os.makedirs(tests_dir)

        # Ruta completa para la imagen
        image_path = os.path.join(tests_dir, 'test_image.jpg')

        with open(image_path, 'wb') as f:
            f.write(b'fake image content')

        self.test_image = SimpleUploadedFile(
            name='test_image.jpg',
            content=open(image_path, 'rb').read(),
            content_type='image/jpeg'
        )
        
        # Create test users
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.user2 = User.objects.create_user(username='testuser2', password='testpass')
        
        # Create test categories
        self.starter_category = ItemCategory.objects.create(name='Inicial')
        self.passive_category = ItemCategory.objects.create(name='Objeto Pasivo')
        self.relic_category = ItemCategory.objects.create(name='Reliquia')
        
        # Create test gods
        self.god1 = God.objects.create(name='Test God 1', power='Physical', image=self.test_image)
        self.god2 = God.objects.create(name='Test God 2', power='Magical', image=self.test_image)
        
        # Create test items with price
        self.starter_item = Item.objects.create(name='Test Starter', tier=2, price=500, image=self.test_image)
        self.starter_item.categories.add(self.starter_category)
        
        self.passive_item1 = Item.objects.create(name='Test Passive 1', tier=3, price=2500, image=self.test_image)
        self.passive_item1.categories.add(self.passive_category)
        
        self.passive_item2 = Item.objects.create(name='Test Passive 2', tier=3, price=2600, image=self.test_image)
        self.passive_item2.categories.add(self.passive_category)
        
        self.relic_item = Item.objects.create(name='Test Relic', tier=3, price=0, image=self.test_image)
        self.relic_item.categories.add(self.relic_category)
        
        # Create test builds
        self.build1 = Build.objects.create(
            user=self.user,
            god=self.god1,
            starter_item=self.starter_item,
            is_random=False
        )
        self.build1.passive_items.add(self.passive_item1)
        self.build1.relics.add(self.relic_item)
        
        self.build2 = Build.objects.create(
            user=self.user2,
            god=self.god2,
            starter_item=self.starter_item,
            is_random=False
        )
        self.build2.passive_items.add(self.passive_item2)
        self.build2.relics.add(self.relic_item)
        
        # Create random build
        self.random_build = Build.objects.create(
            user=self.user,
            god=self.god1,
            starter_item=self.starter_item,
            is_random=True
        )

    def test_build_list_view(self):
        """Test the build list view shows all non-random builds"""
        response = self.client.get(reverse('build_list'))
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'builds/build_list.html')
        
        # Check that both regular builds are in the context
        builds_in_context = list(response.context['builds'])
        self.assertEqual(len(builds_in_context), 2)
        
        # Check random builds are excluded
        build_ids = [build.id for build in builds_in_context]
        self.assertIn(self.build1.id, build_ids)
        self.assertIn(self.build2.id, build_ids)
        self.assertNotIn(self.random_build.id, build_ids)

    def test_build_list_filtered_by_god(self):
        """Test filtering builds by god"""
        response = self.client.get(f"{reverse('build_list')}?god={self.god1.id}")
        
        self.assertEqual(response.status_code, 200)
        builds_in_context = list(response.context['builds'])
        
        # Only builds for god1 should be included
        self.assertEqual(len(builds_in_context), 1)
        self.assertEqual(builds_in_context[0].id, self.build1.id)

    def test_build_list_sorted_by_rating(self):
        """Test sorting builds by rating"""
        # Add ratings to builds
        BuildRating.objects.create(build=self.build1, user=self.user2, rating=3)
        BuildRating.objects.create(build=self.build2, user=self.user, rating=5)
        
        response = self.client.get(f"{reverse('build_list')}?sort=rating")
        
        self.assertEqual(response.status_code, 200)
        builds_in_context = list(response.context['builds'])
        
        # build2 should be first (higher rating)
        self.assertEqual(builds_in_context[0].id, self.build2.id)
        self.assertEqual(builds_in_context[1].id, self.build1.id)

    def test_build_detail_view(self):
        """Test the build detail view"""
        response = self.client.get(reverse('build_detail', args=[self.build1.id]))
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'builds/build_detail.html')
        self.assertEqual(response.context['build'].id, self.build1.id)

    def test_my_builds_view_authenticated(self):
        """Test the my builds view when authenticated"""
        self.client.login(username='testuser', password='testpass')
        response = self.client.get(reverse('my_builds'))
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'builds/my_builds.html')
        
        # Only builds by current user should be included
        builds_in_context = list(response.context['builds'])
        build_ids = [build.id for build in builds_in_context]
        self.assertIn(self.build1.id, build_ids)
        self.assertNotIn(self.build2.id, build_ids)
        
        # Random builds should be excluded
        self.assertNotIn(self.random_build.id, build_ids)

    def test_my_builds_view_unauthenticated(self):
        """Test the my builds view redirects when not authenticated"""
        response = self.client.get(reverse('my_builds'))
        
        # Should redirect to login page
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.startswith('/accounts/login/'))

    def test_create_build_authenticated(self):
        """Test accessing the create build page when authenticated"""
        self.client.login(username='testuser', password='testpass')
        response = self.client.get(reverse('create_build'))
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'builds/create_build.html')

    def test_create_build_unauthenticated(self):
        """Test accessing the create build page when not authenticated"""
        response = self.client.get(reverse('create_build'))
        
        # Should redirect to login page
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.startswith('/accounts/login/'))

    def test_create_build_submission(self):
        """Test submitting a new build"""
        self.client.login(username='testuser', password='testpass')
        
        # Crear objetos adicionales para cumplir con la validación
        passive_item3 = Item.objects.create(name='Test Passive 3', tier=3, price=2700)
        passive_item3.categories.add(self.passive_category)
        
        passive_item4 = Item.objects.create(name='Test Passive 4', tier=3, price=2700)
        passive_item4.categories.add(self.passive_category)
        
        passive_item5 = Item.objects.create(name='Test Passive 5', tier=3, price=2700)
        passive_item5.categories.add(self.passive_category)
        
        relic_item2 = Item.objects.create(name='Test Relic 2', tier=3, price=0)
        relic_item2.categories.add(self.relic_category)
        
        # Actualizar los datos del formulario
        build_data = {
            'god': self.god2.id,
            'starter_item': self.starter_item.id,
            'passive_items': [
                self.passive_item1.id, 
                self.passive_item2.id, 
                passive_item3.id, 
                passive_item4.id, 
                passive_item5.id
            ],
            'relics': [self.relic_item.id, relic_item2.id],
        }
        
        initial_count = Build.objects.count()
        response = self.client.post(reverse('create_build'), data=build_data)
        
        # Comprobamos si hay errores en el formulario
        if response.status_code == 200 and 'form' in response.context:
            print(f"Form errors: {response.context['form'].errors}")
        
        # Puede redirigir a my_builds o a otro lugar
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Build.objects.count(), initial_count + 1)
        
        # Check that the new build has the correct data
        new_build = Build.objects.latest('created_at')
        self.assertEqual(new_build.user, self.user)
        self.assertEqual(new_build.god, self.god2)
        self.assertEqual(new_build.starter_item, self.starter_item)
        self.assertEqual(new_build.passive_items.count(), 5)
        self.assertEqual(new_build.relics.count(), 2)
        self.assertFalse(new_build.is_random)

    def test_edit_build_owner(self):
        """Test editing a build as the owner"""
        self.client.login(username='testuser', password='testpass')
        response = self.client.get(reverse('edit_build', args=[self.build1.id]))
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'builds/edit_build.html')
        self.assertEqual(response.context['build'].id, self.build1.id)

    def test_edit_build_not_owner(self):
        """Test editing a build as a non-owner"""
        self.client.login(username='testuser2', password='testpass')
        response = self.client.get(reverse('edit_build', args=[self.build1.id]))
        
        # Should redirect with an error message
        self.assertEqual(response.status_code, 302)

    def test_delete_build_owner(self):
        """Test deleting a build as the owner"""
        self.client.login(username='testuser', password='testpass')
        response = self.client.get(reverse('delete_build', args=[self.build1.id]))
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'builds/delete_build.html')
        
        # Test actual deletion
        initial_count = Build.objects.count()
        response = self.client.post(reverse('delete_build', args=[self.build1.id]))
        
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Build.objects.count(), initial_count - 1)
        
        # Check the build no longer exists
        with self.assertRaises(Build.DoesNotExist):
            Build.objects.get(id=self.build1.id)

    def test_delete_build_not_owner(self):
        """Test deleting a build as a non-owner"""
        self.client.login(username='testuser2', password='testpass')
        response = self.client.get(reverse('delete_build', args=[self.build1.id]))
        
        # Should redirect with an error message
        self.assertEqual(response.status_code, 302)
        
        # Check the build still exists
        self.assertTrue(Build.objects.filter(id=self.build1.id).exists())


class BuildRatingViewsTest(TestCase):
    def setUp(self):
        # Create test client
        self.client = Client()
        
        # Create test users
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.user2 = User.objects.create_user(username='testuser2', password='testpass')
        
        # Create test god
        self.god = God.objects.create(name='Test God', power='Physical')
        
        # Create test item with price
        self.starter_item = Item.objects.create(name='Test Starter', tier=2, price=500)
        
        # Create test build
        self.build = Build.objects.create(
            user=self.user,
            god=self.god,
            starter_item=self.starter_item
        )

    def test_add_rating_authenticated(self):
        """Test adding a rating when authenticated"""
        self.client.login(username='testuser2', password='testpass')
        
        rating_data = {
            'rating': 4,
            'comment': 'Good build'
        }
        
        response = self.client.post(
            reverse('build_detail', args=[self.build.id]), 
            data=rating_data
        )
        
        # Should redirect back to build detail
        self.assertEqual(response.status_code, 302)
        
        # Check the rating was created
        self.assertTrue(BuildRating.objects.filter(build=self.build, user=self.user2).exists())
        rating = BuildRating.objects.get(build=self.build, user=self.user2)
        self.assertEqual(rating.rating, 4)
        self.assertEqual(rating.comment, 'Good build')

    def test_add_rating_unauthenticated(self):
        """Test adding a rating when not authenticated"""
        rating_data = {
            'rating': 4,
            'comment': 'Good build'
        }
        
        response = self.client.post(
            reverse('build_detail', args=[self.build.id]), 
            data=rating_data
        )
        
        # Should not create a rating
        self.assertFalse(BuildRating.objects.filter(build=self.build).exists())

    def test_update_rating(self):
        """Test updating an existing rating"""
        self.client.login(username='testuser2', password='testpass')
        
        # Create initial rating
        initial_rating = BuildRating.objects.create(
            build=self.build,
            user=self.user2,
            rating=2,
            comment='Not great'
        )
        
        # Update rating
        updated_data = {
            'rating': 5,
            'comment': 'Changed my mind, it\'s excellent!'
        }
        
        response = self.client.post(
            reverse('build_detail', args=[self.build.id]), 
            data=updated_data
        )
        
        # Should redirect back to build detail
        self.assertEqual(response.status_code, 302)
        
        # Check the rating was updated
        updated_rating = BuildRating.objects.get(build=self.build, user=self.user2)
        self.assertEqual(updated_rating.rating, 5)
        self.assertEqual(updated_rating.comment, 'Changed my mind, it\'s excellent!')