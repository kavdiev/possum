# -*- coding: utf-8 -*-
#
#    Copyright 2009-2013 Sébastien Bonnegent
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
import datetime
from decimal import Decimal
from django.db.models import Sum
from possum.base.payment import Paiement
from possum.base.payment import PaiementType
from django.contrib.auth.models import User
import os
from possum.base.stats import StatsJourGeneral, StatsJourPaiement, \
        StatsJourProduit, StatsJourCategorie, get_working_day
from possum.base.category import Categorie
from possum.base.printer import Printer
from possum.base.log import LogType
from django.contrib.auth import authenticate


def remplissage(nb,  caractere,  largeur):
    """caractere est le caractere de remplissage"""
    milieu = caractere
    # on ajoute len(milieu) a nb
    nb += 1
    while nb < largeur:
        milieu += caractere
        nb += 1
    return milieu


class Suivi(models.Model):
    """Suivi des envois en cuisine:
    category est la categorie envoyée en cuisine"""
    facture = models.ForeignKey('base.Facture', related_name="suivi-facture")
    category = models.ForeignKey('Categorie', related_name="suivi-category")
    date = models.DateTimeField('depuis le', auto_now_add=True)

    def __unicode__(self):
        if self.facture.table:
            table = self.facture.table
        else:
            table = "T??"
        return "[%s] Table %s > %s" % (self.date.strftime("%H:%M"), table, self.category.nom)

class Facture(models.Model):
    date_creation = models.DateTimeField('creer le', auto_now_add=True)
    table = models.ForeignKey('Table', \
            null=True, blank=True, \
            related_name="facture-table")
    couverts = models.PositiveIntegerField("nombre de couverts", default=0)
    produits = models.ManyToManyField('ProduitVendu', \
        related_name="les produits vendus", \
        limit_choices_to = {'date__gt': datetime.datetime.today()})
    total_ttc = models.DecimalField(max_digits=9, decimal_places=2, 
            default=0)
    paiements = models.ManyToManyField('Paiement',
        related_name="les paiements",
        limit_choices_to = {'date__gt': datetime.datetime.today()})
    vats = models.ManyToManyField('VATOnBill',
        related_name="vat total for each vat on a bill")
    restant_a_payer = models.DecimalField(max_digits=9, decimal_places=2, 
            default=0)
    saved_in_stats = models.BooleanField(default=False)
    onsite = models.BooleanField(default=True)

    class Meta:
        get_latest_by = 'id'
        permissions = (
            ("p1", "can modify users and permissions"),
            ("p2", "can play games"),
            ("p3", "can view all bills"),
            ("p4", "can modify all bills"),
            ("p5", "can use POS"),
            ("p6", "can modify la carte"),
            ("p7", "can view results"),
            ("p8", "can change music"),
            ("p9", "can modify music"),
        )

    def __unicode__(self):
        if self.id:
            id = self.id
        else:
            id = 0
        if self.date_creation:
