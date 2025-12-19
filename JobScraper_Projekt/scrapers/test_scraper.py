import unittest
import pandas as pd
from job_scraper import clean_data, categorize_role

class TestJobsFunctions(unittest.TestCase):

    def setUp(self):
        # Sample dataframe for testing
        self.df = pd.DataFrame({
            'title': ['Data Scientist', 'Backend Engineer', 'Projekt Manager', 'Random Job'],
            'salary': ['50 k €', '60 k €', '', '40 k €'],
            'company': ['A', 'B', 'C', 'D'],
            'summary': ['desc1', 'desc2', 'desc3', 'desc4']
        })

    def test_clean_data_salary_extraction(self):
        df_clean = clean_data(self.df)
        # Check salary_k column exists
        self.assertIn('salary_k', df_clean.columns)
        # Check salary is integer
        self.assertTrue(df_clean['salary_k'].dtype.kind in 'iu')

    def test_clean_data_role_categorization(self):
        df_clean = clean_data(self.df)
        roles = df_clean['role'].tolist()
        self.assertIn('Data Scientist', roles)
        self.assertIn('Backend', roles)
        self.assertIn('Project Manager', roles)
        # 'Random Job' should be removed
        self.assertNotIn('Other', roles)

    def test_categorize_role_function(self):
        self.assertEqual(categorize_role('Machine Learning Engineer'), 'Machine Learning')
        self.assertEqual(categorize_role('QA Tester'), 'QA')
        self.assertEqual(categorize_role('Head of Data'), 'Higher level management')

if __name__ == '__main__':
    unittest.main()
