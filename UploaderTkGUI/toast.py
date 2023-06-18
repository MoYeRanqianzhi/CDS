from tkinter import *
from tkinter.ttk import *
from tkinter import font
import sys
from ttkbootstrap import Toplevel

import MoFont
import constants


class MoMenu:
    def __init__(self, binder, data=None):
        """
        Parameters:
            binder: A Tkinter Widget.
            data: Menu data.
        examples:
            binder: Button(master=root, text='MoMenu')
            data: {
                    'File': method.file,
                    'Edit': method.edit,
                    'Help': method.help,
                    'everything': method.everything,
                    'example': lambda: method.example(parameter=parameter)
                }
        """
        self.binder = binder
        self.data = data
        self.style = Style()
        self.setStyle()
        self.bindMenu()
        self.window = None

    def setData(self, data=None):
        self.data = data

    def bindMenu(
            self,
            sequence='<Button-1>'
    ):
        self.binder.bind(
            sequence=sequence,
            func=lambda event: self.popMenu()
        )

    def setStyle(self):
        self.style.configure(
            style='default.TFrame',
            background='#FFFFFF'
        )
        self.style.configure(
            style='default.widget.TLabel',
            background='#FFFFFF',
            foreground='#000000',
        )
        self.style.configure(
            style='_default.widget.TLabel',
            background='#2675BF',
            foreground='#000000',
        )

    def popMenu(
            self,
            x=None,
            y=None,
            style='default'
    ):
        if x is None:
            x = self.binder.winfo_rootx()
        if y is None:
            y = self.binder.winfo_rooty() + self.binder.winfo_height()

        self.makeMenu(x=x, y=y, style=style)
        self.window.focus_set()

    def makeMenu(self, x, y, style):
        self.window = Toplevel()
        self.setWindow(x=x, y=y)

        interface = Frame(
            master=self.window,
            style=f'{style}.TFrame'
        )
        interface.pack(
            fill=BOTH,
            expand=True
        )
        menu = Frame(
            master=interface,
            style=f'{style}.TFrame'
        )
        self.walkData(menu=menu, style=style)
        menu.pack(
            fill=BOTH,
            padx=5,
            pady=5,
            expand=True
        )

    def setWindow(self, x, y):
        self.window.overrideredirect(True)
        self.window.wm_attributes('-topmost', 1)
        self.window.geometry(
            f'+{x}+{y}'
        )
        self.window.wm_maxsize(
            width=int(self.window.winfo_screenwidth() / 8),
            height=int(self.window.winfo_screenheight() / 4)
        )
        self.window.wm_minsize(
            width=int(self.window.winfo_screenwidth() / 30),
            height=0
        )
        self.window.bind(
            sequence='<FocusOut>',
            func=lambda event: self.window.destroy()
        )

    def walkData(self, menu, style):
        """
        遍历data, 创建menu组件
        """
        for text in self.data:
            widget = Label(
                master=menu,
                text=text,
                style=f'{style}.widget.TLabel'
            )
            self.widgetBind(widget=widget, text=text, style=style)
            widget.pack(
                fill=X,
                side=TOP
            )

    def widgetBind(self, widget, text, style):
        widget.bind(
            sequence='<Enter>',
            func=lambda event: widget.configure(style=f'_{style}.widget.TLabel')
        )
        widget.bind(
            sequence='<Leave>',
            func=lambda event: widget.configure(style=f'{style}.widget.TLabel')
        )
        widget.bind(
            sequence='<Button-1>',
            func=lambda event: self.data[text]()
        )


