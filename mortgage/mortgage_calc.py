"""

https://www.hsbc.co.uk/mortgages/repayment-calculator/
https://en.wikipedia.org/wiki/Continuous-repayment_mortgage
https://www.moneyadviceservice.org.uk/en/tools/mortgage-calculator

"""

import math

PRINCIPAL = 'principal'
ANNUAL_INTEREST_RATE = 'annual_interest_rate'
TERM = 'term'
MONTHLY_REPAYMENT = 'monthly_repayment'

inputs = {
    PRINCIPAL: 390_000,
    ANNUAL_INTEREST_RATE: 0.02,
    TERM: 15,
    MONTHLY_REPAYMENT: 2_509.69,
}

principal = inputs[PRINCIPAL]
monthly_repayment = inputs[MONTHLY_REPAYMENT]
annual_interest_rate = inputs[ANNUAL_INTEREST_RATE]
term = inputs[TERM]


monthly_interest_rate = annual_interest_rate / 12.0
annualised_interest_rate_plus_one = (1 + monthly_interest_rate) ** 12
continuously_compounded_rate = math.log(annualised_interest_rate_plus_one)


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


def repayment_mortgage_vanilla(p, r, c):
    ii = 0
    while p >= 0:
        ii += 1
        monthly_interest_charge = r * p
        p = p + monthly_interest_charge - c
    return ii, p


def mortgage_continuously_compounded(p, r, t):
    return p*math.exp(r*t)


def single_coupon_monthly_compounded(c, r, n):
    return c*(1+r)**n


def repayment_mortgage_continuously_compounded(principal):
    months = 0
    investment = 0
    debt = principal
    while debt > investment:
        years = months / 12.0
        debt = mortgage_continuously_compounded(p=principal, r=continuously_compounded_rate, t=years)
        investment = sum(
            single_coupon_monthly_compounded(c=monthly_repayment, r=monthly_interest_rate, n=month)
            for month in range(months)
        )
        months += 1
        yield months, debt, investment


if __name__ == '__main__':

    gg = repayment_mortgage_continuously_compounded(principal=principal)
    while True:
        try:
            print(next(gg))
        except StopIteration:
            break

    duration, remainder = repayment_mortgage_vanilla(p=principal, r=monthly_interest_rate, c=monthly_repayment)
    yy, mm = divmod(duration, 12)
    print(f'year={yy}, month={mm}, remainder={remainder}')

    total_cost = mortgage_continuously_compounded(p=principal, r=continuously_compounded_rate, t=term)

    repayment_mortgage_recursive(p=principal, r=monthly_interest_rate, c=monthly_repayment)


