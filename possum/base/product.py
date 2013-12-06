# -*- coding: utf-8 -*-
#
#    Copyright 2009-2013 Sébastien Bonnegent
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

from possum.base.category import Categorie
from possum.base.generic import NomDouble
from possum.base.options import Cuisson, Sauce, Accompagnement
from possum.base.config import Config


logger = logging.getLogger(__name__)


class Produit(NomDouble):
    categorie = models.ForeignKey(Categorie, related_name="produit-categorie")
    choix_cuisson = models.BooleanField(default=False)
    choix_accompagnement = models.BooleanField(default=False)
    choix_sauce = models.BooleanField(default=False)
    # pour les menus / formules
    # categories authorisees
    categories_ok = models.ManyToManyField(Categorie)
    # produits authorises
    produits_ok = models.ManyToManyField('self')
    actif = models.BooleanField(default=True)
    # max_digits: la longueur totale du nombre (avec les décimaux)
    # decimal_places: la partie décimale
    # ici: 2 chiffres après la virgule et 5 chiffres pour la partie entière
    prix = models.DecimalField(max_digits=7, decimal_places=2, default=0)
    price_surcharged = models.DecimalField(max_digits=7,
                                           decimal_places=2,
                                           default=0)
    vat_onsite = models.DecimalField(max_digits=7, decimal_places=2, default=0)
    vat_surcharged = models.DecimalField(max_digits=7,
                                         decimal_places=2,
                                         default=0)
    vat_takeaway = models.DecimalField(max_digits=7,
                                       decimal_places=2,
                                       default=0)

    def __cmp__(self, other):
        if self.categorie == other.categorie:
            return cmp(self.nom, other.nom)
        else:
            return cmp(self.categorie, other.categorie)

    class Meta:
        ordering = ['categorie', 'nom']
#        ordering = ['-actif', 'nom']

    def __unicode__(self):
#        return u"[%s] %s (%.2f€)" % (self.categorie.nom, self.nom, self.prix)
        return u"%s" % self.nom

    def est_un_menu(self):
        if self.categories_ok.count():
            return True
        else:
            return False

    def get_prize(self):
        return "%.2f" % self.prix

    def set_prize(self, prize):
        """With new prize, we have to create a new product to keep statistics
        and historics.
        """
        if prize != str(self.prix):
            product = Produit()
            product.actif = self.actif
            self.actif = False
            self.save()
            product.prix = prize
            product.nom = self.nom
            product.nom_facture = self.nom_facture
            product.choix_cuisson = self.choix_cuisson
            product.choix_accompagnement = self.choix_accompagnement
            product.choix_sauce = self.choix_sauce
            product.categorie = self.categorie
            product.save()
            product.update_vats()
            for c in self.categories_ok.distinct():
                product.categories_ok.add(c)
            for p in self.produits_ok.distinct():
                product.produits_ok.add(p)
            product.save()
            return product
        else:
            return self

    def set_category(self, category):
        self.categorie = category
        self.update_vats()

    def update_vats(self):
        """Update vat_onsite and vat_takeaway with price in TTC
        """
        price_surcharge, created = Config.objects.get_or_create(key="price_"
                                                                "surcharge")
        if created:
            price_surcharge.value = "0.2"
            price_surcharge.save()
        surcharge = Decimal(price_surcharge.value)
        one = Decimal('1')
        if self.categorie.vat_onsite and self.categorie.vat_takeaway:
            value = self.categorie.vat_onsite.value
            self.vat_onsite = Decimal(self.prix) / (one + value) * value
            if self.categorie.surtaxable:
                self.price_surcharged = self.prix + surcharge
                vat = Decimal(self.price_surcharged) / (one + value) * value
                self.vat_surcharged = vat
            else:
                self.price_surcharged = self.prix
                self.vat_surcharged = self.vat_onsite
            value = self.categorie.vat_takeaway.value
            self.vat_takeaway = Decimal(self.prix) / (one + value) * value
            self.save()
        else:
            logger.warning("[%s] categorie without VAT" % self.categorie)

    def get_prize_takeaway(self):
        if self.categorie:
            if self.categorie.vat_takeaway:
                ttc = self.prix * self.categorie.vat_takeaway.value
                return ttc
            else:
                return self.prix
        else:
            return self.prix

    def get_prize_onsite(self):
        if self.categorie:
            if self.categorie.vat_onsite:
                ttc = self.prix * self.categorie.vat_onsite.value
                return ttc
            else:
                return self.prix
        else:
            return self.prix

    def get_list_with_all_products(self):
        result = []
        result.append(datetime.now().strftime("%d/%m/%Y %H:%M"))
        for category in Categorie.objects.order_by('priorite', 'nom'):
            name = "[%s]" % category.nom
            if category.made_in_kitchen:
                name += "[K]"
            result.append(name)
            for product in Produit.objects.filter(categorie=category,
                                                  actif=True):
                result.append("%s: %.2f" % (product.nom_facture, product.prix))
            result.append(" ")
        return result


class ProduitVendu(models.Model):
    """le prix sert a affiche correctement les prix pour les surtaxes
    """
    date = models.DateTimeField(auto_now_add=True)
    produit = models.ForeignKey(Produit, related_name="produitvendu-produit")
    cuisson = models.ForeignKey(Cuisson, null=True, blank=True,
                                related_name="produitvendu-cuisson")
    prix = models.DecimalField(max_digits=7, decimal_places=2, default=0)
    sauce = models.ForeignKey(Sauce, null=True, blank=True,
                              related_name="produitvendu-sauce")
    accompagnement = models.ForeignKey(Accompagnement, null=True, blank=True,
                                       related_name="produitvendu-accompagnement")
    # dans le cas d'un menu, peut contenir d'autres produits
    contient = models.ManyToManyField('self')
    # faut-il préparer ce plat avec les entrées ?
    made_with = models.ForeignKey(Categorie, related_name="produit-kitchen",
                                  null=True)
    # a-t-il été envoyé en cuisine
    sent = models.BooleanField(default=False)

    class Meta:
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
