from youtube_transcript_api import YouTubeTranscriptApi

def get_youtube_transcript(video_url, language='de'):
    """
    Extracts the transcript for the given YouTube video URL.

    Args:
        video_url (str): The URL of the YouTube video.
        language (str): Language code for the transcript (default is 'de' for German).

    Returns:
        list: A list of transcript segments with timestamps and text.
    """
    try:
        # Extract the video ID
        if "v=" in video_url:
            video_id = video_url.split("v=")[-1].split("&")[0]
        else:
            # Handle short URLs like youtu.be/VIDEO_ID
            video_id = video_url.split("/")[-1]

        # Fetch transcript
        transcript = YouTubeTranscriptApi.get_transcript(video_id, languages=[language])
        return transcript, None  # No error
    except Exception as e:
        return None, str(e)