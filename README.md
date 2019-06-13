# VODBrain

VODBrain is a python library that automatically parses highlights from Twitch.TV streams based on chat history.
For a given stream, VODBrain analyzes the chat records to find anomalies in the time-series (e.g. moments that
indicate the chat is in a reactive state to an event of interest happening on the stream). When such an event is detected
VODBrain automatically downloads, converts, trims, and labels the relevant video clip.

## Inspiration

I wanted to see how easily twitch highlight videos (such as those posted on youtube) could be automatically generated.

## What it does

At set intervals determined by the user, VODBrain fetches the top 50 streamers currently online and analyzes the chat messages from the past elapsed time interval for semantic anomalies (e.g. high-frequency occurences of certain stream-specific keywords). For the detected anomalies, it automatically downloads the relevant video chunks and converts them into the proper output format after trimming.

## How I built it

VODBrain uses the twitch.tv api (v3), ffmpeg, and a collection of useful python libraries. This project was built in increments over the course of a month during the Winter 2018 semester.
