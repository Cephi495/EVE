""" Things I still want want to add:
TODO: base language metrics off specific dictionary **

TODO: spell check / suggestions
TODO: grammar check / suggestions
TODO: take one response and separate it into sub-responses based on punctuation, respond individually
TODO: implement csv functionality
TODO: create yes, no command instances

SOURCES:

https://en.wikipedia.org/wiki/Auxiliary_verb

"""

import os
import re
import time
from datetime import datetime
import pytz

# from spellchecker import SpellChecker
# checker = SpellChecker()

verbose = True

#   ----    ----    knowledge base      ----    ----
#   Interrogatives
interrogatives = ['who', 'whose', 'where', 'when', 'why', 'how', 'which']

#   forms of 'what'
what_types = ['what', 'whats', "what's"]

#   Auxiliary verbs
aux_verbs = ['be', 'can', 'could', 'dare', 'do', 'did', 'does', 'have', 'has', 'had', 'may', 'might', 'must', 'need', 'ought',
             'should', 'shall', 'will', 'would', 'is', 'are', 'was', 'were', 'so', 'if']

#   Aux verb singular response
auxv_single_resp = ['be', 'am', 'am', 'was', 'was', 'can', 'could', 'do', 'did', 'do', 'have', 'had', 'have', 'may',
                    'might', 'must', 'shall', 'should', 'will', 'would', ]

#   Attributes
negative_atr = ['no', 'nor', 'not', 'nah', 'nope', 'never', 'dont', "don't", 'doesnt', "doesn't", 'cant', "can't",
                'havent', "haven't", 'wasnt', "wasn't", 'hasnt', "hasn't", 'couldnt', "could't", 'wouldnt', "wouldn't",
                'shouldnt', "shouldn't", 'didnt', "didn't", ]
positive_atr = ['yes', 'or', 'is', 'yah', 'yep', 'ever', 'do', 'does', 'can', 'have', 'was', 'has', 'could', 'would',
                'should', 'will', ]

#   Possessives
determiners = ['my', 'your', 'yours', 'our', 'ours', 'him', 'his', 'her', 'hers', 'its', 'their', 'theirs', 'whose']
ordinals = ['first', 'second', 'third', 'next', 'last']

#   Subjects
subjects = ['i', 'you', 'he', 'she', 'we', 'they', 'them', 'everyone', 'everybody', 'these', 'that', 'this', 'it']

#   Greetings, TODO: add more
greetings = ['hi', 'hello', 'morning', 'good morning', 'afternoon', 'good afternoon', 'evening', 'good evening', 'night', 'good night']

#   Positive response to call
pos_resp = ['Hello', 'Hi', 'Good morning', 'Morning', 'Good afternoon', 'Afternoon', 'Good evening', 'Evening',
            'Good night', 'Night']

#   Negative response to call
neg_resp = []

#   Punctuation
punc = ['.', '!', '?']
#   ----    ----    end knowledge base  ----    ----

#   ----    ----    response building   ----    ----
#   the final compilation of responses that will be passed to client
response = []

#   used by response_handler() to deposit responses
responding = []

#   for compiling complex responses that will be compiled in responding[]
response_1 = []

#   used as a determiner for inquiry of time recall
time_recall = []

string_subject_pos = []

string_aux_verb_pos = []

#   handle multiple interrogations at once
string_inquiry_pos = []

#   handle greeting interrogations
string_greeting_pos = []

''''''
#   index repository for found interrogators
# found_KEY = []
''''''
#   storing interrogators that have been analyzed already
previous_KEY = []

pytz_timezones = []

#   ----    ----    end response building   ----    ----


def chatbot(data, S):
    response.clear()
    if S:
        print("Received: " + data)

    #   Add client msg to log
    f = open('chat_log.txt', 'a+')
    f.write(str('\n ' + data)), f.close()

    #   separate client message into individual sentences so response_handler() can handle one at a time
    data_modified = re.split(r'(?<!\w\.\w.)(?<![A-Z][a-z]\.)(?<=[.?!])\s', data)

    # print("main_string modified: " + data_modified)
    for sentence in data_modified:  # TODO: Handle all-caps words as well
        response.append(''.join(response_handler(sentence.lower())))

    #   Add EVE response msg to log
    f = open('chat_log.txt', 'a+')
    f.write(str('\n *' + ''.join(response))), f.close()

    #   get the last line of the chat_log
    #   this is not necessary
    f = open('chat_log.txt', 'rb')
    f.seek(-2, os.SEEK_END)
    while f.read(1) != b'\n':
        f.seek(-2, os.SEEK_CUR)
    final_response = f.readline().decode()
    f.close()

    if S:
        return str(final_response.replace(' *', ''))
    else:
        print(str(final_response.replace(' *', '')))


