"""

https://www.hsbc.co.uk/mortgages/repayment-calculator/
https://en.wikipedia.org/wiki/Continuous-repayment_mortgage
https://www.moneyadviceservice.org.uk/en/tools/mortgage-calculator

"""
import math
from collections import namedtuple
from constants import PRINCIPAL, ANNUAL_INTEREST_RATE, TERM, MONTHLY_REPAYMENT

# ==========================================================
# user entered parameters

inputs = {
    PRINCIPAL: 390_000,
    ANNUAL_INTEREST_RATE: 0.02,
    TERM: 15,
    MONTHLY_REPAYMENT: 2_509.69,
}
# ==========================================================

principal = inputs[PRINCIPAL]
monthly_repayment = inputs[MONTHLY_REPAYMENT]
annual_interest_rate = inputs[ANNUAL_INTEREST_RATE]
term = inputs[TERM]

interest_rates = namedtuple('interest_rates', 'monthly, annualised, continuously_compounded')


def calc_rates_from_annual_interest_rate(annual_interest_rate):
    interest_rates.monthly = annual_interest_rate / 12.0
    annualised_interest_rate_plus_one = (1 + interest_rates.monthly) ** 12
    interest_rates.continuously_compounded = math.log(annualised_interest_rate_plus_one)
    interest_rates.annualised = annualised_interest_rate_plus_one - 1
    return interest_rates


def repayment_mortgage_recursive(p, r, c):
    ii = 0

    def repayment_mortgage(p):
        if p <= 0:
            return 0
        else:
            ii += 1
            print(ii, p)
            return repayment_mortgage(p) * r - c + p
    repayment_mortgage(p)


def repayment_mortgage_vanilla(principal, rate, monthly_repayment):
    months = 0
    while principal >= 0:
        months += 1
        monthly_interest_charge = (rate * principal)/12
        assert monthly_repayment > monthly_interest_charge, 'mortgage will never converge'
        principal = principal + monthly_interest_charge - monthly_repayment
    return months, principal


def mortgage_continuously_compounded(p, r, t):
    return p*math.exp(r*t)


def single_coupon_monthly_compounded(c, r, n):
    return c*(1+r)**n


def all_coupons_monthly_compounded(c, r, n):
    return sum(
            single_coupon_monthly_compounded(c=c, r=r, n=month)
            for month in range(n)
        )


def repayment_mortgage_continuously_compounded(p, r, c):
    months = 0
    investment = 0
    debt = p
    while debt > investment:
        years = months / 12.0
        debt = mortgage_continuously_compounded(p=p, r=r.continuously_compounded, t=years)
        investment = all_coupons_monthly_compounded(c=c, r=r.monthly, n=months)
        months += 1
        yield months, debt, investment


if __name__ == '__main__':

    r = calc_rates_from_annual_interest_rate(annual_interest_rate)

    # ====================================================================================
    # calculate as two separate cashflows:
    # 1) continuously compounded debt and 2) monthly compounded investment

    gg = repayment_mortgage_continuously_compounded(p=principal, r=r, c=monthly_repayment)
    while True:
        try:
            months, debt, investment = next(gg)
        except StopIteration:
            yy, mm = divmod(months-1, 12)  # starts at zero months
            print(f'\n\nyear={yy}, month={mm}, remainder={investment-debt}')
            break

    # ====================================================================================
    # brute force calculation; both cashflows monthly compounded

    duration, remainder = repayment_mortgage_vanilla(p=principal, r=r.monthly, c=monthly_repayment)
    yy, mm = divmod(duration, 12)
    print(f'\n\nyear={yy}, month={mm}, remainder={remainder}')

    # ====================================================================================
    # just the debt cashflow continuously compounded

    total_cost = mortgage_continuously_compounded(p=principal, r=r.continuously_compounded, t=term)
    print(f'\n\ntotal_cost={total_cost}')

    # ====================================================================================
    # trying to be smart

    repayment_mortgage_recursive(p=principal, r=r.monthly, c=monthly_repayment)
    print()


