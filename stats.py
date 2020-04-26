import argparse
import datetime
import json
import operator
import os
import sys
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from colour import Color
from PIL import Image


class Message:
    #if the content type is a pictue the content will be the path to this pic
    def __init__(self, sender, timestamp_ms, messenger_type, content_type, content):
        self.sender = sender
        self.timestamp_ms = timestamp_ms
        self.type = messenger_type
        self.content_type = content_type
        self.content = content

    def get_message_hour(self):
        return datetime.datetime.fromtimestamp(int(self.timestamp_ms)/1000.0).hour


    def get_message_weekday(self):
        return datetime.datetime.fromtimestamp(int(self.timestamp_ms)/1000.0).weekday()
    
    def get_message_day(self):
        return datetime.datetime.fromtimestamp(int(self.timestamp_ms)/1000.0).day

    def get_message_month(self):
        return datetime.datetime.fromtimestamp(int(self.timestamp_ms)/1000.0).month

    def get_message_year(self):
        return datetime.datetime.fromtimestamp(int(self.timestamp_ms)/1000.0).year

    def get_message_y_m_d(self):
        return datetime.datetime.fromtimestamp(int(self.timestamp_ms)/1000.0).strftime('%Y-%m-%d')

class Conversation:
    def __init__(self, directory):
        self.directory = directory
        self.files = self.get_message_files()
        self.messages = self.get_messages()
        self.participants = self.get_all_participants()
        self.number_of_messages = self.get_number_of_messages()
        self.number_of_messages_per_participants = self.get_number_of_messages_per_participants()
        self.number_of_char_per_participants = self.get_number_of_char_per_participants()
        self.number_of_photos_per_participants = self.get_number_of_photos_per_participants()

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
                    participants.add((p['name']).encode("iso-8859-1").decode("utf8"))
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
                            content = m['content']
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
                        messages.append(Message(m['sender_name'].encode("iso-8859-1").decode("utf8"), m['timestamp_ms'], m['type'], content_type, content))
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


    def get_number_of_photos_per_participants(self):
        participants_pics = dict()
        for p in self.participants:
            participants_pics[p] = 0
        for msg in self.messages:
            if msg.content_type != 'photos':
                continue
            participants_pics[msg.sender] += len(msg.content.split(';')) - 1 
        return participants_pics

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
            msg_txt = msg.content.encode("iso-8859-1").decode("utf8")
            words = [x.strip() for x in msg_txt.split(' ')]
            for word in words:
                word = word.lower()
                if len(word) == 0 or len(word) <= min_size:
                    continue
                words_occurence[word] = words_occurence.get(word, 0) + 1

        top_words = sorted(words_occurence.items(), key=operator.itemgetter(1), reverse=True)[:number_of_word]
        return top_words


    def get_most_active_days(self):
        msg_day = {}
        for msg in self.messages:
            current_date = msg.get_message_y_m_d()
            msg_day[current_date] = msg_day.get(current_date, 0) + 1
        return msg_day

    def get_n_most_active_days(self, value):
        msg_day = self.get_most_active_days()
        return sorted(msg_day.items(), key=operator.itemgetter(1), reverse=True)[:value]

            


def print_dict_ordered_reverse(d):
    print(sorted(d.items(), key=operator.itemgetter(1), reverse=True))


def create_bar_plot_from_list(l, x_name, y_name, title, name):
    x = []
    y = []
    for item in l:
        x.append(item[0])
        y.append(item[1])
    create_bar_plot(x, x_name, y, y_name, title, name)


def create_bar_plot(x, x_name, y, y_name, title, name):
    plt.figure()
    df = pd.DataFrame(list(zip(x, y)), columns=(x_name, y_name))
    plot = df.plot.bar(x=x_name, y=y_name, color='#3377ff', figsize=(16,11))
    plot.set_xticklabels(plot.get_xticklabels(), rotation=45, horizontalalignment='right')
    plt.title(title)
    plot.get_figure().savefig(name)


def create_pie_chart_from_list(l, title, name):
    values = []
    labels = []
    for item in l:
        labels.append(item[0])
        values.append(item[1])
    create_pie_chart(values, labels, title, name)


