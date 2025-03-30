import os
from random import sample
import subprocess
import sys
import threading
from time import sleep


import tkinter as tk
from tkinter import messagebox, simpledialog

import requests as rq
from colorama import Fore, init


# Global variable to track the virtual environment status
virtualenv_path = None


def on_entry_click(event):
    """
    Clears the placeholder text in the Entry widget when it is clicked.

    Changes the text color to normal.
    """
    if entry_package_name.get() == "Enter package name...":
        entry_package_name.delete(0, tk.END)  # Clear the placeholder text
        entry_package_name.config(fg="#333")  # Change text color to normal


def on_focus_out(event):
    """
    Restores the placeholder text in the Entry widget if it's empty when it loses focus.

    Changes the text color to the placeholder color.
    """
    if entry_package_name.get() == "":
        entry_package_name.insert(0, "Enter package name...")  # Insert placeholder text
        entry_package_name.config(fg="#999")  # Change text color to placeholder color


def is_valid_virtualenv(path):
    """
    Checks if the given path contains a valid virtual environment.

    A valid virtual environment should have the appropriate 'activate' script.
    """
    if not os.path.exists(path):
        return False

    # Check for the presence of 'bin/activate' (Linux/Mac) or 'Scripts/activate' (Windows)
    activate_script = os.path.join(path, "bin", "activate") if os.name != 'nt' else os.path.join(path, "Scripts",
                                                                                                 "activate")
    return os.path.exists(activate_script)


def create_virtualenv():
    """
    Creates a new virtual environment in the specified directory.

    This function prompts the user for a directory path and creates a Python virtual environment
    at the given location if one does not already exist.
    """
    env_path = simpledialog.askstring("Create Virtualenv", "Enter the path for the virtual environment:")

    if not env_path:
        messagebox.showerror("Error", "No path provided!")
        return

    if is_valid_virtualenv(env_path):
        messagebox.showerror("Error", "A valid virtual environment already exists at this path!")
        return

    def create():
        """
        Handles the virtual environment creation process.

        Runs in a separate thread to prevent UI freezing and updates the UI with progress information.
        """
        global virtualenv_path
        result_text.config(state=tk.NORMAL)
        result_text.delete(1.0, tk.END)

        try:
            # Notify user that the virtual environment is being created
            result_text.insert(tk.END, f"Creating virtual environment at {env_path}...\n")

            # Run the command to create a virtual environment
            subprocess.check_call([sys.executable, "-m", "venv", env_path])
            virtualenv_path = env_path

            success_message = f"Virtual environment created and activated at {env_path}"
            result_text.insert(tk.END, success_message + "\n")

            # Display success message in the main window
            result_text.winfo_toplevel().after(0, lambda: messagebox.showinfo("Success", success_message))

        except subprocess.CalledProcessError as e:
            # Handle errors during virtual environment creation
            error_message = f"Error creating virtual environment: {str(e)}"
            result_text.insert(tk.END, error_message + "\n")
            result_text.winfo_toplevel().after(0, lambda: messagebox.showerror("Error", error_message))

        result_text.config(state=tk.DISABLED)

    # Run the virtual environment creation process in a separate thread
    threading.Thread(target=create, daemon=True).start()


def activate_virtualenv():
    """
    Prompts the user to enter the path of a virtual environment and activates it if valid.

    If no path is provided or the path is invalid, an error message is displayed.
    """
    env_path = simpledialog.askstring(
        "Activate Virtualenv",
        "Enter the path of the virtual environment to activate:"
    )

    if not env_path:
        messagebox.showerror("Error", "No path provided!")  # Show an error if no path is entered
        return

    if not is_valid_virtualenv(env_path):
        messagebox.showerror("Error", "Invalid virtual environment path!")  # Show an error if the path is invalid
        return

    def activate():
        """Activates the virtual environment and updates the UI."""
        global virtualenv_path

        result_text.config(state=tk.NORMAL)  # Enable text widget for modification
        result_text.delete(1.0, tk.END)  # Clear previous output

        virtualenv_path = env_path  # Store the virtual environment path
        result_text.insert(tk.END, f"Virtual environment activated: {virtualenv_path}\n")

        # Show confirmation message asynchronously
        result_text.after(0, lambda: messagebox.showinfo(
            "Info", f"Virtual environment activated: {virtualenv_path}"
        ))

        result_text.config(state=tk.DISABLED)  # Disable text widget after update

    # Run activation in a separate thread to keep the UI responsive
    threading.Thread(target=activate).start()


