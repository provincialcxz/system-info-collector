import psutil
import platform
import cpuinfo
import GPUtil
import subprocess


def get_laptop_model():
    try:
        result = subprocess.check_output(
            "wmic csproduct get name", shell=True, encoding="utf-8"
        ).strip()
        model = result.split("\n")[-1]  # Получаем последнюю строку (модель)
        return model
    except Exception as e:
        return "Неизвестно"
        

def get_system_info():

    # Информация о модели ноутбука
    print(f"\nМодель ноутбука: {get_laptop_model()}")
    
    # Информация о процессоре
    print("Процессор:")
    cpu_info = cpuinfo.get_cpu_info()  # Получаем информацию о процессоре
    print(f"  Имя процессора: {cpu_info.get('brand_raw', 'Неизвестно')}")
    print(f"  Количество ядер: {psutil.cpu_count(logical=False)}")
    print(f"  Количество потоков: {psutil.cpu_count(logical=True)}")
    print(f"  Частота процессора: {psutil.cpu_freq().current} MHz")

    # Информация о видеокарте
    print("\nВидеокарта:")
    try:
        gpus = GPUtil.getGPUs()
        for gpu in gpus:
            print(f"  Имя видеокарты: {gpu.name}")
            print(f"  Память видеокарты: {gpu.memoryTotal} MB")
            print(f"  Используемая память: {gpu.memoryUsed} MB")
            print(f"  Загрузка видеокарты: {gpu.load * 100}%")
    except Exception as e:
        print("  Информация о видеокарте недоступна.")

    # Информация о оперативной памяти
    print("\nОперативная память:")
    mem = psutil.virtual_memory()
    print(f"  Всего памяти: {mem.total / (1024 ** 3):.2f} GB")
    print(f"  Доступно памяти: {mem.available / (1024 ** 3):.2f} GB")
    print(f"  Используется памяти: {mem.used / (1024 ** 3):.2f} GB")
    print(f"  Процент использования памяти: {mem.percent}%")

    # Информация о диске
    print("\nДиск:")
    disk = psutil.disk_usage('/')
    print(f"  Всего места на диске: {disk.total / (1024 ** 3):.2f} GB")
    print(f"  Используется места на диске: {disk.used / (1024 ** 3):.2f} GB")
    print(f"  Процент использования диска: {disk.percent}%")

    # Информация о системе
    print("\nСистема:")
    print(f"  Операционная система: {platform.system()} {platform.release()}")
    print(f"  Версия системы: {platform.version()}")
    print(f"  Архитектура: {platform.machine()}")



if __name__ == "__main__":
    get_system_info()
