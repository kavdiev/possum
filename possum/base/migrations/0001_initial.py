# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):

        # Adding model 'Etat'
        db.create_table('base_etat', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('nom', self.gf('django.db.models.fields.CharField')(max_length=60)),
            ('priorite', self.gf('django.db.models.fields.PositiveIntegerField')(default=0)),
        ))
        db.send_create_signal('base', ['Etat'])

        # Adding model 'LogType'
        db.create_table('base_logtype', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('nom', self.gf('django.db.models.fields.CharField')(max_length=60)),
            ('description', self.gf('django.db.models.fields.CharField')(max_length=200, blank=True)),
        ))
        db.send_create_signal('base', ['LogType'])

        # Adding model 'Log'
        db.create_table('base_log', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('date', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('type', self.gf('django.db.models.fields.related.ForeignKey')(related_name='log-logtype', to=orm['base.LogType'])),
        ))
        db.send_create_signal('base', ['Log'])

        # Adding model 'Couleur'
        db.create_table('base_couleur', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('nom', self.gf('django.db.models.fields.CharField')(max_length=60)),
            ('red', self.gf('django.db.models.fields.PositiveIntegerField')(default=255)),
            ('green', self.gf('django.db.models.fields.PositiveIntegerField')(default=255)),
            ('blue', self.gf('django.db.models.fields.PositiveIntegerField')(default=255)),
        ))
        db.send_create_signal('base', ['Couleur'])

        # Adding model 'Categorie'
        db.create_table('base_categorie', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('nom', self.gf('django.db.models.fields.CharField')(max_length=60)),
            ('priorite', self.gf('django.db.models.fields.PositiveIntegerField')(default=0)),
            ('surtaxable', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('couleur', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='categorie-couleur', null=True, to=orm['base.Couleur'])),
            ('alcool', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('disable_surtaxe', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal('base', ['Categorie'])

        # Adding model 'Cuisson'
        db.create_table('base_cuisson', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('nom', self.gf('django.db.models.fields.CharField')(max_length=60)),
            ('priorite', self.gf('django.db.models.fields.PositiveIntegerField')(default=0)),
            ('couleur', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='cuisson-couleur', null=True, to=orm['base.Couleur'])),
        ))
        db.send_create_signal('base', ['Cuisson'])

        # Adding model 'Sauce'
        db.create_table('base_sauce', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('nom', self.gf('django.db.models.fields.CharField')(max_length=60)),
            ('couleur', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='sauce-couleur', null=True, to=orm['base.Couleur'])),
        ))
        db.send_create_signal('base', ['Sauce'])

        # Adding model 'Accompagnement'
        db.create_table('base_accompagnement', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('nom', self.gf('django.db.models.fields.CharField')(max_length=60)),
            ('couleur', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='accompagnement-couleur', null=True, to=orm['base.Couleur'])),
        ))
        db.send_create_signal('base', ['Accompagnement'])

        # Adding model 'Produit'
        db.create_table('base_produit', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('nom', self.gf('django.db.models.fields.CharField')(max_length=60)),
            ('nom_facture', self.gf('django.db.models.fields.CharField')(max_length=35)),
            ('categorie', self.gf('django.db.models.fields.related.ForeignKey')(related_name='produit-categorie', to=orm['base.Categorie'])),
            ('choix_cuisson', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('choix_accompagnement', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('choix_sauce', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('actif', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('prix', self.gf('django.db.models.fields.DecimalField')(default=0, max_digits=7, decimal_places=2)),
        ))
        db.send_create_signal('base', ['Produit'])

        # Adding M2M table for field categories_ok on 'Produit'
        db.create_table('base_produit_categories_ok', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('produit', models.ForeignKey(orm['base.produit'], null=False)),
            ('categorie', models.ForeignKey(orm['base.categorie'], null=False))
        ))
        db.create_unique('base_produit_categories_ok', ['produit_id', 'categorie_id'])

        # Adding M2M table for field produits_ok on 'Produit'
        db.create_table('base_produit_produits_ok', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('from_produit', models.ForeignKey(orm['base.produit'], null=False)),
            ('to_produit', models.ForeignKey(orm['base.produit'], null=False))
        ))
        db.create_unique('base_produit_produits_ok', ['from_produit_id', 'to_produit_id'])

        # Adding model 'ProduitVendu'
        db.create_table('base_produitvendu', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('date', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('produit', self.gf('django.db.models.fields.related.ForeignKey')(related_name='produitvendu-produit', to=orm['base.Produit'])),
            ('cuisson', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='produitvendu-cuisson', null=True, to=orm['base.Cuisson'])),
            ('prix', self.gf('django.db.models.fields.DecimalField')(default=0, max_digits=7, decimal_places=2)),
            ('sauce', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='produitvendu-sauce', null=True, to=orm['base.Sauce'])),
            ('accompagnement', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='produitvendu-accompagnement', null=True, to=orm['base.Accompagnement'])),
        ))
        db.send_create_signal('base', ['ProduitVendu'])

        # Adding M2M table for field contient on 'ProduitVendu'
        db.create_table('base_produitvendu_contient', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('from_produitvendu', models.ForeignKey(orm['base.produitvendu'], null=False)),
            ('to_produitvendu', models.ForeignKey(orm['base.produitvendu'], null=False))
        ))
        db.create_unique('base_produitvendu_contient', ['from_produitvendu_id', 'to_produitvendu_id'])

        # Adding model 'PaiementType'
        db.create_table('base_paiementtype', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('nom', self.gf('django.db.models.fields.CharField')(max_length=60)),
            ('nom_facture', self.gf('django.db.models.fields.CharField')(max_length=35)),
            ('priorite', self.gf('django.db.models.fields.PositiveIntegerField')(default=0)),
            ('fixed_value', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal('base', ['PaiementType'])

        # Adding model 'Paiement'
        db.create_table('base_paiement', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('type', self.gf('django.db.models.fields.related.ForeignKey')(related_name='paiement-type', to=orm['base.PaiementType'])),
            ('montant', self.gf('django.db.models.fields.DecimalField')(default=0, max_digits=9, decimal_places=2)),
            ('valeur_unitaire', self.gf('django.db.models.fields.DecimalField')(default=1, max_digits=9, decimal_places=2)),
            ('date', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('nb_tickets', self.gf('django.db.models.fields.PositiveIntegerField')(default=0)),
        ))
        db.send_create_signal('base', ['Paiement'])

        # Adding model 'StatsJourGeneral'
        db.create_table('base_statsjourgeneral', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('date', self.gf('django.db.models.fields.DateField')()),
            ('valeur', self.gf('django.db.models.fields.DecimalField')(default=0, max_digits=9, decimal_places=2)),
            ('type', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='statsjour-logtype', null=True, to=orm['base.LogType'])),
        ))
        db.send_create_signal('base', ['StatsJourGeneral'])

        # Adding model 'StatsJourPaiement'
        db.create_table('base_statsjourpaiement', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('date', self.gf('django.db.models.fields.DateField')()),
            ('valeur', self.gf('django.db.models.fields.DecimalField')(default=0, max_digits=9, decimal_places=2)),
            ('paiement', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='statsjour-paiement', null=True, to=orm['base.PaiementType'])),
            ('nb', self.gf('django.db.models.fields.PositiveIntegerField')(default=0)),
        ))
        db.send_create_signal('base', ['StatsJourPaiement'])

        # Adding model 'StatsJourProduit'
        db.create_table('base_statsjourproduit', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('date', self.gf('django.db.models.fields.DateField')()),
            ('valeur', self.gf('django.db.models.fields.DecimalField')(default=0, max_digits=9, decimal_places=2)),
            ('produit', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='statsjour-produit', null=True, to=orm['base.Produit'])),
            ('nb', self.gf('django.db.models.fields.PositiveIntegerField')(default=0)),
        ))
        db.send_create_signal('base', ['StatsJourProduit'])

        # Adding model 'StatsJourCategorie'
        db.create_table('base_statsjourcategorie', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('date', self.gf('django.db.models.fields.DateField')()),
            ('valeur', self.gf('django.db.models.fields.DecimalField')(default=0, max_digits=9, decimal_places=2)),
            ('categorie', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='statsjour-categorie', null=True, to=orm['base.Categorie'])),
            ('nb', self.gf('django.db.models.fields.PositiveIntegerField')(default=0)),
        ))
        db.send_create_signal('base', ['StatsJourCategorie'])

        # Adding model 'Zone'
        db.create_table('base_zone', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('nom', self.gf('django.db.models.fields.CharField')(max_length=60)),
            ('surtaxe', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('prix_surtaxe', self.gf('django.db.models.fields.DecimalField')(default=0, max_digits=4, decimal_places=2)),
        ))
        db.send_create_signal('base', ['Zone'])

        # Adding model 'Table'
        db.create_table('base_table', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('nom', self.gf('django.db.models.fields.CharField')(max_length=60)),
            ('zone', self.gf('django.db.models.fields.related.ForeignKey')(related_name='table-zone', to=orm['base.Zone'])),
        ))
        db.send_create_signal('base', ['Table'])

        # Adding model 'Suivi'
        db.create_table('base_suivi', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('facture', self.gf('django.db.models.fields.related.ForeignKey')(related_name='suivi-facture', to=orm['base.Facture'])),
            ('etat', self.gf('django.db.models.fields.related.ForeignKey')(related_name='suivi-etat', to=orm['base.Etat'])),
            ('date', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
        ))
        db.send_create_signal('base', ['Suivi'])

        # Adding model 'Facture'
        db.create_table('base_facture', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('date_creation', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('table', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='facture-table', null=True, to=orm['base.Table'])),
            ('couverts', self.gf('django.db.models.fields.PositiveIntegerField')(default=0)),
            ('montant_normal', self.gf('django.db.models.fields.DecimalField')(default=0, max_digits=9, decimal_places=2)),
            ('montant_alcool', self.gf('django.db.models.fields.DecimalField')(default=0, max_digits=9, decimal_places=2)),
            ('restant_a_payer', self.gf('django.db.models.fields.DecimalField')(default=0, max_digits=9, decimal_places=2)),
            ('saved_in_stats', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal('base', ['Facture'])

        # Adding M2M table for field produits on 'Facture'
        db.create_table('base_facture_produits', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('facture', models.ForeignKey(orm['base.facture'], null=False)),
            ('produitvendu', models.ForeignKey(orm['base.produitvendu'], null=False))
        ))
        db.create_unique('base_facture_produits', ['facture_id', 'produitvendu_id'])

        # Adding M2M table for field paiements on 'Facture'
        db.create_table('base_facture_paiements', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('facture', models.ForeignKey(orm['base.facture'], null=False)),
            ('paiement', models.ForeignKey(orm['base.paiement'], null=False))
        ))
        db.create_unique('base_facture_paiements', ['facture_id', 'paiement_id'])

        # Adding M2M table for field etats on 'Facture'
        db.create_table('base_facture_etats', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('facture', models.ForeignKey(orm['base.facture'], null=False)),
            ('suivi', models.ForeignKey(orm['base.suivi'], null=False))
        ))
        db.create_unique('base_facture_etats', ['facture_id', 'suivi_id'])


    def backwards(self, orm):
        
        # Deleting model 'Etat'
        db.delete_table('base_etat')

        # Deleting model 'LogType'
        db.delete_table('base_logtype')

        # Deleting model 'Log'
        db.delete_table('base_log')

        # Deleting model 'Couleur'
        db.delete_table('base_couleur')

        # Deleting model 'Categorie'
        db.delete_table('base_categorie')

        # Deleting model 'Cuisson'
        db.delete_table('base_cuisson')

        # Deleting model 'Sauce'
        db.delete_table('base_sauce')

        # Deleting model 'Accompagnement'
        db.delete_table('base_accompagnement')

        # Deleting model 'Produit'
        db.delete_table('base_produit')

        # Removing M2M table for field categories_ok on 'Produit'
        db.delete_table('base_produit_categories_ok')

        # Removing M2M table for field produits_ok on 'Produit'
        db.delete_table('base_produit_produits_ok')

        # Deleting model 'ProduitVendu'
        db.delete_table('base_produitvendu')

        # Removing M2M table for field contient on 'ProduitVendu'
        db.delete_table('base_produitvendu_contient')

        # Deleting model 'PaiementType'
        db.delete_table('base_paiementtype')

        # Deleting model 'Paiement'
        db.delete_table('base_paiement')

        # Deleting model 'StatsJourGeneral'
        db.delete_table('base_statsjourgeneral')

        # Deleting model 'StatsJourPaiement'
        db.delete_table('base_statsjourpaiement')

        # Deleting model 'StatsJourProduit'
        db.delete_table('base_statsjourproduit')

        # Deleting model 'StatsJourCategorie'
        db.delete_table('base_statsjourcategorie')

        # Deleting model 'Zone'
        db.delete_table('base_zone')

        # Deleting model 'Table'
        db.delete_table('base_table')

        # Deleting model 'Suivi'
        db.delete_table('base_suivi')

        # Deleting model 'Facture'
        db.delete_table('base_facture')

        # Removing M2M table for field produits on 'Facture'
        db.delete_table('base_facture_produits')

        # Removing M2M table for field paiements on 'Facture'
        db.delete_table('base_facture_paiements')

        # Removing M2M table for field etats on 'Facture'
        db.delete_table('base_facture_etats')


    models = {
        'base.accompagnement': {
            'Meta': {'ordering': "['nom']", 'object_name': 'Accompagnement'},
            'couleur': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'accompagnement-couleur'", 'null': 'True', 'to': "orm['base.Couleur']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'nom': ('django.db.models.fields.CharField', [], {'max_length': '60'})
        },
        'base.categorie': {
            'Meta': {'ordering': "['nom']", 'object_name': 'Categorie'},
            'alcool': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'couleur': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'categorie-couleur'", 'null': 'True', 'to': "orm['base.Couleur']"}),
            'disable_surtaxe': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'nom': ('django.db.models.fields.CharField', [], {'max_length': '60'}),
            'priorite': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'}),
            'surtaxable': ('django.db.models.fields.BooleanField', [], {'default': 'False'})
        },
        'base.couleur': {
            'Meta': {'ordering': "['nom']", 'object_name': 'Couleur'},
            'blue': ('django.db.models.fields.PositiveIntegerField', [], {'default': '255'}),
            'green': ('django.db.models.fields.PositiveIntegerField', [], {'default': '255'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'nom': ('django.db.models.fields.CharField', [], {'max_length': '60'}),
            'red': ('django.db.models.fields.PositiveIntegerField', [], {'default': '255'})
        },
        'base.cuisson': {
            'Meta': {'ordering': "['nom']", 'object_name': 'Cuisson'},
            'couleur': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'cuisson-couleur'", 'null': 'True', 'to': "orm['base.Couleur']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'nom': ('django.db.models.fields.CharField', [], {'max_length': '60'}),
            'priorite': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'})
        },
        'base.etat': {
            'Meta': {'ordering': "['nom']", 'object_name': 'Etat'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'nom': ('django.db.models.fields.CharField', [], {'max_length': '60'}),
            'priorite': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'})
        },
        'base.facture': {
            'Meta': {'object_name': 'Facture'},
            'couverts': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'}),
            'date_creation': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'etats': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'le suivi'", 'symmetrical': 'False', 'to': "orm['base.Suivi']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'montant_alcool': ('django.db.models.fields.DecimalField', [], {'default': '0', 'max_digits': '9', 'decimal_places': '2'}),
            'montant_normal': ('django.db.models.fields.DecimalField', [], {'default': '0', 'max_digits': '9', 'decimal_places': '2'}),
            'paiements': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'les paiements'", 'symmetrical': 'False', 'to': "orm['base.Paiement']"}),
            'produits': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'les produits factures'", 'symmetrical': 'False', 'to': "orm['base.ProduitVendu']"}),
            'restant_a_payer': ('django.db.models.fields.DecimalField', [], {'default': '0', 'max_digits': '9', 'decimal_places': '2'}),
            'saved_in_stats': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'table': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'facture-table'", 'null': 'True', 'to': "orm['base.Table']"})
        },
        'base.log': {
            'Meta': {'object_name': 'Log'},
            'date': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'type': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'log-logtype'", 'to': "orm['base.LogType']"})
        },
        'base.logtype': {
            'Meta': {'ordering': "['nom']", 'object_name': 'LogType'},
            'description': ('django.db.models.fields.CharField', [], {'max_length': '200', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'nom': ('django.db.models.fields.CharField', [], {'max_length': '60'})
        },
        'base.paiement': {
            'Meta': {'object_name': 'Paiement'},
            'date': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'montant': ('django.db.models.fields.DecimalField', [], {'default': '0', 'max_digits': '9', 'decimal_places': '2'}),
            'nb_tickets': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'}),
            'type': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'paiement-type'", 'to': "orm['base.PaiementType']"}),
            'valeur_unitaire': ('django.db.models.fields.DecimalField', [], {'default': '1', 'max_digits': '9', 'decimal_places': '2'})
        },
        'base.paiementtype': {
            'Meta': {'ordering': "['priorite']", 'object_name': 'PaiementType'},
            'fixed_value': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'nom': ('django.db.models.fields.CharField', [], {'max_length': '60'}),
            'nom_facture': ('django.db.models.fields.CharField', [], {'max_length': '35'}),
            'priorite': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'})
        },
        'base.produit': {
            'Meta': {'ordering': "('categorie', 'nom')", 'object_name': 'Produit'},
            'actif': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'categorie': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'produit-categorie'", 'to': "orm['base.Categorie']"}),
            'categories_ok': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['base.Categorie']", 'symmetrical': 'False'}),
            'choix_accompagnement': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'choix_cuisson': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'choix_sauce': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'nom': ('django.db.models.fields.CharField', [], {'max_length': '60'}),
            'nom_facture': ('django.db.models.fields.CharField', [], {'max_length': '35'}),
            'prix': ('django.db.models.fields.DecimalField', [], {'default': '0', 'max_digits': '7', 'decimal_places': '2'}),
            'produits_ok': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'produits_ok_rel_+'", 'to': "orm['base.Produit']"})
        },
        'base.produitvendu': {
            'Meta': {'ordering': "('produit',)", 'object_name': 'ProduitVendu'},
            'accompagnement': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'produitvendu-accompagnement'", 'null': 'True', 'to': "orm['base.Accompagnement']"}),
            'contient': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'contient_rel_+'", 'to': "orm['base.ProduitVendu']"}),
            'cuisson': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'produitvendu-cuisson'", 'null': 'True', 'to': "orm['base.Cuisson']"}),
            'date': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'prix': ('django.db.models.fields.DecimalField', [], {'default': '0', 'max_digits': '7', 'decimal_places': '2'}),
            'produit': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'produitvendu-produit'", 'to': "orm['base.Produit']"}),
            'sauce': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'produitvendu-sauce'", 'null': 'True', 'to': "orm['base.Sauce']"})
        },
        'base.sauce': {
            'Meta': {'ordering': "['nom']", 'object_name': 'Sauce'},
            'couleur': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'sauce-couleur'", 'null': 'True', 'to': "orm['base.Couleur']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'nom': ('django.db.models.fields.CharField', [], {'max_length': '60'})
        },
        'base.statsjourcategorie': {
            'Meta': {'object_name': 'StatsJourCategorie'},
            'categorie': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'statsjour-categorie'", 'null': 'True', 'to': "orm['base.Categorie']"}),
            'date': ('django.db.models.fields.DateField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'nb': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'}),
            'valeur': ('django.db.models.fields.DecimalField', [], {'default': '0', 'max_digits': '9', 'decimal_places': '2'})
        },
        'base.statsjourgeneral': {
            'Meta': {'object_name': 'StatsJourGeneral'},
            'date': ('django.db.models.fields.DateField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'type': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'statsjour-logtype'", 'null': 'True', 'to': "orm['base.LogType']"}),
            'valeur': ('django.db.models.fields.DecimalField', [], {'default': '0', 'max_digits': '9', 'decimal_places': '2'})
        },
        'base.statsjourpaiement': {
            'Meta': {'object_name': 'StatsJourPaiement'},
            'date': ('django.db.models.fields.DateField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'nb': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'}),
            'paiement': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'statsjour-paiement'", 'null': 'True', 'to': "orm['base.PaiementType']"}),
            'valeur': ('django.db.models.fields.DecimalField', [], {'default': '0', 'max_digits': '9', 'decimal_places': '2'})
        },
        'base.statsjourproduit': {
            'Meta': {'object_name': 'StatsJourProduit'},
            'date': ('django.db.models.fields.DateField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'nb': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'}),
            'produit': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'statsjour-produit'", 'null': 'True', 'to': "orm['base.Produit']"}),
            'valeur': ('django.db.models.fields.DecimalField', [], {'default': '0', 'max_digits': '9', 'decimal_places': '2'})
        },
        'base.suivi': {
            'Meta': {'object_name': 'Suivi'},
            'date': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'etat': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'suivi-etat'", 'to': "orm['base.Etat']"}),
            'facture': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'suivi-facture'", 'to': "orm['base.Facture']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        'base.table': {
            'Meta': {'ordering': "['nom']", 'object_name': 'Table'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'nom': ('django.db.models.fields.CharField', [], {'max_length': '60'}),
            'zone': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'table-zone'", 'to': "orm['base.Zone']"})
        },
        'base.zone': {
            'Meta': {'ordering': "['nom']", 'object_name': 'Zone'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'nom': ('django.db.models.fields.CharField', [], {'max_length': '60'}),
            'prix_surtaxe': ('django.db.models.fields.DecimalField', [], {'default': '0', 'max_digits': '4', 'decimal_places': '2'}),
            'surtaxe': ('django.db.models.fields.BooleanField', [], {'default': 'False'})
        }
    }

    complete_apps = ['base']