def deactivate_virtualenv():
    """
    Deactivates the currently active virtual environment.

    If no virtual environment is active, an error message is displayed.
    """
    if not virtualenv_path:
        messagebox.showerror("Error", "No virtual environment is currently active!")
        return

    def deactivate():
        """Deactivates the virtual environment and updates the UI."""
        global virtualenv_path

        result_text.config(state=tk.NORMAL)  # Enable text widget for modification
        result_text.delete(1.0, tk.END)  # Clear previous output

        virtualenv_path = None  # Reset the virtual environment path
        result_text.insert(
            tk.END, "Virtual environment deactivated. Using global environment now.\n"
        )

        # Show confirmation message asynchronously
        result_text.after(0, lambda: messagebox.showinfo(
            "Info", "Virtual environment deactivated. Using global environment now."
        ))

        result_text.config(state=tk.DISABLED)  # Disable text widget after update

    # Run deactivation in a separate thread to keep the UI responsive
    threading.Thread(target=deactivate).start()


def get_pip_command():
    """
    Returns the path to the pip executable for the active virtual environment.

    If no virtual environment is active, returns the system-wide pip command.
    """
    if virtualenv_path:
        # Construct the pip path based on the operating system
        pip_path = os.path.join(virtualenv_path, 'bin', 'pip') if os.name != 'nt' else os.path.join(virtualenv_path, 'Scripts', 'pip.exe')
        return pip_path
    else:
        return "pip"  # Return the system-wide pip command if no virtual environment is active


def fetch_package_info():
    """
    Fetches package information from PyPI and displays it in the result_text widget.

    If the package name is empty or invalid, an error message is shown.
    """
    def fetch():
        """Fetches the package information from PyPI in a separate thread."""
        result_text.config(state=tk.NORMAL)  # Enable text widget for modification
        result_text.delete(1.0, tk.END)  # Clear the result text before starting

        package_name = entry_package_name.get().strip()

        # Check if package name is provided
        if not package_name or package_name == "Enter package name...":
            # Use after() to run UI updates on the main thread
            result_text.after(0, lambda: messagebox.showerror("Error", "Please enter a package name!"))
            return

        url = f"https://pypi.org/pypi/{package_name}/json"
        try:
            result_text.insert(tk.END, f"Fetching package information for {package_name}...\n")
            response = rq.get(url, timeout=5)  # Send request to PyPI API
            response.raise_for_status()  # Check for successful response
            data = response.json()
            package_info = data.get("info", {})

            # Extract relevant package information
            name = package_info.get("name", "Unknown")
            version = package_info.get("version", "Unknown")
            summary = package_info.get("summary", "No description available.")
            author = package_info.get("author", "Unknown")
            project_urls = package_info.get("project_urls", {})
            documentation_url = project_urls.get("Documentation", "No documentation available")

            # Display the fetched data in the text widget
            result_text.insert(tk.END,
                               f"Package Name: {name}\n"
                               f"Version: {version}\n"
                               f"Description: {summary}\n"
                               f"Author: {author}\n"
                               f"Documentation: {documentation_url}\n"
                               f"Source: {url}\n"
                               )

        except rq.exceptions.RequestException:
            # Handle errors during the fetch operation
            result_text.insert(tk.END, "Error fetching package details.\n")

        result_text.config(state=tk.DISABLED)  # Disable text widget after update

    # Start the fetch operation in a separate thread to avoid UI freeze
    threading.Thread(target=fetch).start()


