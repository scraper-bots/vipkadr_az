#!/usr/bin/env python3
"""
Business Analytics Dashboard Generator
Generates comprehensive visualizations for VIPKadr job market data
"""

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

# Set style for professional business charts
plt.style.use('seaborn-v0_8-darkgrid')
sns.set_palette("husl")
colors = ['#2E86AB', '#A23B72', '#F18F01', '#C73E1D', '#6A994E', '#BC4B51']

# Load data
df = pd.read_csv('vipkadr_candidates.csv')

print(f"Analyzing {len(df)} job postings...")
print("Generating business intelligence charts...\n")

# ============================================================================
# DATA PREPROCESSING
# ============================================================================

def extract_salary_value(salary_str):
    """Extract numeric salary values from string format"""
    if pd.isna(salary_str):
        return None

    salary_str = str(salary_str).replace('AZN', '').strip()

    if '-' in salary_str:
        # Range like "700-1000"
        parts = salary_str.split('-')
        try:
            return (float(parts[0]) + float(parts[1])) / 2
        except:
            return None
    else:
        # Single value like "600"
        try:
            return float(salary_str)
        except:
            return None

df['salary_numeric'] = df['salary'].apply(extract_salary_value)
df['added_date'] = pd.to_datetime(df['added_date'], format='%d %b %Y', errors='coerce')
df['end_date'] = pd.to_datetime(df['end_date'], format='%d %b %Y', errors='coerce')
df['posting_duration'] = (df['end_date'] - df['added_date']).dt.days

# ============================================================================
# CHART 1: TOP HIRING COMPANIES
# ============================================================================

print("1. Analyzing top hiring companies...")
fig, ax = plt.subplots(figsize=(12, 8))

top_companies = df['company'].value_counts().head(15)
bars = ax.barh(range(len(top_companies)), top_companies.values, color=colors[0])
ax.set_yticks(range(len(top_companies)))
ax.set_yticklabels(top_companies.index, fontsize=10)
ax.set_xlabel('Number of Job Postings', fontsize=12, fontweight='bold')
ax.set_title('Top 15 Most Active Hiring Companies', fontsize=14, fontweight='bold', pad=20)
ax.invert_yaxis()

# Add value labels
for i, (bar, val) in enumerate(zip(bars, top_companies.values)):
    ax.text(val + 0.5, i, str(val), va='center', fontweight='bold')

plt.tight_layout()
plt.savefig('charts/01_top_hiring_companies.png', dpi=300, bbox_inches='tight')
plt.close()

# ============================================================================
# CHART 2: SALARY DISTRIBUTION
# ============================================================================

print("2. Analyzing salary distribution...")
fig, ax = plt.subplots(figsize=(12, 7))

salary_data = df[df['salary_numeric'].notna()]['salary_numeric']
bins = [0, 500, 600, 700, 800, 900, 1000, 1200, 1500, 2000]
counts, edges, patches = ax.hist(salary_data, bins=bins, edgecolor='black', color=colors[1], alpha=0.8)

ax.set_xlabel('Salary Range (AZN)', fontsize=12, fontweight='bold')
ax.set_ylabel('Number of Job Postings', fontsize=12, fontweight='bold')
ax.set_title('Salary Distribution Across Job Market', fontsize=14, fontweight='bold', pad=20)

# Add value labels on bars
for count, edge, patch in zip(counts, edges, patches):
    if count > 0:
        height = patch.get_height()
        ax.text(patch.get_x() + patch.get_width()/2., height,
                f'{int(count)}',
                ha='center', va='bottom', fontweight='bold')

ax.grid(axis='y', alpha=0.3)
plt.tight_layout()
plt.savefig('charts/02_salary_distribution.png', dpi=300, bbox_inches='tight')
plt.close()

# ============================================================================
# CHART 3: TOP JOB ROLES IN DEMAND
# ============================================================================

print("3. Identifying most demanded job roles...")
fig, ax = plt.subplots(figsize=(12, 8))

top_titles = df['title'].value_counts().head(15)
bars = ax.barh(range(len(top_titles)), top_titles.values, color=colors[2])
ax.set_yticks(range(len(top_titles)))
ax.set_yticklabels(top_titles.index, fontsize=10)
ax.set_xlabel('Number of Openings', fontsize=12, fontweight='bold')
ax.set_title('Top 15 Most In-Demand Job Roles', fontsize=14, fontweight='bold', pad=20)
ax.invert_yaxis()

for i, (bar, val) in enumerate(zip(bars, top_titles.values)):
    ax.text(val + 0.3, i, str(val), va='center', fontweight='bold')

