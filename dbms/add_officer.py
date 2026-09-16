from app import app, db
from models import PoliceOfficer, CrimeRecord

# Run this script in Flask app context
with app.app_context():
    # Input officer details
    name = input("Enter officer name: ")
    phone = input("Enter officer phone: ")
    email = input("Enter officer email: ")
    designation = input("Enter officer designation: ")
    photo_filename = input("Enter photo filename (or leave blank): ")

    # Create officer object
    officer = PoliceOfficer(
        name=name,
        phone=phone,
        email=email,
        designation=designation,
        photo_filename=photo_filename if photo_filename else None
    )

    db.session.add(officer)
    db.session.commit()

    print(f"\n✅ Officer '{name}' added successfully with ID {officer.id}.\n")

    # Add crimes for this officer
    while True:
        crime_type = input("Enter crime type (or type 'done' to finish): ")
        if crime_type.lower() == 'done':
            break

        description = input("Enter crime description: ")
        status = input("Enter crime status (e.g., 'Open', 'Closed'): ")

        crime = CrimeRecord(
            crime_type=crime_type,
            description=description,
            status=status,
            officer_id=officer.id
        )

        db.session.add(crime)
        db.session.commit()
        print(f"✔️ Crime '{crime_type}' added for officer {name}.\n")
