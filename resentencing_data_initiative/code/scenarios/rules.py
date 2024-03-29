# -*- coding: utf-8 -*-

r_1 = 'Age 50 and older'
r_2 = 'Sentenced to 20 years or more'
r_3 = 'Served a minimum of 10 years in custody'
r_4 = 'Is not serving a current sentence for any offense listed in Table A, B, C, or D and their implied offenses (from sorting_criteria.xlsx)'
r_5 = 'Does not have a prior conviction for any offense listed in Tables C & D and their implied offenses (from sorting_criteria.xlsx)'
r_6 = 'Sentenced for a crime that was committed at age 14 or 15'
r_7 = 'Is not serving current sentence for any offense listed in Table D and E and their implied offenses (from sorting_criteria.xlsx)'
r_8 = 'Does not have a prior conviction for any offense listed in Table D and its implied offenses (from sorting_criteria.xlsx)'
r_9 = 'Is serving current sentence for at least one offense listed in Table F and its implied offenses (from sorting_criteria.xlsx)'
r_10 = 'Has a controlling offense that is present in Table F (from sorting_criteria.xlsx)'
r_11 = 'Does not have an enhancement that contains PC 12022'
r_12 = 'Is not serving a current sentence for any offense listed in Table A, B (minus Table F), C or D and their implied offenses (from sorting_criteria.xlsx)'
r_13 = 'Served a minimum of 15 years in custody'

cat = {'age related': [r_1, r_6],
       'sentence length related': [r_2, r_3, r_13],
       'current offenses related': [r_4, r_7, r_12, r_9, r_10],
       'prior offenses related': [r_5, r_8],
       'controlling offense related': [r_10], 
       'enhancement related': [r_11]}
