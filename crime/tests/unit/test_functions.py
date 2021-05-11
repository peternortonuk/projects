"""
C:\dev\code\projects (master -> origin)
(reference) λ python -m unittest discover -s crime/tests/unit
"""

import unittest
import pandas as pd
from crime.crime.main import get_date_from_string, create_colors_for_items, build_string_for_location


class TestFunctions(unittest.TestCase):
    def test_get_date_from_string(self):
        columns = ['Month']
        df = pd.DataFrame(data=['2020-11'], columns=columns)
        get_date_from_string(df)

        truth = pd.DataFrame(data=[pd.to_datetime('2020-11-01')], columns=columns)

        pd.testing.assert_frame_equal(df, truth)

    def test_create_colors_for_items(self):
        lst = list('abcd')
        result = create_colors_for_items(lst)

        truth = {'a': '0x1f77b4', 'b': '0xff7f0e', 'c': '0x2ca02c', 'd': '0xd62728'}

        assert truth == result

    def test_build_string_for_location(self):
        data = [{'Latitude': 54.123, 'Longitude': 0.123, },
                {'Latitude': 53.000, 'Longitude': 0.000, }]
        df = pd.DataFrame(data=data)

        result = []
        for _, row in df.iterrows():
            ss = build_string_for_location(row)
            result.append(ss)

        truth = ['54.123,0.123', '53.0,0.0']

        assert truth == result



