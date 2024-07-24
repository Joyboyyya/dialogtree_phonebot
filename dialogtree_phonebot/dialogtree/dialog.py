
from xml.etree import ElementTree as ET
from openai import OpenAI
import textwrap
import argparse
import sys
import requests
import json



class Branch:
    def __init__(self, node, parent):
        self.node = node
        self.parent = parent
        self.prompt, self.errorprompt, self.answerparse, *self.jumps = node
        self.jump_table = {}
        self.anonymous_jumps = []
        for j in self.jumps:
            if j.attrib.get('answer', None):
                for a in j.attrib['answer'].split(' '):
                    self.jump_table[a] = j
            elif j.attrib.get('accept', None):
                self.anonymous_jumps.append(j)

    
    async def execute(self):
        print(f"execute destination name: {self.node.attrib['destinationname']}")
        backprompt = self.parent.substitute(self.prompt)
        question = {"question":backprompt, "destination_name":self.node.attrib['destinationname'], "context":self.parent.context}
        response = await self.parent.conversation.ask(question) 
        answerparse_prompt = self.parent.substitute(
            self.answerparse, response=response, backprompt=backprompt
        )
        choice = await self.parent.complete(answerparse_prompt)
        while (pair:= await findmatch(choice, self.jump_table, self.anonymous_jumps, self.parent.functions, self.parent.context)) is None:
            error_prompt = self.parent.substitute(self.errorprompt, response=response, backprompt=backprompt)
            error_completion = await self.parent.complete(error_prompt)
            error_resolve_question = {"question":error_completion, "destination_name":self.node.attrib['destinationname'], "context":self.parent.context}
            response = await self.parent.conversation.ask(error_resolve_question)
            answerparse_prompt = self.parent.substitute(
                self.answerparse, response=response, backprompt=backprompt
            )
            choice = await self.parent.complete(answerparse_prompt)
        await self.parent.jump(pair[0], pair[1])



        


class State:
    def __init__(self, node, parent):
        self.node = node
        self.parent = parent
    
    async def execute(self):
        # await self.parent.conversation.say(self.parent.substitute(self.node, self.parent.context))
        await self.parent.conversation.say({"question":self.node.text, "destination_name":self.node.attrib['destinationname'], "context":self.parent.context})
        if 'nextdestination' in self.node.attrib:
            await self.parent.jump_destinations[self.node.attrib['nextdestination']].execute()
        else:
            await self.parent.jump_destinations['end'].execute()

class LLMQuestionDirect:
    def __init__(self, node, parent):
        self.node = node
        self.parent = parent
    
    async def execute(self):
        llm_input = self.parent.substitute(self.node, self.parent.context)
        await self.parent.conversation.say(await self.parent.complete(llm_input))
        if 'nextdestination' in self.node.attrib:
            await self.parent.jump_destinations[self.node.attrib['nextdestination']].execute()
        else:
            await self.parent.jump_destinations['end'].execute()

class LLMQuestionIndirect:
    def __init__(self, node, parent):
        self.node = node
        self.parent = parent
        self.userquestion, self.answerparse = node
    
    async def execute(self):
        backprompt = self.parent.substitute(self.userquestion)
        response = await self.parent.conversation.ask(backprompt)
        answerparse_prompt = self.parent.substitute(
            self.answerparse, response=response, backprompt=backprompt
        )
        await self.parent.conversation.say(await self.parent.complete(answerparse_prompt))
        if 'nextdestination' in self.node.attrib:
            await self.parent.jump_destinations[self.node.attrib['nextdestination']].execute()
        else:
            await self.parent.jump_destinations['end'].execute()

class Goodbye:
    def __init__(self, node, parent):
        self.node = node
        self.parent = parent
    
    async def execute(self):
        await self.parent.conversation.ask({"question":self.parent.substitute(self.node, self.parent.context), "destination_name":self.node.attrib['destinationname'] })
        self.parent.conversation.goodbye()


        
