# import the necessary packages after installing them
from googleapiclient.discovery import build
from pymongo import MongoClient
import streamlit as st
import pandas as pd
import mysql.connector
from sqlalchemy import create_engine

# Set up MongoDB connection
MONGO_CONNECTION_STRING = "mongodb://127.0.0.1:27017"
client = MongoClient(MONGO_CONNECTION_STRING)
db = client["youtube_data_v4"]
channel_col = db["channel"]
video_col = db["video"]
comment_col = db["comment"]

# MySQL connection details
host = "localhost"
user = "root"
password = "12345"
database = "youtube_data"

# Create a connection string
connection_string = f"mysql+mysqlconnector://{user}:{password}@{host}/{database}"

# Create the database engine
engine = create_engine(connection_string)

# Streamlit app
def main():
    st.title("YouTube Data Retrieval and Conversion")

    # YouTube Data Retrieval section
    st.subheader("YouTube Data Retrieval")

    channel_id = st.text_input("Enter the Channel ID")

    if st.button("Retrieve and Store Data"):
        if channel_id:
            # Retrieve data from YouTube API
            youtube = build("youtube", "v3", developerKey="AIzaSyCzhHTN-9XqDyHW2dVTHamyTW4bcObePVY")

            # Initialize lists to store documents
            video_documents = []
            channel_documents = []
            comment_documents = []

            # Call the channels().list method to retrieve channel statistics and snippet
            channel_request = youtube.channels().list(
                part="snippet,statistics",
                id=channel_id
            )
            channel_response = channel_request.execute()

            if "items" in channel_response and len(channel_response["items"]) > 0:
                channel_info = {
                    "Channel_Name": channel_response["items"][0]["snippet"]["title"],
                    "Channel_Id": channel_response["items"][0]["id"],
                    "Subscription_Count": channel_response["items"][0]["statistics"]["subscriberCount"],
                    "Channel_Views": channel_response["items"][0]["statistics"]["viewCount"],
                    "Channel_Description": channel_response["items"][0]["snippet"]["description"],
                    "Playlist_Id": ""
                }

                # Get the playlist ID for the channel
                playlist_request = youtube.playlists().list(
                    part="snippet",
                    channelId=channel_id,
                    maxResults=1
                )

                playlist_response = playlist_request.execute()

                if "items" in playlist_response and len(playlist_response["items"]) > 0:
                    channel_info["Playlist_Id"] = playlist_response["items"][0]["id"]
                else:
                    channel_info["Playlist_Id"] = "No Playlist Found"

                channel_documents.append(channel_info)

                # Retrieve videos using pagination
                next_page_token = None
                while True:
                    search_request = youtube.search().list(
                        part="id,snippet",
                        channelId=channel_id,
                        maxResults=50,
                        pageToken=next_page_token,
                        type="video"
                    )
                    search_response = search_request.execute()

                    for item in search_response["items"]:
                        video_id = item["id"]["videoId"]

                        video_request = youtube.videos().list(
                            part="snippet,statistics,contentDetails",
                            id=video_id
                        )
                        video_response = video_request.execute()

                        video_info = {
                            "Video_Id": video_id,
                            "Channel_Name": channel_response["items"][0]["snippet"]["title"],
                            "Video_Name": video_response["items"][0]["snippet"]["title"],
                            "Video_Description": video_response["items"][0]["snippet"]["description"],
                            "PublishedAt": video_response["items"][0]["snippet"]["publishedAt"],
                            "View_Count": video_response["items"][0]["statistics"]["viewCount"],
                            "Like_Count": video_response["items"][0]["statistics"]["likeCount"],
                            "Favorite_Count": video_response["items"][0]["statistics"]["favoriteCount"],
                            "Comment_Count": video_response["items"][0]["statistics"]["commentCount"],
                            "Duration": video_response["items"][0]["contentDetails"]["duration"],
                            "Thumbnail": video_response["items"][0]["snippet"]["thumbnails"]["high"]["url"],
                            "Caption_Status": video_response["items"][0]["contentDetails"]["caption"]
                        }

                        video_documents.append(video_info)

                        comment_request = youtube.commentThreads().list(
                            part="snippet",
                            videoId=video_id,
                            textFormat="plainText",
                            maxResults=50
                        )

                        comment_response = comment_request.execute()

                        for comment in comment_response["items"]:
                            comment_id = comment["id"]
                            comment_text = comment["snippet"]["topLevelComment"]["snippet"]["textDisplay"]
                            video_name = video_response["items"][0]["snippet"]["title"]
                            comment_author = comment["snippet"]["topLevelComment"]["snippet"]["authorDisplayName"]
                            comment_published = comment["snippet"]["topLevelComment"]["snippet"]["publishedAt"]
                            comment_likes = comment["snippet"]["topLevelComment"]["snippet"]["likeCount"]
                            comment_info = {
                                "Comment_Id": comment_id,
                                "Video_Name": video_name,
                                "Comment_Text": comment_text,
                                "Comment_Author": comment_author,
                                "Comment_Published": comment_published,
                                "Comment_Likes": comment_likes
                            }

                            comment_documents.append(comment_info)

                    if "nextPageToken" in search_response:
                        next_page_token = search_response["nextPageToken"]
                    else:
                        break

            # Store data in MongoDB
            if len(channel_documents) > 0:
                channel_col.insert_many(channel_documents)

            if len(video_documents) > 0:
                video_col.insert_many(video_documents)

            if len(comment_documents) > 0:
                comment_col.insert_many(comment_documents)

            # Display success prompt
            st.success("Data retrieval and storage completed successfully.")

        else:
            st.warning("Please enter a channel ID.")

    # MySQL Data Conversion and Queries section
    st.subheader("MySQL Data Conversion and Queries")

    if st.button("Convert to MySQL"):
        # Retrieve the documents from MongoDB collections
        channel_docs = list(channel_col.find())
        video_docs = list(video_col.find())
        comment_docs = list(comment_col.find())

        # Convert channel documents to DataFrame
        channel_df = pd.DataFrame(channel_docs)

        # Convert video documents to DataFrame
        video_df = pd.DataFrame(video_docs)

        # Convert comment documents to DataFrame
        comment_df = pd.DataFrame(comment_docs)

        # Remove the "_id" column from the DataFrames
        if "_id" in channel_df.columns:
            channel_df = channel_df.drop("_id", axis=1)
        if "_id" in video_df.columns:
            video_df = video_df.drop("_id", axis=1)
        if "_id" in comment_df.columns:
            comment_df = comment_df.drop("_id", axis=1)

        # Insert the DataFrames into MySQL tables
        channel_df.to_sql("channels", con=engine, if_exists="append", index=False)
        video_df.to_sql("videos", con=engine, if_exists="append", index=False)
        comment_df.to_sql("comments", con=engine, if_exists="append", index=False)

        # Display success prompt
        st.success("Data conversion to MySQL completed successfully.")

        # 1st query (video_name, channel_name)
        query = """
            SELECT video_name, channel_name
            FROM videos
        """
        results = pd.read_sql_query(query, engine)
        st.subheader("Query 1: Video Name and Channel Name")
        st.table(results)

        # 2nd query (channel_name, video_count)
        query = """
            SELECT channel_name, COUNT(video_id) AS video_count
            FROM videos
            GROUP BY channel_name
            ORDER BY video_count DESC
        """
        results = pd.read_sql_query(query, engine)
        st.subheader("Query 2: Channel Name and Video Count")
        st.table(results)

        # 3rd query (channel_name, video_count)
        query = """
            SELECT video_name, channel_name
            FROM videos
            ORDER BY view_count DESC
            LIMIT 10
        """
        results = pd.read_sql_query(query, engine)
        st.subheader("Query 3: Top 10 Videos by View Count")
        st.table(results)

        # 4th query (video_name, comment_count)
        query = """
            SELECT video_name, COUNT(comment_id) AS comment_count
            FROM comments
            GROUP BY video_name
        """
        results = pd.read_sql_query(query, engine)
        st.subheader("Query 4: Video Name and Comment Count")
        st.table(results)

        # 5th query (video_name, channel_name, like_count)
        query = """
            SELECT video_name, channel_name, like_count
            FROM videos
            ORDER BY like_count DESC
            LIMIT 10
        """
        results = pd.read_sql_query(query, engine)
        st.subheader("Query 5: Top 10 Videos by Like Count")
        st.table(results)

        # 6th query (video_name, like_count)
        query = """
                SELECT video_name, like_count
                FROM videos
                ORDER BY like_count DESC
            """
        results = pd.read_sql_query(query, engine)
        st.subheader("Query 6: Videos by Total Likes")
        st.table(results)

        # 7th query (channel_name, channel_views)
        query = """
                SELECT channel_name, channel_views
                FROM channels
            """
        results = pd.read_sql_query(query, engine)
        st.subheader("Query 7: Channels and Total Views")
        st.table(results)

        # 8th query (video_name, max_views)
        query = """
                SELECT video_name, MAX(view_count) AS max_views
                FROM videos
                GROUP BY video_name
                LIMIT 10
            """
        results = pd.read_sql_query(query, engine)
        st.subheader("Query 8: Top 10 Videos by Views count")
        st.table(results)

        # 9th query (video_name, channel_name, comment_count)
        query = """
                SELECT v.video_name, v.channel_name, COUNT(c.comment_id) AS comment_count
                FROM videos AS v
                JOIN comments AS c ON v.video_name = c.video_name
                GROUP BY v.video_id, v.video_name, v.channel_name
                ORDER BY comment_count DESC
                LIMIT 10
            """
        results = pd.read_sql_query(query, engine)
        st.subheader("Query 9: Top 10 Videos by Comment Count")
        st.table(results)

        # 10th query (video_name, channel_name, comment_likes)
        query = """
                SELECT v.video_name, v.channel_name, c.comment_likes
                FROM videos AS v
                JOIN comments AS c ON v.video_name = c.video_name
                ORDER BY comment_likes DESC
                LIMIT 10
            """
        results = pd.read_sql_query(query, engine)
        st.subheader("Query 10: Top 10 Comments by Likes")
        st.table(results)

if __name__ == "__main__":
    main()
