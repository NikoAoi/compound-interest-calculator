import customtkinter as ctk
from tkinter import messagebox
import locale

# 尝试设置本地化，用于格式化数字（添加千位分隔符）
try:
    locale.setlocale(locale.LC_ALL, 'en_US.UTF-8')
except locale.Error:
    try:
        locale.setlocale(locale.LC_ALL, 'English_United States.1252')
    except locale.Error:
        print("警告：无法设置本地化，数字可能不会被格式化。")

class FlexibleCompoundInterestCalculator(ctk.CTk):
    def __init__(self):
        super().__init__()

        # --- 窗口基本设置 ---
        self.title("灵活复利计算器 (Flexible Compound Interest Calculator)")
        self.geometry("600x750")
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
        self._set_appearance_mode("System")

        # --- 字体设置 ---
        self.title_font = ctk.CTkFont(family="Helvetica", size=26, weight="bold")
        self.label_font = ctk.CTkFont(family="Helvetica", size=14)
        self.helper_font = ctk.CTkFont(family="Helvetica", size=12, slant="italic")
        self.button_font = ctk.CTkFont(family="Helvetica", size=14, weight="bold")
        self.result_font = ctk.CTkFont(family="Helvetica", size=18, weight="bold")
        self.result_value_font = ctk.CTkFont(family="Courier New", size=20, weight="bold")

        # --- 创建主框架 ---
        main_frame = ctk.CTkFrame(self, corner_radius=15)
        main_frame.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")
        main_frame.grid_columnconfigure(1, weight=1)
        
        # --- 标题 ---
        title_label = ctk.CTkLabel(main_frame, text="复利的力量 (灵活版)", font=self.title_font)
        title_label.grid(row=0, column=0, columnspan=2, padx=20, pady=(20, 20))

        # --- 输入区域 ---
        # 1. 本金 (Principal)
        ctk.CTkLabel(main_frame, text="初始本金 (P)", font=self.label_font).grid(row=1, column=0, padx=20, pady=10, sticky="w")
        self.principal_entry = ctk.CTkEntry(main_frame, placeholder_text="例如: 1000", font=self.label_font)
        self.principal_entry.grid(row=1, column=1, padx=20, pady=10, sticky="ew")
        self.principal_entry.insert(0, "1000")

        # 2. 复利频率 (Compounding Frequency)
        ctk.CTkLabel(main_frame, text="复利计算频率", font=self.label_font).grid(row=2, column=0, padx=20, pady=10, sticky="w")
        self.frequency_selector = ctk.CTkSegmentedButton(main_frame, values=["按日", "按月", "按年"], font=self.label_font, command=self.update_rate_helper_text)
        self.frequency_selector.grid(row=2, column=1, padx=20, pady=10, sticky="ew")
        self.frequency_selector.set("按日")

        # 3. 收益率 (Rate)
        ctk.CTkLabel(main_frame, text="收益率 (%)", font=self.label_font).grid(row=3, column=0, padx=20, pady=(10,0), sticky="w")
        self.rate_entry = ctk.CTkEntry(main_frame, placeholder_text="例如: 10", font=self.label_font)
        self.rate_entry.grid(row=3, column=1, padx=20, pady=(10,0), sticky="ew")
        self.rate_entry.insert(0, "10")

        # 4. 动态提示标签 (Rate Helper)
        self.rate_helper_label = ctk.CTkLabel(main_frame, text="", font=self.helper_font, text_color="gray")
        self.rate_helper_label.grid(row=4, column=1, padx=20, pady=(0, 10), sticky="w")
        
        # 5. 复利总时间 (Total Duration) - 全新改造的部分
        ctk.CTkLabel(main_frame, text="复利总时间", font=self.label_font).grid(row=5, column=0, padx=20, pady=10, sticky="w")
        
        # 创建一个框架来容纳数值输入框和单位下拉菜单
        duration_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        duration_frame.grid(row=5, column=1, padx=20, pady=10, sticky="ew")
        duration_frame.grid_columnconfigure(0, weight=2) # 数值框占2/3
        duration_frame.grid_columnconfigure(1, weight=1) # 单位选择占1/3

        self.duration_value_entry = ctk.CTkEntry(duration_frame, font=self.label_font)
        self.duration_value_entry.grid(row=0, column=0, sticky="ew", padx=(0, 5))
        self.duration_value_entry.insert(0, "1")

        self.duration_unit_selector = ctk.CTkOptionMenu(duration_frame, values=["年", "月", "周", "日"], font=self.label_font)
        self.duration_unit_selector.grid(row=0, column=1, sticky="ew", padx=(5, 0))
        self.duration_unit_selector.set("年")

        # --- 计算按钮 ---
        calculate_button = ctk.CTkButton(main_frame, text="开始计算", font=self.button_font, command=self.calculate, height=40)
        calculate_button.grid(row=6, column=0, columnspan=2, padx=20, pady=(30, 20), sticky="ew")

        # --- 结果显示区域 ---
        result_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        result_frame.grid(row=7, column=0, columnspan=2, padx=20, pady=10, sticky="ew")
        result_frame.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(result_frame, text="本息总额 (Total Amount)", font=self.result_font, text_color=("blue", "cyan")).grid(row=0, column=0, pady=(10,5))
        self.total_amount_label = ctk.CTkLabel(result_frame, text="¥ 0.00", font=self.result_value_font, wraplength=500)
        self.total_amount_label.grid(row=1, column=0, padx=10, pady=(0,10))

        ctk.CTkLabel(result_frame, text="总收益 (Total Interest)", font=self.result_font, text_color=("green", "#33FF99")).grid(row=2, column=0, pady=(10,5))
        self.total_interest_label = ctk.CTkLabel(result_frame, text="¥ 0.00", font=self.result_value_font, wraplength=500)
        self.total_interest_label.grid(row=3, column=0, padx=10, pady=(0,20))

        # --- 初始化动态标签 ---
        self.update_rate_helper_text(self.frequency_selector.get())

    def update_rate_helper_text(self, selection):
        """根据复利频率选择，更新收益率输入框下方的提示文字"""
        if selection == "按日":
            text = "（这是您设置的每日收益率）"
        elif selection == "按月":
            text = "（这是您设置的每月收益率）"
        else: # "按年"
            text = "（这是您设置的每年收益率）"
        self.rate_helper_label.configure(text=text)

    def calculate(self):
        """执行复利计算并更新界面"""
        try:
            # --- 1. 获取输入值 ---
            principal = float(self.principal_entry.get())
            rate_percent = float(self.rate_entry.get())
            frequency = self.frequency_selector.get()
            duration_value = float(self.duration_value_entry.get())
            duration_unit = self.duration_unit_selector.get()
            
            # --- 2. 核心改动：将输入的时长统一转换为总天数 ---
            if duration_unit == "年":
                total_days = duration_value * 365
            elif duration_unit == "月":
                total_days = duration_value * 30  # 使用30天作为一个月的近似值
            elif duration_unit == "周":
                total_days = duration_value * 7
            else: # "日"
                total_days = duration_value

            if principal < 0 or rate_percent < 0 or total_days < 0:
                messagebox.showerror("输入错误", "本金、利率和时长不能为负数。")
                return

            # --- 3. 计算逻辑 (与上一版相同) ---
            rate_per_period = rate_percent / 100.0
            
            if frequency == "按年":
                total_periods = total_days / 365.0
            elif frequency == "按月":
                total_periods = total_days / 30.0
            else: # "按日"
                total_periods = float(total_days)

            # --- 4. 应用复利公式 ---
            total_amount = principal * ((1 + rate_per_period) ** total_periods)
            total_interest = total_amount - principal
            
            # --- 5. 格式化并显示结果 ---
            try:
                formatted_amount = f"¥ {total_amount:,.2f}"
                formatted_interest = f"¥ {total_interest:,.2f}"
            except (OverflowError, ValueError):
                formatted_amount = f"¥ {total_amount:.2e}"
                formatted_interest = f"¥ {total_interest:.2e}"

            self.total_amount_label.configure(text=formatted_amount)
            self.total_interest_label.configure(text=formatted_interest)

        except ValueError:
            messagebox.showerror("输入错误", "请输入有效的数字！")
        except Exception as e:
            messagebox.showerror("计算错误", f"发生未知错误: {e}")

if __name__ == "__main__":
    app = FlexibleCompoundInterestCalculator()
    app.mainloop()