
from dotenv import load_dotenv
import os
from .dialog import Dialog
import requests
import re
from geopy.geocoders import Nominatim
import geopy.distance
from geopy.distance import geodesic
import pgeocode 

load_dotenv()
# openai_org_id = ''
# openai_key = '' 
# llama2_key = ''


states = {
    "Alabama": "AL",
    "Alaska": "AK",
    "Arizona": "AZ",
    "Arkansas": "AR",
    "California": "CA",
    "Colorado": "CO",
    "Connecticut": "CT",
    "Delaware": "DE",
    "Florida": "FL",
    "Georgia": "GA",
    "Hawaii": "HI",
    "Idaho": "ID",
    "Illinois": "IL",
    "Indiana": "IN",
    "Iowa": "IA",
    "Kansas": "KS",
    "Kentucky": "KY",
    "Louisiana": "LA",
    "Maine": "ME",
    "Maryland": "MD",
    "Massachusetts": "MA",
    "Michigan": "MI",
    "Minnesota": "MN",
    "Mississippi": "MS",
    "Missouri": "MO",
    "Montana": "MT",
    "Nebraska": "NE",
    "Nevada": "NV",
    "New Hampshire": "NH",
    "New Jersey": "NJ",
    "New Mexico": "NM",
    "New York": "NY",
    "North Carolina": "NC",
    "North Dakota": "ND",
    "Ohio": "OH",
    "Oklahoma": "OK",
    "Oregon": "OR",
    "Pennsylvania": "PA",
    "Rhode Island": "RI",
    "South Carolina": "SC",
    "South Dakota": "SD",
    "Tennessee": "TN",
    "Texas": "TX",
    "Utah": "UT",
    "Vermont": "VT",
    "Virginia": "VA",
    "Washington": "WA",
    "West Virginia": "WV",
    "Wisconsin": "WI",
    "Wyoming": "WY"
}

neighbor_states = {
    'AL': ['MS', 'TN', 'GA', 'FL'],
    'AK': ['WA'],
    'AZ': ['CA', 'NV', 'UT', 'CO', 'NM'],
    'AR': ['MO', 'TN', 'MS', 'LA', 'TX', 'OK'],
    'CA': ['OR', 'NV', 'AZ'],
    'CO': ['WY', 'NE', 'KS', 'OK', 'NM', 'AZ', 'UT'],
    'CT': ['NY', 'MA', 'RI'],
    'DE': ['MD', 'PA', 'NJ'],
    'FL': ['GA', 'AL'],
    'GA': ['NC', 'SC', 'FL', 'AL', 'TN'],
    'HI': ['WA'],
    'ID': ['MT', 'WY', 'UT', 'NV', 'OR', 'WA'],
    'IL': ['WI', 'IA', 'MO', 'KY', 'IN'],
    'IN': ['MI', 'OH', 'KY', 'IL'],
    'IA': ['MN', 'WI', 'IL', 'MO', 'NE', 'SD'],
    'KS': ['NE', 'MO', 'OK', 'CO'],
    'KY': ['IN', 'OH', 'WV', 'VA', 'TN', 'MO', 'IL'],
    'LA': ['TX', 'AR', 'MS'],
    'ME': ['NH'],
    'MD': ['PA', 'DE', 'VA', 'WV'],
    'MA': ['NH', 'VT', 'NY', 'CT', 'RI'],
    'MI': ['WI', 'IN', 'OH'],
    'MN': ['WI', 'IA', 'SD', 'ND'],
    'MS': ['LA', 'AR', 'TN', 'AL'],
    'MO': ['IA', 'IL', 'KY', 'TN', 'AR', 'OK', 'KS', 'NE'],
    'MT': ['ND', 'SD', 'WY', 'ID'],
    'NE': ['SD', 'IA', 'MO', 'KS', 'CO', 'WY'],
    'NV': ['OR', 'ID', 'UT', 'AZ', 'CA'],
    'NH': ['VT', 'ME', 'MA'],
    'NJ': ['NY', 'DE', 'PA'],
    'NM': ['AZ', 'UT', 'CO', 'OK', 'TX'],
    'NY': ['VT', 'MA', 'CT', 'NJ', 'PA'],
    'NC': ['VA', 'SC', 'GA', 'TN'],
    'ND': ['MN', 'SD', 'MT'],
    'OH': ['MI', 'PA', 'WV', 'KY', 'IN'],
    'OK': ['KS', 'MO', 'AR', 'TX', 'NM', 'CO'],
    'OR': ['WA', 'ID', 'NV', 'CA'],
    'PA': ['NY', 'NJ', 'DE', 'MD', 'WV', 'OH'],
    'RI': ['MA', 'CT'],
    'SC': ['NC', 'GA'],
    'SD': ['ND', 'MN', 'IA', 'NE', 'WY', 'MT'],
    'TN': ['KY', 'VA', 'NC', 'GA', 'AL', 'MS', 'AR', 'MO'],
    'TX': ['NM', 'OK', 'AR', 'LA'],
    'UT': ['ID', 'WY', 'CO', 'NM', 'AZ', 'NV'],
    'VT': ['NY', 'NH', 'MA'],
    'VA': ['MD', 'DC', 'NC', 'TN', 'KY', 'WV'],
    'WA': ['ID', 'OR'],
    'WV': ['OH', 'PA', 'MD', 'VA', 'KY'],
    'WI': ['MI', 'MN', 'IA', 'IL'],
    'WY': ['MT', 'SD', 'NE', 'CO', 'UT', 'ID']
}


