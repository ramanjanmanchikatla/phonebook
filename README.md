# Advanced Phone Book

This is a complete Flask-based Advanced Phone Book application with SQLite backend and edit-distance fuzzy search.

## Folder Structure
```
AdvancedPhoneBook/
├── backend/
│   └── phonebook.py        # Backend Python logic (Insertion, Deletion, Search)
├── frontend/
│   ├── templates/
│   │   ├── base.html
│   │   ├── index.html
│   │   ├── add_contact.html
│   │   └── search_contact.html
│   └── static/
│       └── style.css
├── database/
│   └── contacts.db         # SQLite database
├── app.py                  # Flask app routes
├── requirements.txt        # Python dependencies
├── README.md               # Setup instructions
└── reports/
    └── DAA_Project_Report.docx
```

## Setup Instructions

1. **Install dependencies:**
```
pip install -r requirements.txt
```

2. **Run the Flask app:**
```
python app.py
```

3. **Access the app:**
Open `http://127.0.0.1:5000` in your browser.

