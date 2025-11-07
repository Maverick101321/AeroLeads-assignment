import pandas as pd
import os

# Read profiles.csv
if os.path.exists("profiles.csv"):
    df = pd.read_csv("profiles.csv")
    
    # Row count
    row_count = len(df)
    print(f"Row count: {row_count}")

    # % rows with non-empty full_name
    non_empty_name_count = df['full_name'].notna() & (df['full_name'].str.strip() != '')
    pct_with_name = (non_empty_name_count.sum() / row_count * 100) if row_count > 0 else 0
    print(f"% rows with non-empty full_name: {pct_with_name:.1f}%")

    # Avg #skills (split by ;)
    df['skill_count'] = df['skills'].apply(lambda x: len(str(x).split(';')) if pd.notna(x) and str(x).strip() else 0)
    avg_skills = df['skill_count'].mean()
    print(f"Avg #skills: {avg_skills:.1f}")

else:
    print("profiles.csv not found")

# Read errors.csv
if os.path.exists("errors.csv"):
    # Count of errors in errors.csv
    error_df = pd.read_csv("errors.csv")
    error_count = len(error_df)
    print(f"Count of errors: {error_count}")
else:
    print("errors.csv not found")