plt.tight_layout()
plt.savefig('charts/03_top_job_roles.png', dpi=300, bbox_inches='tight')
plt.close()

# ============================================================================
# CHART 4: EXPERIENCE REQUIREMENTS
# ============================================================================

print("4. Analyzing experience requirements...")
fig, ax = plt.subplots(figsize=(12, 7))

exp_counts = df['experience'].value_counts().head(10)
bars = ax.bar(range(len(exp_counts)), exp_counts.values, color=colors[3], edgecolor='black', alpha=0.8)
ax.set_xticks(range(len(exp_counts)))
ax.set_xticklabels(exp_counts.index, rotation=45, ha='right', fontsize=10)
ax.set_ylabel('Number of Job Postings', fontsize=12, fontweight='bold')
ax.set_title('Experience Level Requirements', fontsize=14, fontweight='bold', pad=20)

for bar, val in zip(bars, exp_counts.values):
    height = bar.get_height()
    ax.text(bar.get_x() + bar.get_width()/2., height,
            f'{int(val)}',
            ha='center', va='bottom', fontweight='bold')

ax.grid(axis='y', alpha=0.3)
plt.tight_layout()
plt.savefig('charts/04_experience_requirements.png', dpi=300, bbox_inches='tight')
plt.close()

# ============================================================================
# CHART 5: AVERAGE SALARY BY EXPERIENCE LEVEL
# ============================================================================

print("5. Calculating salary by experience level...")
fig, ax = plt.subplots(figsize=(12, 7))

salary_by_exp = df.groupby('experience')['salary_numeric'].mean().sort_values(ascending=False).head(10)
bars = ax.bar(range(len(salary_by_exp)), salary_by_exp.values, color=colors[4], edgecolor='black', alpha=0.8)
ax.set_xticks(range(len(salary_by_exp)))
ax.set_xticklabels(salary_by_exp.index, rotation=45, ha='right', fontsize=10)
ax.set_ylabel('Average Salary (AZN)', fontsize=12, fontweight='bold')
ax.set_title('Average Salary by Experience Level', fontsize=14, fontweight='bold', pad=20)

for bar, val in zip(bars, salary_by_exp.values):
    height = bar.get_height()
    ax.text(bar.get_x() + bar.get_width()/2., height,
            f'{int(val)}',
            ha='center', va='bottom', fontweight='bold')

ax.grid(axis='y', alpha=0.3)
plt.tight_layout()
plt.savefig('charts/05_salary_by_experience.png', dpi=300, bbox_inches='tight')
plt.close()

# ============================================================================
# CHART 6: WORK TYPE DISTRIBUTION
# ============================================================================

print("6. Analyzing work type preferences...")
fig, ax = plt.subplots(figsize=(10, 7))

work_type_counts = df['work_type'].value_counts()
bars = ax.bar(range(len(work_type_counts)), work_type_counts.values,
              color=colors[:len(work_type_counts)], edgecolor='black', alpha=0.8)
ax.set_xticks(range(len(work_type_counts)))
ax.set_xticklabels(work_type_counts.index, fontsize=11, fontweight='bold')
ax.set_ylabel('Number of Job Postings', fontsize=12, fontweight='bold')
ax.set_title('Work Type Distribution in Job Market', fontsize=14, fontweight='bold', pad=20)

for bar, val in zip(bars, work_type_counts.values):
    height = bar.get_height()
    ax.text(bar.get_x() + bar.get_width()/2., height,
            f'{int(val)}',
            ha='center', va='bottom', fontweight='bold', fontsize=11)

ax.grid(axis='y', alpha=0.3)
plt.tight_layout()
plt.savefig('charts/06_work_type_distribution.png', dpi=300, bbox_inches='tight')
plt.close()

# ============================================================================
# CHART 7: JOB POSTING VIEWS ANALYSIS
# ============================================================================

print("7. Analyzing job posting performance...")
fig, ax = plt.subplots(figsize=(12, 7))

# Group views into ranges
view_ranges = pd.cut(df['views'], bins=[0, 100, 200, 300, 400, 500, 1000],
                     labels=['0-100', '101-200', '201-300', '301-400', '401-500', '500+'])
view_counts = view_ranges.value_counts().sort_index()

