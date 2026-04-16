import pandas as pd
import numpy as np
from scipy import stats

np.random.seed(42)

df = pd.read_csv('/mnt/user-data/uploads/influencer_marketing_roi_dataset.csv')

print(f"Loaded: {df.shape[0]:,} rows")

# ─────────────────────────────────────────────
# BENCHMARK SOURCES (cited in README)
# HypeAuditor State of Influencer Marketing 2024
# Influencer Marketing Hub Benchmark Report 2024
# Sprout Social Influencer Marketing Report 2024
# ─────────────────────────────────────────────

# CTR benchmarks by platform (mean, std)
# Source: HypeAuditor 2024, IMH 2024
CTR_BENCHMARKS = {
    'TikTok':    {'mean': 0.018, 'std': 0.008},   # TikTok ~1.8% CTR, higher virality
    'Instagram': {'mean': 0.012, 'std': 0.006},   # Instagram ~1.2% CTR
    'YouTube':   {'mean': 0.007, 'std': 0.004},   # YouTube ~0.7% CTR (longer intent cycle)
    'Twitter':   {'mean': 0.009, 'std': 0.005},   # Twitter ~0.9% CTR
}

# Conversion rate benchmarks by platform (mean, std)
# Source: IMH 2024, Sprout Social 2024
CVR_BENCHMARKS = {
    'TikTok':    {'mean': 0.032, 'std': 0.015},   # TikTok Shop effect, impulse behavior
    'Instagram': {'mean': 0.025, 'std': 0.012},   # Shoppable posts, strong intent
    'YouTube':   {'mean': 0.045, 'std': 0.018},   # Highest CVR — search intent, trust
    'Twitter':   {'mean': 0.015, 'std': 0.008},   # Lower purchase intent
}

# Campaign type multipliers on CTR
# Product Launch and Seasonal Sale drive higher click intent
CAMPAIGN_CTR_MULTIPLIERS = {
    'Product Launch':  1.25,
    'Seasonal Sale':   1.35,
    'Giveaway':        0.80,   # High engagement, low purchase intent
    'Brand Awareness': 0.70,   # Awareness ≠ action
    'Event Promotion': 1.00,
}

# Category multipliers on CVR
# Beauty/Fashion convert well; Gaming/Tech have longer consideration cycles
CATEGORY_CVR_MULTIPLIERS = {
    'Beauty':  1.30,
    'Fashion': 1.20,
    'Food':    1.10,
    'Fitness': 1.05,
    'Travel':  0.90,
    'Tech':    0.80,
    'Gaming':  0.75,
}

# ─────────────────────────────────────────────
# DERIVE: engagement_rate
# ─────────────────────────────────────────────
df['engagement_rate'] = df['engagements'] / df['estimated_reach'].replace(0, np.nan)

# ─────────────────────────────────────────────
# DERIVE: clicks  (CTR × estimated_reach)
# with campaign type multiplier + noise
# ─────────────────────────────────────────────
def generate_clicks(row):
    bench = CTR_BENCHMARKS[row['platform']]
    ctr_base = np.random.normal(bench['mean'], bench['std'])
    ctr_base = max(0.001, ctr_base)   # floor at 0.1%
    multiplier = CAMPAIGN_CTR_MULTIPLIERS.get(row['campaign_type'], 1.0)
    ctr = ctr_base * multiplier
    clicks = int(row['estimated_reach'] * ctr)
    return max(1, clicks)

df['clicks'] = df.apply(generate_clicks, axis=1)
df['ctr'] = df['clicks'] / df['estimated_reach']

# ─────────────────────────────────────────────
# DERIVE: conversions  (CVR × clicks)
# with category multiplier + engagement signal
# ─────────────────────────────────────────────
def generate_conversions(row):
    bench = CVR_BENCHMARKS[row['platform']]
    cvr_base = np.random.normal(bench['mean'], bench['std'])
    cvr_base = max(0.001, cvr_base)
    cat_mult = CATEGORY_CVR_MULTIPLIERS.get(row['influencer_category'], 1.0)
    # High engagement rate slightly boosts conversion (trust signal)
    er_boost = 1 + (row['engagement_rate'] - 0.10) * 0.5 if row['engagement_rate'] > 0.10 else 1.0
    er_boost = min(er_boost, 1.5)  # cap
    cvr = cvr_base * cat_mult * er_boost
    conversions = int(row['clicks'] * cvr)
    return max(0, conversions)

df['conversions'] = df.apply(generate_conversions, axis=1)
df['conversion_rate'] = df['conversions'] / df['clicks'].replace(0, np.nan)

