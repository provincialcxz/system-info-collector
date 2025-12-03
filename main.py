import psutil
import platform
import cpuinfo
import GPUtil
import subprocess
import socket
import os
import sys
import argparse
from datetime import datetime
from typing import Optional


class SystemInfoCollector:
    def __init__(self, verbose: bool = False):
        self.verbose = verbose
        self.output_lines = []
        
    def print_and_capture(self, text: str):
        print(text)
        self.output_lines.append(text)
    
    def format_size(self, bytes_size: float) -> str:
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if bytes_size < 1024:
                return f"{bytes_size:.2f} {unit}"
            bytes_size /= 1024
        return f"{bytes_size:.2f} PB"
    
    def get_system_model(self) -> str:
        try:
            system = platform.system()
            
            if system == "Windows":
                # через wmic
                try:
                    result = subprocess.check_output(
                        "wmic csproduct get name",
                        shell=True,
                        encoding="utf-8",
                        stderr=subprocess.DEVNULL
                    ).strip()
                    lines = result.split('\n')
                    if len(lines) > 1:
                        model = lines[1].strip()
                        if model and model.lower() != "name":
                            return model
                except:
                    pass
                
                # через systeminfo
                try:
                    result = subprocess.check_output(
                        "systeminfo | findstr /C:\"System Model\"",
                        shell=True,
                        encoding="utf-8",
                        stderr=subprocess.DEVNULL
                    ).strip()
                    if result:
                        return result.split(":")[1].strip()
                except:
                    pass
                
                # через реестр
                try:
                    result = subprocess.check_output(
                        "reg query HKEY_LOCAL_MACHINE\\HARDWARE\\DESCRIPTION\\System\\BIOS /v SystemProductName",
                        shell=True,
                        encoding="utf-8",
                        stderr=subprocess.DEVNULL
                    ).strip()
                    if result:
                        lines = result.split('\n')
                        if len(lines) > 1:
                            return lines[-1].split("REG_SZ")[-1].strip()
                except:
                    pass
                    
            elif system == "Linux":
                try:
                    with open('/sys/class/dmi/id/product_name', 'r') as f:
                        model = f.read().strip()
                        if model:
                            return model
                except:
                    pass
                    
                try:
                    result = subprocess.check_output(
                        "cat /proc/cpuinfo | grep 'model name' | head -1",
                        shell=True,
                        encoding="utf-8"
                    )
                    return result.split(":")[-1].strip()
                except:
                    pass
                    
            elif system == "Darwin":
                try:
                    result = subprocess.check_output(
                        "sysctl -n hw.model",
                        shell=True,
                        encoding="utf-8"
                    )
                    return result.strip()
                except:
                    pass
                    
            return "Неизвестно"
            
        except Exception:
            return "Неизвестно"
    
    def get_basic_info(self):
        self.print_and_capture("\n" + "="*60)
        self.print_and_capture(f"{' СИСТЕМНАЯ ИНФОРМАЦИЯ (КРАТКО) ':=^60}")
        self.print_and_capture(f"  Дата и время: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        self.print_and_capture("="*60)
        
        self.print_and_capture(f"\n{' ОСНОВНЫЕ ДАННЫЕ ':-^60}")
        self.print_and_capture(f"  Модель системы: {self.get_system_model()}")
        self.print_and_capture(f"  Имя компьютера: {platform.node()}")
        self.print_and_capture(f"  ОС: {platform.system()} {platform.release()}")
        self.print_and_capture(f"  Архитектура: {platform.machine()}")
        
        try:
            cpu_info = cpuinfo.get_cpu_info()
            self.print_and_capture(f"\n{' ПРОЦЕССОР ':-^60}")
            self.print_and_capture(f"  Модель: {cpu_info.get('brand_raw', 'Неизвестно')}")
            self.print_and_capture(f"  Ядер/потоков: {psutil.cpu_count(logical=False)}/{psutil.cpu_count(logical=True)}")
            self.print_and_capture(f"  Загрузка: {psutil.cpu_percent(interval=0.5):.1f}%")
        except Exception:
            pass
        
        try:
            mem = psutil.virtual_memory()
            self.print_and_capture(f"\n{' ОПЕРАТИВНАЯ ПАМЯТЬ ':-^60}")
            self.print_and_capture(f"  Всего: {self.format_size(mem.total)}")
            self.print_and_capture(f"  Используется: {self.format_size(mem.used)}")
            self.print_and_capture(f"  Загрузка: {mem.percent:.1f}%")
        except Exception:
            pass
        
        try:
            self.print_and_capture(f"\n{' ДИСКИ ':-^60}")
            partitions = psutil.disk_partitions(all=False)
            for part in partitions:
                if part.fstype and len(part.mountpoint) <= 3:
                    try:
                        usage = psutil.disk_usage(part.mountpoint)
                        self.print_and_capture(f"  {part.mountpoint}: {self.format_size(usage.total)} свободно {self.format_size(usage.free)} ({usage.percent:.1f}% заполнено)")
                    except Exception:
                        pass
        except Exception:
            pass
        
        self.print_and_capture("\n" + "="*60)
        self.print_and_capture(f"{' КОНЕЦ ОТЧЕТА ':=^60}")
        self.print_and_capture("="*60)
    
    def get_verbose_info(self):
        self.print_and_capture("\n" + "="*60)
        self.print_and_capture(f"{' СИСТЕМНАЯ ИНФОРМАЦИЯ (ПОЛНОСТЬЮ) ':=^60}")
        self.print_and_capture(f"  Дата и время: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        self.print_and_capture("="*60)
        
        self.print_and_capture(f"\n{' ОСНОВНЫЕ ДАННЫЕ ':-^60}")
        self.print_and_capture(f"  Модель системы: {self.get_system_model()}")
        self.print_and_capture(f"  Имя компьютера: {platform.node()}")
        self.print_and_capture(f"  ОС: {platform.system()} {platform.release()}")
        self.print_and_capture(f"  Версия ОС: {platform.version()}")
        self.print_and_capture(f"  Архитектура: {platform.machine()}")
        self.print_and_capture(f"  Процессор: {platform.processor()}")
        
        self.print_and_capture(f"\n{' ПРОЦЕССОР ':-^60}")
        try:
            cpu_info = cpuinfo.get_cpu_info()
            self.print_and_capture(f"  Производитель: {cpu_info.get('vendor_id_raw', 'Неизвестно')}")
            self.print_and_capture(f"  Модель: {cpu_info.get('brand_raw', 'Неизвестно')}")
            
            physical_cores = psutil.cpu_count(logical=False)
            logical_cores = psutil.cpu_count(logical=True)
            self.print_and_capture(f"  Ядер/потоков: {physical_cores}/{logical_cores}")
            
            if (freq := psutil.cpu_freq()):
                self.print_and_capture(f"  Текущая частота: {freq.current:.2f} MHz")
                if freq.max:
                    self.print_and_capture(f"  Максимальная частота: {freq.max:.2f} MHz")
            else:
                self.print_and_capture(f"  Частота: Неизвестна")
            
            cpu_load = psutil.cpu_percent(interval=0.5)
            self.print_and_capture(f"  Общая загрузка: {cpu_load:.1f}%")
            
            if 'l3_cache_size' in cpu_info:
                cache_size = cpu_info['l3_cache_size']
                if cache_size:
                    self.print_and_capture(f"  Кэш L3: {self.format_size(cache_size)}")
                    
        except Exception as e:
            self.print_and_capture(f"  Ошибка получения данных о процессоре: {str(e)}")
        
        self.print_and_capture(f"\n{' ОПЕРАТИВНАЯ ПАМЯТЬ ':-^60}")
        try:
            mem = psutil.virtual_memory()
            swap = psutil.swap_memory()
            
            self.print_and_capture(f"  Всего RAM: {self.format_size(mem.total)}")
            self.print_and_capture(f"  Доступно RAM: {self.format_size(mem.available)}")
            self.print_and_capture(f"  Используется RAM: {self.format_size(mem.used)}")
            self.print_and_capture(f"  Загрузка RAM: {mem.percent:.1f}%")
            
            if swap.total > 0:
                self.print_and_capture(f"\n  Всего Swap: {self.format_size(swap.total)}")
                self.print_and_capture(f"  Используется Swap: {self.format_size(swap.used)}")
                self.print_and_capture(f"  Загрузка Swap: {swap.percent:.1f}%")
            
        except Exception as e:
            self.print_and_capture(f"  Ошибка получения данных о памяти: {str(e)}")
        
        self.print_and_capture(f"\n{' ВИДЕОКАРТА ':-^60}")
        try:
            gpus = GPUtil.getGPUs()
            if not gpus:
                self.print_and_capture("  Видеокарты не обнаружены")
            else:
                for i, gpu in enumerate(gpus, 1):
                    self.print_and_capture(f"\n  Видеокарта #{i}: {gpu.name}")
                    self.print_and_capture(f"    Память: {self.format_size(gpu.memoryTotal * 1024 * 1024)}")
                    self.print_and_capture(f"    Используется: {self.format_size(gpu.memoryUsed * 1024 * 1024)}")
                    self.print_and_capture(f"    Загрузка GPU: {gpu.load * 100:.1f}%")
                    temp = gpu.temperature if gpu.temperature is not None else 'N/A'
                    self.print_and_capture(f"    Температура: {temp}°C")
                    
        except Exception as e:
            self.print_and_capture(f"  Ошибка получения данных о видеокарте: {str(e)}")
        
        self.get_disk_info_verbose()
        
        self.get_network_info()
        
        self.get_battery_info()
        
        if platform.system() == "Windows":
            self.get_windows_specific_info()
        
        self.print_and_capture(f"\n{' СИСТЕМА ':-^60}")
        try:
            boot_time = datetime.fromtimestamp(psutil.boot_time())
            uptime = datetime.now() - boot_time
            
            days = uptime.days
            hours, remainder = divmod(uptime.seconds, 3600)
            minutes, seconds = divmod(remainder, 60)
            
            uptime_str = ""
            if days > 0:
                uptime_str += f"{days} дн. "
            uptime_str += f"{hours:02d}:{minutes:02d}:{seconds:02d}"
            
            self.print_and_capture(f"  Время загрузки: {boot_time.strftime('%Y-%m-%d %H:%M:%S')}")
            self.print_and_capture(f"  Время работы: {uptime_str}")
            
        except Exception as e:
            self.print_and_capture(f"  Ошибка получения времени работы: {str(e)}")
        
        self.print_and_capture("\n" + "="*60)
        self.print_and_capture(f"{' КОНЕЦ ОТЧЕТА ':=^60}")
        self.print_and_capture("="*60)
    

    def get_disk_info_verbose(self):
        self.print_and_capture(f"\n{' НАКОПИТЕЛИ ИНФОРМАЦИИ ':-^60}")
        
        try:
            partitions = psutil.disk_partitions(all=True)
            local_disks = []
            network_disks = []
            optical_drives = []
            removable_disks = []
            other_devices = []
            
            for part in partitions:
                if part.fstype == '' or 'cdrom' in part.opts.lower():
                    optical_drives.append((part.device, part.mountpoint))
                    continue
                
                if 'remote' in part.opts.lower() or part.fstype in ('cifs', 'nfs', 'smbfs'):
                    try:
                        usage = psutil.disk_usage(part.mountpoint)
                        network_disks.append((part.device, part.mountpoint, part.fstype, usage, "Network"))
                    except Exception:
                        network_disks.append((part.device, part.mountpoint, part.fstype, None, "Network"))
                    continue
                
                if platform.system() == "Windows":
                    try:
                        import ctypes
                        drive_type = ctypes.windll.kernel32.GetDriveTypeW(part.mountpoint)
                        
                        if drive_type == 2:  # DRIVE_REMOVABLE
                            try:
                                usage = psutil.disk_usage(part.mountpoint)
                                removable_disks.append((part.device, part.mountpoint, part.fstype, usage, "Removable"))
                            except Exception:
                                removable_disks.append((part.device, part.mountpoint, part.fstype, None, "Removable"))
                            continue
                        
                        elif drive_type == 4:  # DRIVE_REMOTE
                            try:
                                usage = psutil.disk_usage(part.mountpoint)
                                network_disks.append((part.device, part.mountpoint, part.fstype, usage, "Network"))
                            except Exception:
                                network_disks.append((part.device, part.mountpoint, part.fstype, None, "Network"))
                            continue
                        
                        elif drive_type == 5:  # DRIVE_CDROM
                            optical_drives.append((part.device, part.mountpoint))
                            continue
                            
                    except Exception:
                        pass
                
                skip_fs = {'tmpfs', 'devtmpfs', 'squashfs', 'overlay', 'efivarfs'}
                if part.fstype in skip_fs:
                    continue
                
                try:
                    usage = psutil.disk_usage(part.mountpoint)
                    local_disks.append((part.device, part.mountpoint, part.fstype, usage, "Local"))
                except Exception:
                    other_devices.append((part.device, part.mountpoint, "Недоступен"))
            
            def print_disk_section(disks, title):
                if not disks:
                    return
                
                self.print_and_capture(f"\n  [{title}]")
                for i, (device, mountpoint, fstype, usage, disk_type) in enumerate(disks, 1):
                    self.print_and_capture(f"\n    Диск #{i}:")
                    self.print_and_capture(f"      Устройство: {device}")
                    self.print_and_capture(f"      Точка монтирования: {mountpoint}")
                    self.print_and_capture(f"      Тип: {disk_type}")
                    self.print_and_capture(f"      Файловая система: {fstype}")
                    
                    if usage:
                        self.print_and_capture(f"      Общий размер: {self.format_size(usage.total)}")
                        self.print_and_capture(f"      Использовано: {self.format_size(usage.used)}")
                        self.print_and_capture(f"      Свободно: {self.format_size(usage.free)}")
                        self.print_and_capture(f"      Заполнено: {usage.percent:.1f}%")
                        
                    else:
                        self.print_and_capture(f"      Статус: Недоступен")
            
            print_disk_section(local_disks, "ЛОКАЛЬНЫЕ ДИСКИ")
            print_disk_section(network_disks, "СЕТЕВЫЕ ДИСКИ")
            print_disk_section(removable_disks, "СЪЕМНЫЕ НОСИТЕЛИ")
            
            if optical_drives:
                self.print_and_capture(f"\n  [CD/DVD ПРИВОДЫ]")
                for device, mountpoint in optical_drives:
                    self.print_and_capture(f"    • {device} ({mountpoint})")
            
            if other_devices:
                self.print_and_capture(f"\n  [ДРУГИЕ УСТРОЙСТВА]")
                for device, mountpoint, error in other_devices:
                    self.print_and_capture(f"    • {device} ({mountpoint}) - {error}")
            
            if not (local_disks or network_disks or removable_disks or optical_drives):
                self.print_and_capture("  Нет доступных дисков для анализа")
        
        except Exception as e:
            self.print_and_capture(f"  Ошибка получения информации о дисках: {str(e)}")
    
    def get_network_info(self):
        self.print_and_capture(f"\n{' СЕТЕВЫЕ ИНТЕРФЕЙСЫ ':-^60}")
        
        try:
            interfaces = psutil.net_if_addrs()
            stats = psutil.net_if_stats()
            
            for interface_name, addresses in interfaces.items():
                if interface_name not in stats:
                    continue
                    
                stat = stats[interface_name]
                if interface_name.startswith('Loopback'):
                    continue
                
                self.print_and_capture(f"\n  Интерфейс: {interface_name}")
                self.print_and_capture(f"    Статус: {'Активен' if stat.isup else 'Неактивен'}")
                
                mac_address = None
                for addr in addresses:
                    if addr.family == psutil.AF_LINK:
                        mac_address = addr.address
                        break
                
                if mac_address:
                    self.print_and_capture(f"    MAC: {mac_address}")
                
                ipv4_addrs = []
                ipv6_addrs = []
                for addr in addresses:
                    if addr.family == socket.AF_INET:
                        ipv4_addrs.append(addr.address)
                    elif addr.family == socket.AF_INET6 and not addr.address.startswith('fe80:'):
                        ipv6_addrs.append(addr.address)
                
                if ipv4_addrs:
                    self.print_and_capture(f"    IPv4: {', '.join(ipv4_addrs)}")
                if ipv6_addrs:
                    self.print_and_capture(f"    IPv6: {', '.join(ipv6_addrs)}")
                
                if stat.speed > 0:
                    self.print_and_capture(f"    Скорость: {stat.speed} Mbps")
                    
        except Exception as e:
            self.print_and_capture(f"  Ошибка получения сетевой информации: {str(e)}")
    
    def get_battery_info(self):
        try:
            battery = psutil.sensors_battery()
            if battery:
                self.print_and_capture(f"\n{' АККУМУЛЯТОР ':-^60}")
                self.print_and_capture(f"  Заряд: {battery.percent}%")
                status = "Заряжается" if battery.power_plugged else "Разряжается"
                self.print_and_capture(f"  Статус: {status}")
                
                if battery.secsleft not in (psutil.POWER_TIME_UNLIMITED, -1):
                    if battery.secsleft > 0:
                        hours = battery.secsleft // 3600
                        minutes = (battery.secsleft % 3600) // 60
                        self.print_and_capture(f"  Осталось: {hours} ч {minutes} мин")
        except Exception:
            pass
    
    def get_windows_specific_info(self):
        if platform.system() != "Windows":
            return
            
        self.print_and_capture(f"\n{' WINDOWS ИНФОРМАЦИЯ ':-^60}")
        
        try:
            result = subprocess.check_output(
                "ver",
                shell=True,
                encoding="utf-8",
                stderr=subprocess.DEVNULL
            ).strip()
            if result:
                self.print_and_capture(f"  Командная строка: {result}")
            
            try:
                import winreg
                key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, 
                                    r"SOFTWARE\Microsoft\Windows NT\CurrentVersion")
                build_number = winreg.QueryValueEx(key, "CurrentBuildNumber")[0]
                display_version = winreg.QueryValueEx(key, "DisplayVersion")[0]
                self.print_and_capture(f"  Сборка: {build_number}")
                self.print_and_capture(f"  Версия отображения: {display_version}")
                winreg.CloseKey(key)
            except:
                pass
                
            try:
                import ctypes
                import getpass
                self.print_and_capture(f"  Пользователь: {getpass.getuser()}")
                
                is_admin = ctypes.windll.shell32.IsUserAnAdmin() != 0
                self.print_and_capture(f"  Администратор: {'Да' if is_admin else 'Нет'}")
            except:
                pass
                
        except Exception:
            self.print_and_capture(f"  Не удалось получить информацию Windows")
    
    def save_to_file(self, filename: str = "system_info.txt"):
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                f.write('\n'.join(self.output_lines))
            print(f"\nОтчет сохранен в файл: {filename}")
            return True
        except Exception as e:
            print(f"\nОшибка при сохранении в файл: {str(e)}")
            return False


def print_help():
    print("""

ИСПОЛЬЗОВАНИЕ:
  python main.py [ПАРАМЕТРЫ]

ПАРАМЕТРЫ:
  -h, --help            Показать эту справку
  -v, --verbose         Полный подробный отчет
  -o ФАЙЛ, --output ФАЙЛ
                        Сохранить отчет в указанный файл
  -q, --quiet           Только сохранить в файл, не выводить на экран

ПРИМЕРЫ:
  python main.py                      # Краткий отчет (по умолчанию)
  python main.py -v                   # Полный подробный отчет
  python main.py -o res.txt           # Краткий отчет с сохранением в файл
  python main.py -v -o full_res.txt   # Полный отчет с сохранением в файл
  python main.py -q                   # Тихий режим (автосохранение)

АВТОР: System Info Collector Team
ЛИЦЕНЗИЯ: MIT
    """)
    sys.exit(0)


def main():
    verbose = False
    output_file = None
    quiet = False
    
    args = sys.argv[1:]
    
    i = 0
    while i < len(args):
        arg = args[i]
        
        if arg in ('-h', '--help'):
            print_help()
        elif arg in ('-v', '--verbose'):
            verbose = True
        elif arg in ('-o', '--output'):
            if i + 1 < len(args):
                output_file = args[i + 1]
                i += 1
            else:
                print("Ошибка: для параметра -o необходимо указать имя файла")
                sys.exit(1)
        elif arg in ('-q', '--quiet'):
            quiet = True
        else:
            print(f"Неизвестный параметр: {arg}")
            print_help()
            sys.exit(1)
        
        i += 1
    
    collector = SystemInfoCollector(verbose=verbose)
    
    if quiet:
        original_stdout = sys.stdout
        sys.stdout = open(os.devnull, 'w')
    
    try:
        if verbose:
            collector.get_verbose_info()
        else:
            collector.get_basic_info()
        
        if quiet:
            sys.stdout.close()
            sys.stdout = original_stdout
        
        if output_file:
            filename = output_file
        elif quiet:
            filename = "system_info.txt"
        else:
            response = input("\nСохранить отчет в файл? (y/n/д/н): ").lower()
            if response in ('y', 'д', 'да', 'yes'):
                filename = input("Имя файла (по умолчанию: system_info.txt): ").strip()
                if not filename:
                    filename = "system_info.txt"
            else:
                print("Отчет не сохранен.")
                return
        
        if collector.save_to_file(filename):
            if not quiet:
                print(f"Отчет успешно сохранен в файл: {filename}")
        else:
            if not quiet:
                print("Не удалось сохранить отчет в файл")
    
    except KeyboardInterrupt:
        if not quiet:
            print("\n\nОперация прервана пользователем")
    except Exception as e:
        if not quiet:
            print(f"\nПроизошла ошибка: {str(e)}")
            import traceback
            traceback.print_exc()


if __name__ == "__main__":
    main()
