import fal_client

def on_queue_update(update):
    if isinstance(update, fal_client.InProgress):
        for log in update.logs:
           print(log["message"])

result = fal_client.subscribe(
    "fal-ai/kling-video/v2.6/standard/motion-control",
    arguments={
        "prompt": "Realistic webcam-style close-up of a man seated on a chair, looking into the camera and speaking calmly.",
        "image_url": "blob:https://fal.ai/1fd247d8-27f5-4766-b31c-1ce95e48debd",
        "video_url": "blob:https://fal.ai/afd4d361-48c0-417d-89e5-a0979f1e77bc",
        "keep_original_sound": True,
        "character_orientation": "video"
    },
    with_logs=True,
    on_queue_update=on_queue_update,
)
print(result)