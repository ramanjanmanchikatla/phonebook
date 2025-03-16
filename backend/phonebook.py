import sqlite3
from functools import lru_cache

DB_PATH = 'database/contacts.db'

def connect_db():
    """
    Create a database connection with proper error handling.
    """
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row  # Enable row name access
        return conn
    except sqlite3.Error as e:
        raise Exception(f"Database connection error: {str(e)}")

def create_table():
    """
    Create the contacts table if it doesn't exist.
    """
    conn = connect_db()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "CREATE TABLE IF NOT EXISTS contacts ("
            "id INTEGER PRIMARY KEY AUTOINCREMENT, "
            "name TEXT NOT NULL, "
            "phone TEXT NOT NULL UNIQUE, "
            "email TEXT)"
        )
        conn.commit()
    except sqlite3.Error as e:
        conn.rollback()
        raise Exception(f"Error creating table: {str(e)}")
    finally:
        conn.close()

def insert_contact(name, phone, email):
    """
    Insert a new contact into the database.
    Returns True if successful, False if phone number already exists.
    Raises an exception for other errors.
    """
    conn = connect_db()
    cursor = conn.cursor()
    try:
        # Validate inputs
        if not name or not phone:
            raise ValueError("Name and phone number are required")
            
        # Clean up inputs
        name = name.strip()
        phone = phone.strip()
        email = email.strip() if email else None
        
        # Insert the contact
        cursor.execute('INSERT INTO contacts (name, phone, email) VALUES (?, ?, ?)', 
                      (name, phone, email))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        conn.rollback()
        raise ValueError("Phone number already exists!")
    except Exception as e:
        conn.rollback()
        raise Exception(f"Error adding contact: {str(e)}")
    finally:
        conn.close()

def delete_contact(phone):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM contacts WHERE phone = ?', (phone,))
    conn.commit()
    conn.close()

def update_contact(old_phone, new_name=None, new_phone=None, new_email=None):
    conn = connect_db()
    cursor = conn.cursor()
    if new_name:
        cursor.execute('UPDATE contacts SET name = ? WHERE phone = ?', (new_name, old_phone))
    if new_phone:
        cursor.execute('UPDATE contacts SET phone = ? WHERE phone = ?', (new_phone, old_phone))
    if new_email:
        cursor.execute('UPDATE contacts SET email = ? WHERE phone = ?', (new_email, old_phone))
    conn.commit()
    conn.close()

def display_contacts():
    """
    Display all contacts from the database.
    Returns a list of tuples containing contact information.
    """
    conn = connect_db()
    cursor = conn.cursor()
    try:
        cursor.execute('SELECT * FROM contacts ORDER BY name')
        rows = cursor.fetchall()
        return rows
    except Exception as e:
        raise Exception(f"Error fetching contacts: {str(e)}")
    finally:
        conn.close()

def edit_distance(s1, s2):
    """
    Calculate the Levenshtein distance between two strings.
    This helps in finding similar but not exact matches.
    """
    if len(s1) < len(s2):
        return edit_distance(s2, s1)
    if len(s2) == 0:
        return len(s1)
    
    previous_row = range(len(s2) + 1)
    for i, c1 in enumerate(s1):
        current_row = [i + 1]
        for j, c2 in enumerate(s2):
            insertions = previous_row[j + 1] + 1
            deletions = current_row[j] + 1
            substitutions = previous_row[j] + (c1 != c2)
            current_row.append(min(insertions, deletions, substitutions))
        previous_row = current_row
    
    return previous_row[-1]

@lru_cache(maxsize=50)
def fuzzy_search(keyword):
    """
    Enhanced search that handles:
    1. Partial name matches
    2. Case-insensitive search
    3. Multiple word search
    4. Search across name, phone, and email
    """
    if not keyword:
        return []
        
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute('SELECT name, phone, email FROM contacts')
    contacts = cursor.fetchall()
    result = []
    
    # Convert keyword to lowercase for case-insensitive comparison
    keyword = keyword.lower()
    search_terms = keyword.split()
    
    for contact in contacts:
        name = contact[0].lower()
        phone = contact[1].lower()
        email = contact[2].lower() if contact[2] else ""
        
        # Check if any search term is in any of the contact fields
        should_include = False
        
        # Direct partial matches
        if any(term in name or term in phone or term in email for term in search_terms):
            should_include = True
        else:
            # Fuzzy matching for names
            name_parts = name.split()
            for term in search_terms:
                for part in name_parts:
                    # Check for close matches using edit distance
                    if (len(term) > 2 and len(part) > 2 and  # Only check substantial terms
                        (term in part or  # Partial match
                         part in term or  # Partial match other way
                         edit_distance(term, part) <= min(3, len(part) // 2))):  # Fuzzy match with adaptive threshold
                        should_include = True
                        break
                if should_include:
                    break
        
        if should_include:
            result.append(contact)
    
    conn.close()
    # Sort results by relevance (exact matches first)
    result.sort(key=lambda x: sum(term in x[0].lower() for term in search_terms), reverse=True)
    return result
