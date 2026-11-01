"""
Task 1: Data Cleaning Pipeline
==============================
Project: Internship_Data_Analytics
Script:  Task_1_Data_Cleaning/src/cleaning.py

Description:
    Standardized, reproducible data cleaning script for cafe sales transactions.
    Standardizes corrupted sentinel tokens, casts native physical data types,
    performs mathematically validated numerical recovery (Quantity * Price = Total),
    tracks data provenance using boolean imputation flags, enforces domain validation,
    and produces a clean dataset without fabricating categorical data or deleting rows.
"""

import os
import sys
from typing import Dict, Tuple, Set
import pandas as pd
import numpy as np


# Shared sentinel tokens representing missing or corrupted text values
SENTINEL_TOKENS: Set[str] = {'ERROR', 'UNKNOWN', 'NAN', 'NONE', 'NULL', 'NA', '?'}

# Recognized fixed menu pricing domain for validation
MENU_PRICE_MAPPING: Dict[str, float] = {
    'Salad': 5.0,
    'Sandwich': 4.0,
    'Smoothie': 4.0,
    'Cake': 3.0,
    'Juice': 3.0,
    'Coffee': 2.0,
    'Tea': 1.5,
    'Cookie': 1.0
}

VALID_MENU_PRICES: Set[float] = set(MENU_PRICE_MAPPING.values())
VALID_ITEMS: Set[str] = set(MENU_PRICE_MAPPING.keys())
VALID_PAYMENT_METHODS: Set[str] = {'Cash', 'Credit Card', 'Digital Wallet'}
VALID_LOCATIONS: Set[str] = {'Takeaway', 'In-store'}


def load_raw_data(filepath: str) -> pd.DataFrame:
    """
    Load raw CSV dataset without modifying the source file.
    """
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"Source file not found at: {filepath}")
    df = pd.read_csv(filepath)
    print(f"[1/7] Raw dataset loaded successfully from: {filepath}")
    print(f"      Initial shape: {df.shape[0]:,} rows x {df.shape[1]} columns")
    return df


def standardize_missing_tokens(df: pd.DataFrame) -> pd.DataFrame:
    """
    Standardize corrupted sentinel tokens ('ERROR', 'UNKNOWN', whitespace variants)
    into standard missing values (np.nan).
    Null-safe: Preserves existing genuine nulls without coercing them to literal 'nan' strings.
    """
    df_clean = df.copy()

    for col in df_clean.columns:
        # Operate strictly on non-null values to preserve true missing values
        mask_notnull = df_clean[col].notnull()
        series_notnull = df_clean.loc[mask_notnull, col].astype(str).str.strip()
        
        # Check for sentinel error tokens or empty/whitespace-only strings
        is_sentinel = series_notnull.str.upper().isin(SENTINEL_TOKENS) | (series_notnull == '')
        
        # Assign stripped strings back, and set sentinels to np.nan
        df_clean.loc[mask_notnull, col] = series_notnull
        df_clean.loc[mask_notnull & is_sentinel, col] = np.nan

    print("[2/7] Corrupted sentinel tokens standardized to NaN (null-safe).")
    return df_clean


def convert_data_types(df: pd.DataFrame) -> pd.DataFrame:
    """
    Cast columns to appropriate physical types:
    - Quantity: numeric float (temporary for recovery, later nullable Int64)
    - Price Per Unit: float64
    - Total Spent: float64
    - Transaction Date: datetime64[ns]
    - Categorical variables: string/object with NaN preserved
    """
    df_typed = df.copy()

    # Numeric conversion with coercion (invalid values become NaN)
    df_typed['Quantity'] = pd.to_numeric(df_typed['Quantity'], errors='coerce')
    df_typed['Price Per Unit'] = pd.to_numeric(df_typed['Price Per Unit'], errors='coerce')
    df_typed['Total Spent'] = pd.to_numeric(df_typed['Total Spent'], errors='coerce')

    # Temporal conversion
    df_typed['Transaction Date'] = pd.to_datetime(df_typed['Transaction Date'], format='%Y-%m-%d', errors='coerce')

    print("[3/7] Physical data types converted (Numeric and Datetime formats applied).")
    return df_typed


