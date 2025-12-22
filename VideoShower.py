# 用于播放ESP32-CAM保存的图片的播放器
# 打包代码：pyinstaller VideoShower.py --onefile -w
import tkinter as tk
from tkinter import filedialog
from PIL import Image, ImageTk, ImageOps
import time
from pathlib import Path
import threading

window = tk.Tk()
window.title("图片播放器")
mid_font = ('Noto Sans Mono', 10)
canvas = tk.Canvas(window, width=800, height=600, bg='black')
canvas.pack()
current_index = 1
image_nums = 0
degree = 270
paused_flag = False
frame_rate = 10
mirror = False
new_video_selected = False


def run_as_thread(func):  # 装饰器，让函数运行时另开一个线程
    def wrapper(*args, **kwargs):
        t = threading.Thread(target=func, args=args, kwargs=kwargs)
        t.setDaemon(True)
        t.start()

    return wrapper


@run_as_thread
def load_images():
    global current_index, image_nums, new_video_selected, percent

    def show_image():
        global current_index, percent, new_video_selected
        new_video_selected = False
        while not new_video_selected:
            img_path = f"{folder}/{current_index}.jpg"
            print(img_path)
            try:
                img = Image.open(img_path)
                img = img.rotate(degree)
                if mirror:
                    img = ImageOps.mirror(img)
                img = img.resize((800, 600))
                photo = ImageTk.PhotoImage(img)
            except Exception:
                label1.config(text=f'当前帧数：{current_index} / {image_nums}    进度条：', font=mid_font)
                percent.set(int(current_index / image_nums * 100))
                current_index = (1 + current_index) % image_nums
                continue
            canvas.delete("all")
            canvas.create_image(0, 0, image=photo, anchor=tk.NW)
            label1.config(text=f'当前帧数：{current_index} / {image_nums}    进度条：', font=mid_font)
            percent.set(int(current_index / image_nums * 100))
            current_index = (1 + current_index) % image_nums
            window.update()
            while paused_flag and not new_video_selected:
                time.sleep(0.2)
                current_index = int(image_nums * percent.get() / 100) if percent.get() != 0 else 1
            time.sleep(1 / frame_rate)

    new_video_selected = True
    current_index = 1
    folder = filedialog.askdirectory(title="选择图片文件夹")
    if not folder:
        return 0

    percent.set(0)
    label1.config(text='当前帧数：0 / 0    进度条：')
    label3.config(text=f'当前播放：{folder}')
    image_nums = sum(1 for f in Path(folder).iterdir() if f.is_file())

    if image_nums:
        show_image()


@run_as_thread
def change_progress(*args):
    global paused_flag
    if not paused_flag:
        paused_flag = True
        time.sleep(0.5)
        paused_flag = False


def pause(*args):
    global paused_flag
    paused_flag = not paused_flag


def acc():
    global frame_rate
    if frame_rate <= 9:
        frame_rate += 1
    elif frame_rate <= 48:
        frame_rate += 2
    label2.config(text='帧率：{:>2}帧/秒'.format(frame_rate))


def dec():
    global frame_rate
    if frame_rate >= 12:
        frame_rate -= 2
    elif frame_rate >= 2:
        frame_rate -= 1
    label2.config(text='帧率：{:>2}帧/秒'.format(frame_rate))


def rot():
    global degree
    degree = (degree + 90) % 360


def mir():
    global mirror
    mirror = not mirror


label3 = tk.Label(window, text='当前播放：', font=mid_font)
label3.pack()
frm2 = tk.Frame(window)
frm2.pack()
label1 = tk.Label(frm2, text='当前帧数：0 / 0    进度条：', font=mid_font)
label1.grid(row=1, column=1)
percent = tk.IntVar()
percent.set(0)
scale = tk.Scale(frm2, from_=0, to=100, orient=tk.HORIZONTAL, command=change_progress, length=450, tickinterval=20, resolution=1, showvalue=1, variable=percent)
scale.grid(row=1, column=2)

frm1 = tk.Frame(window)
frm1.pack()
load_button = tk.Button(frm1, text="选择图片文件夹", command=load_images, font=mid_font)
load_button.grid(row=1, column=1, padx=10, pady=10)
rot_button = tk.Button(frm1, text='左旋90度', command=rot, font=mid_font)
rot_button.grid(row=1, column=2, padx=10, pady=10)
mir_button = tk.Button(frm1, text='镜像翻转', command=mir, font=mid_font)
mir_button.grid(row=1, column=3, padx=10, pady=10)
pause_button = tk.Button(frm1, text='暂停/播放', command=pause, font=mid_font)
pause_button.grid(row=1, column=4, padx=10, pady=10)
window.bind('<space>', pause)
acc_button = tk.Button(frm1, text='加速', command=acc, font=mid_font)
acc_button.grid(row=1, column=5, padx=10, pady=10)
dec_button = tk.Button(frm1, text='减速', command=dec, font=mid_font)
dec_button.grid(row=1, column=6, padx=10, pady=10)
label2 = tk.Label(frm1, text='帧率：{:>2}帧/秒'.format(frame_rate), font=mid_font)
label2.grid(row=1, column=7, padx=10, pady=10)
window.mainloop()
