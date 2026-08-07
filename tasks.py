# from celery_app import celery
# from flask_mail import Message
# import csv
# import os
# from datetime import datetime, date
# import logging

# # Setup logging
# logging.basicConfig(level=logging.INFO)
# logger = logging.getLogger(__name__)


# def _get_flask_resources():
#     from app import app, db, mail
#     from app import Trek, Booking, User
#     return app, db, mail, Trek, Booking, User


# # TASK 1: Send daily reminders at 8 AM
# @celery.task
# def send_daily_reminder():
#     """Send reminder emails to people about treks starting today"""
#     try:
#         app, db, mail, Trek, Booking, User = _get_flask_resources()
#         with app.app_context():
#             # Get today's date
#             today = date.today()
            
#             # Find treks that start today
#             treks_today = Trek.query.filter(Trek.start_date == today).all()
            
#             if not treks_today:
#                 print("No treks today")
#                 return "No treks today"
            
#             # For each trek
#             for trek in treks_today:
#                 # Get all people booked on this trek
#                 bookings = Booking.query.filter_by(trek_id=trek.id).all()
                
#                 # Send email to each person
#                 for booking in bookings:
#                     user = booking.user
#                     subject = f"Reminder: {trek.name} starts today!"
#                     body = f"""
#                     Hi {user.name},
                    
#                     Your trek {trek.name} starts today!
                    
#                     Details:
#                     - Location: {trek.location}
#                     - Duration: {trek.duration} days
#                     - Difficulty: {trek.difficulty}
                    
#                     Please arrive on time!
                    
#                     Thanks,
#                     Trekking Team
#                     """
                    
#                     # Send the email
#                     try:
#                         msg = Message(subject, recipients=[user.email], body=body)
#                         mail.send(msg)
#                         print(f"Sent email to {user.email} for trek {trek.name}")
#                     except Exception as e:
#                         print(f"Failed to send email: {e}")
            
#             return "Reminders sent"
    
#     except Exception as e:
#         print(f"Error in send_daily_reminder: {e}")
#         return f"Error: {e}"


# # TASK 2: Generate monthly report on 1st at 9 AM
# @celery.task
# def generate_monthly_report():
#     """Make a monthly report and send to admin"""
#     try:
#         app, db, mail, Trek, Booking, User = _get_flask_resources()
#         with app.app_context():
#             # Get dates for this month
#             today = date.today()
#             first_day = today.replace(day=1)
            
#             # Count treks this month
#             treks_count = Trek.query.filter(Trek.start_date >= first_day).count()
            
#             # Count participants
#             participants_count = Booking.query.count()
            
#             # Create reports folder
#             reports_dir = os.path.join(app.root_path, 'reports')
#             if not os.path.exists(reports_dir):
#                 os.makedirs(reports_dir)
            
#             # Create HTML report
#             month_str = today.strftime('%B %Y')
#             html_report = f"""
#             <html>
#             <head>
#                 <title>Monthly Report</title>
#                 <style>
#                     body {{ font-family: Arial; margin: 20px; }}
#                     h1 {{ color: #333; }}
#                     p {{ font-size: 16px; }}
#                 </style>
#             </head>
#             <body>
#                 <h1>Monthly Trek Report - {month_str}</h1>
#                 <p><strong>Total Treks:</strong> {treks_count}</p>
#                 <p><strong>Total Participants:</strong> {participants_count}</p>
#                 <p><strong>Report Date:</strong> {datetime.now()}</p>
#             </body>
#             </html>
#             """
            
#             # Save the file
#             filename = f"monthly_report_{today.strftime('%Y_%m')}.html"
#             filepath = os.path.join(reports_dir, filename)
            
#             with open(filepath, 'w') as f:
#                 f.write(html_report)
            
#             print(f"Report saved: {filepath}")
            
#             # Send email to admin
#             admin_email = os.getenv('ADMIN_EMAIL', 'admin@example.com')
#             try:
#                 msg = Message(
#                     f"Monthly Report - {month_str}",
#                     recipients=[admin_email],
#                     html=html_report
#                 )
#                 mail.send(msg)
#                 print(f"Report sent to {admin_email}")
#             except Exception as e:
#                 print(f"Error sending email: {e}")
            
#             return "Report generated"
    
#     except Exception as e:
#         print(f"Error in generate_monthly_report: {e}")
#         return f"Error: {e}"


# # TASK 3: Export user's trek history as CSV
# @celery.task
# def export_user_trekking_history(user_id):
#     """Create CSV file with user's trek bookings"""
#     try:
#         app, db, mail, Trek, Booking, User = _get_flask_resources()
#         with app.app_context():
#             # Get the user
#             user = User.query.get(user_id)
#             if not user:
#                 return "User not found"
            
#             # Get all bookings
#             bookings = Booking.query.filter_by(user_id=user_id).all()
            
#             # Create exports folder
#             exports_dir = os.path.join(app.root_path, 'exports')
#             if not os.path.exists(exports_dir):
#                 os.makedirs(exports_dir)
            
#             # Create filename with timestamp
#             time_str = datetime.now().strftime('%Y%m%d_%H%M%S')
#             filename = f"user_{user_id}_history_{time_str}.csv"
#             filepath = os.path.join(exports_dir, filename)
            
#             # Write CSV file
#             with open(filepath, 'w', newline='') as f:
#                 writer = csv.writer(f)
                
#                 # Write header
#                 writer.writerow(['Trek Name', 'Location', 'Difficulty', 'Duration', 'Start Date', 'Status'])
                
#                 # Write each trek booking
#                 for booking in bookings:
#                     trek = booking.trek
#                     writer.writerow([
#                         trek.name,
#                         trek.location,
#                         trek.difficulty,
#                         trek.duration,
#                         trek.start_date,
#                         booking.status
#                     ])
            
#             print(f"CSV created: {filepath}")
            
#             # Send email to user
#             try:
#                 msg = Message(
#                     "Your trek history is ready!",
#                     recipients=[user.email],
#                     body=f"Hi {user.name}, your trek history export is ready. Filename: {filename}"
#                 )
#                 mail.send(msg)
#                 print(f"Email sent to {user.email}")
#             except Exception as e:
#                 print(f"Error sending email: {e}")
            
#             return f"Export created: {filename}"
    
#     except Exception as e:
#         print(f"Error in export: {e}")
#         return f"Error: {e}"

# #     print(f"CSV export complete: {filename}")
# #     return filename