def recover_numerical_values(df: pd.DataFrame) -> Tuple[pd.DataFrame, Dict[str, int]]:
    """
    Recover missing numerical values strictly using the mathematical constraint:
        Quantity * Price Per Unit = Total Spent

    Rules:
    - Only infer a value when the other two values in the triad are valid and non-null.
    - Validate every inferred value against domain constraints:
        * Quantity: must be a positive integer in [1, 5]
        * Price Per Unit: must belong to the valid menu price domain {1.0, 1.5, 2.0, 3.0, 4.0, 5.0}
        * Total Spent: must be greater than 0 and equal Quantity * Price Per Unit
    - Never overwrite observed, legitimate values.
    - Set explicit boolean provenance flags to track data lineage.
    """
    df_rec = df.copy()

    # Initialize provenance tracking flags
    df_rec['is_quantity_imputed'] = False
    df_rec['is_price_imputed'] = False
    df_rec['is_total_imputed'] = False

    recovery_stats = {'quantity': 0, 'price': 0, 'total': 0}

    # 1. Recover Quantity: Total Spent / Price Per Unit
    # Condition: Quantity is missing; Price Per Unit and Total Spent are valid
    q_mask = df_rec['Quantity'].isnull() & df_rec['Price Per Unit'].notnull() & df_rec['Total Spent'].notnull()
    inferred_q = df_rec.loc[q_mask, 'Total Spent'] / df_rec.loc[q_mask, 'Price Per Unit']
    # Validation: must evaluate to integer within domain 1 to 5
    valid_q = (inferred_q % 1 == 0) & (inferred_q >= 1) & (inferred_q <= 5)
    valid_q_idx = q_mask[q_mask].index[valid_q]
    df_rec.loc[valid_q_idx, 'Quantity'] = inferred_q[valid_q]
    df_rec.loc[valid_q_idx, 'is_quantity_imputed'] = True
    recovery_stats['quantity'] = len(valid_q_idx)

    # 2. Recover Total Spent: Quantity * Price Per Unit
    # Condition: Total Spent is missing; Quantity and Price Per Unit are valid
    t_mask = df_rec['Total Spent'].isnull() & df_rec['Quantity'].notnull() & df_rec['Price Per Unit'].notnull()
    inferred_t = df_rec.loc[t_mask, 'Quantity'] * df_rec.loc[t_mask, 'Price Per Unit']
    # Validation: must be strictly positive
    valid_t = inferred_t > 0
    valid_t_idx = t_mask[t_mask].index[valid_t]
    df_rec.loc[valid_t_idx, 'Total Spent'] = inferred_t[valid_t]
    df_rec.loc[valid_t_idx, 'is_total_imputed'] = True
    recovery_stats['total'] = len(valid_t_idx)

    # 3. Recover Price Per Unit: Total Spent / Quantity
    # Condition: Price Per Unit is missing; Quantity and Total Spent are valid
    p_mask = df_rec['Price Per Unit'].isnull() & df_rec['Quantity'].notnull() & df_rec['Total Spent'].notnull()
    inferred_p = df_rec.loc[p_mask, 'Total Spent'] / df_rec.loc[p_mask, 'Quantity']
    # Validation: must match one of the verified menu price points
    valid_p = inferred_p.isin(VALID_MENU_PRICES)
    valid_p_idx = p_mask[p_mask].index[valid_p]
    df_rec.loc[valid_p_idx, 'Price Per Unit'] = inferred_p[valid_p]
    df_rec.loc[valid_p_idx, 'is_price_imputed'] = True
    recovery_stats['price'] = len(valid_p_idx)

    # Convert Quantity to nullable integer Int64
    df_rec['Quantity'] = df_rec['Quantity'].astype('Int64')

    print(f"[4/7] Numerical recovery complete:")
    print(f"      - Quantities imputed  : {recovery_stats['quantity']:,}")
    print(f"      - Prices imputed      : {recovery_stats['price']:,}")
    print(f"      - Total Spent imputed : {recovery_stats['total']:,}")
    print(f"      - Total recoveries    : {sum(recovery_stats.values()):,}")

    return df_rec, recovery_stats


