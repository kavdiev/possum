"""
This file demonstrates two different styles of tests (one doctest and one
unittest). These will both pass when you run "manage.py test".

Replace these with more appropriate tests for your application.
"""

from django.test import TestCase
from possum.base.models import VAT
from decimal import Decimal

class VATTests(TestCase):
    def test_set_tax(self):
        """
        """
        vat = VAT()
        vat.set_tax("19.6")
        self.failUnlessEqual(vat.tax, "19.6")
        self.failUnlessEqual(vat.value, Decimal("0.196"))


