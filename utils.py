import os
import pandas as pd

def load_csv(file_path):
    """Load data from a CSV file."""
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")

    try:
        data = pd.read_csv(file_path)
    except Exception as e:
        raise ValueError(f"Could not read file: {e}")

    return data

def list_csv_files(folder_path):
    """List all CSV files in a folder."""
    try:
        return [f for f in os.listdir(folder_path) if f.endswith('.csv')]
    except Exception as e:
        raise ValueError(f"Failed to list files: {e}")