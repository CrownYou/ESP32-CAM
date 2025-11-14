# ESP32-CAM开发板
import socket
import network
import camera
import time
import _thread
import json
from machine import Pin, PWM, SDCard
import uos
import os

sd_loaded = wifi_connected = False

# SD 卡挂载路径（根据你的实际挂载点调整）
SD_PATH = "/sd"


# 获取 SD 卡根目录下的所有文件夹（名称为数字）
def get_numeric_dirs(path):
    return sorted([
        name for name in os.listdir(path)
        if name.isdigit() and os.stat(path + "/" + name)[0] & 0x4000  # 判断是否为目录
    ], key=int)


# 删除最小名称的文件夹
def delete_smallest_dir(path, dirs):
    smallest = min(dirs, key=int)
    full_path = path + "/" + smallest
    for file in os.listdir(full_path):
        os.remove(full_path + "/" + file)
    os.rmdir(full_path)


try:
    uos.mount(SDCard(), SD_PATH)
except Exception:
    print('未识别到SD卡')
else:
    # 将新图片存在新文件夹中，SD中最多保留4个文件夹，自动删除最老的
    dirs = get_numeric_dirs(SD_PATH)

    if len(dirs) >= 4:
        delete_smallest_dir(SD_PATH, dirs)
        dirs = get_numeric_dirs(SD_PATH)  # 更新列表

    # 新建文件夹，名字为最大数字 + 1（new_path）
    next_name = int(max(dirs, default="0")) + 1
    while True:
        new_path = SD_PATH + "/" + str(next_name)
        try:
            os.mkdir(new_path)
        except OSError as e:
            if e.args[0] == 17:  # EEXIST，目录已存在
                next_name += 1
                continue
            else:
                break  # 其他错误就退出，不保存在SD卡上了
        else:
            sd_loaded = True
            print(f"新视频将保存在{new_path}中")
            break


def connect_wifi(ssid, password, timeout=5):
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)

    if wlan.isconnected():
        wlan.disconnect()
        time.sleep(1)

    wlan.connect(ssid, password)
    print(f"尝试连接到 {ssid} ...")

    start = time.ticks_ms()
    while not wlan.isconnected():
        if time.ticks_diff(time.ticks_ms(), start) > timeout * 1000:
            print(f"连接 {ssid} 超时")
            wlan.disconnect()
            time.sleep(1)
            return False
        time.sleep(0.3)

    print(f"已连接到 {ssid}，网络配置：{wlan.ifconfig()}")
    return True


# 主网络失败后尝试备用网络
wifi_connected = connect_wifi('CrownYou', '3141592653', timeout=5)
if not wifi_connected:
    wifi_connected = connect_wifi('CMCC-EhtH', 'fxuu7433', timeout=5)

# 摄像头初始化
try:
    camera.init(0, format=camera.JPEG)
except Exception as e:
    camera.deinit()
    time.sleep(0.5)
    camera.init(0, format=camera.JPEG)

