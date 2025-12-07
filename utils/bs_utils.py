import math
from scipy.stats import norm

def d1(S, K, r, q, sigma, T):
    return (math.log(S / K) + (r - q + 0.5 * sigma**2) * T) / (sigma * math.sqrt(T))

def d2(S, K, r, q, sigma, T):
    return d1(S, K, r, q, sigma, T) - sigma * math.sqrt(T)

def bs_price(S, K, r, q, sigma, T, option_type='call'):
    # S - spot, K - strike, r - risk-free rate, q - dividend yield, sigma - vol, T - time in years
    if T <= 0:
        # at or after expiry: payoff
        if option_type == 'call':
            return max(0.0, S - K)
        else:
            return max(0.0, K - S)
    if sigma <= 0:
        # degenerate case: price = discounted payoff under no vol (approx)
        if option_type == 'call':
            return max(0.0, S * math.exp(-q*T) - K * math.exp(-r*T))
        else:
            return max(0.0, K * math.exp(-r*T) - S * math.exp(-q*T))

    D1 = d1(S, K, r, q, sigma, T)
    D2 = D1 - sigma * math.sqrt(T)
    if option_type == 'call':
        price = S * math.exp(-q*T) * norm.cdf(D1) - K * math.exp(-r*T) * norm.cdf(D2)
    else:
        price = K * math.exp(-r*T) * norm.cdf(-D2) - S * math.exp(-q*T) * norm.cdf(-D1)
    return price

def bs_delta(S, K, r, q, sigma, T, option_type='call'):
    if T <= 0:
        return 1.0 if (option_type=='call' and S>K) else (0.0 if option_type=='call' else (-1.0 if S<K else 0.0))
    D1 = d1(S, K, r, q, sigma, T)
    if option_type == 'call':
        return math.exp(-q*T) * norm.cdf(D1)
    else:
        return math.exp(-q*T) * (norm.cdf(D1) - 1.0)

def bs_vega(S, K, r, q, sigma, T):
    if T <= 0 or sigma <= 0:
        return 0.0
    D1 = d1(S, K, r, q, sigma, T)
    return S * math.exp(-q*T) * norm.pdf(D1) * math.sqrt(T)

def bs_gamma(S, K, r, q, sigma, T):
    if T <= 0 or sigma <= 0:
        return 0.0
    D1 = d1(S, K, r, q, sigma, T)
    return math.exp(-q*T) * norm.pdf(D1) / (S * sigma * math.sqrt(T))

def bs_theta(S, K, r, q, sigma, T, option_type='call'):
    # not strictly necessary for start, but useful
    if T <= 0:
        return 0.0
    D1 = d1(S, K, r, q, sigma, T)
    D2 = D1 - sigma * math.sqrt(T)
    term1 = - (S * norm.pdf(D1) * sigma * math.exp(-q*T)) / (2 * math.sqrt(T))
    if option_type == 'call':
        term2 = q * S * norm.cdf(D1) * math.exp(-q*T)
        term3 = - r * K * math.exp(-r*T) * norm.cdf(D2)
        return term1 + term2 + term3
    else:
        term2 = q * S * math.exp(-q*T) * norm.cdf(-D1)
        term3 = - r * K * math.exp(-r*T) * norm.cdf(-D2)
        return term1 + term2 + term3