# API endpoint URL
url = "https://api.test.transplantcentersearch.org/search"
#
# Headers
headers = {
    "Content-Type": "application/json",
    "sec-ch-ua": "\"Not_A Brand\";v=\"8\", \"Chromium\";v=\"120\", \"Google Chrome\";v=\"120\"",
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": "\"Windows\""
}    

payload = {
        "organ": 'heart',
        "donorType": 'deceased',
        "distanceZipCode": '',
        "distanceMiles": '',
        "distanceState": ''
    }

    
async def extract_zipcode(answer, context):
    print("Your input is: " + answer)
    
    if (re.match(r"\d{5}", answer) is not None) and (zipcode:= re.match(r"\d{5}", answer)[0]):
        context["zipcode"] = zipcode
        return zipcode
    else:
        #print("it is None")
        return None
async def extract_search_radius(answer, context):
    print(f"Your input is: {answer}")
    context['donorCount'] = True
    if (re.match(r"\d+", answer) is not None) and (search_radius:= re.match(r"\d+", answer)[0]):
        if (int(search_radius) > 0 and int(search_radius) <= 50):
            context["search_radius"] = '50'
        elif (int(search_radius) > 50 and int(search_radius) <= 100):
            context["search_radius"] = '100'
        elif (int(search_radius) > 100 and int(search_radius) <= 250):
            context["search_radius"] = '250'
        elif (int(search_radius) > 250 and int(search_radius) <= 500):
            context["search_radius"] = '500'
        elif (int(search_radius) > 500):
            context["search_radius"] = '700'
        
        return '1'
    else:
        #print("it is None")
        return None
    
async def map_state(answer, context):
    print("Your choice is:", answer)
    context['donorCount'] = True
    if(answer in states.keys()):
        context["state"] = states[str(answer)]
        context["main_state"] = states[str(answer)]
        context['neighbor_states'] = neighbor_states[context['main_state']]
        if context['ask_path']:
            return "search_type"

        if context["organ_choice"] in ['heart','lung']:
            return "candidate_age"
        else:
            return "donor_types"
    else: 
        return None

async def get_state_from_zip(zip_code):
    nomi = pgeocode.Nominatim('us')
    result = nomi.query_postal_code(zip_code)
    return states[result.state_name]

async def get_coordinates_from_zip(zip_code):
    nomi = pgeocode.Nominatim('us') 
    loc = nomi.query_postal_code(zip_code) 
    return (loc.latitude, loc.longitude)

async def get_distance_bw_coordinates(a,b):
    return geopy.distance.geodesic(a, b).miles





# def expanded_constraint_search(answer,context):