if wifi_connected:
    # 接收用户传入的参数
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(('0.0.0.0', 8080))
    print(f"正在监听...")
    msg, addr = sock.recvfrom(1024)
    msg = eval(msg.decode('utf-8'))
    target_ip = addr[0].strip("'").strip("\"")
    print(f"收到来自 {target_ip} 的消息：{msg}")

    pre_filter = msg['filter']
    pre_brightness = msg['brightness']
    pre_saturation = msg['saturation']
    pre_flip = msg['flip']
    pre_mirror = msg['mirror']
    pre_wb = msg['wb']
    pre_quality = msg['quality']
    pre_contrast = msg['contrast']
    pre_sleep_time = msg['sleep_time']
    pre_reso = msg['resolution']
    light = msg['light']
    filter = brightness = saturation = flip = mirror = wb = quality = contrast = sleep_time = reso = None

    if pre_filter == '无效果':
        camera.speffect(camera.EFFECT_NONE)
    elif pre_filter == '负效果':
        camera.speffect(camera.EFFECT_NEG)
    elif pre_filter == 'BW效果':
        camera.speffect(camera.EFFECT_BW)
    elif pre_filter == '红色效果':
        camera.speffect(camera.EFFECT_RED)
    elif pre_filter == '绿色效果':
        camera.speffect(camera.EFFECT_GREEN)
    elif pre_filter == '蓝色效果':
        camera.speffect(camera.EFFECT_BLUE)
    elif pre_filter == '复古效果':
        camera.speffect(camera.EFFECT_RETRO)
    camera.brightness(pre_brightness)
    camera.saturation(pre_saturation)
    camera.flip(pre_flip)
    camera.mirror(pre_mirror)
    # 分辨率选项如下：
    # FRAME_96X96 FRAME_QQVGA FRAME_QCIF FRAME_HQVGA FRAME_240X240
    # FRAME_QVGA FRAME_CIF FRAME_HVGA FRAME_VGA FRAME_SVGA
    # FRAME_XGA FRAME_HD FRAME_SXGA FRAME_UXGA FRAME_FHD
    # FRAME_P_HD FRAME_P_3MP FRAME_QXGA FRAME_QHD FRAME_WQXGA
    # FRAME_P_FHD FRAME_QSXGA
    if pre_reso == '96×96':
        camera.framesize(camera.FRAME_96X96)
    elif pre_reso == '160×120':
        camera.framesize(camera.FRAME_QQVGA)
    elif pre_reso == '176×144':
        camera.framesize(camera.FRAME_QCIF)
    elif pre_reso == '240×160':
        camera.framesize(camera.FRAME_HQVGA)
    elif pre_reso == '240×240':
        camera.framesize(camera.FRAME_240X240)
    elif pre_reso == '320×240':
        camera.framesize(camera.FRAME_QVGA)
    elif pre_reso == '352×288':
        camera.framesize(camera.FRAME_CIF)
    elif pre_reso == '480×320':
        camera.framesize(camera.FRAME_HVGA)
    elif pre_reso == '640×480':
        camera.framesize(camera.FRAME_VGA)
    elif pre_reso == '800×600':
        camera.framesize(camera.FRAME_SVGA)
    camera.quality(pre_quality)
    camera.contrast(pre_contrast)
    led = PWM(Pin(4))
    led.freq(70000)
    led.duty(light)
    if pre_wb == '无':
        camera.whitebalance(camera.WB_NONE)
    elif pre_wb == '晴天':
        camera.whitebalance(camera.WB_SUNNY)
    elif pre_wb == '多云':
        camera.whitebalance(camera.WB_CLOUDY)
    elif pre_wb == '办公室':
        camera.whitebalance(camera.WB_OFFICE)
    elif pre_wb == '家':
        camera.whitebalance(camera.WB_HOME)
else:  # 不联网状态下的默认设置
    camera.speffect(camera.EFFECT_NONE)
    camera.brightness(0)
    camera.saturation(0)
    camera.flip(0)
    camera.mirror(0)
    camera.framesize(camera.FRAME_QVGA)
    camera.quality(10)
    camera.contrast(0)
    camera.whitebalance(camera.WB_NONE)
    pre_sleep_time = 0.3


