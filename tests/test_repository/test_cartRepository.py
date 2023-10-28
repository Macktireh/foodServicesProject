import unittest

from flask import Flask
from flask_testing import TestCase

from app import createApp, db
from repository.cartRepository import cartRepository
from repository.orderRepository import orderRepository
from repository.userRepository import userRepository
from tests.fixture import Fixture


class CartRepositoryTestCase(TestCase):

    def create_app(self) -> Flask:
        app, _ = createApp("testing")
        return app

    def setUp(self) -> None:
        db.create_all()

        Fixture.createOrders(1, 2, 1, 1)[0]
        self.user1, self.user2 = userRepository.getAll()

        self.data = {
            "userId": self.user1.id,
            "orders": orderRepository.filterAll(userId=self.user1.id),
        }

    def tearDown(self) -> None:
        db.session.remove()
        db.drop_all()

    def test_create_cart(self) -> None:
        cart = cartRepository.create(**self.data)
        self.assertIsNotNone(cart.id)
        self.assertEqual(cart.userId, self.data["userId"])
        self.assertEqual(cart.orders, self.data["orders"])
        self.assertEqual(len(cart.orders), len(self.data["orders"]))

    def test_get_all_carts(self) -> None:
        cart1 = cartRepository.create(**self.data)
        cart2 = cartRepository.create(userId=self.user2.id)
        carts = cartRepository.getAll()
        self.assertEqual(len(carts), 2)

    def test_get_cart_by_id(self) -> None:
        cart = cartRepository.create(**self.data)
        retrieved_cart = cartRepository.getById(cart.id)
        self.assertIsNotNone(retrieved_cart)
        self.assertEqual(retrieved_cart.id, cart.id)

    def test_get_cart_by_public_id(self) -> None:
        cart = cartRepository.create(**self.data)
        retrieved_cart = cartRepository.getByPublicId(cart.publicId)
        self.assertIsNotNone(retrieved_cart)
        self.assertEqual(retrieved_cart.id, cart.id)

    def test_filter_carts(self) -> None:
        cart1 = cartRepository.create(**self.data)
        cart2 = cartRepository.create(userId=self.user2.id)
        filtered_cart = cartRepository.filter(userId=self.data["userId"])
        self.assertIsNotNone(filtered_cart)
        self.assertEqual(filtered_cart.id, cart1.id)

    def test_filter_all_carts(self) -> None:
        cart1 = cartRepository.create(**self.data)
        cart2 = cartRepository.create(userId=self.user2.id)
        filtered_carts = cartRepository.filterAll(userId=self.data["userId"])
        self.assertEqual(len(filtered_carts), 1)

    def test_get_or_create_cart(self) -> None:
        cart, created = cartRepository.getOrCreate(userId=self.data["userId"])
        self.assertTrue(created)
        cart2, created2 = cartRepository.getOrCreate(userId=self.data["userId"])
        self.assertFalse(created2)
        self.assertEqual(cart.id, cart2.id)

    def test_delete_cart(self) -> None:
        cart = cartRepository.create(**self.data)
        self.assertIsNotNone(cart)
        cartRepository.delete(cart)
        retrieved_cart = cartRepository.getById(cart.id)
        self.assertIsNone(retrieved_cart)


if __name__ == "__main__":
    unittest.main()
