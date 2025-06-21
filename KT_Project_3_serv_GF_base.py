#!/usr/bin/env python
# coding: utf-8

# ### NEF Project 3

# ### Steps for execution:
# - 1) Import the Rubric which has all the matching EOM fee amounts 
# - 2) Import the EOM View dataframe, this is the base of our output
# - 3) Needed column from EOM: Processor, Card Type, Merchant Group, Attempted Captured Charges, Processed, Chargebacks, Alerts.
# - 4) Columns to calc: Disc Due, Auth Due, CB Due, Visa Alert Due
#     - Disc Due --> **Processed** x **Discount Fee**
#     - Auth Due --> **Attempted Captured Charges** x **Attemt Fees**
#     - CB Due --> **Chargebacks** x **35**
#     - Visa Alert Due --> **Alerts** x **Visa Alert**
#     - EOM --> **SUM OF ALL**
# 
# 

# ### Step 1) Import the Rubric Dataframe which we will convert to a dictionary
# 

# In[1]:


import os
import pandas as pd 
import numpy as np

# Get the current directory (where the notebook is saved)
current_directory = os.getcwd()

files = os.listdir(current_directory)

# Get the EOM df
for RUBRIC_df in files:
    if "EOM" in RUBRIC_df and "Rubric" in RUBRIC_df:
        print(RUBRIC_df)
        break

# Import the EOM_df 
import pandas as pd
import os

def import_file(file_name):
    """
    Import a specific file regardless of whether it's CSV or Excel

    Parameters:
    file_name (str): Name of the file to import

    Returns:
    pandas.DataFrame: The imported data
    """
    # Get the full path
    file_path = os.path.join(os.getcwd(), file_name)

    # Check if file exists
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File {file_name} not found in the current directory")

    # Get the file extension (lowercase)
    _, file_extension = os.path.splitext(file_name)
    file_extension = file_extension.lower()

    # Import based on file extension
    if file_extension == '.csv':
        return pd.read_csv(file_path)
    elif file_extension in ['.xlsx', '.xls']:
        return pd.read_excel(file_path)
    else:
        raise ValueError(f"Unsupported file format: {file_extension}")

# Example usage:
try:
    RUBRIC_df = import_file(RUBRIC_df)
    print(f"Successfully imported {RUBRIC_df}")
except Exception as e:
    print(f"Error importing file: {e}")
RUBRIC_df.columns = RUBRIC_df.iloc[1]
RUBRIC_df = RUBRIC_df[2:]
RUBRIC_df

# restaret the index 
RUBRIC_df.reset_index(drop=True, inplace=True)

# make sure that the Processor column is a string 
RUBRIC_df['Processor'] = RUBRIC_df['Processor'].astype(str)

RUBRIC_df


# In[2]:


# make sure that the remainig column are in float 
RUBRIC_df.iloc[:, 1:] = RUBRIC_df.iloc[:, 1:].astype(float)
what = RUBRIC_df.loc[5, "Processor"]

# We are goiung to convert the RUBRIC_df into a dictionary
RUBRIC_dict = RUBRIC_df.set_index("Processor").T.to_dict()

# Set all values into float 
RUBRIC_dict = {
    key.lower(): {inner_key: float(inner_value) for inner_key, inner_value in value.items()}
    for key, value in RUBRIC_dict.items()
}

RUBRIC_dict = {key.lower(): value for key, value in RUBRIC_dict.items()}
RUBRIC_dict["merchant industries"] = {
    "Discount Fees": 0.0,
    "Attempt Fees": 0.0,
    "CB Fee": 35.0,
    "Visa Alert Due": 0.0
}

RUBRIC_dict


# ### Step 2) Import the EOM dataframe

# In[3]:


# Get the EOM df
for EOM_df in files:
    if "EOM" in EOM_df and "View" in EOM_df:
        print(EOM_df)
        break


# In[4]:


current_directory = os.getcwd()
current_directory


# In[5]:


import pandas as pd
import os

# Get the current directory (where the notebook is saved)
current_directory = os.getcwd()

# List all files in the current directory
files = os.listdir(current_directory)

# Import the EOM_df
def import_file(file_name):
    if file_name.endswith(".csv"):
        return pd.read_csv(file_name)
    elif file_name.endswith((".xls", ".xlsx")):
        return pd.read_excel(file_name)
    else:
        raise ValueError("Unsupported file format")

# Example usage: Look for a file named "EOM-View_EXPORT.csv" or similar
for file in files:
    if "EOM" in file and file.endswith((".csv", ".xls", ".xlsx")) and "View" in file:
        EOM_df = import_file(file)
        break
else:
    raise FileNotFoundError("No EOM file found in the current directory")

# Convert "Processor", "Card Type", and "Merchant Group" into string columns
EOM_df["Processor"] = EOM_df["Processor"].astype(str)
EOM_df["Card Type"] = EOM_df["Card Type"].astype(str)
EOM_df["Merchant Group"] = EOM_df["Merchant Group"].astype(str)


