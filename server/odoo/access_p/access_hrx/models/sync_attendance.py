import psycopg2
from psycopg2 import sql
import os

odoo_conn_info = {
    'dbname': 'new_db',
    'user': 'openpg',
    'password': 'openpgpwd',
    'host': '192.168.42.28',
    'port': '5432'
}

mobile_conn_info = {
    'dbname': 'hrx_database',
    'user': 'postgres',
    'password': 'CLxIT@)@$',
    'host': '192.168.43.251',
    'port': '5432'
}

# Path to the text file storing the latest write_date
write_date_file = 'latest_write_date.txt'

def get_latest_write_date():
    if os.path.exists(write_date_file):
        with open(write_date_file, 'r') as file:
            content = file.read().strip()
            return content if content else None
    return None

def set_latest_write_date(write_date):
    with open(write_date_file, 'w') as file:
        file.write(write_date)

def transfer_mobile_attendance_data():
    # Establish connections
    odoo_conn = psycopg2.connect(**odoo_conn_info)
    mobile_conn = psycopg2.connect(**mobile_conn_info)

    try:
        odoo_cursor = odoo_conn.cursor()
        mobile_cursor = mobile_conn.cursor()

        # Get the latest write_date
        latest_write_date = get_latest_write_date()

        # Prepare the query based on the latest write_date
        if latest_write_date:
            query = sql.SQL("""
                SELECT * FROM hrx_attendance
                WHERE write_date > %s
            """)
            mobile_cursor.execute(query, (latest_write_date,))
        else:
            query = sql.SQL("""
                SELECT * FROM hrx_attendance
            """)
            mobile_cursor.execute(query)

        rows = mobile_cursor.fetchall()
        if rows:
            new_latest_write_date = max(row[9] for row in rows)  # Assuming write_date is at index 9
            for row in rows:
                odoo_cursor.execute("""
                    INSERT INTO hr_attendance (employee_id, in_latitude, in_longitude, out_latitude, out_longitude, check_in, check_out, create_date, write_date, worked_hours, attn_id)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (attn_id) DO UPDATE
                    SET employee_id = EXCLUDED.employee_id,
                        in_latitude = EXCLUDED.in_latitude,
                        in_longitude = EXCLUDED.in_longitude,
                        out_latitude = EXCLUDED.out_latitude,
                        out_longitude = EXCLUDED.out_longitude,
                        check_in = EXCLUDED.check_in,
                        check_out = EXCLUDED.check_out,
                        create_date = EXCLUDED.create_date,
                        write_date = EXCLUDED.write_date,
                        worked_hours = EXCLUDED.worked_hours
                """, row[1:])

            # Update the latest write_date
            if not latest_write_date or (new_latest_write_date > latest_write_date):
                set_latest_write_date(new_latest_write_date)

        # Commit the transactions
        odoo_conn.commit()
        mobile_conn.commit()

    except Exception as e:
        print(f"Error: {e}")
        odoo_conn.rollback()
        mobile_conn.rollback()

    finally:
        odoo_cursor.close()
        mobile_cursor.close()
        odoo_conn.close()
        mobile_conn.close()

# Call the function
transfer_mobile_attendance_data()
