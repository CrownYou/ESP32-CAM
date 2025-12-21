# 电脑或手机端监控及遥控程序
import json
import os.path
import tkinter as tk
from tkinter import ttk
import socket
import io
from PIL import Image, ImageTk
import threading
from datetime import datetime
from tkinter import messagebox

window = tk.Tk()
mid_font = ('Noto Sans Mono', 10)
height = window.winfo_screenheight()
width = window.winfo_screenwidth()
window.title("DashCam")
colors = ['mediumblue', 'hotpink', 'darkgreen', 'red', 'orange', 'darkcyan']
ind = rotate_degree = config = 0
if os.path.exists("config.json"):
    with open("config.json", "r", encoding="utf-8") as f:
        config = json.load(f)
    rotate_degree = config["旋转角度"]
# 创建样式对象
style = ttk.Style()
style.configure("Custom.TCombobox", font=mid_font)


def run_as_thread(func):  # 装饰器，让函数运行时另开一个线程
    def wrapper(*args, **kwargs):
        t = threading.Thread(target=func, args=args, kwargs=kwargs)
        t.setDaemon(True)
        t.start()

    return wrapper


def get_time():
    now = datetime.now()
    formatted_time = now.strftime("%Y-%m-%d %H:%M:%S")
    return formatted_time


def send_udp_message(message, target_ip, target_port):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.sendto(message.encode('utf-8'), (target_ip, target_port))
    sock.close()


def send_msg():
    global ind
    ind = (1 + ind) % 6
    lf1_r_button1.config(fg=colors[ind])
    frame_rate = lf1_r_entry1.get()
    if not frame_rate.isdigit() or int(frame_rate) <= 0:
        messagebox.showwarning("Warning", "Frame rate should be a positive integer")
        return 0
    msg = {'time': get_time(),
           'filter': spe_type.get(),
           'brightness': bri.get(),
           'saturation': sat.get(),
           'flip': flip.get(),
           'mirror': mirror.get(),
           'wb': wb_type.get(),
           'quality': int(-0.53 * qua.get() + 63),
           'contrast': con.get(),
           'sleep_time': round(1 / int(frame_rate), 2),
           'resolution': reso.get(),
           'light': int(light.get() / 20 * 1023)}
    target_ip = lf1_l_entry1.get()
    try:
        send_udp_message(str(msg), target_ip, 8080)
    except Exception:
        messagebox.showerror('Failed to send message',
                             f'Failed to send message to {target_ip},\ncheck ip and try again.')
        return 0
    # 把当前的所有设置保存起来，下次启动程序的时候使用
    config = {"滤镜": spe_type.get(),
              "亮度": bri.get(),
              "饱和度": sat.get(),
              "上下反转": flip.get(),
              "左右反转": mirror.get(),
              "行车记录仪ip": target_ip,
              "白平衡": wb_type.get(),
              "质量": qua.get(),
              "对比度": con.get(),
              "帧率": frame_rate,
              "旋转角度": rotate_degree,
              "分辨率": reso.get(),
              "补光灯": light.get()}
    with open("config.json", "w", encoding="utf-8") as f:
        json.dump(config, f, ensure_ascii=False, indent=4)


def rotate():
    global rotate_degree, ind
    ind = (ind + 1) % 6
    lf1_r_button2.config(fg=colors[ind])
    rotate_degree = (90 + rotate_degree) % 360


'''监控画面'''
labelframe2 = tk.LabelFrame(window, text='行车记录仪监控画面', height=height * 17 / 30, width=width, font=mid_font)
labelframe2.pack()
labelframe2.pack_propagate(0)
canvas = tk.Canvas(labelframe2)
canvas.pack(fill=tk.BOTH, expand=True)

'''调节参数'''
labelframe1 = tk.LabelFrame(window, text='调节参数（关闭VPN）', height=height * 13 / 30, width=width, font=mid_font)
labelframe1.pack()
labelframe1.pack_propagate(0)  # 使组件大小不变
'''---左---'''
lf1_l_frm = tk.Frame(labelframe1)
lf1_l_frm.pack(side=tk.LEFT, padx=10)

