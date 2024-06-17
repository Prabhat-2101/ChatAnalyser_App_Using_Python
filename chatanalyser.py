import streamlit as st
import helper as hp
import matplotlib.pyplot as plt
import seaborn as sns


st.sidebar.title("Whatsapp Chat Analyser")

upload_file = st.sidebar.file_uploader("Choose a file", type=["txt"])

if upload_file is not None:
    byte_data = upload_file.getvalue()
    data = byte_data.decode('utf-8')
    df = hp.preprocess_data(data)
    user_list = hp.user_list(df['Sender'])
    user_selected = st.sidebar.selectbox("Choose the User..", user_list)

    if st.sidebar.button("Show Report"):
        st.title('User Report')
        col1, col2, col3, col4 = st.columns(4)

        user_stats = hp.fetch_user_stats(user_selected, df)
        with col1:
            st.header("Messages")
            st.subheader(user_stats['chats'])

        with col2:
            st.header("Words")
            st.subheader(user_stats['messages'])

        with col3:
            st.header("Links/Media")
            st.subheader(user_stats['media_messages'])

        with col4:
            st.header("Join Date")
            st.subheader(user_stats['first_message'])

        if user_selected == 'All User':
            st.title('Most Active Users')
            col1, col2 = st.columns(2)
            names, counts, msg_percent = hp.fetch_most_busy_user(df)
            with col1:
                fig, ax = plt.subplots()
                ax.bar(names, counts, color='red')
                plt.xticks(rotation='vertical')
                st.pyplot(fig)

            with col2:
                st.dataframe(msg_percent)

        st.title("Monthly Timeline")
        timeline = hp.monthly_timeline(user_selected, df)
        fig, ax = plt.subplots()
        ax.plot(timeline['time'], timeline['Message'], color='green')
        plt.xticks(rotation='vertical')
        st.pyplot(fig)

        # daily timeline
        st.title("Daily Timeline")
        daily_timeline = hp.daily_timeline(user_selected, df)
        fig, ax = plt.subplots()
        ax.plot(daily_timeline['Only_date'], daily_timeline['Message'], color='black')
        plt.xticks(rotation='vertical')
        st.pyplot(fig)

        # activity map
        col1, col2 = st.columns(2)

        with col1:
            st.header("Most busy day")
            busy_day = hp.week_activity_map(user_selected, df)
            fig, ax = plt.subplots()
            ax.bar(busy_day.index, busy_day.values, color='purple')
            plt.xticks(rotation='vertical')
            st.pyplot(fig)

        with col2:
            st.header("Most busy month")
            busy_month = hp.month_activity_map(user_selected, df)
            months = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']
            indexes = []
            for i in busy_month.index:
                indexes.append(months[i-1])
            fig, ax = plt.subplots()
            ax.bar(indexes, busy_month.values, color='orange')
            plt.xticks(rotation='vertical')
            st.pyplot(fig)

        st.title("Weekly Activity Map")
        user_heatmap = hp.activity_heatmap(user_selected, df)
        fig, ax = plt.subplots()
        ax = sns.heatmap(user_heatmap)
        st.pyplot(fig)

        st.title("Word Cloud of User")
        df_wc = hp.create_wordcloud(user_selected, df)
        fig, ax = plt.subplots()
        ax.imshow(df_wc)
        st.pyplot(fig)

        #most common words
        most_common_word_df = hp.most_common_words(user_selected, df)
        st.title("Frequent Word of Selected User")
        fig, ax = plt.subplots()
        ax.bar(most_common_word_df[0], most_common_word_df[1])
        plt.xticks(rotation='vertical')
        st.pyplot(fig)

        emoji_df = hp.emoji_helper(user_selected, df)
        st.title("Emoji Analysis")
        col1, col2 = st.columns(2)
        with col1:
            st.dataframe(emoji_df)
        with col2:
            fig, ax = plt.subplots()
            ax.pie(emoji_df[1].head(), labels=emoji_df[0].head(), autopct="%0.2f")
            st.pyplot(fig)

