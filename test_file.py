import unittest
from datetime import datetime
from vamshi import US1_dates_before_current_date, US6_divorce_before_death  # replace 'your_script_name' with the actual name of your script

class TestGedcom(unittest.TestCase):

    def setUp(self):
        # This method sets up the data for use in all test cases.
        self.individuals = {
            "I1": {
                "id": "I1",
                "Name": "Future Person",
                "Lastname": "Doe",
                "Gender": "M",
                "Birthday": "3011-07-16",  # A date that is certainly after the current date
                "Death": "1979-11-04",
                "Alive": "False",
                "Child": "{F5}",
                "Spouse": "{F2}",
                "Age": -1032,
            },
            "I2": {
                "id": "I2",
                "Name": "Past Person",
                "Lastname": "Doe",
                "Gender": "F",
                "Birthday": "1990-07-16",  # A date that is before the current date
                "Death": "2020-11-04",
                "Alive": "False",
                "Child": "{F3}",
                "Spouse": "{F1}",
                "Age": 30,
            },
            "I3": {
                "id": "I3",
                "Name": "Deceased Spouse",
                "Gender": "M",
                "Death": "2020-01-01",  # this person is dead
            },
            "I4": {
                "id": "I4",
                "Name": "Living Spouse",
                "Gender": "F",
                "Death": "NA",  # this person is alive
            }
        }

        self.families = {
            "F1": {
                "id": "F1",
                "Husband ID": "I3",
                "Wife ID": "I4",
                "Divorced": "2021-01-01",  # divorce occurred after the death
            },
            "F2": {
                "id": "F2",
                "Husband ID": "I4",
                "Wife ID": "I3",
                "Divorced": "2019-01-01",  # divorce occurred before the death
            }
        }

    def test_dates_before_current_date(self):
        result_individuals, result_families = US1_dates_before_current_date(self.individuals, {})
        expected_result_individuals = [self.individuals["I1"]]
        expected_result_families = []  # Empty list for families, as no families were provided in this case

        self.assertEqual(result_individuals, expected_result_individuals)
        self.assertEqual(result_families, expected_result_families)

    def test_divorce_before_death(self):
        errors = US6_divorce_before_death(self.individuals, self.families)
        expected_errors = [self.individuals["I3"]]  # this individual's divorce date is after their death date

        self.assertEqual(errors, expected_errors)

    def test_no_errors(self):
        # In this test, we'll manipulate the data to ensure no conditions are met for an error.
        self.families["F1"]["Divorced"] = "2019-01-01"  # change to a date before the death
        errors = US6_divorce_before_death(self.individuals, self.families)
        expected_errors = []

        self.assertEqual(errors, expected_errors)
    def test_ind_males_with_different_lastnames(self):
        # Assuming we have a method that returns males with different last names
        result = ind_males_with_different_lastnames(self.individuals, self.families)
        # You need to define the expected result based on your data setup
        expected_result = [] # Define expected results based on your test setup
        self.assertEqual(result, expected_result)

    def test_US_sibling_spacing(self):
        # Assuming we have a method that checks for the spacing between sibling births
        result = US_sibling_spacing(self.families)
        # You need to define the expected result based on your data setup
        expected_result = [] # Define expected results based on your test setup
        self.assertEqual(result, expected_result)


if __name__ == '__main__':
    unittest.main()