#     # response = context['response_json']
#     #Using soft constraints to expand the search
#     s_constraint = ''
#     if context['response_json'] == []:
#         # changing search radius to expand the search
#         i = 0
#         while True:
#             if context['search_radius']:
#                 s_constraint = 'search_radius'
#                 context['search_radius'] = ''  # if its none then it's' search radius is  max
#                 context['state'] = get_state_from_zip(context['zipcode'])
#                 # payload['distanceMiles'] = context['search_radius']
#                 # payload['distanceState'] = context['state']
#                 post_to_transplant_center_search(answer, context)
#                 # response = requests.post(url, json=payload, headers=headers)
#         #
#         #     try:
#         #         # changing states to neighbor state to expand the search
#         #         if context['state'] and context['response_json'] == []:
#         #             print(f"No centers in the state {context['state']}, finding centers in other nearby states")
#         #             s_constraint = 'state'
#         #             context['neighbor_states'] = neighbor_states[context['main_state']]
#         #             if context['neighbor_states'] != []:
#         #                 context['state'] = context['neighbor_states'].pop(0)
#         #                 payload['distanceState'] = context['state']
#         #                 post_to_transplant_center_search(answer, context)
#         #             # response = requests.post(url, json=payload, headers=headers)
#         # #            
#         #     except Exception as e:
#         #         # This block will catch any other exceptions that might occur
#         #         print(f"No centers in neighbor state {context['state']} too.. finding centers in other nearby states and by modifying other soft constraint responses")
#         #         break

#         #     i += 1
            
#             print(f'loop{i}') 
#             if context['response_json'] != []:
#                 # print(f'changed {s_constraint}: {context[s_constraint]}')
#                 print(context['response_json'])
#                 break
        
#         if context['response_json'] == []:
#             context['neighbor_states'] = neighbor_states[context['main_state']]   
#             while context['neighbor_states'] != []:
#                     context['state'] = context['neighbor_states'].pop(0)
#                     payload['distanceState'] = context['state']
#                     post_to_transplant_center_search(answer, context)               
#                     if context['BMI'] and context['response_json'] == []:
#                         s_constraint = 'BMI'
#                         if context['BMI'] > 35:
#                             print('If you change the BMI to less than 35 you can get more centers')
#                             context['BMI'] = 34
                        

#                     if context['candidate_insurance_provider'] and context['response_json'] == []:
#                         s_constraint = 'candidate_insurance_provider'
#                         if context['candidate_insurance_provider'] == 'medicaid':
#                             context['candidate_insurance_provider'] = 'non-medicaid'
#                         # response = requests.post(url, json=payload, headers=headers)  
#                     filter_response(answer,context) 
#                     if context['response_json'] != []:
#                         print(f'changed {s_constraint}: {context[s_constraint]}')
#                         break

#         if context['response_json'] == [] and i == 10:
#             print("Sorry, we couldn't find any centers based on your choices. Please contact https://srtr.org for more information")

