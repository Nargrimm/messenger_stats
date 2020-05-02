import json
import os

from message import Message


class Conversation:
    def __init__(self, directory):
        self.directory = directory
        self.files = self.get_message_files()
        self.messages = self.get_messages()
        self.participants = self.get_all_participants()
        self.number_of_messages = self.get_number_of_messages()
        self.number_of_messages_per_participants = self.get_number_of_messages_per_participants()
        self.number_of_char_per_participants = self.get_number_of_char_per_participants()
        self.number_of_char = self.get_number_of_char()
        self.number_of_pics_per_participants = self.get_number_of_pics_per_participants()
        self.number_of_pics = self.get_number_of_pics()


    def get_message_files(self):
        files = []
        for r, d, f in os.walk(self.directory):
            for item in f:
                files.append(os.path.join(r, item))
        return files


    def get_current_participants(self):
        participants = set()
        for f in self.files:
            with open(f, 'r') as conv_file:
                data = json.load(conv_file)
                for p in data['participants']:
                    participants.add((p['name']).encode('iso-8859-1').decode('utf8'))
            return participants

    
    def get_all_participants(self):
        participants = self.get_current_participants()
        #former participants are not in the participants array we need to parse all the messages to find them
        for msg in self.messages:
            if msg.sender not in participants:
                participants.add(msg.sender)
        return participants


    def get_messages(self):
        messages = []
        for f in self.files:
            with open(f, 'r') as conv_file:
                data = json.load(conv_file)
                message_type = ['photos', 'files', 'sticker']
                for m in data['messages']:
                    try:
                        if 'content' in m:
                            content_type = 'message'
                            content = m['content'].encode('iso-8859-1').decode('utf8')
                        else:
                            for m_type in message_type:
                                if m_type in m:
                                    content_type = m_type
                                    content = ''
                                    if m_type == 'sticker':
                                        content += m['sticker']['uri'] + ';'
                                    else:
                                        for item in m[m_type]:  # We might have more than one file or one picture
                                            content += item['uri'] + ';'
                        messages.append(Message(m['sender_name'].encode('iso-8859-1').decode('utf8'), m['timestamp_ms'], m['type'], content_type, content))
                    except Exception as e:
                        print('Error while parsing message, Error: ', e)
                        print(json.dumps(m, indent=4))
                        return []
        return messages
    

    def get_number_of_messages(self):
        return len(self.messages)
    

    def get_number_of_messages_per_participants(self):
        participants_msg = dict()
        for p in self.participants:
            participants_msg[p] = 0
        for msg in self.messages:
            participants_msg[msg.sender] += 1
        return participants_msg


    def get_number_of_char_per_participants(self):
        participants_char = dict()
        for p in self.participants:
            participants_char[p] = 0
        for msg in self.messages:
            if msg.content_type != 'message' or msg.type != 'Generic':
                continue
            participants_char[msg.sender] += len(msg.content)
        return participants_char


    def get_number_of_char(self):
        res = 0
        for p, val in self.number_of_char_per_participants.items():
            res += val
        return res


    def get_number_of_pics_per_participants(self):
        participants_pics = dict()
        for p in self.participants:
            participants_pics[p] = 0
        for msg in self.messages:
            if msg.content_type != 'photos':
                continue
            participants_pics[msg.sender] += len(msg.content.split(';')) - 1 
        return participants_pics

    def get_number_of_pics(self):
        return sum(self.number_of_pics_per_participants.values())