bars = ax.bar(range(len(view_counts)), view_counts.values, color=colors[0], edgecolor='black', alpha=0.8)
ax.set_xticks(range(len(view_counts)))
ax.set_xticklabels(view_counts.index, fontsize=11)
ax.set_ylabel('Number of Job Postings', fontsize=12, fontweight='bold')
ax.set_xlabel('View Count Range', fontsize=12, fontweight='bold')
ax.set_title('Job Posting Visibility Performance', fontsize=14, fontweight='bold', pad=20)

for bar, val in zip(bars, view_counts.values):
    height = bar.get_height()
    ax.text(bar.get_x() + bar.get_width()/2., height,
            f'{int(val)}',
            ha='center', va='bottom', fontweight='bold')

ax.grid(axis='y', alpha=0.3)
plt.tight_layout()
plt.savefig('charts/07_job_posting_views.png', dpi=300, bbox_inches='tight')
plt.close()

# ============================================================================
# CHART 8: GENDER REQUIREMENTS ANALYSIS
# ============================================================================

print("8. Analyzing gender requirements...")
fig, ax = plt.subplots(figsize=(10, 7))

gender_counts = df['gender'].value_counts()
bars = ax.bar(range(len(gender_counts)), gender_counts.values,
              color=colors[:len(gender_counts)], edgecolor='black', alpha=0.8)
ax.set_xticks(range(len(gender_counts)))
ax.set_xticklabels(gender_counts.index, fontsize=11, fontweight='bold')
ax.set_ylabel('Number of Job Postings', fontsize=12, fontweight='bold')
ax.set_title('Gender Requirements in Job Postings', fontsize=14, fontweight='bold', pad=20)

for bar, val in zip(bars, gender_counts.values):
    height = bar.get_height()
    ax.text(bar.get_x() + bar.get_width()/2., height,
            f'{int(val)}\n({val/len(df)*100:.1f}%)',
            ha='center', va='bottom', fontweight='bold', fontsize=10)

ax.grid(axis='y', alpha=0.3)
plt.tight_layout()
plt.savefig('charts/08_gender_requirements.png', dpi=300, bbox_inches='tight')
plt.close()

# ============================================================================
# CHART 9: MONTHLY JOB POSTING TRENDS
# ============================================================================

print("9. Analyzing temporal posting trends...")
fig, ax = plt.subplots(figsize=(14, 7))

df_valid_dates = df[df['added_date'].notna()].copy()
df_valid_dates['month_year'] = df_valid_dates['added_date'].dt.to_period('M')
monthly_posts = df_valid_dates['month_year'].value_counts().sort_index()

# Convert to datetime for plotting
months = [pd.Timestamp(str(m)) for m in monthly_posts.index]
ax.plot(months, monthly_posts.values, marker='o', linewidth=2.5, markersize=8, color=colors[1])
ax.fill_between(months, monthly_posts.values, alpha=0.3, color=colors[1])

ax.set_xlabel('Month', fontsize=12, fontweight='bold')
ax.set_ylabel('Number of Job Postings', fontsize=12, fontweight='bold')
ax.set_title('Job Posting Activity Over Time', fontsize=14, fontweight='bold', pad=20)
ax.grid(True, alpha=0.3)

# Rotate x-axis labels
plt.xticks(rotation=45, ha='right')

# Add value labels on points
for month, val in zip(months, monthly_posts.values):
    ax.text(month, val + 1, str(val), ha='center', va='bottom', fontsize=9, fontweight='bold')

plt.tight_layout()
plt.savefig('charts/09_monthly_posting_trends.png', dpi=300, bbox_inches='tight')
plt.close()

# ============================================================================
# CHART 10: TOP ROLES BY AVERAGE SALARY
# ============================================================================

print("10. Identifying highest paying roles...")
fig, ax = plt.subplots(figsize=(12, 8))

role_salary = df.groupby('title')['salary_numeric'].agg(['mean', 'count'])
role_salary = role_salary[role_salary['count'] >= 3]  # At least 3 postings
top_paying_roles = role_salary.nlargest(15, 'mean')

bars = ax.barh(range(len(top_paying_roles)), top_paying_roles['mean'].values, color=colors[5])
ax.set_yticks(range(len(top_paying_roles)))
ax.set_yticklabels(top_paying_roles.index, fontsize=10)
ax.set_xlabel('Average Salary (AZN)', fontsize=12, fontweight='bold')
ax.set_title('Top 15 Highest Paying Job Roles', fontsize=14, fontweight='bold', pad=20)
ax.invert_yaxis()

for i, (bar, val) in enumerate(zip(bars, top_paying_roles['mean'].values)):
    ax.text(val + 10, i, f'{int(val)} AZN', va='center', fontweight='bold')

