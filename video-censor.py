import moviepy.editor as mp
import speech_recognition as sr
import whisper_timestamped as whisper
import json
import string
from bad_words import curse_words

# Function to censor video
def censor_video(video, curse_word_indices):
    censored_video = video
    for index in curse_word_indices:
        censored_video = censored_video.subclip(index-0.5, index+0.5).fx(mp.vfx.colorx, factor=0.2)
    return censored_video

# Function to parse JSON from AI
def parsing_json(jsonres,bad_word_array):
    return_array = []
    segments = jsonres["segments"]
    for objects in segments:
       for word in  objects["words"]:
            if word["text"].translate(str.maketrans('', '', string.punctuation)) in bad_word_array:
                tempdict = {
                    "badword":word["text"],
                    "starttime":word["start"],
                    "endtime":word["end"],
                }
                return_array.append(tempdict)
    
    return return_array
            

# Function to censor audio with beeps
def censor_audio(audio, curse_word_indices):
    offset = 0.1
    censored_audio = audio
    for element in curse_word_indices:
        duration = censored_audio.duration
        difftime = (element["endtime"] + offset) - (element["starttime"] - offset)
        beep = mp.AudioFileClip("./dependencies/censor-beep-9.wav").set_duration(difftime)

        begining = censored_audio.subclip(0, element["starttime"] - offset)
        end = censored_audio.subclip(element["endtime"] + offset ,duration)
                                          
        censored_audio = mp.concatenate_audioclips([begining,
                                                beep,
                                                end
                                                ])
    return censored_audio


def main():
    video_path = "../Videos/Edited Videos/test.mp4"
    output_path = "censored_video.mp4"

    # Load video
    video = mp.VideoFileClip(video_path)

    # Extract audio from video
    audio = video.audio
    audio.to_audiofile("temp_audio.wav")
    # Transcribe audio

    model = whisper.load_model("large-v2")
    result = whisper.transcribe(model,"temp_audio.wav")


    # Detect curse words in the transcribed text
    cursed_array_timestamps = parsing_json(result,curse_words)

    # Censor audio
    censored_audio = censor_audio(video.audio, cursed_array_timestamps)
    censored_audio_path = "censored_audio.wav"
    censored_audio.fps = 44100
    censored_audio.write_audiofile(censored_audio_path)

    # # Censor video
    censored_video = censor_video(video, [])

    # # Combine censored audio and video
    censored_video = censored_video.set_audio(censored_audio)

    # # Save censored video
    censored_video.write_videofile(output_path, codec='libx264')

if __name__ == "__main__":
    main()
