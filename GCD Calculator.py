import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import math
from functools import reduce

class GCDCalculator:
    def __init__(self, master):
        self.master = master
        master.title("最大公约数计算器")
        master.geometry("800x600")

        # 算法选择
        self.algorithm = tk.StringVar(value="euclidean")
        self.algorithms = {
            "euclidean": "欧几里得算法",
            "prime": "质因数分解法",
            "stein": "Stein算法"
        }

        self.create_widgets()

    def create_widgets(self):
        # 输入部分
        input_frame = ttk.Frame(self.master)
        input_frame.pack(pady=10, fill=tk.X)

        ttk.Label(input_frame, text="输入数字（用逗号分隔）:").pack(side=tk.LEFT, padx=5)
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

    def calculate(self):
        try:
            input_str = self.nums_entry.get()
            numbers = [int(num.strip()) for num in input_str.split(",") if num.strip()]
            if len(numbers) < 2:
                raise ValueError("至少需要输入两个数字")
        except ValueError as e:
            messagebox.showerror("输入错误", f"无效输入: {str(e)}")
            return

        algo = [k for k, v in self.algorithms.items() if v == self.algorithm.get()][0]

        try:
            if algo == "euclidean":
                steps, result = self.multi_euclidean_gcd(numbers)
            elif algo == "prime":
                steps, result = self.multi_prime_gcd(numbers)
            elif algo == "stein":
                steps, result = self.multi_stein_gcd(numbers)
            else:
                raise ValueError("未知算法")
        except Exception as e:
            messagebox.showerror("计算错误", str(e))
            return

        self.show_result(numbers, result, steps)

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
        numbers = [abs(num) for num in numbers]
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

    def multi_stein_gcd(self, numbers):
        def stein_pair(a, b):
            steps = []
            a, b = abs(a), abs(b)
            shift = 0

            while ((a | b) & 1) == 0:
                a >>= 1
                b >>= 1
                shift += 1
                steps.append(f"同时右移得到: a={a}, b={b}")

            while a != 0:
                while (a & 1) == 0:
                    a >>= 1
                    steps.append(f"a为偶数，右移得到: a={a}")
                while (b & 1) == 0:
                    b >>= 1
                    steps.append(f"b为偶数，右移得到: b={b}")

                if a > b:
                    a, b = b, a
                    steps.append(f"交换a和b: a={a}, b={b}")

                b -= a
                steps.append(f"b = b - a → {b}")

            gcd = a << shift
            steps.append(f"恢复移位结果: {a} << {shift} = {gcd}")
            return gcd, steps

        numbers = [abs(num) for num in numbers]
        all_steps = []
        current_gcd = numbers[0]
        
        for i in range(1, len(numbers)):
            all_steps.append(f"计算 {current_gcd} 和 {numbers[i]} 的GCD:")
            gcd, steps = stein_pair(current_gcd, numbers[i])
            all_steps.extend(steps)
            current_gcd = gcd
            all_steps.append(f"当前阶段结果: {current_gcd}\n{'-'*40}")
        
        return all_steps, current_gcd

if __name__ == "__main__":
    root = tk.Tk()
    app = GCDCalculator(root)
    root.mainloop()