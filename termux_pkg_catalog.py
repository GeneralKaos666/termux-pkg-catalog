#!/usr/bin/env python3

import os
import re
import shutil
import subprocess
import sys

from catalog import packages, CATALOG_VERSION
from autosync import CatalogError, download_catalog, save_cache


COLORS = {
    "cyan": "\033[96m",
    "green": "\033[92m",
    "yellow": "\033[93m",
    "red": "\033[91m",
    "gray": "\033[90m",
    "bold": "\033[1m",
    "reset": "\033[0m",
}

VERSION = "1.0.0"

COLORS_ENABLED = sys.stdout.isatty() and os.environ.get("NO_COLOR") is None

FRAME_WIDTH = 46


def style(text, *colors):
    if not COLORS_ENABLED:
        return str(text)
    prefix = "".join(COLORS[color] for color in colors)
    return f"{prefix}{text}{COLORS['reset']}"


def frame_line(text):
    return "║" + f"{text:^{FRAME_WIDTH}}" + "║"


def clear_screen():
    if not sys.stdout.isatty():
        return

    command = "cls" if os.name == "nt" else "clear"
    if shutil.which(command):
        os.system(command)


def read_input(message):
    try:
        return input(message).strip()
    except (EOFError, KeyboardInterrupt):
        print("\n" + style("Operation cancelled. Goodbye!", "yellow"))
        raise SystemExit(0)


def pause(message):
    read_input(style(message, "yellow"))


def show_header():
    print(style("╔" + "═" * FRAME_WIDTH + "╗", "cyan"))
    print(style(frame_line("Termux Package Catalog"), "cyan", "bold"))
    print(style(frame_line(f"version {VERSION}"), "gray"))
    print(style(frame_line("Based on Vlsy46 by Lucas Sogaray"), "gray"))
    print(style("╚" + "═" * FRAME_WIDTH + "╝", "cyan"))


def search_packages(query):
    matches = []
    query = query.casefold()

    for category, package_list in packages.items():
        for name, command in package_list.items():
            if query in name.casefold() or query in category.casefold():
                matches.append((name, command, category))

    return matches


def show_search():
    clear_screen()
    show_header()
    print("\n" + style("GLOBAL SEARCH", "cyan", "bold"))
    print(style("Search by package name or category.", "gray"))
    query = read_input("\n" + style("Search: ", "yellow"))

    if not query:
        pause("\nThe search is empty. Press Enter to continue...")
        return

    results = search_packages(query)
    clear_screen()
    show_header()
    print("\n" + style(f"RESULTS FOR: {query}", "cyan", "bold"))
    print(style("────────────────────────────────────────────────", "gray"))

    if not results:
        print("\n" + style("No matches found.", "red"))
    else:
        print(
            f"\n{style('Matches:', 'gray')} "
            f"{style(len(results), 'green', 'bold')}\n"
        )
        for name, command, category in results:
            print(f"  {style('•', 'yellow')} {style(name, 'green', 'bold')}")
            print(f"    {style('Category:', 'gray')} {category}")
            print(f"    {style(command, 'cyan')}\n")

    print(style("────────────────────────────────────────────────", "gray"))
    pause("Press Enter to return to the catalog...")


def show_menu():
    categories = list(packages.keys())
    total_packages = sum(len(package_list) for package_list in packages.values())

    show_header()
    print("\n" + style("PACKAGE CATALOG", "cyan", "bold"))
    print(style("────────────────────────────────────────────────", "gray"))
    print(
        f"{style('Categories:', 'gray')} {style(len(categories), 'yellow', 'bold')}"
        f"  |  {style('Packages:', 'gray')} {style(total_packages, 'green', 'bold')}\n"
    )

    for number, category in enumerate(categories, start=1):
        count = len(packages[category])
        number_text = style(f"{number:>2}.", "yellow")
        category_text = style(f"{category:<22}", "green")
        count_text = style(f"[{count} packages]", "gray")
        print(f"  {number_text} {category_text} {count_text}")

    print("\n  " + style("B. Search packages", "cyan", "bold"))
    print("  " + style("U. Check for updates", "yellow", "bold"))
    print("  " + style("0. Exit", "red"))
    print(style("────────────────────────────────────────────────", "gray"))
    return categories


def parse_install_command(command):
    """Accept only simple pkg or pip install commands."""
    match = re.fullmatch(
        r"(pkg|pip) install ([A-Za-z0-9][A-Za-z0-9._+:-]*)",
        command.strip(),
    )
    if not match:
        return None

    manager, package = match.groups()
    return manager, package


