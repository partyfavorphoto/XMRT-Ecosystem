import psycopg2

try:
    conn = psycopg2.connect("postgresql://postgres:T8VZSiTk3RInnBATYzDemKaNQdPmxPzl2ShDr6obsPw@vlaikrbfunhhnihavxky.supabase.co:5432/postgres")
    cur = conn.cursor()
    cur.execute("SELECT 1")
    print("Database connection successful!")
    cur.close()
    conn.close()
except Exception as e:
    print(f"Database connection failed: {e}")


