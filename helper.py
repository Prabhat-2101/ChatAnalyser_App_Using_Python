import re
import pandas as pd
from wordcloud import WordCloud
from collections import Counter
import emoji
from datetime import datetime

pattern = r"(\d{1,2}/\d{1,2}/\d{2,4}, \d{1,2}:\d{1,2}\s*[\u202F\s]*[apAP][mM]) - (?:(.*?): )?(.*)"
f = open('stopwords_hinglish.txt', 'r')
stop_words = f.read()


def preprocess_data(data):
    matches = re.findall(pattern, data)
    date_times, senders, messages, msg_type = [], [], [], []

    for match in matches:
        date_times.append(match[0])
        if match[1]:
            senders.append(match[1])
            msg_type.append('Chat')
        else:
            senders.append(None)
            msg_type.append('Notification')
        messages.append(match[2])

    df = pd.DataFrame({
        'DateTime': date_times,
        'Sender': senders,
        'Message': messages,
        'Msg_Type': msg_type
    })
    df['DateTime'] = pd.to_datetime(df['DateTime'], format='%d/%m/%Y, %I:%M %p')

    df['Only_date'] = df['DateTime'].dt.date
    df['Day'] = df['DateTime'].dt.day
    df['Day_name'] = df['DateTime'].dt.day_name()
    df['Month'] = df['DateTime'].dt.month
    df['Month_name'] = df['DateTime'].dt.month_name()
    df['Year'] = df['DateTime'].dt.year
    df['Hour'] = df['DateTime'].dt.hour
    df['Minute'] = df['DateTime'].dt.minute

    period = []
    for hour in df[['Day_name', 'Hour']]['Hour']:
        if hour == 23:
            period.append(str(hour) + "-" + str('00'))
        elif hour == 0:
            period.append(str('00') + "-" + str(hour + 1))
        else:
            period.append(str(hour) + "-" + str(hour + 1))

    df['Period'] = period

    return df


def user_list(data):
    users = data.unique().tolist()
    users.remove(None)
    users.sort()
    users.insert(0, "All User")
    return users


def fetch_user_messages(msg):
    url_pattern = r'https?://[^\s]+'
    words, media, links = 0, 0, 0
    for i in msg:
        if i == "<Media omitted>":
            media += 1
        elif bool(re.match(url_pattern, i)):
            links += 1
        else:
            words += len(i.split())
    return words, media + links


def fetch_user_stats(user_selected, df):
    user_stats = {}
    if user_selected != 'All User':
        df = df[df['Sender'] == user_selected]

    user_msg_count, media_msg_count = fetch_user_messages(df['Message'])
    first_message_date = df['DateTime'].min()
    parsed_date = datetime.strptime(str(first_message_date), "%Y-%m-%d %H:%M:%S")
    first_message_date = parsed_date.strftime("%d-%m-%Y")
    user_stats['chats'] = len(df)
    user_stats['messages'] = user_msg_count
    user_stats['media_messages'] = media_msg_count
    user_stats['first_message'] = first_message_date

    return user_stats


def fetch_most_busy_user(df):
    active_users = df['Sender'].value_counts().head()
    names, counts = active_users.index, active_users.values
    df = round((df['Sender'].value_counts() / df.shape[0]) * 100, 2).reset_index().rename(
        columns={'index': 'Name', 'Sender': 'percent'})
    return names, counts, df


def create_wordcloud(user_selected, df):
    if user_selected != 'All User':
        df = df[df['Sender'] == user_selected]

    temp = df[df['Sender'] != 'None']
    temp = temp[temp['Message'] != '<Media omitted>']

    def remove_stop_words(message):
        y = []
        for word in message.lower().split():
            if word not in stop_words:
                y.append(word)
        return " ".join(y)

    wc = WordCloud(width=500, height=500, min_font_size=10, background_color='white')
    temp['Message'] = temp['Message'].apply(remove_stop_words)
    df_wc = wc.generate(temp['Message'].str.cat(sep=" "))
    return df_wc


def most_common_words(selected_user, df):
    if selected_user != 'All User':
        df = df[df['Sender'] == selected_user]

    temp = df[df['Sender'] != 'None']
    temp = temp[temp['Message'] != '<Media omitted>']

    words = []

    for message in temp['Message']:
        for word in message.lower().split():
            if word not in stop_words:
                words.append(word)

    most_common_df = pd.DataFrame(Counter(words).most_common(10))
    return most_common_df


def emoji_helper(selected_user,df):
    if selected_user != 'All User':
        df = df[df['Sender'] == selected_user]

    emojis = []
    for message in df['Message']:
        emojis.extend([c for c in message if c in emoji.UNICODE_EMOJI['en']])

    emoji_df = pd.DataFrame(Counter(emojis).most_common(len(Counter(emojis))))
    return emoji_df


def monthly_timeline(selected_user,df):
    if selected_user != 'All User':
        df = df[df['Sender'] == selected_user]

    timeline = df.groupby(['Year', 'Month', 'Month_name']).count()['Message'].reset_index()
    time = []
    for i in range(timeline.shape[0]):
        time.append(timeline['Month_name'][i] + "-" + str(timeline['Year'][i]))

    timeline['time'] = time

    return timeline


def daily_timeline(selected_user,df):
    if selected_user != 'All User':
        df = df[df['Sender'] == selected_user]

    daily_timelines = df.groupby('Only_date').count()['Message'].reset_index()

    return daily_timelines


def week_activity_map(selected_user,df):
    if selected_user != 'All User':
        df = df[df['Sender'] == selected_user]

    return df['Day_name'].value_counts()


def month_activity_map(selected_user,df):
    if selected_user != 'All User':
        df = df[df['Sender'] == selected_user]

    return df['Month'].value_counts()


def activity_heatmap(selected_user,df):

    if selected_user != 'All User':
        df = df[df['Sender'] == selected_user]

    user_heatmap = df.pivot_table(index='Day_name', columns='Period', values='Message', aggfunc='count').fillna(0)

    return user_heatmap


