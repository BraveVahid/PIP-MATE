import os
import sys
import subprocess
import requests as rq
from colorama import init, Fore
import tkinter as tk
from tkinter import messagebox


# Global variable to track the virtual environment status
virtualenv_path = None

def create_virtualenv():
    """Create a new virtual environment in the specified directory."""
    def create():
        global virtualenv_path
        env_path = os.path.join(os.getcwd(), "myenv")  # Default to current working directory with 'myenv' name
        if os.path.exists(env_path):
            messagebox.showerror("Error", "Virtual environment already exists!")
            return
        try:
            subprocess.check_call([sys.executable, "-m", "venv", env_path])
            virtualenv_path = env_path
            messagebox.showinfo("Success", f"Virtual environment created at {env_path}")
            activate_virtualenv()  # Automatically activate the virtual environment after creation
        except subprocess.CalledProcessError as e:
            messagebox.showerror("Error", f"Error creating virtual environment: {str(e)}")

    create()

def activate_virtualenv():
    """Activate the virtual environment and set the virtualenv_path variable."""
    global virtualenv_path
    if not virtualenv_path or not os.path.exists(os.path.join(virtualenv_path, "bin" if os.name != 'nt' else "Scripts", "activate")):
        messagebox.showerror("Error", "Invalid virtual environment path!")
        return
    messagebox.showinfo("Info", f"Virtual environment activated: {virtualenv_path}")

def deactivate_virtualenv():
    """Deactivate the virtual environment by setting the virtualenv_path to None."""
    global virtualenv_path
    virtualenv_path = None
    messagebox.showinfo("Info", "Virtual environment deactivated. Using global environment now.")

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
        package_name = entry_package_name.get().strip()
        if not package_name:
            messagebox.showerror("Error", "Please enter a package name!")
            return

        url = f"https://pypi.org/pypi/{package_name}/json"
        try:
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
            result_text.config(state=tk.NORMAL)
            result_text.delete(1.0, tk.END)
            result_text.insert(tk.END,
                f"Package Name: {name}\n"
                f"Version: {version}\n"
                f"Description: {summary}\n"
                f"Author: {author}\n"
                f"Documentation: {documentation_url}\n"
                f"Source: {url}"
            )
            result_text.config(state=tk.DISABLED)
        except rq.exceptions.RequestException:
            messagebox.showerror("Error", f"Error fetching package details.")

    fetch()

def install_package():
    """Install a package using pip."""
    def install():
        package_name = entry_package_name.get().strip()
        if not package_name:
            messagebox.showerror("Error", "Please enter a package name!")
            return
        pip_command = get_pip_command()
        try:
            subprocess.check_output([pip_command, "show", package_name])
            messagebox.showinfo("Info", f"{package_name} is already installed.")
        except subprocess.CalledProcessError:
            try:
                subprocess.check_call([pip_command, "install", package_name])
                messagebox.showinfo("Success", f"{package_name} has been installed successfully.")
            except subprocess.CalledProcessError:
                messagebox.showerror("Error", f"Couldn't find or install {package_name}.")

    install()

def uninstall_package():
    """Uninstall a package using pip."""
    def uninstall():
        package_name = entry_package_name.get().strip()
        if not package_name:
            messagebox.showerror("Error", "Please enter a package name!")
            return
        pip_command = get_pip_command()
        try:
            subprocess.check_output([pip_command, "show", package_name])
            subprocess.check_call([pip_command, "uninstall", package_name, "-y"])
            messagebox.showinfo("Success", f"{package_name} has been uninstalled successfully.")
        except subprocess.CalledProcessError:
            messagebox.showerror("Error", f"{package_name} is not installed or an error occurred.")

    uninstall()

def show_installed_packages():
    """Show a list of installed packages."""
    pip_command = get_pip_command()
    try:
        installed_packages = subprocess.check_output([pip_command, "list"])
        result_text.config(state=tk.NORMAL)
        result_text.delete(1.0, tk.END)
        result_text.insert(tk.END, installed_packages.decode("utf-8"))
        result_text.config(state=tk.DISABLED)
    except subprocess.CalledProcessError as e:
        messagebox.showerror("Error", f"Error fetching installed packages: {str(e)}")

def upgrade_package():
    """Upgrade a package using pip."""
    def upgrade():
        package_name = entry_package_name.get().strip()
        if not package_name:
            messagebox.showerror("Error", "Please enter a package name!")
            return
        pip_command = get_pip_command()
        try:
            subprocess.check_call([pip_command, "install", "--upgrade", package_name])
            messagebox.showinfo("Success", f"{package_name} has been upgraded successfully.")
        except subprocess.CalledProcessError:
            messagebox.showerror("Error", f"Error upgrading {package_name}.")

    upgrade()

def clear_cache():
    """Clear the pip cache."""
    pip_command = get_pip_command()
    try:
        subprocess.check_call([pip_command, "cache", "purge"])
        messagebox.showinfo("Success", "Pip cache has been cleared successfully.")
    except subprocess.CalledProcessError as e:
        messagebox.showerror("Error", f"Error clearing pip cache: {str(e)}")

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

    # Input field for package name
    entry_package_name = tk.Entry(root, font=("Arial", 14), width=40, bd=2, relief="solid", bg="#fff", fg="#333")
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
