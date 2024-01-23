# -*- coding: utf-8 -*-

from helpers import *
import rules
import pandas as pd
import numpy as np
import datetime
from tqdm import tqdm
import copy

def gen_adult_eligibility(demographics, 
                          sorting_criteria,
                          current_commits, 
                          prior_commits, 
                          read_path = None, 
                          county_name = None, 
                          month = None,
                          to_excel = False, 
                          write_path = None):
    """

    Parameters
    ----------
    sorting_criteria : pandas dataframe
        Data on offenses and their categories
    demographics : pandas dataframe
        Data on individuals currently incarcerated
    current_commits : pandas dataframe
        Data on current offenses of incarcerated individuals wherein each row pertains to a single offense
    prior_commits : pandas dataframe
        Data on prior offenses of incarcerated individuals wherein each row pertains to a single offense
    data_path : str, optional
        Full path where output data should be written (all parent folders)
        Default is None.
    county_name : str, optional
        Name of the county for which eligibility was evaluated, ex: 'Los Angeles County'
        Default is None.
    month : str, optional
        Year and month for which eligibility was evaluated, ex: '2023_06'
        Default is None.
    to_excel : boolean, optional
        Specify whether to write current commitments and demographics of eligible individuals to Excel files.
        If True, specify the path information to write the output
        Default is False.
    write_path : str, optional 
        Specify the full path where the Excel outputs should be written. 
        If to_excel = True but write_path = None, data outputs are written to the county_name + month folder by default. To avoid this behavior, pass a value to write_path.
 

    Returns
    -------
    errors : pandas dataframe
        Data in the demographics dataframe for which time variables could not be computed
    adult_el_cdcr_nums : list of strs
        List of CDCR numbers that are eligible for resentencing 

    """
    # Add all of the time variables to the demographic data necessary for classification - years served, sentence length, age, etc.
    demographics, errors = gen_time_vars(df = demographics, merge = True)
    
    ####
    
    # Conditions to search: 1., 2. and 3. for Cohort 1
    print('Checking eligibility for cohort 1: adult population')
    print('Checking eligibility for conditions 1, 2 and 3')
    # Extracting CDCR numbers with eligible ages
    el_cdcr_nums_1 = demographics[demographics['Age in years'] >= 50]['CDCR #']
    # Extracting CDCR numbers that met the age criteria that also meet the time sentenced criteria
    el_cdcr_nums_2 = demographics[(demographics['Aggregate sentence in years'] >= 20) & demographics['CDCR #'].isin(el_cdcr_nums_1)]['CDCR #']
    # Extracting CDCR numbers that met the age criteria that also meet the time served criteria
    el_cdcr_nums_3 = demographics[(demographics['Time served in years'] >= 10) & demographics['CDCR #'].isin(el_cdcr_nums_2)]['CDCR #']
    
    ####
    
    # Conditions to search: 4. for Cohort 1
    
    print('Checking eligibility for condition 4')
    # Extracting ineligible offenses from sorting criteria
    inel_offenses = sorting_criteria[sorting_criteria['Table'].isin(['Table A', 'Table B', 'Table C', 'Table D'])]['Offenses'].tolist()
    # Appending new offenses based on implied ineligibility for adult populations
    inel_offenses = gen_inel_off(inel_offenses, clean = True, 
                                 impl = {'all': ["/att", "(664)", "2nd"], '459': ["/att", "(664)"]})
    # Clean offense data in current commits file
    current_commits['Offense cleaned'] = clean_offense_blk(data = current_commits['Offense'])
    # Extracting current commits data with eligible offenses
    el_cdcr_nums_4 = []
    for cdcr_num in tqdm(el_cdcr_nums_3):
      # Extract offenses of the CDCR number
      offenses = current_commits[current_commits['CDCR #'] == cdcr_num]['Offense cleaned'].unique()
      if len(det_inel_off(offenses = offenses, inel_offenses = inel_offenses, pop = 'adult')) == 0:
        el_cdcr_nums_4.append(cdcr_num)
        
    ####
        
    # Conditions to search: 5. for Cohort 1
    
    print('Checking eligibility for condition 5')
    # Extracting ineligible offenses from sorting criteria
    inel_offenses = sorting_criteria[sorting_criteria['Table'].isin(['Table C', 'Table D'])]['Offenses'].tolist()
    # Appending new offenses based on implied ineligibility for adult populations
    inel_offenses = gen_inel_off(inel_offenses, clean = True, 
                                 impl = {'all': ["/att", "(664)", "2nd"], '459': ["/att", "(664)"]})
    # Clean offense data in prior commits file
    prior_commits['Offense cleaned'] = clean_offense_blk(data = prior_commits['Offense'])
    # Extracting prior commits data with eligible offenses
    el_cdcr_nums_5 = []
    for cdcr_num in tqdm(el_cdcr_nums_4):
      # Extract offenses of the CDCR number
      offenses = prior_commits[prior_commits['CDCR #'] == cdcr_num]['Offense cleaned'].unique()
      if len(det_inel_off(offenses = offenses, inel_offenses = inel_offenses, pop = 'adult')) == 0:
        el_cdcr_nums_5.append(cdcr_num)
        
    # Store eligible CDCR numbers in adult population
    adult_el_cdcr_nums = el_cdcr_nums_5
    print('Completed search for eligible CDCR numbers in cohort 1 for adults')
    print('Number of individuals who meet all 5 eligibility conditions: they are older than 50 years, sentenced to over 20 years, served over 10 years, have eligible current offenses and eligible prior offenses: ', len(adult_el_cdcr_nums))
    
    ####
    
    # Write demophraphics and current commits of eligible individuals to Excel output
    if to_excel:
        if not write_path:
            # Write data to excel files
            write_path = '/'.join(l for l in [data_path, county_name, month] if l)
            demographics[demographics['CDCR #'].isin(adult_el_cdcr_nums)].to_excel(write_path+'/'+'adult_eligible_demographics.xlsx', index = False)
            current_commits[current_commits['CDCR #'].isin(adult_el_cdcr_nums)].to_excel(write_path+'/'+'adult_eligible_currentcommits.xlsx', index = False)
        elif write_path:
            # Write data to excel files
            demographics[demographics['CDCR #'].isin(adult_el_cdcr_nums)].to_excel(write_path+'/'+'adult_eligible_demographics.xlsx', index = False)
            current_commits[current_commits['CDCR #'].isin(adult_el_cdcr_nums)].to_excel(write_path+'/'+'adult_eligible_currentcommits.xlsx', index = False)
        print('Current commits of eligible individuals written to: ', write_path+'/'+'adult_eligible_currentcommits.xlsx')
        print('Demographics of eligible individuals written to: ', write_path+'/'+'adult_eligible_currentcommits.xlsx')
    
    return errors, adult_el_cdcr_nums