# ─────────────────────────────────────────────
# DERIVE: action_yield
# conversions per engagement — the core gap metric numerator
# ─────────────────────────────────────────────
df['action_yield'] = df['conversions'] / df['engagements'].replace(0, np.nan)

# ─────────────────────────────────────────────
# DERIVE: sales_per_conversion
# product_sales / conversions — revenue efficiency
# ─────────────────────────────────────────────
df['revenue_per_conversion'] = df['product_sales'] / df['conversions'].replace(0, np.nan)

# ─────────────────────────────────────────────
# DERIVE: campaign_efficiency
# product_sales / estimated_reach — full funnel collapse
# ─────────────────────────────────────────────
df['campaign_efficiency'] = df['product_sales'] / df['estimated_reach'].replace(0, np.nan)

print("\nNew columns created:")
new_cols = ['engagement_rate','clicks','ctr','conversions','conversion_rate','action_yield','revenue_per_conversion','campaign_efficiency']
print(df[new_cols].describe().round(4).to_string())

print("\nSample rows:")
print(df[['platform','influencer_category','campaign_type','engagements','clicks','conversions','ctr','conversion_rate','action_yield']].head(8).to_string())


# ─────────────────────────────────────────────
# IGS COMPUTATION
# IGS = z(action_score) - z(interaction_score)
# ─────────────────────────────────────────────

def z_norm(series):
    s = series.copy()
    s = s.fillna(s.median())
    mean, std = s.mean(), s.std()
    if std == 0:
        return pd.Series(0, index=s.index)
    return (s - mean) / std

# Interaction score: engagement rate + action_yield inverse proxy
# (high engagement relative to reach)
df['z_engagement_rate'] = z_norm(df['engagement_rate'])
df['z_ctr']             = z_norm(df['ctr'])
df['z_action_yield']    = z_norm(df['action_yield'])
df['z_conversion_rate'] = z_norm(df['conversion_rate'])
df['z_campaign_eff']    = z_norm(df['campaign_efficiency'])

# Composite scores
df['interaction_score'] = df['z_engagement_rate']  # engagement vs reach
df['action_score']      = (df['z_ctr'] + df['z_action_yield'] + df['z_conversion_rate']) / 3

# IGS: positive = action outpaces engagement (underpriced)
#       negative = engagement outpaces action (engagement theater)
df['IGS'] = df['action_score'] - df['interaction_score']

print("\nIGS Distribution:")
print(df['IGS'].describe().round(3))
print()
print("IGS by platform:")
print(df.groupby('platform')['IGS'].mean().round(3).sort_values())
print()
print("IGS by campaign type:")
print(df.groupby('campaign_type')['IGS'].mean().round(3).sort_values())
print()
print("IGS by category:")
print(df.groupby('influencer_category')['IGS'].mean().round(3).sort_values())


# ─────────────────────────────────────────────
# ARCHETYPE ASSIGNMENT
# Based on IGS + interaction/action score quintiles
# ─────────────────────────────────────────────

i_q = df['interaction_score'].quantile([0.33, 0.67])
a_q = df['action_score'].quantile([0.33, 0.67])

i_lo, i_hi = i_q[0.33], i_q[0.67]
a_lo, a_hi = a_q[0.33], a_q[0.67]

def assign_archetype(row):
    i = row['interaction_score']
    a = row['action_score']
    igs = row['IGS']

    if igs > 1.5 and a > a_hi:
        return 'Quiet Converter'
    elif igs < -1.5 and i > i_hi:
        return 'Engagement Trap'
    elif i > i_hi and a > a_hi:
        return 'Full-Funnel Creator'
    elif igs < -0.8 and i > i_lo:
        return 'Platform Native'
    elif igs > 0.8 and a > a_lo:
        return 'Behavior-Positive'
    elif i < i_lo and a < a_lo:
        return 'Ghost Amplifier'
    else:
        return 'Spike Artist'

df['archetype'] = df.apply(assign_archetype, axis=1)

print("\nArchetype Distribution:")
arch_counts = df['archetype'].value_counts()
print(arch_counts)
print()
print("Archetype × Mean IGS:")
print(df.groupby('archetype')['IGS'].mean().round(3).sort_values())
print()
print("Archetype × Mean conversion_rate:")
print(df.groupby('archetype')['conversion_rate'].mean().round(4).sort_values())
print()
print("Archetype × Mean action_yield:")
print(df.groupby('archetype')['action_yield'].mean().round(5).sort_values())
print()
print("Archetype × Platform mix (top):")
print(df.groupby(['archetype','platform']).size().unstack(fill_value=0))


