import curses
import datetime
import os
import socket
import sys
import threading
import time

import qrcode
from flask import Flask, request

path = '.\\cds\\'


def checkDirectory():
    if not os.path.exists(path):
        os.makedirs(path)


def startDirectory():
    checkDirectory()
    os.startfile(path)


def get_host():
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
        s.connect(('8.8.8.8', 80))
        return s.getsockname()[0]


def get_port():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(('', 0))
        return s.getsockname()[1]


def UploadPage(ip):
    return '''
<!DOCTYPE html>
<html>
  <head>
    <title>跨设备文件呈递系统-网页极速版</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css">
    <style>
        button[type="submit"] {
          background-color: #3DE1AD;
          color: white;
          border: none;
        }
      </style>
  </head>
  <body>
    <div class="container">
      <div class="row justify-content-center mt-3">
        <div class="col-md-6">
            <p class="text-center mb-0">
              <font color='#758A99' size=2>
                T细胞有抗原呈递细胞, <br>而你有跨设备文件呈递系统<br>比驱动蛋白还快!!!
              </font>
            </p>
          <h1 class="text-center mb-3">跨设备文件呈递系统</h1>
          <h6 class="text-center mb-2"><font color='#FF7500'>[%<IP>%]</font></h6>
          <form action="http://%<HOST>%:%<PORT>%/upload/file" method="post" enctype="multipart/form-data">
            <div class="form-group">
              <label for="file">选择一个文件：</label>
              <input type="file" class="form-control-file" name="file" id="file">
            </div>
            <div class="text-center">
              <button type="submit" class="btn btn-danger mt-3">上传文件</button>
            </div>
          </form>
        </div>
      </div>
    </div>
  </body>
</html>
    '''.replace('%<IP>%', ip).replace('%<HOST>%', str(host)).replace('%<PORT>%', str(port))


def SuccessHTML(filename):
    return '''
<!DOCTYPE html>
<html>
<head>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>上传成功</title>
    <!-- 加载Bootstrap样式文件 -->
    <link rel="stylesheet" href="https://cdn.bootcdn.net/ajax/libs/twitter-bootstrap/5.1.3/css/bootstrap.min.css">
    <style>
      .alert-success {
        overflow-wrap: break-word;
      }
    </style>
</head>
<body>
    <div class="container py-5">
        <div class="row justify-content-center">
            <div class="col-lg-6 col-md-8 col-sm-10">
                <div class="alert alert-success" role="alert">
                    <h6>文件~[%<FILENAME>%]~上传成功</h6>
                </div>
                <a href="http://%<HOST>%:%<PORT>%/upload" class="btn btn-lg btn-danger">继续上传</a>
            </div>
        </div>
    </div>
    <!-- 加载Bootstrap JavaScript文件，必须放在body标签底部 -->
    <script src="https://cdn.bootcdn.net/ajax/libs/twitter-bootstrap/5.1.3/js/bootstrap.min.js"></script>
</body>
</html>
    '''.replace('%<FILENAME>%', filename).replace('%<HOST>%', str(host)).replace('%<PORT>%', str(port))


def timeNow():
    return datetime.datetime.strftime(datetime.datetime.now(), '%F %H:%M:%S')


def QR(data):
    qr = qrcode.QRCode(version=1, box_size=1, border=1)
    qr.add_data(data)
    qr.make(fit=True)
    img = qr.make_image(fill_color="white", back_color="black")
    # img.save('q.png')
    return img


