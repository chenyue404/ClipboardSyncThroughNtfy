#!/usr/bin/python3
import clipboard
import time
import websocket
import json
import threading
import requests
import os

CLIENTNAME = ""
URL = ""
TOKEN = ""

file_path = "config.json"
config = {}
if not os.path.exists(file_path):
    with open(file_path, "w") as f:
            json.dump({
                "clientName": "",
                "url": "",
                "token": ""
            }, f)
if os.path.exists(file_path):
    with open(file_path, "r") as f:
        config = json.load(f)
CLIENTNAME = config["clientName"]
URL = config["url"]
TOKEN = config["token"]
if len(CLIENTNAME) == 0:
    user_input = ""
    while len(user_input) == 0:
        user_input = input("Please input your client name\n")
    config["clientName"] = user_input
    CLIENTNAME = user_input
if len(URL) == 0:
    user_input = ""
    while len(user_input) == 0:
        user_input = input("Please input your url, like: ntfy.sh/topic\n")
    config["url"] = user_input
    URL = user_input
if len(TOKEN) == 0:
    user_input = ""
    while len(user_input) == 0:
        user_input = input("Please enter token, if not, enter \"-\"\n")
    config["token"] = user_input
    TOKEN = user_input
with open(file_path, "w") as f:
    json.dump(config, f, indent=4)

def on_message(ws, message):
    print(message)
    jo = json.loads(message)
    title = jo.get("title")
    msg = jo.get("message")
    if msg is None:
        return 
    if title != CLIENTNAME:
        print("收到：%s" % (msg))
        clipboard.copy(msg)

def on_error(ws, error):
    print(error)

def on_close(ws, close_status_code, close_msg):
    print("### closed ###")

def on_open(ws):
    print("Opened connection")

print("wss://%s/ws" % (URL))
# 创建websocket连接
ws = websocket.WebSocketApp("wss://%s/ws" % (URL),
                            header={
                                "Authorization": TOKEN if TOKEN != "-" else ""
                            },
                             on_message=on_message,
                             on_error=on_error,
                             on_close=on_close,
                             on_open=on_open)
wsThread = threading.Thread(target=ws.run_forever, daemon=True)
wsThread.start()

def send_clipboard(msg):
    requests.post("https://%s" % (URL),
                  data=msg,
                  headers={
                    "Authorization": TOKEN if TOKEN != "-" else "",
                    "Title": CLIENTNAME
                    })

def listen_clipboard():
    oldText = clipboard.paste()
    # 创建一个循环，不断监视剪贴板
    while True:
        # 读取剪贴板的内容
        text = clipboard.paste()
    
        # 如果剪贴板有内容，则打印内容
        if (text != oldText):
            print("剪贴板变化：%s" % (text))
            oldText = text
            send_clipboard(text)
    
        # 延迟1秒钟
        time.sleep(1)

listenThread = threading.Thread(target=listen_clipboard, daemon=True)
listenThread.start()

print("Enter 'exit' to quit: ")
print("Connecting……")
def input_read():
    while True:
        user_input = input()
        if user_input == "exit":
           ws.close()
           break
        else:
            print("Enter 'exit' to quit: ")

# thread2 = threading.Thread(target=input_read, daemon=True)
# thread2.start()
input_read()

# try:
#     thread2.join()
#     listenThread.join()
#     wsThread.join()
# except KeyboardInterrupt:
#     ws.close()
#     exit()
