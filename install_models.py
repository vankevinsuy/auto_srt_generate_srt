import whisper
import os 

model_folder_exist = os.path.exists("whisper_models")
if not model_folder_exist : 
    os.mkdir("whisper_models")


whisper.load_model(os.getenv('MODEL_TARGET'), download_root="./whisper_models")