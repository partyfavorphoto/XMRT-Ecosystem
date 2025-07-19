import os
from supabase import create_client, Client

# Set environment variables
os.environ['SUPABASE_URL'] = 'https://vlaikrbfunhhnihavxky.supabase.co'
os.environ['SUPABASE_KEY'] = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InZsYWlrcmJmdW5oaG5paGF2eGt5Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTI3MTI5MjUsImV4cCI6MjA2ODI4ODkyNX0.T8VZSiTk3RInnBATYzDemKaNQdPmxPzl2ShDr6obsPw'

try:
    url: str = os.environ.get("SUPABASE_URL")
    key: str = os.environ.get("SUPABASE_KEY")
    supabase: Client = create_client(url, key)
    
    # Test connection by trying to fetch from a table
    response = supabase.table('test').select("*").execute()
    print("Supabase client connection successful!")
    print(f"Response: {response}")
    
except Exception as e:
    print(f"Supabase client connection failed: {e}")

