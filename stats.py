import argparse
import datetime
import operator
import os
import sys
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

from colour import Color
from PIL import Image
from conv import Conversation
from matplotlib.offsetbox import OffsetImage,AnnotationBbox

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
    df = pd.DataFrame(list(zip(x, y)), columns=(x_name, y_name))
    plot = df.plot.bar(x=x_name, y=y_name, color='#3377ff', figsize=(16,11))
    plot.set_xticklabels(plot.get_xticklabels(), rotation=45, horizontalalignment='right')
    plt.title(title, fontsize=16)
    plot.get_figure().savefig(name, dpi=300)


def offset_image(coord, name, ax):
    img = plt.imread(name)
    im = OffsetImage(img, zoom=0.3)
    im.image.axes = ax

    ab = AnnotationBbox(im, (coord, 0),  xybox=(0., -16.), frameon=False,
                        xycoords='data',  boxcoords="offset points", pad=0)

    ax.add_artist(ab)


def create_bar_plot_emoji(x, x_name, y, y_name, title, name, emoji_dir):
    fig, ax = plt.subplots()
    df = pd.DataFrame(list(zip(x, y)), columns=(x_name, y_name))
    ax = df.plot.bar(x=x_name, y=y_name, color='#3377ff', figsize=(16,11))
    ax.tick_params(axis='x', which='major', pad=28)
    ax.set_xticklabels(ax.get_xticklabels(), rotation=0, horizontalalignment='center')
    #hide text
    #plt.tick_params(axis='x', which='both', bottom=False, top=False, labelbottom=False)
    for index, emoji_name in enumerate(x):
        emoji_path = (emoji_dir + '/{}.png').format(emoji_name)
        offset_image(index, emoji_path, ax)
    ax.get_figure().savefig(name, dpi=300)

def create_pie_chart_from_list(l, title, name):
    values = []
    labels = []
    for item in l:
        labels.append(item[0])
        values.append(item[1])
    create_pie_chart(values, labels, title, name)


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
    plot = df.plot.pie(y='values', autopct=make_autopct(values), legend=None, colors=colors, figsize=(16, 11))
    plt.title(title, fontsize=16)
    plot.yaxis.set_label_text("")
    plot.get_figure().savefig(name, dpi=300)


#Data should be a 2D array of month (y axes) and day (x axes)
def create_heatmap(data, title, name):
    months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    days = list(range(1, 32))
    
    #Create a custom color map because out data are not linear
    hc = ['#ffffff', '#bad6eb', '#89bedc', '#539ecd', '#2b7bba', '#052647']
    th = [0, 0.001, 0.25, 0.5, 0.75, 1]
    cdict = NonLinCdict(th, hc)
    cm = matplotlib.colors.LinearSegmentedColormap('custom_blue', cdict)

    fig, ax = plt.subplots(figsize=(16,8), dpi=300)
    df = pd.DataFrame(data, index=months, columns=days)
    plt.tight_layout()
    ax = sns.heatmap(df, cmap=cm, annot=True, fmt='d', linewidths=.7, square=True, cbar_kws={'label': 'Number of messages'}, ax=ax)
    ax.figure.axes[-1].yaxis.label.set_size(20)
    ax.set_title(title, pad=50, fontsize=16)
    ax.get_figure().savefig(name)


#This allow to create a single haetmap for all the messages but the result doesn't look that good
def create_heatmap_full_years(data, title, name):
    y = []
    x = list(range(1, 32))
    data_2d = []
    data_sorted = sorted(data.items(), key=lambda x: datetime.datetime.strptime(x[0], "%m-%Y"))
    for item in data_sorted:
        y.append(item[0])
        data_2d.append(item[1])
    #Create a custom color map because out data are not linear
    hc = ['#ffffff', '#bad6eb', '#89bedc', '#539ecd', '#2b7bba', '#052647']
    th = [0, 0.001, 0.25, 0.5, 0.75, 1]
    cdict = NonLinCdict(th, hc)
    cm = matplotlib.colors.LinearSegmentedColormap('custom_blue', cdict)
    fig, ax = plt.subplots(figsize=(16,8 * (len(data_sorted) / 12)), dpi=300)
    df = pd.DataFrame(data_2d, index=y, columns=x)
    #plt.tight_layout()
    ax = sns.heatmap(df, cmap=cm, annot=True, fmt='d', linewidths=.7, square=True, cbar_kws={'label': 'Number of messages'}, ax=ax)
    ax.figure.axes[-1].yaxis.label.set_size(20)
    ax.set_title(title, pad=50, fontsize=16)
    ax.get_figure().savefig(name)


def make_autopct(values):
    def my_autopct(pct):
        total = sum(values)
        val = int(round(pct * total / 100.0))
        s = "{:.2f}%\n({})".format(pct, val)
        return s
    return my_autopct


def merge_pictures(images_path, name):
    total_height = 0
    total_width = 0
    y_offset = 0

    for img in images_path:
        with Image.open(img) as current_img:
            if y_offset == 0:
                total_width = current_img.size[0]
                total_height = len(images_path) * current_img.size[1]
                merge = Image.new('RGB', (total_width, total_height))
            merge.paste(current_img, (0, y_offset))
            y_offset += current_img.size[1]
    merge.save(name)