def install_package():
    """
    Installs a package using pip.

    Checks if the package is already installed. If not, installs it and updates the UI accordingly.
    """
    # Check package name input in the main thread
    package_name = entry_package_name.get().strip()
    if not package_name or package_name == "Enter package name...":
        messagebox.showerror("Error", "Please enter a package name!")
        return

    def install():
        """Handles the package installation process."""
        result_text.config(state=tk.NORMAL)
        result_text.delete(1.0, tk.END)  # Clear the result text before starting

        pip_command = get_pip_command()  # Get the correct pip command based on the environment
        try:
            # Check if the package is already installed
            subprocess.check_output([pip_command, "show", package_name])
            result_text.insert(tk.END, f"{package_name} is already installed.\n")
            # Use after() to display message on the main thread
            result_text.after(0, lambda: messagebox.showinfo("Info", f"{package_name} is already installed."))
        except subprocess.CalledProcessError:
            try:
                # If not installed, try installing the package
                result_text.insert(tk.END, f"Installing {package_name}...\n")
                subprocess.check_call([pip_command, "install", package_name])
                result_text.insert(tk.END, f"{package_name} has been installed successfully.\n")
                # Use after() to display success message on the main thread
                result_text.after(0, lambda: messagebox.showinfo(
                    "Success", f"{package_name} has been installed successfully."
                ))
            except subprocess.CalledProcessError:
                result_text.insert(tk.END, f"Couldn't find or install {package_name}.\n")
                # Use after() to display error message on the main thread
                result_text.after(0, lambda: messagebox.showerror(
                    "Error", f"Couldn't find or install {package_name}."
                ))

        result_text.config(state=tk.DISABLED)

    # Start the install operation in a separate thread to keep the UI responsive
    threading.Thread(target=install).start()


def uninstall_package():
    """
    Uninstalls a package using pip.

    Checks if the package is installed. If it is, it uninstalls the package and updates the UI accordingly.
    """
    # Check package name input in the main thread
    package_name = entry_package_name.get().strip()
    if not package_name or package_name == "Enter package name...":
        messagebox.showerror("Error", "Please enter a package name!")
        return

    def uninstall():
        """Handles the package uninstallation process."""
        result_text.config(state=tk.NORMAL)
        result_text.delete(1.0, tk.END)  # Clear the result text before starting

        pip_command = get_pip_command()  # Get the correct pip command based on the environment
        try:
            # Check if the package is installed
            subprocess.check_output([pip_command, "show", package_name])
            result_text.insert(tk.END, f"Uninstalling {package_name}...\n")
            # Uninstall the package
            subprocess.check_call([pip_command, "uninstall", package_name, "-y"])
            result_text.insert(tk.END, f"{package_name} has been uninstalled successfully.\n")
            # Use after() to display success message on the main thread
            result_text.after(0, lambda: messagebox.showinfo(
                "Success", f"{package_name} has been uninstalled successfully."
            ))
        except subprocess.CalledProcessError:
            result_text.insert(tk.END, f"{package_name} is not installed or an error occurred.\n")
            # Use after() to display error message on the main thread
            result_text.after(0, lambda: messagebox.showerror(
                "Error", f"{package_name} is not installed or an error occurred."
            ))

        result_text.config(state=tk.DISABLED)

    # Start the uninstall operation in a separate thread to keep the UI responsive
    threading.Thread(target=uninstall).start()


def show_installed_packages():
    """
    Displays a list of installed packages using pip.

    Fetches the list of installed packages and shows the output in the result_text widget.
    """
    def fetch_packages():
        """Fetches the installed packages in a separate thread."""
        result_text.config(state=tk.NORMAL)  # Enable text widget for modification
        result_text.delete(1.0, tk.END)  # Clear the result text before starting

        pip_command = get_pip_command()  # Get the correct pip command based on the environment
        try:
            result_text.insert(tk.END, "Fetching installed packages...\n")
            # Get the list of installed packages
            installed_packages = subprocess.check_output([pip_command, "list"])
            result_text.insert(tk.END, installed_packages.decode("utf-8"))
        except subprocess.CalledProcessError as e:
            result_text.insert(tk.END, f"Error fetching installed packages: {str(e)}\n")

        result_text.config(state=tk.DISABLED)  # Disable text widget after the update

    # Start the fetch operation in a separate thread to keep the UI responsive
    threading.Thread(target=fetch_packages).start()


