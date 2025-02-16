import tkinter as tk
from tkinter import messagebox
import pyautogui
import cv2
import numpy as np
import time
import pygetwindow as gw

# 定义全局变量
start_x, start_y = -1, -1  # 拖拽起始位置
end_x, end_y = -1, -1  # 拖拽结束位置
dragging = False  # 是否正在拖拽
template_image = None  # 截取的模板图像

# 定义图像识别函数
def find_image_on_screen(template, confidence=0.8):
    """
    在屏幕上查找模板图像的位置
    """
    screenshot = pyautogui.screenshot()
    screenshot = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
    result = cv2.matchTemplate(screenshot, template, cv2.TM_CCOEFF_NORMED)
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
    if max_val >= confidence:
        return max_loc, template.shape
    return None, None

# 定义拖拽事件处理函数
def on_drag_start(event):
    global start_x, start_y, dragging
    start_x, start_y = event.x, event.y
    dragging = True

def on_drag_end(event):
    global end_x, end_y, dragging, template_image
    end_x, end_y = event.x, event.y
    dragging = False

    # 截取拖拽区域的图像
    if start_x != -1 and start_y != -1 and end_x != -1 and end_y != -1:
        x1, y1 = min(start_x, end_x), min(start_y, end_y)
        x2, y2 = max(start_x, end_x), max(start_y, end_y)
        template_image = pyautogui.screenshot(region=(x1, y1, x2 - x1, y2 - y1))
        template_image = cv2.cvtColor(np.array(template_image), cv2.COLOR_RGB2BGR)
        messagebox.showinfo("完成", "已截取模板图像！")

# 定义自动化操作函数
def automate_baidu_search(keyword):
    try:
        # 打开百度首页并设置窗口大小和位置
        browser = gw.getWindowsWithTitle("百度一下，你就知道")[0]
        browser.activate()
        browser.resizeTo(1000, 800)
        browser.moveTo(0, 0)
        time.sleep(1)

        # 输入关键词并搜索
        pyautogui.write(keyword)
        pyautogui.press('enter')
        time.sleep(2)  # 等待搜索结果加载

        # 使用截取的模板图像进行识别
        if template_image is None:
            raise Exception("未截取模板图像")

        # 查找模板图像的位置
        result_pos, result_size = find_image_on_screen(template_image)
        if result_pos is None:
            raise Exception("未找到匹配的结果")

        # 点击识别到的位置
        result_center = (
            result_pos[0] + result_size[1] // 2,
            result_pos[1] + result_size[0] // 2,
        )
        pyautogui.click(result_center)

        # 提示用户操作完成
        messagebox.showinfo("完成", f"已搜索并打开关键词 '{keyword}' 的第一个结果！")

    except Exception as e:
        messagebox.showerror("错误", f"发生错误: {e}")

# 创建 GUI
def create_gui():
    root = tk.Tk()
    root.title("百度搜索自动化")
    root.geometry("400x200")

    # 添加输入框
    keyword_label = tk.Label(root, text="请输入关键词：")
    keyword_label.pack(pady=10)
    keyword_entry = tk.Entry(root, width=30)
    keyword_entry.pack()

    # 添加拖拽区域
    drag_label = tk.Label(root, text="拖拽选择页面上的区域", bg="lightgray", width=50, height=5)
    drag_label.pack(pady=10)
    drag_label.bind("<Button-1>", on_drag_start)
    drag_label.bind("<ButtonRelease-1>", on_drag_end)

    # 添加按钮
    def start_automation():
        keyword = keyword_entry.get()
        if keyword:
            automate_baidu_search(keyword)
        else:
            messagebox.showwarning("警告", "请输入关键词！")

    start_button = tk.Button(root, text="开始搜索", command=start_automation)
    start_button.pack(pady=10)

    root.mainloop()

# 运行 GUI
if __name__ == "__main__":
    create_gui()