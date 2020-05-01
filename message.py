import datetime

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
