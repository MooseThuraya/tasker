#!/usr/bin/env python3
"""
Simple script to test database connection
"""

import os
import sqlite3
import sys
from pathlib import Path

try:
    # Print all relevant info
    script_dir = os.path.dirname(os.path.abspath(__file__))
    print(f"Script directory: {script_dir}")
    
    os.chdir(script_dir)
    print(f"Current working directory: {os.getcwd()}")
    
    # Try to create a test database directly
    instance_dir = os.path.join(script_dir, 'instance')
    if not os.path.exists(instance_dir):
        print(f"Creating instance directory: {instance_dir}")
        os.makedirs(instance_dir)
    
    db_path = os.path.join(instance_dir, 'test.db')
    print(f"Testing database at: {db_path}")
    
    # Try SQLite connection directly
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Create a test table
    cursor.execute('CREATE TABLE IF NOT EXISTS test (id INTEGER PRIMARY KEY, name TEXT)')
    
    # Insert a test record
    cursor.execute('INSERT INTO test VALUES (1, "test")')
    conn.commit()
    
    # Query the test record
    cursor.execute('SELECT * FROM test')
    result = cursor.fetchall()
    print(f"Test query result: {result}")
    
    conn.close()
    
    print("SQLite direct test passed!")
    
    # Now test with Flask-SQLAlchemy
    from flask import Flask
    from flask_sqlalchemy import SQLAlchemy
    
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    db = SQLAlchemy(app)
    
    class TestModel(db.Model):
        id = db.Column(db.Integer, primary_key=True)
        name = db.Column(db.String(50))
    
    with app.app_context():
        db.create_all()
        
        # Check if the test table exists
        test_record = TestModel.query.first()
        print(f"Flask-SQLAlchemy test record: {test_record}")
        
        # Create a test record
        if not test_record:
            test_record = TestModel(id=1, name="SQLAlchemy Test")
            db.session.add(test_record)
            db.session.commit()
            print("Added test record")
        
        # Verify the record was created
        test_record = TestModel.query.first()
        print(f"Flask-SQLAlchemy verification: {test_record.id} - {test_record.name}")
    
    print("Flask-SQLAlchemy test passed!")
    
    # All tests passed
    print("\nALL DATABASE TESTS PASSED!")
    print(f"Database at {db_path} is working correctly.")
    
except Exception as e:
    print(f"ERROR: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)