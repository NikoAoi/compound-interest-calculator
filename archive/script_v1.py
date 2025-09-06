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

class AdvancedCompoundInterestCalculator(ctk.CTk):
    def __init__(self):
        super().__init__()

        # --- 窗口基本设置 ---
        self.title("高级复利计算器 (Advanced Compound Interest Calculator)")
        self.geometry("600x750")
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
        self._set_appearance_mode("System")

        # --- 字体设置 ---
        self.title_font = ctk.CTkFont(family="Helvetica", size=26, weight="bold")
        self.label_font = ctk.CTkFont(family="Helvetica", size=14)
        self.button_font = ctk.CTkFont(family="Helvetica", size=14, weight="bold")
        self.result_font = ctk.CTkFont(family="Helvetica", size=18, weight="bold")
        self.result_value_font = ctk.CTkFont(family="Courier New", size=20, weight="bold")

        # --- 创建主框架 ---
        main_frame = ctk.CTkFrame(self, corner_radius=15)
        main_frame.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")
        main_frame.grid_columnconfigure(1, weight=1)
        
        # --- 标题 ---
        title_label = ctk.CTkLabel(main_frame, text="复利的力量 (增强版)", font=self.title_font)
        title_label.grid(row=0, column=0, columnspan=2, padx=20, pady=(20, 20))

        # --- 输入区域 ---
        # 1. 本金 (Principal)
        ctk.CTkLabel(main_frame, text="初始本金 (P)", font=self.label_font).grid(row=1, column=0, padx=20, pady=10, sticky="w")
        self.principal_entry = ctk.CTkEntry(main_frame, placeholder_text="例如: 1000", font=self.label_font)
        self.principal_entry.grid(row=1, column=1, padx=20, pady=10, sticky="ew")
        self.principal_entry.insert(0, "1000")

        # 2. 年收益率 (Annual Rate)
        ctk.CTkLabel(main_frame, text="年收益率 (%)", font=self.label_font).grid(row=2, column=0, padx=20, pady=10, sticky="w")
        self.rate_entry = ctk.CTkEntry(main_frame, placeholder_text="例如: 10", font=self.label_font)
        self.rate_entry.grid(row=2, column=1, padx=20, pady=10, sticky="ew")
        self.rate_entry.insert(0, "3650") # 为了演示原问题，10%每天约等于3650%每年

        # 3. 复利频率 (Compounding Frequency)
        ctk.CTkLabel(main_frame, text="复利计算频率", font=self.label_font).grid(row=3, column=0, padx=20, pady=10, sticky="w")
        self.frequency_selector = ctk.CTkSegmentedButton(main_frame, values=["按日", "按月", "按年"], font=self.label_font)
        self.frequency_selector.grid(row=3, column=1, padx=20, pady=10, sticky="ew")
        self.frequency_selector.set("按日")

        # 4. 复利总时间 (Total Duration)
        ctk.CTkLabel(main_frame, text="复利总时间", font=self.label_font).grid(row=4, column=0, padx=20, pady=10, sticky="w")
        self.duration_selector = ctk.CTkSegmentedButton(main_frame, values=["一年", "一月", "一周", "指定天数"], font=self.label_font, command=self.toggle_custom_days_entry)
        self.duration_selector.grid(row=4, column=1, padx=20, pady=10, sticky="ew")
        self.duration_selector.set("一年")

        # 5. 指定天数输入框 ( initially hidden)
        self.custom_days_label = ctk.CTkLabel(main_frame, text="指定天数", font=self.label_font)
        self.custom_days_entry = ctk.CTkEntry(main_frame, placeholder_text="输入总天数", font=self.label_font)
        
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

        # 初始化自定义天数输入框的状态
        self.toggle_custom_days_entry(self.duration_selector.get())

    def toggle_custom_days_entry(self, selection):
        """根据时长选择，显示或隐藏自定义天数输入框"""
        if selection == "指定天数":
            self.custom_days_label.grid(row=5, column=0, padx=20, pady=10, sticky="w")
            self.custom_days_entry.grid(row=5, column=1, padx=20, pady=10, sticky="ew")
        else:
            self.custom_days_label.grid_remove()
            self.custom_days_entry.grid_remove()

    def calculate(self):
        """执行复利计算并更新界面"""
        try:
            # --- 1. 获取所有输入值 ---
            principal = float(self.principal_entry.get())
            annual_rate_percent = float(self.rate_entry.get())
            
            # --- 2. 计算每年的复利期数 (compounding periods per year) ---
            frequency = self.frequency_selector.get()
            if frequency == "按年":
                periods_per_year = 1
            elif frequency == "按月":
                periods_per_year = 12
            else: # "按日"
                periods_per_year = 365
            
            # --- 3. 计算总投资天数 (total days) ---
            duration = self.duration_selector.get()
            if duration == "一年":
                total_days = 365
            elif duration == "一月":
                total_days = 30  # 使用30天作为近似值
            elif duration == "一周":
                total_days = 7
            else: # "指定天数"
                total_days = int(self.custom_days_entry.get())

            # --- 4. 核心计算：推导出复利公式的 r 和 n ---
            # r: 每期的利率 (rate per period)
            rate_per_period = (annual_rate_percent / 100.0) / periods_per_year
            
            # n: 总的复利期数 (total number of periods)
            # 例如：投资730天（2年），按月复利。总期数 = 730 * (12/365) = 24
            total_periods = total_days * (periods_per_year / 365.0)

            if principal < 0 or annual_rate_percent < 0 or total_days < 0:
                messagebox.showerror("输入错误", "本金、利率和天数不能为负数。")
                return

            # --- 5. 应用复利公式 ---
            # A = P * (1 + r)^n
            total_amount = principal * ((1 + rate_per_period) ** total_periods)
            total_interest = total_amount - principal
            
            # --- 6. 格式化并显示结果 ---
            try:
                formatted_amount = f"¥ {total_amount:,.2f}"
                formatted_interest = f"¥ {total_interest:,.2f}"
            except (OverflowError, ValueError):
                # 如果数字太大无法格式化，则使用科学记数法
                formatted_amount = f"¥ {total_amount:.2e}"
                formatted_interest = f"¥ {total_interest:.2e}"

            self.total_amount_label.configure(text=formatted_amount)
            self.total_interest_label.configure(text=formatted_interest)

        except ValueError:
            messagebox.showerror("输入错误", "请输入有效的数字！")
        except Exception as e:
            messagebox.showerror("计算错误", f"发生未知错误: {e}")

if __name__ == "__main__":
    app = AdvancedCompoundInterestCalculator()
    app.mainloop()