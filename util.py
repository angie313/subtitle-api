import os
from fastapi import HTTPException
import httpx
from googleapiclient.discovery import build


# Fetch subtitle from cloud function
def get_subtitle(video_id, user_prompt="", system_prompt=""):
    url = os.environ.get('CLOUD_FUNCTION_URL')
    # Check if the environment variable exists
    if url:
        request_body = {
            "video_id": video_id,
            "user_prompt": user_prompt,
            "system_prompt": system_prompt
        }

        # Use httpx to make an HTTP POST request to the external API
        with httpx.Client(timeout=90) as client:
            try:
                response = client.post(url, json=request_body)
            except httpx.RequestError as exc:
                print(f"An error occurred while requesting {exc.request.url!r}.")


        # Check if the response status code is 200 (OK) or 201 (Created)
        if response.status_code in [200, 201]:
            response_data = response.json()  # Parse the JSON response
            return response_data['result']
        else:
            # If the API call was not successful, raise an HTTPException
            raise HTTPException(status_code=response.status_code, detail="Failed to fetch subtitle from cloud function")
    else:
        print("Cloud function URL not found!")
        raise HTTPException(status_code=500, detail="Issue locating cloud function URL")

# Get video meta data from Youtube API
def request_video_info(video_id):

    key = os.environ.get('YOUTUBE_API_KEY')
    # Check if the environment variable exists
    if key:
        # Build the service object
        youtube = build('youtube', 'v3', developerKey=key)
    
        # Call the videos.list method to retrieve the video resource
        request = youtube.videos().list(
            part="snippet",
            id=video_id
        )
        response = request.execute()

        if 'items' in response and len(response['items']) > 0:
            return response['items'][0]['snippet']
        else:
            print("Video Not Found.")
        
    else:
        print('YOUTUBE_API_KEY is not found.')
    
    return None