lf1_l_frm1 = tk.Frame(lf1_l_frm)
lf1_l_frm1.pack()
lf1_l_label1 = tk.Label(lf1_l_frm1, text='滤镜  ：', font=mid_font)
lf1_l_label1.pack(side=tk.LEFT)
spe_type = ttk.Combobox(lf1_l_frm1,
                        values=['无效果', '负效果', 'BW效果', '红色效果', '绿色效果', '蓝色效果', '复古效果'],
                        style="Custom.TCombobox", width=8, state="readonly")
if config:
    spe_type.set(config['滤镜'])
else:
    spe_type.set('无效果')
spe_type.pack(side=tk.RIGHT)

lf1_l_frm2 = tk.Frame(lf1_l_frm)
lf1_l_frm2.pack()
lf1_l_label2 = tk.Label(lf1_l_frm2, text='亮度  ：', font=mid_font)
lf1_l_label2.pack(side=tk.LEFT)
bri = tk.IntVar()
if config:
    bri.set(config['亮度'])
else:
    bri.set(0)
bri_scale = tk.Scale(lf1_l_frm2, from_=-2, to=2, orient=tk.HORIZONTAL, length=250, tickinterval=1, resolution=1,
                     showvalue=1, variable=bri)
bri_scale.pack(side=tk.RIGHT)

lf1_l_frm3 = tk.Frame(lf1_l_frm)
lf1_l_frm3.pack()
lf1_l_label3 = tk.Label(lf1_l_frm3, text='饱和度：', font=mid_font)
lf1_l_label3.pack(side=tk.LEFT)
sat = tk.IntVar()
if config:
    sat.set(config['饱和度'])
else:
    sat.set(0)
sat_scale = tk.Scale(lf1_l_frm3, from_=-2, to=2, orient=tk.HORIZONTAL, length=250, tickinterval=1, resolution=1,
                     showvalue=1, variable=sat)
sat_scale.pack(side=tk.RIGHT)

lf1_l_frm6 = tk.Frame(lf1_l_frm)
lf1_l_frm6.pack()
lf1_l_label5 = tk.Label(lf1_l_frm6, text='补光灯：', font=mid_font)
lf1_l_label5.pack(side=tk.LEFT)
light = tk.IntVar()
if config:
    light.set(config['补光灯'])
else:
    light.set(0)
light_scale = tk.Scale(lf1_l_frm6, from_=0, to=20, orient=tk.HORIZONTAL, length=250, tickinterval=10, resolution=1,
                     showvalue=1, variable=light)
light_scale.pack(side=tk.RIGHT)

lf1_l_frm4 = tk.Frame(lf1_l_frm)
lf1_l_frm4.pack()
lf1_l_label4 = tk.Label(lf1_l_frm4, text='输入行车记录仪的ip：', font=mid_font)
lf1_l_label4.pack()
lf1_l_entry1 = tk.Entry(lf1_l_frm4, font=mid_font, width=15)
lf1_l_entry1.pack()
if config:
    lf1_l_entry1.insert(tk.END, config['行车记录仪ip'])
else:
    lf1_l_entry1.insert(tk.END, '192.168.1.')

'''---右---'''
lf1_r_frm = tk.Frame(labelframe1)
lf1_r_frm.pack(side=tk.RIGHT, padx=10)

lf1_r_frm1 = tk.Frame(lf1_r_frm)
lf1_r_frm1.pack()
lf1_r_label1 = tk.Label(lf1_r_frm1, text='白平衡：', font=mid_font)
lf1_r_label1.pack(side=tk.LEFT)
wb_type = ttk.Combobox(lf1_r_frm1, values=['无', '晴天', '多云', '办公室', '家'], style="Custom.TCombobox", width=8,
                       state="readonly")
if config:
    wb_type.set(config['白平衡'])
else:
    wb_type.set('无')
wb_type.pack(side=tk.RIGHT)

lf1_r_frm2 = tk.Frame(lf1_r_frm)
lf1_r_frm2.pack()
lf1_r_label2 = tk.Label(lf1_r_frm2, text='质量  ：', font=mid_font)
lf1_r_label2.pack(side=tk.LEFT)
qua = tk.IntVar()
if config:
    qua.set(config['质量'])
else:
    qua.set(50)
