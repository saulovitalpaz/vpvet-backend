from app import create_app
from extensions import db
from models.user import Clinic, User
from models.patient import Tutor, Animal
from models.appointment import Appointment
from models.exam import Consultation, ExamResult
from datetime import datetime, timedelta

app = create_app()

with app.app_context():
    # Check if data already exists
    if User.query.first():
        print("Database already has users. Skipping seed.")
        exit(0)

    # Create clinics
    print("Creating clinics...")
    petcare = Clinic(
        name='PetCare',
        phone='(33) 3271-1234',
        email='contato@petcare.com'
    )
    central = Clinic(
        name='Clinica Central',
        phone='(33) 3271-5678',
        email='contato@clinicacentral.com'
    )
    animais = Clinic(
        name='Animais & Cia',
        phone='(33) 3271-9012',
        email='contato@animaisecia.com'
    )

    db.session.add_all([petcare, central, animais])
    db.session.commit()

    # Create Dr. Saulo
    print("Creating Dr. Saulo...")
    dr_saulo = User(
        name='Dr. Saulo Vital',
        email='saulo@vpvet.com',
        role='dr_saulo'
    )
    dr_saulo.set_password('senha123')
    db.session.add(dr_saulo)

    # Create secretaries
    print("Creating secretaries...")
    maria = User(
        name='Maria Silva',
        email='maria@petcare.com',
        role='secretary',
        clinic_id=petcare.id
    )
    maria.set_password('senha123')

    joana = User(
        name='Joana Santos',
        email='joana@clinicacentral.com',
        role='secretary',
        clinic_id=central.id
    )
    joana.set_password('senha123')

    carla = User(
        name='Carla Oliveira',
        email='carla@animaisecia.com',
        role='secretary',
        clinic_id=animais.id
    )
    carla.set_password('senha123')

    db.session.add_all([maria, joana, carla])
    db.session.commit()

    # Create tutors and animals
    print("Creating tutors and animals...")

    # Tutor 1
    joao = Tutor(
        name='Joao da Silva',
        cpf='123.456.789-00',
        phone='(33) 99999-1111',
        email='joao@email.com'
    )
    db.session.add(joao)
    db.session.commit()

    rex = Animal(
        tutor_id=joao.id,
        name='Rex',
        species='canine',
        breed='Labrador',
        birth_date=datetime(2020, 3, 15).date(),
        sex='male',
        weight=32.5,
        is_neutered=True
    )
    db.session.add(rex)

    # Tutor 2
    ana = Tutor(
        name='Ana Paula',
        cpf='987.654.321-00',
        phone='(33) 98888-2222',
        email='ana@email.com'
    )
    db.session.add(ana)
    db.session.commit()

    mimi = Animal(
        tutor_id=ana.id,
        name='Mimi',
        species='feline',
        breed='Persian',
        birth_date=datetime(2019, 7, 20).date(),
        sex='female',
        weight=4.2,
        is_neutered=False
    )
    db.session.add(mimi)

    # Tutor 3
    carlos = Tutor(
        name='Carlos Eduardo',
        cpf='456.789.123-00',
        phone='(33) 97777-3333',
        email='carlos@email.com'
    )
    db.session.add(carlos)
    db.session.commit()

    thor = Animal(
        tutor_id=carlos.id,
        name='Thor',
        species='canine',
        breed='German Shepherd',
        birth_date=datetime(2021, 1, 10).date(),
        sex='male',
        weight=38.0,
        is_neutered=True
    )
    db.session.add(thor)

    db.session.commit()

    # Create sample appointments
    print("Creating sample appointments...")

    # Tomorrow at 10am
    tomorrow_10am = datetime.now().replace(hour=10, minute=0, second=0, microsecond=0) + timedelta(days=1)

    # Tomorrow at 2pm
    tomorrow_2pm = datetime.now().replace(hour=14, minute=0, second=0, microsecond=0) + timedelta(days=1)

    # Day after tomorrow at 11am
    day_after_11am = datetime.now().replace(hour=11, minute=0, second=0, microsecond=0) + timedelta(days=2)

    appt1 = Appointment(
        clinic_id=petcare.id,
        animal_id=rex.id,
        datetime=tomorrow_10am,
        duration_minutes=30,
        service_type='ultrasound_abdominal',
        status='scheduled',
        notes='First ultrasound exam',
        created_by=maria.id
    )

    appt2 = Appointment(
        clinic_id=central.id,
        animal_id=mimi.id,
        datetime=tomorrow_2pm,
        duration_minutes=30,
        service_type='xray_thoracic',
        status='scheduled',
        notes='Respiratory evaluation',
        created_by=joana.id
    )

    appt3 = Appointment(
        clinic_id=petcare.id,
        animal_id=thor.id,
        datetime=day_after_11am,
        duration_minutes=30,
        service_type='ultrasound_cardiac',
        status='scheduled',
        created_by=maria.id
    )

    db.session.add_all([appt1, appt2, appt3])
    db.session.commit()

    # Create consultations and exam results
    print("Creating consultations and exam results...")

    # Consultation for Rex (ultrasound)
    consultation1 = Consultation(
        appointment_id=appt1.id,
        chief_complaint='Abdominal discomfort',
        physical_exam='Alert, responsive. Abdominal palpation reveals mild discomfort.',
        diagnosis='Mild gastritis',
        prognosis='good',
        treatment_plan='Dietary management and medication',
        notes='Follow-up in 2 weeks'
    )
    db.session.add(consultation1)
    db.session.commit()

    result1 = ExamResult(
        consultation_id=consultation1.id,
        animal_id=rex.id,
        exam_type='Ultrasound Abdominal',
        access_code=ExamResult.generate_access_code(),
        findings='Liver and kidneys appear normal. Mild thickening of stomach wall noted.',
        impression='Mild gastric wall thickening consistent with gastritis. No masses detected.',
        exam_date=datetime.now().date(),
        pdf_url='/results/rex_ultrasound_2024.pdf'
    )
    db.session.add(result1)

    # Consultation for Mimi (x-ray)
    consultation2 = Consultation(
        appointment_id=appt2.id,
        chief_complaint='Respiratory difficulty',
        physical_exam='Increased respiratory effort, bilateral lung sounds',
        diagnosis='Mild bronchitis',
        prognosis='excellent',
        treatment_plan='Antibiotics and bronchodilators',
        notes='Monitor breathing'
    )
    db.session.add(consultation2)
    db.session.commit()

    result2 = ExamResult(
        consultation_id=consultation2.id,
        animal_id=mimi.id,
        exam_type='X-Ray Thoracic',
        access_code=ExamResult.generate_access_code(),
        findings='Mild bronchial pattern. Heart silhouette within normal limits.',
        impression='Mild bronchitis. No evidence of pneumonia or cardiac disease.',
        exam_date=datetime.now().date(),
        pdf_url='/results/mimi_xray_2024.pdf'
    )
    db.session.add(result2)

    # Consultation for Thor (cardiac ultrasound)
    consultation3 = Consultation(
        appointment_id=appt3.id,
        chief_complaint='Exercise intolerance',
        physical_exam='Grade 2/6 systolic murmur, strong pulses',
        diagnosis='Mild mitral valve insufficiency',
        prognosis='good',
        treatment_plan='Monitor, possible medication in future',
        notes='Recheck in 6 months'
    )
    db.session.add(consultation3)
    db.session.commit()

    result3 = ExamResult(
        consultation_id=consultation3.id,
        animal_id=thor.id,
        exam_type='Echocardiogram',
        access_code=ExamResult.generate_access_code(),
        findings='Mild mitral valve regurgitation. Left atrium mildly enlarged. Ejection fraction 65%.',
        impression='Stage B1 myxomatous mitral valve disease. Currently asymptomatic.',
        exam_date=datetime.now().date(),
        pdf_url='/results/thor_echo_2024.pdf',
        images_url=['/results/thor_echo_1.jpg', '/results/thor_echo_2.jpg']
    )
    db.session.add(result3)

    db.session.commit()

    print("\nDatabase seeded successfully!")
    print("\nLogin credentials:")
    print("   Dr. Saulo: saulo@vpvet.com / senha123")
    print("   Maria (PetCare): maria@petcare.com / senha123")
    print("   Joana (Clinica Central): joana@clinicacentral.com / senha123")
    print("   Carla (Animais & Cia): carla@animaisecia.com / senha123")
    print("\nSample data:")
    print(f"   3 tutors with 3 animals")
    print(f"   3 appointments with consultations")
    print(f"   3 exam results")
    print("\nPublic access codes for results:")
    print(f"   Rex (Joao - CPF: 123.456.789-00): {result1.access_code}")
    print(f"   Mimi (Ana - CPF: 987.654.321-00): {result2.access_code}")
    print(f"   Thor (Carlos - CPF: 456.789.123-00): {result3.access_code}")
