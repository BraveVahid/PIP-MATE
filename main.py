import os
import sys
import subprocess
import requests as rq
from colorama import init, Fore
import tkinter as tk
from tkinter import messagebox, simpledialog

# Global variable to track the virtual environment status
virtualenv_path = None

def on_entry_click(event):
    """When the Entry widget is clicked, clear the placeholder text."""
    if entry_package_name.get() == "Enter package name...":
        entry_package_name.delete(0, tk.END)  # Clear the placeholder text
        entry_package_name.config(fg="#333")  # Change text color to normal

def on_focus_out(event):
    """When the Entry widget loses focus, show the placeholder text if it's empty."""
    if entry_package_name.get() == "":
        entry_package_name.insert(0, "Enter package name...")
        entry_package_name.config(fg="#999")  # Change text color to placeholder color

def is_valid_virtualenv(path):
    """Check if the given path contains a valid virtual environment."""
    if not os.path.exists(path):
        return False
    # Check for the presence of 'bin/activate' (Linux/Mac) or 'Scripts/activate' (Windows)
    activate_script = os.path.join(path, "bin", "activate") if os.name != 'nt' else os.path.join(path, "Scripts", "activate")
    return os.path.exists(activate_script)

def create_virtualenv():
    """Create a new virtual environment in the specified directory."""
    def create():
        global virtualenv_path
        result_text.config(state=tk.NORMAL)
        result_text.delete(1.0, tk.END)  # Clear the result text before starting
        # Ask the user for the virtual environment path
        env_path = simpledialog.askstring("Create Virtualenv", "Enter the path for the virtual environment:")
        if not env_path:
            messagebox.showerror("Error", "No path provided!")
            return
        if is_valid_virtualenv(env_path):
            messagebox.showerror("Error", "A valid virtual environment already exists at this path!")
            return
        try:
            result_text.insert(tk.END, f"Creating virtual environment at {env_path}...\n")
            subprocess.check_call([sys.executable, "-m", "venv", env_path])
            virtualenv_path = env_path  # Set the global variable to the new virtual environment path
            result_text.insert(tk.END, f"Virtual environment created and activated at {env_path}\n")
            messagebox.showinfo("Success", f"Virtual environment created and activated at {env_path}")
        except subprocess.CalledProcessError as e:
            result_text.insert(tk.END, f"Error creating virtual environment: {str(e)}\n")
            messagebox.showerror("Error", f"Error creating virtual environment: {str(e)}")
        result_text.config(state=tk.DISABLED)

    create()

def activate_virtualenv():
    """Activate the virtual environment and set the virtualenv_path variable."""
    global virtualenv_path
    result_text.config(state=tk.NORMAL)
    result_text.delete(1.0, tk.END)  # Clear the result text before starting
    # Ask the user for the virtual environment path
    env_path = simpledialog.askstring("Activate Virtualenv", "Enter the path of the virtual environment to activate:")
    if not env_path:
        messagebox.showerror("Error", "No path provided!")
        return
    if not is_valid_virtualenv(env_path):
        messagebox.showerror("Error", "Invalid virtual environment path!")
        return
    virtualenv_path = env_path
    result_text.insert(tk.END, f"Virtual environment activated: {virtualenv_path}\n")
    messagebox.showinfo("Info", f"Virtual environment activated: {virtualenv_path}")
    result_text.config(state=tk.DISABLED)

def deactivate_virtualenv():
    """Deactivate the virtual environment by setting the virtualenv_path to None."""
    global virtualenv_path
    result_text.config(state=tk.NORMAL)
    result_text.delete(1.0, tk.END)  # Clear the result text before starting
    if not virtualenv_path:
        messagebox.showerror("Error", "No virtual environment is currently active!")
        return
    virtualenv_path = None
    result_text.insert(tk.END, "Virtual environment deactivated. Using global environment now.\n")
    messagebox.showinfo("Info", "Virtual environment deactivated. Using global environment now.")
    result_text.config(state=tk.DISABLED)