class Toast:
    def __init__(self, mode=constants.MESSAGE, title='MoToast'):
        self.load = MoFont.load
        if 'IDEM' not in font.families():
            # sys.stdout.write('Load MoFont-IDEM')
            self.load()
        self.window = Toplevel(
            height=1,
            width=1,
            alpha=0
        )
        self.setWindow(mode)
        self.style = Style()
        self.setStyle()
        self.interface = Frame(
            master=self.window
        )
        self.setInterface()
        self.top = Frame(
            master=self.interface
        )
        self.separator = Separator(
            master=self.top,
        )
        self.setTop()
        self.controller = Frame(
            master=self.top
        )
        self.exiter = Label(
            master=self.controller,
            text=' 0 '
        )
        self.dots = Label(
            master=self.controller,
            text='d'
        )
        self.setController()

        self.menu = MoMenu(
            binder=self.dots,
            # data={
            #     'File': lambda: sys.stdout.write('0'),
            #     'Exit': self.EXIT
            # }
        )

        self.title = StringVar()
        self.titleShower = Label(
            master=self.top,
            textvariable=self.title
        )
        self.initTitle(title)

        self.app = Frame(
            master=self.interface
        )
        self.setApp()

    def EXIT(self):
        self.window.destroy()
        try:
            self.menu.window.destroy()
        finally:
            pass

    def setWindow(self, mode):
        self.window.overrideredirect(True)
        self.window.wm_attributes('-topmost', 1)
        # self.window.wm_attributes('-alpha', 0.5)
        self.window.geometry(
            # f'{int(self.window.winfo_screenwidth() / 8)}x{int(self.window.winfo_screenheight() / 8)}'
            f'-20-60'
        )
        self.window.wm_maxsize(
            width=int(self.window.winfo_screenwidth() / 6),
            height=int(self.window.winfo_screenheight() / 2)
        )
        self.window.wm_minsize(
            width=int(self.window.winfo_screenwidth() / 6),
            height=int(self.window.winfo_screenheight() / 6)
        )
        self.window.config(
            highlightthickness=3,
            highlightcolor=constants.ModeColor[mode][0],
            highlightbackground=constants.ModeColor[mode][1],
        )
        self.window.bind(
            sequence='<Enter>',
            func=lambda event: self.window.focus_set()
        )
        self.window.wm_attributes('-alpha', 1.0)

    def setStyle(self):
        self.style.configure(
            style='white.TFrame',
            background='#FFFFFF'
        )
        self.style.configure(
            style='black.TSeparator',
            background='#000000'
        )
        self.style.configure(
            style='exiter.TLabel',
            foreground='#F00056',
            background='#FFFFFF',
            font=('IDEM', 20)
        )
        self.style.configure(
            style='_exiter.TLabel',
            foreground='#F00056',
            background='#F9F1F6',
            font=('IDEM', 20)
        )
        self.style.configure(
            style='dots.TLabel',
            foreground='#000000',
            background='#FFFFFF',
            font=('IDEM', 20)
        )
        self.style.configure(
            style='_dots.TLabel',
            foreground='#000000',
            background='#F9F1F6',
            font=('IDEM', 20)
        )
        self.style.configure(
            style='title.TLabel',
            foreground='#000000',
            background='#FFFFFF',
            font=('微软雅黑', 12, 'bold')
        )
        self.style.configure(
            style='default.TLabel',
            foreground='#000000',
            background='#FFFFFF',
            font=('微软雅黑', 9)
        )
        self.style.configure(
            style='app.TFrame',
            background='#FFFFFF'
        )

    def setInterface(self):
        self.interface.configure(style='white.TFrame')
        self.interface.pack(
            fill=BOTH,
            expand=True
        )

    def setTop(self):
        self.top.configure(style='white.TFrame')
        self.top.pack(
            fill=X,
            side=TOP
        )
        self.separator.configure(style='black.TSeparator')
        self.separator.pack(
            side=BOTTOM,
            fill=X,
        )

    def setController(self):
        self.controller.configure(style='white.TFrame')
        self.controller.pack(
            side=RIGHT
        )
        self.exiter.configure(style='exiter.TLabel')
        self.exiterBind()
        self.exiter.pack(
            side=RIGHT
        )
        self.dots.configure(style='dots.TLabel')
        self.dotsBind()
        self.dots.pack(
            side=RIGHT
        )

    def exiterBind(self):
        self.exiter.bind(
            sequence='<Button-1>',
            func=lambda event: self.EXIT()
        )
        self.exiter.bind(
            sequence='<Enter>',
            func=lambda event: self.exiter.config(
                text=' 1 ',
                style='_exiter.TLabel'
            )
        )
        self.exiter.bind(
            sequence='<Leave>',
            func=lambda event: self.exiter.config(
                text=' 0 ',
                style='exiter.TLabel'
            )
        )

    def dotsBind(self):
        self.dots.bind(
            sequence='<Enter>',
            func=lambda event: self.dots.configure(style='_dots.TLabel')
        )
        self.dots.bind(
            sequence='<Leave>',
            func=lambda event: self.dots.configure(style='dots.TLabel')
        )

    def initTitle(self, title='MoToast'):
        self.title.set(title)
        self.titleShower.configure(style='title.TLabel')
        self.titleShower.pack(
            side=LEFT,
            padx=5
        )

    def setTitle(self, title):
        self.title.set(title)

    def setApp(self):
        self.app.configure(style='app.TFrame')
        self.app.pack(
            fill=BOTH,
            expand=True,
            padx=5,
            pady=5
        )

    def ToastMaster(self):
        return self.app


