#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File    :   planner.py
@Time    :   2023/05/16 09:12:11
@Author  :   Hu Bin 
@Version :   1.0
@Desc    :   None
'''
print("planner1")

import os, requests
from typing import Any
from mediator import *
from utils import global_param


from abc import ABC, abstractmethod

class Base_Planner(ABC):
    """The base class for Planner."""

    def __init__(self):
        super().__init__()
        self.dialogue_system = ''                  
        self.dialogue_user = ''
        self.dialogue_logger = ''         
        self.show_dialogue = False
        self.llm_model = None
        self.llm_url = None
    def reset(self, show=False):
        self.dialogue_user = ''
        self.dialogue_logger = ''
        self.show_dialogue = show

    ## initial prompt, write in 'prompt/task_info.json
    def initial_planning(self, decription, example):
        print(decription,example)
        if self.llm_model is None:
            assert "no select Large Language Model"
        prompts = decription + example
        self.dialogue_system += decription + "\n"
        self.dialogue_system += example + "\n"
        print("prompts",prompts)

        ## set system part
        server_error_cnt = 0
        while server_error_cnt<10:
            try:
                url = self.llm_url
                print("url",url,"51")
                headers = {'Content-Type': 'application/json'}
                
                data = {'model': self.llm_model, "messages":[{"role": "system", "content": prompts}]}
                response = requests.post(url, headers=headers, json=data)
                print("56response",response)
                
                if response.status_code == 200:
                    result = response.json()                    
                    server_flag = 1
                                
                   
                if server_flag:
                    break
                    
            except Exception as e:
                server_error_cnt += 1
                print(e)    

    def query_codex(self, prompt_text):
        print("prompt_text",prompt_text)
        server_flag = 0
        server_error_cnt = 0
        response = ''
        while server_error_cnt<10:
            try:
                #response =  openai.Completion.create(prompt_text)
                url = self.llm_url
                headers = {'Content-Type': 'application/json'}
                
                # prompt_text
                print("url",url)
                data = {'model': self.llm_model, "messages":[{"role": "user", "content": prompt_text }]}
                response = requests.post(url, headers=headers, json=data)
                print(response)
                
                
                

                if response.status_code == 200:
                    result = response.json()                    
                    server_flag = 1
                                
                   
                if server_flag:
                    break
                    
            except Exception as e:
                server_error_cnt += 1
                print(e)
        if result is None:
            return
        else:
            return result['messages'][-1][-1] 

    def check_plan_isValid(self, plan):
        if "{" in plan and "}" in plan:
            return True
        else:
            return False
        
    def step_planning(self, text):
        print("text",text)
        ## seed for LLM and get feedback
        plan = self.query_codex(text)
        if plan is not None:
            ## check Valid, llm may give wrong answer
            while not self.check_plan_isValid(plan):
                print("%s is illegal Plan! Replan ...\n" %plan)
                plan = self.query_codex(text)
        return plan

    @abstractmethod
    def forward(self):
        pass

class SimpleDoorKey_Planner(Base_Planner):
    def __init__(self, seed=0):
        super().__init__()
        print("1")
        self.mediator = SimpleDoorKey_Mediator()
        if seed %2 ==0:
            self.llm_model = "gpt-4"
            self.llm_url = 'https://api.openai.com/v1/chat/completions'
        else:
            self.llm_model = "gpt-4"
            self.llm_url = 'https://api.openai.com/v1/chat/completions'

    def __call__(self, input):
        return self.forward(input)
    
    def reset(self, show=False):
        self.dialogue_user = ''
        self.dialogue_logger = ''
        self.show_dialogue = show
        ## reset dialogue
        if self.show_dialogue:
            print(self.dialogue_system)

       
    def forward(self, obs):
        text = self.mediator.RL2LLM(obs)
        # print(text)
        plan = self.step_planning(text)
        
        self.dialogue_logger += text
        self.dialogue_logger += plan
        self.dialogue_user = text +"\n"
        self.dialogue_user += plan
        if self.show_dialogue:
            print(self.dialogue_user)
        skill = self.mediator.LLM2RL(plan)
        return skill
   
    
class KeyInBox_Planner(Base_Planner):
    def __init__(self,seed=0):
        super().__init__()
        self.mediator = KeyInBox_Mediator()
        if seed %2 == 0:
            self.llm_model = "gpt-4"
            self.llm_url = 'https://api.openai.com/v1/chat/completions'
        else:
            self.llm_model = "gpt-4"
            self.llm_url = 'https://api.openai.com/v1/chat/completions'

    def __call__(self, input):
        return self.forward(input)
    
    def reset(self, show=False):
        self.dialogue_user = ''
        self.dialogue_logger = ''
        self.show_dialogue = show
        ## reset dialogue
        if self.show_dialogue:
            print(self.dialogue_system)


    def forward(self, obs):
        text = self.mediator.RL2LLM(obs)
        # print(text)
        plan = self.step_planning(text)

        self.dialogue_logger += text
        self.dialogue_logger += plan
        self.dialogue_user = text +"\n"
        self.dialogue_user += plan
        if self.show_dialogue:
            print(self.dialogue_user)
        skill = self.mediator.LLM2RL(plan)
        return skill


class RandomBoxKey_Planner(Base_Planner):
    def __init__(self, seed=0):
        super().__init__()
        self.mediator = RandomBoxKey_Mediator()
        if seed %2 == 0:
            self.llm_model = "gpt-4"
            self.llm_url = 'https://api.openai.com/v1/chat/completions'
        else:
            self.llm_model = "gpt-4"
            self.llm_url = 'https://api.openai.com/v1/chat/completions'    
    def __call__(self, input):
        return self.forward(input)
    
    def reset(self, show=False):
        self.dialogue_user = ''
        self.dialogue_logger = ''
        self.show_dialogue = show
        ## reset dialogue
        if self.show_dialogue:
            print(self.dialogue_system)
     
    def forward(self, obs):
        text = self.mediator.RL2LLM(obs)
        # print(text)
        plan = self.step_planning(text)
        
        self.dialogue_logger += text
        self.dialogue_logger += plan
        self.dialogue_user = text +"\n"
        self.dialogue_user += plan
        if self.show_dialogue:
            print(self.dialogue_user)
        skill = self.mediator.LLM2RL(plan)
        return skill
   
class ColoredDoorKey_Planner(Base_Planner):
    def __init__(self,seed=0):
        super().__init__()
        self.mediator = ColoredDoorKey_Mediator()
        if seed %2 == 0:
            self.llm_model = "gpt-4"
            self.llm_url = 'https://api.openai.com/v1/chat/completions'
        else:
            self.llm_model = "gpt-4"
            self.llm_url = 'https://api.openai.com/v1/chat/completions'


    def __call__(self, input):
        return self.forward(input)
    
    def reset(self, show=False):
        self.dialogue_user = ''
        self.dialogue_logger = ''
        self.show_dialogue = show
        ## reset dialogue
        if self.show_dialogue:
            print(self.dialogue_system)
    

    def forward(self, obs):
        text = self.mediator.RL2LLM(obs)
        # print(text)
        plan = self.step_planning(text)

        self.dialogue_logger += text
        self.dialogue_logger += plan
        self.dialogue_user = text +"\n"
        self.dialogue_user += plan
        if self.show_dialogue:
            print(self.dialogue_user)
        skill = self.mediator.LLM2RL(plan)
        return skill
   

def Planner(task,seed=0):
    if task.lower() == "simpledoorkey":
        planner = SimpleDoorKey_Planner(seed)
    elif task.lower() == "keyinbox":
        planner = KeyInBox_Planner(seed)
    elif task.lower() == "randomboxkey":
        planner = RandomBoxKey_Planner(seed)
    elif task.lower() == "coloreddoorkey":
        planner = ColoredDoorKey_Planner(seed)
    return planner