def validate_cleaned_data(df: pd.DataFrame) -> bool:
    """
    Perform rigorous validation checks on the cleaned dataset:
    1. Transaction ID uniqueness
    2. Quantity domain (1 to 5)
    3. Price Per Unit domain ({1.0, 1.5, 2.0, 3.0, 4.0, 5.0})
    4. Categorical Domains:
       - Item categories in {Salad, Sandwich, Smoothie, Cake, Juice, Coffee, Tea, Cookie}
       - Payment Method categories in {Cash, Credit Card, Digital Wallet}
       - Location categories in {Takeaway, In-store}
       - Cross-validation of Item vs Price Per Unit
    5. Mathematical consistency (Quantity * Price Per Unit == Total Spent)
    6. Date validation: Report valid timestamps range & explicit remaining missing counts
    """
    print("[5/7] Executing post-cleaning validation checks...")
    validation_passed = True

    # Check 1: Transaction ID uniqueness
    n_unique_id = df['Transaction ID'].nunique()
    if n_unique_id != len(df):
        print(f"  [FAIL] Transaction ID is not unique: {n_unique_id} unique out of {len(df)}")
        validation_passed = False
    else:
        print(f"  [PASS] Transaction ID Uniqueness: 100% unique ({n_unique_id:,}/{len(df):,})")

    # Check 2: Quantity domain
    valid_qty = df['Quantity'].dropna()
    qty_out_of_bounds = ((valid_qty < 1) | (valid_qty > 5)).sum()
    if qty_out_of_bounds > 0:
        print(f"  [FAIL] Quantity domain violation: {qty_out_of_bounds} entries outside [1, 5]")
        validation_passed = False
    else:
        print(f"  [PASS] Quantity Domain: 100% of non-null quantities within [1, 5] (observed: {sorted(valid_qty.unique())})")

    # Check 3: Price Per Unit domain
    valid_prices = df['Price Per Unit'].dropna()
    invalid_prices = (~valid_prices.isin(VALID_MENU_PRICES)).sum()
    if invalid_prices > 0:
        print(f"  [FAIL] Price Per Unit domain violation: {invalid_prices} unmapped prices")
        validation_passed = False
    else:
        print(f"  [PASS] Price Domain: 100% of non-null prices belong to verified menu prices {sorted(VALID_MENU_PRICES)}")

    # Check 4a: Item Category Validation
    valid_items = df['Item'].dropna()
    invalid_items = valid_items[~valid_items.isin(VALID_ITEMS)]
    if len(invalid_items) > 0:
        print(f"  [FAIL] Item Category violation: {len(invalid_items)} unexpected items ({invalid_items.unique()})")
        validation_passed = False
    else:
        print(f"  [PASS] Item Domain: 100% of non-null items belong to expected categories ({len(valid_items):,} records)")

    # Check 4b: Payment Method Category Validation
    valid_pm = df['Payment Method'].dropna()
    invalid_pm = valid_pm[~valid_pm.isin(VALID_PAYMENT_METHODS)]
    if len(invalid_pm) > 0:
        print(f"  [FAIL] Payment Method violation: {len(invalid_pm)} unexpected values ({invalid_pm.unique()})")
        validation_passed = False
    else:
        print(f"  [PASS] Payment Method Domain: 100% of non-null payment methods valid ({len(valid_pm):,} records)")

    # Check 4c: Location Category Validation
    valid_loc = df['Location'].dropna()
    invalid_loc = valid_loc[~valid_loc.isin(VALID_LOCATIONS)]
    if len(invalid_loc) > 0:
        print(f"  [FAIL] Location violation: {len(invalid_loc)} unexpected values ({invalid_loc.unique()})")
        validation_passed = False
    else:
        print(f"  [PASS] Location Domain: 100% of non-null locations valid ({len(valid_loc):,} records)")

    # Check 4d: Cross-validation of Item vs Price Per Unit
    known_item_price = df['Item'].notnull() & df['Price Per Unit'].notnull()
    item_price_mismatches = 0
    for item, expected_price in MENU_PRICE_MAPPING.items():
        subset_mismatch = (df['Item'] == item) & df['Price Per Unit'].notnull() & (df['Price Per Unit'] != expected_price)
        item_price_mismatches += subset_mismatch.sum()
    if item_price_mismatches > 0:
        print(f"  [FAIL] Item-Price Mapping violation: {item_price_mismatches} records contradict menu prices")
        validation_passed = False
    else:
        print(f"  [PASS] Item-Price Alignment: 100% match between known items and fixed unit prices")

    # Check 5: Mathematical consistency
    full_numeric_mask = df['Quantity'].notnull() & df['Price Per Unit'].notnull() & df['Total Spent'].notnull()
    math_diff = ((df.loc[full_numeric_mask, 'Quantity'] * df.loc[full_numeric_mask, 'Price Per Unit']) - df.loc[full_numeric_mask, 'Total Spent']).abs()
    discrepancy_count = (math_diff > 1e-4).sum()
    if discrepancy_count > 0:
        print(f"  [FAIL] Mathematical discrepancy: {discrepancy_count} rows violate Qty * Price = Total")
        validation_passed = False
    else:
        print(f"  [PASS] Mathematical Determinism: 100% consistent across all {full_numeric_mask.sum():,} complete rows")

    # Check 6: Date validation
    valid_dates = df['Transaction Date'].dropna()
    missing_dates_count = df['Transaction Date'].isnull().sum()
    missing_dates_pct = (missing_dates_count / len(df)) * 100
    print(f"  [PASS] Date Parsing: {len(valid_dates):,} valid timestamps spanning {valid_dates.min().strftime('%Y-%m-%d')} to {valid_dates.max().strftime('%Y-%m-%d')} | Remaining Missing: {missing_dates_count:,} ({missing_dates_pct:.2f}%)")

    if not validation_passed:
        raise ValueError("Dataset validation failed. Please inspect logged errors.")

    return True