class ToastAPI(Toast):
    def __init__(self, mode=constants.MESSAGE, title='ToastApplication', menu=None):
        super().__init__(mode=mode, title=title)
        if menu is None:
            self.menu.setData(
                data={
                    # 'Copyright': lambda: sys.stdout.write(constants.Copyright),
                    'Exit': self.EXIT
                }
            )
        else:
            self.menu.setData(menu)


class ToastApplication(ToastAPI):
    def __init__(
            self,
            mode=constants.MESSAGE,
            title='ToastApplication',
            message=''
    ):
        super().__init__(mode=mode, title=title)
        self.message = StringVar()
        self.message.set(message)

        self.exhibition = Frame(
            master=self.app
        )

        self.AppConfig()

    def AppConfig(self):
        Label(
            master=self.exhibition,
            textvariable=self.message,
            background='#FFFFFF',
            foreground='#000000',
            font=('微软雅黑', 9),
            anchor='nw',
            wraplength=int(self.window.winfo_screenwidth() / 6 - 15)
        ).pack(
            fill=BOTH,
            expand=True
        )

        self.exhibition.pack(
            fill=BOTH,
            expand=True
        )



if __name__ == '__main__':
    root = Tk()
    t = ToastApplication(
        title='Test',
        message='''Beautiful is better than ugly.
Explicit is better than implicit.
Simple is better than complex.
Complex is better than complicated.
Flat is better than nested.
Sparse is better than dense.
Readability counts.
Special cases aren't special enough to break the rules.
Although practicality beats purity.
Errors should never pass silently.
Unless explicitly silenced.
In the face of ambiguity, refuse the temptation to guess.
There should be one-- and preferably only one --obvious way to do it.
Although that way may not be obvious at first unless you're Dutch.
Now is better than never.
Although never is often better than *right* now.
If the implementation is hard to explain, it's a bad idea.
If the implementation is easy to explain, it may be a good idea.
Namespaces are one honking great idea -- let's do more of those!'''
    )
    t = ToastApplication(
        title='Test',
        message='''Beautiful is better than ugly.
Explicit is better than implicit.
Simple is better than complex.
Complex is better than complicated.
Flat is better than nested.
Sparse is better than dense.
Readability counts.
Special cases aren't special enough to break the rules.
Although practicality beats purity.
Errors should never pass silently.
Unless explicitly silenced.
In the face of ambiguity, refuse the temptation to guess.
There should be one-- and preferably only one --obvious way to do it.
Although that way may not be obvious at first unless you're Dutch.
Now is better than never.
Although never is often better than *right* now.
If the implementation is hard to explain, it's a bad idea.
If the implementation is easy to explain, it may be a good idea.
Namespaces are one honking great idea -- let's do more of those!'''
    )
    # Text(t.ToastMaster()).pack()
    root.mainloop()
