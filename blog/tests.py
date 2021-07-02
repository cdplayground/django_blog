from django.test import TestCase, Client
from bs4 import BeautifulSoup
from django.contrib.auth.models import User
from .models import Post, Category


class TestView(TestCase):
    def setUp(self):
        self.client = Client()

        self.user_trumb = User.objects.create_user(username='trump', password='somepassword')
        self.user_obama = User.objects.create_user(username='obama', password='somepassword')

        self.category_programming = Category.objects.create(name='programming',slug='programming')
        self.category_music = Category.objects.create(name='music', slug='music')

        post_001 = Post.objects.create(
            title='첫번째 포스트',
            content='디지털데일리 권하영기자] 국내 배달앱 2위 요기요',
            category=self.category_programming,
            author=self.user_trumb
        )
        post_002 = Post.objects.create(
            title='두번째 포스트',
            content='원하는 내용을 채운뒤 save 버튼을 눌러보세요!!',
            category=self.category_music,
            author=self.user_obama
        )
        post_002 = Post.objects.create(
            title='세번째 포스트',
            content='category가 없을 수도 있죠',
            author=self.user_obama
        )

        def category_card_test(self, soup):
            categories_card = soup.find('div', id='categories-card')
            self.assertIn('Categories', categories_card.text)
            self.assertIn(
                f'{self.category_programming.name} ({self.category_programming.post_set.count()})', categories_card.text)
            self.assertIn(
                f'{self.category_music.name} ({self.category_music.post_set.count()})', categories_card.text)
            self.assertIn(f'미분류 (1)', categories_card.text)

    def navbar_test(self, soup):
        navbar = soup.nav
        self.assertIn('Blog', navbar.text)
        self.assertIn('About Me', navbar.text)

        logo_btn = navbar.find('a', text='Django-SY')
        self.assertEqual(logo_btn.attrs['href'], '/')

        home_btn = navbar.find('a', text='Home')
        self.assertEqual(home_btn.attrs['href'], '/')

        blog_btn = navbar.find('a', text='Blog')
        self.assertEqual(blog_btn.attrs['href'], '/blog/')

        about_me_btn = navbar.find('a', text='About Me')
        self.assertEqual(about_me_btn.attrs['href'], '/about_me/')

    def test_post_list(self):
        self.assertEqual(Post.objects.count(), 3)
        
        response = self.client.get('/blog/')
        self.assertEqual(response.status_code, 200)
        soup = BeautifulSoup(response.content, 'html.parser')
        
        self.navbar_test(soup)
        self.category_card_test(soup)

        main_area = soup.find('div', id='main-area')
        self.assertNotIn('아직 게시물이 없습니다', main_area.text)

        post_001_card = main_area.find('div', id='post-1')
        self.assertIn(self.post_001.title, post_001_card.text)
        self.assertIn(self.post_001.category.name, post_001_card.text)
                
        post_002_card = main_area.find('div', id='post-2')
        self.assertIn(self.post_002.title, post_002_card.text)
        self.assertIn(self.post_002.category.name, post_002_card.text)

        post_003_card = main_area.find('div', id='post-3')
        self.assertIn('미분류', post_003_card.text)
        self.assertIn(self.post_003.category.name, post_003_card.text)

        self.assertIn(self.user_trump.username.upper(), main_area.text)
        self.assertIn(self.user_obama.username.upper(), main_area.text)

        #포스트가 없는경우
        Post.objects.all().delete()
        self.assertEqual(Post.objects.count(), 0)
        response = self.client.get('/blog/')
        soup = BeautifulSoup(response.content, 'html.parser')
        main_area = soup.find('div', id='main-area')
        self.assertIn('아직 게시물이 없습니다', main_area.text)

    def test_post_detail(self):
        # 0.   Post가 하나 있다.
        post_001 = Post.objects.create(
            title='첫번째 포스트',
            content='디지털데일리 권하영기자] 국내 배달앱 2위 요기요',
            author=self.user_trumb
        )
        # 0.1  그 포스트의 url은 'blog/1/' 이다.
        self.assertEqual(self.post_001.get_absolute_url(), '/blog/1/')

        # 1.   첫 번째 post의 detail 페이지 테스트
        # 1.1  첫 번째 post url로 접근하면 정상적으로 작동한다. (status code: 200)
        response = self.client.get(self.post_001.get_absolute_url())
        self.assertEqual(response.status_code, 200)
        soup = BeautifulSoup(response.content, 'html.parser')

        # 1.2  post_list 페이지와 똑같은 네비게이션 바가 있다.
        # beautifulsoup를 이용하면 간단히 페이지의 태그 요소에 접근이 가능합니다.
        self.navbar_test(soup)
        self.category_card_test(soup)

        # 1.3  첫 번째 post의 title이 브라우저 탭에 표기되는 페이지 title에 있다.
        self.assertIn(self.post_001.title, soup.title.text)


        # 1.4  첫 번째 post의 title이 post-area에 있다.
        main_area = soup.find('div', id='main-area')
        post_area = main_area.find('div', id='post-area')
        self.assertIn(self.post_001.title, post_area.text)

        # 1.5  첫 번째 post의 작성자(author)가 post-area에 있다.
        # 아직 작성 불가
        self.assertIn(self.user_trump.username.upper(), post_area.text)
        # 1.6  첫 번째 post의 content가 post-area에 있다.
        self.assertIn(self.post_001.content, post_area.text)