import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import threading
from queue import Queue
from fractions import Fraction

class GCDCalculator:
    def __init__(self, master):
        self.master = master
        master.title("最大公约数计算器")
        master.geometry("800x600")

        # 算法选择和状态变量
        self.algorithm = tk.StringVar(value="euclidean")
        self.algorithms = {
            "euclidean": "欧几里得算法",
            "prime": "质因数分解法",
            "stein": "Stein算法"
        }
        self.calculating = False
        self.result_queue = Queue()
        
        # 添加进度条
        self.progress_bar = ttk.Progressbar(self.master, orient=tk.HORIZONTAL, length=300, mode='determinate')
        self.progress_bar.pack(pady=10)

        self.create_widgets()
        self.create_menu()
        self.master.after(100, self.check_queue)

    def create_widgets(self):
        # 输入部分
        input_frame = ttk.Frame(self.master)
        input_frame.pack(pady=10, fill=tk.X)

        ttk.Label(input_frame, text="输入数字或分数（用逗号分隔）:").pack(side=tk.LEFT, padx=5)
        self.nums_entry = ttk.Entry(input_frame, width=40)
        self.nums_entry.pack(side=tk.LEFT, padx=5)

        # 算法选择
        ttk.Label(input_frame, text="算法:").pack(side=tk.LEFT, padx=5)
        self.algo_menu = ttk.OptionMenu(input_frame, self.algorithm,
                                       self.algorithms["euclidean"],
                                       *self.algorithms.values())
        self.algo_menu.pack(side=tk.LEFT, padx=5)

        # 计算按钮
        self.calc_btn = ttk.Button(input_frame, text="计算", command=self.calculate)
        self.calc_btn.pack(side=tk.LEFT, padx=10)

        # 结果展示
        result_frame = ttk.Frame(self.master)
        result_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        ttk.Label(result_frame, text="计算结果:").pack(anchor=tk.W)
        self.result_text = scrolledtext.ScrolledText(result_frame, height=3)
        self.result_text.pack(fill=tk.X, pady=5)

        ttk.Label(result_frame, text="计算步骤:").pack(anchor=tk.W)
        self.steps_text = scrolledtext.ScrolledText(result_frame)
        self.steps_text.pack(fill=tk.BOTH, expand=True)

        # 添加状态栏
        self.status = ttk.Label(self.master, text="就绪", relief=tk.SUNKEN)
        self.status.pack(side=tk.BOTTOM, fill=tk.X)

    def create_menu(self):
        # 创建菜单栏
        menubar = tk.Menu(self.master)
        self.master.config(menu=menubar)

        # 创建“关于”菜单
        about_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="关于", menu=about_menu)

        # 添加“关于”选项
        about_menu.add_command(label="关于", command=self.show_about)

    def show_about(self):
        # 显示关于信息
        messagebox.showinfo("关于", "Produced by Terry Gao\nv0.2")

    def calculate(self):
        if self.calculating:
            return

        try:
            input_str = self.nums_entry.get()
            # 解析输入为分数或整数
            numbers = [self.parse_number(num.strip()) for num in input_str.split(",") if num.strip()]
            if len(numbers) < 2:
                raise ValueError("至少需要输入两个数字")
        except ValueError as e:
            messagebox.showerror("输入错误", f"无效输入: {str(e)}")
            return

        algo = [k for k, v in self.algorithms.items() if v == self.algorithm.get()][0]

        # 禁用计算按钮
        self.calc_btn.config(state=tk.DISABLED)
        self.calculating = True
        self.status.config(text="计算中...")

        # 重置进度条
        self.progress_bar['value'] = 0
        self.progress_bar['maximum'] = len(numbers) - 1

        # 在独立线程中运行计算
        threading.Thread(
            target=self.run_calculation,
            args=(numbers, algo),
            daemon=True
        ).start()

    def parse_number(self, num_str):
        """将输入字符串解析为分数或整数"""
        try:
            # 尝试解析为分数
            if '/' in num_str:
                return Fraction(num_str)
            # 尝试解析为整数
            return int(num_str)
        except ValueError:
            # 尝试解析为浮点数并转换为分数
            try:
                return Fraction(float(num_str))
            except ValueError:
                raise ValueError(f"无法解析的数字: {num_str}")

    def run_calculation(self, numbers, algo):
        try:
            if algo == "euclidean":
                steps, result = self.multi_euclidean_gcd(numbers)
            elif algo == "prime":
                steps, result = self.multi_prime_gcd(numbers)
            elif algo == "stein":
                steps, result = self.optimized_stein_gcd(numbers)
            else:
                raise ValueError("未知算法")
        except Exception as e:
            self.result_queue.put(("error", str(e)))
        else:
            self.result_queue.put(("result", (numbers, result, steps)))
        finally:
            self.result_queue.put(("done", None))

    def check_queue(self):
        while not self.result_queue.empty():
            msg_type, content = self.result_queue.get()
            
            if msg_type == "error":
                messagebox.showerror("计算错误", content)
            elif msg_type == "result":
                self.show_result(*content)
            elif msg_type == "done":
                self.calc_btn.config(state=tk.NORMAL)
                self.calculating = False
                self.status.config(text="就绪")
                # 重置进度条
                self.progress_bar['value'] = 0
        
        self.master.after(100, self.check_queue)

    def show_result(self, numbers, result, steps):
        self.result_text.config(state=tk.NORMAL)
        self.result_text.delete(1.0, tk.END)
        self.result_text.insert(tk.END, f"数字集合: {numbers}\n最大公约数: {result}")
        self.result_text.config(state=tk.DISABLED)

        self.steps_text.config(state=tk.NORMAL)
        self.steps_text.delete(1.0, tk.END)
        for step in steps:
            self.steps_text.insert(tk.END, step + "\n\n")
        self.steps_text.config(state=tk.DISABLED)

    def multi_euclidean_gcd(self, numbers):
        # 将分数转换为整数形式
        numbers = [abs(num.numerator) for num in numbers]
        steps = []
        current_gcd = numbers[0]
        
        for i in range(1, len(numbers)):
            a = current_gcd
            b = numbers[i]
            steps.append(f"计算 {a} 和 {b} 的GCD:")
            
            while b != 0:
                q, r = divmod(a, b)
                steps.append(f"  {a} = {b} × {q} + {r}")
                a, b = b, r
                # 更新进度条
                self.progress_bar['value'] = i
            
            current_gcd = a
            steps.append(f"当前阶段结果: {current_gcd}\n{'-'*40}")
        
        return steps, current_gcd

    def multi_prime_gcd(self, numbers):
        def prime_factors(n):
            n = abs(n)
            factors = {}
            while n % 2 == 0:
                factors[2] = factors.get(2, 0) + 1
                n = n // 2
            i = 3
            while i * i <= n:
                while n % i == 0:
                    factors[i] = factors.get(i, 0) + 1
                    n = n // i
                i += 2
            if n > 2:
                factors[n] = 1
            return factors

        # 将分数转换为整数形式
        numbers = [abs(num.numerator) for num in numbers]
        steps = []
        all_factors = []
        
        # 获取所有数字的质因数分解
        for num in numbers:
            factors = prime_factors(num)
            all_factors.append(factors)
            steps.append(f"{num} 的质因数分解: {factors}")
        
        # 找出公共质因数
        common_factors = {}
        for factor in all_factors[0]:
            min_power = min(factors.get(factor, 0) for factors in all_factors)
            if min_power > 0:
                common_factors[factor] = min_power
                steps.append(f"共同质因数 {factor}^{min_power}")
        
        if not common_factors:
            return steps, 1
        
        gcd = 1
        for factor, power in common_factors.items():
            gcd *= factor ** power
        
        return steps, gcd

    def optimized_stein_gcd(self, numbers):
        def stein(a, b):
            # 优化后的Stein算法实现
            steps = []
            a, b = abs(a), abs(b)
            shift = 0

            # 快速处理偶数情况
            if a == 0:
                return b, steps
            if b == 0:
                return a, steps

            # 计算公共的2的幂
            while (a | b) & 1 == 0:
                a >>= 1
                b >>= 1
                shift += 1
                steps.append(f"同时右移得到: a={a}, b={b}")

            # 确保a是奇数
            while (a & 1) == 0:
                a >>= 1
                steps.append(f"a为偶数，右移得到: a={a}")

            while True:
                # 确保b是奇数
                while (b & 1) == 0:
                    b >>= 1
                    steps.append(f"b为偶数，右移得到: b={b}")

                # 确保a >= b
                if a < b:
                    a, b = b, a
                    steps.append(f"交换a和b: a={a}, b={b}")

                # 使用减法代替取模
                a -= b
                steps.append(f"a = a - b → {a}")

                if a == 0:
                    gcd = b << shift
                    steps.append(f"恢复移位结果: {b} << {shift} = {gcd}")
                    return gcd, steps

        # 将分数转换为整数形式
        numbers = [abs(num.numerator) for num in numbers]
        if len(numbers) == 0:
            return [], 0

        current_gcd = numbers[0]
        all_steps = []

        for num in numbers[1:]:
            all_steps.append(f"计算 {current_gcd} 和 {num} 的GCD:")
            gcd, steps = stein(current_gcd, num)
            all_steps.extend(steps)
            current_gcd = gcd
            all_steps.append(f"当前阶段结果: {current_gcd}\n{'-'*40}")

        return all_steps, current_gcd

if __name__ == "__main__":
    root = tk.Tk()
    app = GCDCalculator(root)
    root.mainloop()