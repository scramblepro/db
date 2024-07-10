import psycopg2

def create_db(conn):
    with conn.cursor() as cur:
        cur.execute("""
        CREATE TABLE IF NOT EXISTS clients (
            id SERIAL PRIMARY KEY,
            first_name VARCHAR(50),
            last_name VARCHAR(50),
            email VARCHAR(100) UNIQUE
        );
        """)
        cur.execute("""
        CREATE TABLE IF NOT EXISTS phones (
            id SERIAL PRIMARY KEY,
            client_id INTEGER REFERENCES clients(id) ON DELETE CASCADE,
            phone VARCHAR(20)
        );
        """)
        conn.commit()

def add_client(conn, first_name, last_name, email, phones=None):
    with conn.cursor() as cur:
        cur.execute("""
        INSERT INTO clients (first_name, last_name, email) VALUES (%s, %s, %s) RETURNING id;
        """, (first_name, last_name, email))
        client_id = cur.fetchone()[0]
        if phones:
            for phone in phones:
                cur.execute("""
                INSERT INTO phones (client_id, phone) VALUES (%s, %s);
                """, (client_id, phone))
        conn.commit()
        return client_id

def add_phone(conn, client_id, phone):
    with conn.cursor() as cur:
        cur.execute("""
        INSERT INTO phones (client_id, phone) VALUES (%s, %s);
        """, (client_id, phone))
        conn.commit()

def change_client(conn, client_id, first_name=None, last_name=None, email=None, phones=None):
    with conn.cursor() as cur:
        if first_name:
            cur.execute("""
            UPDATE clients SET first_name = %s WHERE id = %s;
            """, (first_name, client_id))
        if last_name:
            cur.execute("""
            UPDATE clients SET last_name = %s WHERE id = %s;
            """, (last_name, client_id))
        if email:
            cur.execute("""
            UPDATE clients SET email = %s WHERE id = %s;
            """, (email, client_id))
        if phones is not None:
            cur.execute("""
            DELETE FROM phones WHERE client_id = %s;
            """, (client_id,))
            for phone in phones:
                cur.execute("""
                INSERT INTO phones (client_id, phone) VALUES (%s, %s);
                """, (client_id, phone))
        conn.commit()

def delete_phone(conn, client_id, phone):
    with conn.cursor() as cur:
        cur.execute("""
        DELETE FROM phones WHERE client_id = %s AND phone = %s;
        """, (client_id, phone))
        conn.commit()

def delete_client(conn, client_id):
    with conn.cursor() as cur:
        cur.execute("""
        DELETE FROM phones WHERE client_id = %s;
        """, (client_id,))
        cur.execute("""
        DELETE FROM clients WHERE id = %s;
        """, (client_id,))
        conn.commit()

def find_client(conn, first_name=None, last_name=None, email=None, phone=None):
    with conn.cursor() as cur:
        query = """
        SELECT c.id, c.first_name, c.last_name, c.email, p.phone
        FROM clients c
        LEFT JOIN phones p ON c.id = p.client_id
        WHERE TRUE
        """
        params = []
        if first_name:
            query += " AND c.first_name = %s"
            params.append(first_name)
        if last_name:
            query += " AND c.last_name = %s"
            params.append(last_name)
        if email:
            query += " AND c.email = %s"
            params.append(email)
        if phone:
            query += " AND p.phone = %s"
            params.append(phone)
        cur.execute(query, tuple(params))
        results = cur.fetchall()
        return results

# Пример использования функций

with psycopg2.connect(database="python", user="postgres", password="******* ;)))", options='-c client_encoding=UTF8') as conn:
    create_db(conn)

    client_id = add_client(conn, "John", "Doe", "john.doe@example.com", ["1234567890", "0987654321"])
    print(f"Added client with ID: {client_id}")

    add_phone(conn, client_id, "5555555555")
    print("Added another phone number.")

    change_client(conn, client_id, first_name="Jonathan", phones=["2222222222"])
    print("Updated client information.")

    delete_phone(conn, client_id, "5555555555")
    print("Deleted a phone number.")

    results = find_client(conn, first_name="Jonathan")
    print("Found clients:", results)

    delete_client(conn, client_id)
    print("Deleted client.")

conn.close()
