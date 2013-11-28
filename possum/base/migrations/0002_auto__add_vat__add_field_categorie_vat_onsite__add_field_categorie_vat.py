# -*- coding: utf-8 -*-
import datetime
from django.db import models

from south.db import db
from south.v2 import SchemaMigration


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'VAT'
        db.create_table(u'base_vat', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=32)),
            ('tax', self.gf('django.db.models.fields.DecimalField')(default=0, max_digits=4, decimal_places=2)),
        ))
        db.send_create_signal(u'base', ['VAT'])

        # Adding field 'Categorie.vat_onsite'
        db.add_column(u'base_categorie', 'vat_onsite',
                      self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='categorie-vat-onsite', null=True, to=orm['base.VAT']),
                      keep_default=False)

        # Adding field 'Categorie.vat_takeaway'
        db.add_column(u'base_categorie', 'vat_takeaway',
                      self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='categorie-vat-takeaway', null=True, to=orm['base.VAT']),
                      keep_default=False)


    def backwards(self, orm):
        # Deleting model 'VAT'
        db.delete_table(u'base_vat')

        # Deleting field 'Categorie.vat_onsite'
        db.delete_column(u'base_categorie', 'vat_onsite_id')

        # Deleting field 'Categorie.vat_takeaway'
        db.delete_column(u'base_categorie', 'vat_takeaway_id')


    models = {
        u'base.accompagnement': {
            'Meta': {'ordering': "['nom']", 'object_name': 'Accompagnement'},
            'couleur': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'accompagnement-couleur'", 'null': 'True', 'to': u"orm['base.Couleur']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'nom': ('django.db.models.fields.CharField', [], {'max_length': '60'})
        },
        u'base.categorie': {
            'Meta': {'ordering': "['nom']", 'object_name': 'Categorie'},
            'alcool': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'couleur': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'categorie-couleur'", 'null': 'True', 'to': u"orm['base.Couleur']"}),
            'disable_surtaxe': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'nom': ('django.db.models.fields.CharField', [], {'max_length': '60'}),
            'priorite': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'}),
            'surtaxable': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'vat_onsite': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'categorie-vat-onsite'", 'null': 'True', 'to': u"orm['base.VAT']"}),
            'vat_takeaway': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'categorie-vat-takeaway'", 'null': 'True', 'to': u"orm['base.VAT']"})
        },
        u'base.couleur': {
            'Meta': {'ordering': "['nom']", 'object_name': 'Couleur'},
            'blue': ('django.db.models.fields.PositiveIntegerField', [], {'default': '255'}),
            'green': ('django.db.models.fields.PositiveIntegerField', [], {'default': '255'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'nom': ('django.db.models.fields.CharField', [], {'max_length': '60'}),
            'red': ('django.db.models.fields.PositiveIntegerField', [], {'default': '255'})
        },
        u'base.cuisson': {
            'Meta': {'ordering': "['nom']", 'object_name': 'Cuisson'},
            'couleur': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'cuisson-couleur'", 'null': 'True', 'to': u"orm['base.Couleur']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'nom': ('django.db.models.fields.CharField', [], {'max_length': '60'}),
            'priorite': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'})
        },
        u'base.etat': {
            'Meta': {'ordering': "['nom']", 'object_name': 'Etat'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'nom': ('django.db.models.fields.CharField', [], {'max_length': '60'}),
            'priorite': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'})
        },
        u'base.facture': {
            'Meta': {'object_name': 'Facture'},
            'couverts': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'}),
            'date_creation': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'etats': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'le suivi'", 'symmetrical': 'False', 'to': u"orm['base.Suivi']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'montant_alcool': ('django.db.models.fields.DecimalField', [], {'default': '0', 'max_digits': '9', 'decimal_places': '2'}),
            'montant_normal': ('django.db.models.fields.DecimalField', [], {'default': '0', 'max_digits': '9', 'decimal_places': '2'}),
            'paiements': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'les paiements'", 'symmetrical': 'False', 'to': u"orm['base.Paiement']"}),
            'produits': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'les produits factures'", 'symmetrical': 'False', 'to': u"orm['base.ProduitVendu']"}),
            'restant_a_payer': ('django.db.models.fields.DecimalField', [], {'default': '0', 'max_digits': '9', 'decimal_places': '2'}),
            'saved_in_stats': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'table': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'facture-table'", 'null': 'True', 'to': u"orm['base.Table']"})
        },
        u'base.log': {
            'Meta': {'object_name': 'Log'},
            'date': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'type': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'log-logtype'", 'to': u"orm['base.LogType']"})
        },
        u'base.logtype': {
            'Meta': {'ordering': "['nom']", 'object_name': 'LogType'},
            'description': ('django.db.models.fields.CharField', [], {'max_length': '200', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'nom': ('django.db.models.fields.CharField', [], {'max_length': '60'})
        },
        u'base.paiement': {
            'Meta': {'object_name': 'Paiement'},
            'date': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'montant': ('django.db.models.fields.DecimalField', [], {'default': '0', 'max_digits': '9', 'decimal_places': '2'}),
            'nb_tickets': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'}),
            'type': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'paiement-type'", 'to': u"orm['base.PaiementType']"}),
            'valeur_unitaire': ('django.db.models.fields.DecimalField', [], {'default': '1', 'max_digits': '9', 'decimal_places': '2'})
        },
        u'base.paiementtype': {
            'Meta': {'ordering': "['priorite']", 'object_name': 'PaiementType'},
            'fixed_value': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'nom': ('django.db.models.fields.CharField', [], {'max_length': '60'}),
            'nom_facture': ('django.db.models.fields.CharField', [], {'max_length': '35'}),
            'priorite': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'})
        },
        u'base.produit': {
            'Meta': {'ordering': "('categorie', 'nom')", 'object_name': 'Produit'},
            'actif': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'categorie': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'produit-categorie'", 'to': u"orm['base.Categorie']"}),
            'categories_ok': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['base.Categorie']", 'symmetrical': 'False'}),
            'choix_accompagnement': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'choix_cuisson': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'choix_sauce': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'nom': ('django.db.models.fields.CharField', [], {'max_length': '60'}),
            'nom_facture': ('django.db.models.fields.CharField', [], {'max_length': '35'}),
            'prix': ('django.db.models.fields.DecimalField', [], {'default': '0', 'max_digits': '7', 'decimal_places': '2'}),
            'produits_ok': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'produits_ok_rel_+'", 'to': u"orm['base.Produit']"})
        },
        u'base.produitvendu': {
            'Meta': {'ordering': "('produit',)", 'object_name': 'ProduitVendu'},
            'accompagnement': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'produitvendu-accompagnement'", 'null': 'True', 'to': u"orm['base.Accompagnement']"}),
            'contient': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'contient_rel_+'", 'to': u"orm['base.ProduitVendu']"}),
            'cuisson': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'produitvendu-cuisson'", 'null': 'True', 'to': u"orm['base.Cuisson']"}),
            'date': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'prix': ('django.db.models.fields.DecimalField', [], {'default': '0', 'max_digits': '7', 'decimal_places': '2'}),
            'produit': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'produitvendu-produit'", 'to': u"orm['base.Produit']"}),
            'sauce': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'produitvendu-sauce'", 'null': 'True', 'to': u"orm['base.Sauce']"})
        },
        u'base.sauce': {
            'Meta': {'ordering': "['nom']", 'object_name': 'Sauce'},
            'couleur': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'sauce-couleur'", 'null': 'True', 'to': u"orm['base.Couleur']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'nom': ('django.db.models.fields.CharField', [], {'max_length': '60'})
        },
        u'base.statsjourcategorie': {
            'Meta': {'object_name': 'StatsJourCategorie'},
            'categorie': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'statsjour-categorie'", 'null': 'True', 'to': u"orm['base.Categorie']"}),
            'date': ('django.db.models.fields.DateField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'nb': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'}),
            'valeur': ('django.db.models.fields.DecimalField', [], {'default': '0', 'max_digits': '9', 'decimal_places': '2'})
        },
        u'base.statsjourgeneral': {
            'Meta': {'object_name': 'StatsJourGeneral'},
            'date': ('django.db.models.fields.DateField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'type': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'statsjour-logtype'", 'null': 'True', 'to': u"orm['base.LogType']"}),
            'valeur': ('django.db.models.fields.DecimalField', [], {'default': '0', 'max_digits': '9', 'decimal_places': '2'})
        },
        u'base.statsjourpaiement': {
            'Meta': {'object_name': 'StatsJourPaiement'},
            'date': ('django.db.models.fields.DateField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'nb': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'}),
            'paiement': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'statsjour-paiement'", 'null': 'True', 'to': u"orm['base.PaiementType']"}),
            'valeur': ('django.db.models.fields.DecimalField', [], {'default': '0', 'max_digits': '9', 'decimal_places': '2'})
        },
        u'base.statsjourproduit': {
            'Meta': {'object_name': 'StatsJourProduit'},
            'date': ('django.db.models.fields.DateField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'nb': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'}),
            'produit': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'statsjour-produit'", 'null': 'True', 'to': u"orm['base.Produit']"}),
            'valeur': ('django.db.models.fields.DecimalField', [], {'default': '0', 'max_digits': '9', 'decimal_places': '2'})
        },
        u'base.suivi': {
            'Meta': {'object_name': 'Suivi'},
            'date': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'etat': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'suivi-etat'", 'to': u"orm['base.Etat']"}),
            'facture': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'suivi-facture'", 'to': u"orm['base.Facture']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        u'base.table': {
            'Meta': {'ordering': "['nom']", 'object_name': 'Table'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'nom': ('django.db.models.fields.CharField', [], {'max_length': '60'}),
            'zone': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'table-zone'", 'to': u"orm['base.Zone']"})
        },
        u'base.vat': {
            'Meta': {'ordering': "['name']", 'object_name': 'VAT'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '32'}),
            'tax': ('django.db.models.fields.DecimalField', [], {'default': '0', 'max_digits': '4', 'decimal_places': '2'})
        },
        u'base.zone': {
            'Meta': {'ordering': "['nom']", 'object_name': 'Zone'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'nom': ('django.db.models.fields.CharField', [], {'max_length': '60'}),
            'prix_surtaxe': ('django.db.models.fields.DecimalField', [], {'default': '0', 'max_digits': '4', 'decimal_places': '2'}),
            'surtaxe': ('django.db.models.fields.BooleanField', [], {'default': 'False'})
        }
    }

    complete_apps = ['base']