async def expanded_constraint_search(answer,context):

    # response = context['response_json']
    #Using soft constraints to expand the search
    bmi = context['BMI']
    hepatitis_c = context['is_candidate_hepatitis_c_positive']
    response = context['responce_json']
    insurance = context['candidate_insurance_provider']
    s_constraint = ''
    advice = []
    filter = []

    if bmi:
        adv = ""
        
        if bmi > 40:
            filter_key = 'bmiOverForty'
            if [response[i] for i in response if response[i]['bmiOverForty'] != 0] == []:
                bmi = 40
                adv = "You might need to reduce your BMI to less than or equal to 40 to find better centers"
                filter_key = 'bmiOverThirtyFive'
                if [response[i] for i in response if response[i]['bmiOverThirtyFive'] != 0] == []:
                    bmi = 35
                    adv = "You might need to reduce your BMI to less than or equal to 35 to find better centers"
                    filter_key = 'bmiOverThirty'
                    if [response[i]for i in response if response[i]['bmiOverThirty'] != 0] == []:
                        bmi = 30
                        adv = "You might need to reduce your BMI to less than or equal to 30 to find better centers"
                        filter_key = ''
        elif bmi >35 and bmi<=40:
            filter_key = 'bmiOverThirtyFive'
            if [response[i] for i in response if response[i]['bmiOverThirtyFive'] != 0] == []:
                bmi = 35
                adv = "You might need to reduce your BMI to less than or equal to 35 to find better centers"
                filter_key = 'bmiOverThirty'
                if [response[i] for i in response if response[i]['bmiOverThirty'] != 0] == []:
                    bmi = 30
                    adv = "You might need to reduce your BMI to less than or equal to 30 to find better centers"
                    filter_key = ''
        elif bmi >30 and bmi<=35:   
            filter_key = 'bmiOverThirty'
            if [response[i] for i in response if response[i]['bmiOverThirty'] != 0] == []:
                bmi = 30
                adv = "You might need to reduce your BMI to less than or equal to 30 to find better centers" 
                filter_key = ''

        advice.append(adv)
        if filter_key != '':
            filter.append(filter_key)
        

    if insurance:
        adv = ""
        if insurance == 'medicaid':
            filter_key = 'insuranceMedicaid'
            if [response[i] for i in response if response[i]['insuranceMedicaid'] != 0] == []:
                insurance = 'non-medicaid'
                adv = "You might need to change the insurance to Non Medicaid to find better centers"
                filter_key = ''
        if insurance == 'non-insurance':
            insurance = 'non-medicaid'
            adv = "You might need to buy Non Medicaid insurance plan to find better centers"
            filter_key = ''

        advice.append(adv)
        if filter_key != '':
            filter.append(filter_key)

    if hepatitis_c:
        if  hepatitis_c == 'yes-active':
            filter_key = 'donorHepCPositiveRecipientHepCPositive'
            if [response[i] for i in response if response[i]['donorHepCPositiveRecipientHepCPositive'] != 0] == []:
                hepatitis_c = 'yes-treated'
                adv = "You might need to get treated for Hepatitis C to find better centers"
                filter_key = 'donorHepCPositiveRecipientHepCNegative'

    results = []
    
    for i in range(len(response)):
        skip_flag = False
        for j in filter:
            if response[i][j] == 0 :
                skip_flag = True
                break
        if response[i] not in results and skip_flag is False:
            results.append(response[i])

    if results == []:
        print("Found null response after passing through expanded constraint search")
        print("Sorry, we couldn't find any centers based on your choices. Please contact https://srtr.org for more information")   
    else:
        context['response_json'] = results

async def check_and_expand_search_if_null_response(answer,context):
    if context['response_json'] == []:
        expanded_constraint_search(answer,context)
        if context['response_json'] == []:
                # print("Sorry, we couldn't find any centers based on your choices. Please contact https://srtr.org for more information")
                return False
    else:
        print("Skipping check and expand search since response is not null!")         
        return True
    

async def filter_sc_response(answer,context):
    bmi = context['BMI']
    hepatitis_c = context['is_candidate_hepatitis_c_positive']
    response = context['responce_json']
    insurance = context['candidate_insurance_provider']
    response = context['response_json']
    filter = []

    if bmi:
        if bmi >30 and bmi<=35:
            filter.append('bmiOverThirty')
        elif bmi >35 and bmi<=40:
            filter.append('bmiOverThirtyFive')
        elif bmi >40:
            filter.append('bmiOverForty')

    if hepatitis_c:
        if  hepatitis_c == 'yes-active':
            filter.append('donorHepCPositiveRecipientHepCPositive')
        elif hepatitis_c == 'yes-treated':
            filter.append('donorHepCPositiveRecipientHepCNegative')

    results = []

    print(f"Before passing SC: {len(response)}")
    if filter != []:

        for i in range(len(response)):
            skip_flag = False
            for j in filter:
                if response[i][j] == 0 :
                    skip_flag = True
                    break
            if response[i] not in results and skip_flag is False:
                results.append(response[i])
    else:
        results = response
    print(f"After passing SC: {len(results)}")

    if results != []:
        #print(f"Soft_Constraints_filtered_response: {results}")
        context['response_json'] = results
        return True
    elif check_and_expand_search_if_null_response(answer,context):
        #print(f"Soft_Constraints_filtered_response: {results}")
        context['response_json'] = results
        return True
    else:
        print("Found null response after passing through SC filter")
        return False

                