# - Disc Due --> **Processed** x **Discount Fee**
# - Auth Due --> **Attempted Captured Charges** x **Attempt Fees**
# - CB Due --> **Chargebacks** x **35**
# - Visa Alert Due --> **Alerts** x **Visa Alert**
# - EOM --> **SUM OF ALL**
# 
# As we through the df we append the index and values for each dict representing each new colummn, in the end we will map the original df with these to fill them out

# In[30]:


EOM_df = EOM_df[EOM_df['Merchant Group'] != "Sale Shield"]
EOM_df = EOM_df[EOM_df['Merchant Group'] != "SaleShield"]
EOM_df = EOM_df[EOM_df["Processor"] != "EMS"]


# In[31]:


EOM_df.columns

# Columns to keep Processor, Card Type, Merchant Group, Attempted Captured Charges, Processed, Chargebacks, Alerts, Disc Due, Auth Due, CB Due, Visa Alert Due
EOM_df = EOM_df[["Processor", "Card Type", "Merchant Group", "Attempted Captured Charges", "Processed", "Chargebacks", "Alerts"]]
EOM_df["Disc Due"] = np.nan
EOM_df["Auth Due"] = np.nan
EOM_df["CB Due"] = np.nan
EOM_df["Visa Alert Due"] = np.nan
EOM_df["Total EOM"] = np.nan

# Drop all rows that have FlexFactor and Stripe in the processor column
EOM_df = EOM_df[~EOM_df["Processor"].str.contains("FlexFactor|Stripe", na=False)]

# Remove trailing spaces from EOM_df column names
def clean_column_names(df):
    df.columns = (
        df.columns.str.strip()         # Remove leading/trailing spaces
        .str.lower()                   # Convert to lowercase
        .str.replace(r'\W+', '_', regex=True)  # Replace non-word characters with '_'
        .str.replace(r'_+', '_', regex=True)   # Remove multiple consecutive '_'
        .str.rstrip('_')                # Remove trailing '_'
    )
    return df

# Clean Porcessed column such that we remove special characters and convert to float
EOM_df["Processed"] = EOM_df["Processed"].astype(str).str.replace(r'[^0-9.]', '', regex=True).astype(float)

# Replace empty strings and non-numeric values with NaN
EOM_df["Attempted Captured Charges"] = (
    EOM_df["Attempted Captured Charges"]
    .astype(str)  # Ensure the column is treated as strings
    .str.replace(r'[^0-9.]', '', regex=True)  # Remove non-numeric characters
    .replace('', 0)  # Replace empty strings with NaN
)

# Convert the column to float, coercing any remaining invalid values to NaN
EOM_df["Attempted Captured Charges"] = pd.to_numeric(EOM_df["Attempted Captured Charges"], errors='coerce')

# Convert charbacks column into integer 
# Clean and convert the column (replace "Chargebacks" with the desired column name)
EOM_df["Chargebacks"] = (
    EOM_df["Chargebacks"]
    .astype(str)  # Ensure the column is treated as strings
    .str.replace(r'[^0-9.]', '', regex=True)  # Remove non-numeric characters
    .replace('', 0)  # Replace empty strings with NaN
    .astype(float)  # Convert to float
)
EOM_df["Chargebacks"] = EOM_df["Chargebacks"].astype(str).str.replace(r'[^0-9.]', '', regex=True).astype(float)

EOM_df = clean_column_names(EOM_df)


# In[32]:


# If nan in the processor column, then drop the row
EOM_df = EOM_df.dropna(subset=["processor"])
# Reset the index
EOM_df.reset_index(drop=True, inplace=True)
EOM_df 


# #### Filling in the columns 

# In[33]:


# Now we fill in the columns above

# These dicts will in the end be mapped over the original df, they have as keys the index and as values the due amounts
disc_due_dict = {}
auth_due_dict = {}
cb_due_dict = {}
visa_alert_due_dict = {}


# Debug 1: Check if all processors in df are in the dict
count_debug_1 = 0
# Debug 2: Check if totals match rod output
count_debug_2 = 0

# Debug 3: Check if total match len of df 
count_debug3 = 0 

# Debug 4: Check if total match len of df
count_debug4 = 0

for row in EOM_df.itertuples():
    P = row.processor.lower()
    amount_processed = row.processed
    attempted_captured_charges = row.attempted_captured_charges
    attempted_captured_charges = float(attempted_captured_charges)
    chargebacks = row.chargebacks
    alerts = row.alerts
    card_used = row.card_type.lower()


    # start the iteration
    if P in RUBRIC_dict:
        count_debug_1 += 1

        # Column Disc Due --> Discount on the processed column
        discount_due = RUBRIC_dict[P]["Discount Fees"] * amount_processed
        count_debug_2 += discount_due
        disc_due_dict[row.Index] = discount_due

        # Column Auth Due --> Authorization on the processed column
        authorization_due = RUBRIC_dict[P]["Attempt Fees"] * attempted_captured_charges
        count_debug3 += 1
        auth_due_dict[row.Index] = authorization_due

        # Column CB Due --> Chargeback on the processed column
        chargeback_due = RUBRIC_dict[P]["CB Fee"] * chargebacks
        cb_due_dict[row.Index] = chargeback_due
        count_debug4 += 1
        cb_due_dict[row.Index] = chargeback_due

        # Column Visa Alert Due --> Visa Alert on the processed column
        if "visa" in card_used:

            visa_alert_due = RUBRIC_dict[P]["Visa Alert Due"] * alerts
            visa_alert_due_dict[row.Index] = visa_alert_due
        else:
            visa_alert_due = 0.0
            visa_alert_due_dict[row.Index] = visa_alert_due
    else:
        print(P)


