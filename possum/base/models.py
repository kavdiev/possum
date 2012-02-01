# -*- coding: utf-8 -*-
#
#    Copyright 2009, 2010, 2011, 2012 Sébastien Bonnegent
#
#    This file is part of POSSUM.
#
#    POSSUM is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
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
#import io
import os

from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from django.db.models import Avg, Max, Min, Sum
from possum.base.stats import StatsJour, StatsJourGeneral, \
    StatsJourPaiement, StatsJourProduit, StatsJourCategorie
from possum.base.bill import Facture

LONGUEUR_IHM = 60
LONGUEUR_FACTURE = 35

def remplissage(nb,  caractere,  largeur):
    """caractere est le caractere de remplissage"""
    milieu = caractere
    # on ajoute len(milieu) a nb
    nb += 1
    while nb < largeur:
        milieu += caractere
        nb += 1
    return milieu

# les classes generiques
class Nom(models.Model):
    nom = models.CharField(max_length=LONGUEUR_IHM)

    def __unicode__(self):
        return self.nom

    def __cmp__(self,other):
        return cmp(self.nom, other.nom)

    class Meta:
        abstract = True
        ordering = ['nom']

class NomDouble(Nom):
    nom_facture = models.CharField(max_length=LONGUEUR_FACTURE)

    class Meta:
        abstract = True

class Priorite(models.Model):
    """Getter / setter: si priorite inferieur à 0 on reste à 0
    """
    priorite = models.PositiveIntegerField(default=0)


    class Meta:
        abstract = True
        ordering = ['priorite']

    def __cmp__(self, other):
        return cmp(self.priorite,other.priorite)

# les classes metiers
class Couleur(Nom):
    red = models.PositiveIntegerField(default=255)
    green = models.PositiveIntegerField(default=255)
    blue = models.PositiveIntegerField(default=255)

    def __unicode__(self):
        return "%s [%d / %d / %d]" % (self.nom, self.red, self.green, self.blue)

    def web(self):
        """Retourne la couleur sous la forme #ffe013
        """
        result = "#"
        for rgb in [self.red, self.green, self.blue]:
            tmp = hex(rgb).split('x')[1]
            if len(tmp) == 1:
                result += "0%s" % tmp
            elif len(tmp) == 2:
                result += tmp
            else:
                logging.warning("valeur trop grande")
        return result

    def set_from_rgb(self, color):
        """Set a color from a color like: #123454"""
        try:
            self.red = int(color[1:3], 16)
            self.green = int(color[3:5], 16)
            self.blue = int(color[5:7], 16)
            return True
        except:
            return False

class Cuisson(Nom, Priorite):
    """Cuisson d'un produit"""
    couleur = models.ForeignKey('Couleur', null=True, blank=True, related_name="cuisson-couleur")

class Sauce(Nom):
    """Sauce d'un produit"""
    couleur = models.ForeignKey('Couleur', null=True, blank=True, related_name="sauce-couleur")

class Accompagnement(Nom):
    """Accompagnement d'un produit"""
    couleur = models.ForeignKey('Couleur', null=True, blank=True, related_name="accompagnement-couleur")

class Etat(Nom, Priorite):
    """Etat d'une facture"""

    def __cmp__(self, other):
        return cmp(self.priorite,other.priorite)

class Suivi(models.Model):
    """Suivi des etats"""
    facture = models.ForeignKey('Facture', related_name="suivi-facture")
    etat = models.ForeignKey('Etat', related_name="suivi-etat")
    date = models.DateTimeField('depuis le', auto_now_add=True)

    def __unicode__(self):
        return "Facture %s : etat %s" % (self.facture, self.etat.nom)

class Categorie(Nom, Priorite):
    surtaxable = models.BooleanField("majoration terrasse", default=False)
    couleur = models.ForeignKey('Couleur', null=True, blank=True, related_name="categorie-couleur")