def get_pip_command():
    """Return the pip command based on whether a virtual environment is active."""
    if virtualenv_path:
        # If virtual environment is active, use the pip from the virtual environment
        pip_path = os.path.join(virtualenv_path, 'bin', 'pip') if os.name != 'nt' else os.path.join(virtualenv_path, 'Scripts', 'pip.exe')
        return pip_path
    else:
        # Use global pip if no virtual environment is active
        return "pip"

def fetch_package_info():
    """Fetches package information from PyPI and displays it."""
    def fetch():
        result_text.config(state=tk.NORMAL)
        result_text.delete(1.0, tk.END)  # Clear the result text before starting
        package_name = entry_package_name.get().strip()
        if not package_name or package_name == "Enter package name...":
            messagebox.showerror("Error", "Please enter a package name!")
            return

        url = f"https://pypi.org/pypi/{package_name}/json"
        try:
            result_text.insert(tk.END, f"Fetching package information for {package_name}...\n")
            response = rq.get(url, timeout=5)
            response.raise_for_status()  # Check for a successful response
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
            result_text.insert(tk.END, "Error fetching package details.\n")
        result_text.config(state=tk.DISABLED)

    fetch()

def install_package():
    """Install a package using pip."""
    def install():
        result_text.config(state=tk.NORMAL)
        result_text.delete(1.0, tk.END)  # Clear the result text before starting
        package_name = entry_package_name.get().strip()
        if not package_name or package_name == "Enter package name...":
            messagebox.showerror("Error", "Please enter a package name!")
            return
        pip_command = get_pip_command()
        try:
            subprocess.check_output([pip_command, "show", package_name])
            result_text.insert(tk.END, f"{package_name} is already installed.\n")
            messagebox.showinfo("Info", f"{package_name} is already installed.")
        except subprocess.CalledProcessError:
            try:
                result_text.insert(tk.END, f"Installing {package_name}...\n")
                subprocess.check_call([pip_command, "install", package_name])
                result_text.insert(tk.END, f"{package_name} has been installed successfully.\n")
                messagebox.showinfo("Success", f"{package_name} has been installed successfully.")
            except subprocess.CalledProcessError:
                result_text.insert(tk.END, f"Couldn't find or install {package_name}.\n")
                messagebox.showerror("Error", f"Couldn't find or install {package_name}.")
        result_text.config(state=tk.DISABLED)

    install()

def uninstall_package():
    """Uninstall a package using pip."""
    def uninstall():
        result_text.config(state=tk.NORMAL)
        result_text.delete(1.0, tk.END)  # Clear the result text before starting
        package_name = entry_package_name.get().strip()
        if not package_name or package_name == "Enter package name...":
            messagebox.showerror("Error", "Please enter a package name!")
            return
        pip_command = get_pip_command()
        try:
            subprocess.check_output([pip_command, "show", package_name])
            result_text.insert(tk.END, f"Uninstalling {package_name}...\n")
            subprocess.check_call([pip_command, "uninstall", package_name, "-y"])
            result_text.insert(tk.END, f"{package_name} has been uninstalled successfully.\n")
            messagebox.showinfo("Success", f"{package_name} has been uninstalled successfully.")
        except subprocess.CalledProcessError:
            result_text.insert(tk.END, f"{package_name} is not installed or an error occurred.\n")
            messagebox.showerror("Error", f"{package_name} is not installed or an error occurred.")
        result_text.config(state=tk.DISABLED)

    uninstall()

def show_installed_packages():
    """Show a list of installed packages."""
    result_text.config(state=tk.NORMAL)
    result_text.delete(1.0, tk.END)  # Clear the result text before starting
    pip_command = get_pip_command()
    try:
        result_text.insert(tk.END, "Fetching installed packages...\n")
        installed_packages = subprocess.check_output([pip_command, "list"])
        result_text.insert(tk.END, installed_packages.decode("utf-8"))
    except subprocess.CalledProcessError as e:
        result_text.insert(tk.END, f"Error fetching installed packages: {str(e)}\n")
    result_text.config(state=tk.DISABLED)

