import asyncio, os
from .conversation_controller import ConversationController
from dataclasses import dataclass
from ..dialogtree.dialog import Dialog
# from ..config import org_id, openai_key 
from ..dialogtree.helper_functions import *

call_dict = {}

@dataclass
class CallState:
    call_sid: str
    history: list
    controller: ConversationController
    outbound_call_script: str
    inbound_call_script: str

    def __init__(self, 
                call_sid: str, 
                outbound_xml:str, 
                inbound_xml:str,
                controller):
        self.call_sid = call_sid
        self.outbound_xml = outbound_xml
        self.inbound_xml = inbound_xml
        self.history = []
        self.controller = controller
        call_dict[self.call_sid] = self

    async def hangup_on_time_limit(self):
        await asyncio.sleep(1200)
        self.controller.end_event.set()

    async def manage_call(self, inbound_or_outbound):
        match inbound_or_outbound:
            case "inbound": script_coro = self.inbound_coro()
            case "outbound": script_coro = self.outbound_coro()
        # timer = asyncio.ensure_future(self.hangup_on_time_limit())
        script = asyncio.ensure_future(script_coro)
        await self.controller.end_event.wait()
        # script.cancel()
        # timer.cancel()
        print(f'call {self.call_sid} completed')
        # call_dict.pop(self.call_sid)

    async def get_response(self):
        await self.controller.send_event.wait()
        response = []
        dn = []
        context = {}
        while not self.controller.outbound_track.empty():
            item = await self.controller.outbound_track.get()
            response.append(item["question"])
            dn.append(item["destination_name"])
            if item["destination_name"] == 'end':
                context = {}
            else:
                context = item['context']
        self.controller.send_event.clear()
        output = {"question": '\n'.join(response), "destination_name": '\n'.join(dn), "context": context }
        return output

    async def send(self, quote):
        print('sent', quote)
        await self.controller.participant_track.put(quote)



    async def say(self, quote, **kwargs):
        self.history.append(("SYSTEM", quote))
        await self.controller.say(quote=quote, **kwargs)

    async def ask(self, quote, **kwargs):
        self.history.append(("SYSTEM", quote))
        print('got to ask')
        reply =  await self.controller.ask(quote, **kwargs)
        self.history.append(("USER", reply))
        return reply
    
    def goodbye(self):
        self.controller.goodbye()
        
    async def outbound_coro(self):
        dialog = Dialog(conversation=self, 
                        treefile=self.outbound_xml, 
                        # openai_key=openai_key, org_id=org_id,
                        model="gpt-4", functions={'extract_zipcode': extract_zipcode, 
                                                       'extract_search_radius': extract_search_radius, 
                                                       'map_state': map_state,
                                                       'expanded_constraint_search': expanded_constraint_search,
                                                       'check_and_expand_search_if_null_response':check_and_expand_search_if_null_response,
                                                       'filter_hc_response': filter_hc_response,
                                                       'filter_sc_response': filter_sc_response,
                                                       'post_to_transplant_center_search': post_to_transplant_center_search,
                                                       'get_all_response': get_all_response,
                                                       'print_results': print_results,
                                                       'get_donor_type': get_donor_type,
                                                       'get_donor_count': get_donor_count,
                                                       'check_donor_type_required': check_donor_type_required,
                                                       'validate_user_age': validate_user_age,
                                                       'validate_candidate_height': validate_candidate_height,
                                                       'validate_candidate_weight': validate_candidate_weight,
                                                       'calculate_BMI': calculate_BMI,
                                                       'get_blood_type': get_blood_type,
                                                       'get_disease_cause': get_disease_cause,
                                                       'get_is_multiorgan_candidate': get_is_multiorgan_candidate,
                                                       'add_filters_and_post': add_filters_and_post
                                                       })
        await dialog.start()

    async def inbound_coro(self):
        dialog = Dialog(conversation=self, 
                        treefile=self.inbound_xml, 
                        # openai_key=openai_key, org_id=org_id,
                        model="gpt-4", functions={'extract_zipcode': extract_zipcode, 
                                                       'extract_search_radius': extract_search_radius, 
                                                       'map_state': map_state,
                                                       'expanded_constraint_search': expanded_constraint_search,
                                                       'check_and_expand_search_if_null_response':check_and_expand_search_if_null_response,
                                                       'filter_hc_response': filter_hc_response,
                                                       'filter_sc_response': filter_sc_response,
                                                       'post_to_transplant_center_search': post_to_transplant_center_search,
                                                       'get_all_response': get_all_response,
                                                       'print_results': print_results,
                                                       'get_donor_type': get_donor_type,
                                                       'get_donor_count': get_donor_count,
                                                       'check_donor_type_required': check_donor_type_required,
                                                       'validate_user_age': validate_user_age,
                                                       'validate_candidate_height': validate_candidate_height,
                                                       'validate_candidate_weight': validate_candidate_weight,
                                                       'calculate_BMI': calculate_BMI,
                                                       'get_blood_type': get_blood_type,
                                                       'get_disease_cause': get_disease_cause,
                                                       'get_is_multiorgan_candidate': get_is_multiorgan_candidate,
                                                       'add_filters_and_post': add_filters_and_post
                                                       })
        await dialog.start()





   

   


        
