# -*- coding: utf-8 -*-
#
#    Copyright 2009-2014 Sébastien Bonnegent
#
#    This file is part of POSSUM.
#
#    POSSUM is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    POSSUM is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with POSSUM.  If not, see <http://www.gnu.org/licenses/>.
#
from datetime import datetime
from decimal import Decimal
from django.db import models
import logging
from category import Categorie
from generic import NomDouble
from product import Produit
from options import Cuisson, Sauce, Dish
from config import Config
from note import Note


logger = logging.getLogger(__name__)


class ProduitVendu(models.Model):
    """le prix sert a affiche correctement les prix pour les surtaxes
    """
    date = models.DateTimeField(auto_now_add=True)
    produit = models.ForeignKey(Produit, related_name="produitvendu-produit")
    cuisson = models.ForeignKey(Cuisson, null=True, blank=True,
                                related_name="produitvendu-cuisson")
    prix = models.DecimalField(max_digits=7, decimal_places=2, default=0)
    sauces = models.ManyToManyField(Sauce, null=True, blank=True,
                                   related_name="produitvendu-sauce")
    dishes = models.ManyToManyField(Dish, null=True, blank=True)
    # dans le cas d'un menu, peut contenir d'autres produits
    contient = models.ManyToManyField('self')
    notes = models.ManyToManyField(Note, null=True, blank=True)
    # faut-il préparer ce plat avec les entrées ?
    made_with = models.ForeignKey(Categorie, related_name="produit-kitchen",
                                  null=True)
    # a-t-il été envoyé en cuisine
    sent = models.BooleanField(default=False)

    class Meta:
        app_label = 'base'
        ordering = ['produit', ]

    def __unicode__(self):
        return u"%s" % self.produit.nom

    def isFull(self):
        """
        True si tous les élèments sous présents (les sous produits pour 
        les formules) et False sinon. """
        nb_produits = self.contient.count()
        nb_categories = self.produit.categories_ok.count()
        if nb_produits == nb_categories:
            logger.debug("product is full")
            return True
        elif nb_produits > nb_categories:
            logger.warning("product id [%s] have more products that categories authorized" % self.id)
            return True
        else:
            logger.debug("product is not full")
            return False

    def __cmp__(self, other):
        if self.produit.categorie == other.produit.categorie:
            return cmp(self.produit.nom, other.produit.nom)
        else:
            return cmp(self.produit.categorie, other.produit.categorie)

    def est_un_menu(self):
        if self.produit.categories_ok.count():
            return True
        else:
            return False

    def get_menu_products(self):
        products = []
        for product in self.contient.order_by("produit__categorie__priorite").iterator():
            products.append(product)
        return products

    def get_menu_resume(self):
        """Return a short string with product in menu
        """
        products = []
        for product in self.get_menu_products():
            tmp = product.produit.nom[:6]
            if product.cuisson:
                tmp += product.cuisson.nom_facture
            products.append(tmp)
        return "/".join(products)

    def getFreeCategorie(self):
        """Retourne la premiere categorie dans la liste categories_ok
        qui n'a pas de produit dans la partir 'contient'. Sinon retourne
        None """
        if self.produit.categories_ok.count() > 0:
            for categorie in self.produit.categories_ok.order_by("priorite").iterator():
                if self.contient.filter(produit__categorie=categorie).count() == 0:
                    return categorie
        else:
            logger.warning("Product [%s] have no categories_ok, return None" % self.id)
        return None
