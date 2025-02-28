import pandas as pd
import pandas as pd
import matplotlib.pyplot as plt
import ast
import os
import tkinter as tk
from tkinter.filedialog import askopenfilename


def userInputPrompts():
    """
    Prompts user to select a CSV file and returns its path.

    Args:
        No function arguments

    Returns:
        file_path (str) : The path of the selected CSV file

    Raises:
        No exception handling

    """
    # Show dialog, accept file path
    root = tk.Tk()
    root.withdraw()  # Hide the root window
    file_path = askopenfilename(
        title="Select a CSV file", filetypes=[("CSV files", "*.csv")]
    )
    root.destroy()

    return file_path


def plot_raman_shift_vs_scope(file_path):
    # Read the CSV file into a DataFrame
    df = pd.read_csv(file_path)

    # Convert string representations of lists to actual lists
    df["wavelengths"] = df["wavelengths"].apply(ast.literal_eval)
    df["scopes"] = df["scopes"].apply(ast.literal_eval)
    df["raman_shift time"] = df["raman_shift time"].apply(ast.literal_eval)

    # Plot each row
    for index, row in df.iterrows():
        plt.plot(row["scopes"], row["raman_shift time"], label=row["filename"])

    # Add labels and title
    plt.xlabel("Scope")
    plt.ylabel("Raman Shift")
    plt.title("Raman Shift vs Scope")
    plt.legend()
    plt.show()


# Example usage
file_path = userInputPrompts()  # Call the function to get the file path
plot_raman_shift_vs_scope(file_path)
