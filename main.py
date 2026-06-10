import os
import json
import xml.etree.ElementTree as ET
import pandas as pd


# ==========================================================
# INPUT FILE
# ==========================================================

FILE = input("Enter the name of the file: ").strip()

INPUT_FILE = FILE

BASE_NAME = os.path.splitext(
    os.path.basename(FILE)
)[0]

OUTPUT_DIR = os.path.join(
    "/mnt/d/Coding",
    f"{BASE_NAME}_CSV"
)

os.makedirs(
    OUTPUT_DIR,
    exist_ok=True
)


# ==========================================================
# LOAD CONFIG
# ==========================================================

CONFIG_FILE = "config.json"

if not os.path.exists(CONFIG_FILE):
    raise FileNotFoundError(
        f"{CONFIG_FILE} not found."
    )

with open(CONFIG_FILE, "r") as f:
    CONFIG = json.load(f)


# ==========================================================
# CONVERT XML TAG TO TABLE
# ==========================================================
# ==========================================================
# CONVERT XML TAG TO TABLE
# ==========================================================

# ==========================================================
# CONVERT XML TAG TO TABLE
# ==========================================================
def convert_tag_to_dataframe(top_tag):

    raw_rows = []

    def process_element(element, accumulated_levels):
        
        # Extract attributes for the current level
        current_values = []
        for key, value in element.attrib.items():
            current_values.append(f"{key}={value}")

        # Handle text data inside leaf nodes if present
        if len(element) == 0 and element.text and element.text.strip():
            current_values.append(element.text.strip())

        current_level_data = {
            "tag": element.tag,
            "values": current_values
        }

        # ----------------------------------------------------
        # STRIP ROOT TAG LOGIC
        # ----------------------------------------------------
        if element == top_tag:
            # Don't add the root tag (D1, D4, D9, etc.) to the layout
            new_levels = accumulated_levels
        else:
            # Add this tag and its values to the row hierarchy
            new_levels = accumulated_levels + [current_level_data]
            raw_rows.append(new_levels)

        for child in element:
            process_element(child, new_levels)

    # Start recursive processing
    process_element(top_tag, [])

    # If the file had no valid nested children, return empty
    if not raw_rows:
        return pd.DataFrame()

    # ----------------------------------------------------
    # DYNAMIC COLUMN SIZING
    # Determine maximum depth and max values per depth
    # ----------------------------------------------------
    max_depth = max(len(row) for row in raw_rows)
    max_vals_per_depth = {i: 0 for i in range(max_depth)}

    for row in raw_rows:
        for i, level in enumerate(row):
            max_vals_per_depth[i] = max(
                max_vals_per_depth[i], 
                len(level["values"])
            )

    # ----------------------------------------------------
    # BUILD INTERLEAVED COLUMN ORDER
    # Creates: LEVEL1_TAG, LEVEL1_VALUE1, LEVEL2_TAG...
    # ----------------------------------------------------
    ordered_columns = []
    for i in range(max_depth):
        ordered_columns.append(f"LEVEL{i+1}_TAG")
        for j in range(max_vals_per_depth[i]):
            ordered_columns.append(f"LEVEL{i+1}_VALUE{j+1}")

    # ----------------------------------------------------
    # MAP DATA TO COLUMNS
    # ----------------------------------------------------
    flattened_rows = []
    for raw_row in raw_rows:
        row_dict = {}
        
        for i in range(max_depth):
            if i < len(raw_row):
                # Tag exists at this level
                level = raw_row[i]
                row_dict[f"LEVEL{i+1}_TAG"] = level["tag"]
                
                # Map values for this level
                for j in range(max_vals_per_depth[i]):
                    if j < len(level["values"]):
                        row_dict[f"LEVEL{i+1}_VALUE{j+1}"] = level["values"][j]
                    else:
                        row_dict[f"LEVEL{i+1}_VALUE{j+1}"] = ""
            else:
                # No tag at this depth for this specific row; pad with blanks
                row_dict[f"LEVEL{i+1}_TAG"] = ""
                for j in range(max_vals_per_depth[i]):
                    row_dict[f"LEVEL{i+1}_VALUE{j+1}"] = ""

        flattened_rows.append(row_dict)

    # Build DataFrame using our strictly ordered columns
    df = pd.DataFrame(flattened_rows, columns=ordered_columns)

    # ----------------------------------------------------
    # ULTIMATE SWEEPER
    # Automatically drops any column that is 100% blank
    # ----------------------------------------------------
    df = df.replace("", None).dropna(how="all", axis=1).fillna("")

    return df
# ==========================================================
# PARSE XML
# ==========================================================

try:

    tree = ET.parse(INPUT_FILE)

except Exception as e:

    raise Exception(
        f"Unable to read file: {e}"
    )

root = tree.getroot()

utility = root.find("UTILITYTYPE")

if utility is None:

    raise Exception(
        "UTILITYTYPE tag not found."
    )


# ==========================================================
# CREATE DATAFRAMES
# ==========================================================

tag_data = {}

for top_tag in utility:

    tag_name = top_tag.tag

    df = convert_tag_to_dataframe(
        top_tag
    )

    if not df.empty:

        tag_data[tag_name] = df

if not tag_data:

    raise Exception(
        "No data found."
    )


# ==========================================================
# EXPORT CONFIGURED TAGS
# ==========================================================

print("\nProcessing tags...\n")

for tag in CONFIG.keys():

    if tag not in tag_data:

        print(
            f"Skipping {tag} "
            f"(tag not found in file)"
        )

        continue

    df = tag_data[tag]

    output_file = os.path.join(
        OUTPUT_DIR,
        f"{BASE_NAME}_{tag}.csv"
    )

    df.to_csv(
        output_file,
        index=False
    )

    print(
        f"Created: "
        f"{BASE_NAME}_{tag}.csv "
        f"({len(df)} rows)"
    )

print(
    f"\nDone.\n"
    f"Output Folder:\n{OUTPUT_DIR}"
)