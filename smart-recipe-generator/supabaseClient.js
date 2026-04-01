// supabaseClient.js

import { createClient } from '@supabase/supabase-js';

// Replace these with your actual Supabase URL and Anon Key
const SUPABASE_URL = 'https://hazgghhpurqmxaywejxi.supabase.co';  // Your Supabase URL
const SUPABASE_ANON_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImhhemdnaGhwdXJxbXhheXdlanhpIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDM4NzYyNzIsImV4cCI6MjA1OTQ1MjI3Mn0.66YnxFAv1udH-E4ov4uphWxH2-d3Wzsf1wHg9WDd8uk';  // Your Supabase Anon Key

// Initialize the Supabase client
const supabase = createClient(SUPABASE_URL, SUPABASE_ANON_KEY);

export default supabase;
