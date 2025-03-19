# PIP-MATE

PIP-MATE is a Python application that allows users to manage Python packages, create and manage virtual environments, and perform various pip operations in a user-friendly graphical interface built with Tkinter.

## Features

- **Install, Uninstall, and Upgrade Packages**: Allows users to install, uninstall, or upgrade Python packages easily.
- **Show Installed Packages**: View the list of installed Python packages in the current environment.
- **Create and Manage Virtual Environments**: Create new virtual environments, activate or deactivate them with ease.
- **Fetch Package Information**: Fetch detailed information about a package from PyPI (Python Package Index).
- **Clear Pip Cache**: Clear the pip cache to free up disk space.


## Installation

1. Clone the repository to your local machine:

    ```bash
    git clone https://github.com/BraveVahid/PIP-MATE.git
    ```

2. Navigate to the project directory:

    ```bash
    cd PIP-MATE
    ```

3. (Optional) Set up a virtual environment (recommended):

    ```bash
    python3 -m venv myenv
    source myenv/bin/activate  # On Windows use `myenv\Scripts\activate`
    ```

4. Install the required dependencies:

    ```bash
    pip install -r requirements.txt
    ```

5. Run the application:

    ```bash
    python main.py
    ```

## Usage

### User Interface

- **Create Virtual Environment**: Click on the "Create Virtualenv" button to create a new virtual environment in the current directory.
- **Activate/Deactivate Virtual Environment**: You can activate or deactivate a virtual environment by clicking the respective buttons.
- **Install Package**: Enter the package name in the input field and click "Install Package" to install a Python package.
- **Upgrade Package**: You can upgrade an already installed package by clicking "Upgrade Package."
- **Uninstall Package**: Uninstall a package by clicking "Uninstall Package."
- **Show Installed Packages**: View the list of installed packages by clicking "Show Installed Packages."
- **Clear Pip Cache**: Clear pip cache with the "Clear Pip Cache" button.
- **Fetch Package Info**: Fetch detailed information about a package from PyPI by entering the package name and clicking "Fetch Package Info."

## Screenshots

### Fetch Package Info View
![Main Screen](screenshot1.png)

### Installed Packages View
![Installed Packages](screenshot2.png)

## Contributing

Contributions are welcome! If you have any suggestions, bug reports, or feature requests, please open an issue or submit a pull request.
## License

This project is open-source and available under the [MIT License](LICENSE).


## Contact

If you have any questions or need further assistance, feel free to contact the developer:

- **GitHub**: [https://github.com/bravevahid](https://github.com/bravevahid)
- **Email**: vahidsiyami.dev@gmail.com
- **Telegram**: [https://t.me/pycevz](https://t.me/pycevz)
