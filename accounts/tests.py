from django.test import TestCase, Client, TransactionTestCase
from django.urls import reverse
from django.contrib.auth.models import User
from django.core import mail
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from accounts.models import Account
import os
from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile


class RegisterViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.register_url = reverse('register')
        
    def test_register_page_loads(self):
        response = self.client.get(self.register_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'accounts/register.html')
    
    def test_successful_registration(self):
        # Create a small test image for avatar upload
        test_image = SimpleUploadedFile(
            name='test_avatar.jpg',
            content=b'',  # Empty content for simplicity
            content_type='image/jpeg'
        )
        
        data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'first_name': 'Test',
            'last_name': 'User',
            'telephone': '123456789',
            'address': 'Test Address',
            'password': 'securepassword123',
            'confirm_password': 'securepassword123',
            'avatar': test_image
        }
        
        response = self.client.post(self.register_url, data)
        
        # Check redirect to login page
        self.assertRedirects(response, reverse('login'))
        
        # Verify user and account were created
        self.assertTrue(User.objects.filter(username='testuser').exists())
        self.assertTrue(Account.objects.filter(user__username='testuser').exists())
        
        # Verify account fields
        account = Account.objects.get(user__username='testuser')
        self.assertEqual(account.telephone, '123456789')
        self.assertEqual(account.address, 'Test Address')
        self.assertTrue(account.avatar)
        
        # Clean up uploaded test files
        if account.avatar and os.path.isfile(os.path.join(settings.MEDIA_ROOT, account.avatar.name)):
            os.remove(os.path.join(settings.MEDIA_ROOT, account.avatar.name))
    
    def test_password_mismatch(self):
        data = {
            'username': 'testuser2',
            'email': 'test2@example.com',
            'first_name': 'Test',
            'last_name': 'User',
            'telephone': '123456789',
            'address': 'Test Address',
            'password': 'securepassword123',
            'confirm_password': 'differentpassword'
        }
        
        response = self.client.post(self.register_url, data)
        
        # Should stay on register page
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, self.register_url)
        
        # User should not be created
        self.assertFalse(User.objects.filter(username='testuser2').exists())


# Separate class using TransactionTestCase for testing duplicate username
class DuplicateUsernameTest(TransactionTestCase):
    def setUp(self):
        self.client = Client()
        self.register_url = reverse('register')
        # Create a user first
        self.user = User.objects.create_user(
            username='existinguser', 
            email='existing@example.com', 
            password='password123'
        )
    
    def test_duplicate_username(self):
        # Try to register with the same username
        data = {
            'username': 'existinguser',
            'email': 'new@example.com',
            'first_name': 'Test',
            'last_name': 'User',
            'telephone': '123456789',
            'address': 'Test Address',
            'password': 'securepassword123',
            'confirm_password': 'securepassword123'
        }
        
        response = self.client.post(self.register_url, data)
        
        # Should stay on register page with error message
        self.assertEqual(response.status_code, 200)
        
        # Verify that only one user exists with this username
        user_count = User.objects.filter(username='existinguser').count()
        self.assertEqual(user_count, 1)


class LoginViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.login_url = reverse('login')
        self.success_url = reverse('home')  # Changed from 'success' to 'home'
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='password123'
        )
        self.user.is_active = True
        self.user.save()
        
    def test_login_page_loads(self):
        response = self.client.get(self.login_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'accounts/login.html')
    
    def test_login_with_username(self):
        data = {
            'identifier': 'testuser',
            'password': 'password123'
        }
        
        response = self.client.post(self.login_url, data, follow=True)
        
        # Check redirect to home page (following redirects)
        self.assertRedirects(response, self.success_url, target_status_code=200)
        
        # Check if user is logged in
        self.assertTrue('_auth_user_id' in self.client.session)
    
    def test_login_with_email(self):
        data = {
            'identifier': 'test@example.com',
            'password': 'password123'
        }
        
        response = self.client.post(self.login_url, data, follow=True)
        
        # Check redirect to home page (following redirects)
        self.assertRedirects(response, self.success_url, target_status_code=200)
        
        # Check if user is logged in
        self.assertTrue('_auth_user_id' in self.client.session)
    
    def test_login_with_wrong_password(self):
        data = {
            'identifier': 'testuser',
            'password': 'wrongpassword'
        }
        
        response = self.client.post(self.login_url, data)
        
        # Should stay on login page
        self.assertEqual(response.status_code, 200)
        
        # User should not be logged in
        self.assertFalse('_auth_user_id' in self.client.session)
    
    def test_login_with_nonexistent_user(self):
        data = {
            'identifier': 'nonexistentuser',
            'password': 'password123'
        }
        
        response = self.client.post(self.login_url, data)
        
        # Should stay on login page
        self.assertEqual(response.status_code, 200)
        
        # User should not be logged in
        self.assertFalse('_auth_user_id' in self.client.session)
    
    def test_login_with_inactive_user(self):
        # Set user to inactive
        self.user.is_active = False
        self.user.save()
        
        data = {
            'identifier': 'testuser',
            'password': 'password123'
        }
        
        response = self.client.post(self.login_url, data)
        
        # Should stay on login page
        self.assertEqual(response.status_code, 200)
        
        # User should not be logged in
        self.assertFalse('_auth_user_id' in self.client.session)


class LogoutViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.logout_url = reverse('logout')
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='password123'
        )
        
    def test_logout(self):
        # Log in first
        self.client.login(username='testuser', password='password123')
        
        # Check that user is logged in
        self.assertTrue('_auth_user_id' in self.client.session)
        
        # Logout
        response = self.client.get(self.logout_url)
        
        # Check redirect to home page
        self.assertRedirects(response, reverse('home'))
        
        # Check that user is logged out
        self.assertFalse('_auth_user_id' in self.client.session)


class PasswordResetTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.password_reset_url = reverse('password_reset')
        self.password_reset_done_url = reverse('password_reset_done')
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='oldpassword123'
        )
        
    def test_password_reset_page_loads(self):
        response = self.client.get(self.password_reset_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'accounts/password_reset_form.html')
    
    def test_password_reset_request_for_existing_email(self):
        data = {
            'email': 'test@example.com'
        }
        
        response = self.client.post(self.password_reset_url, data)
        
        # Check redirect to password_reset_done page
        self.assertRedirects(response, self.password_reset_done_url)
        
        # Check that an email was sent
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].subject, 'Restablece tu contraseña en SmitePRO')
        self.assertIn('test@example.com', mail.outbox[0].to)
    
    def test_password_reset_request_for_nonexistent_email(self):
        data = {
            'email': 'nonexistent@example.com'
        }
        
        response = self.client.post(self.password_reset_url, data)
        
        # Should still redirect to password_reset_done page for security
        self.assertRedirects(response, self.password_reset_done_url)
        
        # No email should be sent
        self.assertEqual(len(mail.outbox), 0)
    
    def test_password_reset_confirm(self):
        # Generate token and uid for the user
        token = default_token_generator.make_token(self.user)
        uid = urlsafe_base64_encode(force_bytes(self.user.pk))
        
        # Build the confirm URL
        confirm_url = reverse('password_reset_confirm', kwargs={'uidb64': uid, 'token': token})
        
        # Get the confirm page
        response = self.client.get(confirm_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'accounts/password_reset_confirm.html')
        
        # Post new password
        data = {
            'new_password': 'newpassword123',
            'confirm_password': 'newpassword123'
        }
        
        response = self.client.post(confirm_url, data)
        
        # Check redirect to login page
        self.assertRedirects(response, reverse('login'))
        
        # Verify password was changed
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password('newpassword123'))
    
    def test_password_reset_confirm_password_mismatch(self):
        # Generate token and uid for the user
        token = default_token_generator.make_token(self.user)
        uid = urlsafe_base64_encode(force_bytes(self.user.pk))
        
        # Build the confirm URL
        confirm_url = reverse('password_reset_confirm', kwargs={'uidb64': uid, 'token': token})
        
        # Post mismatched passwords
        data = {
            'new_password': 'newpassword123',
            'confirm_password': 'differentpassword'
        }
        
        response = self.client.post(confirm_url, data)
        
        # Should stay on confirm page
        self.assertEqual(response.status_code, 200)
        
        # Password should not be changed
        self.user.refresh_from_db()
        self.assertFalse(self.user.check_password('newpassword123'))
        self.assertTrue(self.user.check_password('oldpassword123'))


class ProfileViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.perfil_url = reverse('perfil')
        self.login_url = reverse('login')
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='password123'
        )
        Account.objects.create(
            user=self.user,
            telephone='123456789',
            address='Test Address'
        )
        
    def test_profile_page_requires_login(self):
        # Try to access profile without login
        response = self.client.get(self.perfil_url)
        
        # Should redirect to login page
        self.assertRedirects(response, f'{self.login_url}?next={self.perfil_url}')
    
    def test_profile_page_loads_when_logged_in(self):
        # Log in
        self.client.login(username='testuser', password='password123')
        
        # Access profile page
        response = self.client.get(self.perfil_url)
        
        # Check that page loads successfully
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'accounts/perfil.html')


class AccountModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='password123'
        )
        self.account = Account.objects.create(
            user=self.user,
            telephone='123456789',
            address='Test Address'
        )
        
    def test_account_creation(self):
        self.assertEqual(self.account.user.username, 'testuser')
        self.assertEqual(self.account.telephone, '123456789')
        self.assertEqual(self.account.address, 'Test Address')
        self.assertEqual(self.account.role, Account.USER)  # Default role
        
    def test_account_str_method(self):
        self.assertEqual(str(self.account), 'testuser')
        
    def test_admin_role(self):
        self.account.role = Account.ADMIN
        self.account.save()
        self.assertEqual(self.account.role, 'Administrador')
        
    def test_delete_user_cascades_to_account(self):
        # Count accounts before
        account_count = Account.objects.count()
        self.assertEqual(account_count, 1)
        
        # Delete user
        self.user.delete()
        
        # Account should be deleted too (CASCADE)
        account_count = Account.objects.count()
        self.assertEqual(account_count, 0)