import requests
from pytube import YouTube
from pytube.exceptions import PytubeError
from urllib.error import URLError


messages = {
    "AgeRestrictedError": "Video is age restricted, and cannot be accessed without OAuth",
    "ExtractError": "Data extraction based error",
    "HTMLParseError": "HTML could not be parsed",
    "LiveStreamError": "Video is a live stream",
    "MaxRetriesExceeded": "Maximum number of retries exceeded",
    "MembersOnly": "Video is members-only",
    "RecordingUnavailable": "Recording unavailable",
    "RegexMatchError": "Invalid URL",
    "VideoPrivate": "Video is private",
    "VideoRegionBlocked": "Video region blocked",
    "VideoUnavailable": "Video is unavailable"
}


def find_video(url):
    try:
        yt = YouTube(url)
        title = yt.title

        thumbnail_url = yt.thumbnail_url
        thumbnail_data = requests.get(thumbnail_url).content

        video_streams = list(yt.streams.filter(progressive=True).order_by('resolution')[::-1])
        audio_streams = list(yt.streams.filter(only_audio=True).order_by('abr')[::-1])
        video_streams_info = [
            ' '.join([stream.resolution, str(stream.fps) + 'fps',
                      f'{stream.mime_type.split("/")[0]} (*.{stream.mime_type.split("/")[1]})'])
            for stream in video_streams
        ]
        audio_streams_info = [
            ' '.join([stream.abr, f'{stream.mime_type.split("/")[0]} (*.{stream.mime_type.split("/")[1]})'])
            for stream in audio_streams
        ]
        streams = video_streams + audio_streams
        streams_info = video_streams_info + audio_streams_info
        streams = {streams_info[i]: streams[i] for i in range(len(streams))}

        return title, thumbnail_data, streams
    except PytubeError as e:
        e = repr(e).split('(')[0]
        return messages[e], None, {}
    except URLError as e:
        return str(e), None, {}
    except Exception as e:
        return f"{repr(e)}. Try to upgrade libraries"


def download(stream, path):
    try:
        stream.download(*path)
        return 'done'
    except PytubeError as e:
        e = repr(e).split('(')[0]
        return messages[e]
    except URLError as e:
        return str(e)
    except Exception as e:
        return f"{repr(e)}. Try to upgrade libraries"