def gen_juvenile_eligibility(demographics, 
                             sorting_criteria,
                             current_commits, 
                             prior_commits, 
                             data_path = None, 
                             county_name = None, 
                             month = None,
                             to_excel = False, 
                             write_path = None):
    """

    Parameters
    ----------
        
    sorting_criteria : pandas dataframe
        Data on offenses and their categories
    demographics : pandas dataframe
        Data on individuals currently incarcerated
    current_commits : pandas dataframe
        Data on current offenses of incarcerated individuals wherein each row pertains to a single offense
    prior_commits : pandas dataframe
        Data on prior offenses of incarcerated individuals wherein each row pertains to a single offense
    data_path : str, optional
        Full path where output data should be written (all parent folders)
        Default is None.
    county_name : str, optional
        Name of the county for which eligibility was evaluated, ex: 'Los Angeles County'
        Default is None.
    month : str, optional
        Year and month for which eligibility was evaluated, ex: '2023_06'
        Default is None.
   to_excel : boolean, optional
        Specify whether to write current commitments and demographics of eligible individuals to Excel files.
        If True, specify the path information to write the output
        Default is False.
   write_path : str, optional 
        Specify the full path where the Excel outputs should be written. 
        If to_excel = True but write_path = None, data outputs are written to the county_name + month folder by default. To avoid this behavior, pass a value to write_path.
 
    Returns
    -------
    errors : pandas dataframe
        Data in the demographics dataframe for which time variables could not be computed
    juvenile_el_cdcr_nums : list of strs
        List of CDCR numbers that are eligible for resentencing 

    """
    # Add all of the time variables to the demographic data necessary for classification - years served, sentence length, age, etc.
    demographics, errors = gen_time_vars(df = demographics, merge = True)
    
    ####
    
    # Conditions to search: 1. for Cohort 2
    
    print('Checking eligibility for cohort 2: minors tried as adults')
    print('Checking eligibility for condition 1')
    # Extracting CDCR numbers that meet the age criteria
    el_cdcr_nums_1 = []
    el_cdcr_nums_1 = demographics[(demographics['Age during offense'] < 16) & (demographics['Age during offense'] >= 14)]['CDCR #'].to_list()
    
    ####
        
    # Conditions to search: 2. for Cohort 2
    
    print('Checking eligibility for condition 2')
    # Extracting ineligible offenses from sorting criteria
    inel_offenses = sorting_criteria[sorting_criteria['Table'].isin(['Table E', 'Table D'])]['Offenses'].tolist()
    inel_offenses = gen_inel_off(inel_offenses, clean = True, impl = {'187': ["2nd", "(664)"]}, perm = 2)
    # Clean offense data in current commits file
    current_commits['Offense cleaned'] = clean_offense_blk(data = current_commits['Offense'])
    # Extracting CDCR numbers that meet the age criteria and offense eligibility
    el_cdcr_nums_2 = []
    for cdcr_num in tqdm(el_cdcr_nums_1):
      # Extracting offenses of the CDCR number
      offenses = current_commits[current_commits['CDCR #'] == cdcr_num]['Offense cleaned'].unique()
      if len(det_inel_off(offenses = offenses, inel_offenses = inel_offenses, pop = 'juvenile')) == 0:
        el_cdcr_nums_2.append(cdcr_num)
    
    ####
    
    # Conditions to search: 3. for Cohort 2
    
    print('Checking eligibility for condition 3')
    # Extracting CDCR numbers that met the age and offense criteria that also meet the time served criteria
    el_cdcr_nums_3 = []
    el_cdcr_nums_3 = demographics[(demographics['Time served in years'] >= 10) & demographics['CDCR #'].isin(el_cdcr_nums_2)]['CDCR #'].to_list()
    
    ####
    
    # Conditions to search: 4. for Cohort 2
    
    print('Checking eligibility for condition 4')
    # Extracting ineligible offenses from sorting criteria
    inel_offenses = sorting_criteria[sorting_criteria['Table'].isin(['Table D'])]['Offenses'].tolist()
    inel_offenses = gen_inel_off(inel_offenses, clean = True, impl = {'187': ["2nd", "(664)"]}, perm = 2)
    # Clean offense data in current commits file
    prior_commits['Offense cleaned'] = clean_offense_blk(data = prior_commits['Offense'])
    # Extracting CDCR numbers that met the age, time sentenced and current and prior offense eligibility criteria
    el_cdcr_nums_4 = []
    for cdcr_num in tqdm(el_cdcr_nums_3):
      offenses = prior_commits[prior_commits['CDCR #'] == cdcr_num]['Offense cleaned'].unique()
      if len(det_inel_off(offenses = offenses, inel_offenses = inel_offenses, pop = 'juvenile')) == 0:
        el_cdcr_nums_4.append(cdcr_num)
    
    # Store eligible CDCR numbers in cohort 2 or juvenile population
    juvenile_el_cdcr_nums = el_cdcr_nums_4
    print('Completed search for eligible CDCR numbers in cohort 2 for juveniles sentenced as adults')
    print('Number of individuals who meet all 4 eligibility conditions: they committed offenses at age 14 and 15, have eligible current and prior offenses, and served more than 10 years: ', len(juvenile_el_cdcr_nums))
    
    ####
    
    # Write demographics and current commits of eligible individuals to Excel output
    if to_excel:
        if not write_path:
            # Write data to excel files
            write_path = '/'.join(l for l in [data_path, county_name, month] if l)
            demographics[demographics['CDCR #'].isin(juvenile_el_cdcr_nums)].to_excel(write_path+'/'+'juvenile_eligible_demographics.xlsx', index = False)
            current_commits[current_commits['CDCR #'].isin(juvenile_el_cdcr_nums)].to_excel(write_path+'/'+'juvenile_eligible_currentcommits.xlsx', index = False)
        elif write_path:
            # Write data to excel files
            demographics[demographics['CDCR #'].isin(juvenile_el_cdcr_nums)].to_excel(write_path+'/'+'juvenile_eligible_demographics.xlsx', index = False)
            current_commits[current_commits['CDCR #'].isin(juvenile_el_cdcr_nums)].to_excel(write_path+'/'+'juvenile_eligible_currentcommits.xlsx', index = False)
        print('Current commits of eligible individuals written to: ', write_path+'/'+'juvenile_eligible_currentcommits.xlsx')
        print('Demographics of eligible individuals written to: ', write_path+'/'+'juvenile_eligible_currentcommits.xlsx')
    
    return errors, juvenile_el_cdcr_nums


