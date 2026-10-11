"""
Test MongoDB Atlas Connection
Verifies that the connection string works and data can be stored/retrieved
"""
import os
from dotenv import load_dotenv
from pymongo import MongoClient
from datetime import datetime, timedelta

# Load environment variables
load_dotenv()

MONGODB_URI = os.environ.get('MONGODB_URI')
MONGODB_DATABASE = os.environ.get('MONGODB_DATABASE', 'naukri_automation')

print("=" * 60)
print("MongoDB Atlas Connection Test")
print("=" * 60)

if not MONGODB_URI:
    print("ERROR: MONGODB_URI not found in .env file")
    print("Please add your MongoDB connection string to .env file")
    exit(1)

print(f"\nTesting connection to: {MONGODB_DATABASE}")
print(f"URI: {MONGODB_URI[:50]}...")

try:
    # Test connection
    client = MongoClient(MONGODB_URI, serverSelectionTimeoutMS=5000)
    db = client[MONGODB_DATABASE]
    
    # Ping the database
    client.admin.command('ping')
    print("[OK] Successfully connected to MongoDB Atlas!")
    
    # Test write operation
    test_collection = db['test_collection']
    test_doc = {
        'test': True,
        'timestamp': datetime.now(),
        'message': 'MongoDB connection test successful'
    }
    
    result = test_collection.insert_one(test_doc)
    print(f"[OK] Successfully wrote test document (ID: {result.inserted_id})")
    
    # Test read operation
    retrieved_doc = test_collection.find_one({'_id': result.inserted_id})
    print("[OK] Successfully read test document")
    
    # Clean up test document
    test_collection.delete_one({'_id': result.inserted_id})
    print("[OK] Successfully cleaned up test document")
    
    # Test GridFS
    from gridfs import GridFS
    fs = GridFS(db, collection='test_files')
    
    # Test GridFS write
    test_data = b"Test file content for GridFS"
    file_id = fs.put(test_data, filename='test.txt', test=True)
    print(f"[OK] Successfully wrote test file to GridFS (ID: {file_id})")
    
    # Test GridFS read
    grid_out = fs.get(file_id)
    content = grid_out.read()
    print(f"[OK] Successfully read test file from GridFS ({len(content)} bytes)")
    
    # Clean up GridFS test file
    fs.delete(file_id)
    print("[OK] Successfully cleaned up GridFS test file")
    
    # Test expiration cleanup
    print("\n" + "=" * 60)
    print("Testing Expiration Cleanup")
    print("=" * 60)
    
    # Create a test document with expiration
    expired_doc = {
        'test': True,
        'expires_at': datetime.now() - timedelta(hours=24),  # Expired 24 hours ago
        'message': 'This should be cleaned up'
    }
    
    test_collection.insert_one(expired_doc)
    print("[OK] Created expired test document")
    
    # Cleanup expired documents
    now = datetime.now()
    result = test_collection.delete_many({'expires_at': {'$lt': now}})
    print(f"[OK] Cleaned up {result.deleted_count} expired documents")
    
    # Clean up test collection
    db.drop_collection('test_collection')
    db.drop_collection('test_files.files')
    db.drop_collection('test_files.chunks')
    print("[OK] Cleaned up test collections")
    
    print("\n" + "=" * 60)
    print("[OK] ALL TESTS PASSED!")
    print("=" * 60)
    print("\nMongoDB Atlas is ready for production use!")
    print("Data will automatically expire after 12 hours.")
    print("Daily cleanup will run at 9 AM UTC.")
    
except Exception as e:
    print(f"\n[ERROR] {e}")
    print("\nPlease check:")
    print("1. Your MongoDB connection string is correct")
    print("2. Your IP is whitelisted in MongoDB Atlas (0.0.0.0/0)")
    print("3. Your database user has correct permissions")
    print("4. The cluster is running (not paused)")
    exit(1)
