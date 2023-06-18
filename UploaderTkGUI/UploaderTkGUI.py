import os
import time
import requests
from io import BytesIO
import sys
from threading import Thread
from tkinter.messagebox import showerror
from tkinter.filedialog import askopenfilename
from tkextrafont import Font
import pystray
from ttkbootstrap import *
import toast
from DnD import DnD
from ttkbootstrap.scrolled import ScrolledFrame

from tkinter import Text as tkText
from tkinter import Frame as tkFrame
import MoFont
from tklinenums.tklinenums import TkLineNumbers
import datetime

__title__ = 'UploaderTkGUI'
__version__ = 'v0.1.0beta'
__help__ = """UploaderTkGUI
by MoYeRanQianZhi
"""

__background_light_dark_table__ = {
    'light': '#F9F1F6',
    'dark': '#3D3B4F'
}

__local_web_bootstyle__ = {
    'local': 'warning',
    'web': 'dark'
}

__FileTypes__ = [
    ('所有文件', '*.*'),
    ('文本文档', '*.txt'),
    ('Python文件', '*.py;*.pyw'),
    ('位图文件', '*.jpg'),
    ('网格式图片文件', '*.png'),
    ('程序文件', '*.exe'),
    ('zip压缩文件', '*.zip'),
    ('rar压缩文件', '*.rar'),
    ('7z压缩文件', '*.7z'),
    ('tar压缩文件', '*.tar'),
    ('gz压缩文件', '*.gz'),
    ('tz压缩文件', '*.tar.gz'),
    ('批处理文件', '*.bat'),
    ('MoYeRanPythonFile', '*.mpy'),
    ('墨叶染文件', '*.mo'),
    ('数据库', '*.db'),
    ('C', '*.c;*.i'),
    ('C#', '*.cs;*.csx;*.cake'),
    ('C++', '*.cpp;*.cc;*.cxx;*.c++;*.hpp;*.hh;*.hxx;*.h++;*.h;*.ii'),
    ('Java', '*.java;*.jav'),
    ('JavaScript', '*.js'),
    ('JSON', '*.json'),
    ('HTML', '*.html;*.htm;*.xhtml'),
    ('Go', '*.go'),
    ('CSS', '*.css'),
    ('PHP', '*.php'),
    ('PowerShell', '*.ps1;*.psm1;*.psd1'),
    ('R', '*.r'),
    ('Ini', '*.ini'),
    ('SQL', '*.sql'),
    ('XML', '*.xml'),
    ('Visual Basic', '*.vb;*.vbs'),
    ('PS文件', '*.pad'),
    ('矢量图文件', '*.svg'),
    ('AI文件', '*.ai'),
]


def URL(host, port):
    return f'http://{host}:{port}/upload/file'


def upload(file, url):
    if requests.post(url=url, files={'file': file}).status_code == 200:
        return True
    else:
        return False


def CDF(path, host, port):
    """
    本地文件呈递
    Parameters:
        path(str):
        host(str):
        port(int):
    """
    if not os.path.exists(path):
        return False
    if not os.path.isfile(path):
        return False
    with open(file=path, mode='rb') as f:
        return upload(file=f, url=URL(host=host, port=port))


def CDW(webURL, host, port):
    """
    网络文件呈递
    Parameters:
        webURL(str):
        host(str):
        port(int):
    """
    resource = requests.get(webURL)
    if resource.status_code == 200:
        return upload(file=(webURL.split('/')[-1], resource.content), url=URL(host=host, port=port))
    else:
        return False


def PositiveNegativeInteger(value):
    if value > 0:
        return 1
    elif value < 0:
        return -1
    else:
        return 0

def NumberEntry(text):
    if text.isdigit() or text == '':
        return True
    else:
        return False

def timeNow():
    return datetime.datetime.strftime(datetime.datetime.now(), '%F %H:%M:%S')

class MoError(Exception):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)

    __module__ = 'builtins'


def LineNumber(master, text, bar):
    def LineNumberBind(*args):
        bar.set(*args)
        l.redraw(*args)

    l = TkLineNumbers(master, text, justify='center')
    text.config(
        yscrollcommand=LineNumberBind
    )
    text.bind("<Key>", lambda event: text.after_idle(l.redraw), add=True)
    l.pack(side=LEFT, expand=1, fill=Y)
    return l


