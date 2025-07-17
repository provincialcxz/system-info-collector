# System Info Collector

Скрипт для сбора информации о системе: процессор, видеокарта, память, диск и другие характеристики.

  
## Установка и использование

### Python 3.12.3
1. Скачайте установщик с [официального сайта](https://www.python.org/downloads/release/python-3123/)
2. Запустите установщик
3. В процессе установки обязательно отметьте галочку **"Add Python to PATH"**

### Запуск
```bash
git clone https://github.com/provincialcxz/System-Info-Collector.git

cd system-info-collector/

python -m venv venv

# Windows
venv\Scripts\activate
# Unix
source venv/bin/activate

pip install -r requirements.txt

python ./main.py
```
