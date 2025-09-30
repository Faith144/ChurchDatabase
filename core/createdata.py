import pandas as pd
from core.models import Assembly, Cell, Member

def import_data_from_excel(file_path):
    # Read the Excel file
    df = pd.read_excel(file_path)

    for index, row in df.iterrows():
        # Create or get Assembly
        assembly, created = Assembly.objects.get_or_create(name=row['Assembly'])
        
        # Create or get Cell
        cell, created = Cell.objects.get_or_create(name=row['Cell'], assembly=assembly)
        
        # Create Member
        member = Member(
            first_name=row['First Name'],
            last_name=row['Last Name'],
            email=row['Email'],
            phone=row['Phone'],
            assembly=assembly,
            cell=cell
        )
        member.save()