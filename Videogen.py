import os
import pandas as pd
from google.cloud import texttospeech
from moviepy import ImageClip, AudioFileClip
import google_auth_oauthlib.flow
import googleapiclient.discovery
import googleapiclient.errors
from google.oauth2 import service_account

def load_plots(csv_file):
    """
    Load plots from a CSV file.
    The CSV file should have at least the columns "title" and "plot".
    """
    df = pd.read_csv(csv_file)
    return df[['movie', 'plot_excerpt']].to_dict('records')

def generate_audio(text, output_filename):
    """
    Generate an audio file from text using Google Cloud Text-to-Speech.
    
    Make sure the GOOGLE_APPLICATION_CREDENTIALS environment variable is
    set to your JSON key file for Google Cloud.
    """
    credentials = service_account.Credentials.from_service_account_file(r'D:\Code_J\Video scripting\theta-anchor-460202-b0-795a3b3ee72d.json')
    # Set the environment variable for Google Cloud authentication
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "D:\Code_J\Video scripting\theta-anchor-460202-b0-795a3b3ee72d.json"
    client = texttospeech.TextToSpeechClient(credentials=credentials)

    synthesis_input = texttospeech.SynthesisInput(text=text)
    voice = texttospeech.VoiceSelectionParams(
        language_code="en-US", 
        ssml_gender=texttospeech.SsmlVoiceGender.NEUTRAL
    )
    audio_config = texttospeech.AudioConfig(
        audio_encoding=texttospeech.AudioEncoding.MP3
    )
    
    response = client.synthesize_speech(
        input=synthesis_input, 
        voice=voice, 
        audio_config=audio_config
    )

    with open(output_filename, "wb") as out:
        out.write(response.audio_content)
    print(f"Audio file saved as {output_filename}")

def create_video(audio_filename, image_filename, output_video):
    """
    Create a video using a static background image and an audio clip.
    
    The generated video lasts as long as the audio.
    """
    audio_clip = AudioFileClip(audio_filename)
    duration = audio_clip.duration
    image_clip = ImageClip(image_filename).set_duration(duration)
    
    # Set the audio to the image clip to make a video clip
    video_clip = image_clip.set_audio(audio_clip)
    
    # Write the video file to disk (adjust fps as needed)
    video_clip.write_videofile(output_video, fps=24)
    print(f"Video created as {output_video}")

def upload_video(video_file, title, description, tags=None, category_id="22"):
    """
    Upload a video to YouTube using the YouTube Data API.
    
    Replace "YOUR_CLIENT_SECRET_FILE.json" with the path to your OAuth client secrets.
    When running this function for the first time, it will prompt you to complete
    the OAuth flow.
    """
    scopes = ["https://www.googleapis.com/auth/youtube.upload"]
    client_secrets_file = "YOUR_CLIENT_SECRET_FILE.json"  # Update with your path

    # Run local server OAuth flow
    flow = google_auth_oauthlib.flow.InstalledAppFlow.from_client_secrets_file(
        client_secrets_file, scopes)
    credentials = flow.run_console()
    youtube = googleapiclient.discovery.build("youtube", "v3", credentials=credentials)
    
    request_body = {
        "snippet": {
            "title": title,
            "description": description,
            "tags": tags if tags else [],
            "categoryId": category_id
        },
        "status": {
            "privacyStatus": "public"  # Change to "private" or "unlisted" if needed.
        }
    }
    
    request = youtube.videos().insert(
        part="snippet,status",
        body=request_body,
        media_body=video_file
    )
    response = request.execute()
    print("Video uploaded successfully! Video ID:", response.get("id"))

def process_plot(plot_record, background_image):
    """
    Process a single plot: generate audio, create a video, and optionally upload to YouTube.
    """
    title = plot_record['movie']
    plot_text = plot_record['plot_excerpt']

    # Generate safe filenames by replacing special characters
    safe_title = "".join([c if c.isalnum() else "_" for c in title])
    audio_file = f"{safe_title}_audio.mp3"
    video_file = f"{safe_title}_video.mp4"
    
    # Step 1: Generate audio from the plot text
    print(f"\nProcessing '{title}': Generating audio...")
    generate_audio(plot_text, audio_file)
    
    # Step 2: Create a video using the generated audio and a background image
    print(f"Creating video for '{title}'...")
    create_video(audio_file, background_image, video_file)
    
    # Step 3: Optionally, upload the video to YouTube.
    # Uncomment the following lines to enable uploading.
    # Note: Running the YouTube upload will prompt you to authenticate.
    #
    # print(f"Uploading video for '{title}' to YouTube...")
    # upload_video(video_file, title, plot_text[:200])  # Using first 200 characters for the description

def main():
    csv_file = "D:\Code_J\Video scripting\sample.csv"          # CSV containing your plots
    background_image = "background.jpg"  # Background image for the video
    
    # Load the plot records from the CSV file
    plots = load_plots(csv_file)
    if not plots:
        print("No plots found in the CSV file!")
        return
    
    # Process each plot in the CSV
    for plot_record in plots:
        process_plot(plot_record, background_image)
        
if __name__ == "__main__":
    main()