def upgrade_package():
    """
    Upgrades a package using pip in a separate thread.

    Checks if the package is provided and upgrades it, showing the result in the result_text widget.
    """
    def upgrade():
        """Handles the package upgrade process."""
        result_text.config(state=tk.NORMAL)  # Enable text widget for modification
        result_text.delete(1.0, tk.END)  # Clear the result text before starting

        package_name = entry_package_name.get().strip()

        # Check if the package name is provided
        if not package_name or package_name == "Enter package name...":
            messagebox.showerror("Error", "Please enter a package name!")
            return

        pip_command = get_pip_command()  # Get the correct pip command based on the environment
        try:
            result_text.insert(tk.END, f"Upgrading {package_name}...\n")
            # Attempt to upgrade the package
            subprocess.check_call([pip_command, "install", "--upgrade", package_name])
            result_text.insert(tk.END, f"{package_name} has been upgraded successfully.\n")
            # Show success message in the main thread
            messagebox.showinfo("Success", f"{package_name} has been upgraded successfully.")
        except subprocess.CalledProcessError:
            result_text.insert(tk.END, f"Error upgrading {package_name}.\n")
            # Show error message in the main thread
            messagebox.showerror("Error", f"Error upgrading {package_name}.")

        result_text.config(state=tk.DISABLED)  # Disable text widget after the update

    # Start the upgrade operation in a separate thread to keep the UI responsive
    threading.Thread(target=upgrade).start()


def clear_cache():
    """
    Clears the pip cache in a separate thread.

    Clears the pip cache and shows the result in the result_text widget.
    """
    def clear():
        """Handles the pip cache clearing process."""
        result_text.config(state=tk.NORMAL)  # Enable text widget for modification
        result_text.delete(1.0, tk.END)  # Clear the result text before starting

        pip_command = get_pip_command()  # Get the correct pip command based on the environment
        try:
            result_text.insert(tk.END, "Clearing pip cache...\n")
            # Clear the pip cache
            subprocess.check_call([pip_command, "cache", "purge"])
            result_text.insert(tk.END, "Pip cache has been cleared successfully.\n")
            # Show success message in the main thread
            messagebox.showinfo("Success", "Pip cache has been cleared successfully.")
        except subprocess.CalledProcessError as e:
            result_text.insert(tk.END, f"Error clearing pip cache: {str(e)}\n")
            # Show error message in the main thread
            messagebox.showerror("Error", f"Error clearing pip cache: {str(e)}")

        result_text.config(state=tk.DISABLED)  # Disable text widget after the update

    # Start the cache clearing operation in a separate thread to keep the UI responsive
    threading.Thread(target=clear).start()


