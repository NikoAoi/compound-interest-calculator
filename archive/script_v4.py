import customtkinter as ctk
from tkinter import messagebox
import locale

# --- 图表库导入 ---
import matplotlib
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.ticker import FuncFormatter

# 设置Matplotlib使用TkAgg后端
matplotlib.use("TkAgg")

# 尝试设置本地化，用于格式化数字
try:
    locale.setlocale(locale.LC_ALL, 'en_US.UTF-8')
except locale.Error:
    try:
        locale.setlocale(locale.LC_ALL, 'English_United States.1252')
    except locale.Error:
        print("警告：无法设置本地化，数字可能不会被格式化。")


class VisualCompoundInterestCalculator(ctk.CTk):
    def __init__(self):
        super().__init__()

        # --- 窗口基本设置 ---
        self.title("可视化复利计算器 (Visual Compound Interest Calculator)")
        self.geometry("700x950")
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

        # --- 主框架 ---
        main_frame = ctk.CTkScrollableFrame(self, corner_radius=15)
        main_frame.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")
        main_frame.grid_columnconfigure(1, weight=1)

        # ... (UI组件部分保持不变) ...
        title_label = ctk.CTkLabel(main_frame, text="复利的力量 (可视化版)", font=self.title_font)
        title_label.grid(row=0, column=0, columnspan=2, padx=20, pady=(10, 20))
        ctk.CTkLabel(main_frame, text="初始本金 (P)", font=self.label_font).grid(row=1, column=0, padx=20, pady=10, sticky="w")
        self.principal_entry = ctk.CTkEntry(main_frame, placeholder_text="例如: 1000", font=self.label_font)
        self.principal_entry.grid(row=1, column=1, padx=20, pady=10, sticky="ew")
        self.principal_entry.insert(0, "1000")
        ctk.CTkLabel(main_frame, text="复利计算频率", font=self.label_font).grid(row=2, column=0, padx=20, pady=10, sticky="w")
        self.frequency_selector = ctk.CTkSegmentedButton(main_frame, values=["按日", "按月", "按年"], font=self.label_font, command=self.update_rate_helper_text)
        self.frequency_selector.grid(row=2, column=1, padx=20, pady=10, sticky="ew")
        self.frequency_selector.set("按日")
        ctk.CTkLabel(main_frame, text="收益率 (%)", font=self.label_font).grid(row=3, column=0, padx=20, pady=(10,0), sticky="w")
        self.rate_entry = ctk.CTkEntry(main_frame, placeholder_text="例如: 10", font=self.label_font)
        self.rate_entry.grid(row=3, column=1, padx=20, pady=(10,0), sticky="ew")
        self.rate_entry.insert(0, "10")
        self.rate_helper_label = ctk.CTkLabel(main_frame, text="", font=self.helper_font, text_color="gray")
        self.rate_helper_label.grid(row=4, column=1, padx=20, pady=(0, 10), sticky="w")
        ctk.CTkLabel(main_frame, text="复利总时间", font=self.label_font).grid(row=5, column=0, padx=20, pady=10, sticky="w")
        duration_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        duration_frame.grid(row=5, column=1, padx=20, pady=10, sticky="ew")
        duration_frame.grid_columnconfigure(0, weight=2)
        duration_frame.grid_columnconfigure(1, weight=1)
        self.duration_value_entry = ctk.CTkEntry(duration_frame, font=self.label_font)
        self.duration_value_entry.grid(row=0, column=0, sticky="ew", padx=(0, 5))
        self.duration_value_entry.insert(0, "1")
        self.duration_unit_selector = ctk.CTkOptionMenu(duration_frame, values=["年", "月", "周", "日"], font=self.label_font)
        self.duration_unit_selector.grid(row=0, column=1, sticky="ew", padx=(5, 0))
        self.duration_unit_selector.set("年")
        self.calculate_button = ctk.CTkButton(main_frame, text="计算并生成图表", font=self.button_font, command=self.calculate, height=40)
        self.calculate_button.grid(row=6, column=0, columnspan=2, padx=20, pady=(30, 20), sticky="ew")
        result_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        result_frame.grid(row=7, column=0, columnspan=2, padx=20, pady=10, sticky="ew")
        result_frame.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(result_frame, text="本息总额 (Total Amount)", font=self.result_font, text_color=("blue", "cyan")).grid(row=0, column=0, pady=(10,5))
        self.total_amount_label = ctk.CTkLabel(result_frame, text="¥ 0.00", font=self.result_value_font, wraplength=600)
        self.total_amount_label.grid(row=1, column=0, padx=10, pady=(0,10))
        ctk.CTkLabel(result_frame, text="总收益 (Total Interest)", font=self.result_font, text_color=("green", "#33FF99")).grid(row=2, column=0, pady=(10,5))
        self.total_interest_label = ctk.CTkLabel(result_frame, text="¥ 0.00", font=self.result_value_font, wraplength=600)
        self.total_interest_label.grid(row=3, column=0, padx=10, pady=(0,20))
        chart_frame = ctk.CTkFrame(main_frame)
        chart_frame.grid(row=8, column=0, columnspan=2, padx=20, pady=20, sticky="nsew")
        chart_frame.grid_columnconfigure(0, weight=1)
        chart_control_frame = ctk.CTkFrame(chart_frame, fg_color="transparent")
        chart_control_frame.grid(row=0, column=0, columnspan=2, padx=10, pady=5, sticky="ew")
        ctk.CTkLabel(chart_control_frame, text="图表周期:", font=self.label_font).pack(side="left", padx=(0,10))
        self.chart_period_selector = ctk.CTkSegmentedButton(chart_control_frame, values=["日", "周", "月", "年"], font=self.label_font, command=self.update_plot)
        self.chart_period_selector.pack(side="left")
        self.chart_period_selector.set("月")
        self.fig = Figure(figsize=(6, 4), dpi=100)
        self.ax = self.fig.add_subplot(111)
        self.canvas = FigureCanvasTkAgg(self.fig, master=chart_frame)
        self.canvas.get_tk_widget().grid(row=1, column=0, sticky="nsew")
        self.plot_data = []

        # --- 初始化 ---
        self.update_rate_helper_text(self.frequency_selector.get())
        self.setup_initial_plot()

    # <--- FIX 1: 新增一个辅助函数来获取与主题匹配的、Matplotlib兼容的颜色
    def _get_plot_colors(self):
        """返回一个包含与当前主题匹配的图表颜色的字典。"""
        if ctk.get_appearance_mode() == "Dark":
            return {
                "bg_color": "#2b2b2b",
                "text_color": "#dce4ee",
                "spine_color": "#565b5e",
                "grid_color": "#343638",
                "line_color": "#1f77b4"
            }
        else:
            return {
                "bg_color": "#f0f0f0",
                "text_color": "#1c1c1c",
                "spine_color": "#565b5e",
                "grid_color": "#d6d6d6",
                "line_color": "#1f77b4"
            }

    # <--- FIX 2: 修改初始绘图函数以使用新的颜色方案
    def setup_initial_plot(self):
        """设置图表的初始外观，使其与主题匹配。"""
        colors = self._get_plot_colors()
        
        self.fig.patch.set_facecolor(colors["bg_color"])
        self.ax.set_facecolor(colors["bg_color"])
        
        self.ax.spines['top'].set_visible(False)
        self.ax.spines['right'].set_visible(False)
        
        # 使用新颜色设置坐标轴和标签
        self.ax.tick_params(colors=colors["text_color"])
        self.ax.spines['bottom'].set_color(colors["spine_color"])
        self.ax.spines['left'].set_color(colors["spine_color"])
        
        self.ax.set_title("收益增长曲线", color=colors["text_color"])
        self.ax.set_xlabel("时间", color=colors["text_color"])
        self.ax.set_ylabel("本息总额", color=colors["text_color"])
        
        # 清空之前的文本
        self.ax.clear()
        self.ax.text(0.5, 0.5, '点击"计算"按钮生成图表', horizontalalignment='center', verticalalignment='center', transform=self.ax.transAxes, color=colors["text_color"], fontsize=14)
        
        self.fig.tight_layout()
        self.canvas.draw()
        
    def update_rate_helper_text(self, selection):
        text_map = {"按日": "（这是每日收益率）", "按月": "（这是每月收益率）", "按年": "（这是每年收益率）"}
        self.rate_helper_label.configure(text=text_map.get(selection, ""))

    def calculate(self):
        """计算核心数据并生成每日数据点用于绘图"""
        self.calculate_button.configure(state="disabled", text="计算中...")
        self.update_idletasks() # 使用 update_idletasks 更安全
        try:
            principal = float(self.principal_entry.get())
            rate_percent = float(self.rate_entry.get())
            frequency = self.frequency_selector.get()
            duration_value = float(self.duration_value_entry.get())
            duration_unit = self.duration_unit_selector.get()
            
            unit_to_days = {"年": 365, "月": 30, "周": 7, "日": 1}
            total_days = duration_value * unit_to_days.get(duration_unit, 0)

            if principal < 0 or rate_percent < 0 or total_days <= 0:
                messagebox.showerror("输入错误", "本金、利率必须为正数，且时长必须大于0。")
                return

            rate_per_period = rate_percent / 100.0
            
            freq_to_days = {"按年": 365.0, "按月": 30.0, "按日": 1.0}
            days_per_period = freq_to_days.get(frequency)

            self.plot_data = []
            for day in range(int(total_days) + 1):
                current_periods = day / days_per_period
                amount = principal * ((1 + rate_per_period) ** current_periods)
                self.plot_data.append((day, amount))
            
            final_amount = self.plot_data[-1][1]
            total_interest = final_amount - principal
            
            try:
                formatted_amount = f"¥ {final_amount:,.2f}"
                formatted_interest = f"¥ {total_interest:,.2f}"
            except (OverflowError, ValueError):
                formatted_amount = f"¥ {final_amount:.2e}"
                formatted_interest = f"¥ {total_interest:.2e}"

            self.total_amount_label.configure(text=formatted_amount)
            self.total_interest_label.configure(text=formatted_interest)

            self.update_plot()

        except ValueError:
            messagebox.showerror("输入错误", "请输入有效的数字！")
        except Exception as e:
            messagebox.showerror("计算错误", f"发生未知错误: {e}")
        finally:
            self.calculate_button.configure(state="normal", text="计算并生成图表")

    # <--- FIX 3: 修改更新绘图函数以使用新的颜色方案
    def update_plot(self, *args):
        """根据选择的周期粒度，使用已生成的数据更新图表"""
        if not self.plot_data:
            # 如果没有数据，确保图表是干净的初始状态
            self.setup_initial_plot()
            return

        period = self.chart_period_selector.get()
        period_map = {"日": 1, "周": 7, "月": 30, "年": 365}
        step = period_map.get(period, 30)

        x_data, y_data = [], []
        x_data.append(0)
        y_data.append(self.plot_data[0][1])

        # 优化采样逻辑，确保小周期图表不会过于拥挤
        num_points = len(self.plot_data) // step
        if num_points > 1000: # 如果采样后点数仍然过多，增加步长
            step = len(self.plot_data) // 1000

        for i in range(step, len(self.plot_data), step):
            day, amount = self.plot_data[i]
            x_data.append(day / period_map[period])
            y_data.append(amount)
        
        last_day, last_amount = self.plot_data[-1]
        if last_day % step != 0:
             x_data.append(last_day / period_map[period])
             y_data.append(last_amount)

        # --- 开始绘图 ---
        self.ax.clear()
        colors = self._get_plot_colors()
        
        self.fig.patch.set_facecolor(colors["bg_color"])
        self.ax.set_facecolor(colors["bg_color"])

        self.ax.plot(x_data, y_data, marker='.', linestyle='-', color=colors["line_color"], markersize=3)
        
        self.ax.set_title("收益增长曲线", color=colors["text_color"])
        self.ax.set_xlabel(f"时间 ({period})", color=colors["text_color"])
        self.ax.set_ylabel("本息总额 (元)", color=colors["text_color"])
        
        self.ax.yaxis.set_major_formatter(FuncFormatter(lambda y, pos: f'{y:,.2f}' if y < 1e6 else f'{y:.2e}'))
        
        self.ax.grid(True, linestyle='--', alpha=0.3, color=colors["grid_color"])
        self.ax.tick_params(axis='x', colors=colors["text_color"])
        self.ax.tick_params(axis='y', colors=colors["text_color"])
        for spine in self.ax.spines.values():
            spine.set_edgecolor(colors["spine_color"])
        
        self.fig.tight_layout()
        self.canvas.draw()


if __name__ == "__main__":
    app = VisualCompoundInterestCalculator()
    app.mainloop()