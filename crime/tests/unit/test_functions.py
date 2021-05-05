"""
C:\dev\code\projects (master -> origin)
(reference) λ python -m unittest discover -s crime/tests/unit
"""

import unittest
import pandas as pd
from crime.crime.main import get_date_from_string


class TestFunctions(unittest.TestCase):
    def test_get_date_from_string(self):
        columns = ['Month']
        df = pd.DataFrame(data=['2020-11'], columns=columns)
        get_date_from_string(df)

        truth = pd.DataFrame(data=[pd.to_datetime('2020-11-01')], columns=columns)

        pd.testing.assert_frame_equal(df, truth)