#    majoration_terrasse = models.BooleanField()
#    couleur = models.ForeignKey(Couleur)
    alcool = models.BooleanField(default=False)
    disable_surtaxe = models.BooleanField("peut enlever la surtaxe presente", default=False)

    def __cmp__(self,other):
        """
        Classement par priorite_facture (plus la valeur est petite,
        plus elle est prioritaire), puis par nom_ihm en cas d'égalité.

        >>> cat1 = Categorie(nom="nom1",priorite=1)
        >>> cat2 = Categorie(nom="nom2")
        >>> cat3 = Categorie(nom="nom3",priorite=1)
        >>> liste = []
        >>> liste.append(cat3)
        >>> liste.append(cat2)
        >>> liste.append(cat1)
        >>> liste
        [<Categorie: [0] [nom3]>, <Categorie: [0] [nom2]>, <Categorie: [0] [nom1]>]
        >>> liste.sort()
        >>> liste
        [<Categorie: [0] [nom2]>, <Categorie: [0] [nom1]>, <Categorie: [0] [nom3]>]
        """
        if self.priorite == other.priorite:
            return cmp(self.nom,other.nom)
        else:
            return cmp(self.priorite,other.priorite)

    def show(self):
        nb = Produit.objects.filter(categorie=self,actif=True).count()
        if self.surtaxable:
            # soumis a la majoration terrasse
            infos = "MAJ"
        else:
            infos = "___"
        if self.disable_surtaxe:
            # peut desactiver une eventuelle surtaxe
            infos += " DIS"
        else:
            infos += " ___"
#        return u"1 %s % 12.2f" % (self.produit.nom_facture, self.prix)
        return u"%-18s (% 3d produits)  [%s]" % (self.nom[:18], nb, infos)

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

    def show(self):
#        return u"1 %s % 12.2f" % (self.produit.nom_facture, self.prix)
        return u" 1 %-25s % 7.2f" % (self.nom_facture[:25], self.prix)

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

    def show(self):
#        return u"1 %s % 12.2f" % (self.produit.nom_facture, self.prix)
        return u"1 %-25s % 7.2f" % (self.produit.nom_facture[:25], self.prix)

    def showSubProducts(self):
        return u"   - %s " % self.produit.nom_facture

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

class Zone(Nom):
    surtaxe = models.BooleanField("zone surtaxée ?", default=False)
    prix_surtaxe = models.DecimalField(max_digits=4, decimal_places=2, default=0)
#    prix_surtaxe = models.PositiveIntegerField("surtaxe en centimes")

    def est_surtaxe(self):
#       logging.debug("surtaxe de %d centimes sur la zone %s" % (self.surtaxe))
        return self.surtaxe

class Table(Nom):
    zone = models.ForeignKey('Zone', related_name="table-zone")

    def est_surtaxe(self):
        if self.zone:
            result = self.zone.est_surtaxe()
        else:
            # par defaut, il n'y a pas de surtaxe
            result = False
        return result

class LogType(Nom):
    """Correspond au type de Log ainsi qu'au type de stats"""
#    pass
    description = models.CharField(max_length=200, blank=True)

class Log(models.Model):
    date = models.DateTimeField('creer le', auto_now_add=True)
    type = models.ForeignKey('LogType', related_name="log-logtype")

    class Meta:
        get_latest_by = 'date'

    def __unicode__(self):
        return "[%s] %s" % (self.date.strftime("%H:%M %d/%m/%Y"), self.type.nom)

class PaiementType(Priorite, NomDouble):
    """Type de paiment"""
    fixed_value = models.BooleanField("ticket ?", default=False)
#    last_value = models.PositiveIntegerField("dernière valeur", default=0)

class Paiement(models.Model):
    """valeur_unitaire: pour gerer les montants des tickets restos"""
    #facture = models.ForeignKey('Facture', related_name="paiement-facture")
    type = models.ForeignKey('PaiementType', related_name="paiement-type")
#    montant = models.IntegerField("TTC")
#    valeur_unitaire = models.PositiveIntegerField(default=1)
    montant = models.DecimalField(max_digits=9, decimal_places=2, default=0)
    valeur_unitaire = models.DecimalField(max_digits=9, decimal_places=2, default=1)
    date = models.DateTimeField('encaisser le', auto_now_add=True)
    nb_tickets = models.PositiveIntegerField(default=0)

    class Meta:
        get_latest_by = 'date'

    def __unicode__(self):
        if self.type.fixed_value:
            return u"%-20s % 8.2f €    (%d tickets x %5.2f €)" % ( \
                    self.type.nom, self.montant, self.nb_tickets, \
                    self.valeur_unitaire)
        else:
            return u"%-20s % 8.2f €" % (self.type.nom, self.montant)

    def __cmp__(self,other):
        return cmp(self.date.date,other.date.date)

    def show(self):
        return str(self)


