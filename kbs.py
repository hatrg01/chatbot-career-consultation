import pandas as pd
import streamlit as st
from streamlit_chat import message
import numpy as np
import skfuzzy as fuzz
from skfuzzy import control as ctrl
# import requests

list_questions = pd.read_csv('.\\data\\ListQuestions.csv').to_numpy()
class_questions = pd.read_csv('.\\data\\ClassQuestions.csv').to_numpy()
description = pd.read_csv('.\\data\\DescriptionCharacters.csv').to_numpy()
careers = pd.read_csv('.\\data\\Careers.csv').to_numpy()

def fuzzy_logic(c, m):
    mean = ctrl.Antecedent(np.arange(0, 101, 1), 'mean')
    character = ctrl.Antecedent(np.arange(0, 101, 1), 'character')
    cmd = ctrl.Consequent(np.arange(0,11,1), 'cmd')

    character['verylow'] = fuzz.trapmf(character.universe, [0, 0, 10, 25])
    character['low'] = fuzz.trapmf(character.universe, [15, 25, 30, 45])
    character['medium'] = fuzz.trapmf(character.universe, [35, 45, 50, 65])
    character['high'] = fuzz.trapmf(character.universe, [50, 70, 75, 85])
    character['veryhigh'] = fuzz.trapmf(character.universe, [75, 85, 100, 100])

    mean['verylow'] = fuzz.trapmf(mean.universe, [0, 0, 15, 25])
    mean['low'] = fuzz.trapmf(mean.universe, [15, 25, 30, 40])
    mean['medium'] = fuzz.trapmf(mean.universe, [30, 40, 45, 55])
    mean['high'] = fuzz.trapmf(mean.universe, [45, 55, 65, 75])
    mean['veryhigh'] = fuzz.trapmf(mean.universe, [60, 75, 100, 100])

    cmd['no'] = fuzz.trapmf(cmd.universe, [0, 0, 3, 6])
    cmd['yes'] = fuzz.trapmf(cmd.universe, [4, 7, 10, 10])

    rule1 = ctrl.Rule(
        character['high'] | 
        character['veryhigh'] | 
        mean['verylow'] | 
        mean['low'] | 
        (mean['medium'] & character['medium']) |
        (mean['high'] & character['medium']), cmd['yes'])
    rule2 = ctrl.Rule(
        (mean['medium'] & character['verylow']) |
        (mean['medium'] & character['low']) |
        (mean['high'] & character['verylow']) |  
        (mean['high'] & character['low']) |
        (mean['veryhigh'] & character['medium']) |
        (mean['veryhigh'] & character['verylow']) |
        (mean['veryhigh'] & character['low']), cmd['no'])

    cmd_ctrl = ctrl.ControlSystem([rule1, rule2])
    cmd_op = ctrl.ControlSystemSimulation(cmd_ctrl)

    cmd_op.input['mean'] = m
    cmd_op.input['character'] = c

    cmd_op.compute()
    if cmd_op.output['cmd'] < 4:
        return 0
    return 1

st.set_page_config(
    page_title="Career Consultant System",
    # page_icon=":robot:"
)

st.header("Chatbot Tư vấn nghề nghiệp")
# st.write("*Gõ OK để bắt đầu!*")

if 'generated' not in st.session_state:
    st.session_state['generated'] = []

if 'past' not in st.session_state:
    st.session_state['past'] = []

if 'questions' not in st.session_state:
    st.session_state['questions'] = []

if 'a' not in st.session_state:
    st.session_state['a'] = []

if 'b' not in st.session_state:
    st.session_state['b'] = ['R','I','A','S','E','C']

if 'c' not in st.session_state:
    st.session_state['c'] = []

if 'index' not in st.session_state:
    st.session_state['index'] = 0

if 'count' not in st.session_state:
    st.session_state['count'] = 0

if 'max' not in st.session_state:
    st.session_state['max'] = [0, 0]

if 'ok' not in st.session_state:
    st.session_state['ok'] = 0

# if 'n' not in st.session_state:
#     st.session_state['n'] = [6]

# if 'choose' not in st.session_state:
#     st.session_state['choose'] = []
# if len(st.session_state['choose']) <30:
#     for i in range(30):
#         st.session_state['choose'].append(1)

# load questions
if len(st.session_state.questions) < 5 * len(st.session_state.b):
    for i in range(5):
        # st.session_state.questions.append([])
        for j in range(6):
            st.session_state.questions.append(list_questions[class_questions[i, j + 1] - 1, 1])
    # st.session_state.questions

def get_text():
    input_text = st.text_input("You: ","Hi!", key="input")
    return str(input_text)