def viz_eligibility(adult_el_cdcr_nums, 
                    juvenile_el_cdcr_nums, 
                    demographics):
    """

    Parameters
    ----------
    adult_el_cdcr_nums : list of strs
        List of CDCR numbers in cohort 1 for adults that are eligible for resentencing
    juvenile_el_cdcr_nums : list of strs
        List of CDCR numbers in cohort 2 for juveniles sentenced as adults that are eligible for resentencing
    demographics : pandas dataframe
        Data on demographics of both juveniles and adults

    Returns
    -------
    None.

    """
    
    # Adult eligible demographics
    print('Top 20 offenses of individuals in Cohort 1 who meet all 5 eligibility conditions (from demographics data)')
    print(demographics[demographics['CDCR #'].isin(adult_el_cdcr_nums)]['Description'].value_counts()[0:20])

    print('Top 20 offenses of individuals in Cohort 1 who meet all 5 eligibility conditions (from demographics data)')
    demographics[demographics['CDCR #'].isin(adult_el_cdcr_nums)]['Controlling Offense'].value_counts()[0:20]

    print('Top 20 offenses of individuals in Cohort 1 who meet all 5 eligibility conditions (from current commits data)')
    current_commits[current_commits['CDCR #'].isin(adult_el_cdcr_nums)]['Offense'].value_counts()[0:20]

    print('Sex offenses of individuals in Cohort 1 who meet all 5 eligibility conditions')
    print(demographics[demographics['CDCR #'].isin(adult_el_cdcr_nums)]['Sex Registrant'].value_counts())

    print('Type of offenses of individuals in Cohort 1 who meet all 5 eligibility conditions')
    print(demographics[demographics['CDCR #'].isin(adult_el_cdcr_nums)]['Offense Category'].value_counts())

    ####
    
    # Juvenile eligible demographics
    print('Top 20 offenses of individuals in Cohort 2 who meet all 4 eligibility conditions (from demographics data)')
    print(demographics[demographics['CDCR #'].isin(juvenile_el_cdcr_nums)]['Description'].value_counts()[0:20])
    
    print('Top 20 offenses of individuals in Cohort 2 who meet all 4 eligibility conditions (from demographics data)')
    demographics[demographics['CDCR #'].isin(juvenile_el_cdcr_nums)]['Controlling Offense'].value_counts()[0:20]
    
    print('Sex offenses of individuals in Cohort 2 who meet all 4 eligibility conditions')
    print(demographics[demographics['CDCR #'].isin(juvenile_el_cdcr_nums)]['Sex Registrant'].value_counts())
    
    print('Type of offenses of individuals in Cohort 2 who meet all 4 eligibility conditions')
    print(demographics[demographics['CDCR #'].isin(juvenile_el_cdcr_nums)]['Offense Category'].value_counts())
    
    return