def run_install(command):
    """Run an installation without going through a command interpreter."""
    parsed = parse_install_command(command)
    if parsed is None:
        print(style("Command not allowed. Only pkg or pip installs are accepted.", "red"))
        pause("Press Enter to continue...")
        return

    manager, package = parsed
    if manager == "pkg":
        arguments = ["pkg", "install", package]
        visible_command = f"pkg install {package}"
    else:
        arguments = [sys.executable, "-m", "pip", "install", package]
        visible_command = f"{sys.executable} -m pip install {package}"

    print("\n" + style("PACKAGE RUNNER", "cyan", "bold"))
    print(f"{style('Manager:', 'gray')} {manager}")
    print(f"{style('Package:', 'gray')} {package}")
    print(f"{style('Command:', 'gray')} {visible_command}")
    print(style("The installer may modify your Termux/Python environment.", "yellow"))
    answer = read_input(style("Run the installation? [y/N]: ", "yellow"))
    if answer.casefold() not in ("y", "yes"):
        print(style("Installation cancelled.", "yellow"))
        pause("Press Enter to continue...")
        return

    print("\n" + style("Starting installation...", "cyan", "bold"))
    try:
        result = subprocess.run(arguments, check=False)
    except FileNotFoundError:
        print(style(f"Required executable for {manager} was not found.", "red"))
    except OSError as error:
        print(style(f"Could not start the installer: {error}", "red"))
    else:
        if result.returncode == 0:
            print(style("\nInstallation completed successfully.", "green", "bold"))
        else:
            print(style(f"\nThe installer exited with code {result.returncode}.", "red"))
    pause("Press Enter to return to packages...")


def show_category(category):
    package_list = list(packages[category].items())

    while True:
        clear_screen()
        show_header()
        print("\n" + style(category.upper(), "cyan", "bold"))
        print(style("Select a package to view its command or install it.", "gray"))
        print(style("────────────────────────────────────────────────", "gray"))
        print(f"{style('Available packages:', 'gray')} {style(len(package_list), 'green', 'bold')}\n")

        for number, (name, command) in enumerate(package_list, start=1):
            print(f"  {style(f'{number:>3}.', 'yellow')} {style(name, 'green', 'bold')}")
            print(f"       {style(command, 'cyan')}")

        print("\n  " + style("0. Back", "red"))
        print(style("────────────────────────────────────────────────", "gray"))
        choice = read_input(style("Select a package: ", "yellow"))

        if choice == "0":
            return
        if not choice.isdigit() or not 1 <= int(choice) <= len(package_list):
            pause("Invalid selection. Press Enter to continue...")
            continue

        name, command = package_list[int(choice) - 1]
        clear_screen()
        show_header()
        print("\n" + style(f"PACKAGE: {name}", "cyan", "bold"))
        print(f"{style('Catalog command:', 'gray')} {command}")
        run_install(command)


def sync_catalog(origin):
    global packages, CATALOG_VERSION

    print("\n" + style("AUTOSYNC", "cyan", "bold"))
    print(style("Checking the remote catalog...", "gray"))

    try:
        remote = download_catalog()
    except CatalogError as error:
        print(style(f"Check failed: {error}", "red"))
        if origin == "manual":
            pause("Press Enter to return to the menu...")
        return

    remote_version = remote["catalog_version"]
    if remote_version <= CATALOG_VERSION:
        if remote_version == CATALOG_VERSION:
            print(style("You already have the latest catalog version.", "green"))
        else:
            print(style("The remote catalog is older. No changes applied.", "yellow"))
        if origin == "manual":
            pause("Press Enter to return to the menu...")
        return

    added = []
    modified = []
    removed = []
    for category, entries in remote["packages"].items():
        current = packages.get(category, {})
        for name, command in entries.items():
            if name not in current:
                added.append((category, name))
            elif current[name] != command:
                modified.append((category, name))
    for category, entries in packages.items():
        remote_entries = remote["packages"].get(category, {})
        for name in entries:
            if name not in remote_entries:
                removed.append((category, name))

    print(style(f"Update available: catalog {CATALOG_VERSION} → {remote_version}", "green", "bold"))
    print(f"New packages: {len(added)}")
    print(f"Modified commands: {len(modified)}")
    print(f"Removed packages: {len(removed)}")
    for category, name in added[:12]:
        print(style(f"  + {category}/{name}", "green"))
    for category, name in modified[:12]:
        print(style(f"  ~ {category}/{name}", "yellow"))
    for category, name in removed[:12]:
        print(style(f"  - {category}/{name}", "red"))
    if len(added) + len(modified) + len(removed) > 12:
        print(style("Showing up to 12 items per type.", "gray"))

    answer = read_input(style("Apply this update? [y/N]: ", "yellow"))
    if answer.casefold() not in ("y", "yes"):
        print(style("Update cancelled. The current catalog is kept.", "yellow"))
    else:
        try:
            save_cache(remote)
        except CatalogError as error:
            print(style(str(error), "red"))
        else:
            packages = remote["packages"]
            CATALOG_VERSION = remote_version
            print(style("Catalog updated successfully.", "green", "bold"))

    if origin == "manual":
        pause("Press Enter to return to the menu...")


def main():
    global packages
    if sys.stdout.isatty():
        sync_catalog("startup")

    while True:
        clear_screen()
        categories = show_menu()
        choice = read_input("\n" + style("Select a category, B to search or U to update: ", "yellow"))

        if choice == "0":
            print("\n" + style("Goodbye!", "green", "bold"))
            break

        if choice.casefold() == "b":
            show_search()
            continue

        if choice.casefold() == "u":
            sync_catalog("manual")
            continue

        if not choice.isdigit():
            pause("\nInvalid input. Enter a number, B or U. Press Enter...")
            continue

        number = int(choice)
        if 1 <= number <= len(categories):
            show_category(categories[number - 1])
        else:
            pause("\nOption outside the menu. Press Enter to continue...")


if __name__ == "__main__":
    try:
        main()
    except BrokenPipeError:
        pass