def print_cleaning_summary(df_raw: pd.DataFrame, df_cleaned: pd.DataFrame, recovery_stats: Dict[str, int]) -> None:
    """
    Print an empirical, comprehensive before-and-after cleaning comparison summary.
    All counts and percentages are derived dynamically using identical sentinel definitions.
    """
    print("\n" + "=" * 80)
    print("               DATA CLEANING BEFORE-AND-AFTER SUMMARY")
    print("=" * 80)

    summary_rows = []
    for col in df_raw.columns:
        # Before metrics: raw NaNs + string sentinels / empty strings (identical to cleaning logic)
        raw_nan = df_raw[col].isnull()
        raw_notnull = df_raw.loc[~raw_nan, col].astype(str).str.strip()
        raw_sentinel = raw_notnull.str.upper().isin(SENTINEL_TOKENS) | (raw_notnull == '')
        raw_total_dirty = raw_nan.sum() + raw_sentinel.sum()
        raw_dirty_pct = (raw_total_dirty / len(df_raw)) * 100

        # After metrics: genuine remaining NaNs
        clean_nan = df_cleaned[col].isnull().sum()
        clean_dirty_pct = (clean_nan / len(df_cleaned)) * 100
        recovered = raw_total_dirty - clean_nan

        summary_rows.append({
            'Column': col,
            'Raw Dirty (NaN+Tokens)': f"{raw_total_dirty:,} ({raw_dirty_pct:.1f}%)",
            'Cleaned Missing': f"{clean_nan:,} ({clean_dirty_pct:.1f}%)",
            'Recovered / Fixed': f"{recovered:,}" if recovered > 0 else "0",
            'Clean Data Type': str(df_cleaned[col].dtype)
        })

    summary_df = pd.DataFrame(summary_rows)
    print(summary_df.to_string(index=False))
    print("=" * 80)

    # Dynamic evaluation of lineage and solved metrics
    solved_count = ((df_cleaned['Quantity'].notnull()) & (df_cleaned['Price Per Unit'].notnull()) & (df_cleaned['Total Spent'].notnull())).sum()
    solved_pct = (solved_count / len(df_cleaned)) * 100

    print("\nPROVENANCE FLAGS (DATA LINEAGE TRACKING):")
    print(f"  - is_quantity_imputed : {df_cleaned['is_quantity_imputed'].sum():,} rows ({df_cleaned['is_quantity_imputed'].mean()*100:.2f}%)")
    print(f"  - is_price_imputed    : {df_cleaned['is_price_imputed'].sum():,} rows ({df_cleaned['is_price_imputed'].mean()*100:.2f}%)")
    print(f"  - is_total_imputed    : {df_cleaned['is_total_imputed'].sum():,} rows ({df_cleaned['is_total_imputed'].mean()*100:.2f}%)")
    print(f"  - Fully Solved Rows   : {solved_count:,} out of {len(df_cleaned):,} ({solved_pct:.2f}%)")
    print("=" * 80 + "\n")


