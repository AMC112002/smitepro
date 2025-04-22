# forum/tests.py
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from .models import Post, Category, Comment
from .forms import PostForm, CommentForm

class CategoryModelTest(TestCase):
    def setUp(self):
        self.category = Category.objects.create(
            name='Python',
            slug='python'
        )
    
    def test_category_creation(self):
        self.assertEqual(self.category.name, 'Python')
        self.assertEqual(self.category.slug, 'python')
        self.assertEqual(str(self.category), 'Python')


class PostModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='password123'
        )
        self.category = Category.objects.create(
            name='Python',
            slug='python'
        )
        self.post = Post.objects.create(
            title='Test Post',
            content='This is a test post content',
            author=self.user,
            category=self.category
        )
    
    def test_post_creation(self):
        self.assertEqual(self.post.title, 'Test Post')
        self.assertEqual(self.post.content, 'This is a test post content')
        self.assertEqual(self.post.author, self.user)
        self.assertEqual(self.post.category, self.category)
        self.assertEqual(self.post.views, 0)
        self.assertEqual(str(self.post), 'Test Post')


class CommentModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='password123'
        )
        self.post = Post.objects.create(
            title='Test Post',
            content='This is a test post content',
            author=self.user
        )
        self.comment = Comment.objects.create(
            post=self.post,
            author=self.user,
            content='This is a test comment'
        )
    
    def test_comment_creation(self):
        self.assertEqual(self.comment.post, self.post)
        self.assertEqual(self.comment.author, self.user)
        self.assertEqual(self.comment.content, 'This is a test comment')
        self.assertEqual(str(self.comment), 'testuser - This is a test comment')


class PostFormTest(TestCase):
    def setUp(self):
        self.category = Category.objects.create(
            name='Python',
            slug='python'
        )
    
    def test_valid_form(self):
        data = {
            'title': 'Test Post',
            'content': 'This is a test post content',
            'category': self.category.id
        }
        form = PostForm(data=data)
        self.assertTrue(form.is_valid())
    
    def test_invalid_form(self):
        data = {
            'title': '',
            'content': 'This is a test post content',
            'category': self.category.id
        }
        form = PostForm(data=data)
        self.assertFalse(form.is_valid())


class CommentFormTest(TestCase):
    def test_valid_form(self):
        data = {
            'content': 'This is a test comment'
        }
        form = CommentForm(data=data)
        self.assertTrue(form.is_valid())
    
    def test_invalid_form(self):
        data = {
            'content': ''
        }
        form = CommentForm(data=data)
        self.assertFalse(form.is_valid())


class PostListViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            password='password123'
        )
        self.category = Category.objects.create(
            name='Python',
            slug='python'
        )
        # Create multiple posts for testing
        for i in range(15):  # Create 15 posts to test pagination
            Post.objects.create(
                title=f'Test Post {i}',
                content=f'This is test post {i} content',
                author=self.user,
                category=self.category
            )
    
    def test_post_list_view(self):
        response = self.client.get(reverse('forum:post_list'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'forum/post_list.html')
        # Test default pagination (9 posts per page)
        self.assertEqual(len(response.context['posts']), 9)
    
    def test_post_list_pagination(self):
        response = self.client.get(reverse('forum:post_list') + '?page=2')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['posts']), 6)  # Second page should have remaining 6 posts
    
    def test_post_list_filter_recent(self):
        response = self.client.get(reverse('forum:post_list') + '?filter=recent')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['filter_option'], 'recent')
    
    def test_post_list_filter_popular(self):
        # Create a popular post with comments
        popular_post = Post.objects.first()
        Comment.objects.create(
            post=popular_post,
            author=self.user,
            content='Test comment'
        )
        
        response = self.client.get(reverse('forum:post_list') + '?filter=popular')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['filter_option'], 'popular')
        # The post with comments should be first
        self.assertEqual(response.context['posts'][0].pk, popular_post.pk)
    
    def test_post_list_filter_unanswered(self):
        # Create a post with comments
        post_with_comment = Post.objects.first()
        Comment.objects.create(
            post=post_with_comment,
            author=self.user,
            content='Test comment'
        )
        
        response = self.client.get(reverse('forum:post_list') + '?filter=unanswered')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['filter_option'], 'unanswered')
        # Check that post with comments is not in the response
        self.assertNotIn(post_with_comment, response.context['posts'])
    
    def test_post_list_search(self):
        # Create a post with specific content for search
        search_post = Post.objects.create(
            title='Unique Search Term',
            content='This post should be found in search',
            author=self.user,
            category=self.category
        )
        
        response = self.client.get(reverse('forum:post_list') + '?search=Unique+Search')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['search_query'], 'Unique Search')
        self.assertEqual(len(response.context['posts']), 1)
        self.assertEqual(response.context['posts'][0].pk, search_post.pk)


class PostDetailViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            password='password123'
        )
        self.category = Category.objects.create(
            name='Python',
            slug='python'
        )
        self.post = Post.objects.create(
            title='Test Post',
            content='This is a test post content',
            author=self.user,
            category=self.category,
            views=0
        )
        # Create related posts
        for i in range(3):
            Post.objects.create(
                title=f'Related Post {i}',
                content=f'This is related post {i} content',
                author=self.user,
                category=self.category
            )
    
    def test_post_detail_view(self):
        response = self.client.get(reverse('forum:post_detail', kwargs={'pk': self.post.pk}))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'forum/post_detail.html')
        self.assertEqual(response.context['post'], self.post)
        
        # Test view count increases
        self.post.refresh_from_db()
        self.assertEqual(self.post.views, 1)
    
    def test_post_detail_related_posts(self):
        response = self.client.get(reverse('forum:post_detail', kwargs={'pk': self.post.pk}))
        self.assertEqual(len(response.context['related_posts']), 3)
    
    def test_add_comment(self):
        self.client.login(username='testuser', password='password123')
        response = self.client.post(
            reverse('forum:post_detail', kwargs={'pk': self.post.pk}),
            {'content': 'Test comment content'}
        )
        self.assertEqual(response.status_code, 302)  # Redirect after successful comment
        self.assertEqual(Comment.objects.count(), 1)
        comment = Comment.objects.first()
        self.assertEqual(comment.content, 'Test comment content')
        self.assertEqual(comment.author, self.user)
        self.assertEqual(comment.post, self.post)


class PostCreateViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            password='password123'
        )
        self.category = Category.objects.create(
            name='Python',
            slug='python'
        )
    
    def test_post_create_view_login_required(self):
        response = self.client.get(reverse('forum:post_create'))
        self.assertNotEqual(response.status_code, 200)  # Should redirect to login
    
    def test_post_create_view(self):
        self.client.login(username='testuser', password='password123')
        response = self.client.get(reverse('forum:post_create'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'forum/post_form.html')
    
    def test_post_create_submission(self):
        self.client.login(username='testuser', password='password123')
        response = self.client.post(
            reverse('forum:post_create'),
            {
                'title': 'New Test Post',
                'content': 'This is new test post content',
                'category': self.category.id
            }
        )
        self.assertEqual(Post.objects.count(), 1)
        post = Post.objects.first()
        self.assertEqual(post.title, 'New Test Post')
        self.assertEqual(post.content, 'This is new test post content')
        self.assertEqual(post.author, self.user)
        self.assertEqual(post.category, self.category)
        self.assertEqual(post.views, 0)


class PostEditViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            password='password123'
        )
        self.other_user = User.objects.create_user(
            username='otheruser',
            password='password123'
        )
        self.category = Category.objects.create(
            name='Python',
            slug='python'
        )
        self.post = Post.objects.create(
            title='Test Post',
            content='This is a test post content',
            author=self.user,
            category=self.category
        )
    
    def test_post_edit_view_login_required(self):
        response = self.client.get(reverse('forum:post_edit', kwargs={'pk': self.post.pk}))
        self.assertNotEqual(response.status_code, 200)  # Should redirect to login
    
    def test_post_edit_view_author_required(self):
        self.client.login(username='otheruser', password='password123')
        response = self.client.get(reverse('forum:post_edit', kwargs={'pk': self.post.pk}))
        self.assertEqual(response.status_code, 302)  # Redirect non-authors
    
    def test_post_edit_view(self):
        self.client.login(username='testuser', password='password123')
        response = self.client.get(reverse('forum:post_edit', kwargs={'pk': self.post.pk}))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'forum/post_form.html')
        self.assertTrue(response.context['edit_mode'])
    
    def test_post_edit_submission(self):
        self.client.login(username='testuser', password='password123')
        response = self.client.post(
            reverse('forum:post_edit', kwargs={'pk': self.post.pk}),
            {
                'title': 'Updated Test Post',
                'content': 'This is updated test post content',
                'category': self.category.id
            }
        )
        self.post.refresh_from_db()
        self.assertEqual(self.post.title, 'Updated Test Post')
        self.assertEqual(self.post.content, 'This is updated test post content')


class PostDeleteViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            password='password123'
        )
        self.other_user = User.objects.create_user(
            username='otheruser',
            password='password123'
        )
        self.post = Post.objects.create(
            title='Test Post',
            content='This is a test post content',
            author=self.user
        )
    
    def test_post_delete_view_login_required(self):
        response = self.client.get(reverse('forum:post_delete', kwargs={'pk': self.post.pk}))
        self.assertNotEqual(response.status_code, 200)  # Should redirect to login
    
    def test_post_delete_view_author_required(self):
        self.client.login(username='otheruser', password='password123')
        response = self.client.get(reverse('forum:post_delete', kwargs={'pk': self.post.pk}))
        self.assertEqual(response.status_code, 302)  # Redirect non-authors
    
    def test_post_delete_view(self):
        self.client.login(username='testuser', password='password123')
        response = self.client.get(reverse('forum:post_delete', kwargs={'pk': self.post.pk}))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'forum/post_confirm_delete.html')
    
    def test_post_delete_submission(self):
        self.client.login(username='testuser', password='password123')
        response = self.client.post(reverse('forum:post_delete', kwargs={'pk': self.post.pk}))
        self.assertEqual(Post.objects.count(), 0)  # Post should be deleted


class CommentEditViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            password='password123'
        )
        self.other_user = User.objects.create_user(
            username='otheruser',
            password='password123'
        )
        self.staff_user = User.objects.create_user(
            username='staffuser',
            password='password123',
            is_staff=True
        )
        self.post = Post.objects.create(
            title='Test Post',
            content='This is a test post content',
            author=self.user
        )
        self.comment = Comment.objects.create(
            post=self.post,
            author=self.user,
            content='This is a test comment'
        )
    
    def test_comment_edit_view_login_required(self):
        response = self.client.get(reverse('forum:comment_edit', kwargs={'pk': self.comment.pk}))
        self.assertNotEqual(response.status_code, 200)  # Should redirect to login
    
    def test_comment_edit_view_author_required(self):
        self.client.login(username='otheruser', password='password123')
        response = self.client.get(reverse('forum:comment_edit', kwargs={'pk': self.comment.pk}))
        self.assertEqual(response.status_code, 302)  # Redirect non-authors
    
    def test_comment_edit_view_staff_allowed(self):
        self.client.login(username='staffuser', password='password123')
        response = self.client.get(reverse('forum:comment_edit', kwargs={'pk': self.comment.pk}))
        self.assertEqual(response.status_code, 200)  # Staff should be allowed
    
    def test_comment_edit_view(self):
        self.client.login(username='testuser', password='password123')
        response = self.client.get(reverse('forum:comment_edit', kwargs={'pk': self.comment.pk}))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'forum/comment_form.html')
    
    def test_comment_edit_submission(self):
        self.client.login(username='testuser', password='password123')
        response = self.client.post(
            reverse('forum:comment_edit', kwargs={'pk': self.comment.pk}),
            {'content': 'Updated test comment'}
        )
        self.comment.refresh_from_db()
        self.assertEqual(self.comment.content, 'Updated test comment')


class CommentDeleteViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            password='password123'
        )
        self.other_user = User.objects.create_user(
            username='otheruser',
            password='password123'
        )
        self.staff_user = User.objects.create_user(
            username='staffuser',
            password='password123',
            is_staff=True
        )
        self.post = Post.objects.create(
            title='Test Post',
            content='This is a test post content',
            author=self.user
        )
        self.comment = Comment.objects.create(
            post=self.post,
            author=self.user,
            content='This is a test comment'
        )
    
    def test_comment_delete_view_login_required(self):
        response = self.client.get(reverse('forum:comment_delete', kwargs={'pk': self.comment.pk}))
        self.assertNotEqual(response.status_code, 200)  # Should redirect to login
    
    def test_comment_delete_view_author_required(self):
        self.client.login(username='otheruser', password='password123')
        response = self.client.get(reverse('forum:comment_delete', kwargs={'pk': self.comment.pk}))
        self.assertEqual(response.status_code, 302)  # Redirect non-authors
    
    def test_comment_delete_view_staff_allowed(self):
        self.client.login(username='staffuser', password='password123')
        response = self.client.get(reverse('forum:comment_delete', kwargs={'pk': self.comment.pk}))
        self.assertEqual(response.status_code, 200)  # Staff should be allowed
    
    def test_comment_delete_view(self):
        self.client.login(username='testuser', password='password123')
        response = self.client.get(reverse('forum:comment_delete', kwargs={'pk': self.comment.pk}))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'forum/comment_confirm_delete.html')
    
    def test_comment_delete_submission(self):
        self.client.login(username='testuser', password='password123')
        response = self.client.post(reverse('forum:comment_delete', kwargs={'pk': self.comment.pk}))
        self.assertEqual(Comment.objects.count(), 0)  # Comment should be deleted