plt.tight_layout()
plt.savefig('charts/10_highest_paying_roles.png', dpi=300, bbox_inches='tight')
plt.close()

# ============================================================================
# CHART 11: SALARY VS VIEWS CORRELATION
# ============================================================================

print("11. Analyzing relationship between salary and visibility...")
fig, ax = plt.subplots(figsize=(12, 7))

df_clean = df[(df['salary_numeric'].notna()) & (df['views'] > 0)].copy()
ax.scatter(df_clean['salary_numeric'], df_clean['views'], alpha=0.5, s=50, color=colors[3])

# Add trend line
z = np.polyfit(df_clean['salary_numeric'], df_clean['views'], 1)
p = np.poly1d(z)
ax.plot(df_clean['salary_numeric'].sort_values(),
        p(df_clean['salary_numeric'].sort_values()),
        "r--", linewidth=2, label='Trend Line')

ax.set_xlabel('Salary (AZN)', fontsize=12, fontweight='bold')
ax.set_ylabel('Number of Views', fontsize=12, fontweight='bold')
ax.set_title('Salary vs Job Posting Visibility', fontsize=14, fontweight='bold', pad=20)
ax.legend()
ax.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig('charts/11_salary_vs_views.png', dpi=300, bbox_inches='tight')
plt.close()

# ============================================================================
# CHART 12: POSTING DURATION ANALYSIS
# ============================================================================

print("12. Analyzing job posting duration...")
fig, ax = plt.subplots(figsize=(12, 7))

duration_data = df[df['posting_duration'].notna() & (df['posting_duration'] > 0)]['posting_duration']
bins = [0, 15, 30, 45, 60, 90, 120, 365]
counts, edges, patches = ax.hist(duration_data, bins=bins, edgecolor='black', color=colors[4], alpha=0.8)

ax.set_xlabel('Posting Duration (Days)', fontsize=12, fontweight='bold')
ax.set_ylabel('Number of Job Postings', fontsize=12, fontweight='bold')
ax.set_title('How Long Jobs Stay Active on Platform', fontsize=14, fontweight='bold', pad=20)

for count, edge, patch in zip(counts, edges, patches):
    if count > 0:
        height = patch.get_height()
        ax.text(patch.get_x() + patch.get_width()/2., height,
                f'{int(count)}',
                ha='center', va='bottom', fontweight='bold')

ax.grid(axis='y', alpha=0.3)
plt.tight_layout()
plt.savefig('charts/12_posting_duration.png', dpi=300, bbox_inches='tight')
plt.close()

# ============================================================================
# GENERATE SUMMARY STATISTICS
# ============================================================================

print("\n" + "="*70)
print("BUSINESS INTELLIGENCE SUMMARY")
print("="*70)

print(f"\nDataset Overview:")
print(f"  Total Job Postings: {len(df)}")
print(f"  Unique Companies: {df['company'].nunique()}")
print(f"  Unique Job Titles: {df['title'].nunique()}")
print(f"  Date Range: {df['added_date'].min()} to {df['added_date'].max()}")

print(f"\nSalary Insights:")
print(f"  Average Salary: {df['salary_numeric'].mean():.0f} AZN")
print(f"  Median Salary: {df['salary_numeric'].median():.0f} AZN")
print(f"  Min Salary: {df['salary_numeric'].min():.0f} AZN")
print(f"  Max Salary: {df['salary_numeric'].max():.0f} AZN")

print(f"\nEngagement Metrics:")
print(f"  Average Views per Posting: {df['views'].mean():.0f}")
print(f"  Median Views per Posting: {df['views'].median():.0f}")
print(f"  Most Viewed Posting: {df['views'].max()} views")

print(f"\nTop 3 Hiring Companies:")
for i, (company, count) in enumerate(df['company'].value_counts().head(3).items(), 1):
    print(f"  {i}. {company}: {count} postings")

print(f"\nTop 3 In-Demand Roles:")
for i, (title, count) in enumerate(df['title'].value_counts().head(3).items(), 1):
    print(f"  {i}. {title}: {count} openings")

print(f"\nMarket Composition:")
print(f"  Full-time positions: {(df['work_type']=='Tam İş saatı').sum()} ({(df['work_type']=='Tam İş saatı').sum()/len(df)*100:.1f}%)")
print(f"  Gender-neutral postings: {(df['gender']=='Fərq etmir').sum()} ({(df['gender']=='Fərq etmir').sum()/len(df)*100:.1f}%)")

print("\n" + "="*70)
print("All charts successfully generated in 'charts/' directory!")
print("="*70)
