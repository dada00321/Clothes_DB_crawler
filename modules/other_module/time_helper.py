import time

def countdown(n):
    print(f"開始等待 {n} 秒...")
    for i in range(n):
        print(f"倒數 {n-i} 秒")
        time.sleep(1)
    print("等待結束！")

if __name__ == "__main__":
    countdown(3)