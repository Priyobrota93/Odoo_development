from . import test_portal_relation
from . import hr_employee_mobile_access
from . import hr_conn_input_form
from . import hr_attendance
from . import hr_attendance_request
from . import hr_expense
from . import hr_expense_sheet
from . import pg_connection
# from . import attendance_sync
# from . import sync_attendance
# from . import hr_hrx_expense_sync



# INSERT INTO hrx_attendance (employee_id, in_latitude, in_longitude, out_latitude, out_longitude, check_in, check_out, create_date, write_date, worked_hours, update) VALUES (46,  37.4219999,  -122.0840575,0.0000000, 0.0000000, '2024-08-11 08:00:00', Null,'2024-08-11 08:01:00','2024-08-11 08:01:00', 0, False);

#  UPDATE hrx_attendance SET write_date = '2024-08-10 08:31:00', out_latitude = 37.4220936, out_longitude = -122.083922, check_out = '2024-08-10 08:30:00', worked_hours = 1.30 WHERE attn_id = 155;


# UPDATE sync_status SET latest_write_date = Null, latest_write_date = Null WHERE id = 1;