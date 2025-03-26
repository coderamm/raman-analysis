import os
import tkinter as tk
from tkinter.filedialog import askdirectory
from pprint import pprint
import matplotlib.pyplot as plt
import pyAvantes
import pandas as pd
import numpy as np
import sys


def userInputPrompts():
    """
    Prompts user to select the folder containing the Avantes .raw8 files

    Args:
        No function arguments

    Returns:
        folder_name (str)   : the name of the folder selected by the user
        file_list (list)    : a List of filenames present in the directory
                            chosen by user

    Raises:
        No exception handling

    """
    # Show dialog, accept folder path and change folder
    root = tk.Tk()
    root.update()
    folder_path = askdirectory(title="Select folder containing the .raw8 files")
    root.destroy()
    os.chdir(folder_path)

    # Get the folder name
    folder_name = os.path.basename(os.path.normpath(folder_path))

    # Get list of files in directory, sort by name
    file_list = os.listdir()
    file_list.sort()

    return folder_name, file_list


if __name__ == "__main__":
    # Prompt user for required inputs
    folder_name, file_list = userInputPrompts()
    laser_wavelength = 785  # Laser wavelength in nanometers

    # Initialize an empty list to store the data
    data = []

    # Loop through each file in the list
    for filename in file_list:
        # Check if the file has the correct extension (e.g., .raw)
        if filename.lower().endswith(".raw8"):  # Adjust the extension as needed
            try:
                # Import spectral data using pyAvantes
                spectrum = pyAvantes.Raw8(filename)
                # Retrieve the required variables
                wavelengths = spectrum.wavelength
                intensity = spectrum.scope - spectrum.dark
                spectrum_datetime = spectrum.SPCfiledate
                raman_shift = ((1 / laser_wavelength) - (1 / wavelengths)) * 10000000

                # Append the data to the list as a single row per file
                data.append(
                    {
                        "filename": filename,
                        "wavelengths": wavelengths,
                        "intensity": intensity,
                        # "datetime": spectrum_datetime,
                        "raman_shift": raman_shift,
                    }
                )

            except Exception as e:
                print(f"Error processing file {filename}: {e}")

    # Create a DataFrame from the collected data
    df = pd.DataFrame(data)
    # Calculate the time difference from the first datetime
    # df["time_difference"] = (
    #     df["datetime"] - df["datetime"].iloc[0]
    # ).dt.total_seconds()  # Time difference in seconds
    df["time"] = [i * 15 for i in range(len(df))]

    # Reference peak 932 nm
    index_932nm = (np.abs(np.array(df["raman_shift"].iloc[0]) - 931)).argmin()

    # Plotting
    # Set global font size
    plt.rcParams.update({"font.size": 14})
    plt.figure(
        figsize=(7.5, 10)
    )  # 7.5, 10 for broader with legend outside; 5, 10 for normal
    lines = []
    for index in range(9, len(df), 2 * 4):
        # Normalize the scopes array
        normalized_scopes = (
            df.iloc[index]["intensity"] / df.iloc[index]["intensity"][index_932nm]
        )
        y_offset = (
            index // 2 * 4
        ) * 0.025  # Increment by 0.1 for each successive curve
        # Swap axes: plot raman_shift on the x-axis and normalized intensity on the y-axis
        (line,) = plt.plot(df.iloc[index]["raman_shift"], normalized_scopes + y_offset)
        lines.append(line)

    # Adding labels and title
    plt.xlabel("Raman shift (1/cm)")
    # plt.ylabel("Scope")
    # plt.title("Scope vs Wavelength for " + df.iloc[0]["filename"])
    plt.xlim(400, 1800)
    plt.ylim(bottom=0.57)  # , top=2.7)

    # Set legend
    legend = [
        "0.71 V",
        "0.51 V",
        "0.31 V",
        "0.11 V",
        "-0.09 V",
        "-0.29 V",
        "-0.49 V",
        "-0.69 V",
        "-0.89 V",
        "-1.09 V",
        "-1.29 V",
        "-1.49 V",
        "-1.69 V",
    ]
    lines.reverse()
    legend.reverse()
    plt.legend(
        lines,
        legend,
        frameon=False,
        loc="center left",
        bbox_to_anchor=(1, 0.5),
    )
    plt.grid(False)
    plt.yticks([])
    plt.tight_layout()

    # Show plot
    plt.show(block=False)

    # Change directory to parent before saving files
    os.chdir("..")

    # Save the plot as an image file in the current directory
    plt.savefig(f"{folder_name}.png")

    # Save the DataFrame to a CSV file in the current directory
    np.set_printoptions(threshold=sys.maxsize)
    df.to_csv(f"{folder_name}.csv", index=True)

    # Keep the script running until the user closes the plot window
    input("Press Enter to exit...")