# 接收任务
def listen_task():
    global filter, brightness, saturation, flip, mirror, wb, quality, contrast, sleep_time, reso, light, camera, pre_filter, pre_brightness, pre_saturation, pre_flip, pre_mirror, pre_wb, pre_quality, pre_contrast, pre_sleep_time, pre_reso
    print(f"正在监听用户传入的新参数...")
    while True:
        try:
            msg, addr = sock.recvfrom(1024)
        except Exception:
            continue  # 没有数据时继续
        msg = eval(msg.decode('utf-8'))
        print(f"收到消息：{msg}")
        filter = msg['filter']
        brightness = msg['brightness']
        saturation = msg['saturation']
        flip = msg['flip']
        mirror = msg['mirror']
        wb = msg['wb']
        quality = msg['quality']
        contrast = msg['contrast']
        sleep_time = msg['sleep_time']
        reso = msg['resolution']
        light = msg['light']
        if filter != pre_filter:
            if filter == '无效果':
                camera.speffect(camera.EFFECT_NONE)
            elif filter == '负效果':
                camera.speffect(camera.EFFECT_NEG)
            elif filter == 'BW效果':
                camera.speffect(camera.EFFECT_BW)
            elif filter == '红色效果':
                camera.speffect(camera.EFFECT_RED)
            elif filter == '绿色效果':
                camera.speffect(camera.EFFECT_GREEN)
            elif filter == '蓝色效果':
                camera.speffect(camera.EFFECT_BLUE)
            elif filter == '复古效果':
                camera.speffect(camera.EFFECT_RETRO)
            pre_filter = filter
            print('滤镜调整成功')
        if brightness != pre_brightness:
            camera.brightness(brightness)
            pre_brightness = brightness
            print('亮度调整成功')
        if saturation != pre_saturation:
            camera.saturation(saturation)
            pre_saturation = saturation
            print('饱和度调整成功')
        if flip != pre_flip:
            camera.flip(flip)
            pre_flip = flip
            print('上下反转调整成功')
        if mirror != pre_mirror:
            camera.mirror(mirror)
            pre_mirror = mirror
            print('左右反转调整成功')
        if wb != pre_wb:
            if wb == '无':
                camera.whitebalance(camera.WB_NONE)
            elif wb == '晴天':
                camera.whitebalance(camera.WB_SUNNY)
            elif wb == '多云':
                camera.whitebalance(camera.WB_CLOUDY)
            elif wb == '办公室':
                camera.whitebalance(camera.WB_OFFICE)
            elif wb == '家':
                camera.whitebalance(camera.WB_HOME)
            pre_wb = wb
            print('白平衡调整成功')
        if reso != pre_reso:
            if reso == '96×96':
                camera.framesize(camera.FRAME_96X96)
            elif reso == '160×120':
                camera.framesize(camera.FRAME_QQVGA)
            elif reso == '176×144':
                camera.framesize(camera.FRAME_QCIF)
            elif reso == '240×160':
                camera.framesize(camera.FRAME_HQVGA)
            elif reso == '240×240':
                camera.framesize(camera.FRAME_240X240)
            elif reso == '320×240':
                camera.framesize(camera.FRAME_QVGA)
            elif reso == '352×288':
                camera.framesize(camera.FRAME_CIF)
            elif reso == '480×320':
                camera.framesize(camera.FRAME_HVGA)
            elif reso == '640×480':
                camera.framesize(camera.FRAME_VGA)
            elif reso == '800×600':
                camera.framesize(camera.FRAME_SVGA)
            pre_reso = reso
            print('分辨率调整成功')
        if quality != pre_quality:
            camera.quality(quality)
            pre_quality = quality
            print('质量调整成功')
        if contrast != pre_contrast:
            camera.contrast(contrast)
            pre_contrast = contrast
            print('对比度调整成功')
        if sleep_time != pre_sleep_time:
            pre_sleep_time = sleep_time
            print('帧率调整成功')
        led.duty(light)


# 发送任务（包括发送图像和将图像写入sd卡
def send_task():
    frame_number = 1
    while True:
        buf = camera.capture()  # 获取图像数据
        if wifi_connected:  # 向服务器发送图像数据
            sock.sendto(buf, (target_ip, 8080))
        if sd_loaded:  # 本地保存图像数据
            with open(f"{new_path}/{frame_number}.jpg", "wb") as f:
                f.write(buf)
            print(f'保存至{new_path}/{frame_number}.jpg')
            frame_number += 1
        if not wifi_connected and not sd_loaded:
            break
        time.sleep(pre_sleep_time)
    camera.deinit()


if wifi_connected:
    _thread.start_new_thread(listen_task, ())
send_task()