def comp(a): 
    m = 0
    for i in a:
        m += int(i)
    m /= len(a)
    for i in range(len(a)):
        if fuzzy_logic(float(a[i]), m) == 0:
            st.session_state.b.pop(i - st.session_state['count'])
            for j in range(5):
                st.session_state.questions.pop(i + j * len(st.session_state.b) - st.session_state['count'])
                if st.session_state['index'] > i + j * len(st.session_state.b) - st.session_state['count']:
                    st.session_state['index'] -= 1

            st.session_state['count'] += 1
    # if len(st.session_state.b) == 1:
    #     st.session_state.index = 30
    
def loadCareer(b):
    for i in range(len(careers)):
        if careers[i, 2] == b:
            st.session_state.c.append([])
            for j in careers[i]:
                st.session_state.c[len(st.session_state.c) - 1].append(j)


def generate(ip, index):
    

    if ip == 'Hi!':
        return 'Trả lời các câu hỏi sau bằng cách cho điểm từ 0 - 100! Gõ OK để bắt đầu!'

    if index == 0 and ip.lower() != 'ok' and st.session_state.ok == 0:
        return 'Gõ OK để bắt đầu!'

    
    if ip.lower() == 'next':
        st.session_state.index = 31
        index = 30
        return str(index - 29) + '. ' + st.session_state.c[index - 30][1]

    if st.session_state.ok and not(ip.isdigit()):
        return 'Nhập số từ 0 - 100'

    if st.session_state.ok and (int(ip) < 0 or int(ip) > 100):
        return 'Nhập số từ 0 - 100'

    # if ip.isdigit() and (int(ip) >= 0 and int(ip) <= 100):
        

    if st.session_state['index'] >= len(st.session_state.questions) and st.session_state['index'] < 29:
        return 'Không thể xác định kiểu tính cách! Hãy tìm hiểu thêm về bản thân'

    if index - 30 >= len(st.session_state.c):
        st.session_state['index'] += 1
        if int(ip) > st.session_state.max[0]:
            st.session_state.max[0] = int(ip)
            st.session_state.max[1] = index - 30
        return 'Bạn phù hợp với nhóm ngành ' + st.session_state.c[st.session_state.max[1]][3]


    if index > 30 and index - 30 < len(st.session_state.c):
        st.session_state['index'] += 1
        if int(ip) > st.session_state.max[0]:
            st.session_state.max[0] = int(ip)
            st.session_state.max[1] = index - 30
        return str(index - 29) + '. ' + st.session_state.c[index - 30][1]


    
    if len(st.session_state.questions) == 5:
        st.session_state['index'] += 1
        loadCareer(st.session_state.b[0])
        for i in range(6):
            if st.session_state.b[0] == description[i, 0]:
                return description[i, 1] + ' Gõ NEXT để tiếp tục!'

    if ip.lower() == 'ok':
        st.session_state['index'] += 1
        st.session_state.ok = 1
        return 'Nhóm câu hỏi về Tính cách: 1. ' + st.session_state.questions[index]

    i = (index + 1) // len(st.session_state.b)
    j = (index + 1) % len(st.session_state.b)

    if j == 1:
        st.session_state['index'] += 1
        return 'Nhóm câu hỏi về ' + class_questions[i,0] + ': ' + str(j) + '. ' + st.session_state.questions[index]
    
    if j == 0:
        j += len(st.session_state.b)
        i -= 1
    st.session_state['index'] += 1
    return str(j) + '. ' + st.session_state.questions[index]
    
    

user_input = get_text()
# num = len(st.session_state.n)


if user_input:

    st.session_state.past.append(user_input)

    if st.session_state.index > 0 and user_input.isdigit() and int(user_input) >= 0 and int(user_input) <= 100:
        st.session_state.a.append(user_input)

    if len(st.session_state.a) == len(st.session_state.b) and len(st.session_state.b) > 1:
        comp(st.session_state.a)
        # st.session_state.a
        st.session_state.a = []
        st.session_state['count'] = 0

    # if len(st.session_state.b) == 1:
    #     st.session_state.index = 30
            
    # st.session_state['a']
    # st.session_state['index']

    st.session_state.generated.append(generate(user_input, st.session_state['index']))
    
    # st.session_state.flag.append(len(st.session_state['generated'])%2)


# st.session_state['a']


# st.session_state.questions
# st.session_state.a

if st.session_state['generated']:
    for i in range(len(st.session_state['generated'])-1, -1, -1):
        # if i % 7 ==0 :
        #     message(st.session_state['generated'][i], key=str(i))
        #     continue
        # st.session_state['choose'][i+1]=0
        
        message(st.session_state['generated'][i], key=str(i))
        message(st.session_state['past'][i], key=str(i)+ '_user', is_user=True)
    # message(st.session_state['generated'][0], key=str(0))


# message(user_input, key='0_user', is_user=True)
