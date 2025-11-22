
import os
import assemblyai as aai
#Appelle l'api de assemblyai afin de generer la transcription et recuperer un fichier srt
NB_CARACTERE_PER_CAPTION = 20
aai.settings.api_key = "c7dce2def45841bdb9d66f0cf8866b51"

transcriber = aai.Transcriber()

def transcribe(audio_path,  language_code="fr", generate_subtitles=True, nb_caracter_per_caption=NB_CARACTERE_PER_CAPTION,):
    config = aai.TranscriptionConfig(speaker_labels=True, language_code=language_code)

    transcript = transcriber.transcribe(audio_path, config)
    srt_path = audio_path.replace(".mp3", f"_{language_code}.srt")

    if transcript.error:
        print(transcript.error)
    else:
        if generate_subtitles:
            f = open(srt_path, "a", encoding="UTF8")
            f.write(transcript.export_subtitles_srt(chars_per_caption=nb_caracter_per_caption))
            f.close()

        #for utterance in transcript.utterances:
            #print(f"Speaker {utterance.speaker}: {utterance.text}")
    return transcript,srt_path

