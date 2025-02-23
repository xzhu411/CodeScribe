from django.test import TestCase
from django.urls import reverse
from .models import Article

class ArticleViewTests(TestCase):
    def setUp(self):
        # Create a test article
        self.article = Article.objects.create(
            title='Test Article',
            content='# Heading 1\nContent under heading 1.\n# Heading 2\nContent under heading 2.'
        )

    def test_markdown_view_page_1(self):
        url = reverse('markdown_view', args=[self.article.id])
        response = self.client.get(url, {'page': 1})
        self.assertEqual(response.status_code, 200)
        # self.assertIn('Heading 1', response.json()['content'][0]['text'])
        self.assertIn('Heading 1', response.json()['content'][0]['children'][0]['raw'])


    def test_markdown_view_page_out_of_range(self):
        url = reverse('markdown_view', args=[self.article.id])
        response = self.client.get(url, {'page': 10})
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()['error'], '頁碼超出範圍')
