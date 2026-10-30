import sqlite3  # Importing SQLite for database operations
from rich.console import Console  # Importing Console from rich for styled console output
from rich.table import Table  # Importing Table from rich for displaying tabular data
import re  # Import regex module for validation

# Initialize a console object for styled output
console = Console()

# Hardcoded user credentials for login
USERS = {
    'admin': {'password': 'admin', 'role': 'admin'},
}

# Validation function to allow only letters for names
def validate_name(name):
    return bool(re.match("^[A-Za-z ]+$", name))  # Allow only letters and spaces

# Validation function to ensure email follows the correct format
def validate_email(email):
    return bool(re.match(r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$", email))  # Regex for valid email

# Function to create necessary database tables if they don't already exist
def create_tables():
    with sqlite3.connect("school.db") as conn:  # Connect to the SQLite database
        cursor = conn.cursor()
        # Create Students table
        cursor.execute("""CREATE TABLE IF NOT EXISTS Students (
            StudentID INTEGER PRIMARY KEY AUTOINCREMENT,
            Name TEXT NOT NULL,
            Age INTEGER,
            Email TEXT UNIQUE
        )""")
        # Create Teachers table
        cursor.execute("""CREATE TABLE IF NOT EXISTS Teachers (
            TeacherID INTEGER PRIMARY KEY AUTOINCREMENT,
            Name TEXT NOT NULL,
            Subject TEXT
        )""")
        # Create Courses table
        cursor.execute("""CREATE TABLE IF NOT EXISTS Courses (
            CourseID INTEGER PRIMARY KEY AUTOINCREMENT,
            CourseName TEXT NOT NULL,
            TeacherID INTEGER,
            FOREIGN KEY (TeacherID) REFERENCES Teachers(TeacherID)
        )""")
        # Create Registrations table
        cursor.execute("""CREATE TABLE IF NOT EXISTS Registrations (
            RegID INTEGER PRIMARY KEY AUTOINCREMENT,
            StudentID INTEGER,
            CourseID INTEGER,
            FOREIGN KEY (StudentID) REFERENCES Students(StudentID),
            FOREIGN KEY (CourseID) REFERENCES Courses(CourseID)
        )""")
        # Create Attendance table
        cursor.execute("""CREATE TABLE IF NOT EXISTS Attendance (
            AttendanceID INTEGER PRIMARY KEY AUTOINCREMENT,
            StudentID INTEGER,
            CourseID INTEGER,
            Date TEXT,
            Status TEXT,
            FOREIGN KEY (StudentID) REFERENCES Students(StudentID),
            FOREIGN KEY (CourseID) REFERENCES Courses(CourseID)
        )""")
        conn.commit()  # Commit changes to the database

# Function to get user input with error handling and optional validation
def get_input(prompt, cast=str, validation=None):
    while True:
        try:
            value = input(prompt)  # Get user input
            if validation and not validation(value):  # Check if validation fails
                raise ValueError("Invalid input.")  # Raise an error for invalid input
            return cast(value)  # Return the casted value
        except ValueError as e:
            print(e)  # Print the error message
            print("Try again.")  # Prompt the user to try again

# Function to handle user login
def login():
    user = input("Username: ")  # Prompt for username
    password = input("Password: ")  # Prompt for password
    # Check if the username and password match the hardcoded credentials
    if user in USERS and USERS[user]['password'] == password:
        print("Login successful.\n")
        return USERS[user]['role']  # Return the user's role
    else:
        print("Login failed.\n")
        return None  # Return None if login fails

# Function to display data in a table format using rich
def show_table(data, columns):
    table = Table(title="Results")  # Create a table with a title
    for col in columns:
        table.add_column(col)  # Add columns to the table
    for row in data:
        table.add_row(*[str(cell) for cell in row])  # Add rows to the table
    console.print(table)  # Print the table to the console

# Function to add a new record to a specified table
def add_record(table, fields):
    values = []
    for field in fields:
        if field == "Name":  # Apply name validation for the Name field
            value = get_input(f"Enter {field}: ", validation=validate_name)
        elif field == "Email":  # Apply email validation for the Email field
            value = get_input(f"Enter {field}: ", validation=validate_email)
        else:
            value = get_input(f"Enter {field}: ")
        values.append(value)
    with sqlite3.connect("school.db") as conn:
        # Insert the new record into the table
        conn.execute(f"INSERT INTO {table} ({', '.join(fields)}) VALUES ({', '.join(['?']*len(values))})", values)
        conn.commit()  # Commit changes to the database
        print(f"{table} record added.")

# Function to view all records from a specified table
def view_records(table, columns):
    with sqlite3.connect("school.db") as conn:
        cursor = conn.cursor()
        cursor.execute(f"SELECT * FROM {table}")  # Fetch all records from the table
        data = cursor.fetchall()
        show_table(data, columns)  # Display the records in a table format

# Function to update a record in a specified table
def update_record(table, fields, id_field):
    record_id = get_input(f"Enter {id_field} to update: ", int)  # Prompt for the record ID
    # Prompt for new values for each field
    updates = [get_input(f"New {field}: ") for field in fields]
    set_clause = ", ".join([f"{field} = ?" for field in fields])  # Create the SET clause for the SQL query
    with sqlite3.connect("school.db") as conn:
        # Update the record in the table
        conn.execute(f"UPDATE {table} SET {set_clause} WHERE {id_field} = ?", (*updates, record_id))
        conn.commit()  # Commit changes to the database
        print("Record updated.")

# Function to delete a record from a specified table
def delete_record(table, id_field):
    record_id = get_input(f"Enter {id_field} to delete: ", int)  # Prompt for the record ID
    with sqlite3.connect("school.db") as conn:
        # Delete the record from the table
        conn.execute(f"DELETE FROM {table} WHERE {id_field} = ?", (record_id,))
        conn.commit()  # Commit changes to the database
        print("Record deleted.")

# Function to display a menu for managing a specific entity (e.g., Students, Teachers)
def entity_menu(title, table, fields, id_field, columns):
    while True:
        # Display the entity menu
        print(f"\n-- {title} Menu --")
        print("1. Add\n2. View\n3. Update\n4. Delete\n0. Back")
        choice = get_input("Choice: ", int)  # Prompt for the user's choice
        if choice == 1:
            add_record(table, fields)  # Add a new record
        elif choice == 2:
            view_records(table, columns)  # View all records
        elif choice == 3:
            update_record(table, fields, id_field)  # Update a record
        elif choice == 4:
            delete_record(table, id_field)  # Delete a record
        elif choice == 0:
            break  # Exit the menu
        else:
            print("Invalid choice.")  # Handle invalid input

# Main function to run the program
def main():
    create_tables()  # Ensure all necessary tables are created
    role = login()  # Prompt the user to log in
    if not role:
        return  # Exit if login fails
    while True:
        # Display the main menu
        print("\nMain Menu:")
        print("1. Students\n2. Teachers\n3. Courses\n4. Registrations\n5. Attendance\n0. Exit")
        choice = get_input("Choose: ", int)  # Prompt for the user's choice
        if choice == 1:
            # Open the Students menu
            entity_menu("Students", "Students", ["Name", "Age", "Email"], "StudentID", ["ID", "Name", "Age", "Email"])
        elif choice == 2:
            # Open the Teachers menu
            entity_menu("Teachers", "Teachers", ["Name", "Subject"], "TeacherID", ["ID", "Name", "Subject"])
        elif choice == 3:
            # Open the Courses menu
            entity_menu("Courses", "Courses", ["CourseName", "TeacherID"], "CourseID", ["ID", "Course", "TeacherID"])
        elif choice == 4:
            # Open the Registrations menu
            entity_menu("Registrations", "Registrations", ["StudentID", "CourseID"], "RegID", ["ID", "StudentID", "CourseID"])
        elif choice == 5:
            # Open the Attendance menu
            entity_menu("Attendance", "Attendance", ["StudentID", "CourseID", "Date", "Status"], "AttendanceID", ["ID", "StudentID", "CourseID", "Date", "Status"])
        elif choice == 0:
            print("Goodbye!")  # Exit the program
            break
        else:
            print("Invalid option.")  # Handle invalid input

# Entry point of the program
if __name__ == "__main__":
    main()