qua_scale = tk.Scale(lf1_r_frm2, from_=0, to=100, orient=tk.HORIZONTAL, length=250, tickinterval=50, resolution=1,
                     showvalue=1, variable=qua)
qua_scale.pack(side=tk.RIGHT)

lf1_r_frm3 = tk.Frame(lf1_r_frm)
lf1_r_frm3.pack()
lf1_r_label3 = tk.Label(lf1_r_frm3, text='对比度：', font=mid_font)
lf1_r_label3.pack(side=tk.LEFT)
con = tk.IntVar()
if config:
    con.set(config['对比度'])
else:
    con.set(0)
con_scale = tk.Scale(lf1_r_frm3, from_=-2, to=2, orient=tk.HORIZONTAL, length=250, tickinterval=1, resolution=1,
                     showvalue=1, variable=con)
con_scale.pack(side=tk.RIGHT)

lf1_r_frm5 = tk.Frame(lf1_r_frm)
lf1_r_frm5.pack()
lf1_r_label4 = tk.Label(lf1_r_frm5, text='帧率：', font=mid_font)
lf1_r_label4.pack(side=tk.LEFT)
lf1_r_entry1 = tk.Entry(lf1_r_frm5, width=5, font=mid_font)
lf1_r_entry1.pack(side=tk.RIGHT)
if config:
    lf1_r_entry1.insert(tk.END, config['帧率'])
else:
    lf1_r_entry1.insert(tk.END, '10')

lf1_r_frm7 = tk.Frame(lf1_r_frm)
lf1_r_frm7.pack()
flip = tk.IntVar()
if config:
    flip.set(config['上下反转'])
else:
    flip.set(0)
flip_switch = tk.Checkbutton(lf1_r_frm7, variable=flip, onvalue=1, offvalue=0, text='上下翻', font=mid_font)
flip_switch.pack(side=tk.LEFT)
mirror = tk.IntVar()
if config:
    mirror.set(config['左右反转'])
else:
    mirror.set(0)
mirror_switch = tk.Checkbutton(lf1_r_frm7, variable=mirror, onvalue=1, offvalue=0, text='左右翻', font=mid_font)
mirror_switch.pack(side=tk.RIGHT)

lf1_r_frm6 = tk.Frame(lf1_r_frm)
lf1_r_frm6.pack()
lf1_r_label5 = tk.Label(lf1_r_frm6, text='分辨率：', font=mid_font)
lf1_r_label5.pack(side=tk.LEFT)
reso = ttk.Combobox(lf1_r_frm6, values=['96×96', '160×120', '176×144', '240×160', '240×240', '320×240', '352×288', '480×320', '640×480', '800×600'], style="Custom.TCombobox", width=8,
                       state="readonly")
if config:
    reso.set(config['分辨率'])
else:
    reso.set('240×160')
reso.pack(side=tk.RIGHT)

lf1_r_frm4 = tk.Frame(lf1_r_frm)
lf1_r_frm4.pack()
lf1_r_button1 = tk.Button(lf1_r_frm, text='确定', font=mid_font, command=send_msg, fg=colors[ind])
lf1_r_button1.pack(side=tk.RIGHT)
lf1_r_button2 = tk.Button(lf1_r_frm, text='左旋90度', font=mid_font, command=rotate, fg=colors[ind])
lf1_r_button2.pack(side=tk.LEFT)


@run_as_thread
def show_video():
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
        # s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind(("0.0.0.0", 8080))  # 监听所有 IP 的 8080 端口
        print("UDP 服务器已启动，等待数据...")
        while True:
            data, IP = s.recvfrom(100000)
            print('收到画面')
            image = Image.open(io.BytesIO(data))
            image = image.rotate(rotate_degree, expand=True)
            original_width, original_height = image.size
            scale_w = width / original_width
            scale_h = height * 17 / 30 / original_height
            scale = min(scale_w, scale_h)
            new_width = int(original_width * scale)
            new_height = int(original_height * scale)
            image = image.resize((new_width, new_height))
            tk_image = ImageTk.PhotoImage(image)
            canvas.delete("all")
            canvas.create_image(0, 0, anchor='nw', image=tk_image)
            window.update()


show_video()

window.mainloop()
