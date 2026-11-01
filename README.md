# Termux Package Catalog

Termux Package Catalog is a command-line tool written in Python for exploring an interactive catalog of Termux and Python packages. It groups packages by category, lets you search them, keeps the catalog synchronized and can start confirmed installations from its own interface.

It is an independent English-language project based on Vlsy46 by Lucas Sogaray.

- **Version:** 1.0.0
- **Release type:** Initial release
- **Maintained by:** GeneralKaos666
- **Based on:** Vlsy46 by Lucas Sogaray (MIT)
- **Language:** Python 3
- **External dependencies to run Termux Package Catalog:** none

## Version 1.0.0

### Catalog: 250 packages

The remote catalog contains **250 packages across 34 categories**. It combines tools available through the Termux package manager (`pkg`) with Python packages installable through `pip`.

The categories cover, among others, system tools, networking, languages, databases, servers, multimedia, formats, data, development, compilation, documentation, configuration, terminal and testing.

Each entry pairs the package name with its install command. Each package's availability and compatibility depend on Termux, the Python version, the architecture and the dependencies it requires.

### AutoSync: catalog synchronization

AutoSync checks for and applies remote catalog updates without editing the local list by hand.

- **Automatic check:** when Termux Package Catalog starts in an interactive terminal.
- **Manual check:** select option `U` in the main menu.
- **Change summary:** reports how many packages are new, how many commands changed and how many packages were removed.
- **Confirmation before applying:** changes are not saved until you accept them.
- **Catalog validation:** checks the structure, the schema version and the received data before accepting them.
- **Local cache:** stores the last accepted catalog so it survives between runs and keeps working when there is no connection.
- **Safe saving:** writes a temporary file first and then replaces the cache.

AutoSync only updates the catalog data; **it never installs packages by itself**.

### Package Runner: install from the catalog

Package Runner starts a package installation directly from its category.

1. Open a category.
2. Select the package number.
3. Review the manager, the name and the command that will run.
4. Confirm the operation by typing `y` or `yes`. The default answer is no.
5. Termux Package Catalog starts the matching manager and shows the result.

Two managers are supported:

- **Termux (`pkg`):** runs installations with `pkg install`.
- **Python (`pip`):** runs `python -m pip install` with the same Python interpreter that started Termux Package Catalog.

For safety, the catalog command is validated and converted into separate process arguments. It never runs through a shell, and strings with additional commands are rejected.

### Other features

- Interactive menu with category and package counts.
- Package and command view inside each category.
- Global search by package name or category, case-insensitive.
- ANSI colour interface, disabled when the output is not an interactive terminal or the `NO_COLOR` variable is set.
- Input validation and handling of cancellations with `Ctrl+C` or end of input.
- Screen clearing adapted to the system when appropriate.

## Installation and usage

Clone the repository:

```bash
git clone https://github.com/GeneralKaos666/termux-pkg-catalog.git
cd termux-pkg-catalog
```

Run the program with Python 3:

```bash
python3 termux_pkg_catalog.py
```

On Termux you can also use:

```bash
python termux_pkg_catalog.py
```

To update an existing copy from the main branch:

```bash
git pull origin main
```

You do not need to install additional Python dependencies to run the catalog. The `pkg` and `pip` managers are only required when you install packages through Package Runner.

## How to use the menu

- **Category number:** opens that category.
- **Package number:** shows the details and starts the Package Runner flow.
- **B:** opens the global search.
- **U:** checks whether a catalog update is available.
- **0:** goes back from a category or exits the program, depending on the screen.

When you open a category, select a package to review its command. Package Runner always asks for confirmation before running an installation.

## Project structure

```text
termux-pkg-catalog/
├── termux_pkg_catalog.py
├── catalog.py
├── catalog.json
├── autosync.py
└── README.md
```

- **`termux_pkg_catalog.py`:** interface, menu, search, package selection and Package Runner.
- **`catalog.py`:** local fallback catalog and loading of the last accepted cache.
- **`catalog.json`:** versioned remote catalog that AutoSync reads.
- **`autosync.py`:** download, validation and storage of the catalog cache.
- **`catalog_cache.json`:** local file generated when an update is accepted; you do not need to create it by hand.

## Adding or modifying packages

The remote catalog is kept in `catalog.json`. Each category holds package names paired with commands compatible with the supported managers.

Example of a category:

```json
{
  "my_category": {
    "termux-package": "pkg install termux-package",
    "python-package": "pip install python-package"
  }
}
```

When you publish changes to the remote catalog, increment `catalog_version` so AutoSync can detect the update. Keep `schema_version` at the value supported by the current release of Termux Package Catalog.

## Security and compatibility

Termux Package Catalog never installs packages automatically. Package Runner shows which manager and package will be used and requires explicit confirmation before running the installation.

Installations can change your Termux or Python environment, consume storage, require a connection or need additional dependencies. Review every package before confirming. Not every Python package published on PyPI works on Android or Termux, especially those that need native components.

AutoSync updates the catalog only after validating the data and receiving confirmation. If the remote catalog cannot be reached, Termux Package Catalog keeps using the local catalog or the last accepted cache.

## License

MIT. See [LICENSE](LICENSE).

This project is based on Vlsy46, copyright (c) 2026 lucassogarayDA, distributed under the MIT license.

## Credits

- Original project: Vlsy46 by Lucas Sogaray.
- English translation and maintenance: GeneralKaos666.
