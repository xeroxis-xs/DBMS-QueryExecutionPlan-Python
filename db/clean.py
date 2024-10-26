import os

# Define the base directory and files to process
base_path = 'C:/Users/XiSheng/Documents/Github/DBMS-QueryExecutionPlan-Python/db/tbl'
files_to_clean = [
    "region.tbl",
    "nation.tbl",
    "customer.tbl",
    "supplier.tbl",
    "part.tbl",
    "partsupp.tbl",
    "orders.tbl",
    "lineitem.tbl"
]

# Function to clean up each file
def clean_file(file_path):
    cleaned_lines = []
    with open(file_path, 'r') as file:
        for line in file:
            # Remove the trailing delimiter if present
            cleaned_line = line.rstrip("|\n") + '\n'
            cleaned_lines.append(cleaned_line)

    # Write the cleaned data back to the file
    with open(file_path, 'w') as file:
        file.writelines(cleaned_lines)
    print(f"Cleaned file: {file_path}")

# Process each file
for file_name in files_to_clean:
    file_path = os.path.join(base_path, file_name)
    clean_file(file_path)