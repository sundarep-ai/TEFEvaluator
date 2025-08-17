#!/usr/bin/env python3
"""
TEF AI Practice Tool - Database Migration Script
Adds new columns for enhanced evaluation data
"""

import sqlite3
import os
from datetime import datetime

def migrate_database():
    """Migrate the database to add new evaluation columns."""
    
    db_path = "tef_evaluator.db"
    
    if not os.path.exists(db_path):
        print("❌ Database file not found. Please run the application first to create the database.")
        return False
    
    try:
        # Connect to the database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        print("🔄 Starting database migration...")
        
        # Check if new columns already exist
        cursor.execute("PRAGMA table_info(evaluations)")
        columns = [column[1] for column in cursor.fetchall()]
        
        new_columns = [
            ("detailed_errors", "TEXT"),
            ("consolidated_scores", "TEXT"), 
            ("cross_task_analysis", "TEXT"),
            ("final_tef_writing_score", "INTEGER")
        ]
        
        added_columns = []
        
        for column_name, column_type in new_columns:
            if column_name not in columns:
                try:
                    cursor.execute(f"ALTER TABLE evaluations ADD COLUMN {column_name} {column_type}")
                    added_columns.append(column_name)
                    print(f"✅ Added column: {column_name}")
                except Exception as e:
                    print(f"❌ Failed to add column {column_name}: {e}")
            else:
                print(f"ℹ️  Column {column_name} already exists")
        
        # Commit changes
        conn.commit()
        
        if added_columns:
            print(f"\n🎉 Migration completed successfully!")
            print(f"Added columns: {', '.join(added_columns)}")
        else:
            print("\nℹ️  No new columns were added - database is already up to date")
        
        # Verify the migration
        cursor.execute("PRAGMA table_info(evaluations)")
        final_columns = [column[1] for column in cursor.fetchall()]
        print(f"\n📊 Current table structure:")
        for column in final_columns:
            print(f"  - {column}")
        
        return True
        
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        return False
        
    finally:
        if conn:
            conn.close()

def rollback_migration():
    """Rollback the migration by removing the new columns."""
    
    db_path = "tef_evaluator.db"
    
    if not os.path.exists(db_path):
        print("❌ Database file not found.")
        return False
    
    try:
        # Connect to the database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        print("🔄 Starting rollback...")
        
        # Note: SQLite doesn't support DROP COLUMN directly
        # We would need to recreate the table without the new columns
        print("⚠️  Warning: SQLite doesn't support DROP COLUMN directly.")
        print("   To rollback, you would need to recreate the table.")
        print("   This is not implemented for safety reasons.")
        
        return False
        
    except Exception as e:
        print(f"❌ Rollback failed: {e}")
        return False
        
    finally:
        if conn:
            conn.close()

def check_database_status():
    """Check the current status of the database."""
    
    db_path = "tef_evaluator.db"
    
    if not os.path.exists(db_path):
        print("❌ Database file not found.")
        return
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        print("📊 Database Status:")
        print(f"  Database: {db_path}")
        print(f"  Size: {os.path.getsize(db_path)} bytes")
        print(f"  Last modified: {datetime.fromtimestamp(os.path.getmtime(db_path))}")
        
        # Check evaluations table
        cursor.execute("PRAGMA table_info(evaluations)")
        columns = cursor.fetchall()
        
        print(f"\n📋 Evaluations table columns ({len(columns)} total):")
        for column in columns:
            print(f"  - {column[1]} ({column[2]})")
        
        # Check record count
        cursor.execute("SELECT COUNT(*) FROM evaluations")
        count = cursor.fetchone()[0]
        print(f"\n📈 Total evaluations: {count}")
        
        # Check for new schema data
        cursor.execute("SELECT COUNT(*) FROM evaluations WHERE detailed_errors IS NOT NULL")
        detailed_errors_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM evaluations WHERE consolidated_scores IS NOT NULL")
        consolidated_scores_count = cursor.fetchone()[0]
        
        print(f"\n🔍 New schema usage:")
        print(f"  Evaluations with detailed errors: {detailed_errors_count}")
        print(f"  Evaluations with consolidated scores: {consolidated_scores_count}")
        
    except Exception as e:
        print(f"❌ Status check failed: {e}")
        
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        
        if command == "migrate":
            migrate_database()
        elif command == "rollback":
            rollback_migration()
        elif command == "status":
            check_database_status()
        else:
            print("Usage: python migrations.py [migrate|rollback|status]")
            print("  migrate  - Add new columns to the database")
            print("  rollback - Remove new columns (not implemented for SQLite)")
            print("  status   - Check database status")
    else:
        print("TEF AI Practice Tool - Database Migration")
        print("========================================")
        print()
        print("Available commands:")
        print("  python migrations.py migrate  - Add new columns")
        print("  python migrations.py status   - Check database status")
        print()
        print("The migration will add the following columns to the evaluations table:")
        print("  - detailed_errors: Detailed error analysis in French")
        print("  - consolidated_scores: Combined scores for both tasks")
        print("  - cross_task_analysis: Comparative analysis between tasks")
        print("  - final_tef_writing_score: Final TEF score (0-450)")
        print()
        print("Run 'python migrations.py migrate' to proceed.")