# ─────────────────────────────────────────────
# KEY ANALYSES
# ─────────────────────────────────────────────

print("\n" + "="*60)
print("ANALYSIS 1: Engagement-Conversion Decoupling")
print("="*60)
from scipy.stats import pearsonr, spearmanr

for platform in df['platform'].unique():
    sub = df[df['platform'] == platform]
    r_pearson, p_pearson = pearsonr(sub['engagement_rate'].clip(0,5), sub['conversion_rate'])
    r_spearman, p_spearman = spearmanr(sub['engagement_rate'], sub['conversion_rate'])
    print(f"{platform}: Pearson r={r_pearson:.3f} (p={p_pearson:.3f}) | Spearman r={r_spearman:.3f}")

print("\n" + "="*60)
print("ANALYSIS 2: IGS by Platform — Structural Gap")
print("="*60)
platform_igs = df.groupby('platform').agg(
    mean_IGS=('IGS','mean'),
    mean_engagement_rate=('engagement_rate','mean'),
    mean_conversion_rate=('conversion_rate','mean'),
    mean_action_yield=('action_yield','mean'),
    n=('IGS','count')
).round(4)
print(platform_igs.sort_values('mean_IGS').to_string())

print("\n" + "="*60)
print("ANALYSIS 3: Archetype Value Audit — ROI Story")
print("="*60)
archetype_audit = df.groupby('archetype').agg(
    n=('IGS','count'),
    mean_IGS=('IGS','mean'),
    mean_product_sales=('product_sales','mean'),
    mean_conversions=('conversions','mean'),
    mean_conversion_rate=('conversion_rate','mean'),
    mean_action_yield=('action_yield','mean'),
    sales_per_engagement=('product_sales', lambda x: x.mean() / df.loc[x.index, 'engagements'].mean())
).round(3)
print(archetype_audit.sort_values('mean_IGS').to_string())

print("\n" + "="*60)
print("ANALYSIS 4: Engagement Trap vs Quiet Converter — The Money Slide")
print("="*60)
et = df[df['archetype'] == 'Engagement Trap']
qc = df[df['archetype'] == 'Quiet Converter']
print(f"Engagement Trap   — avg engagements: {et['engagements'].mean():.0f} | avg conversions: {et['conversions'].mean():.0f} | avg CVR: {et['conversion_rate'].mean():.3f} | avg action_yield: {et['action_yield'].mean():.6f}")
print(f"Quiet Converter   — avg engagements: {qc['engagements'].mean():.0f} | avg conversions: {qc['conversions'].mean():.0f} | avg CVR: {qc['conversion_rate'].mean():.3f} | avg action_yield: {qc['action_yield'].mean():.6f}")
print(f"\nQuiet Converter delivers {qc['action_yield'].mean() / et['action_yield'].mean():.0f}x more action per engagement unit")
print(f"Engagement Trap has {et['engagements'].mean() / qc['engagements'].mean():.1f}x more raw engagement — but converts worse")

print("\n" + "="*60)
print("ANALYSIS 5: Reach Efficiency Frontier")
print("="*60)
reach_bins = pd.cut(df['estimated_reach'], bins=5, labels=['Very Low','Low','Mid','High','Very High'])
reach_eff = df.groupby(reach_bins, observed=True).agg(
    mean_action_yield=('action_yield','mean'),
    mean_conversion_rate=('conversion_rate','mean'),
    mean_IGS=('IGS','mean'),
    n=('IGS','count')
).round(4)
print(reach_eff.to_string())


# ─────────────────────────────────────────────
# SAVE FINAL DATASET
# ─────────────────────────────────────────────

output_cols = [
    'campaign_id', 'platform', 'influencer_category', 'campaign_type',
    'start_date', 'end_date', 'campaign_duration_days',
    'estimated_reach', 'engagements', 'clicks', 'conversions', 'product_sales',
    'engagement_rate', 'ctr', 'conversion_rate', 'action_yield',
    'revenue_per_conversion', 'campaign_efficiency',
    'interaction_score', 'action_score', 'IGS', 'archetype'
]

df[output_cols].to_csv('/home/claude/influence_gap_final.csv', index=False)
print(f"\nFinal dataset saved: {df.shape[0]:,} rows × {len(output_cols)} columns")
print("Columns:", output_cols)

# Quick sanity check
print("\nFinal archetype counts:")
print(df['archetype'].value_counts().to_string())
print("\nIGS range by archetype:")
print(df.groupby('archetype')['IGS'].agg(['min','mean','max']).round(2).sort_values('mean').to_string())