async def filter_hc_response(answer,context):
    age = context['candidate_age']
    hiv = context['is_candidate_hiv_positive']
    diabetic = context['is_candidate_diabetic']
    response = context['response_json']
    
    filter = []

    if age:
        if age >65 and age<=70:
            if context['response_json'] != []:
                filter.append('ageOverSixtyFive')
        elif age>70:
            if context['response_json'] != []:
                filter.append('ageOverSeventy')

    if hiv:
        print(f"hiv: {hiv}")
        if hiv == 'yes':
            if context['response_json'] != []:
                filter.append('donorHIVPositive')
                # filter.append('recipientHIVPositive')

    if diabetic:
        if diabetic == 'yes':
            if context['response_json'] != []:
                filter.append('diabetes')

    results = []
    print(f"Before passing HC: {len(response)}")
    for i in range(len(response)):
        skip_flag = False
        for j in filter:
            if response[i][j] == 0 :
                skip_flag = True
                break
        if response[i] not in results and skip_flag is False:
            results.append(response[i])
    print(f"Affter passing HC: {len(results)}")
    if results != []:
        #print(f"Hard_Constraints_filtered_response: {results}")
        context['response_json'] = results
        return True
    else:
        print("Found null response after passing through HC filter")
        print("Sorry, we couldn't find any centers based on your choices. Please contact https://srtr.org for more information")
        return False
            

    
async def post_to_transplant_center_search(answer, custom_values):
    # Create the JSON payload
    payload = {
        "organ": custom_values["organ_choice"],
        "donorType": custom_values["donor_type"],
        "distanceZipCode": custom_values["zipcode"],
        "distanceMiles": custom_values["search_radius"],
        "distanceState": custom_values["state"]
    }
    # Send the POST request
    response = requests.post(url, json=payload, headers=headers)
    custom_values["response_json"] = response.json()
    # if custom_values['response_json'] == [] and custom_values['donorCount']:
    #     print("Sorry, we currently don't have any centers matching your search criteria. Do you want to try considering other States/Distance in your search?")
    #     custom_values['ask_path'] = True
    
    print(f'response : {response.json()}')

    # if not custom_values['donorCount'] and custom_values['response_json'] != []:
    #     # Print the response content
    #     print(response.json())
        
    # if custom_values['response_json'] != []:
    #     if custom_values['candidate_age']:
            

    # if custom_values['print_flag']:
    #     print(response.json())
    
    return "1"

