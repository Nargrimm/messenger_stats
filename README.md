# Messenger Stats

This tool was created to give you stats about your Facebook Messenger's conversations

## Data Export

First you need to export your Facebook data. To do this, follow [this guide](https://www.facebook.com/help/972879969525875?helpref=uf_permalink) and request the data as JSON. Depending of the size of the requested data this can take a long time (few hours or a day).

Once you have your data unzip the archive. The content (messages, picture...) should be in a "message" folder


## Usage

```
usage: python3 stats.py -c CONVERSATION_PATH -s STICKER
```

CONVERSATION_PATH: Should be the path to the conversation folder. Be careful for every conversation there is two directories, one for the files (pictures/gifs/files...) and one with the actual messages (in json files). Here we want the second one, the folder containing the json messages files. For example /my/path/messages/inbox/johndoe_1a2b3c4d

STICKER: Should be the path to the "stickers_used" folder (within your message folder) usually this will be something like /my/path/messages/stickers_used

```
python3 stats.py -c /my/path/messages/inbox/johndoe_1a2b3c4d -s /my/path/messages/stickers_used/
```

## Output

By default you will find the output in the "output/" directory

The output will consist of several PNG files:

* **Messages per days**: Heatmap representing the messages repartition per days for a year. We output one heatmap for each year of the conversation

* **Messages per participants**: A pie and a bar chart representing the number of messages sent per participant. If there is more than a certain number of participants in the conversation we aggregate the one who send the least messages in the pie chart

* **Characters per participants**: A bar chart representing the number of characters sent per participant. This data can be uselful to correlate with the messages per participant

* **Pictures per participants**: A pie and a bar chart representing the number of pictures sent per participant.  If there is more than a certain number of participants in the conversation we aggregate the one who sent the least messages in the pie chart

* **Message per year**: A bar chart representing the number of messages sent for each year of the conversation

* **Message per weekday**:  A bar chart representing the number of messages sent per weekdays

* **Message per hour**: A bar chart representing the number of messages sent per hours (from 0 to 23)

* **Sticker**: A bar chart representing the repartition of the most sent stickers

* **Reactions**: A bar chart representing the repartition of the different reactions used

* **Merge**: A PNG merging all the of the aboved pictures in one big pictures

## Perfs

The tool can take a few seconds on big conversation. The parsing is quiet fast but the generating the PNG files takes some time (since most of them are in 4800x3300). If you want to improve the speed you can manually reduce the PNG output quality.