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

lastMsg = ""

file_path = "config.json"
config = {}
if not os.path.exists(file_path):
    with open(file_path, "w") as f:
        json.dump({"clientName": "", "url": "", "token": ""}, f)
if os.path.exists(file_path):
    with open(file_path, "r") as f:
        config = json.load(f)
CLIENTNAME = config["clientName"]
URL = config["url"]
TOKEN = config["token"]
if len(CLIENTNAME) == 0:
    user_input = ""
    while len(user_input) == 0:
        user_input = input("输入当前客户端的名字\n")
    config["clientName"] = user_input
    CLIENTNAME = user_input
if len(URL) == 0:
    user_input = ""
    while len(user_input) == 0:
        user_input = input("输入ntfy的地址，带topic的，例如: ntfy.sh/topic\n")
    config["url"] = user_input
    URL = user_input
if len(TOKEN) == 0:
    user_input = ""
    while len(user_input) == 0:
        user_input = input("输入token，例如“Bearer tk_xxx”，没有请输入\"-\"\n")
    config["token"] = user_input
    TOKEN = user_input
with open(file_path, "w") as f:
    json.dump(config, f, indent=4)


def on_message(ws, message):
    print(f"on_message: {message}")
    data = json.loads(message)
    title = data.get("title")
    message_content = data.get("message")

    if not message_content:
        return

    # 判断消息是否来自自己
    if title == CLIENTNAME:
        return

    # 判断消息内容是否与剪贴板内容一致
    current_clipboard_content = clipboard.paste()
    if message_content == current_clipboard_content:
        return
    
    global lastMsg
    if message_content == lastMsg:
        return

    print(f"收到: {message_content}")
    lastMsg = message_content
    clipboard.copy(message_content)


def on_error(ws, error):
    print(error)


def on_close(ws, close_status_code, close_msg):
    print(f"### closed ###:\n close_status_code={close_status_code}\n close_msg={close_msg}")


def on_open(ws):
    print("Opened connection")


print("wss://%s/ws" % (URL))
# 创建websocket连接
ws = websocket.WebSocketApp(
    "wss://%s/ws" % (URL),
    header={"Authorization": TOKEN if TOKEN != "-" else ""},
    on_message=on_message,
    on_error=on_error,
    on_close=on_close,
    on_open=on_open)
wsThread = threading.Thread(target=ws.run_forever, daemon=True)
wsThread.start()


def send_clipboard(msg):
    requests.post("http://%s" % (URL),
                  data=msg.encode(encoding='utf-8'),
                  headers={
                      "Authorization": TOKEN if TOKEN != "-" else "",
                      "Title": CLIENTNAME
                  })


def listen_clipboard():
    global lastMsg
    lastMsg = clipboard.paste()
    # 创建一个循环，不断监视剪贴板
    while True:
        # 读取剪贴板的内容
        text = clipboard.paste()

        # 如果剪贴板有内容，则打印内容
        if (len(text) > 0 and text != lastMsg):
            print("剪贴板变化：%s" % (text))
            lastMsg = text
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
            exit()
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
