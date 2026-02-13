"""
This file creates our vector database and loads scheme data into it.
Vector databases store text as numbers (embeddings) so AI can search by meaning.
"""
import os
from dotenv import load_dotenv
import chromadb
import json
from pathlib import Path
load_dotenv()  # Load environment variables
class SchemeDatabase:
    def __init__(self):
        """Initialize the database"""
        # Create a persistent database (saves to disk)
        self.client = chromadb.PersistentClient(path="./chroma_db")
        
        # Get or create collection for schemes
        self.collection = self.client.get_or_create_collection(
            name="government_schemes",
            metadata={"description": "Indian government schemes database"}
        )
        
    def load_schemes(self, json_file_path):
        """Load schemes from JSON file into database"""
        
        # Read the JSON file
        with open(json_file_path, 'r', encoding='utf-8') as f:
            schemes = json.load(f)
        
        print(f"Loading {len(schemes)} schemes into database...")
        
        # Prepare data for database
        documents = []  # Text to search through
        metadatas = []  # Structured data to return
        ids = []        # Unique IDs
        
        for scheme in schemes:
            # Create searchable text combining all important fields
            doc_text = f"""
            Scheme: {scheme['name']} ({scheme['full_name']})
            Ministry: {scheme['ministry']}
            Description: {scheme['description']}
            Eligibility: {scheme['eligibility']}
            Benefits: {scheme['benefits']}
            Documents: {scheme['documents_required']}
            How to Apply: {scheme['how_to_apply']}
            """
            
            documents.append(doc_text)
            metadatas.append(scheme)
            ids.append(scheme['id'])
        
        # Add to database
        self.collection.add(
            documents=documents,
            metadatas=metadatas,
            ids=ids
        )
        
        print(f"✓ Successfully loaded {len(schemes)} schemes!")
        print(f"Total schemes in database: {self.collection.count()}")
        
    def search_schemes(self, query, n_results=3):
        """Search for relevant schemes based on user query"""
        
        results = self.collection.query(
            query_texts=[query],
            n_results=n_results
        )
        
        return results['metadatas'][0] if results['metadatas'] else []
    
    def get_all_schemes(self):
        """Get all schemes from database"""
        return self.collection.get()

# Test the database
if __name__ == "__main__":
    # Create database instance
    db = SchemeDatabase()
    
    # Load schemes from JSON
    db.load_schemes("data/schemes_data.json")
    
    # Test search
    print("\n--- Testing Search ---")
    query = "I am a farmer looking for financial help"
    results = db.search_schemes(query, n_results=2)
    
    print(f"\nQuery: {query}")
    print(f"Found {len(results)} relevant schemes:\n")
    
    for scheme in results:
        print(f"• {scheme['name']}: {scheme['description'][:100]}...")