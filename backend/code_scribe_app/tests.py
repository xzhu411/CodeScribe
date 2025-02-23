from django.test import TestCase, Client
from django.urls import reverse
from .models import Article
import json

class ProcessModelRequestTests(TestCase):
    def setUp(self):
        self.client = Client()
        # 创建一个测试文章
        self.article = Article.objects.create(
            title='Test Article',
            content='# Heading 1\nContent under heading 1.\n# Heading 2\nContent under heading 2.'
        )

    def test_process_model_request_valid_command(self):
        url = reverse('process_model_request')
        data = {'command': 'generate summary'}
        response = self.client.post(url, json.dumps(data), content_type='application/json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['status'], 'success')
        self.assertIn('doc', response.json()['data'])

    def test_process_model_request_empty_command(self):
        url = reverse('process_model_request')
        data = {'command': ''}
        response = self.client.post(url, json.dumps(data), content_type='application/json')
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()['status'], 'error')
        self.assertEqual(response.json()['message'], 'Input cannot be empty')

    def test_process_model_request_invalid_method(self):
        url = reverse('process_model_request')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 405)
        self.assertEqual(response.json()['status'], 'error')
        self.assertEqual(response.json()['message'], 'Invalid request method')