#Return a dict with hour, weekday and year repartition
#We do this in a single iteration which is faster than calling the 3 functions 
    def get_message_time_repartition(self):
        msg_per_hour = dict()
        msg_per_weekday = {'0': 0, '1': 0, '2': 0, '3': 0, '4': 0, '5': 0, '6': 0}
        msg_per_year = dict()
        for msg in self.messages:
            hour = msg.get_message_hour()
            if hour not in msg_per_hour:
                msg_per_hour[hour] = 1
            else:
                msg_per_hour[hour] += 1
            msg_per_weekday[str(msg.get_message_weekday())] += 1
            year = msg.get_message_year()
            if year not in msg_per_year:
                msg_per_year[year] = 1
            else:
                msg_per_year[year] += 1
        weekdays = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        for i in range(0, 7):
            msg_per_weekday[weekdays[i]] = msg_per_weekday.pop(str(i))
        return {'hour': msg_per_hour, 'weekday': msg_per_weekday, 'year': msg_per_year}


    def get_number_of_messages_per_hour(self):
        msg_per_hour = dict()
        for msg in self.messages:
            hour = msg.get_message_hour()
            if hour not in msg_per_hour:
                msg_per_hour[hour] = 1
            else:
                msg_per_hour[hour] += 1
        return msg_per_hour


    def get_number_of_messages_per_weekday(self):
        msg_per_weekday = {'0': 0, '1': 0, '2': 0, '3': 0, '4': 0, '5': 0, '6': 0}
        for msg in self.messages:
            msg_per_weekday[str(msg.get_message_weekday())] += 1
        msg_per_weekday['Monday'] = msg_per_weekday.pop('0')
        msg_per_weekday['Tuesday'] = msg_per_weekday.pop('1')
        msg_per_weekday['Wednesday'] = msg_per_weekday.pop('2')
        msg_per_weekday['Thursday'] = msg_per_weekday.pop('3')
        msg_per_weekday['Friday'] = msg_per_weekday.pop('4')
        msg_per_weekday['Saturday'] = msg_per_weekday.pop('5')
        msg_per_weekday['Sunday'] = msg_per_weekday.pop('6')
        return msg_per_weekday
            

    def get_number_of_messages_per_year(self):
        msg_per_year = dict()
        for msg in self.messages:
            year = msg.get_message_year()
            if year not in msg_per_year:
                msg_per_year[year] = 1
            else:
                msg_per_year[year] += 1
        return msg_per_year


    def get_most_used_words(self, min_size, number_of_word):
        words_occurence = {}
        for msg in self.messages:
            msg_txt = msg.content
            words = [x.strip() for x in msg_txt.split(' ')]
            for word in words:
                word = word.lower()
                if len(word) == 0 or len(word) <= min_size:
                    continue
                words_occurence[word] = words_occurence.get(word, 0) + 1

        top_words = sorted(words_occurence.items(), key=operator.itemgetter(1), reverse=True)[:number_of_word]
        return top_words


    def get_message_per_day_as_2d_array_per_year(self):
        msg_per_year = {}
        for msg in self.messages:
            current_month = msg.get_message_month()
            current_day = msg.get_message_day()
            current_year = msg.get_message_year()
            if current_year not in msg_per_year:
                #array of 31 by 12 (day and months)
                msg_per_year[current_year] = [[0 for x in range(31)] for y in range(12)]
            #Minus -1 since array index are 0 based
            msg_per_year[current_year][current_month - 1][current_day - 1] += 1
        return msg_per_year


#This allow to create a single haetmap for all the messages but the result doesn't look that good
    def get_message_per_day(self):
        msg_per_day = {}
        for msg in self.messages:
            current_month = msg.get_message_month()
            current_day = msg.get_message_day()
            current_year = msg.get_message_year()
            current_month_year = str(current_month) + '-' + str(current_year)
            if current_month_year not in msg_per_day:
                #array of 31 by 12 (day and months)
                msg_per_day[current_month_year] = [0 for x in range(31)]
            #Minus -1 since array index are 0 based
            msg_per_day[current_month_year][current_day - 1] += 1
        return msg_per_day

    def get_message_per_day_as_dict(self):
        msg_day = {}
        for msg in self.messages:
            current_date = msg.get_message_y_m_d()
            msg_day[current_date] = msg_day.get(current_date, 0) + 1
        return msg_day


    def get_n_most_active_days(self, value):
        msg_day = self.get_message_per_day_as_dict()
        return sorted(msg_day.items(), key=operator.itemgetter(1), reverse=True)[:value]


    def get_specific_word_occurence_per_participant(self, name, word):
        res = 0
        for msg in self.messages:
            if msg.sender != name:
                continue
            if word in msg.content.lower():
                res += 1
        return res
