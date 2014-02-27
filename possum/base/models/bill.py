# -*- coding: utf-8 -*-
#
#    Copyright 2009-2014 Sébastien Bonnegent
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
try:
    from collections import OrderedDict
except:
    #  Needed if you use a python older than 2.7
    from ordereddict import OrderedDict

import datetime
from decimal import Decimal
from django.db import models
import logging
from category import Categorie
from config import Config
from follow import Follow
from payment import Paiement, PaiementType
from printer import Printer
from product_sold import ProduitVendu
from django.contrib.auth.models import User


logger = logging.getLogger(__name__)


class Facture(models.Model):
    """
    surcharge: surtaxe à ajouter par produits par exemple
        dans le cas d'une terrasse pour laquelle le service
        est surtaxé
    following: liste des envois en cuisine
    next: si présent, la prochaine catégorie a envoyée en
        cuisine
    in_use_by: 1 seule personne peut éditer une facture en cours
    """
    date_creation = models.DateTimeField('creer le', auto_now_add=True)
    table = models.ForeignKey('Table',
                              null=True,
                              blank=True,
                              related_name="facture-table")
    couverts = models.PositiveIntegerField("nombre de couverts", default=0)
    produits = models.ManyToManyField(ProduitVendu,
                                      related_name="les produits vendus",
                                      limit_choices_to={
                                      'date__gt': datetime.datetime.today()})
    total_ttc = models.DecimalField(max_digits=9,
                                    decimal_places=2,
                                    default=0)
    paiements = models.ManyToManyField('Paiement',
                                       related_name="les paiements",
                                       limit_choices_to={
                                       'date__gt': datetime.datetime.today()})
    vats = models.ManyToManyField('VATOnBill',
                                  related_name="vat total for each vat on "
                                  "a bill")
    restant_a_payer = models.DecimalField(max_digits=9,
                                          decimal_places=2,
                                          default=0)
    saved_in_stats = models.BooleanField(default=False)
    in_use_by = models.ForeignKey(User, null=True, blank=True)
    onsite = models.BooleanField(default=True)
    surcharge = models.BooleanField(default=False)
    following = models.ManyToManyField('Follow',
                                       null=True,
                                       blank=True)
    category_to_follow = models.ForeignKey('Categorie', null=True, blank=True)

    class Meta:
        get_latest_by = 'id'
        app_label = 'base'
        permissions = (
            ("p1", "can use manager part"),
            ("p2", "can use carte part"),
            ("p3", "can use POS"),
            ("p4", "can ..."),
            ("p5", "can ..."),
            ("p6", "can ..."),
            ("p7", "can ..."),
            ("p8", "can ..."),
            ("p9", "can ..."),
        )

    def __unicode__(self):
        if self.date_creation:
            # TODO strftime copy pasted =~ 20 time (Date class ?)
            date = self.date_creation.strftime("%H:%M %d/%m")
        else:
            date = "--:-- --/--"
        return u"%s" % date

    def __cmp__(self, other):
        """
            Les factures sont triees par date_creation.
            D'abord les plus récentes, puis les plus vieilles.
        """
        return cmp(self.date_creation, other.date_creation)

    def used_by(self, user=None):
        """mark bill as 'in edition by user', only one
            person can edit a bill at a time
        """
        if user != self.in_use_by:
            self.in_use_by = user
            self.save()

    def regroup_produits(self):
        dict_produits = OrderedDict()
        for produit in self.produits.iterator():
            if str(produit) in dict_produits:
                dict_produits[str(produit)].append((produit.id, produit))
            else:
                dict_produits[str(produit)] = [(produit.id, produit)]
        return dict_produits

    def update_kitchen(self):
        """If one, set the first category to prepare in the
        kitchen. Example: Entree if there are Entree and Plat.
        """
        logger.debug("[%s] update kitchen" % self.id)
        todolist = []
        for product in self.produits.filter(sent=False).iterator():
            if product.est_un_menu():
                for sub in product.contient.filter(
                        sent=False,
                        produit__categorie__made_in_kitchen=True).iterator():
                    todolist.append(sub.made_with)
            elif product.produit.categorie.made_in_kitchen:
                todolist.append(product.made_with)

        if todolist:
            todolist.sort()
            self.category_to_follow = todolist[0]
        else:
            self.category_to_follow = None
        self.save()

    def get_first_todolist_for_kitchen(self):
        """Prepare la liste des produits a envoyer en cuisine
        """
        categories = []
        products = {}
        for product in self.produits.iterator():
            if product.est_un_menu():
                for subproduct in product.contient.filter(produit__categorie__made_in_kitchen=True).iterator():
                    # cas des menus
                    if subproduct.made_with not in categories:
                        categories.append(subproduct.made_with)
                    if subproduct.made_with.id not in products:
                        products[subproduct.made_with.id] = []
                    name = subproduct.produit.nom
                    if subproduct.produit.choix_cuisson:
                        if subproduct.cuisson:
                            name += ": %s" % subproduct.cuisson.nom_facture
                        else:
                            name += ": ?"
                    products[subproduct.made_with.id].append(name)
            else:
                if product.produit.categorie.made_in_kitchen:
                    if product.made_with not in categories:
                        categories.append(product.made_with)
                    if product.made_with.id not in products:
                        products[product.made_with.id] = []
                    name = product.produit.nom
                    if product.produit.choix_cuisson:
                        name += ": %s" % product.cuisson
                    products[product.made_with.id].append(name)
        categories.sort()
        todolist = []
        for category in categories:
            todolist.append("***> %s" % category.nom)
            for product in products[category.id]:
                todolist.append(product)
            todolist.append(" ")
        return todolist

    def get_products_for_category(self, category):
        """Return ProduitVendu list for this category
        """
        products_list = []
        for product in self.produits.iterator():
            if product.est_un_menu():
                for sub in product.contient.iterator():
                    if not sub.sent and sub.made_with == category:
                        products_list.append(sub)
            else:
                if not product.sent and product.made_with == category:
                    products_list.append(product)
        return products_list

    def send_in_the_kitchen(self):
        """We send the first category available to the kitchen.
        """
        if self.category_to_follow:
            follow = Follow(category=self.category_to_follow)
            follow.save()
            todolist = []
            heure = follow.date.strftime("%H:%M")
            # heure = datetime.datetime.now().strftime("%H:%M")
            todolist.append("[%s] Table %s (%s couv.)" % (heure, self.table,
                                                          self.couverts))
            todolist.append(">>> envoye %s" % follow.category.nom)
            todolist.append(" ")
            nb_products_sent = self.produits.filter(sent=True).count()
            # liste des produits qui doivent etre envoyés en cuisine
            products = self.get_products_for_category(follow.category)
            for product in products:
                product.sent = True
                product.save()
            follow.produits = products
            if nb_products_sent == 0:
                # on crée le ticket avec la liste des produits et
                # des suites
                products = self.get_first_todolist_for_kitchen()
                if products:
                    todolist += products
            else:
                products.sort()
                for product in products:
                    todolist.append(product)
            for printer in Printer.objects.filter(kitchen=True):
                result = printer.regroup_list_and_print(todolist,
                                                        "kitchen-%s-%s" % (
                                                        self.id,
                                                        follow.category.id))
                if not result:
                    return False
            follow.save()
            self.following.add(follow)
            self.update_kitchen()
            return True

    def guest_couverts(self):
        """Essaye de deviner le nombre de couverts"""
        nb = {}
        # categories = Categorie.objects.filter(made_in_kitchen=True)
        for categorie in Categorie.objects.filter(made_in_kitchen=True):
            nb[categorie.nom] = 0
        for vendu in self.produits.iterator():
            if vendu.produit.categorie.nom in nb:
                nb[vendu.produit.categorie.nom] += 1
            for sous_produit in vendu.contient.iterator():
                if sous_produit.produit.categorie.nom in nb:
                    nb[sous_produit.produit.categorie.nom] += 1
        return max(nb.values())

    def set_couverts(self, nb):
        """Change le nombre de couvert"""
        self.couverts = nb
        self.save()

    def set_table(self, table):
        """Change la table de la facture
        On prend en compte le changement de tarification si changement
        de zone.

        On ne traite pas le cas ou les 2 tables sont surtaxées à des montants
        différents.
        """
        self.table = table
        self.save()
        if self.is_surcharged() != self.surcharge:
            self.update_surcharge()

    def set_onsite(self, onsite):
        """onsite: Boolean"""
        self.onsite = onsite
        self.save()
        if self.is_surcharged() != self.surcharge:
            self.update_surcharge()

    def update_surcharge(self):
        self.surcharge = self.is_surcharged()
        self.save()
        self.update()

    def non_soldees(self):
        """ Return the list of unpaid facture
        :return: A list of Facture
        TODO: est ce encore utile ?
        """
        liste = []
        for i in Facture.objects.exclude(restant_a_payer=0).iterator():
            liste.append(i)
        for i in Facture.objects.filter(produits__isnull=True).iterator():
            liste.append(i)
        return liste

    def update(self):
        """Update prize and kitchen
        """
        logger.debug("[%s] update prize" % self.id)
        self.total_ttc = Decimal("0")
        self.restant_a_payer = Decimal("0")
        for v in self.vats.iterator():
            v.total = 0
            v.save()
        for product in self.produits.iterator():
            self.add_product_prize(product)
        for payment in self.paiements.iterator():
            self.restant_a_payer -= payment.montant
        self.save()

    def add_product_prize(self, sold):
        """Ajoute le prix d'un ProduitVendu sur la facture.
        Le ProduitVendu se trouve deja dans la liste
        des produits."""
        if self.surcharge:
            if not sold.produit.price_surcharged:
                # TODO: just in case for backwards comtability
                # in case Produit has no price_surcharged
                logger.info("[%s] product without price_surcharged" %
                            sold.produit.id)
                sold.produit.update_vats(keep_clone=False)
            sold.set_prize(sold.produit.price_surcharged)
            vat = sold.produit.categorie.vat_onsite
            value = sold.produit.vat_surcharged
        else:
            sold.set_prize(sold.produit.prix)
            if self.onsite:
                vat = sold.produit.categorie.vat_onsite
                value = sold.produit.vat_onsite
            else:
                vat = sold.produit.categorie.vat_takeaway
                value = sold.produit.vat_takeaway
        ttc = Decimal(sold.prix)
        self.total_ttc += ttc
        self.restant_a_payer += ttc
        self.save()
        vatonbill, created = self.vats.get_or_create(vat=vat)
        vatonbill.total += value
        vatonbill.save()

    def add_product(self, sold):
        """Ajout d'un produit à la facture.
        Si c'est le premier produit alors on modifie la date de creation
        :param sold: ProduitVendu
        """
        if sold.produit.actif:
            if self.produits.count() == 0:
                self.date_creation = datetime.datetime.now()
            sold.made_with = sold.produit.categorie
            sold.save()
            self.produits.add(sold)
        else:
            logger.warning("[%s] try to add an inactive Produit()" % self.id)

    def del_payment(self, payment):
        """On supprime un paiement"""
        if payment in self.paiements.iterator():
            self.paiements.remove(payment)
            payment.delete()
            self.save()
            self.update()
        else:
            logger.warning("[%s] on essaye de supprimer un paiement "
                           "qui n'est pas dans la facture: %s"
                           % (self, payment))

    def is_valid_payment(self, montant):
        ''' Vérifie un paiement avant add_payment '''
        if self.restant_a_payer <= Decimal("0"):
            logger.info("[%s] nouveau paiement ignore car restant"
                        " a payer <= 0 (%5.2f)" % (self,
                                                   self.restant_a_payer))
            return False
        if not self.produits:
            logger.debug("Pas de produit, donc rien a payer")
            return False
        if float(montant) == 0.0:
            logger.debug("Le montant n'est pas indique.")
            return False
        return True

    def add_payment(self, type_payment, montant, valeur_unitaire="1.0"):
        """
        :param type_payment: Un TypePaiement
        :param montant: String convertissable en décimal
        :param valeur_unitaire : String convertissable en décimal
        :return: Boolean
        """
        if not self.is_valid_payment(montant):
            return False
        paiement = Paiement()
        paiement.type = type_payment
        paiement.valeur_unitaire = Decimal(valeur_unitaire)
        if type_payment.fixed_value:
            # Dans ce cas le montant est le nombre de ticket
            paiement.nb_tickets = int(montant)
            paiement.montant = paiement.nb_tickets * paiement.valeur_unitaire
        else:
            paiement.montant = Decimal(montant)
        # On enregistre ce paiement
        logger.debug("Nouveau paiement : {0}".format(paiement))
        paiement.save()
        self.paiements.add(paiement)
        if paiement.montant > self.restant_a_payer:
            # Si le montant est superieur au restant du alors on rembourse en
            # espece.
            self.rendre_monnaie(paiement)
        self.restant_a_payer -= paiement.montant
        self.save()
        return True

    def rendre_monnaie(self, paiement):
        '''Régularisation si le montant payé est superieur au montant
        de la facture'''
        monnaie = Paiement()
        payment_for_refunds = Config.objects.get(key="payment_for_refunds"
                                                 ).value
        monnaie.type = PaiementType.objects.get(id=payment_for_refunds)
        monnaie.montant = self.restant_a_payer - paiement.montant
        monnaie.save()
        self.paiements.add(monnaie)
        self.restant_a_payer -= monnaie.montant

    def est_soldee(self):
        """La facture a été utilisée et soldée"""
        if self.restant_a_payer == 0 and self.produits.count() > 0:
            return True
        else:
            return False

    def est_un_repas(self):
        """Est ce que la facture contient un element qui est
        fabriqué en cuisine, dans ce cas on considère que
        c'est de la restauration.
        """
        for sold in self.produits.iterator():
            if sold.produit.categorie.made_in_kitchen:
                return True
            if sold.contient.filter(produit__categorie__made_in_kitchen=True
                                    ).count():
                return True
        return False

    def is_empty(self):
        """La facture est vierge"""
        if self.restant_a_payer == 0 and self.produits.count() == 0:
            return True
        else:
            return False

    def is_surcharged(self):
        """
        Table is surtaxed et il n'y a pas de nourriture.
        """
        if self.onsite:
            for vendu in self.produits.iterator():
                logger.debug("test with produit: %s and categorie id: %d" % (
                             vendu.produit.nom, vendu.produit.categorie.id))
                if vendu.produit.categorie.disable_surtaxe:
                    logger.debug("pas de surtaxe")
                    return False
            if self.table:
                return self.table.is_surcharged()
            else:
                return False
        else:
            return False

    def get_bills_for(self, date):
        """Retourne la liste des factures soldees du jour 'date'
        date de type datetime
        """
        date_min = datetime.datetime(date.year, date.month, date.day, 5)
        tmp = date_min + datetime.timedelta(days=1)
        date_max = datetime.datetime(tmp.year, tmp.month, tmp.day, 5)
        bills = Facture.objects.filter(date_creation__gt=date_min,
                                       date_creation__lt=date_max,
                                       restant_a_payer=0)
        return bills.exclude(produits__isnull=True)

    def print_ticket(self):
        try:
            printer = Printer.objects.filter(billing=True)[0]
        except:
            return False
        ticket = []
        ticket.append("Le %s" % self.date_creation.strftime("%d/%m/%Y %H:%M"))
        if self.table and self.couverts:
            ticket.append("Table: %s / %s couverts" % (self.table,
                                                       self.couverts))
        separateur = '-' * printer.width
        ticket.append(separateur)
        dict_vendu = OrderedDict()
        for vendu in self.produits.order_by("produit__categorie__priorite"):
            if vendu.produit.nom in dict_vendu:
                dict_vendu[vendu.produit.nom].append(vendu.prix)
            else:
                dict_vendu[vendu.produit.nom] = [vendu.prix]
        for nom, prix in dict_vendu.items():
            name = nom[:25]
            prize = "% 3.2f" % prix[0]
            # la largeur disponible correspond à la largeur du ticket
            # sans la 1er partie (" 1 ") et sans la largeur du prix
            # " 1 largeur_dispo PRIX"
            largeur_dispo = printer.width - 4 - len(prize)
            if len(nom) < largeur_dispo:
                name = nom
            else:
                longueur_max = largeur_dispo - 2
                name = nom[:longueur_max]
            remplissage = " " * (largeur_dispo - len(name))
            ticket.append("%s x %s%s%s" % (len(prix),
                                           name,
                                           remplissage,
                                           prize))
        ticket.append(separateur)
        ticket.append("  Total: % 8.2f Eur." % self.total_ttc)
        for vatonbill in self.vats.iterator():
            ticket.append("  TVA % 5.2f%%: % 6.2f Eur." % (vatonbill.vat.tax,
                                                           vatonbill.total))
        ticket.append(separateur)
        return printer.print_list(ticket, "invoice-%s" % self.id,
                                  with_header=True)

    def get_working_day(self):
        """Retourne la journee de travail officiel
            (qui fini a 5h du matin)
            date de type datetime.datetime.now()
        """
        if self.date_creation.hour < 5:
            # jour de travail precedent
            return self.date_creation - datetime.timedelta(days=1)
        else:
            return self.date_creation

    def reduce_sold_list(self, sold_list):
        """les élèments ProduitVendu de sold_list
        sont regroupés par 'élèment identique en fonction
        de leur Produit d'origine, de leurs options et de leurs
        notes
        """
        sold_dict = {}
        for sold in sold_list:
            if not sold.est_un_menu():
                key = sold.get_identifier()
                if key in sold_dict:
                    logger.debug("[%s] increment count for this key" % key)
                    sold_dict[key].count += 1
                else:
                    logger.debug("[%s] new key" % key)
                    sold_dict[key] = sold
                    sold_dict[key].count = 1
        return sold_dict.values()

    def get_sold_list_on_last_follow(self):
        if self.following.count():
            follow = self.following.latest()
            return self.reduce_sold_list(follow.produits.all())
        else:
            return []