def upgrade_package():
    """Upgrade a package using pip."""
    def upgrade():
        result_text.config(state=tk.NORMAL)
        result_text.delete(1.0, tk.END)  # Clear the result text before starting
        package_name = entry_package_name.get().strip()
        if not package_name or package_name == "Enter package name...":
            messagebox.showerror("Error", "Please enter a package name!")
            return
        pip_command = get_pip_command()
        try:
            result_text.insert(tk.END, f"Upgrading {package_name}...\n")
            subprocess.check_call([pip_command, "install", "--upgrade", package_name])
            result_text.insert(tk.END, f"{package_name} has been upgraded successfully.\n")
            messagebox.showinfo("Success", f"{package_name} has been upgraded successfully.")
        except subprocess.CalledProcessError:
            result_text.insert(tk.END, f"Error upgrading {package_name}.\n")
            messagebox.showerror("Error", f"Error upgrading {package_name}.")
        result_text.config(state=tk.DISABLED)

    upgrade()

def clear_cache():
    """Clear the pip cache."""
    result_text.config(state=tk.NORMAL)
    result_text.delete(1.0, tk.END)  # Clear the result text before starting
    pip_command = get_pip_command()
    try:
        result_text.insert(tk.END, "Clearing pip cache...\n")
        subprocess.check_call([pip_command, "cache", "purge"])
        result_text.insert(tk.END, "Pip cache has been cleared successfully.\n")
        messagebox.showinfo("Success", "Pip cache has been cleared successfully.")
    except subprocess.CalledProcessError as e:
        result_text.insert(tk.END, f"Error clearing pip cache: {str(e)}\n")
        messagebox.showerror("Error", f"Error clearing pip cache: {str(e)}")
    result_text.config(state=tk.DISABLED)

def create_gui():
    """Create the main Tkinter window and user interface."""
    global entry_package_name, result_text

    root = tk.Tk()
    root.title("PIPMATE")
    root.geometry("700x650")  # increased window size for more space
    root.config(bg="#f7f7f7")  # lighter background color

    # Header Label
    header_label = tk.Label(root, text="PIPMATE", font=("Arial", 22, "bold"), fg="#333", bg="#f7f7f7")
    header_label.pack(pady=20)

    # Input field for package name with placeholder text
    entry_package_name = tk.Entry(root, font=("Arial", 14), width=40, bd=2, relief="solid", bg="#fff", fg="#999")
    entry_package_name.insert(0, "Enter package name...")  # Add placeholder text
    entry_package_name.bind("<FocusIn>", on_entry_click)  # Bind click event
    entry_package_name.bind("<FocusOut>", on_focus_out)  # Bind focus out event
    entry_package_name.pack(pady=10)

    # Button Frame with rounded buttons and shadows
    button_frame = tk.Frame(root, bg="#f7f7f7")
    button_frame.pack(pady=10)

    # Rounded button style (using a flat style with borders)
    button_style = {"font": ("Arial", 11, "bold"), "width": 20, "height": 2, "relief": "flat", "padx": 10}

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

# Start the Tkinter GUI application
if __name__ == "__main__":
    init()
    print(Fore.MAGENTA + """██████╗ ██╗██████╗ ███╗   ███╗ █████╗ ████████╗███████╗
██╔══██╗██║██╔══██╗████╗ ████║██╔══██╗╚══██╔══╝██╔════╝
██████╔╝██║██████╔╝██╔████╔██║███████║   ██║   █████╗
██╔═══╝ ██║██╔═══╝ ██║╚██╔╝██║██╔══██║   ██║   ██╔══╝
██║     ██║██║     ██║ ╚═╝ ██║██║  ██║   ██║   ███████╗
╚═╝     ╚═╝╚═╝     ╚═╝     ╚═╝╚═╝  ╚═╝   ╚═╝   ╚══════╝""")
    print("GitHub: https://github.com/BraveVahid")
    create_gui()
