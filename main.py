import requests
import subprocess
import numpy as np
import os, datetime, json, time
import pytesseract
#from display_progress import progress_for_pyrogram
from PIL import Image
from telethon import TelegramClient, events, Button

pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

Videos_Folder = r"C:/videos_folder"
BOT_NAME = "Type-Here-Any-Name"
BOT_TOKEN = " "
API_ID = " "
API_HASH = " "

LANG = "fas"
USE_CROP = False


Bot = TelegramClient(BOT_NAME, API_ID, API_HASH).start(bot_token=BOT_TOKEN)

refresh_button = [
    Button.inline(
        "Refresh List",
        data="refresh"
    )
]
@Bot.on(events.NewMessage(incoming=True, func=lambda e: e.is_private))
async def expor(event):
    if event.text:
        keyboard = []
        keyboard.append(refresh_button)
        try:
            for file in glob.glob(Videos_Folder+'/*'):
                if file.endswith(('.ts', '.mp4', '.mkv')):
                    keyboard.append(
                        [
                            Button.inline(
                                file.rsplit('/', 1)[1].replace(main, ''),
                                data=file.rsplit('/', 1)[1].replace(main, '')
                            )
                        ]
                    )
        except Exception as e:
            print(e)
            return
        keyboard.append(refresh_button)
        await event.reply("which one?", buttons=keyboard)
        return

    msg = await event.reply("Downloading..")
    #c_time = time.time()
    file_dl_path = await Bot.download_media(event.media, 'temp/')
    await msg.edit("Now Extracting..")
    video_info = subprocess.check_output(f'ffprobe -v quiet -show_streams -select_streams v:0 -of json "{file_dl_path}"', shell=True).decode()
    fields = json.loads(video_info)['streams'][0]
    duration = int(fields['duration'].split(".")[0])
    sub_count = 0
    repeated_count = 0
    last_text = " "
    duplicate = True
    lastsub_time = 0
    srt = "temp/"+event.file_name.rsplit('.', 1)[0]+".srt"
    time = duration
    intervals = [round(num, 2) for num in np.linspace(0,duration,(duration-0)*int(1/0.1)+1).tolist()]
    # Extract frames every 100 milliseconds for ocr
    for interval in intervals:
        try:
            os.system(f'ffmpeg -ss {interval} -i "{file_dl_path}" -pix_fmt yuvj422p -vframes 1 -q:v 2 -y temp/output.jpg')

            #Probably makes better recognition
            """
            import cv2  #Install opencv-python-headless
            img = cv2.imread("temp/output.jpg")
            img = cv2.cvtColor(im, cv2.COLOR_BGR2LUV)
            cv2.imwrite("temp/output.jpg", img)
            import PIL.ImageOps
            img = PIL.ImageOps.invert(img)
            img.save("temp/output.jpg")
            """

            if USE_CROP:
                img = Image.open("temp/output.jpg")
                width, height = img.size
                x1 = width // 7
                y1 = 3 * (height // 4)
                x2 = 6 * (width // 7)
                y2 = height
                crop_area = (x1, y1, x2, y2)
                cropped = img.crop(crop_area) # Learn how to change crop parameters: https://stackoverflow.com/a/39424357
                #cropped.show()
                cropped.save("temp/output.jpg")
            text = pytesseract.image_to_string("temp/output.jpg", LANG)
        except MessageEmpty:
            text = None
            pass
        except Exception as e:
            print(e)
            pass
        if not "-" in str(time):
            time -= 0.1
            try:
                await msg.edit(str(time)[:5])
            except:
                pass
        if text != None and text[:1].isspace() == False :
            # Check either text is duplicate or not
            commons = list(set(text.split()) & set(last_text.split()))
            if (len(text.split()) <= 3 and len(commons) != 0) or (len(text.split()) == 4 and len(commons) > 1):
                duplicate = True
                repeated_count += 1
            elif len(text.split()) > 4 and len(commons) > 2:
                duplicate = True
                repeated_count += 1
            else:
                duplicate = False

            # time of the last dialogue
            if duplicate == False:
                lastsub_time = interval
                
            # Write the dialogues text
            if repeated_count != 0 and duplicate == False:
                sub_count += 1
                from_time = str(datetime.datetime.fromtimestamp(interval-0.1-repeated_count*0.1)+datetime.timedelta(hours=0)).split(' ')[1][:12]
                to_time = str(datetime.datetime.fromtimestamp(interval)+datetime.timedelta(hours=0)).split(' ')[1][:12]
                from_time = f"{from_time}.000" if not "." in from_time else from_time
                to_time = f"{to_time}.000" if not "." in to_time else to_time
                f = open(srt, "a+", encoding="utf-8")
                f.write(str(sub_count) + "\n" + from_time + " --> " + to_time + "\n" + last_text + "\n\n")
                duplicate = True
                repeated_count = 0
            last_text = text

        # Write the last dialogue
        if interval == duration:
            ftime = str(datetime.datetime.fromtimestamp(lastsub_time)+datetime.timedelta(hours=0)).split(' ')[1][:12]
            ttime = str(datetime.datetime.fromtimestamp(lastsub_time+10)+datetime.timedelta(hours=0)).split(' ')[1][:12]
            ftime = f"{ftime}.000" if not "." in ftime else ftime
            ttime = f"{ttime}.000" if not "." in ttime else ttime
            f = open(srt, "a+", encoding="utf-8")
            f.write(str(sub_count+1) + "\n" + ftime + " --> " + ttime + "\n" + last_text + "\n\n")

    f.close
    try:
        await Bot.send_file(event.chat_id, file=srt)
        await msg.delete()
    except:
        pass
    os.remove(file_dl_path)
    os.remove(srt)

@Bot.on(events.CallbackQuery)
async def handler(event):
    if event.data=="refresh":
        keyboard = []
        keyboard.append(refresh_button)
        try:
            for file in glob.glob(Videos_Folder+'/*'):
                if file.endswith(('.ts', '.mp4', '.mkv')):
                    keyboard.append(
                        [
                            Button.inline(
                                file.rsplit('/', 1)[1].replace(main, ''),
                                data=file.rsplit('/', 1)[1].replace(main, '')
                            )
                        ]
                    )
        except Exception as e:
            print(e)
            return
        keyboard.append(refresh_button)
        await event.edit("which one?", buttons=keyboard)
        return

    msg = await Bot.send_message(event.chat_id, "downloading..")
    file_dl_path = VideosFolder + "/" + event.data
    video_info = subprocess.check_output(f'ffprobe -v quiet -show_streams -select_streams v:0 -of json "{file_dl_path}"', shell=True).decode()
    fields = json.loads(video_info)['streams'][0]
    duration = int(fields['duration'].split(".")[0])
    sub_count = 0
    repeated_count = 0
    last_text = " "
    duplicate = True
    lastsub_time = 0
    srt = "temp/"+event.data.rsplit('.', 1)[0]+".srt"
    time = duration
    intervals = [round(num, 2) for num in np.linspace(0,duration,(duration-0)*int(1/0.1)+1).tolist()]
    # Extract frames every 100 milliseconds for ocr
    for interval in intervals:
        try:
            os.system(f'ffmpeg -ss {interval} -i "{file_dl_path}" -pix_fmt yuvj422p -vframes 1 -q:v 2 -y temp/output.jpg')

            #Probably makes better recognition
            """
            import cv2  #Install opencv-python-headless
            img = cv2.imread("temp/output.jpg")
            img = cv2.cvtColor(im, cv2.COLOR_BGR2LUV)
            cv2.imwrite("temp/output.jpg", img)
            import PIL.ImageOps
            img = PIL.ImageOps.invert(img)
            img.save("temp/output.jpg")
            """

            if USE_CROP:
                img = Image.open("temp/output.jpg")
                width, height = img.size
                x1 = width // 7
                y1 = 3 * (height // 4)
                x2 = 6 * (width // 7)
                y2 = height
                crop_area = (x1, y1, x2, y2)
                cropped = img.crop(crop_area) # Learn how to change crop parameters: https://stackoverflow.com/a/39424357
                #cropped.show()
                cropped.save("temp/output.jpg")
            text = pytesseract.image_to_string("temp/output.jpg", LANG)
        except MessageEmpty:
            text = None
            pass
        except Exception as e:
            print(e)
            pass
        if not "-" in str(time):
            time -= 0.1
            try:
                await msg.edit(str(time)[:5])
            except:
                pass
        if text != None and text[:1].isspace() == False :
            # Check either text is duplicate or not
            commons = list(set(text.split()) & set(last_text.split()))
            if (len(text.split()) <= 3 and len(commons) != 0) or (len(text.split()) == 4 and len(commons) > 1):
                duplicate = True
                repeated_count += 1
            elif len(text.split()) > 4 and len(commons) > 2:
                duplicate = True
                repeated_count += 1
            else:
                duplicate = False

            # time of the last dialogue
            if duplicate == False:
                lastsub_time = interval
                
            # Write the dialogues text
            if repeated_count != 0 and duplicate == False:
                sub_count += 1
                from_time = str(datetime.datetime.fromtimestamp(interval-0.1-repeated_count*0.1)+datetime.timedelta(hours=0)).split(' ')[1][:12]
                to_time = str(datetime.datetime.fromtimestamp(interval)+datetime.timedelta(hours=0)).split(' ')[1][:12]
                from_time = f"{from_time}.000" if not "." in from_time else from_time
                to_time = f"{to_time}.000" if not "." in to_time else to_time
                f = open(srt, "a+", encoding="utf-8")
                f.write(str(sub_count) + "\n" + from_time + " --> " + to_time + "\n" + last_text + "\n\n")
                duplicate = True
                repeated_count = 0
            last_text = text

        # Write the last dialogue
        if interval == duration:
            ftime = str(datetime.datetime.fromtimestamp(lastsub_time)+datetime.timedelta(hours=0)).split(' ')[1][:12]
            ttime = str(datetime.datetime.fromtimestamp(lastsub_time+10)+datetime.timedelta(hours=0)).split(' ')[1][:12]
            ftime = f"{ftime}.000" if not "." in ftime else ftime
            ttime = f"{ttime}.000" if not "." in ttime else ttime
            f = open(srt, "a+", encoding="utf-8")
            f.write(str(sub_count+1) + "\n" + ftime + " --> " + ttime + "\n" + last_text + "\n\n")

    f.close
    try:
        await Bot.send_file(event.chat_id, file=srt)
    except:
        pass
    try:
        os.remove(file_dl_path)
        os.remove(srt)
    except:
        pass
    await msg.delete()


Bot.run_until_disconnected()
