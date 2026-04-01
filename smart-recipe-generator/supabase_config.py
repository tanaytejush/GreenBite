from supabase import create_client, Client

url = "https://hazgghhpurqmxaywejxi.supabase.co"
key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImhhemdnaGhwdXJxbXhheXdlanhpIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDM4NzYyNzIsImV4cCI6MjA1OTQ1MjI3Mn0.66YnxFAv1udH-E4ov4uphWxH2-d3Wzsf1wHg9WDd8uk"

supabase: Client = create_client(url, key)
