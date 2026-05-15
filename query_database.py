#!/usr/bin/env python3
"""
Query the SQLite database and display schema and records
"""
import sqlite3
import json
from datetime import datetime

db_path = 'detections.db'

try:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    print("=" * 80)
    print("DATABASE SCHEMA")
    print("=" * 80)
    
    # Get all tables
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = cursor.fetchall()
    
    if not tables:
        print("No tables found in database")
    else:
        for table_name in tables:
            table = table_name[0]
            print(f"\n📋 TABLE: {table}")
            print("-" * 80)
            
            # Get table schema
            cursor.execute(f"PRAGMA table_info({table})")
            columns = cursor.fetchall()
            
            print(f"{'Column Name':<25} {'Type':<15} {'Nullable':<10} {'Primary Key':<12}")
            print("-" * 80)
            for col in columns:
                col_id, col_name, col_type, not_null, default, pk = col
                nullable = "NO" if not_null else "YES"
                is_pk = "YES" if pk else "NO"
                print(f"{col_name:<25} {col_type:<15} {nullable:<10} {is_pk:<12}")
    
    print("\n" + "=" * 80)
    print("TABLE STATISTICS")
    print("=" * 80)
    
    # Get record count
    cursor.execute("SELECT COUNT(*) FROM detections")
    count = cursor.fetchone()[0]
    print(f"\n📊 Total Records in 'detections' table: {count:,}")
    
    if count > 0:
        # Get attack type distribution
        cursor.execute("""
            SELECT attack_type, COUNT(*) as count, 
                   ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM detections), 2) as percentage
            FROM detections 
            GROUP BY attack_type 
            ORDER BY count DESC
        """)
        dist = cursor.fetchall()
        
        print(f"\n🎯 Attack Type Distribution:")
        print("-" * 80)
        print(f"{'Attack Type':<20} {'Count':<15} {'Percentage':<15}")
        print("-" * 80)
        for attack_type, count_val, percentage in dist:
            print(f"{attack_type:<20} {count_val:<15,} {percentage:<15}%")
        
        # Get is_attack distribution
        cursor.execute("""
            SELECT is_attack, COUNT(*) as count,
                   ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM detections), 2) as percentage
            FROM detections 
            GROUP BY is_attack 
            ORDER BY is_attack
        """)
        attack_dist = cursor.fetchall()
        
        print(f"\n🚨 Attack vs Normal Distribution:")
        print("-" * 80)
        print(f"{'Classification':<20} {'Count':<15} {'Percentage':<15}")
        print("-" * 80)
        for is_attack, count_val, percentage in attack_dist:
            classification = "ATTACK" if is_attack else "NORMAL"
            print(f"{classification:<20} {count_val:<15,} {percentage:<15}%")
        
        # Get confidence statistics
        cursor.execute("""
            SELECT 
                MIN(confidence) as min_conf,
                MAX(confidence) as max_conf,
                ROUND(AVG(confidence), 4) as avg_conf,
                ROUND(AVG(latency_ms), 4) as avg_latency
            FROM detections
        """)
        stats = cursor.fetchone()
        
        print(f"\n📈 Confidence & Latency Statistics:")
        print("-" * 80)
        print(f"Min Confidence:     {stats[0]:.4f}")
        print(f"Max Confidence:     {stats[1]:.4f}")
        print(f"Avg Confidence:     {stats[2]:.4f}")
        print(f"Avg Latency (ms):   {stats[3]:.4f}")
        
        # Get source distribution
        cursor.execute("""
            SELECT source, COUNT(*) as count
            FROM detections 
            GROUP BY source
        """)
        sources = cursor.fetchall()
        
        print(f"\n📡 Detection Source Distribution:")
        print("-" * 80)
        print(f"{'Source':<20} {'Count':<15}")
        print("-" * 80)
        for source, count_val in sources:
            print(f"{source:<20} {count_val:<15,}")
        
        # Get sample records
        print(f"\n" + "=" * 80)
        print("SAMPLE RECORDS (First 10)")
        print("=" * 80)
        
        cursor.execute("""
            SELECT id, timestamp, attack_type, is_attack, confidence, latency_ms, source
            FROM detections 
            LIMIT 10
        """)
        rows = cursor.fetchall()
        
        print(f"\n{'ID':<5} {'Timestamp':<25} {'Attack Type':<15} {'Is Attack':<10} {'Confidence':<12} {'Latency':<10} {'Source':<10}")
        print("-" * 100)
        for row in rows:
            is_attack_str = "YES" if row[3] else "NO"
            print(f"{row[0]:<5} {row[1]:<25} {row[2]:<15} {is_attack_str:<10} {row[4]:<12.4f} {row[5]:<10.4f} {row[6]:<10}")
        
        # Get latest records
        print(f"\n" + "=" * 80)
        print("LATEST RECORDS (Last 10)")
        print("=" * 80)
        
        cursor.execute("""
            SELECT id, timestamp, attack_type, is_attack, confidence, latency_ms, source
            FROM detections 
            ORDER BY id DESC
            LIMIT 10
        """)
        rows = cursor.fetchall()
        
        print(f"\n{'ID':<5} {'Timestamp':<25} {'Attack Type':<15} {'Is Attack':<10} {'Confidence':<12} {'Latency':<10} {'Source':<10}")
        print("-" * 100)
        for row in rows:
            is_attack_str = "YES" if row[3] else "NO"
            print(f"{row[0]:<5} {row[1]:<25} {row[2]:<15} {is_attack_str:<10} {row[4]:<12.4f} {row[5]:<10.4f} {row[6]:<10}")
    
    conn.close()
    
except FileNotFoundError:
    print(f"❌ Database file not found: {db_path}")
    print("Run 'python app.py' to create the database and start detecting intrusions")
except Exception as e:
    print(f"❌ Error: {e}")
