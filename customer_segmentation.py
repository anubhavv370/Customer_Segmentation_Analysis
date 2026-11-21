"""
CUSTOMER SEGMENTATION ANALYSIS - INTERACTIVE CONSOLE APPLICATION
Dataset: customer_data_500.csv
Requirements: Python 3, pandas, numpy
Run in Python IDLE or a terminal. No graphs or visualizations are used.
"""

from pathlib import Path
import pandas as pd
import numpy as np

DATA_FILE = Path(__file__).with_name("customer_data_500.csv")

SPENDING_COLUMNS = [
    "MntWines", "MntFruits", "MntMeatProducts",
    "MntFishProducts", "MntSweetProducts", "MntGoldProds"
]
PURCHASE_COLUMNS = [
    "NumDealsPurchases", "NumWebPurchases",
    "NumCatalogPurchases", "NumStorePurchases"
]
CAMPAIGN_COLUMNS = [
    "AcceptedCmp1", "AcceptedCmp2", "AcceptedCmp3",
    "AcceptedCmp4", "AcceptedCmp5", "Response"
]


def load_data():
    """Load the 500-row CSV and prepare calculated customer fields."""
    if not DATA_FILE.exists():
        print("Dataset file not found:", DATA_FILE.name)
        print("Keep customer_data_500.csv in the same folder as this Python file.")
        return None

    try:
        data = pd.read_csv(DATA_FILE)
    except Exception as error:
        print("Could not read the dataset:", error)
        return None

    if "ID" not in data.columns:
        print("The dataset does not contain the expected customer ID column 'ID'.")
        return None

    data = data.drop_duplicates(subset="ID", keep="first").copy()

    # Recalculate these fields if the source CSV does not already contain them.
    spend_cols = [c for c in SPENDING_COLUMNS if c in data.columns]
    purchase_cols = [c for c in PURCHASE_COLUMNS if c in data.columns]
    if spend_cols:
        data["Total_Spending"] = data[spend_cols].apply(
            pd.to_numeric, errors="coerce"
        ).fillna(0).sum(axis=1)
    if purchase_cols:
        data["Total_Purchases"] = data[purchase_cols].apply(
            pd.to_numeric, errors="coerce"
        ).fillna(0).sum(axis=1)

    # Assign relative spending segments from the selected 500 customers.
    if "Total_Spending" in data.columns and len(data) >= 3:
        low_cut = data["Total_Spending"].quantile(1 / 3)
        high_cut = data["Total_Spending"].quantile(2 / 3)
        data["Customer_Segment"] = np.select(
            [data["Total_Spending"] <= low_cut,
             data["Total_Spending"] >= high_cut],
            ["Low Spending", "High Spending"],
            default="Medium Spending"
        )
    return data


def print_line():
    print("-" * 65)


def ask_number(message, allow_blank=False):
    while True:
        value = input(message).strip()
        if allow_blank and value == "":
            return None
        try:
            return float(value)
        except ValueError:
            print("Please enter a valid number.")


def show_customer(data, customer_id):
    matches = data[data["ID"].astype(str).str.strip() == str(customer_id).strip()]
    if matches.empty:
        print("\nCustomer ID not found in this 500-customer dataset.")
        return

    customer = matches.iloc[0]
    print_line()
    print("                 CUSTOMER PROFILE")
    print_line()

    groups = {
        "CUSTOMER INFORMATION": ["ID", "Year_Birth", "Income", "Kidhome", "Teenhome", "Dt_Customer", "Recency"],
        "PRODUCT SPENDING": SPENDING_COLUMNS + ["Total_Spending"],
        "PURCHASE CHANNELS": PURCHASE_COLUMNS + ["Total_Purchases", "NumWebVisitsMonth"],
        "CAMPAIGN AND FEEDBACK": CAMPAIGN_COLUMNS + ["Complain"]
    }
    shown = set()
    for heading, columns in groups.items():
        available = [c for c in columns if c in data.columns and c not in shown]
        if available:
            print("\n" + heading)
            for column in available:
                value = customer[column]
                if pd.isna(value):
                    value = "Not available"
                print(f"{column:25}: {value}")
                shown.add(column)

    other_columns = [c for c in data.columns if c not in shown and c != "Customer_Segment"]
    if other_columns:
        print("\nOTHER AVAILABLE INFORMATION")
        for column in other_columns:
            value = customer[column]
            if pd.isna(value):
                value = "Not available"
            print(f"{column:25}: {value}")

    if "Customer_Segment" in data.columns:
        print("\nCUSTOMER SEGMENT")
        print("Customer_Segment       :", customer["Customer_Segment"])
    print_line()


def search_by_id(data):
    customer_id = input("Enter Customer ID: ").strip()
    if customer_id:
        show_customer(data, customer_id)
    else:
        print("Customer ID cannot be empty.")


