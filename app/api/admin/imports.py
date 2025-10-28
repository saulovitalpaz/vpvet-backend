"""Test imports for admin module"""
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

try:
    from models.user import User
    print("✓ User model imported successfully")

    from models.user import Clinic
    print("✓ Clinic model imported successfully")

    from models.patient import Tutor, Animal
    print("✓ Patient models imported successfully")

    from models.appointment import Appointment
    print("✓ Appointment model imported successfully")

    from models.exam import Consultation, ExamResult
    print("✓ Exam models imported successfully")

    print("\n✅ All models imported successfully!")

except ImportError as e:
    print(f"\n❌ Import error: {e}")
    print("\nMake sure you're running from the vpet-backend root directory:")
    print("1. Activate virtual environment: .venv\\Scripts\\activate")
    print("2. Run as module: python -m app")