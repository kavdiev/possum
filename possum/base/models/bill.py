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
    """Main class of POSSUM

    :param DateTime date_creation: Creation of bill
    :param Table table: Table where are guests, default None
    :param PositiveInteger couverts: Number of guests, default 0
    :param ProduitVendu produits: List of products sold
    :param Decimal total_ttc: Amount TTC
    :param Paiement paiements: List of payments
    :param VATOnBill vats: Amount of VAT HT by VAT
    :param Decimal restant_a_payer: Amount TTC not yet record
    :param Boolean saved_in_stats: Bill is saved in Stat() ? default False
    :param User in_use_by: Someone is editing ?
    :param Boolean onsite: Is it on site or take away ? default True
    :param Boolean surcharge: Is it surtaxed ? default False
    :param Follow following:
    :param Categorie category_to_follow: Next category to send in kitchen
    """
    date_creation = models.DateTimeField('creer le', auto_now_add=True)
    table = models.ForeignKey('Table',
                              null=True,
                              blank=True,
                              related_name="facture-table")
    couverts = models.PositiveIntegerField("nombre de couverts", default=0)
    produits = models.ManyToManyField(ProduitVendu,
                                      related_name="les produits vendus")
    total_ttc = models.DecimalField(max_digits=9,
                                    decimal_places=2,
                                    default=0)
    paiements = models.ManyToManyField('Paiement',
                                       related_name="les paiements")
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
        """We sort Facture() by date, first new Facture first and older after"""
        return cmp(self.date_creation, other.date_creation)

    def used_by(self, user=None):
        """Mark bill as 'in edition by user', only one
            person can edit a bill at a time
        """
        if user != self.in_use_by:
            self.in_use_by = user
            self.save()

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

    def get_products_for_category(self, category):
        """Return ProduitVendu list for this category

        :returni: list of ProduitVendu
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

    def prepare_products(self, products):
        """Prepare a list to create a print ticket for kitchen
        products: list of ProduitVendu()
        return: list of ""
        """
        output = []
        for product in self.reduced_sold_list(products, full=True):
            tmp = "%dx %s " % (product.count, product.produit.nom)
            if product.cuisson:
                tmp += "%s " % product.cuisson
            tmp += ",".join([option.name for option in product.options.all()])
            output.append(tmp)
            for note in product.notes.all():
                output.append("!> %s" % note.message)
        return output

    def print_ticket_kitchen(self):
        """Prepare and send ticket to printers in kitchen.
        """
        output = True
        if self.category_to_follow:
            follow = Follow(category=self.category_to_follow)
            follow.save()
            todolist = []
            # header
            time = follow.date.strftime("%H:%M")
            todolist.append("[%s] Table %s (%s couv.)" % (time, self.table,
                                                          self.couverts))
            todolist.append(">>> faire: %s" % follow.category.nom)
            todolist.append(" ")
            # list of products to prepare (without Menu)
            products = self.get_products_for_category(follow.category)
            todolist += self.prepare_products(products)
            follow.produits = products
            follow.save()
            self.following.add(follow)
            # save send status
            for product in products:
                product.sent = True
                product.save()
            self.update_kitchen()
            # if another category following, we send it too to inform kitchen
            if self.category_to_follow:
                todolist.append(" ")
                category = self.category_to_follow
                todolist.append("Ensuite, pour info: %s" % category)
                products = self.get_products_for_category(category)
                todolist += self.prepare_products(products)
            # we print for each printers in kitchen
            name = "kitchen-%s-%s" % (self.id, follow.category_id)
            for printer in Printer.objects.filter(kitchen=True):
                if not printer.print_list(todolist, name):
                    output = False
        return output

    def guest_couverts(self):
        """Try to find number of guests"""
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

    def set_table(self, table):
        """Change la table de la facture
        On prend en compte le changement de tarification si changement
        de zone.

        On ne traite pas le cas ou les 2 tables sont surtaxées à des montants
        différents.
        """
        self.table = table
        if self.is_surcharged() != self.surcharge:
            self.update_surcharge()

    def set_onsite(self, onsite):
        """onsite: Boolean"""
        self.onsite = onsite
        if self.is_surcharged() != self.surcharge:
            self.update_surcharge()

    def update_surcharge(self):
        self.surcharge = self.is_surcharged()
        self.update()

    def non_soldees(self):
        """ Return the list of unpaid facture
        :return: A list of Facture
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
        logger.debug("[%s] update bill" % self.id)
        self.total_ttc = Decimal("0")
        self.restant_a_payer = Decimal("0")
        for vatonbill in self.vats.iterator():
            vatonbill.total = Decimal("0")
            vatonbill.save()
        self.surcharge = self.is_surcharged()
        for sold in self.produits.iterator():
            if self.surcharge:
                if not sold.produit.price_surcharged:
                    # just in case for backwards comtability
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
            self.total_ttc += sold.prix
            vatonbill, created = self.vats.get_or_create(vat=vat)
            if created:
                logger.debug("[%s] new vat_on_bill" % self)
            vatonbill.total += value
            vatonbill.save()
            logger.debug(vatonbill)
        self.restant_a_payer = self.total_ttc
        for payment in self.paiements.iterator():
            self.restant_a_payer -= payment.montant
        self.save()

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
        """Add a payment to Facture().

        :param type_payment: TypePaiement()
        :param montant: String (will be use with Decimal())
        :param valeur_unitaire: String (will be use with Decimal())
        :return: Boolean"""
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
        Table is surtaxed if there are no Produit() in a Categorie() with
        disable_surtaxe = True
        """
        if self.onsite:
            if self.produits.filter(produit__categorie__disable_surtaxe=True
                                    ).count() > 0:
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
        """Print this bill
        """
        try:
            printer = Printer.objects.filter(billing=True)[0]
        except:
            return False
        ticket = []
        ticket.append("Le %s" % self.date_creation.strftime("%d/%m/%Y %H:%M"))
        if self.table and self.couverts:
            ticket.append("Table: %s (%s couverts)" % (self.table,
                                                       self.couverts))
        separateur = '-' * printer.width
        ticket.append(separateur)
        products = self.reduced_sold_list(self.produits.all())
        for sold in products:
            price = "% 3.2f" % sold.prix
            # la largeur disponible correspond à la largeur du ticket
            # sans la 1er partie (" 1 ") et sans la largeur du prix
            # " 1 largeur_dispo PRIX"
            largeur_dispo = printer.width - 4 - len(price)
            if len(sold.produit.nom) < largeur_dispo:
                name = sold.produit.nom
            else:
                longueur_max = largeur_dispo - 2
                name = sold.produit.nom[:longueur_max]
            padding = " " * (largeur_dispo - len(name))
            ticket.append("%dx %s%s%s" % (sold.count, name, padding, price))
        ticket.append(separateur)
        ticket.append("  Total: % 8.2f Eur." % self.total_ttc)
        for vatonbill in self.vats.iterator():
            if vatonbill.total != Decimal('0'):
                ticket.append("  TVA % 5.2f%%: % 6.2f Eur." % (
                              vatonbill.vat.tax, vatonbill.total))
        ticket.append(separateur)
        return printer.print_list(ticket, "invoice-%s" % self.id,
                                  with_header=True)

    def reduced_sold_list(self, sold_list, full=False):
        """les élèments ProduitVendu de sold_list
        sont regroupés par 'élèment identique en fonction soit:
        - du Produit() (full=False)
        - du Produit(), des options et des notes (full=True)

        On ajoute sur chaque élèment:
        - count: le nombre total
        - members: la liste des instances
        """
        sold_dict = {}
        for sold in sold_list:
            if full:
                key = sold.get_identifier()
            else:
                key = "%s" % sold.produit_id
            if key in sold_dict:
                logger.debug("[%s] increment count for this key" % key)
                sold_dict[key].count += 1
                sold_dict[key].members.append(sold)
            else:
                logger.debug("[%s] new key" % key)
                sold_dict[key] = sold
                sold_dict[key].count = 1
                sold_dict[key].members = [sold, ]
        return sorted(sold_dict.values())