def create_gui():
    """
    Create the main Tkinter window and user interface.

    This function sets up the main window, input fields, buttons, and the result display.
    It includes configuration for buttons, labels, and layout for the PIPMATE app.
    """
    global entry_package_name, result_text

    root = tk.Tk()
    root.title("PIPMATE")
    root.geometry("700x650")  # Increased window size for more space
    root.config(bg="#f7f7f7")  # Lighter background color

    # Header Label
    header_label = tk.Label(root, text="PIPMATE", font=("Arial", 22, "bold"), fg="#333", bg="#f7f7f7")
    header_label.pack(pady=20)

    # Input field for package name with placeholder text
    entry_package_name = tk.Entry(root, font=("Arial", 14), width=40, bd=2, relief="solid", bg="#fff", fg="#999")
    entry_package_name.insert(0, "Enter package name...")  # Add placeholder text
    entry_package_name.bind("<FocusIn>", on_entry_click)  # Bind click event to clear placeholder
    entry_package_name.bind("<FocusOut>", on_focus_out)  # Bind focus out event to restore placeholder
    entry_package_name.pack(pady=10)

    # Button Frame with rounded buttons and shadows
    button_frame = tk.Frame(root, bg="#f7f7f7")
    button_frame.pack(pady=10)

    # Rounded button style (using a flat style with borders)
    button_style = {
        "font": ("Arial", 11, "bold"), "width": 20, "height": 2, "relief": "flat", "padx": 10
    }

    # Buttons with hover effects arranged in two columns
    # First column (left side)
    tk.Button(button_frame, text="Install Package", command=install_package, bg="#28A745", fg="white", **button_style).grid(row=0, column=0, padx=10, pady=5)
    tk.Button(button_frame, text="Upgrade Package", command=upgrade_package, bg="#28A745", fg="white", **button_style).grid(row=1, column=0, padx=10, pady=5)
    tk.Button(button_frame, text="Activate Virtualenv", command=activate_virtualenv, bg="#28A745", fg="white", **button_style).grid(row=2, column=0, padx=10, pady=5)
    tk.Button(button_frame, text="Show Installed Packages", command=show_installed_packages, bg="#007BFF", fg="white", **button_style).grid(row=3, column=0, padx=10, pady=5)

    # Second column (right side)
    tk.Button(button_frame, text="Uninstall Package", command=uninstall_package, bg="#DC3545", fg="white", **button_style).grid(row=0, column=1, padx=10, pady=5)
    tk.Button(button_frame, text="Clear Pip Cache", command=clear_cache, bg="#DC3545", fg="white", **button_style).grid(row=1, column=1, padx=10, pady=5)
    tk.Button(button_frame, text="Deactivate Virtualenv", command=deactivate_virtualenv, bg="#DC3545", fg="white", **button_style).grid(row=2, column=1, padx=10, pady=5)
    tk.Button(button_frame, text="Fetch Package Info", command=fetch_package_info, bg="#007BFF", fg="white", **button_style).grid(row=3, column=1, padx=10, pady=5)

    # Create Virtualenv button at the bottom of the window
    tk.Button(root, text="Create Virtualenv", command=create_virtualenv, bg="#6C757D", fg="white", font=("Arial", 11, "bold"), width=25, height=2).pack(pady=5)

    # Result Text Box with Scrollbar
    result_frame = tk.Frame(root)
    result_frame.pack(pady=10)

    result_text = tk.Text(result_frame, height=10, width=60, font=("Courier New", 12), wrap=tk.WORD, bd=2, relief="solid", bg="#fff", fg="#333")
    result_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    result_text.config(state=tk.DISABLED)

    scrollbar = tk.Scrollbar(result_frame, command=result_text.yview)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    result_text.config(yscrollcommand=scrollbar.set)

    # Run the GUI
    root.mainloop()


if __name__ == "__main__":
    init(autoreset=True)  # Initialize colorama for automatic color reset

    # ASCII text to be displayed with random colors
    text = """
    ██████╗  ██╗ ██████╗  ███╗   ███╗  █████╗  ████████╗ ███████╗
    ██╔══██╗ ██║ ██╔══██╗ ████╗ ████║ ██╔══██╗ ╚══██╔══╝ ██╔════╝
    ██████╔╝ ██║ ██████╔╝ ██╔████╔██║ ███████║    ██║    █████╗  
    ██╔═══╝  ██║ ██╔═══╝  ██║╚██╔╝██║ ██╔══██║    ██║    ██╔══╝  
    ██║      ██║ ██║      ██║ ╚═╝ ██║ ██║  ██║    ██║    ███████╗
    ╚═╝      ╚═╝ ╚═╝      ╚═╝     ╚═╝ ╚═╝  ╚═╝    ╚═╝    ╚══════╝
    """

    # List of available colors for random selection
    colors = [
        Fore.LIGHTCYAN_EX,
        Fore.LIGHTMAGENTA_EX,
        Fore.LIGHTRED_EX,
        Fore.LIGHTGREEN_EX,
        Fore.LIGHTYELLOW_EX,
        Fore.LIGHTWHITE_EX,
        Fore.LIGHTBLUE_EX,
    ]

    # Loop through each character and print with a random color
    for char in text:
        random_color = sample(colors, 1)[0]
        sys.stdout.write(random_color + char)
        sys.stdout.flush()
        sleep(0.01)  # Add a delay for a typing effect

    create_gui()
