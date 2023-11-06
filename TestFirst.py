import unittest
from datetime import datetime
import dateutil.relativedelta
from m2b3_gedcom_code import process_gedcom_line, individual_ids, error_messages, individuals, name_birth_dict

#US03
def birthBeforeDeath(individual):
    if individual["Birthday"] > individual["Death Date"]:    
        return False
    else:
        return True

#US02
def birthBeforeMarriage(individual):
    if individual["Birthday"] > individual["Wedding Day"]:
        return False
    else:
        return True
    
#US08
def birthBeforeMarriageofParents(individual, parents):
    if individual["Birthday"] < parents["Marriage Day"]:
        return False
    else:
        return True


#US09
def birthAfterDeathOfMom(individual, mom):
    if individual["Birthday"] > mom["Death Day"]:
        return False
    else:
        return True

#US27
def calculate_current_age(birth_date):
    birth_date_obj = datetime.strptime(birth_date, "%d %b %Y")
    today = datetime.now()
    current_age = today.year - birth_date_obj.year - ((today.month, today.day) < (birth_date_obj.month, birth_date_obj.day))
    return current_age

#US29
def calculate_age_at_death(birth_date, death_date):
    birth_date_obj = datetime.strptime(birth_date, "%d %b %Y")
    death_date_obj = datetime.strptime(death_date, "%d %b %Y")
    age_at_death = death_date_obj.year - birth_date_obj.year - ((death_date_obj.month, death_date_obj.day) < (birth_date_obj.month, birth_date_obj.day))
    return age_at_death

#US17
def marriedToDescendants(patriarch, matriarch, individual, individuals):

    if individuals[individual]["gender"] ==  'M' and individual == patriarch:
        return False
    elif  individuals[individual]["gender"] == 'F' and individual == matriarch:
        return False
    elif individuals[individual]["Children"] is None:
        return True
    else: 
        for child in individuals[individual]["Children"]:
            if child == individual:
                continue
            else:
                return marriedToDescendants(patriarch, matriarch, child, individuals)
            
#US18
def marriedToSiblings(individual):
 if individual["spouse"] in individual["siblings"]:
    return False
 else: 
    return True
    

class TestUserStories(unittest.TestCase):

    def setUp(self):
        individual_ids.clear()
        error_messages.clear()
        individuals.clear()
        name_birth_dict.clear()
    
    
    def test_us22_uniqueID(self):
        line1 = "0 @I123 INDI"
        line2 = "0 @I123 INDI"
        process_gedcom_line(line1)
        process_gedcom_line(line2)

        self.assertIn("ERROR: INDIVIDUAL: US22: @I123: Individual ID is not unique", error_messages)

    def test_us23_same_name_and_birthdate(self):
        name_birth_dict = {('Raj /Palival/', '21 FEB 1998'): ['@I1@', '@I13@']}

        individuals['@I1@'] = {"name": "Raj /Palival/", "birth_date": "21 FEB 1998"}
        individuals['@I13@'] = {"name": "Raj /Palival/", "birth_date": "21 FEB 1998", "death_date": None}

        processed_pairs = set()

        for name_birth_key, individual_ids in name_birth_dict.items():
            name, birth_date = name_birth_key
            for i in range(len(individual_ids)):
                for j in range(i + 1, len(individual_ids)):
                    pair = (individual_ids[i], individual_ids[j])
                    if pair not in processed_pairs:
                        error_msg = f"ERROR: INDIVIDUAL: US23: {individual_ids[i]} and {individual_ids[j]}: Have the same name and birth date {name} - {birth_date}"
                        error_messages.append(error_msg)
                        processed_pairs.add(pair)

        self.assertIn("ERROR: INDIVIDUAL: US23: @I1@ and @I13@: Have the same name and birth date Raj /Palival/ - 21 FEB 1998", error_messages)
    
    def test_us02True(self):
        test1 = {"Birthday": datetime(1998, 6, 12), "Wedding Day": datetime(1999, 6, 12)}
        self.assertTrue(birthBeforeMarriage(test1))

    def test_us03True(self):
        test2 = {"Birthday": datetime(1998, 6, 12), "Death Date": datetime(1998, 6, 13)}
        self.assertTrue(birthBeforeDeath(test2))

    def test_us08True(self):
        test3Individual = {"Birthday": datetime(1998, 6, 12)}
        test3Parents = {"Marriage Day": datetime(1997, 6, 13)}
        self.assertTrue(birthBeforeMarriageofParents(test3Individual, test3Parents))

    def test_us09True(self):
        test4Individual = {"Birthday": datetime(1998, 6, 12)}
        test4Mom = {"Death Day": datetime(1999, 6, 13)}
        self.assertTrue(birthAfterDeathOfMom(test4Individual, test4Mom))

    def test_US27_current_age_calculation(self):
        
        # Birth date format is "%d %b %Y", e.g., "25 Dec 1990"
        test_birth_date_1 = "25 Dec 1990"
        test_birth_date_2 = "12 Jan 2000"
        test_birth_date_3 = "01 Mar 1985"

        # Calculating current age based on today's date
        current_age_1 = calculate_current_age(test_birth_date_1)
        current_age_2 = calculate_current_age(test_birth_date_2)
        current_age_3 = calculate_current_age(test_birth_date_3)

        # Assert statements to check if the calculated ages are as expected
        self.assertEqual(current_age_1, 32)  # Adjust the expected age according to current date
        self.assertEqual(current_age_2, 23)
        self.assertEqual(current_age_3, 38)

    def test_US29_age_at_death_calculation(self):
        test_cases = [
            {
                "birth_date": "15 Mar 1980",
                "death_date": "20 Jan 2020",
                "expected_age": 39
            },
        ]
        for case in test_cases:
            calculated_age = calculate_age_at_death(case["birth_date"], case["death_date"])
            self.assertEqual(calculated_age, case["expected_age"], f"Failed for {case['birth_date']} - {case['death_date']}. Expected: {case['expected_age']}, Got: {calculated_age}")

    def test_us17True(self):
        test5Individual = {"spouse": "I11", "siblings": ["I01"]}
        self.assertTrue(marriedToSiblings(test5Individual))
    
    def test_us018True(self):
        test6Individuals = {"I1": {"gender": "M", "Children": None}}
        test6patriarch = "I4"
        test6matriarch = "I6"
        self.assertTrue(marriedToDescendants(test6patriarch, test6matriarch, "I1", test6Individuals))


if __name__ == '__main__':
    unittest.main()


    