#            print self.date_creation
#            date = self.date_creation.strftime("%Y/%m/%d %H:%M")
            date = self.date_creation.strftime("%H:%M %d/%m")
        else:
            date = "--:-- --/--"
        return u"%s F%06d" % (date, id)

    def __cmp__(self, other):
        """
            Les factures sont triees par date_creation.
            D'abord les plus récentes, puis les plus vielles.
        """
        return cmp(self.date_creation, other.date_creation)

    def something_for_the_kitchen(self):
        """Return, if one, the first category to prepare in the
        kitchen. Example: Entree if there are Entree and Plat.
        """
        todolist = [p.made_with for p in self.produits.filter( \
                produit__categorie__made_in_kitchen=True, 
                sent=False)]
        # le cas des menus
        menu = [p.made_with for p in self.produits.filter( \
                contient__produit__categorie__made_in_kitchen=True, 
                sent=False)]
        if menu:
            todolist += menu
        if todolist:
            todolist.sort()
            return todolist[0]
        else:
            return None

    def get_first_todolist_for_kitchen(self):
        """Prepare la liste des produits a envoyer en cuisine
        """
        categories = []
        products = {}
        for product in self.produits.filter(sent=False):
            if product.est_un_menu():
                for subproduct in product.contient.all():
                    # cas des menus
                    if subproduct.made_with not in categories:
                        categories.append(subproduct.made_with)
                    if subproduct.made_with.id not in products:
                        products[subproduct.made_with.id] = []
                    name = subproduct.produit.nom
                    if subproduct.produit.choix_cuisson:
                        name += ": %s" % subproduct.cuisson
                    products[subproduct.made_with.id].append(name)
            else:
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

    def send_in_the_kitchen(self):
        """We send the first category available to the kitchen.
        """
        category = self.something_for_the_kitchen()
        if category:
            todolist = []
            if self.produits.filter(sent=True).count() == 0:
                # on crée le ticket avec la liste des produits et 
                # des suites
                first = True
            else:
                # on indique seulement qu'il faut la suite de la table
                first = False
            heure = datetime.datetime.now().strftime("%H:%M")
            if first:
                todolist.append("> Table %s : envoye %s (%s)" % (self.table, category.nom, heure))
                products = self.get_first_todolist_for_kitchen()
                if products:
                    todolist += products
            else:
                todolist.append("> Table %s : envoye %s (%s)" % (self.table, category.nom, heure))
            # les produits standards
            for product in self.produits.filter(made_with=category, sent=False):
                product.sent = True
                product.save()
            # les menus
            for product in self.produits.filter(contient__made_with=category, sent=False):
                product.sent = True
                product.save()
            for printer in Printer.objects.filter(kitchen=True):
                result = printer.print_list(todolist, "kitchen-%s-%s" % (self.id, category.id))
            suivi = Suivi(category=category, facture=self)
            suivi.save()
            return result

    def guest_couverts(self):
        """Essaye de deviner le nombre de couverts"""
        nb = {}
        categories = ["Entrees", "Plats"]
        for categorie in categories:
            nb[categorie] = 0
        for vendu in self.produits.iterator():
            if vendu.produit.categorie.nom in categories:
                nb[vendu.produit.categorie.nom] += 1
            for sous_produit in vendu.contient.iterator():
                if sous_produit.produit.categorie.nom in categories:
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
        if self.est_surtaxe():
            if not table.zone.surtaxe:
                # la nouvelle table n'est pas surtaxée
                self.remove_surtaxe()
            self.table = table
            self.save()
        else:
            self.table = table
            self.save()
            if table.zone.surtaxe:
                # la nouvelle table est surtaxée
                self.add_surtaxe()

    def nb_soldee_jour(self, date):
        """Nombre de facture soldee le jour 'date'"""
        if date.hour > 5:
            date_min = datetime.datetime(date.year, date.month, date.day, 5)
        else:
            tmp = date - datetime.timedelta(days=1)
            date_min = datetime.datetime(tmp.year, tmp.month, tmp.day, 5)
        tmp = date_min + datetime.timedelta(days=1)
        date_max = datetime.datetime(tmp.year, tmp.month, tmp.day, 5)
        return Facture.objects.filter(date_creation__gt=date_min, \
                                        date_creation__lt=date_max, \
                                        restant_a_payer=0).exclude( \
                                        produits__isnull=True).count()

    def non_soldees(self):
        """Retourne la liste des factures non soldees"""
        liste = []
        for i in Facture.objects.exclude(restant_a_payer=0).iterator():
            liste.append(i)
        for i in Facture.objects.filter(produits__isnull=True).iterator():
            liste.append(i)
        return liste

    def compute_total(self):
        self.total_ttc = Decimal("0")
        self.restant_a_payer = Decimal("0")
        for v in self.vats.all():
            v.total = 0
            v.save()
        for product in self.produits.all():
            self.add_product_prize(product)
        for payment in self.paiements.all():
            self.restant_a_payer -= payment.montant
        self.save()

    def add_product_prize(self, product):
        """Ajoute le prix d'un ProduitVendu sur la facture."""
        ttc = product.produit.prix
        self.total_ttc += ttc
        self.restant_a_payer += ttc
        self.save()
        if self.onsite:
            vat = product.produit.categorie.vat_onsite
            value = product.produit.vat_onsite
        else:
            vat = product.produit.categorie.vat_takeaway
            value = product.produit.vat_takeaway
        vatonbill, created = self.vats.get_or_create(vat=vat)
        vatonbill.total += value
        vatonbill.save()

    def del_product_prize(self, product):
        ttc = product.produit.prix
        self.total_ttc -= ttc
        self.restant_a_payer -= ttc
        self.save()
        if self.onsite:
            vat = product.produit.categorie.vat_onsite
            value = product.produit.vat_onsite
        else:
            vat = product.produit.categorie.vat_takeaway
            value = product.produit.vat_takeaway
        vatonbill, created = self.vats.get_or_create(vat=vat)
        vatonbill.total -= value
        vatonbill.save()

    def add_surtaxe(self):
        """Add surtaxe on all needed products
        """
        for product in self.produits.filter(produit__categorie__surtaxable=True):
            product.prix += self.table.zone.prix_surtaxe
            product.save()
        self.compute_total()

    def remove_surtaxe(self):
        """Remove surtaxe on all needed products
        """
        for product in self.produits.filter(produit__categorie__surtaxable=True):
            product.prix -= self.table.zone.prix_surtaxe
            product.save()
        self.compute_total()

    def add_product(self, vendu):
        """Ajout d'un produit à la facture.
        Si c'est le premier produit alors on modifie la date de creation
        """
        if self.produits.count() == 0:
            self.date_creation = datetime.datetime.now()

        vendu.prix = vendu.produit.prix
        vendu.made_with = vendu.produit.categorie
        vendu.save()
        if vendu.prix:
            self.produits.add(vendu)
            self.save()
            if self.est_surtaxe():
                if vendu.produit.categorie.disable_surtaxe:
                    # on doit enlever la surtaxe pour tous les produits
                    # concernés
                    self.remove_surtaxe()
                else:
                    if vendu.produit.categorie.surtaxable:
                        vendu.prix += self.table.zone.prix_surtaxe
                        vendu.save()
                    self.add_product_prize(vendu)
            else:
                self.add_product_prize(vendu)