def make_autopct(values):
    def my_autopct(pct):
        total = sum(values)
        val = int(round(pct * total / 100.0))
        s = "{:.2f}%\n({})".format(pct, val)
        return s
    return my_autopct


def create_pie_chart(values, labels, title, name):
    plt.figure(figsize=(16,11), dpi=300)
    max_slices = 7
    #plt.rcParams.update({'font.size': 8})
    df = pd.DataFrame({'values': values}, index=labels)

    if len(values) > max_slices + 1 :
        df2 = df[:max_slices].copy()
        custom_label = ""
        total = df.values.sum()
        for item in df[max_slices:].itertuples():
            percent = item.values / total * 100.0
            custom_label +=  '\n  {}: {:.2f}% ({})'.format(item.Index, percent, item.values)
        new_row = pd.DataFrame({'values' : [df['values'][max_slices:].sum()]}, index=['Other:' + custom_label])
        df = pd.concat([df2, new_row])

    colors = list(Color("#3377ff").range_to(Color("#e6eeff"),len(df.values)))
    colors = [color.rgb for color in colors]
    plot = df.plot.pie(y='values', autopct=make_autopct(values), title=title, legend=None, colors=colors, figsize=(16, 11))
    plot.yaxis.set_label_text("")
    plot.get_figure().savefig(name, dpi=300)


def merge_pictures(images_path, name):
    images = [Image.open(x) for x in images_path]
    total_height = 0
    total_width = 0

    for img in images:
        size = img.size
        total_height += size[1]
        total_width = max(size[0], total_width)

    merge = Image.new('RGB', (total_width, total_height))
    y_offset = 0
    for img in images:
        merge.paste(img, (0, y_offset))
        y_offset += img.size[1]
    
    merge.save(name)


##TODO Most used sticker/
# Number of Reaction per person
# Display number of messages and average per day
# Top N active day
# Most used word filtered/unfiltered

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-d', '--directory', type=str, required=True, help='Directory with the messages files')

    args = parser.parse_args()
    print(args.directory)
    print(args.directory.split("/")[-1])
    output_dir = os.path.join("output", args.directory.split("/")[-1])
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    conv = Conversation(args.directory)
   
    most_active_days = conv.get_n_most_active_days(10)
    print(most_active_days)
    create_bar_plot_from_list(most_active_days, 'Date', 'Number of messages', 'Most active days', 'most_active_days.png')

   
    #words_occurence = conv.get_most_used_words(3, 100)
    #print(words_occurence)
    '''
    msg_per_participant = sorted(conv.number_of_messages_per_participants.items(), key=operator.itemgetter(1), reverse=True)
    title = "Repartition of the {} messages of this conversation".format(conv.number_of_messages)
    create_pie_chart_from_list(msg_per_participant, title, 'msg_per_participants_pie.png')
    create_bar_plot_from_list(msg_per_participant, 'Participant', 'Number of messages', 'msg_per_participants_bar.png')
    

    msg_per_participant = sorted(conv.number_of_char_per_participants.items(), key=operator.itemgetter(1), reverse=True)
    create_bar_plot_from_list(msg_per_participant, 'Participant', 'Number of characters', 'char_per_participants.png')

    per_year_sorted = sorted(conv.get_number_of_messages_per_year().items())
    create_bar_plot_from_list(per_year_sorted, 'Year', 'Number of messages', 'year.png')

    ### Week day is a special case 
    per_weekday = conv.get_number_of_messages_per_weekday()
    weekday_ordered = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    weekday_value = []
    for day in weekday_ordered:
        weekday_value.append(per_weekday[day])
    create_bar_plot(weekday_ordered, 'Weekday', weekday_value, 'Number of messages', 'weekday.png')

    per_hour_sorted = sorted(conv.get_number_of_messages_per_hour().items())
    create_bar_plot_from_list(per_hour_sorted, 'Hours', 'Number of messages','hour.png')

    images_path = ['msg_per_participants_pie.png', 'msg_per_participants_bar.png', 'char_per_participants.png', 'year.png', 'weekday.png', 'hour.png']
    merge_pictures(images_path, 'merge.png')

    #print_dict_ordered_reverse(conv.number_of_char_per_participants)
    #print_dict_ordered_reverse(conv.number_of_photos_per_participants)
    '''
