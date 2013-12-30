# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Deleting model 'Accompagnement'
        db.delete_table(u'base_accompagnement')

        # Adding model 'Dish'
        db.create_table(u'base_dish', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('nom', self.gf('django.db.models.fields.CharField')(max_length=60)),
            ('nom_facture', self.gf('django.db.models.fields.CharField')(default='', max_length=35)),
            ('color', self.gf('django.db.models.fields.CharField')(default='#ffdd82', max_length=8)),
        ))
        db.send_create_signal('base', ['Dish'])

        # Adding M2M table for field available_sauces on 'Categorie'
        m2m_table_name = db.shorten_name(u'base_categorie_available_sauces')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('categorie', models.ForeignKey(orm['base.categorie'], null=False)),
            ('sauce', models.ForeignKey(orm['base.sauce'], null=False))
        ))
        db.create_unique(m2m_table_name, ['categorie_id', 'sauce_id'])

        # Adding M2M table for field available_dishes on 'Categorie'
        m2m_table_name = db.shorten_name(u'base_categorie_available_dishes')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('categorie', models.ForeignKey(orm['base.categorie'], null=False)),
            ('dish', models.ForeignKey(orm['base.dish'], null=False))
        ))
        db.create_unique(m2m_table_name, ['categorie_id', 'dish_id'])

        # Adding field 'Sauce.nom_facture'
        db.add_column(u'base_sauce', 'nom_facture',
                      self.gf('django.db.models.fields.CharField')(default='', max_length=35),
                      keep_default=False)

        # Deleting field 'Produit.choix_accompagnement'
        db.delete_column(u'base_produit', 'choix_accompagnement')

        # Adding field 'Produit.choix_dish'
        db.add_column(u'base_produit', 'choix_dish',
                      self.gf('django.db.models.fields.BooleanField')(default=False),
                      keep_default=False)

        # Deleting field 'ProduitVendu.accompagnement'
        db.delete_column(u'base_produitvendu', 'accompagnement_id')

        # Deleting field 'ProduitVendu.sauce'
        db.delete_column(u'base_produitvendu', 'sauce_id')

        # Adding M2M table for field sauces on 'ProduitVendu'
        m2m_table_name = db.shorten_name(u'base_produitvendu_sauces')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('produitvendu', models.ForeignKey(orm['base.produitvendu'], null=False)),
            ('sauce', models.ForeignKey(orm['base.sauce'], null=False))
        ))
        db.create_unique(m2m_table_name, ['produitvendu_id', 'sauce_id'])

        # Adding M2M table for field dishes on 'ProduitVendu'
        m2m_table_name = db.shorten_name(u'base_produitvendu_dishes')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('produitvendu', models.ForeignKey(orm['base.produitvendu'], null=False)),
            ('dish', models.ForeignKey(orm['base.dish'], null=False))
        ))
        db.create_unique(m2m_table_name, ['produitvendu_id', 'dish_id'])


    def backwards(self, orm):
        # Adding model 'Accompagnement'
        db.create_table(u'base_accompagnement', (
            ('color', self.gf('django.db.models.fields.CharField')(default='#ffdd82', max_length=8)),
            ('nom', self.gf('django.db.models.fields.CharField')(max_length=60)),
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
        ))
        db.send_create_signal('base', ['Accompagnement'])

        # Deleting model 'Dish'
        db.delete_table(u'base_dish')

        # Removing M2M table for field available_sauces on 'Categorie'
        db.delete_table(db.shorten_name(u'base_categorie_available_sauces'))

        # Removing M2M table for field available_dishes on 'Categorie'
        db.delete_table(db.shorten_name(u'base_categorie_available_dishes'))

        # Deleting field 'Sauce.nom_facture'
        db.delete_column(u'base_sauce', 'nom_facture')

        # Adding field 'Produit.choix_accompagnement'
        db.add_column(u'base_produit', 'choix_accompagnement',
                      self.gf('django.db.models.fields.BooleanField')(default=False),
                      keep_default=False)

        # Deleting field 'Produit.choix_dish'
        db.delete_column(u'base_produit', 'choix_dish')

        # Adding field 'ProduitVendu.accompagnement'
        db.add_column(u'base_produitvendu', 'accompagnement',
                      self.gf('django.db.models.fields.related.ForeignKey')(related_name='produitvendu-accompagnement', null=True, to=orm['base.Accompagnement'], blank=True),
                      keep_default=False)

        # Adding field 'ProduitVendu.sauce'
        db.add_column(u'base_produitvendu', 'sauce',
                      self.gf('django.db.models.fields.related.ForeignKey')(related_name='produitvendu-sauce', null=True, to=orm['base.Sauce'], blank=True),
                      keep_default=False)

        # Removing M2M table for field sauces on 'ProduitVendu'
        db.delete_table(db.shorten_name(u'base_produitvendu_sauces'))

        # Removing M2M table for field dishes on 'ProduitVendu'
        db.delete_table(db.shorten_name(u'base_produitvendu_dishes'))


    models = {
        'base.categorie': {
            'Meta': {'ordering': "['priorite']", 'object_name': 'Categorie'},
            'available_dishes': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': "orm['base.Dish']", 'null': 'True', 'blank': 'True'}),
            'available_sauces': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': "orm['base.Sauce']", 'null': 'True', 'blank': 'True'}),
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
        'base.dish': {
            'Meta': {'object_name': 'Dish'},
            'color': ('django.db.models.fields.CharField', [], {'default': "'#ffdd82'", 'max_length': '8'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'nom': ('django.db.models.fields.CharField', [], {'max_length': '60'}),
            'nom_facture': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '35'})
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
            'Meta': {'object_name': 'Follow'},
            'category': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['base.Categorie']"}),
            'date': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
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
            'Meta': {'object_name': 'PaiementType'},
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
            'choix_dish': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'choix_sauce': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'nom': ('django.db.models.fields.CharField', [], {'max_length': '60'}),
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
            'dishes': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': "orm['base.Dish']", 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'made_with': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'produit-kitchen'", 'null': 'True', 'to': "orm['base.Categorie']"}),
            'prix': ('django.db.models.fields.DecimalField', [], {'default': '0', 'max_digits': '7', 'decimal_places': '2'}),
            'produit': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'produitvendu-produit'", 'to': "orm['base.Produit']"}),
            'sauces': ('django.db.models.fields.related.ManyToManyField', [], {'blank': 'True', 'related_name': "'produitvendu-sauce'", 'null': 'True', 'symmetrical': 'False', 'to': "orm['base.Sauce']"}),
            'sent': ('django.db.models.fields.BooleanField', [], {'default': 'False'})
        },
        'base.sauce': {
            'Meta': {'object_name': 'Sauce'},
            'color': ('django.db.models.fields.CharField', [], {'default': "'#ffdd82'", 'max_length': '8'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'nom': ('django.db.models.fields.CharField', [], {'max_length': '60'}),
            'nom_facture': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '35'})
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