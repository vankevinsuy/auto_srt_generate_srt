import sys,pika,os
import time
import json
import whisper
from whisper import Whisper

def write_srt_file(segments:list[dict[str, str]], sound_file_name:str)->str:
        file_name = sound_file_name.replace(".mp3", "")

        with open(f"/app/bucket/{file_name}.srt", "a") as srt:
            for index, seg in enumerate(segments, start=1):
                start = time.strftime('%H:%M:%S,000', time.gmtime(float(seg["start"])))
                end = time.strftime('%H:%M:%S,000', time.gmtime(float(seg["end"])))
                text = seg["text"].strip()

                srt.writelines([
                    f"\n{index}", 
                    f"\n{start} --> {end}",
                    f"\n{text}",
                    f"\n"
                    ])
                
        return f"{file_name}.srt"

def main(asr_model : Whisper):
    connection = pika.BlockingConnection(pika.ConnectionParameters(host=os.getenv("PUBSUB_HOSTNAME"), port=5672))
    channel = connection.channel()

    channel.queue_declare(queue='generate_srt', durable=True)

    def send_message_to_pubsub(msg:str):
        channel.basic_publish(
            exchange='',
            routing_key="new_file",
            body=msg,
            properties=pika.BasicProperties(
                delivery_mode=pika.DeliveryMode.Persistent
            ))

    def callback(ch, method, properties, body):
        print(f" [x] Received {body.decode()}")

        sound_file_path = body.decode()
        sound_file_name = sound_file_path.split('/')[-1]

        result = asr_model.transcribe(sound_file_path)

        segments = [{'start':segment['start'],'end':segment['end'], 'text':segment['text'] } for segment in result["segments"]]

        srt_file = write_srt_file(segments=segments, sound_file_name=sound_file_name)

        send_message_to_pubsub(json.dumps({"type":"srt", "file_name":f"{srt_file}"}))


    channel.basic_consume(queue='generate_srt', on_message_callback=callback, auto_ack=True)

    print(' [*] Waiting for messages. To exit press CTRL+C')
    channel.start_consuming()




def load_model()->Whisper:
    model = whisper.load_model(name=f"./whisper_models/{os.getenv('MODEL_TARGET')}.pt", in_memory=True)
    return model

if __name__ == '__main__':
    try:
        asr_model = load_model()
        main(asr_model)
    except KeyboardInterrupt:
        print('Interrupted')
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)
