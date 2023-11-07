from datetime import datetime
from prettytable import PrettyTable
from dateutil.relativedelta import relativedelta
import re

def parse_date(detail):
    date_str = detail.replace('2 DATE ', '').strip()
    return datetime.strptime(date_str, "%d %b %Y").strftime("%Y-%m-%d")

def calculate_age(birth_date_str, end_date_str=None):
    birth_date = datetime.strptime(birth_date_str, "%Y-%m-%d")
    end_date = datetime.strptime(end_date_str, "%Y-%m-%d") if end_date_str else datetime.now()
    age = end_date.year - birth_date.year - ((end_date.month, end_date.day) < (birth_date.month, birth_date.day))
    return age

def process_individuals(individuals):
    indidict = {}
    for person in individuals:
        id = None
        birth = None
        for detail in person:
            if 'INDI' in detail:
                id = detail.split('@')[1]
                indidict[id] = {
                    'id': id,
                    'Name': 'Unknown',
                    'Lastname': 'NA',
                    'Gender': 'NA',
                    'Birthday': 'NA',
                    'Death': 'NA',
                    'Alive': 'False',
                    'Child': 'NA',
                    'Spouse': 'NA'
                }
            elif 'GIVN' in detail:
                indidict[id]['Name'] = detail.replace('2 GIVN ', '').strip()
            elif 'SURN' in detail:
                indidict[id]['Lastname'] = detail.replace('2 SURN ', '').strip()
            elif 'SEX' in detail:
                indidict[id]['Gender'] = detail.split(' ')[2]
            elif 'BIRT' in detail:
                indidict[id]['Alive'] = 'True'
                if 'DATE' in person[person.index(detail) + 1]:
                    birth = parse_date(person[person.index(detail) + 1])
                    indidict[id]['Birthday'] = birth
                    indidict[id]['Age'] = calculate_age(birth)
            elif 'DEAT' in detail:
                indidict[id]['Alive'] = 'False'
                if 'DATE' in person[person.index(detail) + 1]:
                    death = parse_date(person[person.index(detail) + 1])
                    indidict[id]['Death'] = death
                    indidict[id]['Age'] = calculate_age(birth, death)
            elif 'FAMS' in detail:
                indidict[id]['Spouse'] = "{" + detail.split('@')[1] + "}"
            elif 'FAMC' in detail:
                indidict[id]['Child'] = "{" + detail.split('@')[1] + "}"
    return indidict

def process_families(families, indidict):
    famdict = {}
    for fam in families:
        id = None
        for detail in fam:
            if 'FAM' in detail:
                id = detail.split('@')[1]
                famdict[id] = {
                    'id': id,
                    'Husband ID': 'NA',
                    'Husband Name': 'NA',
                    'Husband Lastname': 'NA',
                    'Wife ID': 'NA',
                    'Wife Name': 'NA',
                    'Wife Lastname': 'NA',
                    'Married': 'NA',
                    'Divorced': 'NA',
                    'Children': [] 
                }
            elif 'HUSB' in detail:
                husbid = detail.split('@')[1]
                famdict[id]['Husband ID'] = husbid
                famdict[id]['Husband Name'] = indidict.get(husbid, {}).get('Name', 'Unknown')
                famdict[id]['Husband Lastname'] = indidict.get(husbid, {}).get('Lastname', 'Unknown')
            elif 'WIFE' in detail:
                wifeid = detail.split('@')[1]
                famdict[id]['Wife ID'] = wifeid
                famdict[id]['Wife Name'] = indidict.get(wifeid, {}).get('Name', 'Unknown')
                famdict[id]['Wife Lastname'] = indidict.get(wifeid, {}).get('Lastname', 'Unknown')
            elif 'CHIL' in detail:
                famdict[id]['Children'].append(detail.split('@')[1])
            elif 'MARR' in detail:
                if 'DATE' in fam[fam.index(detail) + 1]:
                    famdict[id]['Married'] = parse_date(fam[fam.index(detail) + 1])
            elif 'DIV' in detail:
                if 'DATE' in fam[fam.index(detail) + 1]:
                    famdict[id]['Divorced'] = parse_date(fam[fam.index(detail) + 1])
    return famdict

