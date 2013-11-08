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

import unittest

class Test_DailyStat(unittest.TestCase):

    def test_add_value(self, values, key, value):
            pass  # TODO

    class Meta:
        get_latest_by = 'date'

    def test_get_value(self, key, date):
        """Return value if exist and 0 else
        """
        pass  # TODO

    def test_get_avg(self, key):
        pass  # TODO

    def test_get_max(self, key):
        pass  # TODO

    def test_add_bill(self, bill):
        """if necessary, add this bill
        """
        pass  # TODO

    def test___add_bill_common(self, bill, date, year, month, week):
        pass  # TODO

    def test___add_bill_products(self, bill, date, year, month, week):
        """On fonctionne en deux passages:
        - en 1er on construit values avec toutes les stats
        - en 2eme on enregistre les résultats

        Cela nous permet de regrouper les stats de plusieurs catégories
        """
        pass  # TODO

    def test___add_bill_guests(self, bill, date, year, month, week):
        pass  # TODO

    def test___add_bill_bar(self, bill, date, year, month, week):
        pass  # TODO

    def test___add_bill_payments(self, bill, date, year, month, week):
        pass  # TODO

    def test_get_common(self, date):
        """Return les stats pour date sous forme de liste
        """
        pass  # TODO

    def test_update(self):
        """Update statistics with new bills
        """
        pass  # TODO

    def test_get_data(self, data, date):
        """Recupere les donnees pour une date, retourne data
            data = {}
        """
        pass  # TODO