async def add_filters_and_post(answer,context):
    # temp_url = "https://api.test.transplantcentersearch.org/odata/heartmetrics/GetMetricsByCenterDistance(ZipCode='55417',Distance=500)?$expand=center&$filter=(DeceasedDonor%20lt%2015)%20and%20(Diabetes%20gt%200)"
    temp_url = f"https://api.test.transplantcentersearch.org/odata/{context['organ_choice']}metrics"
    if context['state']:
        temp_url += f"?$expand=center&$filter=center/state eq '{context['state']}' and "
    elif context['zipcode']:
        temp_url += f"/GetMetricsByCenterDistance(ZipCode='{context['zipcode']}',Distance={context['search_radius']})?$expand=center&$filter="
    
    if context['donor_type']:
        if context['donor_type'] == 'both':
            temp_url += "(LivingDonor gt 0) and (DeceasedDonor gt 0)"
        elif context['donor_type'] == 'living':
            temp_url += "(LivingDonor gt 0)"
        elif context['donor_type'] == 'deceased':
            temp_url += "(DeceasedDonor gt 0)"
    else:
        print("donor type is null")

    context['proximal_centers'] = requests.get(temp_url)

    if context['candidate_age']:
        if context['candidate_age'] > 70:
            temp_url += " and (AgeOverSeventy gt 0)"
        elif context['candidate_age'] > 65:
            temp_url += " and (AgeOverSixtyFive gt 0)"
        
    if context['BMI']:
        if context['BMI'] > 40:
            temp_url += " and (BMIOverForty gt 0)"
        elif context['BMI'] > 35:
            temp_url += " and (BMIOverThirtyFive gt 0)" 
        elif context['BMI'] > 30:
            temp_url += " and (BMIOverThirty gt 0)"    

    if context['candidate_organ_disease_cause']:
        if context['organ_choice'] == 'heart':
            if context['candidate_organ_disease_cause'].lower() == 'heart valve disease':
                temp_url += " and (CauseOfHeartDiseaseValvularHeartDisease gt 0)"
            elif context['candidate_organ_disease_cause'].lower() == 'congenital disease':
                temp_url += " and (CauseOfHeartDiseaseCongenitalHeartDisease gt 0)"
            elif context['candidate_organ_disease_cause'].lower() == 'cardiomyopathy':
                temp_url += " and (CauseOfHeartDiseaseCardiomyopathy gt 0)"
            elif context['candidate_organ_disease_cause'].lower() == 'coronary artery disease':
                temp_url += " and (CauseOfHeartDiseaseCoronaryArteryDisease gt 0)"
            elif context['candidate_organ_disease_cause'].lower() == 'other':
                temp_url += " and (CauseOfHeartDiseaseOther gt 0)" 

        # for lung
        # for kidney
        # for liver
    
    if context['is_candidate_diabetic']:
        if context['organ_choice'] == "heart" and context['is_candidate_diabetic'].lower() == 'yes':
            temp_url += " and (Diabetes gt 0)"

    # insurance skipped bcoz it can be changed and its not an HC

    if context['is_candidate_hiv_positive'] and context['is_candidate_hiv_positive'].lower() == 'yes':
        temp_url += "and (RecipientHIVPositive gt 0)"

    # hep b

    if context['is_candidate_hepatitis_c_positive']:
        if context['is_candidate_hepatitis_c_positive'].lower() == 'yes-active':
            temp_url += " and (DonorHepCPositiveRecipientHepCPositive gt 0)"
        # elif context['is_candidate_hepatitis_c_positive'].lower() == 'yes-treated':
        #     temp_url += " and (DonorHepCPositiveRecipientHepCNegative gt 0)"

    if context['is_candidate_had_previous_organ_transplant'] and context['is_candidate_had_previous_organ_transplant'].lower() == 'yes':
        temp_url += " and (Retransplant gt 0)"

    # if context['is_candidate_had_previous_organ_transplant'] and context['is_candidate_had_previous_organ_transplant'].lower() == 'yes':
    #     temp_url += " and (MultiOrganTx gt 0)"

    


    print(temp_url)
    response = requests.get(temp_url)


    # Check if the request was successful
    if response.status_code == 200:
        # Assuming the response is JSON
        data = response.json()
        print("Data retrieved successfully!")
        print(data)
    else:
        print("Failed to retrieve data. Status code:", response.status_code)

    return "1"


async def get_all_response(answer,context):
    payload = {
        "organ": context["organ_choice"],
        "donorType": '',
        "distanceZipCode": '',
        "distanceMiles": '',
        "distanceState": ''
    }

    response = requests.post(url, json=payload, headers=headers)
    context["response_json"] = response.json()

    return "1"


async def print_results(answer,context):
    get_all_response(answer,context)
    print(len(context['response_json']))
    if context['response_json']:
        filter_hc_response(answer,context)
        print(f"After passing the HC filter:  {len(context['response_json'])}")
        filter_sc_response(answer,context)  
        print(f"After passing the SC filter:  {len(context['response_json'])}")
        
        if context['response_json'] != []:
            for i in context['response_json']:
                print("##############################################################################")
                print(f"Center Name: {i['centerName']}")
                print(f"Center Address: {i['centerAddress1']}, {i['centerCity']}, {i['centerState']}")
                print(f"Center Website: {i['centerUrl']}")
                print(f"Center Phone Number: {i['centerPhoneNumber']}")
                print("##############################################################################")

    return '1'

async def get_donor_type(answer,context):
    print("Your choice is:", answer)
    if answer=="living":
      context["donor_type"] = answer
    elif answer == "deceased":
        context["donor_type"] = answer
    elif answer == "both":
        context["donor_type"] = answer
    else:
        return None
    
    return "search_type"