def save_cleaned_data(df: pd.DataFrame, output_path: str) -> None:
    """
    Save the cleaned dataset to CSV, ensuring parent directories exist.
    """
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    df.to_csv(output_path, index=False)
    file_size_bytes = os.path.getsize(output_path)
    print(f"[6/7] Cleaned dataset successfully exported to: {output_path}")
    print(f"      File size: {file_size_bytes:,} bytes (~{file_size_bytes / 1024:.2f} KB)")


def run_pipeline(input_path: str, output_path: str) -> pd.DataFrame:
    """
    Orchestrate the end-to-end data cleaning pipeline.
    """
    print("\n" + "#" * 80)
    print("       STARTING DATA CLEANING PIPELINE: TASK 1 (CAFE SALES)")
    print("#" * 80 + "\n")

    # 1. Load raw data safely (read-only)
    df_raw = load_raw_data(input_path)

    # 2. Standardize corrupted sentinel tokens (null-safe)
    df_standardized = standardize_missing_tokens(df_raw)

    # 3. Convert physical types
    df_typed = convert_data_types(df_standardized)

    # 4. Perform validated numerical recovery & attach provenance flags
    df_recovered, recovery_stats = recover_numerical_values(df_typed)

    # 5. Validate dataset integrity (including categorical domains & date transparency)
    validate_cleaned_data(df_recovered)

    # 6. Save cleaned dataset
    save_cleaned_data(df_recovered, output_path)

    # 7. Print comprehensive summary with dynamic percentages
    print("[7/7] Generating final audit report...")
    print_cleaning_summary(df_raw, df_recovered, recovery_stats)

    print("#" * 80)
    print("       DATA CLEANING PIPELINE COMPLETED SUCCESSFULLY")
    print("#" * 80 + "\n")

    return df_recovered


def main():
    # Standard project paths relative to repository root
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    input_csv = os.path.join(base_dir, 'data', 'raw', 'extracted', 'dirty_cafe_sales.csv')
    output_csv = os.path.join(base_dir, 'data', 'cleaned', 'cleaned_cafe_sales.csv')

    # Allow custom CLI arguments if provided
    if len(sys.argv) > 1:
        input_csv = sys.argv[1]
    if len(sys.argv) > 2:
        output_csv = sys.argv[2]

    run_pipeline(input_csv, output_csv)


if __name__ == '__main__':
    main()
