# Copyright 2016, 2023 John J. Rofrano. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
Test cases for Product Model

Test cases can be run with:
    nosetests
    coverage report -m

While debugging just these tests it's convenient to use this:
    nosetests --stop tests/test_models.py:TestProductModel

"""
import os
import logging
import unittest
from decimal import Decimal
from service.models import Product, Category, db, DataValidationError
from service import app
from tests.factories import ProductFactory


DATABASE_URI = os.getenv(
    "DATABASE_URI", "postgresql://postgres:postgres@localhost:5432/postgres"
)


######################################################################
#  P R O D U C T   M O D E L   T E S T   C A S E S
######################################################################
# pylint: disable=too-many-public-methods
class TestProductModel(unittest.TestCase):
    """Test Cases for Product Model"""

    @classmethod
    def setUpClass(cls):
        """This runs once before the entire test suite"""
        app.config["TESTING"] = True
        app.config["DEBUG"] = False
        app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URI
        app.logger.setLevel(logging.CRITICAL)
        Product.init_db(app)

    @classmethod
    def tearDownClass(cls):
        """This runs once after the entire test suite"""
        db.session.close()

    def setUp(self):
        """This runs before each test"""
        db.session.query(Product).delete()  # clean up the last tests
        db.session.commit()

    def tearDown(self):
        """This runs after each test"""
        db.session.remove()

    ######################################################################
    #  T E S T   C A S E S
    ######################################################################

    def test_create_a_product(self):
        """It should Create a product and assert that it exists"""
        product = Product(name="Fedora", description="A red hat", price=12.50, available=True, category=Category.CLOTHS)
        self.assertEqual(str(product), "<Product Fedora id=[None]>")
        self.assertTrue(product is not None)
        self.assertEqual(product.id, None)
        self.assertEqual(product.name, "Fedora")
        self.assertEqual(product.description, "A red hat")
        self.assertEqual(product.available, True)
        self.assertEqual(product.price, 12.50)
        self.assertEqual(product.category, Category.CLOTHS)

    def test_add_a_product(self):
        """It should Create a product and add it to the database"""
        products = Product.all()
        self.assertEqual(products, [])
        product = ProductFactory()
        product.id = None
        product.create()
        # Assert that it was assigned an id and shows up in the database
        self.assertIsNotNone(product.id)
        products = Product.all()
        self.assertEqual(len(products), 1)
        # Check that it matches the original product
        new_product = products[0]
        self.assertEqual(new_product.name, product.name)
        self.assertEqual(new_product.description, product.description)
        self.assertEqual(Decimal(new_product.price), product.price)
        self.assertEqual(new_product.available, product.available)
        self.assertEqual(new_product.category, product.category)

    #
    # ADD YOUR TEST CASES HERE
    #
    def test_get_a_product(self):
        """It should Get a product via its id """
        products = Product.all()
        self.assertEqual(products, [])
        product = ProductFactory()
        logging.info(product.serialize())
        product.id = None
        product.create()
        # Assert that it was assigned an id and shows up in the database
        self.assertIsNotNone(product.id)

        # retrieve product from DB
        retrieved_product = Product.find(product.id)

        # check that its the same
        self.assertEqual(retrieved_product.id, product.id)
        self.assertEqual(retrieved_product.name, product.name)
        self.assertEqual(retrieved_product.description, product.description)
        self.assertEqual(retrieved_product.price, product.price)
        self.assertEqual(retrieved_product.available, product.available)
        self.assertEqual(retrieved_product.category, product.category)

    def test_update_a_product(self):
        """It should Update a product and assert that it was updated"""
        products = Product.all()
        self.assertEqual(products, [])
        product = ProductFactory()
        logging.info(product.serialize())
        product.id = None
        product.create()

        original_id = product.id

        # log created product
        logging.info(product.serialize())

        product.description = "This is not a duck."
        product.update()

        products = Product.all()
        self.assertEqual(len(products), 1)
        self.assertEqual(product.id, original_id)
        self.assertEqual(product.description, "This is not a duck.")

    def test_update_no_id_a_product(self):
        """It should Update a product and assert that it was updated"""
        products = Product.all()
        self.assertEqual(products, [])
        product = ProductFactory()
        logging.info(product.serialize())
        product.id = None
        self.assertRaises(DataValidationError, product.update)

    def test_delete_a_product(self):
        """It should Delete a product and assert that its deleted."""
        products = Product.all()
        self.assertEqual(products, [])
        product = ProductFactory()
        logging.info(product.serialize())
        product.id = None
        product.create()

        products = Product.all()
        self.assertEqual(len(products), 1)

        product.delete()
        products = Product.all()
        self.assertEqual(len(products), 0)

    def test_list_all_products(self):
        """It should create 5 products and then ensure they were created."""
        products = Product.all()
        self.assertEqual(products, [])

        # create 5 Products and ensure that their id is not None
        for _ in range(5):
            product = ProductFactory()
            logging.info(product.serialize())
            product.id = None
            product.create()
            self.assertIsNotNone(product.id)

        # get all products and ensure there are 5
        products = Product.all()
        self.assertEqual(len(products), 5)

    def test_find_by_availability_product(self):
        """It should create 10 products and test find_by_availability"""
        products = Product.all()
        self.assertEqual(products, [])

        # create 10 Products and ensure that their id is not None
        products = ProductFactory.create_batch(10)
        for product in products:
            product.id = None
            product.create()
            self.assertIsNotNone(product.id)

        available = products[0].available
        count = len([product for product in products if product.available == available])

        found = Product.find_by_availability(available)
        self.assertEqual(found.count(), count)

        for product in found:
            self.assertEqual(product.available, available)

    def test_find_by_price_product(self):
        """It should create 10 products and test find_by_price"""
        products = Product.all()
        self.assertEqual(products, [])

        # create 10 Products and ensure that their id is not None
        products = ProductFactory.create_batch(10)
        for product in products:
            product.id = None
            product.create()
            self.assertIsNotNone(product.id)

        price = float(products[0].price)
        count = len([product for product in products if float(product.price) == price])

        found = Product.find_by_price(price)
        self.assertEqual(found.count(), count)

        for product in found:
            self.assertEqual(float(product.price), price)

    def test_find_by_price_string_product(self):
        """It should create 10 products and test find_by_price using a string value"""
        products = Product.all()
        self.assertEqual(products, [])

        # create 10 Products and ensure that their id is not None
        products = ProductFactory.create_batch(10)
        for product in products:
            product.id = None
            product.create()
            self.assertIsNotNone(product.id)

        price = float(products[0].price)
        count = len([product for product in products if float(product.price) == price])

        found = Product.find_by_price(str(price))
        self.assertEqual(found.count(), count)

        for product in found:
            self.assertEqual(float(product.price), price)

    def test_find_by_name_product(self):
        """It should create 10 products and test find_by_name"""
        products = Product.all()
        self.assertEqual(products, [])

        # create 10 Products and ensure that their id is not None
        products = ProductFactory.create_batch(10)
        for product in products:
            product.id = None
            product.create()
            self.assertIsNotNone(product.id)

        name = products[0].name
        count = len([product for product in products if product.name == name])

        found = Product.find_by_name(name)
        self.assertEqual(found.count(), count)

        for product in found:
            self.assertEqual(product.name, name)

    def test_find_by_category_product(self):
        """It should create 10 products and test find_by_category"""
        products = Product.all()
        self.assertEqual(products, [])

        # create 10 Products and ensure that their id is not None
        products = ProductFactory.create_batch(10)
        for product in products:
            product.id = None
            product.create()
            self.assertIsNotNone(product.id)

        category = products[0].category
        count = len([product for product in products if product.category == category])

        found = Product.find_by_category(category)
        self.assertEqual(found.count(), count)

        for product in found:
            self.assertEqual(product.category, category)

    def test_serialize__a_product(self):
        """It should serialize a product to dictionary """
        products = Product.all()
        self.assertEqual(products, [])
        product = ProductFactory()
        logging.info(product.serialize())

        serialized = product.serialize()
        self.assertEqual(serialized["name"], product.name)
        self.assertEqual(serialized["description"], product.description)
        self.assertEqual(float(serialized["price"]), float(product.price))
        self.assertEqual(serialized["available"], product.available)
        self.assertEqual(serialized["category"], product.category.name)

    def test_deserialize_a_product(self):
        """It should deserialize a dictionary into a product """
        products = Product.all()
        self.assertEqual(products, [])

        fake_product = ProductFactory()
        product_dict = {
            "name": fake_product.name,
            "description": fake_product.description,
            "price": fake_product.price,
            "available": fake_product.available,
            "category": fake_product.category.name,
        }

        product = Product()
        product.deserialize(product_dict)

    def test_deserialize_not_bool_a_product(self):
        """It shoudl throw an error when available is not a bool. """
        products = Product.all()
        self.assertEqual(products, [])
        fake_product = ProductFactory()
        product_dict = {
            "name": fake_product.name,
            "description": fake_product.description,
            "price": fake_product.price,
            "available": "TOTALLY REAL BOOL",
            "category": fake_product.category.name,
        }
        product = ProductFactory()
        product.available = "TRUE"
        with self.assertRaises(DataValidationError):
            product.deserialize(product_dict)

        product_dict = {
            "name": fake_product.name,
            "description": fake_product.description,
            "price": "apple",
            "available": True,
            "category": fake_product.category.name,
        }
        with self.assertRaises(DataValidationError):
            product.deserialize([])