def get_ind_fam_details(gedcomfile):
    individuals = []
    individual = []
    families = []
    family = []

    for line in gedcomfile:
        line = line.strip()
        if line.endswith("INDI"):
            if individual:
                individuals.append(individual)
            individual = [line]
        elif line.startswith("0 @"):
            if individual:
                individuals.append(individual)
                individual = []
            if family:
                families.append(family)
                family = []
        elif line.endswith("FAM"):
            if family:
                families.append(family)
            family = [line]
        else:
            if individual:
                individual.append(line)
            elif family:
                family.append(line)

    indidict = process_individuals(individuals)
    famdict = process_families(families, indidict)
    return indidict, famdict


def display_gedcom_table(individuals, family):
    
    with open('Output.txt', 'w') as output:
        
        inditable = PrettyTable()
        inditable.field_names = ['ID', 'Name', 'Lastname', 'Gender', 'Birthday', 'Death', 'Alive', 'Child', 'Spouse', 'Age']
        inditable.add_rows([individual.values() for individual in individuals.values()])
        output.write('Individuals:\n')
        output.write(str(inditable))
        output.write('\n')

        # Print Families table
        famtable = PrettyTable()
        famtable.field_names = ['ID', 'Husband ID', 'Husband Name', 'Husband Lastname', 'Wife ID', 'Wife Name', 'Wife Lastname', 'Married', 'Divorced', 'Children']
        famtable.add_rows([fam.values() for fam in family.values()])
        output.write('Families:\n')
        output.write(str(famtable))
        output.write('\n')


def US1_dates_before_current_date(individuals, family):
    current_date = datetime.now()
    
    Error01_individuals = [
        ind for ind in individuals.values()
        if ('Death' in ind and ind['Death'] != 'NA' and datetime.strptime(ind["Death"], "%Y-%m-%d") > current_date)
        or ('Birthday' in ind and ind['Birthday'] != 'NA' and datetime.strptime(ind["Birthday"], "%Y-%m-%d") > current_date)
    ]
    
    Error01_family = [
        fam for fam in family.values()
        if ('Divorced' in fam and fam["Divorced"] != 'NA' and datetime.strptime(fam["Divorced"], "%Y-%m-%d") > current_date)
        or ('Married' in fam and fam["Married"] != 'NA' and datetime.strptime(fam["Married"], "%Y-%m-%d") > current_date)
    ]

    return Error01_individuals, Error01_family


def US6_divorce_before_death(individuals, family):
    
    errors = [
        individuals[spouse_id]
        for fam in family.values() if fam['Divorced'] != 'NA'
        for spouse_id in [fam['Husband ID'], fam['Wife ID']]
        if individuals[spouse_id]['Death'] != 'NA' and datetime.strptime(individuals[spouse_id]['Death'], "%Y-%m-%d") < datetime.strptime(fam['Divorced'], "%Y-%m-%d")
    ]
    
    return errors

def US7_Death_less_150_after_birth(individuals):
    current_date = datetime.now()
    
    Error07 = [
        f"ERROR US07: {ind['id']} {ind['Death']} {ind['Name']} Age: {age}"
        for ind in individuals.values()
        for age in [
            (datetime.strptime(ind['Death'], "%Y-%m-%d") if ind['Alive'] == 'False' and ind['Death'] != 'NA' else current_date).year - datetime.strptime(ind['Birthday'], "%Y-%m-%d").year
        ]
        if age > 150
    ]

    return Error07



def age_at_event(birthday, event_date):
    """Helper function to compute age at a given event."""
    birth_date = datetime.strptime(birthday, "%Y-%m-%d")
    event_dt = datetime.strptime(event_date, "%Y-%m-%d")
    return relativedelta(event_dt, birth_date).years

def US10_marriage_after_14(family, individuals):
    Error10 = []

    for fam in family.values():
        if fam['Married'] != 'NA':
            for spouse_role, spouse_id in [('Wife ID', fam['Wife ID']), ('Husband ID', fam['Husband ID'])]:
                age_at_marriage = age_at_event(individuals[spouse_id]['Birthday'], fam['Married'])
                if age_at_marriage < 14:
                    Error10.append(spouse_id)

    return Error10

