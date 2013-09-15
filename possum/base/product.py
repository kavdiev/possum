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
from django.db import models
from possum.base.generic import NomDouble
from possum.base.category import Categorie
from possum.base.options import Cuisson, Sauce, Accompagnement

class Produit(NomDouble):
    categorie = models.ForeignKey('Categorie', related_name="produit-categorie")
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

    def __cmp__(self,other):
        if self.categorie == other.categorie:
            return cmp(self.nom,other.nom)
        else:
            return cmp(self.categorie,other.categorie)

    class Meta:
        ordering = ('categorie', 'nom')
#        ordering = ['-actif', 'nom']

    def __unicode__(self):
#        return u"[%s] %s (%.2f€)" % (self.categorie.nom, self.nom, self.prix)
        return u"%s" % self.nom

    def est_un_menu(self):
        if self.categories_ok.count():
            return True
        else:
            return False

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
            for c in self.categories_ok.distinct():
                product.categories_ok.add(c)
            for p in self.produits_ok.distinct():
                product.produits_ok.add(p)
            product.save()
            return product
        else:
            return self

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

class ProduitVendu(models.Model):
    """le prix sert a affiche correctement les prix pour les surtaxes
    """
    date = models.DateTimeField(auto_now_add=True)
#    facture = models.ForeignKey('Facture', related_name="produitvendu-facture")
    #facture = models.ForeignKey('Facture', limit_choices_to = {'date_creation__gt': datetime.datetime.today()})
    produit = models.ForeignKey('Produit', related_name="produitvendu-produit")
    cuisson = models.ForeignKey('Cuisson', null=True, blank=True, related_name="produitvendu-cuisson")
    prix = models.DecimalField(max_digits=7, decimal_places=2, default=0)
    sauce = models.ForeignKey('Sauce', null=True, blank=True, related_name="produitvendu-sauce")
    accompagnement = models.ForeignKey('Accompagnement', null=True, blank=True, related_name="produitvendu-accompagnement")
    # dans le cas d'un menu, peut contenir d'autres produits
#    contient = models.ManyToManyField(Produit, null=True)
    contient = models.ManyToManyField('self')

    class Meta:
        ordering = ('produit',)

    def __unicode__(self):
        return u"%s" % self.produit.nom

    def isFull(self):
        """
        True si tous les élèments sous présents (les sous produits pour les formules)
        et False sinon.

        >>> vendu = ProduitVendu()
        >>> vendu.save()
        >>> vendu.isFull()
        True
        >>> cat1 = Categorie(nom="cat1")
        >>> cat1.save()
        >>> cat2 = Categorie(nom="cat2")
        >>> cat2.save()
        >>> vendu.categories_ok.add(cat1, cat2)
        >>> vendu.isFull()
        False
        >>> vendu.produits = [ 1 ]
        >>> vendu.isFull()
        False
        >>> vendu.produits = [ 1, 2 ]
        >>> vendu.isFull()
        True
        >>> vendu.produits = [ 1, 2, 3 ]
        >>> vendu.isFull()
        True
        """
        nb_produits = self.contient.count()
        nb_categories = self.produit.categories_ok.count()
        if nb_produits == nb_categories:
#            logging.debug("product is full")
            return True
        elif nb_produits > nb_categories:
 #           logging.warning("product id "+str(self.id)+" have more products that categories authorized")
            return True
        else:
#            logging.debug("product is not full")
            return False

    def __cmp__(self,other):
        if self.produit.categorie == other.produit.categorie:
            return cmp(self.produit.nom,other.produit.nom)
        else:
            return cmp(self.produit.categorie,other.produit.categorie)

    def est_un_menu(self):
        if self.produit.categories_ok.count():
            return True
        else:
            return False

    def get_menu_resume(self):
        """Return a short string with product in menu
        """
        if self.est_un_menu():
            products = []
            for product in self.contient.all():
                tmp = product.produit.nom[:6]
                if product.cuisson:
                    tmp += product.cuisson.nom_facture
                products.append(tmp)
            return "/".join(products)
        else:
            return ""

    def getFreeCategorie(self):
        """Retourne la premiere categorie dans la liste categories_ok
        qui n'a pas de produit dans la partir 'contient'. Sinon retourne
        None

        >>> f = Facture(id=3)
        >>> cat1 = Categorie(id=1, nom="cat1")
        >>> cat2 = Categorie(id=2, nom="cat2")
        >>> produit1 = Produit(id=1, nom="p1", categorie=cat1)
        >>> produit2 = Produit(id=2, nom="p2", categorie=cat2)
        >>> vendu = ProduitVendu(id=1, produit=produit1, facture=f)
        >>> vendu.getFreeCategorie()
        0
        >>> produit1.categories_ok.add(cat1, cat2)
        >>> vendu.getFreeCategorie()
        0
        >>> sub = ProduitVendu(id=2, produit=produit1, facture=f)
        >>> vendu.contient.add(sub)
        >>> vendu.getFreeCategorie()
        1
        >>> sub = ProduitVendu(id=3, produit=produit2, facture=f)
        >>> sub.produit.categorie = cat2
        >>> vendu.contient.add(sub)
        >>> vendu.getFreeCategorie()
        0
        """
        if self.produit.categories_ok.count() > 0:
            for categorie in self.produit.categories_ok.order_by("priorite").iterator():
                if self.contient.filter(produit__categorie=categorie).count() == 0:
                    return categorie
        else:
            logging.warning("Product "+str(self.id)+" have no categories_ok, return None")
        return None