#        else:
#            # on a certainement a faire a une reduction
#            # -10%
#            if vendu.produit.nom == "Remise -10%":
#                vendu.prix = self.get_montant() / Decimal("-10")
#                vendu.save()
#                logging.debug("la remise est de: %s" % vendu.prix)
#                self.produits.add(vendu)
#                self.restant_a_payer += vendu.prix
#                self.montant_normal += vendu.prix
#            else:
#                logging.debug("cette remise n'est pas connue")
        #self.produits.order_by('produit')
#        self.save()

    def del_product(self, product):
        """On enleve un produit à la facture.

        Si le montant est négatif après le retrait d'un élèment,
        c'est qu'il reste certainement une remise, dans
        ce cas on enlève tous les produits.
        """
        if product in self.produits.all():
            surtaxe = self.est_surtaxe()
            self.produits.remove(product)
            if surtaxe != self.est_surtaxe():
                self.compute_total()
            else:
                self.del_product_prize(product)
        else:
            logging.warning("[%s] on essaye de supprimer un produit "\
                            "qui n'est pas dans la facture" % self)

    def del_all_payments(self):
        """On supprime tous les paiements"""
        if self.paiements.count():
            for paiement in self.paiements.iterator():
                paiement.delete()
            self.paiements.clear()
            self.restant_a_payer = self.total_ttc
            self.save()

    def del_payment(self, payment):
        """On supprime un paiement"""
        if payment in self.paiements.all():
            self.paiements.remove(payment)
            payment.delete()
            self.save()
            self.compute_total()
        else:
            logging.warning("[%s] on essaye de supprimer un paiement "\
                            "qui n'est pas dans la facture: %s %s %s %s"\
                            % (self, payment.id, payment.date,\
                            payment.type.nom, payment.montant))

    def get_users(self):
        """Donne la liste des noms d'utilisateurs"""
        users = []
        for user in User.objects.order_by('username').iterator():
            if user.is_active:
                users.append(user.username)
        return users

    def get_last_connected(self):
        try:
            return User.objects.order_by('last_login')[0].username
        except:
            return "aucun utilisateur"

    def authenticate(self, username, password):
        user = authenticate(username=username, password=password)
        if user is not None:
            if user.groups.filter(name='Managers').count() == 1:
                return True
            else:
                logging.debug("utilisateur non authorise: %s" % username)
                return False
        else:
            logging.debug("erreur avec: %s / %s" % (username, password))
            return False

    def getTvaNormal(self):
        """
            calcul la TVA
            On arrondi seulement à 1 parce que les 2 décimals sont dans la partie entière du montant
            # la TVA est sur le HT !!
        """
        #return self.montant_normal - ((self.montant_normal*100)/Decimal("105.5"))
        return self.montant_normal * (Decimal("0.055") / Decimal("1.055"))

    def getTvaAlcool(self):
        #return self.montant_alcool - ((self.montant_alcool*100)/Decimal("119.6"))
        return self.montant_alcool * (Decimal("0.196") / Decimal("1.196"))

    def get_resume(self):
        return "%s %s %d" % (self.table.nom, self.date_creation, self.montant)

    def get_montant(self):
        return self.montant_normal + self.montant_alcool

    def add_payment(self, type_payment, montant, valeur_unitaire="1.0"):
        """
        type_payment est un TypePaiement
        montant et valeur_unitaire sont des chaines de caracteres
        qui seront converti en Decimal

        Si le montant est superieur au restant du alors on rembourse en
        espece.
        """
        logging.debug("Nouveau paiement")
        if self.restant_a_payer <= Decimal("0"):
            logging.info("[%s] nouveau paiement ignore car restant"\
                            " a payer <= 0 (%5.2f)"
                            % (self, self.restant_a_payer))
            return False

        paiement = Paiement()
        paiement.type = type_payment
        paiement.valeur_unitaire = Decimal(valeur_unitaire)
        if self.produits:
            # le montant est-il indique ?
            if float(montant) == 0.0:
                return False
            else:
                # le montant est indique
                if type_payment.fixed_value:
                    # dans ce cas le montant est le nombre de ticket
                    paiement.nb_tickets = int(montant)
                    paiement.montant = paiement.nb_tickets * paiement.valeur_unitaire
                else:
                    paiement.montant = Decimal(montant)
                # on enregistre ce paiement
                paiement.save()
                self.paiements.add(paiement)
            # regularisation si le montant est superieur au montant du
            if paiement.montant > self.restant_a_payer:
                monnaie = Paiement()
                monnaie.type = PaiementType.objects.get(nom="Espece")
                monnaie.montant = self.restant_a_payer - paiement.montant
                monnaie.save()
                self.paiements.add(monnaie)
                self.restant_a_payer -= monnaie.montant
            self.restant_a_payer -= paiement.montant
            self.save()
            # if needed, update stats
            self.update_stats()
            return True
        else:
            logging.debug("pas de produit, donc rien n'a payer")
            return False

    def est_soldee(self):
        """La facture a été utilisée et soldée"""
        if self.restant_a_payer == 0 and self.produits.count() > 0:
            return True
        else:
            return False

    def est_un_repas(self):
        """Est ce que la facture contient un element qui est
        fabriqué en cuisine
        """
        for vendu in self.produits.iterator():
            if vendu.produit.categorie.made_in_kitchen:
                return True
            if vendu.contient.filter(produit__categorie__made_in_kitchen=True).count():
                return True
        return False

    def is_empty(self):
        """La facture est vierge"""
        if self.restant_a_payer == 0 and self.produits.count() == 0:
            return True
        else:
            return False

    def est_surtaxe(self):
        """
        Table is surtaxed et il n'y a pas de nourriture.
        """
        if self.onsite:
            for produit in self.produits.all():
                #logging.debug("test with produit: %s and categorie id: %d" % (produit.nom, produit.categorie.id))
                if produit.produit.categorie.disable_surtaxe:
                    #logging.debug("pas de surtaxe")
                    return False
            if self.table:
                return self.table.est_surtaxe()
            else:
                return False
        else:
            return False

    def rapport_mois(self, mois):
        """Retourne dans une liste le rapport du mois 'mois'
        'mois' est de type datetime.today()

        exemple:

        -- CA mensuel 12/2010 --
        Cheque               285,05
        Ticket Resto         723,67
        Espece              3876,46
        ANCV                 150,00
        CB                  3355,60
        total TTC:          8386,08
        montant TVA  5,5:    353,26
        montant TVA 19,6:    263,82

        """
        logging.debug(mois)
        date_min = datetime.datetime(mois.year, mois.month, 1, 5)
        # on est le mois suivant (32 c'est pour etre sur de ne pas
        # tomber sur le 31 du mois)
        tmp = date_min + datetime.timedelta(days=32)
        # modulo pour le cas de decembre + 1 = janvier
        date_max = datetime.datetime(tmp.year, tmp.month, 1, 5)
        texte = []
        texte.append("    -- CA mensuel %s --" % mois.strftime("%m/%Y"))
        selection = StatsJourPaiement.objects.filter( \
                            date__gte=date_min, \
                            date__lt=date_max)
        for paiement in PaiementType.objects.iterator():
            total = selection.filter(paiement=paiement).aggregate(Sum('valeur'))['valeur__sum']
            if total > 0:
                texte.append("%-20s %10.2f" % (paiement.nom, total))
        selection = StatsJourGeneral.objects.filter( \
                            date__gte=date_min, \
                            date__lt=date_max)
        ca = selection.filter(type=LogType.objects.get(nom="ca")).aggregate(Sum('valeur'))['valeur__sum']
        if ca == None:
            ca = 0.0

        # IMPORTANT:
        #   ici on ne se sert pas des stats 'tva_normal' et 'tva_alcool'
        #   car il y a des erreurs d'arrondies à cause des additions
        #   successives
        montant_normal = selection.filter(type=LogType.objects.get(nom="montant_normal")).aggregate(Sum('valeur'))['valeur__sum']
        if montant_normal == None:
            tva_normal = 0.0
        else:
            tva_normal = montant_normal*(Decimal("0.055") / Decimal("1.055"))
        montant_alcool = selection.filter(type=LogType.objects.get(nom="montant_alcool")).aggregate(Sum('valeur'))['valeur__sum']
        if montant_alcool == None:
            tva_alcool = 0.0
        else:
            tva_alcool = montant_alcool*(Decimal("0.196") / Decimal("1.196"))

        texte.append("%-20s %10.2f" % ("total TTC:", ca))
        texte.append("%-20s %10.2f" % ("total TVA  5.5:", tva_normal))
        texte.append("%-20s %10.2f" % ("total TVA 19.6:", tva_alcool))
        return texte

    def get_factures_du_jour(self, date):
        """Retourne la liste des factures soldees du jour 'date'"""
        date_min = datetime.datetime(date.year, date.month, date.day, 5)
        tmp = date_min + datetime.timedelta(days=1)
        date_max = datetime.datetime(tmp.year, tmp.month, tmp.day, 5)
        return Facture.objects.filter( \
                                      date_creation__gt=date_min, \
                                      date_creation__lt=date_max, \
                                      restant_a_payer = 0).exclude(\
                                      produits__isnull = True)

    def rapport_jour(self, date):
        """Retourne le rapport du jour sous la forme d'une liste
        'jour' est de type datetime.today()

        exemple:
        -- 15/12/2010 --
        Cheque               285,05
        Ticket Resto         723,67
        Espece              3876,46
        ANCV                 150,00
        CB                  3355,60
        total TTC:          8386,08
        montant TVA  5,5:    353,26
        montant TVA 19,6:    263,82

        Menu E/P :            16
        Menu P/D :            16
        Menu Tradition :      16

        Salade cesar :         6
        ...

        plat ...
        """
        logging.debug(date)
        texte = []
        if date == None:
            logging.warning("la date fournie est inconnue")
            return texte
        stats = StatsJourGeneral()
        texte.append("       -- %s --" % date.strftime("%d/%m/%Y"))
        texte.append("CA TTC (% 4d fact.): %11.2f" % (
                                    stats.get_data("nb_factures", date),
                                    stats.get_data("ca", date)))
        # IMPORTANT:
        #   ici on ne se sert pas des stats 'tva_normal' et 'tva_alcool'
        #   car il y a des erreurs d'arrondies à cause des additions
        #   successives
        tva_normal = stats.get_data("montant_normal", date)*(Decimal("0.055") / Decimal("1.055"))
        texte.append("%-20s %11.2f" % ("total TVA  5.5:", tva_normal))
        tva_alcool = stats.get_data("montant_alcool", date)*(Decimal("0.196") / Decimal("1.196"))
        texte.append("%-20s %11.2f" % ("total TVA 19.6:", tva_alcool))
        for stats in StatsJourPaiement.objects.filter(date=date)\
                                              .order_by("paiement")\
                                              .iterator():
            texte.append("%-15s (%d) %11.2f" % (stats.paiement.nom,
                                                stats.nb,
                                                stats.valeur))
        texte.append(" ")
        for cate in ["Formules", "Entrees", "Plats", "Desserts"]:
            try:
                categorie = Categorie.objects.get(nom=cate)
                stats = StatsJourCategorie.objects.get(date=date,
                                                    categorie=categorie)
                texte.append("%-21s %10d" % (cate, stats.nb))
                for stats in StatsJourProduit.objects.filter(date=date, produit__categorie=categorie).order_by("produit").iterator():
                    texte.append(" %-20s %10d" % (stats.produit.nom, stats.nb))
                texte.append(" ")
            except StatsJourCategorie.DoesNotExist:
                continue
        return texte

    def update_common_stats(self, date):
        """Update common stats
        nb_invoices : number of invoices
        total_ttc   : total
        ID_vat_only : VAT part only for each vat
        """
        logtype, created = LogType.objects.get_or_create(nom="nb_invoices")
        if created:
            logtype.save()
        stat = StatsJourGeneral.objects.get_or_create(date=date, type=logtype)[0]
        stat.valeur += 1
        stat.save()
        logtype, created = LogType.objects.get_or_create(nom="total_ttc")
        if created:
            logtype.save()
        stat = StatsJourGeneral.objects.get_or_create(date=date, type=logtype)[0]
        stat.valeur += self.total_ttc
        stat.save()
        for vatonbill in self.vats.all():
            logtype, created = LogType.objects.get_or_create(nom="%s_vat_only" % vatonbill.vat.id)
            if created:
                logtype.save()
            stat = StatsJourGeneral.objects.get_or_create(date=date, type=logtype)[0]
            stat.valeur += vatonbill.total
            stat.save()
            
    def update_products_stats(self, date):
        """Update stats on products, for each:
        nb     : how many
        valeur : total TTC
        """
        for vendu in self.produits.iterator():
            # produit
            stat = StatsJourProduit.objects.get_or_create(date=date, produit=vendu.produit)[0]
            stat.valeur += vendu.prix
            stat.nb += 1
            stat.save()
            for sous_vendu in vendu.contient.iterator():
                # il n'y a pas de CA donc on ne le compte pas
                stat = StatsJourProduit.objects.get_or_create(date=date, produit=sous_vendu.produit)[0]
                stat.nb += 1
                stat.save()
                # categorie
                stat = StatsJourCategorie.objects.get_or_create(date=date, categorie=sous_vendu.produit.categorie)[0]
                stat.nb += 1
                stat.save()
            # categorie
            stat = StatsJourCategorie.objects.get_or_create(date=date, categorie=vendu.produit.categorie)[0]
            stat.valeur += vendu.prix
            stat.nb += 1
            stat.save()

    def update_guests_stats(self, date):
        """Update stats on guests, for each:
        nb_guests        : how many people
        guest_average    : average TTC by guest
        guests_total_ttc : total TTC for guests
        """
        logtype, created = LogType.objects.get_or_create(nom="nb_guests")
        if created:
            logtype.save()
        stat = StatsJourGeneral.objects.get_or_create(date=date, type=logtype)[0]
        if self.couverts == 0:
            # if not, we try to find a number
            self.couverts = self.guest_couverts()
            self.save()
        stat.valeur += self.couverts
        stat.save()
        nb_guests = stat.valeur
        logtype, created = LogType.objects.get_or_create(nom="guests_total_ttc")
        if created:
            logtype.save()
        stat = StatsJourGeneral.objects.get_or_create(date=date, type=logtype)[0]
        stat.valeur += self.total_ttc
        stat.save()
        total_ttc = stat.valeur
        logtype, created = LogType.objects.get_or_create(nom="guest_average")
        if created:
            logtype.save()
        stat = StatsJourGeneral.objects.get_or_create(date=date, type=logtype)[0]
        if nb_guests:
            stat.valeur = total_ttc / nb_guests
        else:
            stat.valeur = 0
        stat.save()

    def update_bar_stats(self, date):
        """Update stats on bar, for each:
        nb_bar        : how many invoices
        bar_average   : average TTC by invoice
        bar_total_ttc : total TTC for bar activity
        """
        logtype, created = LogType.objects.get_or_create(nom="nb_bar")
        if created:
            logtype.save()
        stat = StatsJourGeneral.objects.get_or_create(date=date, type=logtype)[0]
        stat.valeur += 1
        stat.save()
        nb_bar = stat.valeur
        logtype, created = LogType.objects.get_or_create(nom="bar_total_ttc")
        if created:
            logtype.save()
        stat = StatsJourGeneral.objects.get_or_create(date=date, type=logtype)[0]
        stat.valeur += self.total_ttc
        stat.save()
        total_ttc = stat.valeur
        logtype, created = LogType.objects.get_or_create(nom="bar_average")
        if created:
            logtype.save()
        stat = StatsJourGeneral.objects.get_or_create(date=date, type=logtype)[0]
        if nb_bar:
            stat.valeur = total_ttc / nb_bar
        else:
            stat.valeur = 0
        stat.save()

    def update_payments_stats(self, date):
        for paiement in self.paiements.iterator():
            stat = StatsJourPaiement.objects.get_or_create(date=date, paiement=paiement.type)[0]
            stat.valeur += paiement.montant
            if paiement.nb_tickets > 0:
                stat.nb += paiement.nb_tickets
            else:
                stat.nb += 1
            stat.save()

    def update_stats(self):
        """Calcule les statistiques pour cette facture
        si elle est soldée"""
        if self.est_soldee():
            date = get_working_day(self.date_creation)
            self.update_common_stats(date)
            self.update_products_stats(date)
            if self.est_un_repas():
                self.update_guests_stats(date)
            else:
                self.update_bar_stats(date)
            self.update_payments_stats(date)
            self.saved_in_stats = True
            self.save()

    def print_ticket(self):
        try:
            printer = Printer.objects.filter(billing=True)[0]
        except:
            return False
        ticket = []
        ticket.append("Le %s" % self.date_creation.strftime("%d/%m/%Y %H:%M"))
        separateur = '-' * printer.width
        ticket.append(separateur)
        for vendu in self.produits.order_by( \
                            "produit__categorie__priorite").iterator():
            name = vendu.produit.nom_facture[:25]
            prize = "% 3.2f" % vendu.produit.prix
            # la largeur disponible correspond à la largeur du ticket
            # sans la 1er partie (" 1 ") et sans la largeur du prix
            # " 1 largeur_dispo PRIX"
            largeur_dispo = printer.width - 3 - len(prize)
            if len(vendu.produit.nom_facture) < largeur_dispo:
                name = vendu.produit.nom_facture
            else:
                longueur_max = largeur_dispo - 2
                name = vendu.produit.nom_facture[:longueur_max]
            remplissage = " " * (largeur_dispo - len(name))
            ticket.append(" 1 %s%s%s" % (name, remplissage, prize))
        ticket.append(separateur)
        ticket.append("  Total: % 8.2f Eur." % self.total_ttc)
        for vatonbill in self.vats.all():
            ticket.append("  TVA % 5.2f%%: % 6.2f Eur." % (\
                    vatonbill.vat.tax, vatonbill.total))
        ticket.append(separateur)
        return printer.print_list(ticket, "invoice-%s" % self.id, with_header=True)

