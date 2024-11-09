from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

# Create your tests here.

class OptimizeGownsApiTests(APITestCase):
    def setUp(self):
        self.url = reverse('optimize_gowns_api')  # Adjust the name if necessary

    def test_optimize_gowns_valid_data(self):
        # Test with valid data
        data = {
            "gowns": [{"id": 1, "name": "Gown 1"}],
            "specifications": {"some_spec": "value"}
        }
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('results', response.data)

    def test_optimize_gowns_missing_gowns(self):
        # Test with missing gowns
        data = {
            "specifications": {"some_spec": "value"}
        }
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['error'], 'Invalid input data. Both gowns and specifications are required.')

    def test_optimize_gowns_missing_specifications(self):
        # Test with missing specifications
        data = {
            "gowns": [{"id": 1, "name": "Gown 1"}]
        }
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['error'], 'Invalid input data. Both gowns and specifications are required.')

    def test_optimize_gowns_invalid_json(self):
        # Test with invalid JSON
        response = self.client.post(self.url, '{"gowns":', content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['error'], 'Invalid JSON data')
