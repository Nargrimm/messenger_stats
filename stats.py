import argparse
import json
import operator
import os
import sys

class Message:
    #if the content type is a pictue the content will be the path to this pic
    def __init__(self, sender, timestamp_ms, messenger_type, content_type, content):
        self.sender = sender
        self.timestamp_ms = timestamp_ms
        self.type = messenger_type
        self.content_type = content_type
        self.content = content


class Conversation:
    def __init__(self, directory):
        self.directory = directory
        self.files = self.get_message_files()
        self.messages = self.get_messages()
        self.participants = self.get_all_participants()
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
                    participants.add(p['name'])
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
                        messages.append(Message(m['sender_name'], m['timestamp_ms'], m['type'], content_type, content))
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
            if msg.content_type != "photos":
                continue
            participants_pics[msg.sender] += len(msg.content.split(';')) - 1 
        return participants_pics


def print_dict_ordered_reverse(d):
    print(sorted(d.items(), key=operator.itemgetter(1), reverse=True))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-d', '--directory', type=str, required=True, help='Directory with the messages files')

    args = parser.parse_args()
    print(args.directory)
    conv = Conversation(args.directory)

    print_dict_ordered_reverse(conv.number_of_messages_per_participants)
    print_dict_ordered_reverse(conv.number_of_char_per_participants)
    print_dict_ordered_reverse(conv.number_of_photos_per_participants)


       