class UploaderTkGUI:
    def __init__(self):
        self.Fonts = {}
        self.Menus = {}
        self.SHOW = True
        self.text = ''
        self.saving = False
        self.mouseX = 0
        self.mouseY = 0
        self.TaskFrames = []
        self.root = Window()

        self.host = StringVar()
        self.port = IntVar()
        self.webURL = StringVar()

        self.X = IntVar()
        self.X.set(int(self.root.winfo_screenwidth() / 4))
        self.Y = IntVar()
        self.Y.set(int(self.root.winfo_screenheight() / 4))

        self.root.geometry(
            f'{int(self.root.winfo_screenwidth() / 2)}x{int(self.root.winfo_screenheight() / 2)}'
            f'+{self.X.get()}+{self.Y.get()}'
        )
        self.root.wm_minsize(
            int(self.root.winfo_screenwidth()/16),
            int(self.root.winfo_screenheight()/32)
        )

        self.root.iconbitmap(sys.executable)
        self.root.title(__title__)
        self.style = Style()
        self.style.theme_use('darkly')

        self.root.overrideredirect(True)
        self.root.wm_attributes('-topmost', 1)
        self.root.update()

        self.dnd = DnD(
            tkroot=self.root
        )
        self.initFonts()

        self.title = StringVar()
        self.title.set(__title__)

        self.icon = StringVar()
        self.icon.set(' f ')

        self.filename = None
        self.filepath = None

        self.TopMostMode = IntVar()
        self.TopMostMode.set(1)
        self.TopMostMode.trace(
            mode='w',
            callback=self.TopMostHandoff
        )
        self.lineNumberMode = IntVar()
        self.lineNumberMode.set(0)
        self.lineNumberMode.trace(
            mode='w',
            callback=self.LineNumberModeChange
        )

        self.textFont = StringVar()
        self.textFont.set('HarmonyOS Sans SC Medium')

        self.titleFont = StringVar()
        self.titleFont.set('HarmonyOS Sans Black')

        self.container = tkFrame(
            master=self.root,
            highlightthickness=1,
            highlightcolor='#000000',
            highlightbackground='#3DE1AD',
        )

        self.top = Frame(
            master=self.container,
            bootstyle='default'
        )

        self.controller = Frame(
            master=self.top,
            bootstyle='default'
        )
        self.exiterAPP = Frame(
            master=self.controller,
            bootstyle='default'
        )
        self.changerAPP = Frame(
            master=self.controller,
            bootstyle='default'
        )
        self.hiderAPP = Frame(
            master=self.controller,
            bootstyle='default'
        )
        self.exiter = Label(
            master=self.exiterAPP,
            text='0',
            foreground='#F00056',
            font=('IDEM', 20)
        )
        self.changer = Label(
            master=self.changerAPP,
            text='0',
            foreground='#FFA400',
            font=('IDEM', 20)
        )
        self.hider = Label(
            master=self.hiderAPP,
            text='0',
            foreground='#801DAE',
            font=('IDEM', 20)
        )

        self.iconShower = Label(
            master=self.top,
            textvariable=self.icon,
            # foreground='#3DE1AD',
            font=('IDEM', 20),
        )

        self.menu = Frame(
            master=self.top,
        )

        self.titleShower = Label(
            master=self.top,
            textvariable=self.title,
            font=(self.titleFont.get(), 10, 'bold')
        )

        self.separator = Separator(
            master=self.container,
            bootstyle='secondary'
        )

        self.right = Frame(
            master=self.container,
            bootstyle='default'
        )

        self.left = Frame(
            master=self.container,
            bootstyle='default'
        )
        self.bottom = Frame(
            master=self.container,
            bootstyle='default'
        )

        self.versionShower = Label(
            master=self.bottom,
            text=__version__,
            bootstyle='secondary',
        )

        self.sizegriz = Sizegrip(
            master=self.right,
            bootstyle='secondary'
        )

        self.window = Frame(
            master=self.container,
            bootstyle='default'
        )

        self.toolbar = Frame(
            master=self.window,
            bootstyle='default'
        )

        # --------------------------------------------------APPS--------------------------------------------------
        self.interface = tkFrame(
            master=self.window,
            highlightthickness=0.5,
            highlightcolor='#000000',
            highlightbackground='#000000'
        )
        self.workSpace = Frame(
            master=self.interface,
            bootstyle='default'
        )

        self.informationSpace = tkFrame(
            master=self.workSpace,
            width=467,
            height=231,
        )
        self.operateSpace = Frame(
            master=self.workSpace,
        )
        self.taskSpace = Frame(
            master=self.workSpace,
        )

        self.informationArea = ScrolledFrame(
            master=self.informationSpace,
            bootstyle='default'
        )

        self.LineNumberArea = Frame(
            master=self.informationArea,
            bootstyle='default'
        )
        self.LineNumber = None
        self.informationShower = Text(
            master=self.informationArea,
            font=(self.textFont.get(), 12),
        )

        self.informationShower.tag_config('default', foreground='')
        self.informationShower.tag_config('success', foreground='green')
        self.informationShower.tag_config('error', foreground='red')

        self.informationShower.insert('0.0', '欢迎使用CDS配套Tkinter GUI.', 'default')
        self.informationShower.configure(state='disabled')

        self.operateArea = ScrolledFrame(
            master=self.operateSpace,
            bootstyle='default'
        )
        self.HostPortArea = Frame(
            master=self.operateArea,
            bootstyle='default'
        )
        self.serverTextLabel = Label(
            master=self.HostPortArea,
            text='SERVER:',
            font=(self.textFont.get(), 12, 'bold')
        )
        self.hostEntry = Entry(
            master=self.HostPortArea,
            textvariable=self.host,
            font=(self.textFont.get(), 12, 'bold'),
            width=20
        )
        self.colonTextLabel = Label(
            master=self.HostPortArea,
            text=':',
            font=(self.textFont.get(), 12, 'bold')
        )
        self.portEntry = Entry(
            master=self.HostPortArea,
            textvariable=self.port,
            validatecommand=NumberEntry,
            font=(self.textFont.get(), 12, 'bold'),
            width=10
        )
        self.addButton = Button(
            master=self.operateArea,
            text='ADD LOCAL FILE',
            command=self.LoadFileThread,
            bootstyle='success'
        )
        self.webFileLoadArea = Frame(
            self.operateArea,
            bootstyle='default'
        )
        self.urlTextLabel = Label(
            master=self.webFileLoadArea,
            text='URL:',
            font=(self.textFont.get(), 12, 'bold')
        )
        self.webUrlEntry = Entry(
            master=self.webFileLoadArea,
            textvariable=self.webURL,
            font=(self.textFont.get(), 12, 'bold'),
            width=30
        )
        self.uploadWebFileButton = Button(
            master=self.webFileLoadArea,
            text='UPLOAD',
            command=lambda: self.add(path=self.webURL.get(), mode='web'),
            bootstyle='danger'
        )

        self.taskArea = ScrolledFrame(
            master=self.taskSpace,
            bootstyle='default'
        )

    def loads(self):
        self.container.pack(
            fill=BOTH,
            expand=True
        )
        self.root.update()
        self.top.pack(
            side=TOP,
            fill=X
        )
        self.controller.pack(
            side=RIGHT,
            fill=Y,
        )

        self.exiterAPP.pack(
            side=RIGHT,
        )
        self.changerAPP.pack(
            side=RIGHT
        )
        self.hiderAPP.pack(
            side=RIGHT
        )
        self.exiter.pack(
            padx=2
        )
        self.changer.pack(
            padx=2
        )
        self.hider.pack(
            padx=2
        )

        self.iconShower.pack(
            side=LEFT,
            fill=BOTH
        )

        self.menu.pack(
            side=LEFT,
            fill=BOTH,
        )

        self.titleShower.pack(
            fill=BOTH,
            side=LEFT,
            padx=20,
        )

        self.separator.pack(
            side=TOP,
            fill=X
        )

        self.right.pack(
            side=RIGHT,
            fill=Y
        )
        self.left.pack(
            side=LEFT,
            fill=Y,
            padx=5
        )
        self.bottom.pack(
            side=BOTTOM,
            fill=X
        )

        self.versionShower.pack(
            side=LEFT
        )

        self.sizegriz.pack(
            side=BOTTOM
        )

        self.window.pack(
            fill=BOTH,
            expand=True
        )
        self.toolbar.pack(
            fill=X
        )

        self.root.update()
        self.loadToolBar()
        # --------------------------------------------------APPS--------------------------------------------------
        self.interface.pack(
            fill=BOTH,
            expand=True
        )
        self.workSpace.pack(
            fill=BOTH,
            expand=True
        )

        self.informationSpace.grid(
            row=0,
            column=0,
            sticky='nsew'
        )
        self.operateSpace.grid(
            row=1,
            column=0,
            sticky='nsew'
        )
        self.taskSpace.grid(
            row=0,
            column=1,
            rowspan=2,
            sticky='nsew'
        )

        self.informationArea.pack(
            fill=BOTH,
            expand=True
        )

        self.LineNumberArea.pack(
            side=LEFT,
            fill=Y
        )
        self.informationShower.pack(
            fill=BOTH,
        )

        self.operateArea.pack(
            fill=BOTH,
            expand=True
        )

        self.HostPortArea.pack(pady=10),
        self.serverTextLabel.grid(row=0, column=0)
        self.hostEntry.grid(row=0, column=1)
        self.colonTextLabel.grid(row=0, column=2)
        self.portEntry.grid(row=0, column=3)
        self.addButton.pack(pady=10)
        self.webFileLoadArea.pack(pady=10)
        self.urlTextLabel.grid(row=0, column=0)
        self.webUrlEntry.grid(row=0, column=1)
        self.uploadWebFileButton.grid(row=0, column=2)

        self.taskArea.pack(
            fill=BOTH,
            expand=True
        )

        self.workSpace.rowconfigure(0, weight=1)
        self.workSpace.rowconfigure(1, weight=1)
        self.workSpace.columnconfigure(0, weight=1)
        self.workSpace.columnconfigure(1, weight=1)

        self.informationSpace.rowconfigure(0, weight=1)
        self.informationSpace.columnconfigure(0, weight=1)

        self.operateSpace.rowconfigure(0, weight=1)
        self.operateSpace.columnconfigure(0, weight=1)

        self.taskSpace.rowconfigure(0, weight=1)
        self.taskSpace.columnconfigure(0, weight=1)

        # self.style.theme_use('cosmo')

        # --------------------------------------------------------------------------------------------------------

    def mainloop(self):
        self.initTrayIcon()
        self.initSystem()
        self.root.mainloop()

    def initFonts(self):
        self.Fonts.update(
            {
                'idea': Font(file='font/idea.ttf')
            }
        )
        self.Fonts.update(
            {
                'idem': MoFont.load()
            }
        )
        self.Fonts.update(
            {
                'HarmonyOS': Font(file='font/HarmonyOS.ttf')
            }
        )

    def EXIT(self):
        self.root.destroy()

    def binds(self):
        self.exiterAPP.bind(
            sequence='<Button-1>',
            func=lambda event: self.EXIT()
        )
        self.changerAPP.bind(
            sequence='<Button-1>',
            func=lambda event: self.MaxMinHandoff()
        )
        self.hiderAPP.bind(
            sequence='<Button-1>',
            func=lambda event: self.Hide()
        )
        self.exiter.bind(
            sequence='<Button-1>',
            func=lambda event: self.EXIT()
        )
        self.changer.bind(
            sequence='<Button-1>',
            func=lambda event: self.MaxMinHandoff()
        )
        self.hider.bind(
            sequence='<Button-1>',
            func=lambda event: self.Hide()
        )

        self.exiterAPP.bind(
            sequence='<Enter>',
            func=lambda event: self.exiter.config(text='1')
        )
        self.exiterAPP.bind(
            sequence='<Leave>',
            func=lambda event: self.exiter.config(text='0')
        )
        self.changerAPP.bind(
            sequence='<Enter>',
            func=lambda event: self.changer.config(text='2')
        )
        self.changerAPP.bind(
            sequence='<Leave>',
            func=lambda event: self.changer.config(text='0')
        )
        self.hiderAPP.bind(
            sequence='<Enter>',
            func=lambda event: self.hider.config(text='3')
        )
        self.hiderAPP.bind(
            sequence='<Leave>',
            func=lambda event: self.hider.config(text='0')
        )

        self.titleShower.bind(
            sequence='<Button-1>',
            func=self.titleShowerMouseDown
        )
        self.titleShower.bind(
            sequence='<B1-Motion>',
            func=self.titleShowerMouseMove
        )
        self.titleShower.bind(
            sequence='<Double-Button-1>',
            func=lambda event: self.MaxMinHandoff()
        )

        self.top.bind(
            sequence='<Button-1>',
            func=self.topMouseDown
        )
        self.top.bind(
            sequence='<B1-Motion>',
            func=self.topMouseMove
        )
        self.top.bind(
            sequence='<Double-Button-1>',
            func=lambda event: self.MaxMinHandoff()
        )

        self.sizegriz.bind(
            sequence='<Enter>',
            func=lambda event: self.sizegriz.config(bootstyle='success')
        )
        self.sizegriz.bind(
            sequence='<Leave>',
            func=lambda event: self.sizegriz.config(bootstyle='secondary')
        )

        # --------------------------------------------------MENU--------------------------------------------------
        self.root.bind(
            sequence='<Control-l>',
            func=lambda event: self.LoadFileThread()
        )
        self.root.bind(
            sequence='<Control-w>',
            func=lambda event: self.add(path=self.webURL.get(), mode='web')
        )
        # --------------------------------------------------------------------------------------------------------

        # --------------------------------------------------APPS--------------------------------------------------
        self.dnd.bindtarget(
            widget=self.workSpace,
            type='text/uri-list',
            sequence='<Drop>',
            command=self.fileinDnDThread,
            arguments=('%A', '%a', '%T', '%W', '%X', '%Y', '%x', '%y', '%D')
        )
        self.portEntry.bind(
            sequence='<MouseWheel>',
            func=lambda event: self.port.set(
                self.port.get() + PositiveNegativeInteger(event.delta)
            )
        )
        self.portEntry.bind(
            sequence='<Up>',
            func=lambda event: self.port.set(
                self.port.get() + 1
            )
        )
        self.portEntry.bind(
            sequence='<Down>',
            func=lambda event: self.port.set(
                self.port.get() - 1
            )
        )
        # --------------------------------------------------------------------------------------------------------

    def MinShow(self):
        self.root.geometry(
            f'{int(self.root.winfo_screenwidth() / 2)}x{int(self.root.winfo_screenheight() / 2)}'
            f'+{int(self.root.winfo_screenwidth() / 4)}+{int(self.root.winfo_screenheight() / 4)}'
        )

    def MaxShow(self):
        self.root.geometry(
            f'{int(self.root.winfo_screenwidth())}x{int(self.root.winfo_screenheight())}+0+0'
        )

    def MaxMinHandoff(self):
        if self.root.winfo_height() == self.root.winfo_screenheight() and self.root.winfo_width() == self.root.winfo_screenwidth() and self.root.winfo_x() == 0 and self.root.winfo_y() == 0:
            self.MinShow()
        else:
            self.MaxShow()


    def Hide(self):
        self.root.withdraw()
        self.SHOW = False

    def Show(self):
        # 使窗口出现时在最上层
        self.root.wm_attributes('-topmost', 1)
        if not self.TopMostMode.get():
            self.downTopMost()
        self.root.deiconify()
        self.SHOW = True

    def HideShowHandoff(self):
        if self.SHOW:
            self.Hide()
        else:
            self.Show()

    def upTopMost(self):
        self.root.wm_attributes('-topmost', 1)

    def downTopMost(self):
        self.root.wm_attributes('-topmost', 0)

    def TopMostHandoff(self, *args):
        if self.TopMostMode.get():
            self.upTopMost()
        else:
            self.downTopMost()

    def TopMostModeChange(self, TopMostModeBinder=None):
        if self.TopMostMode.get():
            self.TopMostMode.set(0)
            if TopMostModeBinder is not None:
                TopMostModeBinder.configure(foreground='')
        else:
            self.TopMostMode.set(1)
            if TopMostModeBinder is not None:
                TopMostModeBinder.configure(foreground='#3DE1AD')

    def titleShowerMouseDown(self, event):
        self.mouseX = event.x
        self.mouseY = event.y

    def titleShowerMouseMove(self, event):
        self.root.geometry(
            f'+{event.x_root - self.mouseX - self.titleShower.winfo_x()}+{event.y_root - self.mouseY - self.titleShower.winfo_y()}'
        )

    def topMouseDown(self, event):
        self.mouseX = event.x
        self.mouseY = event.y

    def topMouseMove(self, event):
        self.root.geometry(
            f'+{event.x_root - self.mouseX - self.top.winfo_x()}+{event.y_root - self.mouseY - self.top.winfo_y()}'
        )

    def loadToolBar(self):
        TopMostAPP = Frame(
            master=self.top
        )
        TopMostAPP.pack(
            side=RIGHT,
            fill=BOTH,
            padx=5
        )
        TopMostConfig = Label(
            master=TopMostAPP,
            text=' T ',
            font=('IDEM', 15)
        )
        TopMostConfig.pack(
            side=LEFT,
            fill=BOTH
        )
        TopMostConfig.configure(foreground='#3DE1AD')
        TopMostConfig.bind(
            sequence='<Button-1>',
            func=lambda event: self.TopMostModeChange(TopMostModeBinder=TopMostConfig)
        )
        TopMostConfig.bind(
            sequence='<Enter>',
            func=lambda event: TopMostConfig.configure(
                background=__background_light_dark_table__[self.style.theme.type]
            )
        )
        TopMostConfig.bind(
            sequence='<Leave>',
            func=lambda event: TopMostConfig.configure(background='')
        )

        LineNumberAPP = Frame(
            master=self.toolbar
        )
        LineNumberAPP.pack(
            side=LEFT,
            fill=BOTH,
            padx=5
        )
        Checkbutton(
            master=self.toolbar,
            text='',
            variable=self.lineNumberMode,
            onvalue=1,
            offvalue=0,
            bootstyle='danger-round-toggle'
        ).pack(
            side=LEFT,
            fill=BOTH
        )
        Label(
            master=LineNumberAPP,
            text='LineNumber',
            font=('jetbrains mono', 9)
        ).pack(
            side=LEFT,
            fill=BOTH
        )

        ClearTasksButtonAPP = Frame(
            master=self.toolbar
        )

        ClearTasksButtonAPP.pack(
            side=LEFT,
            fill=BOTH,
            padx=5
        )
        Label(
            master=ClearTasksButtonAPP,
            text='ClearTasks',
            font=('jetbrains mono', 9)
        ).pack(
            side=LEFT,
            fill=BOTH
        )
        ClearTasksButton = Label(
            master=ClearTasksButtonAPP,
            text=' t ',
            font=('IDEM', 15)
        )
        ClearTasksButton.pack(
            side=LEFT,
            fill=BOTH
        )
        ClearTasksButton.configure(foreground='#3DE1AD')
        ClearTasksButton.bind(
            sequence='<Button-1>',
            func=lambda event: self.clearTasksThread()
        )
        ClearTasksButton.bind(
            sequence='<Enter>',
            func=lambda event: ClearTasksButton.configure(
                background=__background_light_dark_table__[self.style.theme.type]
            )
        )
        ClearTasksButton.bind(
            sequence='<Leave>',
            func=lambda event: ClearTasksButton.configure(background='')
        )

    def Menu(self):
        for menu in ['File', 'Edit', 'View', 'Tool', 'Window', 'Help']:
            self.Menus.update(
                {
                    menu: Menu(master=self.root),
                }
            )
            MenuTrigger = Label(
                master=self.menu,
                text=f' {menu} ',
                font=('JetBrains Mono', 10),
                underline=1
            )
            MenuTrigger.pack(side=LEFT, fill=Y)
            self.bindMenu(
                MenuTrigger=MenuTrigger,
                MenuClassName=menu
            )
            self.rootBindMenu(
                MenuTrigger=MenuTrigger,
                MenuClassName=menu,
                BindKey=f'<Alt-{menu[0]}>'
            )

        self.Menus['File'].add_command(
            label='Load',
            activebackground='#2675bf',
            font=('JetBrains Mono', 10),
            accelerator='Ctrl+L',
            command=self.LoadFileThread
        )
        self.Menus['File'].add_command(
            label='WebLoad',
            activebackground='#2675bf',
            font=('JetBrains Mono', 10),
            accelerator='Ctrl+W',
            command=lambda: self.add(path=self.webURL.get(), mode='web')
        )
        self.Menus['File'].add_command(
            label='Setting',
            activebackground='#2675bf',
            font=('JetBrains Mono', 10),
            accelerator='Ctrl+T',
        )

        Theme = Menu(
            master=self.Menus['File']
        )
        for theme in self.style.theme_names():
            self.bindStyleChangeMenu(
                FatherMenu=Theme,
                useStyle=theme
            )
        self.Menus['File'].add_cascade(
            label='Theme',
            activebackground='#2675bf',
            font=('JetBrains Mono', 10),
            accelerator='Ctrl+T',
            menu=Theme
        )

    def bindMenu(
            self,
            MenuTrigger,
            MenuClass=None,
            MenuClassName=None
    ):
        """
        绑定菜单触发器, 并完成一些基础设置, 例如点击事件绑定, 鼠标进入变色等
        Parameters:
            MenuTrigger: 菜单触发器, 以触发器相对于屏幕的位置弹出菜单
            MenuClass: 菜单类, 弹出的菜单, 与菜单类至少二选一
            MenuClassName: 菜单类的名字, 与菜单类至少二选一
        """
        if MenuClass is None and MenuClassName is None:
            raise MoError('Both MenuClass and MenuClassName is None.')
        else:
            if MenuClass is None:
                MenuClass = self.Menus[MenuClassName]

        MenuTrigger.bind(
            sequence='<Button-1>',
            func=lambda event: self.popupMenu(
                MenuTrigger=MenuTrigger,
                MenuClass=MenuClass
            )
        )
        MenuTrigger.bind(
            sequence='<Enter>',
            func=lambda event: MenuTrigger.config(
                background='#2675bf',
                foreground='#ffffff'
            )
        )
        MenuTrigger.bind(
            sequence='<Leave>',
            func=lambda event: MenuTrigger.config(
                background='',
                foreground=''
            )
        )

    def rootBindMenu(
            self,
            MenuTrigger,
            MenuClass=None,
            MenuClassName=None,
            BindKey=None
    ):
        """
        绑定菜单触发器, 并完成一些基础设置, 例如点击事件绑定, 鼠标进入变色等
        Parameters:
            MenuTrigger: 菜单触发器, 以触发器相对于屏幕的位置弹出菜单
            MenuClass: 菜单类, 弹出的菜单, 与菜单类至少二选一
            MenuClassName: 菜单类的名字, 与菜单类至少二选一
            BindKey: 绑定的键盘
        """
        if MenuClass is None and MenuClassName is None:
            raise MoError('Both MenuClass and MenuClassName is None.')
        else:
            if MenuClass is None:
                MenuClass = self.Menus[MenuClassName]

        self.root.bind(
            sequence=BindKey,
            func=lambda event: self.popupMenu(
                MenuTrigger=MenuTrigger,
                MenuClass=MenuClass
            )
        )

    def popupMenu(
            self,
            MenuTrigger,
            MenuClass=None,
            MenuClassName=None
    ):
        """
        Parameters:
            MenuTrigger: 菜单触发器, 以触发器相对于屏幕的位置弹出菜单
            MenuClass: 菜单类, 弹出的菜单, 与菜单类至少二选一
            MenuClassName: 菜单类的名字, 与菜单类至少二选一
        """
        if MenuClass is None and MenuClassName is None:
            raise MoError('Both MenuClass and MenuClassName is None.')

        else:
            if MenuClass is None:
                MenuClass = self.Menus[MenuClassName]

        MenuClass.post(
            x=MenuTrigger.winfo_rootx(),
            y=MenuTrigger.winfo_rooty() + MenuTrigger.winfo_height()
        )

    def bindStyleChangeMenu(
            self,
            FatherMenu,
            useStyle
    ):
        """绑定主题更改按键"""
        FatherMenu.add_command(
            label=useStyle,
            activebackground='#2675bf',
            font=('JetBrains Mono', 10),
            # accelerator='Ctrl+T',
            command=lambda: self.style.theme_use(themename=useStyle)
        )

    def getFileLoad(self):
        return askopenfilename(
            filetypes=__FileTypes__,
            parent=self.root,
        )

    def LoadLocalFile(self):
        path = self.getFileLoad()
        if path:
            self.add(
                path=path,
                mode='local'
            )

    def LoadFileThread(self):
        Thread(
            target=lambda: self.LoadLocalFile(),
            daemon=True
        ).start()

    def fileinDnD(self, data):
        files = data.split()
        for file in files:
            self.add(path=file, mode='local')

    def fileinDnDThread(
            self,
            action,
            actions,
            type,
            win,
            X,
            Y,
            x,
            y,
            data
    ):
        Thread(
            target=lambda: self.fileinDnD(data),
            daemon=True
        ).start()

    def initTrayIcon(self):
        Thread(
            target=pystray.Icon(
                name=__title__,
                icon=Image.open(
                    BytesIO(
                        b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\xa7\x00\x00\x00\x93\x08\x06\x00\x00\x00\xeb\xfd\tW\x00\x00\x18\x90IDATx\x9c\xed\x9d\t\x94\x1dU\x99\xc7\x7fUo\xed\xd7\xfb\x9e\xa4\x93\xee\xce\x8a\xd94+\x89@\x12v38\x02\x830\x8a0\x07\xd4\xa3r\x023\xa8Gg\x90\x80\x8e\xe3\xc2\xc1}\xe7\x883\xa28\x8cQA\x0e\x08(D\x03\t\tK \x0b$\x10\x12Bgk\x92t\xa7\xf7~\xefu\xbf\xb5\xe6\xdc\xaaj\xb3u\xbfW\xefu\xd5[\xebwh\x0e\xf4\xabWu\xab\xfa_\xf7~\xf7\xbb\xdf\xf7]i\xc5-\xf7\x92e\xe6\x00W\x01\x8b\x81i\xc0\x14\xa0\x04P\xf4\x9f|G\x06\xe2@\x1fp\x00\xd8\x0fl\x04\xfe\x04\xf4\x16\xc0\xfdY\x863\x8b\xd7\xbe\x19\xb8\x038\'\x8bm\xc8$\xe5\xfa\x8b\xb7\x12\xf8\x84~\xdd\xc7\x81\xaf\x03\xaf\x14\xc7#H\r9\x0b\xd7\xbc\x028\x01<PD\xc2\x1c\x8b+\x81\xad\xc03\xc0\xc4\xdclb\xf6\xc8\xb48\x7f\x0b<\t\xd4\xe5\xd2C\xc8\x01.\x03\x8e\x027\x16\xfb\x838\x95L\x89\xb3\x12x\x03\xf8h\x86\xae\x97\xaf\xfc\x06\xf8V\xb1?\x84\x112!N/\xf0\x92>\xf1\xb1I\xce\x17\x81\x1f\xdb\xcf)3\xe2|\x1axO\x06\xaeSH\xdc\x06|\xbe\xd8\x1f\x82\xd5\xe2\xfc\xa1>;\xb5I\x9d\xef\x02\xe7\x15\xf3s\xb3\xd2\x95t1\xf0o\xa9~)\x1e\x8d\x10\x8f\xc6\xaciQ\xb6\x90@v\xb9\x90eG\xaa\r\xf8)\xb0\xb0`\x9eC\x8aX)\xce\xaf\x1a9H\x92$\xe2\x8aB\xa8\xaf\x8fx,\x8a\xb7\xb2\nOE\x85\xf6\x17U\n\xc0\x07/I(\xf1\x18\xa1\x81\x01\x86\x82\x01\xdc\xbeR\xdc\xa5e(J\xdc\xc8\xb7\x17\x00k\x80\x9fY\xdf\xd0\xdc\xc3*q^\x02\\\x90\xec Iv\x10\x0e\xf8\x89\x04\x034\xcc\x99G\xe3\xbc\xf9\x9454\xe2*-E\x11\x8bC\x05 NI\x92Q\xe2q\x86\xfb\xfb\xe8?|\x98w\xb7\xbfB\xa0\xb3\x93\x92\x9aZdYFI~\x8f\xb7\xdb\xe24\x97\x1b\x92\x9dM\x92eB\x03\xfdj\x079\xef\xda\xeb\x99\xb2|!\x0e7D\x82\x10\x8b\xc4\x0bd\xe5R\xbb\rq\xafe\x8d\xd54\xce\x9f\xca\xe4\xe5\xefg\xef\x9f\x1e\xa7\xfd\x95\x97\xf1\xd5\xd6"9\x1c\xc9^\xc2Y\xfa\xf2\xeec\x99ktn`\x858k\x81\xeb\x12\x1e!ID\x86\x86\xd4?\xca\x82\x7f\xb9\x89\xa6\xc53\x18\xec\x08\x13\x0b\x87\xd5a\xbe\x10\x89h\xb7\x8b\xb7\xb2\x94E7_\x8b\xc3\xe3\xe1\xd0\x96M\x94\xd67\x18\xb9\xdb+\x8bQ\x9cV\xcc\xd6\x97\x00e\t\x8fP\x14\xc2\x83\x83\xcc\xb8\xfc\x03\xaa0\xfb\xdb\x83\xc4\x0bX\x98#\x88\xdb\x1b\xee\xf3\x13\x1aT\x98{\xcd\x87\xa8\x9d>\x93\xe1\xde^\xed\x83\xc4\xac\xc8~\xeb3\x8f\x15=\xe7\xb2d\x07\x84\xfd~*\x9b\x9b\x99\xbcl\x19\x81\xae\x18\x88\xc9A\x81\x0bs\x04I\x96\x08\r\x06(\x9fXF\xeb\xca\x15\xecx\xf0\xa0j\x93&y1g\x00\xff\x04\xec\xd1G\xa6\\G\xdcL\x14\xe8\x07\x0e\x03\x81t\xdak\x858[\x92\x1d\x10\x1d\x1e\xa6~\xf6l<\x15.\xfc\x1d\xfe\x82\xef1\xcfD\x08t\xa87JUK+\x95S\x9a\xf0wt\xe2.-M\xf8\x15\xe0\x8fYi\xec\xf8\x19\x02\xb6\x03\x9b\x80\xff\x03v\x1b=\xa3\x15\xc3zu\xa2\x0f\xc5\xecT\xf8\xfcJ\xeb\x1aPb\x14\x9d0G\x10\xf6\xb5\xa7\xbc\x84\x8aIM\xc4B\xa1\xdch\x945\x88\xd8\xdc\xf3\x81/\x01\xbb\x80\xd7\x80\x0f\x18\xb9\x92\x15\xe2\xf4&\xfcT\x88\xd3\xe1@v:Tq\x16/\x8a\xda\x1f:=^\xc5\x80;\xa9\x90x/\xf0\x17\xe0E`r\xa2\xfb\xcaF<\xa7\xfa\x87Q\x84#\xb38;M\r1b(\xdaHR\xa4\xcfa9pD\x0f:\x1f\x15+\xc4i\xac\x1b(\xae\xdebL\xe2\xb1X\xc1\xb8t\xd3D\x04\x9d\xdf3\xdaW\xad\x98\x10%}\xd4\xf1\xb8\x82\xbb\xac\x04\x9f:\xefL8\x11\xc8\x1a\xe2\xdd\x89G \x1a\x0e\x13\x8fD\xcco\x86\xa2 9\xc0\xe9vKbyS\xebI\x8bV\xa5w\xe8\xb3\xfb\xbbO\xfd\xe5x\xc4)&>s\x81z\xfd<Q=akR\xc2oI\x12N\xb7\x8b\xee\xfd\x07\xa4xT!\x1cH\xcb\xcb`\x1d\xea0+\t[\x10oU\x15\xde\xaajJjJU\xed\x84\x06"\xc4\xc2!\xd3\xdc^\xc2\x83V6q\x92:)4\xe0N*t\xee\xd2\x93\xff~=r\x9f\xa9f_.\xd7\x97&/\xd5}oi\x89[,\xe7\t_\xa7\xba"$g\xc9\xecM\x88\xe8\xd5\x9c\xb8\xcb\xca\xf0\x94\x97S>q\x125\xd3fP;s\x06%Un\x86\xfa#D\x87B\xaaKh<\xc8N\'N\x8f\x87\x1d\x0f>\xc0\xb1\x9d;\xa8h\x9a\\\xec=hD\x8f\xfdm#\x05q~\x18\x10\x07N7\xab\x15\xb9=CU\xd4\x7f\xe2\xd1(\xd1PH\xf5\xcb\n\xefBE\xd3\x14&-\\\xcc\xe4s\x97\xe0*u\x12\xec\n\xaa\xd1E\xe9\xf6xJ\\\xc1[QFdx\x88\xd7\xd7\xad\xa3c\xf7\xeb\xaa`eG6\x93bM@\x98,\xb2\x84\xd3[\xa2\xbe|\x88\x0e\xc8\xf8\xdf\xfbQ\xe0\x1a\x0c\x88s\xba\xee\xfc}o\xf6\xef8\x8b\x08\xf1\xc5\xe3\x84\x06\x07\x89\x04\x83TO\x9b\xc6\xac\xd5\x1fT\x039\x86z\xc3D\x87\xc3i\xf7\xa2J,\x8e\xb7\xaa\\\x1d\xd6\xdf}u;}\x87\x0f\xaa/En\x8e(\xc6\x10m\x8fE\xc2\x04::\xf1w\x1cCr:)\xa9\xacN%\xd2LD\xb5mH$\xce\x9b\xf5\x99\x94\xcd\x08z\x0f9\xd4\xd3\xad\x8ai\xe6\xea\x0f2\xf3\x03\xab\x88\x04b\x84\x03\xc1\xb4\x05%\xce%z\x18O\x85\x1b17R\xa2\xfa\x9aP\xbe"i\xf6tx\xd0O\xef\xc1\x03\x1cz~\x93\xfa\xd2\x890A\x03QX\x8c\xf4\x9ec\x89S\x04\n\x7f\xd9\x16\xe5\xe8\x08\x11\x8a\xa8\xaa\xa1\xee.ZW]\xc4\xfc\xeb\xae&2$\x04:4n;T5\x11\xf2}b\xf4\xf7I\xa5\x07o\xa5L8\x00o<\xf2G\xda\xb7\xbeHIm\x9d\x113H\xc4LNu\xb4,\xb9\xec\xcc\x0f\xd6\x1a\x8db/Z\x14\x05\x87\xcb\xa5\x06Ew\xec\xdeEd(\xc2\xa4\x85\xb3\x11\xde\x07%\x16\x1b\xbf\xb8\x14}\xf8\xcb\xd7\x1f\xfd\x1e\x84y\x12\x1a\x08\xe1\xf0\xb8\x99\xbct\x0e\xfe\xe3}\xf4\xb4\xed\xc7SV\x9e\xac\xf7\x14\x0f\xf0\xcd3\xc5)\xe20\xef+v\xed\x19E\xf4\xa0.\x9f\x8f\xce7v\xe3\xf4\x96\xd18o\x1aa\x7f\xa4XW|FE\xf4\x92\xd1\xe1\x10\x92\xc3C\xcd\xf4i\x9c\xd8\xb3G\r\x97t\xb8\xdd\xc9\xbe\xdaw\xaa8E9\x94\xf5\x80\'\xe3w\x90\xc7\xa8q\x02.\x17\'\xde\xdaC\xf5\xd4Y\x947\xd5\x11\t\x14~lj*\xa8\x02\x1d\nS\xdeX\xaa\x9a?\x1do\xecN\x16\x85%\x88\x9dj\xc1\x7f[/6e\x93\x02\xc2%&zO1\x84\xbd\xfd\xf4\xd3\xc4\xa3\xe0p\xbb\xecGx\x06\xc2\x16\x17\xd9\x00\xd5\xadS\xf1VV\xaa\xcf+\t\x13F\x1cj\xcb\x8c\xe4\xfd\x8c\xc2\x80\x1e]\xd2\xa7;\xe4\x0b\xa1\xbb\x88\xeaa^\xe2\x99\x18\xca\xa1\x10\xb3m\x91\x0f\xd4\xb5\xf7-\x8e\xed\xd8\xc9\x94\xe5\x0b\xf0wF\xec\xde\xf3\x0c\xa2\xa1\xb8j\xa7\x8b^S\xb8\xe5\x84O7\x01\xe5#\x9f\xaeI\xf1:"\xba\xf9sy\x1c\x00k\x94\x0b\x81\xef\xeb)\xba\x89\x91e\xf5a\x8b\x95\x9e\x89\x0b\x16\xa8\x8etu\xcd\xdc\xe6\x14\x14\x91\x8d\xaa\xe8N\xf9\xa4o\xae\xac\xaf\x8d_\x9b\xc2#|X\x8fv/ta\n\x9e\xd3\x8b\x1a\x8c\x1a5s\x1a\x8a\x82\xa7\xb2\x92\xbeC\x07\xe9=p\x00Oy\xe2\xb0\xd6bE\x19\xf1@\x18\x18Ud\xbd2\x87\xcf\xe0\xb3z4ifear\'\xf0\x9d\xa4\x0f\xd3\xe9$\xec\x0f\xd0w\xe8\x90\x9a\xe6l3>\x9c)\xd42\x12\xc9J\x9f)\xe2\xe7-\xaa\xbf\xad\x06\xe6\x8dy\x84\x88\xf2w:\xe9oo\xc7\xe9\x86\xb2\x86Ru\x82\x94\x17\xe8\x1d\x99X\xd9\x89\x89P\xc1\xa1\x90Z\x1a(\x9b\x0b\x02\xce\x14\xaa\x0b\xdf\xa7W$.fDa\xb2_$\xba\x7fQJ\xc7\xdfq\x9c]\x7fx\x1a\x87\xcb\xad\x96\xd8\xc9\x07\xd4\x08)\xaf\x17wY9%\xd55\x94Oh\xa4\xa4\xd6C$\x10\'\xec\x1f\xd2\xd3J2+T!\xce\xa9\x06\x8f}\xda\xe2\xb6\xe4\x03\xcf$k\xa3p.\x8b\xe0\xe4\xb6g\xff\xa6\xdaW\xf94c\x17\x8b\nb"\xe7,)\xa1|\xc2\x04j\xa6\xcf\xa4a\xee|\xaa\xa6T\x13\x0e\xc4\x08\r\x8e\x7fy6\x15\x9c\x06K`\x8b8\xbb\xb72\xd6\xaa\xdc\xe5\x88\xee\xa9h\x1e\xab\x85j\xd0\xb0\xc3\x81\xaf6?+\x8b\x8b\x17J\x89E\xe9i{\x87\xce7\xdf\xe4\xf0\x0b\x9b\x99\xb8`\x91\x9ac_\xdeXF\xa0k\x88x<\x96\x91\x97\xce\xa8or8\xdd\xc4\xf8\x02C,\x08\x07\x0b\xf9\x06\x85\xe8$\xa7K\xad\xf6\'Uie\x83\xf6\xaf\x7f\x9a\x8e]\xafs\xce\x07?D\xd3\xd2\xd9\x0c\xf5\x89`\xeba\xcb\xc3\xfa\xf27h0{\x14\xcd3\x13\xbd\xa8\xb0C+\x9a\x9a\x08\r\x0e\xb0\xedW\xff\xcd\x9e\xc7\xfe\x86\xa7\xcc\x85\xbb\xd4\xa7\x8e\x12V\x92\xe7!\xd7Y\xc1\xda\xbfH\x0e"D(\xf2\xa9\x9c\xa1\x12\xf6=\xf9\xb8Z\xb6r\xfe?_\x85\x12/!2<l\xd9\x10o\xf7\x9c\xa9s0\xdf\x1al\x06j@\xb4\xdbM\xd9\x84\t\x1c\xd8\xb8\x81\xb7\x1e\xff\x0b\xdeJg\xb2%\xc8qa\x8b3u\x1e\xcf\xb7\x06\x9b\x85\xea}p:\xd5\x02\xbf\xfb\xd7?\xc3\xe1\x17wPZ\xe7Us\xa1\xac\xc0\x16g\xea\xdc\xa7/k\x16\'j\xa0\xb5[\xcdL\xdd\xfb\xc4\x13\x0c\xbc\xdb\x8b\xb7\xaa\xcc\x92\x84E[\x9c\xe9q\xb1^1\xad(\x11\x19\xa7b\xb1a\xa8\xb7\x97\xb6\r\x1bpz\xb4\xf2\xe2fc\xc8`h_V\xe5>xa\xedc\x8a\xacZ\xbe\xc39\xfc\x07i\xd1\x93\xf2\xbe\x9d\xf0\xa8\xe6J\xeeY\xbb\x91;\xbe\xb9\x05\x9a\xab\x92\x9d\xf3N=\x9c\xf0\xf0\x99\x1f\x04\x9c\x8e\xe7\xfb\xdc\xae\x1a\xdd\x1d\x97\x95\\\xe7\xf2H\xb4f[]\xc5\xe6\xaf,\x9c\xf9\xd74O!\xda-\xc2\xa7j\xf4\xeao\x97\x1a\xfa\x92\x1e&x\xfc\xf5\xd7hZ\xba\x94\xea\xd6f\x86\xfb\x02\xa6\x06M\x1a\x12g\xa0\xde#+\xb2t\x91y\x97\xb5\x94\xeb\x93\x8a35>\xa9o\xb5}\xd6\x0et\xa5\xd1\x98\xfa\x93m.:\xd6\xe3\xff\xcaB\xee7\xa1\x19"\xb8\xa5\x11x\x10\xb8<\xd9\xc1b5,\xd8\xd3\xa3\n\xb4vf\xb3\xe9\xd1\xbc\x858\xacOOZ\xf6\xdb8\xb3ta\xe6:f\xf6\xda\x1dz\x0f\xfa\x8dd\x07\n;S\xd8\x9e\xbd\xef\xb4\x11\xec\xf2\xabu\xee\xcd\xa4\x10\xc5Yab\x11\x88E&\x9d\'\x1f\xb9K\xefA\x13\xe2*\xf1\x11\xe8>A\x7f\xfb\x11\xdc>s\xddJ\x85:!\x1a;\xacM\xc7\x1d1\xe4K\x7f\xbfI\xed\xc9WD\x98\xa0?Q\xdbE \x88\xa8\xcc\x1c<qB\xad\x9ag&\x85*\xce\xb9\xc9\x0eH\x9e$\xa02\xdf\x8c\xc6\xe41\x9d\xfa\x1e\xf9\x89\x91d\x82\xdd=Z\xec\xaa\x89\xabE\x85*\xce%\xc9\x0e\xf0\r\'\x8d\xb3\xac0r\x9e"`C\xb2[\x14E\xceB\xfeAb!\xc5\xd4`\x90B\x15\xa7(\xcf\x980?\xd7\x95|\x97\xb89v\xaa\xb4\xca\xa1d\x07\xa8[(\xc6b\xa6\x87\xd2\x15\xaa8\x1b\x92\xda\x9d\xeaCL\xf8 \xcf7\xbbQy\x8a\x05e\x9d\x8dQ\xc8+D\xe3\xb5\x17\x93\xa7\x03\x17\x07\xc64bA`R!\x8b\xf3,\xa7\xf9i\xa8\x0f3\xe1\xb0n\xdb\x9bY\xa6\x90\xc5\xb9<\xd1\x87\x92\x1a\xa80\xe6\xeb\xde\xa2\x97\x7f\xb6\xc9"\x85,\xceE\xa3Nh\xf4\x1e3\x89\x9f\xd3\x1e\xd2s\x80B\x16g\xb9>k?\x1d1\x11\x8a\xc6)\t\xc7\x12\xf5\x9c\xe7e\xac\x956cbL\x9c\xe5.\xa8+\x81j/\x94\xb9\xc0\x997\x9a^x\xd6o\x848#q\xca\x82\xd1D\x0e\xe3\xe2\xae\x81\x9f#\x18Z\x0c\xado\xf7\xe3\xf3\xc6\x18r\xcbtUx\x88M,\x85\x92\x12-\x9d\xa6/\x08\xfd!\xad\x17\xca\xbd\x14\xed\xf7\x9d\xf5\x1b\xbd\x8dR|L\x9bS\xdc\xd8R\xcb[f\x93\x14C\xe2\xfc\xce\x8f\xb7\xb1\xba\xfd\x041\x97L\x9f\xcf\xc5\xde\xd6Jv\xce\xa8f\xfd\xe2\t<\xb5r2\xe1\x96Z\x10\xa5K\x8e\rBL\x81\x0c&\xde\'a\xf6Y\x1f\x8fL\xd0\xc7\x9e\xad\x9f\x93\'{\x9a\x17<\xc6\xc2H\xa2q\x18\x8e\xe2\x08Bm\xf70\xe7\xed\xe9\xe6\xbcx\x9858\t\xcd\xa8a\xdd%-|\xe3\x86\xb9\xbc\xbdb*\x84\x86\xe1\xe8\xa0\xb6\xf7L\xf65\xbaP\xaf\xd4\x9c\xca\x9e\xd1\x17X\xd8\x1e\x9b\x140f<\xba\x1d\xe0si\xf6f\x95\x07&\x97CK\x9d\x1aQ\xee\xe9\x0cr\xd3\xcf\xb7\xb2\xef\xb2u\xfc\xfe\xe3\x8fQ}d\x00\xa66\x80K\xd6z\xd1\xecR7\xea\xa4\x88\x84\x01\n\x17\xda\x02\xca\r\xd2\x9f\xd9\x8c$4\t\xb1N\xad\x87J/\xd7\xfdj\x1b=K~\xcd\xcd\xbfx\x05&Uk\x9f\xc5\xb2\x9e\xe6}\xfa\xe4F\xd2\x93\xb4D\xbbF\x17h\xd2p;\x9b\xcc`\xce\xb4[\xf4\x90^\x07LkP\xc5\xf8\xc0\xa7\x1f\xe5\xc7\x9f\xfb\x0bT\x97A}\xa9f\x16d\x8f\xd3g\xecB\x8fQ\x05\xdfpl4\xdbxF\nU\xf7l,\xc6\\\x9f\x90\x10a\x9d\x0f&\xd4q\xdb\x0f\x9eg\xdd\x8d\x8fB\x99\x1b\xea}\xd9\xecAO\x9f\x14\x89\xde2\xa6\xfb9\xcf\x16\xa7\xed|\xcf!\xcc/\xd7 \\4\x1e\'Ln\xe0#\x0f\xbdJ\\\x92\xf8\xd8o\xaeV\'T\x04\xb3R\x8ct\xe1i\xd9\x91\x92\xd6\xd3{F\x17\xe7\xb9\x99n\x9c\xcd\xd8X\xe3M\x17\xf6\xa8C\x82\xc9\x8d\\\xff\xbf\xaf\xf2\x9f_\xdb\x04\xf5ISp\xad\xa2i\xccI\xd1\xd9\xd8\xe2\xcc!\xac[\xea\x11\xfd\x94XI\xaa\xad\xe1+_~\x8e\x0b\xff\xfa6\xb4\xd4dkxO\x9a\xb6\x01x\xed\xc9Pna\xed:\xa4\x18\xe2+<\xeaX\xfa\xfd\xbb6B(\xa2\xd9\xa0c#\xf6\xdd|\xd9\x82\x96,6p\xcc"\x93\x9d\xef\xa2\x08\xc3\xed)\xfaXmN\xc1\xfaEr\xd1S\xb6T\xb3\xe0\xe5\x83\xdc\xfe\xb3mP_\xa9\x89vt\x1e\x01\xfelA+N\x86\xbf\x8d\xacZJ\x9c\xb99\xa8\xd9\xeb\xe9\xaf\xe8\xc9a\xf6v\x8di\x92\xb9\x08\x0e\xb7\x8f\xcf>\xb0\x0b\xa9k@s\xe6\x8fN\xd8\xa2\x9e\xf3\xa4;I\x9f\x10\xc9\xb1\xb3\n\xf0\x9b\xbd2\xf4\xac\xbd\xc1\xc3\xf8\xc8\x8c8E\x0f5\xb1\x94\xd6]\xc7\xf9\xc8\x13\xef@\xdd\x98[\x1a\x8bJ\x1d\x1b-h\x81\xa8\x022E\xfd/Y\x8bJ\xf2\x88x\xce\xd3g\xebf\xa7\x01\xbfd\xf2\xf9\x8a\x8e\x0c\xc6\xbeiB\xb8\xe6\x99\x03Z4\xd3\xe8\xc1!bJ?\xa4\x97D1\x1b-mC\xd4<\x8f\xc5q\t\x9f\xec\xc9\xbbo1yX\x17\x85\x08\xb6\x19\xdc\x0c\xc2f\x0c2\'N\xd1SV\xf8\xb8h\xc7q\xbcm}P:\xea\xd0>\x12\xb9\xbe\xc5\x82\x16hi\x1b\x12\xea\x90.\xc7O\x1b\xd6\xcf\x0e\xad\x1b\x1f#\xed\xcf\x9a\xff\xac\x10\xc8l\xd4p\x99\x8b\xbaw\xfd\xcc{\xbbG\x9f\xc5\x9f\xc5HA\x93W-\xb8\xfa\xc9\x845\x893\x8b\x16\x1a\x99\xcd\xa7\xc2V\xfdX\xbb\xe6\xfe8\xc8\xac8\x85\xdfsp\x98\x85{\xbb\xc1\x99\xb0\xe6A\xd2\xcd\xa8\xd2`V\x82\xaf\x98]\xde\xf1Y\x93\xcfW\x94d%\xdfbR\xf7P\xb2\xb4\xdcm\xa3\x15k\x1d\'\xb3\xc6\xd8\xad\xae\xc2\xe4a}\x10\xd8nr\xdb\x8b\x92,\x0c;\n\xd5ACE$^M\xb4SZ\x9a\x88\x15\xa0\x03g|u\x9e.P\xb3xA\xdf\xc4\xd6\x02Dr^\x0c\x06\xc2\xe0\x0f\xe9\x05\x89\x0b7G1+6\x91;b(\x08Y\xb8\x94\xae1\xf9\xd2s\x91\xf8\x93,v\xf7\x8d\xff\xdd\x81`v\x99Cs]H\xc2\xab!\x82T:\x02\xdav\xbee>N\xcc\xa8\xe6\xa59\xb5\xec\x9bRA\x7f\xa9\x8b\x98\x84\xc4\xbb\xa6^5\'\xc8\x8a8\xc3NC\x91I\xdb,\xb8\xf4\x12\xf1\xc7\xf6\x84\xe3xOF%\x99\xbd2\xb4\xc9\x94\xb3\x88\xc0\x99P\x0c\x8e\xf6\x83\xcb\xc5\xeb\x17\xb7\xf0\xe0e\xad\xfcy\xe9D\xf6\xcc\xa8Fi*\x07\xc9\xa9\x99G\x8a\xc2\x8a5V\xcc!\xb3K\x16\xc4)\xd17\xba\x1b\xe9L^\xd6\xfd\x9d\x8d&^\xfc\x1c!Hw8\xa6\xfe\xa8\x02HR\x19$E\x06\xc7\xfdRIz\xcc\xe9\xc1~u\xf3\xf3g>:\x9f/|\xf2\xbd\xecZ5\x05\\"\xb3 \x0c\xbd\xc3\xd0>\xa0\xed%\x97\x93I\xaf\xe6\x90\x95\x9e\xf3hM\x89\x91\xcaOQ}b\xf1\x0f&^Z8\xe2\'!qTw%5\'\x99\xc5\xa7\xcaK\xe3\xb27\xc5\xcb""\xf4\x8f\xf5\xd0\xb6\xb8\x99\xeb\xbf\xbe\x92\xad\xabgj\x8b\x16\xa2\x07\r\x0f\x9e\xbexQ\xa8\xaa\xd4\xc9\xac8\xc5\xaaL\x99\x97\x9d\xe7\xe8\xa9\xc4\xc9y\xcedq\xca\xfa\x04\xe8\xa8\xfe\xff\xcbL<7\xfad(=\x840E\xfe\x7f\xcf ?\xbbu9\xb7\xfe\xe0Rp\xba\xa1\xbd[M+QE\x99;)\xd7\x19!\xb3S\xbd@\x84\xee\xa62v\xcd\xac\xd6f\x9c\xc9\xb1\xc2\x90:\xb5@\xd7\xd9\x15A\xc6\xc7\xf3i}\xdb!kCu\xcf \xb7\x7f\x7f5\xb7\xfe\xe4J\x08\x86\xa1\xed\x846t\x17\x99(G\xc8\x9c8\x85\x1d\xd5\x1fd\xe3\xc2F\x86\xa6WA\xc0\x908\xc50\xd9kj;\x14\xceU\xdb\xa2-]\x9aY\xe60={S\x08o \xa4VN\xf9\xf8\xfdW\xf2\xa3\xcf^\x00\xc7\xbb\xa0g8\x9f\xca\xfeXB\x86\xef^\xe1\x91\xcbZ5k\xc2\xd8f\x9eb\xe3\xfd\x9d\xa66A\xe2=\xa2\xfc\xa1V\x02\xd1\xd4\x8461\x81\xebK\xf9[\xc2\xd4\xe9\xee\xe7\xdf\xef\xb9\x98_}j\x19\x1c\xed\xd2\xf2\xad\x8a\xb4\xb7<\x95\xcc\x88S<\xe7\xe3~\x8e\xcc\x9d\xc0\xef\xfeq\x06t\r\xa6\x92\xe8f\xf2&\xa8\xd2lG\\\xc1\x11WZ\x90\xa87\xf1\xc4\xa9\x07\xab\x88\x9e\xb1\xbd\x87u\xd7\xbf\x8fo\xdf\xb1\n:\xbb!2j\xe2]Q\x92!q\n\x9f]\x90\x1f\xde4\x9fXC%\xf8\r\r\xe9#\xbcbj[d|\xce\xa8R\xeb\x8a\xc6\xe7\x98\x9c\t\x9aZ\x04\xbf\xb8\xf61?\x9d\xad\xb5|FL~\x86\x83\xaaM\x9e\x85\xec\xd4\x9c\xc5zq\x8aY\xe8\xc1>v-i\xe1\xbb\xb7-\x02\x11\t\x9fZ\xcf\xb0\xc9\\\xbbS\xc2\xa1(\x97Jq\x96\x99\xe8\x8a\xe9Hy=]\x98\x15CC\xdc\xb9\xf6|\x06\x1a\xaa\xb5\xfaR\x0e[\x98\xa7b\xad+I\xf4\x02\x83\x11\xd5O\xf7\xf9\xaf\xad\x84\x12\x8f:\xbc\xab\xb3S\xe3\x04\xf4\x89\x91I.%\x05E\x92\xd6\x99\xec#|9\xa5]\'\xc4\xb5\x8f\x0c\xb2m\xd54\xfe\xe7\xa6y\xd0\xd1S\xf4\x93\x9f\xd1\xb0\xee\x89Hz\xf6eW7\xdf\xbck\x05\x7f]}\x0e\x1c\xeeMU\x98#X\x91Wd&)\xda\x9b\x12\xc4#\xfc\xe4\xc6y\xe0\xf2B0\xe9\x86]E\x895\xe2\x14=\xa6\xf0\xcf\x1d\xe9\xe0\x91\x8f,d\xed\xd7.\x84\xae\xfe\xb1\xf2\x86\x8c`E^\x91\x99\xa4\xb6\x9e\xde;L\xd7{\x1a\xf8\xfd\xe5\xad\xd0;`\x0f\xe7c`\xbe8\xd5\x04\xb2\x18\x1c\xe9\xe4\xb1k\x17p\xedo\xaf\x02\xff0\x0c\x86\xc6c\xec\xefL\xb6Ah\x16\xe9L\xd9\xde\x1c\x08\xb2~E3\xc1\xe6j\xcd\xc7i3*\xe6\x8aS\xd8M"\x90\xf8h\x17?_s\x1eW\xff\xe1\xc3\xda\x90\xd5\x19Hw8\x1f\xa1/\x87\xb3\x19\xb7\xe8)\xcd) \xf1\xcc\xb9\x13N\xc9\x17\xb1\x19\rs\xc4\xe9\xd0c\x0e\xdb:\xd5\xa1{\xcdO>\xc4-?\xbdB\xab\x17\xdf\xe17\xcb\xd8\xb7"\x84\xce\x0cR\xb3\x87\x85\xd3\xbd\xdc\xcb\x9b-\x15\x10\r\xdb\xdaL@\xfa\xb3uI\xff\x97\x08V\xe8\x1b\x00\xa7\x87\'>\xb6\x80O\xad}?\xc7\xe7L\x82c\xbd\xdaJ\x87y\xb3P\xe1\x8c\xff\x0f\xb3Nf"\xa9\xd9\x9b\xc1\x08\x83M\xe5\xbc\xd5R\x95\xaa\xbf\xb7\xe80&NQ\x80@\xf4\x8cb\xf6-B\xba\xc4\xba\xb8\x88\xcaF&\xdaR\xcd\xc3\xd7,\xe1\x1b7\xcca\xf7\xc5\xd3!\x12\x86\x03\x9dZMxs\r\xfd\x1d\xba\xbb\xc6P0h\x868\x91\xb2\xbd\x19\x8a\xd1Y[\xc2@\x95W\x0b&\xb6\x19\x13c\xe2\x8c\xc7\xb5\xe1\xc8)\xd3\xd3\\\xc1\xfe\xc9e\xbc\xd9R\xc9\x9f\x97M\xe2\xa9\xf3\x9b\xf0\xcf\x12\x15\x8d\xa3p\xa4G\xabr<>\xfbr,:\xf4!4\x976\x14\xd8\x9cr\xa1\xae\x98\x82_T\x81\x16\xd9\x00v\xc7\x99\x10C\xe2\\\xfb\xaf\x8b\xf9B\xab\x97\x80\xc7\xc1\xd1\x06\x1f\xe1\t\xa5\xe0\xd3\xaa\xc7\x89\x99\'\x87z\xb4\x03%\xcb\xc3\xbb\xb6\xe5\x988\xd3\xf2\xbf*\xf6\x12\xa5!\x0c\x89\xb3}z5\x9dK\xab\xb4d?aG\xf6\x85\xa0k\xe8\xe4\x01\x99{\xd6\xcf\xe9e\x05s\x85\xd4\xfd\xaf2xCqm\x84\xb15\x9a\x10c\xc3\xba\x98\xf4t\x04\xb3\xd6\xc8S\xd8\x91\x0b\x8d\xd0iK\xcb\xbd\xe5rP70\x8c\'\x10!$\xb6m\xb4\xed\xce1\xc9\xb7\x05\xddC\xa6G)\xa5Oz\xed\xf0i%y\xa6\x1fIX\n\xb2\xe8!O3\xf2s%\x07vCZ\xdf\x12\x1b\x8eu\x05\x99{x\x00<v]\xd9D\xe4\xa38\xd7\xe7@\x1bH\xbb\xe7T\xed\xcc(+wvh\xff\x93~\xbcA\xc1\x93\x8f\xe2|!\xf5\xe5B\xd3i\x1b\x97\xfd\xeb\xf1p\xc9\x0b\xefB_\x00\xbcv!\xba\xb1\xc8Gq\x8a.\xe7\xf5,\xb7a|\xa6E\xbd\x8f\xd9/\x1f\xe5\x92\xcd\xed\xd08f\x95\xe7\xa2\'_#\\\xcd)\xf9\x92>\xe9\xd9\x9b#\x88%\xddX\x94[~\xbfG+Ij\xfb=G%_\xc5\xb9\xd5\xc01\xb9{}\xb1\x0c<\xb1\x92k\x1fz\x83U\xeb\xdf\x06\x11:\x97\xfd\rls\x8e|\x15\xe7\x96d\x05>-\xe4\x1dS\xfc\xadb\t3\xaep\xef\x7fm\xd1\xca\xcd\x94{\xec\xe1\xfd\x0c\xf2U\x9c\xed\xc0\x9bY\xba\xb69\x85a\xc5\nQK\x15\xcb6\xb7\xf1\xc5{_\x84\xba\x1aSN[H\xe4sVU\xb6R7\xc6go\x9eIM\x05\xdf\xbas#+\x9f\xdd\x0b-\r\xd9\xde\xfe;M\xb4\x1e_\x16;\x95\x18\xf8\xd1H>J\xe4\xb3\x1f#[+E\xe6\xd9\xbbb\x18\x17\xa1s\xfe0O]\xf7(\x8b6\xdd\xc8\xbe9\x13\xe1\xc0\t-\x80&O\xe6IJ\\Av\xc8x*\x1d\xc4\xa3\xe2g\xf4-$]\xa2\xb8 %\xea\x04\xd0\x88\x05\x93\xcf\xe2L\xafh\xd6\xf8h3\xbd\xde\xbb\xe8)\xa7TP\xda\xd6\xc7\xf6\x95\x0f\xb1\xe2\xc9\xeb\xd8\xb1l*\xb4\x9f\xd0>\xcb\x83\xea\x1f\xaeR\x1fC\xbd}\xec~\xf8)5\xbcR\x19Cy\xb2\xc3A,\x12\x91\xe2\x91\x08\x0ew\xc2=PU\xf2Y\x9cbb\xb2W-\x08\x9b9\xac\xe9\xadE0\xf7\xb4*J\x0f\xf6\xb3}\xd5C\\\xf7\xcb+x\xf8c\x8b\xc0?\x08\'\xc6\x9d\x7fe9N\x8f\x97\xb0\xdf\xcf\xc1M\x1b\xf5\x04\x89\xd1_(!ZI\x96)\xa9\xaa\xc2\xe1t\x8e)\xe2\x11\xf2}ybK\x86\xc5i\xc5\x164\x1aB\xa0-\x95j\xed\xf7?\xdc\xf0(?\xddz\x8c\xdb\xbe|>Lm\x84\xee>\x18\x0c\xe7l/\xaa\xc4\xe3\xc8N\'\xbeZ\xe3\x9b.\'\x13&\x05\xb0\x15C\xa6\xfd\x9d\xd6:\xff\xc50\xde\xe0\x83\tU\xdc\xfa\xc3\x17\xe9[\xf6 \x1f\xbf\xef%\xad\'jm\x80I\xe5\xe0qd\xcf\x89\x96a\xf2\xbd\xe7\xcc\xe4fTb9g\xbf\xe5W\x11.&\x8f\x0cS\xeb\xa9<:\xc8/\xd7<\xc9=\xf7\xbf\xc6\xfdW\xcd\xe4\xa1\x8b\x9a\xd9;\xbf^[\xf2\x1c\xd9\x82N\x89\x89\x7f\n\x92|\x17\xe7>\xe05\x0b\xf6\xae\x1c\x8d\xcd\x19\xb8\x86\x86\xa2\xefS__\n\x94\xd2\xb8\xaf\x87\xbb\xbf\xfa,w\x7f\xaf\x94\x83\xf3\xeb\xd9\xb0\xa0\x91\xfd\x93\xca8\xdc\xe0\xe3x\xbd\x8f\x88K.\xc8\xce\xb4\x10Bb\xb6\x15\x9c8G\x18\xb1\xcb\xeaJ@\xf6\xa9\x19\xb0\xad\xdb;\xf8\xc4\x0b\xfa\xe6v\x92C\x8bjrH\xca\xca\x1b/\xccx\xf3,\xa6\xb3\x10\xc4\xf9\x100\xf9\x94M\x08\xcc\xc6\xa5\xbf\xc4\xd9\xdd\xcfR\xac\xc7\x8b\x80\x11a\x93\xe2\xd3~\xa7\xe8\xbf/\xcce\xcf\xc7\nA\x9c\x1bL_\xb5\xc9\x17$\xbd\xdaJ\xe1e\xca\t\x7f\xf2\xddvQH\x9b\\\xe3Y}#\x89\xa0\x1d\x86mc\x16\x07\x81/\xe9&P\xf2\xe5\x9f\xd3q\xe8n\xcd\x97\xf4\t\xae\x8a-N\x1b\xb3\x10\xa5y\xd6\x99\xf94\xeda\xdd&g\xb1\xc5i\x93\xb3\xd8\xe2\xb4\xc9Ylq\xda\xe4,\xb68mr\x16[\x9c69\x8b-N\x9b\x9c\xc5\x16\xa7M\xceb\x8b\xd3Z2\xb5\xe8m\xe5u\xb2\x16U\x92S+DRL\x91/\xf8\xd6;\x8eL\\k\xe5\x15\xcb,\xbf\xc6\x13\xeb\xb7\xc9\x15\x11\xeb\xb7\x0e\x8ck\xd2\xb4\xe2\xb9\xc5,:\xaf!\x0c\x89\xb3\xfa@\xd0))J@\x91$E\x8e)\xe6\xbf\xa5\x12D\xbd\xb2\xdc\xbc\xa5\xf7\xfe\x9468\xcdqn^1_\xfe\xf4\xbe#bcY"\x925\x83TM("o\x9eP}5p\xb9\x05\xa7\x8f\x9e\x8c\xcf\xcb<\xd2\x8a[\xee\x1d\x00\xca\xb3\xd5\x00\x9b\x82Ad\xa6\x9ek\xe6\xcd\xd86\xa7M\xceb\x8b\xd3&g\xb1\xc5ic\x16\xa6kINy\x072\x1b\x9b\xd11]G\xb2\xe9\xb5\x7fl\x8a\x15\xd3u$\xc4\xf9K[N6&`\xba\x8e\x848\x7f\x07\xfc\xc8\xfe\xeb\xd8\x8c\x83[\xad\xd8]o\xc4\t\x7f\xbb\x9e\\$\x12\x94Z\xf4\xdf\xd9\xfb\xde\xd9\x8c\x85\xd0\x8dp\xd0\x8b\xea\xd2k-)\xe4\x0b\xfc?\x9d\xa4\xc52\xfeYp?\x00\x00\x00\x00IEND\xaeB`\x82'
                    )
                ),
                title=f'{__title__}\n'
                      f'版本号: {__version__}\n'
                      '状态: 一切正常',
                menu=pystray.Menu(
                    pystray.MenuItem(
                        text='MoFish',
                        action=self.HideShowHandoff,
                        default=True,
                        visible=False
                    ),
                    pystray.MenuItem(
                        text='复位',
                        action=lambda: self.root.geometry(
                            f'{int(self.root.winfo_screenwidth() / 2)}x{int(self.root.winfo_screenheight() / 2)}'
                            f'+{int(self.root.winfo_screenwidth() / 4)}+{int(self.root.winfo_screenheight() / 4)}'
                        )
                    ),
                    pystray.MenuItem(
                        text='最大化',
                        action=lambda: self.root.geometry(
                            f'{int(self.root.winfo_screenwidth())}x{int(self.root.winfo_screenheight())}+0+0'
                        )
                    ),
                    pystray.MenuItem(
                        text='官网',
                        action=lambda: os.popen(
                            'start https://moyeransoft.netlify.app'
                        )
                    ),
                    pystray.MenuItem(
                        text='[EXIT]',
                        action=lambda: [
                            func() for func in (
                                lambda: toast.ToastApplication(
                                    title=__title__ + __version__,
                                    message='强制退出一般用于软件卡死时的强制, 可以做到极为安静的强制退出软件.\n'
                                            '若是试图体验真正的无申明强制退出, 请点击下方的笑脸☺.',
                                ),
                                lambda: time.sleep(3),
                                lambda: os._exit(-1)
                            )
                        ]
                    ),
                    pystray.MenuItem(
                        text='☺',
                        action=lambda: os._exit(-1)
                    ),
                )
            ).run,
            daemon=True
        ).start()

    def LineNumberModeChange(self, *args):
        if self.lineNumberMode.get():
            self.LineNumber = LineNumber(
                master=self.LineNumberArea,
                text=self.informationShower,
                bar=self.informationArea.vscroll
            )
        else:
            self.LineNumber.pack_forget()
            self.LineNumberArea.configure(width=1)

    def add(self, path, mode='local'):
        path = path.replace('\\', '/')
        if mode == 'local':
            if os.path.exists(path):
                if os.path.isfile(path):
                    self.addTask(path, mode)
                else:
                    showerror(title='ERROR', message='Not A File!')
            else:
                showerror(title='ERROR', message='No Such File!')
        elif mode == 'web':
            self.addTask(path, mode)

    def addTask(self, path, mode='local'):
        taskFrame = Frame(
            master=self.taskArea,
            bootstyle='success'
        )
        taskFrame.pack(fill=BOTH)

        topFrame = Frame(
            master=taskFrame,
            bootstyle='success'
        )
        topFrame.pack(fill=BOTH, side=TOP)

        rightFrame = Frame(
            master=topFrame,
            bootstyle='success'
        )
        rightFrame.pack(side=RIGHT, fill=Y)

        leftFrame = Frame(
            master=topFrame,
            bootstyle='success'
        )
        leftFrame.pack(side=LEFT, fill=Y)

        LeftTopFrame = Frame(
            master=leftFrame,
            bootstyle='success'
        )
        LeftTopFrame.pack(side=TOP, fill=Y)

        LeftBottomFrame = Frame(
            master=leftFrame,
            bootstyle='success'
        )
        LeftBottomFrame.pack(side=BOTTOM, fill=X)

        Label(
            master=LeftTopFrame,
            text=' ' + path + ' ',
            bootstyle='inverse-info'
        ).pack(side=LEFT, padx=5, pady=2)

        Label(
            master=LeftBottomFrame,
            text=' ' + mode + ' ',
            bootstyle='inverse-' + __local_web_bootstyle__[mode]
        ).pack(side=LEFT, padx=5, pady=2)

        taskButton = Button(
            master=rightFrame,
            text='执行',
            bootstyle='danger'
        )
        taskButton.pack(side=RIGHT, padx=15, pady=10)

        trashButton = Label(
            master=rightFrame,
            text=' t ',
            font=('IDEM', 20),
            bootstyle='inverse-success'
        )
        trashButton.pack(side=RIGHT)
        trashButton.bind(
            sequence='<Button-1>',
            func=lambda event: self.removeTask(task=taskFrame)
        )
        trashButton.bind(
            sequence='<Enter>',
            func=lambda event: trashButton.configure(foreground='#000000')
        )
        trashButton.bind(
            sequence='<Leave>',
            func=lambda event: trashButton.configure(foreground='')
        )

        Frame(
            master=taskFrame,
            bootstyle='danger'
        ).pack(side=BOTTOM, fill=X, expand=True)

        self.bindTask(
            taskButton=taskButton,
            taskFrame=taskFrame,
            path=path,
            mode=mode,
        )
        self.TaskFrames.append(taskFrame)

    def bindTask(self, taskButton, taskFrame, path, mode='local'):
        if mode == 'local':
            taskButton.configure(
                command=lambda: [
                    func() for func in (
                        lambda: Thread(
                            target=self.CDF(
                                path=path,
                                mode=mode
                            ),
                            daemon=True
                        ),
                        lambda: self.removeTask(task=taskFrame),)
                ]
            )
        elif mode == 'web':
            taskButton.configure(
                command=lambda: [
                    func() for func in (
                        lambda: Thread(
                            target=self.CDW(
                                path=path,
                                mode=mode
                            ),
                            daemon=True
                        ),
                        lambda: self.removeTask(task=taskFrame),)
                ]
            )

    def addINFO(self, message, mode='default'):
        self.informationShower.configure(state='normal')
        self.informationShower.insert('0.0', message + '\n', mode)
        self.informationShower.configure(state='disabled')

    def clearTasksThread(self):
        Thread(
            target=lambda: self.clearTasks(),
            daemon=True
        ).start()

    def clearTasks(self):
        for task in self.TaskFrames:
            task.pack_forget()
        self.TaskFrames.clear()

    def removeTask(self, task):
        task.pack_forget()
        self.TaskFrames.remove(task)

    def CDF(self, path, mode):
        self.addINFO(
            message=f"{timeNow()}: "
                    f"cd {mode} file[{path.split('/')[-1]}] "
                    f"from {path} "
                    f"to http://{self.host.get()}:{self.port.get()}/",
            mode={
                True: 'success',
                False: 'error'
            }[
                CDF(
                    path=path,
                    host=self.host.get(),
                    port=self.port.get()
                )
            ]
        )

    def CDW(self, path, mode):
        self.addINFO(
            message=f"{timeNow()}: "
                    f"cd {mode} file[{path.split('/')[-1]}] "
                    f"from {path} "
                    f"to http://{self.host.get()}:{self.port.get()}/",
            mode={
                True: 'success',
                False: 'error'
            }[
                CDW(
                    webURL=path,
                    host=self.host.get(),
                    port=self.port.get()
                )
            ]
        )

    def initSystem(self):
        if len(sys.argv) == 3:
            self.host.set(sys.argv[1])
            self.port.set(sys.argv[2])



if __name__ == '__main__':
    m = UploaderTkGUI()
    m.host.set('0.0.0.0')
    m.loads()
    m.binds()
    m.Menu()
    m.mainloop()
