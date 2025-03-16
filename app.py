from flask import Flask, render_template, request, redirect, url_for, flash
from backend import phonebook
import os

app = Flask(__name__)
app.secret_key = os.urandom(24)  # Required for flash messages

# Ensure database directory exists
os.makedirs('database', exist_ok=True)

# Initialize DB
phonebook.create_table()

@app.route('/')
def index():
    try:
        contacts = phonebook.display_contacts()
        return render_template('index.html', contacts=contacts)
    except Exception as e:
        flash(f'Error loading contacts: {str(e)}', 'danger')
        return render_template('index.html', contacts=[])

@app.route('/add', methods=['GET', 'POST'])
def add_contact():
    if request.method == 'POST':
        try:
            name = request.form['name'].strip()
            phone = request.form['phone'].strip()
            email = request.form['email'].strip()
            
            if not name or not phone:
                flash('Name and phone number are required!', 'danger')
                return render_template('add_contact.html')
            
            if not phone.replace('+', '').replace('-', '').replace(' ', '').replace('(', '').replace(')', '').isdigit():
                flash('Invalid phone number format!', 'danger')
                return render_template('add_contact.html')
            
            phonebook.insert_contact(name, phone, email)
            flash('Contact added successfully!', 'success')
            return redirect(url_for('index'))
        except Exception as e:
            flash(f'Error adding contact: {str(e)}', 'danger')
            return render_template('add_contact.html')
    return render_template('add_contact.html')

@app.route('/delete/<phone>')
def delete_contact(phone):
    try:
        phonebook.delete_contact(phone)
        flash('Contact deleted successfully!', 'success')
    except Exception as e:
        flash(f'Error deleting contact: {str(e)}', 'danger')
    return redirect(url_for('index'))

@app.route('/update/<phone>', methods=['GET', 'POST'])
def update_contact(phone):
    if request.method == 'POST':
        try:
            new_name = request.form['name'].strip()
            new_phone = request.form['phone'].strip()
            new_email = request.form['email'].strip()
            
            if not new_name or not new_phone:
                flash('Name and phone number are required!', 'danger')
                return redirect(url_for('update_contact', phone=phone))
            
            if not new_phone.replace('+', '').replace('-', '').replace(' ', '').replace('(', '').replace(')', '').isdigit():
                flash('Invalid phone number format!', 'danger')
                return redirect(url_for('update_contact', phone=phone))
            
            phonebook.update_contact(phone, new_name, new_phone, new_email)
            flash('Contact updated successfully!', 'success')
            return redirect(url_for('index'))
        except Exception as e:
            flash(f'Error updating contact: {str(e)}', 'danger')
            return redirect(url_for('update_contact', phone=phone))
    
    try:
        contacts = phonebook.display_contacts()
        contact = next((c for c in contacts if c[2] == phone), None)
        if not contact:
            flash('Contact not found!', 'danger')
            return redirect(url_for('index'))
        return render_template('add_contact.html', contact=contact)
    except Exception as e:
        flash(f'Error loading contact: {str(e)}', 'danger')
        return redirect(url_for('index'))

@app.route('/search', methods=['GET', 'POST'])
def search_contact():
    results = []
    if request.method == 'POST':
        try:
            keyword = request.form['keyword'].strip()
            if keyword:
                results = phonebook.fuzzy_search(keyword)
        except Exception as e:
            flash(f'Error searching contacts: {str(e)}', 'danger')
    return render_template('search_contact.html', results=results)

if __name__ == '__main__':
    app.run(debug=True)
