from django.test import TestCase
from .models import Product


class PriceRangeAPITests(TestCase):

    @classmethod
    def setUpTestData(cls):
        Product.objects.create(
            name="Notebook",
            price=150
        )
        Product.objects.create(
            name="Mouse",
            price=450
        )

    def test_valid_price_range(self):
        response = self.client.get(
            "/api/products/price-range/",
            {
                "min_price": "100",
                "max_price": "500"
            }
        )

        self.assertEqual(response.status_code, 200)

        data = response.json()

        self.assertEqual(data["count"], 2)
        self.assertEqual(len(data["products"]), 2)
        
    def test_missing_parameters(self):
        response = self.client.get(
            "/api/products/price-range/",
            {
                "min_price": "100"
            }
        )

        self.assertEqual(response.status_code, 400)

        data = response.json()

        self.assertIn("error", data)
        self.assertEqual(data["error"], "Invalid price range")
        
    def test_duplicate_parameter(self):
        response = self.client.get(
            "/api/products/price-range/",
            {
                "min_price": ["100", "200"],
                "max_price": "500"
            }
        )

        self.assertEqual(response.status_code, 400)

        data = response.json()

        self.assertIn("error", data)
        self.assertEqual(data["error"], "Invalid price range")
        
    
    def test_equal_price_boundary(self):
        response = self.client.get(
            "/api/products/price-range/",
            {
                "min_price": "100",
                "max_price": "450"
            }
        )

        self.assertEqual(response.status_code, 200)

        data = response.json()
        names = [p["name"] for p in data["products"]]

        self.assertIn("Notebook", names)
        self.assertNotIn("Mouse", names)
        self.assertEqual(data["count"], 1)

        
    def test_price_sorting(self):
        response = self.client.get(
            "/api/products/price-range/",
            {
                "min_price": "100",
                "max_price": "500"
            }
        )

        self.assertEqual(response.status_code, 200)

        data = response.json()

        sort_keys = [
        (p["price"], p["id"])
            for p in data["products"]
        ]

        self.assertEqual(sort_keys, sorted(sort_keys))
        
    def test_very_large_number(self):
        response = self.client.get(
            "/api/products/price-range/",
            {
                "min_price": "100",
                "max_price": "9" * 5000
            }
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(
        response.json()["error"],
        "Invalid price range"
    )