def search_any_column(data):
    print("\nAvailable columns:")
    for number, column in enumerate(data.columns, start=1):
        print(f"{number:2}. {column}")
    choice = input("Enter column name or number: ").strip()
    if choice.isdigit() and 1 <= int(choice) <= len(data.columns):
        column = data.columns[int(choice) - 1]
    elif choice in data.columns:
        column = choice
    else:
        print("Column not found.")
        return

    term = input(f"Enter value to search in '{column}': ").strip()
    if not term:
        print("Search value cannot be empty.")
        return
    matches = data[data[column].astype(str).str.contains(term, case=False, na=False)]
    display_matches(matches)


def filter_numeric_range(data):
    numeric_columns = data.select_dtypes(include=[np.number]).columns.tolist()
    print("\nNumeric columns:")
    for number, column in enumerate(numeric_columns, start=1):
        print(f"{number:2}. {column}")
    choice = input("Choose a column by number or name: ").strip()
    if choice.isdigit() and 1 <= int(choice) <= len(numeric_columns):
        column = numeric_columns[int(choice) - 1]
    elif choice in numeric_columns:
        column = choice
    else:
        print("Numeric column not found.")
        return

    minimum = ask_number("Minimum value: ")
    maximum = ask_number("Maximum value: ")
    if minimum > maximum:
        print("Minimum cannot be greater than maximum.")
        return
    values = pd.to_numeric(data[column], errors="coerce")
    matches = data[values.between(minimum, maximum, inclusive="both")]
    display_matches(matches)


def display_matches(matches, limit=25):
    print_line()
    print("Matching customers:", len(matches))
    print_line()
    if matches.empty:
        print("No matching records found.")
        return
    preferred = [c for c in ["ID", "Year_Birth", "Income", "Total_Spending", "Total_Purchases", "Customer_Segment"] if c in matches.columns]
    if not preferred:
        preferred = list(matches.columns[:6])
    print(matches[preferred].head(limit).to_string(index=False))
    if len(matches) > limit:
        print(f"\nShowing first {limit} of {len(matches)} matches.")
        print("Use a narrower filter to reduce the results.")


def spending_analysis(data):
    if "Total_Spending" not in data.columns:
        print("Product spending columns are not available in this dataset.")
        return
    print("\n1. Find customers spending at least an amount")
    print("2. Show top spending customers")
    print("3. Find customers in a spending range")
    choice = input("Choose an option: ").strip()
    if choice == "1":
        minimum = ask_number("Minimum total spending: ")
        display_matches(data[data["Total_Spending"] >= minimum].sort_values("Total_Spending", ascending=False))
    elif choice == "2":
        count = ask_number("How many customers to display? ")
        count = max(1, min(int(count), len(data)))
        cols = [c for c in ["ID", "Total_Spending", "Total_Purchases", "Customer_Segment"] if c in data.columns]
        print(data.nlargest(count, "Total_Spending")[cols].to_string(index=False))
    elif choice == "3":
        minimum = ask_number("Minimum spending: ")
        maximum = ask_number("Maximum spending: ")
        if minimum <= maximum:
            display_matches(data[data["Total_Spending"].between(minimum, maximum)].sort_values("Total_Spending", ascending=False))
        else:
            print("Minimum cannot be greater than maximum.")
    else:
        print("Invalid option.")


def segment_analysis(data):
    if "Customer_Segment" not in data.columns:
        print("Customer spending segmentation is not available.")
        return
    print("\nCustomer segments:")
    print(data["Customer_Segment"].value_counts().to_string())
    segment = input("Enter segment name to view customers (or press Enter to return): ").strip()
    if segment:
        matches = data[data["Customer_Segment"].str.lower() == segment.lower()]
        display_matches(matches)


def dataset_information(data):
    print_line()
    print("DATASET INFORMATION")
    print_line()
    print("Customer records:", len(data))
    print("Unique customer IDs:", data["ID"].nunique())
    print("Available fields:", len(data.columns))
    print("Columns:", ", ".join(data.columns))
    print("\nMissing values by column:")
    missing = data.isna().sum()
    missing = missing[missing > 0]
    print(missing.to_string() if not missing.empty else "No missing values.")
    print_line()


def main():
    data = load_data()
    if data is None:
        return

    print("\n" + "=" * 65)
    print("             CUSTOMER SEGMENTATION ANALYSIS")
    print("=" * 65)
    print(f"Loaded {len(data)} unique customer records successfully.")

    while True:
        print("\nMAIN MENU")
        print("1. Search customer by ID")
        print("2. Search using any dataset field")
        print("3. Filter customers by a numeric range")
        print("4. Customer spending analysis")
        print("5. Customer segmentation")
        print("6. View dataset information")
        print("7. Exit")
        choice = input("\nEnter your choice (1-7): ").strip()

        if choice == "1":
            search_by_id(data)
        elif choice == "2":
            search_any_column(data)
        elif choice == "3":
            filter_numeric_range(data)
        elif choice == "4":
            spending_analysis(data)
        elif choice == "5":
            segment_analysis(data)
        elif choice == "6":
            dataset_information(data)
        elif choice == "7":
            print("Thank you for using Customer Segmentation Analysis!")
            break
        else:
            print("Invalid choice. Please select a number from 1 to 7.")


if __name__ == "__main__":
    main()