def US13_sibling_spacing(family, individuals):
    errors = []
    for fam in family.values():
        children_ids = fam.get('Children', [])
        birth_dates = [
            datetime.strptime(individuals[child_id]['Birthday'], "%Y-%m-%d")
            for child_id in children_ids if 'Birthday' in individuals[child_id]
        ]
        sorted_dates = sorted(birth_dates)
        for i in range(len(sorted_dates) - 1):
            delta = sorted_dates[i + 1] - sorted_dates[i]
            if not (0 <= delta.days <= 1 or delta.days >= 243):  # 243 days is roughly 8 months
                errors.append((children_ids[i], children_ids[i + 1]))
    return errors

def US16_find_males_with_different_lastnames(individuals, families):
    males_with_different_lastnames = []  # Initialize a list to store names

    for fam_id, fam in families.items():
        # If there is a husband in the family, get his last name
        husband_id = fam.get('Husband ID')
        if husband_id and husband_id in individuals:
            husband_lastname = individuals[husband_id]['Lastname']

            # Iterate over the children IDs
            for child_id in fam.get('Children', []):
                child = individuals.get(child_id)
                # If the child is male and last name is different, add to the list
                if child and child['Gender'] == 'M' and child['Lastname'] != husband_lastname:
                    males_with_different_lastnames.append(f"{child['Name']} (Family: {fam_id})")

    return males_with_different_lastnames



if __name__ == "__main__":
    with open("Test_File.ged", "r") as gedcomf:
        gedcomfile = [line.rstrip('\n') for line in gedcomf]

    # Retrieve the Individuals and Family from the input file
    individuals, family = get_ind_fam_details(gedcomfile)

    # Print The details using Pretty Table Library
    display_gedcom_table(individuals, family)

    user_stories = [
        {
            'title': "User Story: 01 - Dates before current date",
            'function': US1_dates_before_current_date,
            'args': (individuals, family),
            'description': "These are the details for either of the birthdates, deathdates, marriagedates, and divorcedates that have occurred after the current date."
        },
        {
            'title': "User Story 06: Divorce before death",
            'function': US6_divorce_before_death,
            'args': (individuals, family),
            'description': "These are the details for divorce dates that have occurred after the death date of an individual."
        },
        {
            'title': "User Story: 07 - Death should be less than 150 years after birth for dead people, and current date should be less than 150 years after birth for all living people",
            'function': US7_Death_less_150_after_birth,
            'args': (individuals,),
            'description': "These are the details for dead people who had age more than 150 years or alive people with current age more than 150 years."
        },
        {
            'title': "User Story: 10 - Marriage should be at least 14 years after birth of both spouses (parents must be at least 14 years old)",
            'function': US10_marriage_after_14,
            'args': (family, individuals),
            'description': "These are the details for who were married below 14 years."
        },
        {
            'title': "User Story: 13 - Birth dates of siblings should be more than 8 months apart or less than 2 days apart (twins may be born one day apart, e.g. 11:59 PM and 12:02 AM the following calendar day)",
            'function': US13_sibling_spacing,
            'args': (family, individuals),
            'description': "These are the details of siblings who have less difference span greater that 2 days and less than 8 months"
        },
        {
            'title' : "User Story: 16 - All male members of a family should have the same last name",
            'function' : US16_find_males_with_different_lastnames,
            'args' : (individuals, family),
            'description' : "Errors of All male members of a family who don't have the same last name"
        }
    ]

    output_lines = []
    for story in user_stories:
        errors = story['function'](*story['args'])
        output_lines.append(story['title'])
        output_lines.append("\nErrors related to " + story['title'])
        output_lines.append(": " + str(errors))
        output_lines.append("\n" + story['description'])
        output_lines.append("------------------------------------------------------------------------------\n\n")

    output = "\n".join(output_lines)
    with open("Output.txt", "a") as out:
            out.write(output)






