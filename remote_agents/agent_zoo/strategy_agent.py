import asyncio
import time

async def do_work(name, delay):
    print(f"Task {name}: Bắt đầu chờ {delay} giây...")
    await asyncio.sleep(delay)
    print(f"Task {name}: Đã chờ xong.")

async def main_concurrent():
    print(f"Bắt đầu đồng thời tại {time.strftime('%X')}")
    
    # Tạo ra các Task. Event Loop sẽ bắt đầu chạy chúng ngay khi có thể.
    task1 = asyncio.create_task(do_work("A", 2))
    task2 = asyncio.create_task(do_work("B", 1))

    # await task1 và task2 sẽ tạm dừng main_concurrent,
    # nhưng task1 và task2 đang chạy song song trên Event Loop.
    # Dùng asyncio.gather để chờ tất cả hoàn thành.
    await asyncio.gather(task1, task2)

    print(f"Kết thúc đồng thời tại {time.strftime('%X')}")


start_time = time.time()
asyncio.run(main_concurrent())
end_time = time.time()
print(f"Tổng thời gian thực thi: {end_time - start_time:.2f} giây")