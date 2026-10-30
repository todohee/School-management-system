"""
main.py
Entry point for the School Management System.
Coventry University – KZZ02DTIF | Software and Databases
Author: Student

Run:  python main.py
"""

import sys

from database.db_manager import initialise_database
from utils.auth import login
from utils.display import print_header, print_error
from ui.student_ui import student_menu
from ui.teacher_ui import teacher_menu
from ui.course_ui import course_menu
from ui.registration_ui import registration_menu


def main_menu() -> None:
    """
    Main application loop (R9).
    Keeps running until the user selects 'Exit'.
    Uses match-case for clean dispatch (O5).
    """
    options = {
        "1": ("Student Management",      student_menu),
        "2": ("Teacher Management",      teacher_menu),
        "3": ("Course Management",       course_menu),
        "4": ("Registration Management", registration_menu),
        "0": ("Exit",                    None),
    }

    while True:
        print_header("School Management System – Main Menu")
        for key, (label, _) in options.items():
            print(f"   [{key}] {label}")

        choice = input("\n  Enter choice: ").strip()

        if choice == "0":
            print("\n  Goodbye!\n")
            sys.exit(0)

        action = options.get(choice)
        if action:
            try:
                action[1]()
            except KeyboardInterrupt:
                print("\n  Returning to main menu...")
            except Exception as err:  # R6 – top-level exception guard
                print_error(f"An unexpected error occurred: {err}")
        else:
            print_error("Invalid option. Please choose from the menu.")


if __name__ == "__main__":
    # 1. Set up the database (idempotent – safe to run every time)
    initialise_database()

    # 2. Authenticate administrator (O1)
    if not login():
        sys.exit(1)

    # 3. Enter the main application loop
    main_menu()