async def findmatch(choice, jump_table, anonymous_jumps, functions, context):
    for key, jump in jump_table.items():
        if key.lower() in choice.lower():
            return jump, key
    # for jump in anonymous_jumps:
    #     if (answer:= await functions[jump.attrib['accept']](choice, context)) is not None:
    #         return jump, answer
    # !!!!!!!!!!!!!!!!making changes to accept multiple functions within jump element!!!!!!!!!!!! 
    answer = []
    for jump in anonymous_jumps:
        accept_criteria = jump.attrib['accept'].split()
        
        for i in accept_criteria:
            response = await functions[i](choice, context)
            if response is None:
                answer.append(response)
                break
    
        if None not in answer:
            return jump, answer
        
        

from typing import Callable


class Dialog:
    def __init__(self,conversation:str, treefile:str, functions:dict[str, Callable], openai_key:str, org_id:str, model:str="llama3:70b", context={}):
        self.parse(ET.parse(treefile).getroot())
        self.functions=functions
        # self.client = OpenAI(api_key=openai_key, organization=org_id)
        self.model = model
        self.conversation=conversation
        self.context = context

        self.llama3_url = "https://rxinformatics-llm.ahc.umn.edu/api/chat"
        self.llama3_headers = {
            "Content-Type": "application/json"
        }

        
    
    def __init_subclass__(self, treefile:str, functions:dict[str, Callable], *args, **kwargs):
        self.parse(ET.parse(treefile).getroot())
        self.functions=functions

    
    def parse(self, root):
        self.root = root
        self.targets = [self.parse_target(tn) for tn in root]
        self.start_target = self.targets[0]
        self.jump_destinations = {}
        for t in self.targets:
            if 'destinationname' in t.node.attrib:
                self.jump_destinations[t.node.attrib['destinationname']] = t
    
    async def jump(self, node, answer=""):
        possible_destination = await self.execute_jump_function(node, answer)
        if 'nextdestination' in node.attrib:
            possible_destination = node.attrib['nextdestination']
        print('destination', possible_destination)
        if possible_destination not in self.jump_destinations:
            print(f'Invalid destination: {possible_destination}, restarting')
            await self.start()
        else:
            await self.jump_destinations[possible_destination].execute()
    
    async def execute_jump_function(self, node, answer):
        if 'function_name' in node.attrib:
            return await self.functions[node.attrib['function_name']](answer, self.context)
        elif (node.text is not None) and node.text.strip():
            ldict = {}
            exec("async def jfun(answer, context):\n" +
                        textwrap.indent(textwrap.dedent(node.text).strip(), prefix='    '), globals(), ldict)
            return await (ldict['jfun'](answer, self.context))


    
    def parse_target(self, target_node):
        match target_node.tag:
            case 'state': return State(target_node, self)
            case 'branch': return Branch(target_node, self)
            case 'llmquestion-indirect': return LLMQuestionIndirect(target_node, self)
            case 'llmquestion-direct': return LLMQuestionDirect(target_node, self)
            case 'goodbye': return Goodbye(target_node, self)

    def substitute(self, node, response=None, backprompt=None):
        start = node.text
        for item in node:
            if item.tag == 'response':
                start += response
            elif item.tag == 'backprompt':
                start += backprompt
            elif item.tag == 'context':
                start += self.context[item.attrib['key']]
            start += item.tail
        # print(f"destination name: {node.text}")
        return '\n'.join(s.strip() for s in start.split('\n') if s.strip)
        
    async def start(self):
        print('started')
        await self.start_target.execute()
    
    async def complete(self, prompt):
        #print('asked bot', prompt) #disable when not debugging
        # chat_completion = self.client.chat.completions.create(
        # messages=[
        #          {
        #              "role": "user",
        #              "content": "Don't be verbose. " + prompt,
        #          }
        #      ],
        #      model=self.model,
        # )
        # return chat_completion.choices[0].message.content
        llama3_payload = json.dumps({
        "model": "llama3:70b",
        "Stream": False,
        "messages": [
            {"role": "system", "content": "You are a helpful assistant"},
            {"role": "user", "content": "Don't be verbose. " + prompt}    
        ],
        "temperature": 0.1
        })

        response = requests.post(self.llama3_url, headers=self.llama3_headers, data=llama3_payload)

        if response.status_code == 200:
            data = response.json()
        else:
            print("Sorry, the model is not available..")

        return data['message']['content']