class GUI:
    def __init__(self, url):
        self.filenames = [[timeNow(), '0.0.0.0', '欢 迎 使 用 跨 设 备 文 件 呈 递 系 统']]
        self.index = 0
        self.url = url
        self.QRCode = QR(self.url).convert('L')
        self.pixels = self.QRCode.load()
        self.width, self.height = self.QRCode.size

    def __call__(self, stdscr):
        self.stdscr = stdscr
        # self.stdscr = curses.newwin()
        self.stdscr.clear()
        self.init()
        self.x, self.y = self.stdscr.getmaxyx()

        if self.width * 2 + 1 >= self.y - 10:
            width = self.y - 10
        else:
            width = self.width * 2 + 1
        self.infoWin = curses.newwin(self.x, int(self.y - width), 0, 0)
        self.infoWin.scrollok(True)
        self.qrWin = curses.newwin(self.x, int(width), 0, int(self.y - width))
        self.qrWin.scrollok(True)
        self.main()

    def main(self):
        threading.Thread(target=self.firstScreen, daemon=True).start()
        self.mainloop()

    def init(self):
        self.index = 0
        curses.curs_set(0)
        curses.init_pair(1, curses.COLOR_WHITE, curses.COLOR_CYAN)
        curses.init_pair(2, curses.COLOR_BLACK, curses.COLOR_YELLOW)
        curses.init_pair(3, curses.COLOR_BLUE, curses.COLOR_GREEN)
        curses.init_pair(4, curses.COLOR_WHITE, curses.COLOR_MAGENTA)
        curses.init_pair(10, curses.COLOR_BLACK, curses.COLOR_BLACK)
        curses.init_pair(11, curses.COLOR_WHITE, curses.COLOR_WHITE)

    def mainloop(self):
        while True:
            key = self.stdscr.getch()
            if key == curses.KEY_UP:
                self.up()
                self.showHistory()
            elif key == curses.KEY_DOWN:
                self.down()
                self.showHistory()

            elif key == ord('e'):
                sys.exit(0)
            elif key == ord('q'):
                break
            elif key == ord('p'):
                startDirectory()

            self.sizeChanged()

    def add(self, ip, filename):
        Time = timeNow()
        self.filenames.append([Time, ip, filename])
        self.show(Time=Time, ip=ip, filename=filename)
        self.index = len(self.filenames) - 1

    def show(self, Time, ip, filename):
        self.infoWin.clear()
        self.infoWin.addstr(' ' + Time + ' ', curses.color_pair(1))
        self.infoWin.addstr(' ' + ip + ' ', curses.color_pair(2))
        self.infoWin.addstr(' ' + filename + ' ', curses.color_pair(3))
        self.infoWin.addstr('\n')
        self.infoWin.refresh()

    def up(self):
        if self.index > 0:
            self.index -= 1
        else:
            self.index = 0

    def down(self):
        if self.index < len(self.filenames) - 1:
            self.index += 1
        else:
            self.index = len(self.filenames) - 1

    def showHistory(self):
        self.show(
            Time=self.filenames[self.index][0],
            ip=self.filenames[self.index][1],
            filename=self.filenames[self.index][2],
        )

    def showQRCode(self):
        self.qrWin.clear()
        self.loadQRCode()

        num = int(((self.y / 2) - len(self.url)) / 2)
        if num > 0:
            self.qrWin.addstr(' ' * num)
        self.qrWin.addstr(self.url, curses.color_pair(4))
        self.qrWin.refresh()

    def loadQRCode(self):
        for y in range(self.height):
            for x in range(self.width):
                pixel = self.pixels[x, y]
                if pixel == 0:
                    self.qrWin.addstr('  ', curses.color_pair(10))
                else:
                    self.qrWin.addstr('  ', curses.color_pair(11))
            self.qrWin.addstr('\n')

    def sizeChanged(self):
        x, y = self.stdscr.getmaxyx()
        if x != self.x or y != self.y:
            self.x, self.y = self.stdscr.getmaxyx()
            self.flush()

    def firstScreen(self):
        time.sleep(0.01)
        self.flush()

    def flush(self):
        if self.width * 2 + 1 >= self.y - 10:
            width = self.y - 10
        else:
            width = self.width * 2 + 1
        self.infoWin = curses.newwin(self.x, int(self.y - width), 0, 0)
        self.infoWin.scrollok(True)
        self.qrWin = curses.newwin(self.x, int(width), 0, int(self.y - width))
        self.qrWin.scrollok(True)
        self.showHistory()
        self.showQRCode()


host = get_host()
port = get_port()
gui = GUI(url=f'http://{host}:{port}/upload')

app = Flask(__name__)


@app.route('/upload/file', methods=['POST'])
def upload_file():
    checkDirectory()
    file = request.files['file']
    file.save(path + file.filename)
    gui.add(ip=request.remote_addr, filename=file.filename)
    return SuccessHTML(filename=file.filename)


@app.route('/upload', methods=['POST', 'GET'])
def upload():
    return UploadPage(ip=request.remote_addr)


if __name__ == '__main__':
    os.system('title 跨设备文件呈递系统')
    checkDirectory()
    threading.Thread(
        target=lambda: app.run(host=host, port=port),
        daemon=True
    ).start()
    curses.wrapper(gui)