# def write_donor_count(answer, context):
#     living = 0
#     deceased = 0
#     response_json = context["response_json"]
#     context['donor_available'] = "None"
#     if context["donorCount"]:            
#         for i in range(len(response_json)):
#             if response_json[i]['livingDonor'] != 0:
#                 living += 1
#             if response_json[i]['deceasedDonor'] != 0:
#                 deceased += 1
#             if living != 0 and deceased != 0:
#                 break
#         if living != 0:                
#             context['donor_available'] = "1. living donor"
#         else:
#             context['skip_donor_type'] = True
#         if deceased != 0:                
#             context['donor_available'] = "1. deceased donor"
#         if living != 0 and deceased != 0:                
#             context['donor_available'] = "1. living donor 2.deceased donor 3. pursuing both"
#     context["donorCount"] = False
#     # if not context["donorCount"]:
#     #     print("changed to False")
#     # else:
#     #     print("didnt change to False")
    
#     return "1"
async def get_donor_count(answer, context):
    living = 0
    deceased = 0
    response_json = context["response_json"]
    
    if context["donorCount"]:            
        for i in range(len(response_json)):
            if response_json[i]['livingDonor'] != 0:
                living += 1
            if response_json[i]['deceasedDonor'] != 0:
                deceased += 1
            if living != 0 and deceased != 0:
                break
        if living == 0:                
            context['skip_donor_type'] = True
            print("No living donors hence skipping donor type")
        if living == 0 and deceased != 0:
            context['donor_type'] = 'deceased'
    context["donorCount"] = False
    # if context['skip_donor_type']:
    #     post_to_transplant_center_search(answer=answer, custom_values=context)
    
    
    return "1"
async def check_donor_type_required(answer,context):
    if context["skip_donor_type"]:
        return "end"
    else:
        return "donor_type"
    
async def validate_user_age(answer, context):
    if answer.lower() == "other":
        return None
    age = int(answer)
    if age >=1 and age<=150:
        context['candidate_age'] = age
    else:
        return None 
    
    if age<18: 
        print("Note: This website includes only data fo adult transplant candidates. All data shown will be for adults. Data for pediatric candidates can be found at www.srtr.org.")
    if age>=65 and age<=69:
        if context['organ_choice'] == 'kidney':
            print('Note: Given long wait times of several years, it may become important for you to know that centers have different age criteria for candidates, especially for those close to age 70, that may impact your options.')
        elif context['organ_choice'] == 'lung':
            print('Note: Centers have different age criteria for candidates that may impact your options.')
        else:
            print('Note: Centers have different age criteria for candidates that may impact your options.')
            return context['candidate_age']
    if age >= 70:
        print('Note: Centers have different age criteria for candidates that may impact your options.')
    return context['candidate_age']

async def validate_candidate_height(answer,context):
    if answer.lower() == 'other':
        return None
    feet_inches = answer.split("'")
    ft = int(feet_inches[0])  # Extracting feet part
    inch = int(feet_inches[1].strip('"'))
    print(f"{ft}feet and {inch}inches")
    
    if ft > 0 and ft<10:
        if inch>=0 and inch< 12:
            context['candidate_height_ft'] = ft
            context['candidate_height_inch'] = inch
    else:
        return None
    
    return '1'
async def validate_candidate_weight(answer,context):
    if answer.lower() == "other":
        return None
    lb = int(answer)
    if lb>=0 and lb<=1000:
        context['candidate_weight'] = lb
    else: 
        return None
    return lb

async def calculate_BMI(answer,context):
    # Convert height in feet and inches to meters
    feet = context['candidate_height_ft']
    inches = context['candidate_height_inch']
    pounds = context['candidate_weight']
    total_inches = feet * 12 + inches
    height_meters = total_inches * 0.0254
    # Convert weight from pounds to kilograms
    weight_kilograms = pounds * 0.453592
    # if height_meters <= 0:
    #     return "Height must be greater than zero."
    # if weight_kilograms <= 0:
    #     return "Weight must be greater than zero."
    # Calculate BMI
    bmi = round(weight_kilograms / (height_meters ** 2) , 2)
    context['BMI'] = bmi
    
    if bmi>35:
        print('Centers have different weight criteria for candidates that may impact your options.')
    print(f"Your BMI: {bmi}")
    return bmi