def NonLinCdict(steps, hexcol_array):
    cdict = {'red': (), 'green': (), 'blue': ()}
    for s, hexcol in zip(steps, hexcol_array):
        rgb = matplotlib.colors.hex2color(hexcol)
        cdict['red'] = cdict['red'] + ((s, rgb[0], rgb[0]),)
        cdict['green'] = cdict['green'] + ((s, rgb[1], rgb[1]),)
        cdict['blue'] = cdict['blue'] + ((s, rgb[2], rgb[2]),)
    return cdict


def export_all(conv, output_dir):
    exported_images = []
    
    # Message heatmap per year
    msg_day = conv.get_message_per_day_as_2d_array_per_year()
    for year in msg_day:
        number_of_messages = np.sum(msg_day[year])
        number_of_days = (datetime.date(year, 12, 31)- datetime.date(year, 1, 1)).days + 1
        fig_name = output_dir + '/heatmap' + str(year) + '.png'
        title = 'Number of messages per day in {}\n{} messages this year (avg: {:.2f}/day)'.format(str(year), number_of_messages, number_of_messages / number_of_days)
        create_heatmap(msg_day[year], title, fig_name)
        exported_images.append(fig_name)
    #We want the heatmatp to be in the right order for the merge
    exported_images.sort()

    # Message per participants pie and barplot
    title = 'Repartition of the {} messages of this conversation'.format(conv.number_of_messages)
    fig_name = output_dir + '/msg_per_participants_pie.png'
    msg_per_participant = sorted(conv.number_of_messages_per_participants.items(), key=operator.itemgetter(1), reverse=True)
    create_pie_chart_from_list(msg_per_participant, title, fig_name)
    exported_images.append(fig_name)


    fig_name = output_dir + '/msg_per_participants_bar.png'
    create_bar_plot_from_list(msg_per_participant, 'Participant', 'Number of messages', title, fig_name)
    exported_images.append(fig_name)

    # Char per participants
    title = 'Repartition of the {} characters of this conversation'.format(conv.number_of_char)
    fig_name = output_dir + '/char_per_participants.png'
    char_per_participant = sorted(conv.number_of_char_per_participants.items(), key=operator.itemgetter(1), reverse=True)
    create_bar_plot_from_list(char_per_participant, 'Participant', 'Number of characters', title, fig_name)
    exported_images.append(fig_name)

    # Pics per participants
    title = 'Repartition of the {} sent pictures of this conversation'.format(conv.number_of_pics)
    fig_name = output_dir + '/pics_per_participants_pie.png'
    pics_per_participant = sorted(conv.number_of_pics_per_participants.items(), key=operator.itemgetter(1), reverse=True)
    create_pie_chart_from_list(pics_per_participant, title, fig_name)
    exported_images.append(fig_name)

    fig_name = output_dir + '/pics_per_participants_bar.png'
    create_bar_plot_from_list(pics_per_participant, 'Participant', 'Number of pictures', title, fig_name)
    exported_images.append(fig_name)

    # Year
    title = 'Number of messages per year'
    fig_name = output_dir + '/year.png'
    per_year_sorted = sorted(conv.get_number_of_messages_per_year().items())
    create_bar_plot_from_list(per_year_sorted, 'Year', 'Number of messages', title, fig_name)
    exported_images.append(fig_name)

    # Weekday is a special case 
    title = 'Number of messages per weekday'
    fig_name = output_dir + '/weekday.png'
    per_weekday = conv.get_number_of_messages_per_weekday()
    weekday_ordered = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    weekday_value = []
    for day in weekday_ordered:
        weekday_value.append(per_weekday[day])
    create_bar_plot(weekday_ordered, 'Weekday', weekday_value, 'Number of messages', title, fig_name)
    exported_images.append(fig_name)

    # Hour
    title = 'Number of messages per hour'
    fig_name = output_dir + '/hour.png'
    per_hour_sorted = sorted(conv.get_number_of_messages_per_hour().items())
    create_bar_plot_from_list(per_hour_sorted, 'Hours', 'Number of messages', title, fig_name)
    exported_images.append(fig_name)

    return exported_images


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-d', '--directory', type=str, required=True, help='Directory with the messages files')

    args = parser.parse_args()
    print(args.directory)
    print(args.directory.split('/')[-1])

    output_dir = os.path.join('output', args.directory.split('/')[-1])
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    conv = Conversation(args.directory)

    '''
    wow = "\u00f0\u009f\u0098\u00ae".encode('iso-8859-1').decode('utf8')
    love = "\u00f0\u009f\u0098\u008d".encode('iso-8859-1').decode('utf8')
    sad = "\u00f0\u009f\u0098\u00a2".encode('iso-8859-1').decode('utf8')
    thumb = "\u00f0\u009f\u0091\u008d".encode('iso-8859-1').decode('utf8')
    laugh = "\u00f0\u009f\u0098\u0086".encode('iso-8859-1').decode('utf8')

    x = ['wow', 'love', 'cry', 'laugh']
    y = [10, 5, 2, 15]

    x_name = "reactions"
    y_name = "number"
    title = "num of reactions"
    name = "num_reaction2.png"
    create_bar_plot_emoji(x, x_name, y, y_name, "emoji", "lol.png", "./emoji/")
    '''
    
    exported_path = export_all(conv, output_dir)
    merge_pictures(exported_path, os.path.join(output_dir, 'merge.png'))

  