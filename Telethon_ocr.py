import requests
import subprocess
import os, datetime, json, time, math, shutil
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


Bot = TelegramClient(BOT_NAME, API_ID, API_HASH).start(bot_token=BOT_TOKEN)

refresh_button = [
    Button.inline(
        "Refresh List",
        data="refresh"
    )
]
@Bot.on(events.NewMessage(incoming=True, func=lambda e: e.is_private))
async def expor(event):
    if event.text and "cancel" in event.text:
        try:
            shutil.rmtree("temp/")
        except:
            await event.reply("can't cancel. maybe there wasn't any progress in process.")
        else:
            await event.reply("canceled successfully.")
        return
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
    try:
        shutil.rmtree("temp/")
    except:
        pass
    time.sleep(2)
    try:
        os.makedirs("temp/")
    except:
        pass
    msg = await event.reply("`Downloading..`")
    #c_time = time.time()
    file_dl_path = await Bot.download_media(event.media, 'temp/')
    await msg.edit("`Now Extracting..`")
    video_info = subprocess.check_output(f'ffprobe -v quiet -show_streams -select_streams v:0 -of json "{file_dl_path}"', shell=True).decode()
    fields = json.loads(video_info)['streams'][0]
    duration = int(fields['duration'].split(".")[0])
    sub_count = 0
    repeated_count = 0
    last_text = " "
    duplicate = True
    lastsub_time = 0
    srt = "temp/"+event.file_name.rsplit('.', 1)[0]+".srt"
    intervals = get_intervals(duration)
    time_to_finish = duration
    # Extract frames every 100 milliseconds for ocr
    for interval in intervals:
        command = os.system(f'ffmpeg -ss {ms_to_time(interval)} -i "{file_dl_path}" -pix_fmt yuvj422p -vframes 1 -q:v 2 -y temp/output.jpg')
        if command != 0:
            return await msg.delete()
        try:
            im = Image.open("temp/output.jpg")
            text = pytesseract.image_to_string(im, LANG)
        except:
            text = None
            pass
        if time_to_finish > 0:
            time_to_finish -= 0.1
            percentage = (duration - time_to_finish) * 100 / duration
            progress = "[{0}{1}]\nPercentage : {2}%\n\n".format(
                ''.join(["●" for i in range(math.floor(percentage / 5))]),
                ''.join(["○" for i in range(20 - math.floor(percentage / 5))]),
                round(percentage, 2)
            )
            try:
                await msg.edit(progress + "`For cancel progress, send` /cancel")
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
                from_time = ms_to_time(interval-100-repeated_count*100)
                to_time = ms_to_time(interval)
                f = open("temp/srt.srt", "a+", encoding="utf-8")
                f.write(str(sub_count) + "\n" + from_time + " --> " + to_time + "\n" + last_text + "\n\n")
                duplicate = True
                repeated_count = 0
            last_text = text

        # Write the last dialogue
        if interval/1000 == duration:
            ftime = ms_to_time(lastsub_time)
            ttime = ms_to_time(lastsub_time+10000)
            f = open("temp/srt.srt", "a+", encoding="utf-8")
            f.write(str(sub_count+1) + "\n" + ftime + " --> " + ttime + "\n" + last_text + "\n\n")

    f.close
    try:
        await Bot.send_file(event.chat_id, file=srt)
        await msg.delete()
    except:
        pass

@Bot.on(events.CallbackQuery)
async def handler(event):
    if event.data==b"refresh":
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
    try:
        shutil.rmtree("temp/")
    except:
        pass
    time.sleep(2)
    try:
        os.makedirs("temp/")
    except:
        pass
    msg = await Bot.send_message(event.chat_id, "`downloading..`")
    file_dl_path = VideosFolder + "/" + event.data.decode('utf-8')
    video_info = subprocess.check_output(f'ffprobe -v quiet -show_streams -select_streams v:0 -of json "{file_dl_path}"', shell=True).decode()
    fields = json.loads(video_info)['streams'][0]
    duration = int(fields['duration'].split(".")[0])
    sub_count = 0
    repeated_count = 0
    last_text = " "
    duplicate = True
    lastsub_time = 0
    srt = "temp/"+event.data.decode('utf-8').rsplit('.', 1)[0]+".srt"
    intervals = get_intervals(duration)
    time_to_finish = duration
    # Extract frames every 100 milliseconds for ocr
    for interval in intervals:
        command = os.system(f'ffmpeg -ss {ms_to_time(interval)} -i "{file_dl_path}" -pix_fmt yuvj422p -vframes 1 -q:v 2 -y temp/output.jpg')
        if command != 0:
            return await msg.delete()
        try:
            im = Image.open("temp/output.jpg")
            text = pytesseract.image_to_string(im, LANG)
        except:
            text = None
            pass
        if time_to_finish > 0:
            time_to_finish -= 0.1
            percentage = (duration - time_to_finish) * 100 / duration
            progress = "[{0}{1}]\nPercentage : {2}%\n\n".format(
                ''.join(["●" for i in range(math.floor(percentage / 5))]),
                ''.join(["○" for i in range(20 - math.floor(percentage / 5))]),
                round(percentage, 2)
            )
            try:
                await msg.edit(progress + "`For cancel progress, send` /cancel")
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
                from_time = ms_to_time(interval-100-repeated_count*100)
                to_time = ms_to_time(interval)
                f = open("temp/srt.srt", "a+", encoding="utf-8")
                f.write(str(sub_count) + "\n" + from_time + " --> " + to_time + "\n" + last_text + "\n\n")
                duplicate = True
                repeated_count = 0
            last_text = text

        # Write the last dialogue
        if interval/1000 == duration:
            ftime = ms_to_time(lastsub_time)
            ttime = ms_to_time(lastsub_time+10000)
            f = open("temp/srt.srt", "a+", encoding="utf-8")
            f.write(str(sub_count+1) + "\n" + ftime + " --> " + ttime + "\n" + last_text + "\n\n")

    f.close
    try:
        await Bot.send_file(event.chat_id, file=srt)
    except:
        pass
    await msg.delete()


def get_intervals(duration):
    intervals = []
    for i in range(0, duration+1):
        for x in range(0, 10):
            interval = (i+(x/10))*1000
            intervals.append(interval)
    return intervals


def ms_to_time(interval):
    ms2time = "0" + str(datetime.timedelta(milliseconds=interval))[:11]
    ms2time = f"{ms2time}.000" if not "." in ms2time else ms2time
    return ms2time


Bot.run_until_disconnected()
