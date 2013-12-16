#!/usr/bin/python
# -*- coding: utf-8 -*-

from django.utils.unittest.case import TestCase
from possum.base.models import Categorie


class Tests_Categories(TestCase):

    def test_cmp(self):
        cat1 = Categorie(nom="nom1", priorite=1)
        cat2 = Categorie(nom="nom2")
        cat3 = Categorie(nom="nom3", priorite=1)
        liste = []
        liste.append(cat3)
        liste.append(cat2)
        liste.append(cat1)
        self.assertEqual(cat3, liste[0])
        self.assertEqual(cat2, liste[1])
        self.assertEqual(cat1, liste[2])
        liste.sort()
        self.assertEqual(cat1, liste[0])
        self.assertEqual(cat2, liste[1])
        self.assertEqual(cat3, liste[2])
