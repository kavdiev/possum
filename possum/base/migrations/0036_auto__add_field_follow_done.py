# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding field 'Follow.done'
        db.add_column(u'base_follow', 'done',
                      self.gf('django.db.models.fields.BooleanField')(default=False),
                      keep_default=False)


    def backwards(self, orm):
        # Deleting field 'Follow.done'
        db.delete_column(u'base_follow', 'done')


    models = {
        'base.categorie': {
            'Meta': {'ordering': "['priorite']", 'object_name': 'Categorie'},
            'color': ('django.db.models.fields.CharField', [], {'default': "'#ffdd82'", 'max_length': '8'}),
            'disable_surtaxe': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'made_in_kitchen': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'nom': ('django.db.models.fields.CharField', [], {'max_length': '60'}),
            'priorite': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'}),
            'surtaxable': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'vat_onsite': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'categorie-vat-onsite'", 'null': 'True', 'to': "orm['base.VAT']"}),
            'vat_takeaway': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'categorie-vat-takeaway'", 'null': 'True', 'to': "orm['base.VAT']"})
        },
        'base.config': {
            'Meta': {'ordering': "['key']", 'object_name': 'Config'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'key': ('django.db.models.fields.CharField', [], {'max_length': '32'}),
            'value': ('django.db.models.fields.CharField', [], {'max_length': '64'})
        },
        'base.cuisson': {
            'Meta': {'object_name': 'Cuisson'},
            'color': ('django.db.models.fields.CharField', [], {'default': "'#ffdd82'", 'max_length': '8'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'nom': ('django.db.models.fields.CharField', [], {'max_length': '60'}),
            'nom_facture': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '35'}),
            'priorite': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'})
        },
        'base.dailystat': {
            'Meta': {'object_name': 'DailyStat'},
            'date': ('django.db.models.fields.DateField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'key': ('django.db.models.fields.CharField', [], {'max_length': '32'}),
            'value': ('django.db.models.fields.DecimalField', [], {'default': '0', 'max_digits': '9', 'decimal_places': '2'})
        },
        'base.facture': {
            'Meta': {'object_name': 'Facture'},
            'category_to_follow': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['base.Categorie']", 'null': 'True', 'blank': 'True'}),
            'couverts': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'}),
            'date_creation': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'following': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': "orm['base.Follow']", 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'onsite': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'paiements': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'les paiements'", 'symmetrical': 'False', 'to': "orm['base.Paiement']"}),
            'produits': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'les produits vendus'", 'symmetrical': 'False', 'to': "orm['base.ProduitVendu']"}),
            'restant_a_payer': ('django.db.models.fields.DecimalField', [], {'default': '0', 'max_digits': '9', 'decimal_places': '2'}),
            'saved_in_stats': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'surcharge': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'table': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'facture-table'", 'null': 'True', 'to': "orm['base.Table']"}),
            'total_ttc': ('django.db.models.fields.DecimalField', [], {'default': '0', 'max_digits': '9', 'decimal_places': '2'}),
            'vats': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'vat total for each vat on a bill'", 'symmetrical': 'False', 'to': "orm['base.VATOnBill']"})
        },
        'base.follow': {
            'Meta': {'ordering': "['date']", 'object_name': 'Follow'},
            'category': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['base.Categorie']"}),
            'date': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'done': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'produits': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'les produits envoyes'", 'symmetrical': 'False', 'to': "orm['base.ProduitVendu']"})
        },
        'base.monthlystat': {
            'Meta': {'ordering': "['year', 'month']", 'object_name': 'MonthlyStat'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'key': ('django.db.models.fields.CharField', [], {'max_length': '32'}),
            'month': ('django.db.models.fields.PositiveSmallIntegerField', [], {}),
            'value': ('django.db.models.fields.DecimalField', [], {'default': '0', 'max_digits': '9', 'decimal_places': '2'}),
            'year': ('django.db.models.fields.PositiveSmallIntegerField', [], {})
        },
        'base.note': {
            'Meta': {'ordering': "['message']", 'object_name': 'Note'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'message': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '35'})
        },
        'base.option': {
            'Meta': {'ordering': "['name']", 'object_name': 'Option'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '16'})
        },
        'base.paiement': {
            'Meta': {'object_name': 'Paiement'},
            'date': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'montant': ('django.db.models.fields.DecimalField', [], {'default': '0', 'max_digits': '9', 'decimal_places': '2'}),
            'nb_tickets': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'}),
            'type': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'paiement-type'", 'to': "orm['base.PaiementType']"}),
            'valeur_unitaire': ('django.db.models.fields.DecimalField', [], {'default': '1', 'max_digits': '9', 'decimal_places': '2'})
        },
        'base.paiementtype': {
            'Meta': {'ordering': "['nom']", 'object_name': 'PaiementType'},
            'fixed_value': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'nom': ('django.db.models.fields.CharField', [], {'max_length': '60'})
        },
        'base.printer': {
            'Meta': {'object_name': 'Printer'},
            'billing': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'footer': ('django.db.models.fields.TextField', [], {'default': "''"}),
            'header': ('django.db.models.fields.TextField', [], {'default': "''"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'kitchen': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'manager': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '40'}),
            'options': ('django.db.models.fields.CharField', [], {'max_length': '120'}),
            'width': ('django.db.models.fields.PositiveIntegerField', [], {'default': '27'})
        },
        'base.produit': {
            'Meta': {'ordering': "['categorie', 'nom']", 'object_name': 'Produit'},
            'actif': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'categorie': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'produit-categorie'", 'to': "orm['base.Categorie']"}),
            'categories_ok': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['base.Categorie']", 'symmetrical': 'False'}),
            'choix_cuisson': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'nom': ('django.db.models.fields.CharField', [], {'max_length': '60'}),
            'options_ok': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': "orm['base.Option']", 'null': 'True', 'blank': 'True'}),
            'price_surcharged': ('django.db.models.fields.DecimalField', [], {'default': '0', 'max_digits': '7', 'decimal_places': '2'}),
            'prix': ('django.db.models.fields.DecimalField', [], {'default': '0', 'max_digits': '7', 'decimal_places': '2'}),
            'produits_ok': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'produits_ok_rel_+'", 'to': "orm['base.Produit']"}),
            'vat_onsite': ('django.db.models.fields.DecimalField', [], {'default': '0', 'max_digits': '7', 'decimal_places': '2'}),
            'vat_surcharged': ('django.db.models.fields.DecimalField', [], {'default': '0', 'max_digits': '7', 'decimal_places': '2'}),
            'vat_takeaway': ('django.db.models.fields.DecimalField', [], {'default': '0', 'max_digits': '7', 'decimal_places': '2'})
        },
        'base.produitvendu': {
            'Meta': {'ordering': "['produit']", 'object_name': 'ProduitVendu'},
            'contient': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'contient_rel_+'", 'to': "orm['base.ProduitVendu']"}),
            'cuisson': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'produitvendu-cuisson'", 'null': 'True', 'to': "orm['base.Cuisson']"}),
            'date': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'made_with': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'produit-kitchen'", 'null': 'True', 'to': "orm['base.Categorie']"}),
            'notes': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': "orm['base.Note']", 'null': 'True', 'blank': 'True'}),
            'options': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': "orm['base.Option']", 'null': 'True', 'blank': 'True'}),
            'prix': ('django.db.models.fields.DecimalField', [], {'default': '0', 'max_digits': '7', 'decimal_places': '2'}),
            'produit': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'produitvendu-produit'", 'to': "orm['base.Produit']"}),
            'sent': ('django.db.models.fields.BooleanField', [], {'default': 'False'})
        },
        'base.table': {
            'Meta': {'object_name': 'Table'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'nom': ('django.db.models.fields.CharField', [], {'max_length': '60'}),
            'zone': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'table-zone'", 'to': "orm['base.Zone']"})
        },
        'base.vat': {
            'Meta': {'ordering': "['name']", 'object_name': 'VAT'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '32'}),
            'tax': ('django.db.models.fields.DecimalField', [], {'default': '0', 'max_digits': '4', 'decimal_places': '2'}),
            'value': ('django.db.models.fields.DecimalField', [], {'default': '0', 'max_digits': '6', 'decimal_places': '4'})
        },
        'base.vatonbill': {
            'Meta': {'object_name': 'VATOnBill'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'total': ('django.db.models.fields.DecimalField', [], {'default': '0', 'max_digits': '9', 'decimal_places': '2'}),
            'vat': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'bill-vat'", 'to': "orm['base.VAT']"})
        },
        'base.weeklystat': {
            'Meta': {'ordering': "['year', 'week']", 'object_name': 'WeeklyStat'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'key': ('django.db.models.fields.CharField', [], {'max_length': '32'}),
            'value': ('django.db.models.fields.DecimalField', [], {'default': '0', 'max_digits': '9', 'decimal_places': '2'}),
            'week': ('django.db.models.fields.PositiveSmallIntegerField', [], {}),
            'year': ('django.db.models.fields.PositiveSmallIntegerField', [], {})
        },
        'base.zone': {
            'Meta': {'object_name': 'Zone'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'nom': ('django.db.models.fields.CharField', [], {'max_length': '60'}),
            'surtaxe': ('django.db.models.fields.BooleanField', [], {'default': 'False'})
        }
    }

    complete_apps = ['base']