def gen_eligibility(demographics, 
                    sorting_criteria,
                    current_commits, 
                    prior_commits, 
                    eligibility_conditions,
                    pop,
                    read_path = None, 
                    county_name = None, 
                    month = None,
                    to_excel = False, 
                    write_path = None):
    
    # Add all of the time variables to the demographic data necessary for classification - years served, sentence length, age, etc.
    demographics, errors = gen_time_vars(df = demographics, merge = True)
    
    # Initialize list of eligible CDCR numbers
    el_cdcr_nums = demographics['CDCR #']
    # Clean offense data in current commits file
    current_commits['Offense cleaned'] = clean_offense_blk(data = current_commits['Offense'])
    # Clean offense data in prior commits file
    prior_commits['Offense cleaned'] = clean_offense_blk(data = prior_commits['Offense'])
    
    # Check all eligibility conditions
    if eligibility_conditions['r_1']['use']:
        # Extracting CDCR numbers with eligible ages
        print('Finding CDCR numbers that meet rule: ', eligibility_conditions['r_1']['desc'])
        el_cdcr_nums = demographics[(demographics['Age in years'] >= 50) & (demographics['CDCR #'].isin(el_cdcr_nums))]['CDCR #'].to_list()
    
    if eligibility_conditions['r_2']['use']:
        # Extracting CDCR numbers that met the age criteria that also meet the time sentenced criteria
        print('Finding CDCR numbers that meet rule: ', eligibility_conditions['r_2']['desc'])
        el_cdcr_nums = demographics[(demographics['Aggregate sentence in years'] >= 20) & (demographics['CDCR #'].isin(el_cdcr_nums))]['CDCR #'].to_list()
    
    if eligibility_conditions['r_3']['use']:
        # Extracting CDCR numbers that met the age criteria that also meet the time served criteria
        print('Finding CDCR numbers that meet rule: ', eligibility_conditions['r_3']['desc'])
        el_cdcr_nums = demographics[(demographics['Time served in years'] >= 10) & demographics['CDCR #'].isin(el_cdcr_nums)]['CDCR #'].to_list() 
    
    if eligibility_conditions['r_4']['use']:
        print('Finding CDCR numbers that meet rule: ', eligibility_conditions['r_4']['desc'])
        # Extracting ineligible offenses from sorting criteria
        inel_offenses = sorting_criteria[sorting_criteria['Table'].isin(['Table A', 'Table B', 'Table C', 'Table D'])]['Offenses'].tolist()
        # Appending new offenses based on implied ineligibility
        inel_offenses = gen_inel_off(inel_offenses, 
                                     clean = True, 
                                     impl = eligibility_conditions['r_4']['implied ineligibility'], 
                                     perm = eligibility_conditions['r_4']['perm'])
       # Extracting current commits data with eligible offenses
        el_cdcr_nums_4 = []
        for cdcr_num in tqdm(el_cdcr_nums):
          # Extract offenses of the CDCR number
          offenses = current_commits[current_commits['CDCR #'] == cdcr_num]['Offense cleaned'].unique()
          if len(det_inel_off(offenses = offenses, inel_offenses = inel_offenses)) == 0:
            el_cdcr_nums_4.append(cdcr_num)
        # Store eligible CDCR numbers
        el_cdcr_nums = el_cdcr_nums_4
    
    if eligibility_conditions['r_5']['use']:
        print('Finding CDCR numbers that meet rule: ', eligibility_conditions['r_5']['desc'])
        # Extracting ineligible offenses from sorting criteria
        inel_offenses = sorting_criteria[sorting_criteria['Table'].isin(['Table C', 'Table D'])]['Offenses'].tolist()
        # Appending new offenses based on implied ineligibility
        inel_offenses = gen_inel_off(inel_offenses, 
                                     clean = True, 
                                     impl = eligibility_conditions['r_5']['implied ineligibility'], 
                                     perm = eligibility_conditions['r_5']['perm'])
       # Extracting prior commits data with eligible offenses
        el_cdcr_nums_5 = []
        for cdcr_num in tqdm(el_cdcr_nums):
          # Extract offenses of the CDCR number
          offenses = prior_commits[prior_commits['CDCR #'] == cdcr_num]['Offense cleaned'].unique()
          if len(det_inel_off(offenses = offenses, inel_offenses = inel_offenses)) == 0:
            el_cdcr_nums_5.append(cdcr_num)
        # Store eligible CDCR numbers
        el_cdcr_nums = el_cdcr_nums_5
        
    if eligibility_conditions['r_6']['use']:
        print('Finding CDCR numbers that meet rule: ', eligibility_conditions['r_6']['desc'])
        # Extracting CDCR numbers that meet the age criteria
        el_cdcr_nums = demographics[(demographics['Age during offense'] < 16) & (demographics['Age during offense'] >= 14)]['CDCR #'].to_list()
        
    if eligibility_conditions['r_7']['use']:
        print('Finding CDCR numbers that meet rule: ', eligibility_conditions['r_7']['desc'])
        # Extracting ineligible offenses from sorting criteria
        inel_offenses = sorting_criteria[sorting_criteria['Table'].isin(['Table E', 'Table D'])]['Offenses'].tolist()
        inel_offenses = gen_inel_off(inel_offenses, 
                                     clean = True, 
                                     impl = eligibility_conditions['r_7']['implied ineligibility'], 
                                     perm = eligibility_conditions['r_7']['perm'])
      # Extracting CDCR numbers that meet the age criteria and offense eligibility
        el_cdcr_nums_7 = []
        for cdcr_num in tqdm(el_cdcr_nums):
          # Extracting offenses of the CDCR number
          offenses = current_commits[current_commits['CDCR #'] == cdcr_num]['Offense cleaned'].unique()
          if len(det_inel_off(offenses = offenses, inel_offenses = inel_offenses)) == 0:
            el_cdcr_nums_7.append(cdcr_num)
        # Store eligible CDCR numbers
        el_cdcr_nums = el_cdcr_nums_7
        
    if eligibility_conditions['r_8']['use']:
        print('Finding CDCR numbers that meet rule: ', eligibility_conditions['r_8']['desc'])
        # Extracting CDCR numbers that met the age and offense criteria that also meet the time served criteria
        el_cdcr_nums = demographics[(demographics['Time served in years'] >= 10) & (demographics['CDCR #'].isin(el_cdcr_nums))]['CDCR #'].to_list()
        
    if eligibility_conditions['r_9']['use']:
        print('Finding CDCR numbers that meet rule: ', eligibility_conditions['r_9']['desc'])
        # Extracting ineligible offenses from sorting criteria
        inel_offenses = sorting_criteria[sorting_criteria['Table'].isin(['Table D'])]['Offenses'].tolist()
        inel_offenses = gen_inel_off(inel_offenses, 
                                     clean = True, 
                                     impl = eligibility_conditions['r_9']['implied ineligibility'], 
                                     perm = eligibility_conditions['r_9']['perm'])
       # Extracting CDCR numbers that met the age, time sentenced and current and prior offense eligibility criteria
        el_cdcr_nums_9 = []
        for cdcr_num in tqdm(el_cdcr_nums):
          offenses = prior_commits[prior_commits['CDCR #'] == cdcr_num]['Offense cleaned'].unique()
          if len(det_inel_off(offenses = offenses, inel_offenses = inel_offenses)) == 0:
            el_cdcr_nums_9.append(cdcr_num)
        # Store eligible CDCR numbers in cohort 2 or juvenile population
        el_cdcr_nums = el_cdcr_nums_9

    ####
    
    # Write demophraphics and current commits of eligible individuals to Excel output
    if to_excel:
        if write_path:
            pass
        else:
            write_path = '/'.join(l for l in [read_path, county_name, month] if l)
        # Write data to excel files
        demographics[demographics['CDCR #'].isin(el_cdcr_nums)].to_excel(write_path+'/'+pop+'_eligible_demographics.xlsx', index = False)
        current_commits[current_commits['CDCR #'].isin(el_cdcr_nums)].to_excel(write_path+'/'+pop+'_eligible_currentcommits.xlsx', index = False)

    print('Current commits of eligible individuals written to: ', write_path+'/'+pop+'_eligible_currentcommits.xlsx')
    print('Demographics of eligible individuals written to: ', write_path+'/'+pop+'_eligible_demographics.xlsx')
    
    return errors, el_cdcr_nums
            
