import cv2
import os
import re
import shutil
import subprocess

def numerical_sort(value):
    numbers = re.findall(r'\d+', value)
    return int(numbers[0]) if numbers else 0

def splitframe(videopath, output_dir):
    """
    Videoyu karelere böler ve belirtilen dizine kaydeder.

    Args:
        videopath (str): Bölünecek video dosyasının yolu.
        output_dir (str): Karelerin kaydedileceği dizin.
    """

    if os.path.exists(output_dir):
        shutil.rmtree(output_dir)
    os.makedirs(output_dir)

    capture = cv2.VideoCapture(videopath)
    frameNr = 0
    while True:
        success, frame = capture.read()
        if success:
            cv2.imwrite(os.path.join(output_dir, f'frame_{frameNr}.png'), frame)
        else:
            break
        frameNr += 1
    capture.release()
    sound_file = os.path.join(output_dir, "audio.wav")
    try:
        subprocess.run(['ffmpeg', '-i', videopath, '-vn', '-acodec', 'pcm_s16le', sound_file], check=True)
        print(f"Ses dosyası oluşturuldu: {sound_file}")
    except Exception as e:
        print(f"Ses dosyası oluşturulamadı: {e}")



def generate_video(video_name, image_folder, fps, boyut):
    """
    Verilen karelerden bir video oluşturur.

    Args:
        video_name (str): Oluşturulacak video dosyasının adı.
        image_folder (str): Karelerin bulunduğu dizin.
        fps (int): Oluşturulacak videonun kare hızı.
        boyut (tuple): Oluşturulacak videonun boyutu (genişlik, yükseklik).
    """
    images = sorted([img for img in os.listdir(image_folder) if img.endswith((".png"))], key=numerical_sort)

    fourcc = cv2.VideoWriter_fourcc(*'FFV1')
    video_writer = cv2.VideoWriter(video_name, fourcc, fps, boyut)

    for image in images:
        frame = cv2.imread(os.path.join(image_folder, image))
        video_writer.write(frame)

    video_writer.release()
    cv2.destroyAllWindows()
    print(f"Video oluşturuldu: {video_name}")

    sound_file = os.path.join(image_folder, "audio.wav")
    if os.path.exists(sound_file):
        try:
            subprocess.run(['ffmpeg', '-i', video_name, '-i', sound_file, '-c:v', 'copy', '-c:a', 'aac', '-y', 'output_with_sound.avi'], check=True)
            print(f"Video ve ses birleştirildi: output_with_sound.avi")
            os.remove(video_name)
            os.rename("output_with_sound.avi", video_name)
        except Exception as e:
            print(f"Ses eklenirken hata oluştu: {e}")

    else:
        print("Uyarı: Ses dosyası bulunamadı, video ses olmadan kaydedildi.")

def get_video_boyut(video_path):
    """
    Bir videonun boyutlarını (genişlik, yükseklik) döndürür.

    Args:
        video_path (str): Video dosyasının yolu.

    Returns:
        tuple: (genişlik, yükseklik)
    """
    capture = cv2.VideoCapture(video_path)
    genislik = int(capture.get(cv2.CAP_PROP_FRAME_WIDTH))
    yukseklik = int(capture.get(cv2.CAP_PROP_FRAME_HEIGHT))
    capture.release()
    return (genislik, yukseklik)

def get_video_fps(video_path):
    """
    Bir videonun kare hızını (FPS) döndürür.

    Args:
        video_path (str): Video dosyasının yolu.

    Returns:
        int: Kare hızı.
    """
    capture = cv2.VideoCapture(video_path)
    fps = int(capture.get(cv2.CAP_PROP_FPS))
    capture.release()
    return fps