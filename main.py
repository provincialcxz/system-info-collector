import psutil
import platform
import cpuinfo
import GPUtil
import subprocess
from datetime import datetime


def format_size(bytes_size: float) -> str:
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if bytes_size < 1024:
            return f"{bytes_size:.2f} {unit}"
        bytes_size /= 1024
    return f"{bytes_size:.2f} PB"


def get_system_model() -> str:
    try:
        if platform.system() == "Windows":
            result = subprocess.check_output(
                "wmic csproduct get name",
                shell=True,
                encoding="utf-8",
                stderr=subprocess.DEVNULL
            ).strip()
            model = result.split("\n")[-1]
            return model if model else "Неизвестно"
        elif platform.system() == "Linux":
            try:
                with open('/sys/class/dmi/id/product_name', 'r') as f:
                    return f.read().strip()
            except:
                return subprocess.getoutput("cat /proc/cpuinfo | grep 'model name' | head -1").split(":")[-1].strip()
        return "Неизвестно (неподдерживаемая ОС)"
    except Exception:
        return "Неизвестно (ошибка получения данных)"


def get_disk_info():
    print(f"\n{' НАКОПИТЕЛИ ИНФОРМАЦИИ ':=^60}")
    
    try:
        partitions = psutil.disk_partitions(all=False)
        readable_disks = []
        unreadable_disks = []

        for part in partitions:
            try:
                usage = psutil.disk_usage(part.mountpoint)
                readable_disks.append((part.device, usage))
            except:
                unreadable_disks.append(part.device)

        for i, (device, usage) in enumerate(readable_disks, 1):
            print(f"\nДиск #{i}: {device}")
            print(f"  Общий размер: {format_size(usage.total)}")
            print(f"  Использовано: {format_size(usage.used)}")
            print(f"  Свободно: {format_size(usage.free)}")
            print(f"  Заполнено: {usage.percent}%")

        if unreadable_disks:
            print(f"\nОбнаружены дополнительные диски: {', '.join(unreadable_disks)}")
    
    except Exception:
        print("  Не удалось получить информацию о дисках")


def get_system_info():
    print("\n" + "="*60)
    print(f"{' СИСТЕМНАЯ ИНФОРМАЦИЯ ':=^60}")
    print("="*60)
    
    print(f"\n{' ОСНОВНЫЕ ДАННЫЕ ':-^60}")
    print(f"Модель системы: {get_system_model()}")
    print(f"Имя компьютера: {platform.node()}")
    print(f"ОС: {platform.system()} {platform.release()}")
    print(f"Версия ОС: {platform.version()}")
    print(f"Архитектура: {platform.machine()}")
    
    print(f"\n{' ПРОЦЕССОР ':-^60}")
    try:
        cpu_info = cpuinfo.get_cpu_info()
        print(f"Производитель: {cpu_info.get('vendor_id_raw', 'Неизвестно')}")
        print(f"Модель: {cpu_info.get('brand_raw', 'Неизвестно')}")
        print(f"Ядер/потоков: {psutil.cpu_count(logical=False)}/{psutil.cpu_count(logical=True)}")
        
        if (freq := psutil.cpu_freq()):
            print(f"Частота: {freq.current:.2f} MHz (макс: {freq.max:.2f} MHz)")
        else:
            print("Частота: Неизвестна")
            
        print(f"Загрузка: {psutil.cpu_percent()}%")
    except Exception as e:
        print(f"  Ошибка получения данных о процессоре: {str(e)}")

    print(f"\n{' ОПЕРАТИВНАЯ ПАМЯТЬ ':-^60}")
    try:
        mem = psutil.virtual_memory()
        print(f"Всего: {format_size(mem.total)}")
        print(f"Доступно: {format_size(mem.available)}")
        print(f"Используется: {format_size(mem.used)}")
        print(f"Загрузка: {mem.percent}%")
    except Exception as e:
        print(f"  Ошибка получения данных о памяти: {str(e)}")

    print(f"\n{' ВИДЕОКАРТА ':-^60}")
    try:
        gpus = GPUtil.getGPUs()
        if not gpus:
            print("  Видеокарты не обнаружены")
        else:
            for i, gpu in enumerate(gpus, 1):
                print(f"\n  Видеокарта #{i}: {gpu.name}")
                print(f"    Память: {format_size(gpu.memoryTotal * 1024 * 1024)}")
                print(f"    Используется: {format_size(gpu.memoryUsed * 1024 * 1024)}")
                print(f"    Загрузка: {gpu.load * 100:.1f}%")
                temp = gpu.temperature if gpu.temperature is not None else 'N/A'
                print(f"    Температура: {temp}°C")
    except Exception as e:
        print(f"  Ошибка получения данных о видеокарте: {str(e)}")

    get_disk_info()

    print(f"\n{' СИСТЕМА ':-^60}")
    try:
        boot_time = datetime.fromtimestamp(psutil.boot_time())
        uptime = datetime.now() - boot_time
        print(f"  Время загрузки: {boot_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"  Время работы: {str(uptime).split('.')[0]}")
    except Exception as e:
        print(f"  Ошибка получения времени работы: {str(e)}")

    print("\n" + "="*60)
    print(f"{' КОНЕЦ ОТЧЕТА ':=^60}")
    print("="*60)


if __name__ == "__main__":
    get_system_info()