def response_handler(main_string):
    clear_main_lists()
    main_string_no_dup = []
    string_detected_region = ''
    string_detected_country = ''
    polarity = 0
    for item in pytz.all_timezones:
        pytz_timezones.append(item)
    if verbose:
        print(pytz_timezones)
    for word in main_string.split():
        if main_string.count(word) >= 1 and (word not in main_string_no_dup):
            main_string_no_dup.append(word)
    main_string_no_dup = ' '.join(main_string_no_dup)
    main_string_no_punc = main_string_no_dup.replace('.', '').replace('!', '').replace('?', '')  # TODO: only remove punctuation, ignore decimals
    main_string_no_punc_list = main_string_no_punc.split()
    # data_no_punc_reversed = ' '.join(main_string.split()[::-1])

    try:
        #   filter out tool cmd
        if not main_string.split()[0].startswith('!!'):
            # check for punctuation
            if main_string.endswith(tuple(punc)):
                #   breaking down the message
                for word in main_string_no_punc_list:
                    if word in interrogatives:
                        string_inquiry_pos.append(main_string_no_punc_list.index(word))
                    if word in what_types:
                        string_inquiry_pos.append(main_string_no_punc_list.index(word))
                    if word in aux_verbs:
                        string_aux_verb_pos.append(main_string_no_punc_list.index(word))
                    if word in subjects:
                        string_subject_pos.append(main_string_no_punc_list.index(word))
                    if word in greetings:
                        string_greeting_pos.append(main_string_no_punc_list.index(word))
                    if word in pytz_timezones:
                        pass
                    #   check sentence polarity
                    if any(p in word for p in negative_atr):
                        polarity += 1
                if (polarity % 2) == 0:
                    positive_pol = True
                else:
                    positive_pol = False

                for timezone in pytz_timezones:
                    for word in main_string_no_punc.split():
                        if word == timezone.lower():
                            string_detected_country = timezone.split('/')[0]
                        if '/' in timezone and word == timezone.split('/')[0].lower():    # and not string_detected_country:
                            string_detected_country = timezone.split('/')[0]
                        if '/' in timezone and word == timezone.split('/')[1].lower() and string_detected_country:    # and not string_detected_region:
                            string_detected_region = '/' + timezone.split('/')[1]
                        else:
                            pass

                if verbose:
                    print('    › no_punc: ' + str(main_string_no_punc.split()) +
                          '\n    › inquiry_pos: ' + str(string_inquiry_pos) +
                          '\n    › aux_pos: ' + str(string_aux_verb_pos) +
                          '\n    › subject_pos: ' + str(string_subject_pos) +
                          '\n    › greeting_pos: ' + str(string_greeting_pos) +
                          '\n    › timezone_pos: ' + str(string_detected_country) + str(string_detected_region))

                #   'clear log': retrieval method
                if positive_pol and 'clear log.' in main_string or 'clear log!' in main_string:
                    if punc[2] not in main_string[-1]:
                        open('chat_log.txt', 'w+').close()
                        responding.append("Log cleared! ")
                    else:
                        pass

                #   ----    building complex responses      ----
                #   if ends with (?)

                if main_string[-1] == punc[2]:
                    inquiry_quenched = 0
                    greeting_quenched = 0

                    '''
                    if 'created you' in data_no_punc:  # TODO: in development...
                        time_recall.append(data_no_punc)
                    '''

                    try:
                        #   greeting retrieval method, for single-word-strings  **
                        for call in greetings:
                            if main_string_no_punc == call:
                                responding.append(pos_resp[greetings.index(call)] + ". ")
                                greeting_quenched += 1

                        #   starts or ends with:
                        if main_string_no_punc_list[0] in interrogatives or \
                                main_string_no_punc_list[0] in aux_verbs or \
                                main_string_no_punc_list[0] in what_types or \
                                main_string_no_punc_list[-1] in interrogatives or \
                                main_string_no_punc_list[-1] in aux_verbs or \
                                main_string_no_punc_list[-1] in what_types:
                            # starts with "what"
                            if main_string_no_punc_list[string_inquiry_pos[0]] in what_types:
                                #   'you' detected...
                                if string_subject_pos and main_string_no_punc_list[string_subject_pos[0]] == subjects[1]:
                                    if any(word in main_string_no_punc for word in aux_verbs):  # TODO fix this logic!
                                        for aux in aux_verbs:
                                            #   "how are you" or "you are how"
                                            if (aux + ' ' + subjects[1] in main_string_no_punc_list[0] + ' ' + main_string_no_punc_list[1]) or (
                                                    subjects[1] + ' ' + aux in main_string_no_punc_list[0] + ' ' + main_string_no_punc_list[1]):
                                                #   respond with proper aux verb
                                                x = aux_verbs.index(aux)
                                                response_1.append("I " + auxv_single_resp[x])
                                                #   respond to specific interrogation
                                                for i in main_string_no_punc_list:
                                                    if i in interrogatives:
                                                        if i != 'are':
                                                            b = interrogatives.index(i)
                                                            response_1.append(get_personal_state(b))
                                                #   append built response to response cue
                                                responding.append(' '.join(response_1))
                                                response_1.clear()
                                                inquiry_quenched += 1

                                            #   "are you okay" or "you are okay"
                                            elif (aux + ' ' + subjects[1] in main_string_no_punc_list[0] + ' ' + main_string_no_punc_list[1]) or (
                                                    subjects[1] + ' ' + aux in main_string_no_punc_list[0] + ' ' + main_string_no_punc_list[1]):
                                                #   respond with proper aux verb
                                                x = aux_verbs.index(aux)
                                                response_1.append("I " + auxv_single_resp[x])
                                                #   respond to specific interrogation
                                                b = interrogatives.index(main_string_no_punc_list[0])
                                                response_1.append(get_personal_state(b))
                                                #   append built response to response cue
                                                responding.append(' '.join(response_1))
                                                response_1.clear()
                                                inquiry_quenched += 1

                                #   if what_types comes before 'time'
                                # TODO: specify time zone
                                if string_inquiry_pos[0] < main_string_no_punc_list.index('time') or \
                                        main_string_no_punc_list.index('time') < string_aux_verb_pos[0]:
                                    if string_detected_country and not string_detected_region:
                                        responding.append('The time in ' + string_detected_country + ' is: ' +
                                                          str(datetime.now(pytz.timezone(string_detected_country)).strftime("%T, %Z")) + '. ')
                                    elif string_detected_country and string_detected_region:
                                        detected_time_zone = str(string_detected_country + string_detected_region)
                                        responding.append('The time in ' + detected_time_zone + ' is: ' +
                                                          str(datetime.now(pytz.timezone(detected_time_zone)).strftime("%T, %Z")) + '. ')
                                    else:
                                        responding.append('The time is: ' + str(time.strftime("%T, %Z", time.localtime())) + '. ')
                                    inquiry_quenched += 1
                            #   starts with "who"
                            if main_string_no_punc_list[0] == interrogatives[0]:
                                pass
                            #   starts with "whose"
                            if main_string_no_punc_list[0] == interrogatives[1]:
                                pass
                            #   starts with "where"
                            if main_string_no_punc_list[0] == interrogatives[3]:
                                pass
                            #   starts with "when"
                            if main_string_no_punc_list[0] == interrogatives[4]:
                                pass
                            #   starts with "why"
                            if main_string_no_punc_list[0] == interrogatives[5]:
                                pass
                    except Exception as e:
                        raise e
                    if inquiry_quenched == len(string_inquiry_pos) and greeting_quenched == len(string_greeting_pos):
                        pass
                    else:
                        responding.append('Please elaborate on: [' + main_string + ']')
                #   if ends with (!)
                elif main_string[-1] == punc[1]:
                    #   some more retrieval methods for greetings
                    for call in greetings:
                        if call == main_string_no_punc:
                            i = greetings.index(call)
                            responding.append(pos_resp[i] + "! ")

                #   if ends with (.)
                elif main_string[-1] == punc[0]:
                    #   some more retrieval methods for greetings
                    for call in greetings:
                        if call == main_string_no_punc:
                            i = greetings.index(call)
                            responding.append(pos_resp[i] + ". ")

                else:
                    responding.append("Error in message: [" + main_string + "]")
            else:
                responding.append("Punctuation required. ")

        #   check for tool requests
        else:
            if tool_handler(main_string) is not None:
                responding.append(tool_handler(main_string))
                print(tool_handler(main_string))
            else:
                responding.append("No tools requested. ")
                print("No tools requested. ")
    except Exception as e:
        raise e
    #   if no response could be formed
    if responding:
        return responding
    else:
        return "No response."


def clear_main_lists():
    responding.clear()
    response_1.clear()
    time_recall.clear()
    previous_KEY.clear()
    string_subject_pos.clear()
    string_aux_verb_pos.clear()
    string_inquiry_pos.clear()
    string_greeting_pos.clear()
    pytz_timezones.clear()


def get_personal_state(interrogation):
    personal_intg_resp = ['wpaai. ', '(interrogation detected). ', 'a chat bot. ']
    if interrogation < 7:
        return personal_intg_resp[interrogation]
    #   how
    if interrogation == 7:
        return "good. "
    else:
        return "(interrogation detected). "


def tool_handler(data):
    if data == "!!music":
        return str(data + ". ")
    else:
        return None
