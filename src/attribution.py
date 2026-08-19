"""
Simulates a realistic marketing A/B test: two groups (control = old email
campaign, treatment = new email campaign), with a known, injected conversion
lift, plus realistic noise and a couple of confounding variables — so later
work can validate against ground truth.
"""
import numpy as np
import pandas as pd

def simulate_ab_test(n_per_group=5000, true_lift_pp=2.5, seed=42):
    """
    true_lift_pp: the TRUE conversion rate lift in percentage points that
    the treatment causes. We hard-code this so we can later check whether
    our statistical test correctly recovers it.
    """
    rng = np.random.default_rng(seed)

    n_total = n_per_group * 2
    group = np.array(['control'] * n_per_group + ['treatment'] * n_per_group)

    # Confounders (randomized properly across groups — this IS a real A/B test)
    customer_tenure_days = rng.exponential(scale=400, size=n_total).astype(int)
    prior_purchases = rng.poisson(lam=3, size=n_total)

    # Baseline conversion rate depends on tenure/purchases (realistic), plus
    # the treatment effect is added ONLY for the treatment group
    base_conversion_prob = 0.08 + 0.00005 * customer_tenure_days + 0.01 * prior_purchases
    base_conversion_prob = np.clip(base_conversion_prob, 0.02, 0.5)

    treatment_effect = np.where(group == 'treatment', true_lift_pp / 100, 0)
    true_conversion_prob = np.clip(base_conversion_prob + treatment_effect, 0, 1)

    converted = rng.binomial(1, true_conversion_prob)

    df = pd.DataFrame({
        'customer_id': range(1, n_total + 1),
        'group': group,
        'customer_tenure_days': customer_tenure_days,
        'prior_purchases': prior_purchases,
        'converted': converted
    })
    return df.sample(frac=1, random_state=seed).reset_index(drop=True)

if __name__ == '__main__':
    df = simulate_ab_test()
    df.to_csv('data/raw/ab_test_simulated.csv', index=False)
    print(f"Simulated {len(df)} rows, saved to data/raw/ab_test_simulated.csv")
    print(df.groupby('group')['converted'].mean())