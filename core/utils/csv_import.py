# core/utils/csv_import.py
import csv
from datetime import datetime
from django.utils import timezone
from core.models import Assembly, Unit, Cell, Family, Member

def parse_date(date_str):
    """Parse various date formats in the CSV"""
    if not date_str or date_str.lower() in ['', 'nil', 'null']:
        return None
    
    # Common date formats in your CSV
    date_formats = [
        '%d/%m/%y', '%d/%m/%Y', '%d-%b', '%d/%m', '%d-%b-%y',
        '%d/%m', '%m/%d/%y', '%m/%d/%Y', '%d-%b-%Y'
    ]
    
    for fmt in date_formats:
        try:
            # For dates without year, add current year
            if fmt in ['%d-%b', '%d/%m']:
                date_str_with_year = f"{date_str}-{datetime.now().year}"
                return datetime.strptime(date_str_with_year, f"{fmt}-%Y").date()
            return datetime.strptime(date_str, fmt).date()
        except ValueError:
            continue
    
    # Try parsing as just day-month (like "26/12")
    if '/' in date_str and len(date_str.split('/')) == 2:
        try:
            day, month = map(int, date_str.split('/'))
            return datetime(datetime.now().year, month, day).date()
        except:
            pass
    
    return None

def create_assembly():
    """Create the main assembly"""
    assembly, created = Assembly.objects.get_or_create(
        name="Ifelodun Assembly",
        defaults={
            'description': "Main church assembly from CSV data",
            'street_address': "FUTA Northgate Area",
            'city': "Akure",
            'state': "Ondo",
            'country': "Nigeria",
            'is_active': True
        }
    )
    return assembly

def create_units():
    """Create units based on CSV data"""
    units_data = [
        "Praise Team", "Media", "Ushering", "Children", "Decoration", 
        "Sanctuary Keeper", "Evangelism", "Drama", "Security", "Welfare",
        "Organizing", "Technical", "Prayer", "Interpreting"
    ]
    
    units = {}
    for unit_name in units_data:
        unit, created = Unit.objects.get_or_create(name=unit_name)
        units[unit_name] = unit
    
    return units

def create_cells():
    """Create cells based on CSV data"""
    cells_data = [
        "Ifelodun A", "Ifelodun B", "Ipinsa", "Oke Odu", "Orita-Obele",
        "Akad/Unity", "FUTA South Gate", "Oba-Ile"
    ]
    
    cells = {}
    for cell_name in cells_data:
        cell, created = Cell.objects.get_or_create(
            name=cell_name,
            defaults={'created_at': timezone.now().date()}
        )
        cells[cell_name] = cell
    
    return cells

def get_or_create_family(assembly, surname, row):
    """Get or create family based on surname and address"""
    if not surname:
        return None
    
    # Try to find family by surname and similar address
    address = row.get('Address', '') or ''
    families = Family.objects.filter(
        assembly=assembly,
        family_name__icontains=surname
    )
    
    if families.exists():
        return families.first()
    
    # Create new family
    family = Family.objects.create(
        assembly=assembly,
        family_name=surname,
        address=address,
        phone=row.get('Phone', ''),
        email=row.get('Email', '')
    )
    return family

def import_members_from_csv(csv_file_path):
    """Main function to import members from CSV"""
    
    # Create base data
    assembly = create_assembly()
    units = create_units()
    cells = create_cells()
    
    members_created = 0
    members_updated = 0
    
    with open(csv_file_path, 'r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        
        for row in reader:
            # Skip empty rows
            if not row.get('Surname') and not row.get('Other Names 1'):
                continue
            
            # Prepare member data
            title = row.get('Title', '').strip()
            surname = row.get('Surname', '').strip()
            other_names_1 = row.get('Other Names 1', '').strip()
            other_names_2 = row.get('Other Names 2', '').strip()
            
            # Create full name components
            first_name = other_names_1 if other_names_1 else surname
            last_name = surname
            middle_name = other_names_2
            
            # Handle gender
            gender_map = {'M': 'M', 'F': 'F'}
            gender = gender_map.get(row.get('Gender', '').strip(), 'O')
            
            # Handle marital status
            marital_status_map = {
                'Single': 'SINGLE',
                'Married': 'MARRIED', 
                'Widow': 'WIDOWED',
                'Widowed': 'WIDOWED',
                'Seprated': 'SEPARATED',
                'Separated': 'SEPARATED'
            }
            marital_status = marital_status_map.get(
                row.get('Status', '').strip(), 
                'SINGLE'
            )
            
            # Parse date of birth
            dob = parse_date(row.get('DOB', '').strip())
            
            # Handle unit assignment
            unit_name = row.get('Main Unit', '').strip() or row.get('Sub-Unit 1', '').strip()
            unit = units.get(unit_name) if unit_name in units else None
            
            # Handle cell assignment
            cell_name = row.get('Cell', '').strip() or row.get('Assembly', '').strip()
            cell = cells.get(cell_name) if cell_name in cells else None
            
            # Handle baptism
            baptism_date = None
            if row.get('Baptism', '').strip().lower() == 'yes':
                baptism_year = row.get('Baptism Year', '').strip()
                if baptism_year and baptism_year.isdigit():
                    baptism_date = datetime(int(baptism_year), 1, 1).date()
            
            # Handle born again year
            membership_date = None
            born_again_year = row.get('born again year', '').strip()
            if born_again_year and born_again_year.isdigit():
                membership_date = datetime(int(born_again_year), 1, 1).date()
            
            # Create or update member
            member_data = {
                'assembly': assembly,
                'first_name': first_name,
                'last_name': last_name,
                'middle_name': middle_name,
                'date_of_birth': dob,
                'gender': gender,
                'marital_status': marital_status,
                'email': row.get('Email', '').strip(),
                'phone': row.get('Phone', '').strip(),
                'address': row.get('Address', '') or row.get('Place of Work', '') or '',
                'unit': unit,
                'cell': cell,
                'baptism_date': baptism_date,
                'membership_date': membership_date,
                'membership_status': 'ACTIVE'
            }
            
            # Try to find existing member by name and phone/email
            existing_member = None
            if row.get('Phone'):
                existing_member = Member.objects.filter(
                    phone=row.get('Phone').strip(),
                    first_name__icontains=first_name,
                    last_name__icontains=last_name
                ).first()
            
            if not existing_member and row.get('Email'):
                existing_member = Member.objects.filter(
                    email=row.get('Email').strip(),
                    first_name__icontains=first_name,
                    last_name__icontains=last_name
                ).first()
            
            if existing_member:
                # Update existing member
                for key, value in member_data.items():
                    setattr(existing_member, key, value)
                existing_member.save()
                members_updated += 1
                print(f"Updated: {first_name} {last_name}")
            else:
                # Create new member
                Member.objects.create(**member_data)
                members_created += 1
                print(f"Created: {first_name} {last_name}")
    
    print(f"\nImport completed!")
    print(f"Members created: {members_created}")
    print(f"Members updated: {members_updated}")
    return members_created, members_updated