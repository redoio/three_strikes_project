# -*- coding: utf-8 -*-

from functions import *
from config import *
import pandas as pd
import numpy as np
import datetime
from tqdm import tqdm

def main():
    # Criteria for selection
    sorting_criteria = extract_data(main_path = data_path, 
                                    county_name = county_name, 
                                    file_name = 'Criteria/sorting_criteria.xlsx', 
                                    pickle = True) 
    
    # Demographics of individuals incarcerated
    demographics = extract_data(main_path = data_path, 
                                county_name = county_name, 
                                file_name = 'demographics.xlsx', 
                                month = month,
                                pickle = True)
    
    # Education merit
    merit_credit = extract_data(main_path = data_path, 
                                county_name = county_name, 
                                file_name = 'EducationMeritCredits.xlsx', 
                                month = month,
                                pickle = True)
    
    # Milestone credit
    milestone_credit = extract_data(main_path = data_path, 
                                    county_name = county_name, 
                                    file_name = 'MilestoneCompletionCredits.xlsx', 
                                    month = month,
                                    pickle = True)
    
    # Rehab credit
    rehab_credit = extract_data(main_path = data_path, 
                                county_name = county_name, 
                                file_name = 'RehabilitiveAchievementCredits.xlsx', 
                                month = month,
                                pickle = True)
    
    # Vocational education credit
    voced_credit = extract_data(main_path = data_path, 
                                county_name = county_name, 
                                file_name = 'VocEd_TrainingCerts.xlsx', 
                                month = month,
                                pickle = True)
    
    # Rule violations
    rv_report = extract_data(main_path = data_path, 
                            county_name = county_name, 
                            file_name = 'RVRs.xlsx', 
                            month = month,
                            pickle = True)
    
    # Current commitments
    current_commits = extract_data(main_path = data_path, 
                            county_name = county_name, 
                            file_name = 'currentcommitments.xlsx', 
                            month = month,
                            pickle = True)
    
    # Previous commitments
    prior_commits = extract_data(main_path = data_path, 
                            county_name = county_name, 
                            file_name = 'priorcommitments.xlsx', 
                            month = month,
                            pickle = True)
    
if __name__ == "__main__":
    main()
    
else:
    main()
