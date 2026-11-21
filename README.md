# Customer Segmentation Analysis (Interactive Console Project)

## Files
- `customer_data_500.csv` — a 500-customer subset selected from the uploaded Kaggle `marketing_campaign` dataset.
- `customer_segmentation.py` — interactive Python IDLE/console application.

## Requirements
- Python 3
- pandas
- numpy

Install dependencies if needed:
```bash
python -m pip install pandas numpy
```

## Run
Keep both files in the same folder, open `customer_segmentation.py` in Python IDLE, and choose **Run > Run Module** (F5). Or run:
```bash
python customer_segmentation.py
```

## Interactive features
1. Search customer by ID
2. Search using any available dataset field
3. Filter customers by a numeric range
4. Customer spending analysis
5. Customer segmentation by relative spending level
6. View dataset information
7. Exit

No graphs or visualizations are used. Results appear in the console only.

## Dataset notes
The uploaded Numbers workbook was converted to CSV for use in Python. Its source table contained 2,240 rows and 27 original columns. This project selects 500 distinct customer IDs (random sample, `random_state=42`) and retains the original fields. It adds `Total_Spending` and `Total_Purchases` as calculated fields. The 500-row subset has 500 unique IDs and 6 missing `Income` values; missing values are shown as unavailable rather than fabricated.