async def get_blood_type(answer,context):
    if answer.lower() in ['a', 'b', 'ab', 'o','notsure']:
        context['candidate_blood_type'] = answer.lower()
        if answer == 'B':
            print("Note: Waiting times for Blood type B are often longer than other types. Centers with 'Blood Type B Programs' may have a wider range of donors available.")
        return answer
    else:
        return None

async def get_disease_cause(answer,context):
    
    temp_key = context['organ_choice'] + '_choices'
    if answer.isdigit():
        answer = int(answer)
        context['candidate_organ_disease_cause'] = context[temp_key][answer]
    else:
        return None 
    if context['candidate_organ_disease_cause'].lower() == 'diabetes' and context['organ_choice'] == 'heart':
        print("Note: Some centers have more experience conducting heart transplants in diabetics.")

    print(f"{context['candidate_organ_disease_cause']}")
    return context['candidate_organ_disease_cause']

async def get_is_multiorgan_candidate(answer,context):
    if answer.lower() in ['yes', 'no', 'yes_liver_kidney', 'yes_spk', 'yes_other', 'notSure']:
      context['is_multiorgan_candidate'] = answer.lower()
      if answer.lower() == 'yes':
          print("Note: Multi-organ transplants are rare, contact potential transplant centers to find out if this an option.")
      if answer.lower() == 'yes_other' and context['organ_choice'] == 'liver':
          print("Note: Multi-organ transplants other than Liver-Kidney are rare, contact potential transplant centers to find out if this is an option.")
    elif answer.lower() == 'notSure':
      context['is_multiorgan_candidate'] = 'notSure'
    else:
        return None
    return '1'

# if __name__ == "__main__":




    
    # dialog = Dialog(treefile="example1.xml", functions={'extract_zipcode': extract_zipcode, 
    #                                                    'extract_search_radius': extract_search_radius, 
    #                                                    'map_state': map_state,
    #                                                    'expanded_constraint_search': expanded_constraint_search,
    #                                                    'check_and_expand_search_if_null_response':check_and_expand_search_if_null_response,
    #                                                    'filter_hc_response': filter_hc_response,
    #                                                    'filter_sc_response': filter_sc_response,
    #                                                    'post_to_transplant_center_search': post_to_transplant_center_search,
    #                                                    'get_all_response': get_all_response,
    #                                                    'print_results': print_results,
    #                                                    'get_donor_type': get_donor_type,
    #                                                    'get_donor_count': get_donor_count,
    #                                                    'check_donor_type_required': check_donor_type_required,
    #                                                    'validate_user_age': validate_user_age,
    #                                                    'validate_candidate_height': validate_candidate_height,
    #                                                    'validate_candidate_weight': validate_candidate_weight,
    #                                                    'calculate_BMI': calculate_BMI,
    #                                                    'get_blood_type': get_blood_type,
    #                                                    'get_disease_cause': get_disease_cause,
    #                                                    'get_is_multiorgan_candidate': get_is_multiorgan_candidate,
    #                                                    'add_filters_and_post': add_filters_and_post
    #                                                    }, openai_key=openai_key, openai_org_id=openai_org_id, llama2_key=llama2_key, model="gpt-4")
    # dialog.start()

#     # Define your routes
#     @app.route('/start_dialog', methods=['GET'])
#     def start_dialog():
#         # Start your dialog here
#         dialog.start()
#         return "Dialog started"

#     @app.route('/user_input', methods=['POST'])
#     def user_input():
#         data = request.json
#         user_message = data.get('message')
#         # Process user input here
#         return "User input received: " + user_message
    
#     @app.route('/webhook', methods=['POST'])
#     def webhook():

#         dialog.start()
#         # user_message = request.json['message']
        
#         # print(user_message)

#         # bot_response = requests.post(RASA_API_URL, json={'message': user_message})
#         # rasa_response_json = rasa_response.json()

#         # print("Rasa Response:", rasa_response_json)

#         # bot_response = rasa_response_json if rasa_response_json else 'ok'

#         # return jsonify({'response': bot_response})


# if __name__ == '__main__':
#     app.run(debug=True, port=5000)