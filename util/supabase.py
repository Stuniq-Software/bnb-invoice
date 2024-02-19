import supabase
import os

supabase_client: supabase.Client = supabase.create_client(
    os.getenv("SUPABASE_URL"),
    os.getenv("SUPABASE_KEY")
)