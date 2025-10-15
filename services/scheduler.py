from datetime import datetime, timedelta
from sqlalchemy import and_

class SchedulerService:
    def __init__(self, db_session):
        self.db = db_session

    def check_conflict(self, datetime_slot, duration_minutes=30, exclude_appointment_id=None):
        """Check if time slot has conflict"""
        from models.appointment import Appointment

        end_time = datetime_slot + timedelta(minutes=duration_minutes)

        query = self.db.query(Appointment).filter(
            and_(
                Appointment.datetime < end_time,
                Appointment.datetime >= datetime_slot - timedelta(minutes=60),
                Appointment.status != 'cancelled'
            )
        )

        if exclude_appointment_id:
            query = query.filter(Appointment.id != exclude_appointment_id)

        conflict = query.first()
        return conflict is not None

    def find_next_available(self, start_datetime, duration_minutes=30, max_attempts=20):
        """Find next available slot after given time"""
        current = start_datetime

        for _ in range(max_attempts):
            current += timedelta(minutes=30)
            if not self.check_conflict(current, duration_minutes):
                return current

        return None

    def get_availability(self, start_date, end_date):
        """Get availability for date range"""
        from models.appointment import Appointment

        # Generate all possible slots
        slots = []
        current = start_date.replace(hour=8, minute=0, second=0, microsecond=0)

        while current <= end_date:
            # Skip weekends
            if current.weekday() < 5:  # Monday=0, Sunday=6
                # Generate slots from 8am to 6pm
                for hour in range(8, 18):
                    for minute in [0, 30]:
                        slot_time = current.replace(hour=hour, minute=minute)

                        # Check if occupied
                        appointment = self.db.query(Appointment).filter_by(
                            datetime=slot_time
                        ).filter(
                            Appointment.status != 'cancelled'
                        ).first()

                        slot_info = {
                            'datetime': slot_time.isoformat(),
                            'available': appointment is None
                        }

                        if appointment:
                            slot_info['appointment_id'] = str(appointment.id)
                            slot_info['clinic_id'] = str(appointment.clinic_id)

                        slots.append(slot_info)

            current += timedelta(days=1)

        return slots
