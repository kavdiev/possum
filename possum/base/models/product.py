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
from generic import Nom
from config import Config


logger = logging.getLogger(__name__)


class Produit(Nom):
    categorie = models.ForeignKey(Categorie, related_name="produit-categorie")
    choix_cuisson = models.BooleanField(default=False)
    choix_dish = models.BooleanField(default=False)
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
        app_label = 'base'
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

    def _clone_product(self):
        """Clone a product to keep old one for stats and reports.
        It is use with a modification of prize.

        New product is returned, and old one is disabled.
        """
        product = Produit()
        product.actif = self.actif
        self.actif = False
        self.save()
        product.prix = self.prize
        product.nom = self.nom
        product.choix_cuisson = self.choix_cuisson
        product.choix_dish = self.choix_dish
        product.choix_sauce = self.choix_sauce
        product.categorie = self.categorie
        product.price_surcharged = self.price_surcharged
        product.vat_onsite = self.vat_onsite
        product.vat_surcharged = self.vat_surcharged
        product.vat_takeaway = self.vat_takeaway
        product.save()
        for c in self.categories_ok.distinct():
            product.categories_ok.add(c)
        for p in self.produits_ok.distinct():
            product.produits_ok.add(p)
        product.save()
        return product

    def set_prize(self, prize):
        """With new prize, we have to create a new product to keep statistics
        and historics.
        """
        if prize != str(self.prix):
            product = self._clone_product()
            product.prix = prize
            product.update_vats(keep_clone=False)
            return product
        else:
            return self

    def set_category(self, category):
        self.categorie = category
        self.update_vats()

    def update_vats(self, keep_clone=True):
        """Update vat_onsite and vat_takeaway with price in TTC

        keep_clone=True : we keep a clean with old values
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
            vat_onsite = Decimal(self.prix) / (one + value) * value
            if self.categorie.surtaxable:
                price_surcharged = self.prix + surcharge
                vat = Decimal(price_surcharged) / (one + value) * value
                vat_surcharged = vat
            else:
                price_surcharged = self.prix
                vat_surcharged = vat_onsite
            value = self.categorie.vat_takeaway.value
            vat_takeaway = Decimal(self.prix) / (one + value) * value
            if self.vat_onsite != vat_onsite or \
                    self.price_surcharged != price_surcharged or \
                    self.vat_surcharged != vat_surcharged or \
                    self.vat_takeaway != vat_takeaway:
                if keep_clone:
                    product = self._clone_product()
                else:
                    product = self
                product.vat_onsite = vat_onsite
                product.price_surcharged = price_surcharged
                product.vat_surcharged = vat_surcharged
                product.vat_takeaway = vat_takeaway
                product.save()
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
                result.append("%s: %.2f" % (product.nom, product.prix))
            result.append(" ")
        return result