print(count_debug_1, EOM_df.shape[0], count_debug_2)
print(f"Debug 1, passed? {count_debug_1==EOM_df.shape[0]} ")

# Debug 2: Check if the len of the dict is equal to the number of rows in the df
print(f"Debug 2, passed? {len(disc_due_dict)==EOM_df.shape[0]} ")

# Debug 3: Check if the total of the dict is equal to the number of rows in the df
print(f"Debug 3, passed? {len(auth_due_dict)==EOM_df.shape[0]} ")




# #### Now we map the dicts into the columns

# In[34]:


# Convert dictionaries to pandas Series and assign to DataFrame columns
EOM_df["disc_due"] = pd.Series(disc_due_dict)
EOM_df["auth_due"] = pd.Series(auth_due_dict)
EOM_df["cb_due"] = pd.Series(cb_due_dict)
EOM_df["visa_alert_due"] = pd.Series(visa_alert_due_dict)

# Now we create the eom dict
total_eom_dict = {}

for row in EOM_df.itertuples():
    disc__due = row.disc_due
    auth_due = row.auth_due
    cb_due = row.cb_due
    visa_alert_due = row.visa_alert_due

    sum = disc__due + auth_due + cb_due + visa_alert_due

    # Add to the dict 
    total_eom_dict[row.Index] = sum


# Now we map the EOM dict just as we did with the other columns
EOM_df["total_eom"] = pd.Series(total_eom_dict)

# Quick Ratio to check
EOM_df["processed"].sum() / EOM_df["total_eom"].sum()


# In[35]:


EOM_df[EOM_df["merchant_group"] == "nan"]


# In[36]:


EOM_df.tail(60)


# ### Processor Dataframe 

# In[37]:


EOM_df["total_eom"].sum()


# In[38]:


# Group EOM df by processor
selected_c = ["processor", "total_eom"]
EOM_processor = EOM_df[selected_c].groupby("processor").sum().reset_index()

# If we have a nan in the processor column, we remove that row 
EOM_processor = EOM_processor.dropna(subset=["processor"])
EOM_processor = EOM_processor[EOM_processor["processor"].str.lower() != "nan"]
total_row_processor = pd.DataFrame({
    'processor': ['Total'],
    'total_eom': [EOM_processor['total_eom'].sum()]
})

# Append the total row to the original DataFrame
EOM_processor = pd.concat([EOM_processor, total_row_processor], ignore_index=True)
EOM_processor 


# #### Corp dataframe

# In[39]:


selected_c = ["merchant_group", "total_eom"]
EOM_merchant_group = EOM_df[selected_c].groupby("merchant_group").sum().reset_index()

# order merchant group in alphabetical order
EOM_merchant_group = EOM_merchant_group.sort_values("merchant_group").reset_index(drop=True)

# if nan in merchant group delete the row 
"""
EOM_merchant_group = EOM_merchant_group[
    EOM_merchant_group["merchant_group"].notna() &  # Remove actual NaN values
    (EOM_merchant_group["merchant_group"].str.lower() != "nan")  # Remove string "nan"
]
"""

total_row = pd.DataFrame({
    'merchant_group': ['Total'],
    'total_eom': [EOM_merchant_group['total_eom'].sum()]
})
EOM_merchant_group = pd.concat([EOM_merchant_group, total_row], ignore_index=True)
EOM_merchant_group


# #### Convert to message 
# 

# In[40]:


message_p3 = ""
message_p3 += f"Total EOM fees by Processor: \n"

# Format processor-level fees
for row in EOM_processor.itertuples():
    if not pd.isna(row.processor):  # Exclude rows with missing processor values
        message_p3 += f"{row.processor}: ${row.total_eom:,.2f}\n"

message_p3 += "----------------------------------\n"
message_p3 += "Total EOM fees by Corp: \n"

# Format corp-level fees
for row in EOM_merchant_group.itertuples():
    if not pd.isna(row.merchant_group):  # Exclude rows with missing merchant_group values
        message_p3 += f"{row.merchant_group}: ${row.total_eom:,.2f}\n"

print(message_p3)


# ### Export 

# In[41]:


# Create a excel file that has three sheets, sheet 1 is EOM_df, sheet 2 is EOM_processor, sheet 3 is EOM_merchant_group
# Create an Excel file with three sheets
output_file = "EOM_Report.xlsx"
with pd.ExcelWriter(output_file, engine="xlsxwriter") as writer:
    EOM_df.to_excel(writer, sheet_name="EOM_df", index=False)
    EOM_processor.to_excel(writer, sheet_name="EOM_processor", index=False)
    EOM_merchant_group.to_excel(writer, sheet_name="EOM_merchant_group", index=False)

print(f"✅ Excel file '{output_file}' created successfully!")

