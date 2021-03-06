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

from django.db import models
import logging
from category import Categorie
from product import Produit
from options import Cuisson, Option
from note import Note

logger = logging.getLogger(__name__)


class ProduitVendu(models.Model):
    """le prix sert a affiche correctement les prix pour les surtaxes

    options1 et options2 sont les options sélectionnées.
    """
    date = models.DateTimeField(auto_now_add=True)
    produit = models.ForeignKey(Produit, related_name="produitvendu-produit")
    cuisson = models.ForeignKey(Cuisson, null=True, blank=True,
                                related_name="produitvendu-cuisson")
    prix = models.DecimalField(max_digits=7, decimal_places=2, default=0)
    options = models.ManyToManyField(Option, null=True, blank=True)
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
        """Affichage différent si menu ou pas
        """
        if self.notes.count():
            tmp = "* "
        else:
            tmp = ""
        tmp += self.produit.nom
        if self.prix:
            tmp += " (%.2f)" % self.prix
        if self.produit.categories_ok.count():
            # cas du menu
            products = []
            for sold in self.contient.iterator():
                name = sold.produit.nom[:6]
                if sold.cuisson:
                    name += sold.cuisson.nom_facture
                products.append(name)
            tmp += " "
            tmp += "/".join(products)
        else:
            # cas d'un Produit simple
            if self.cuisson:
                tmp += " %s" % self.cuisson.nom_facture
        return tmp

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

    def get_identifier(self):
        """Retourne un identifiant qui défini le Produit() et ses options
        """
        if self.notes.count():
            notes = "N".join([str(i.id) for i in self.notes.all()])
        else:
            notes = ""
        if self.options.count():
            options = "O".join([str(i.id) for i in self.options.all()])
        else:
            options = ""
        if self.cuisson:
            cuisson = "C%s" % self.cuisson.id
        else:
            cuisson = ""
        if self.produit:
            produit = str(self.produit.id)
        else:
            produit = ""
        return "P%s_C%s_O%s_N%s" % (produit, cuisson, options, notes)

    def set_prize(self, prize):
        """Set prize for the product sold
        """
        if self.prix != prize:
            logger.debug("[%s] prize: %s > %s" % (self.id, self.prix, prize))
            self.prix = prize
            self.save()
