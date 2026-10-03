import sys
import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from config import PROCESSED_DATA_PATH

def generate_10_visualizations():
    df = pd.read_csv(PROCESSED_DATA_PATH)
    
    # Professional styling setup
    sns.set_theme(style="whitegrid")
    plt.rcParams['axes.edgecolor'] = '#cccccc'
    plt.rcParams['axes.linewidth'] = 0.8
    
    os.makedirs('outputs', exist_ok=True)
    print("Generating 10 professional, clean charts...")

    num_cols = df.select_dtypes(include=['number']).columns.tolist()
    
    # Filter out high-cardinality and ID columns to keep charts readable
    cat_cols = [
        c for c in df.select_dtypes(include=['object']).columns.tolist() 
        if df[c].nunique() < 15 and 'id' not in c.lower() and 'date' not in c.lower()
    ]
    if not cat_cols:
        cat_cols = [c for c in df.select_dtypes(include=['object']).columns.tolist() if df[c].nunique() < 30]

    c1 = num_cols[0] if len(num_cols) > 0 else df.columns[0]
    c2 = num_cols[1] if len(num_cols) > 1 else df.columns[1]
    cat1 = cat_cols[0] if len(cat_cols) > 0 else df.columns[0]

    # 1. Histogram
    plt.figure(figsize=(9, 5))
    sns.histplot(df[c1], bins=25, color='#2b5c8f', kde=True, alpha=0.7)
    plt.title(f'1. Distribution of {c1}', fontsize=14, fontweight='bold', pad=15)
    plt.xlabel(c1, fontsize=12)
    plt.ylabel('Count', fontsize=12)
    plt.tight_layout()
    plt.savefig('outputs/chart_1.png', dpi=300)
    plt.close()

    # 2. Count Plot
    plt.figure(figsize=(9, 5))
    sns.countplot(x=cat1, data=df, palette='crest', order=df[cat1].value_counts().index)
    plt.title(f'2. Frequency Count by {cat1}', fontsize=14, fontweight='bold', pad=15)
    plt.xlabel(cat1, fontsize=12)
    plt.ylabel('Count', fontsize=12)
    plt.xticks(rotation=30, ha='right')
    plt.tight_layout()
    plt.savefig('outputs/chart_2.png', dpi=300)
    plt.close()

    # 3. Box Plot
    plt.figure(figsize=(9, 5))
    sns.boxplot(x=cat1, y=c1, data=df, palette='Set2')
    plt.title(f'3. Box Plot: {c1} across {cat1}', fontsize=14, fontweight='bold', pad=15)
    plt.xlabel(cat1, fontsize=12)
    plt.ylabel(c1, fontsize=12)
    plt.xticks(rotation=30, ha='right')
    plt.tight_layout()
    plt.savefig('outputs/chart_3.png', dpi=300)
    plt.close()

    # 4. Scatter Plot
    plt.figure(figsize=(9, 5))
    sns.scatterplot(x=c1, y=c2, data=df, color='#8e44ad', alpha=0.4, s=50)
    plt.title(f'4. Scatter Plot ({c1} vs {c2})', fontsize=14, fontweight='bold', pad=15)
    plt.xlabel(c1, fontsize=12)
    plt.ylabel(c2, fontsize=12)
    plt.tight_layout()
    plt.savefig('outputs/chart_4.png', dpi=300)
    plt.close()

    # 5. KDE Plot
    plt.figure(figsize=(9, 5))
    sns.kdeplot(df[c1], fill=True, color='#e67e22', alpha=0.5)
    plt.title(f'5. Density Estimation of {c1}', fontsize=14, fontweight='bold', pad=15)
    plt.xlabel(c1, fontsize=12)
    plt.ylabel('Density', fontsize=12)
    plt.tight_layout()
    plt.savefig('outputs/chart_5.png', dpi=300)
    plt.close()

    # 6. Bar Plot
    plt.figure(figsize=(9, 5))
    sns.barplot(x=cat1, y=c1, data=df, palette='pastel', errorbar=None, order=df[cat1].value_counts().index)
    plt.title(f'6. Average {c1} by {cat1}', fontsize=14, fontweight='bold', pad=15)
    plt.xlabel(cat1, fontsize=12)
    plt.ylabel(f'Mean {c1}', fontsize=12)
    plt.xticks(rotation=30, ha='right')
    plt.tight_layout()
    plt.savefig('outputs/chart_6.png', dpi=300)
    plt.close()

    # 7. Violin Plot
    plt.figure(figsize=(9, 5))
    sns.violinplot(x=cat1, y=c1, data=df, palette='Blues')
    plt.title(f'7. Violin Plot of {c1} by {cat1}', fontsize=14, fontweight='bold', pad=15)
    plt.xlabel(cat1, fontsize=12)
    plt.ylabel(c1, fontsize=12)
    plt.xticks(rotation=30, ha='right')
    plt.tight_layout()
    plt.savefig('outputs/chart_7.png', dpi=300)
    plt.close()

    # 8. Heatmap
    plt.figure(figsize=(8, 6))
    if len(num_cols) > 1:
        sns.heatmap(df[num_cols[:4]].corr(), annot=True, cmap='coolwarm', fmt='.2f', linewidths=0.5)
    plt.title('8. Correlation Heatmap', fontsize=14, fontweight='bold', pad=15)
    plt.tight_layout()
    plt.savefig('outputs/chart_8.png', dpi=300)
    plt.close()

    # 9. Line Plot
    plt.figure(figsize=(10, 5))
    sns.lineplot(data=df[c1].iloc[:50], color='#27ae60', marker='o', linewidth=2)
    plt.title(f'9. Trend Line of {c1} (First 50 records)', fontsize=14, fontweight='bold', pad=15)
    plt.xlabel('Index', fontsize=12)
    plt.ylabel(c1, fontsize=12)
    plt.tight_layout()
    plt.savefig('outputs/chart_9.png', dpi=300)
    plt.close()

    # 10. Strip Plot
    plt.figure(figsize=(9, 5))
    sns.stripplot(x=cat1, y=c1, data=df, palette='Set1', jitter=True, alpha=0.5, size=6)
    plt.title(f'10. Strip Plot of {c1} by {cat1}', fontsize=14, fontweight='bold', pad=15)
    plt.xlabel(cat1, fontsize=12)
    plt.ylabel(c1, fontsize=12)
    plt.xticks(rotation=30, ha='right')
    plt.tight_layout()
    plt.savefig('outputs/chart_10.png', dpi=300)
    plt.close()

    print("All 10 professional visualizations generated successfully!")

if __name__ == "__main__":
    generate_10_visualizations()