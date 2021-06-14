"""
python -m unittest discover -s mortgage/tests
https://www.moneyadviceservice.org.uk/en/tools/mortgage-calculator
"""
import unittest
from constants import PRINCIPAL, ANNUAL_INTEREST_RATE, TERM, MONTHLY_REPAYMENT
from mortgage_calc import repayment_mortgage_vanilla

inputs = {
    PRINCIPAL: 390_000,
    ANNUAL_INTEREST_RATE: 0.02,
    TERM: 15,
    MONTHLY_REPAYMENT: 2_509.69,
}


class TestFunctions(unittest.TestCase):
    def test_repayment_mortgage_vanilla(self):
        months, remainder = repayment_mortgage_vanilla(inputs[PRINCIPAL], inputs[ANNUAL_INTEREST_RATE], inputs[MONTHLY_REPAYMENT])
        truth = 180, -1.272502095111122
        assert months, remainder == truth
