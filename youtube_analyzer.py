#!/usr/bin/env python3
"""
YouTube History Analyzer
Анализатор истории просмотров YouTube с TUI интерфейсом
"""

import json
import re
import pandas as pd
from pathlib import Path
from typing import Dict, Any, List, Optional
from rich.console import Console
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.prompt import Confirm
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

class YouTubeAnalyzer:
    def __init__(self):
        self.console = Console()
        self.data = []
        self.data_sources = {
            'watch_history': [],
            'my_activity': []
        }
        self.df = None
        self.video_durations = {}
        self.output_dir = Path("youtube_analysis_output")
        self.output_dir.mkdir(exist_ok=True)
    
    def load_data_source(self, file_path: str, source_type: str) -> bool:
        """Загрузка данных из указанного источника"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # Пытаемся исправить возможные проблемы с JSON
            content = content.replace(',]', ']').replace(',}', '}')
            
            data = json.loads(content)
            
            if isinstance(data, list):
                self.data_sources[source_type] = data
                self.console.print(f"✓ Загружено {len(data)} записей из {source_type}")
                return True
            else:
                self.console.print(f"[red]Ошибка: файл {source_type} не содержит список[/red]")
                return False
                
        except json.JSONDecodeError as e:
            self.console.print(f"[red]Ошибка парсинга JSON в {source_type}: {e}[/red]")
            return False
        except Exception as e:
            self.console.print(f"[red]Ошибка загрузки {source_type}: {e}[/red]")
            return False
    
    def load_history(self, file_path: str) -> bool:
        """Загрузка истории просмотров (для обратной совместимости)"""
        return self.load_data_source(file_path, 'watch_history')
    
    def extract_video_id(self, url: str) -> Optional[str]:
        """Извлечение ID видео из URL"""
        if not url:
            return None
            
        # Паттерны для различных форматов URL YouTube
        patterns = [
            r'(?:youtube\.com/watch\?v=|youtu\.be/|music\.youtube\.com/watch\?v=)([a-zA-Z0-9_-]{11})',
            r'youtube\.com/embed/([a-zA-Z0-9_-]{11})',
            r'youtube\.com/v/([a-zA-Z0-9_-]{11})'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)
        
        return None
    
    def merge_data_sources(self) -> None:
        """Объединение данных из разных источников без дублей"""
        self.console.print("[bold blue]Объединяю данные из разных источников...[/bold blue]")
        
        unique_records = {}
        duplicates_count = 0
        total_items = sum(len(data) for data in self.data_sources.values() if data)
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=self.console
        ) as progress:
            task = progress.add_task("Дедупликация записей...", total=total_items)
            
            for source_type, data in self.data_sources.items():
                if not data:
                    continue
                    
                for item in data:
                    # Игнорируем YouTube Music
                    if item.get('header') == 'YouTube Music':
                        progress.advance(task)
                        continue
                    
                    # Игнорируем записи с music.youtube.com
                    if 'titleUrl' in item and 'music.youtube.com' in item['titleUrl']:
                        progress.advance(task)
                        continue
                    
                    # Для My Activity берем только Watched записи
                    if source_type == 'my_activity' and not item.get('title', '').startswith('Watched'):
                        progress.advance(task)
                        continue
                        
                    if 'titleUrl' in item and 'time' in item:
                        video_id = self.extract_video_id(item['titleUrl'])
                        
                        if video_id:
                            unique_key = f"{video_id}_{item['time']}"
                            
                            if unique_key not in unique_records:
                                item_with_source = item.copy()
                                item_with_source['_source'] = source_type
                                unique_records[unique_key] = item_with_source
                            else:
                                duplicates_count += 1
                    
                    progress.advance(task)
            
            self.data = list(unique_records.values())
            self.console.print(f"[green]✓ Объединено {len(self.data)} уникальных записей[/green]")
            self.console.print(f"[yellow]Найдено и удалено {duplicates_count} дублей[/yellow]")
    
    def process_data(self) -> None:
        """Обработка данных истории"""
        self.console.print("[bold blue]Обрабатываю данные...[/bold blue]")
        
        if len([data for data in self.data_sources.values() if data]) > 1:
            self.merge_data_sources()
        else:
            for source_type, data in self.data_sources.items():
                if data:
                    self.data = data
                    break
        
        processed_data = []
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=self.console
        ) as progress:
            task = progress.add_task("Обработка записей...", total=len(self.data))
            
            for item in self.data:
                # Игнорируем YouTube Music
                if item.get('header') == 'YouTube Music':
                    progress.advance(task)
                    continue
                
                # Игнорируем записи с music.youtube.com
                if 'titleUrl' in item and 'music.youtube.com' in item['titleUrl']:
                    progress.advance(task)
                    continue
                
                # Для My Activity берем только Watched записи
                if item.get('_source') == 'my_activity' and not item.get('title', '').startswith('Watched'):
                    progress.advance(task)
                    continue
                    
                if 'titleUrl' in item and 'time' in item:
                    video_id = self.extract_video_id(item['titleUrl'])
                    
                    if video_id:
                        processed_item = {
                            'timestamp': item['time'],
                            'video_id': video_id,
                            'title': item.get('title', 'Unknown'),
                            'url': item['titleUrl'],
                            'channel': item.get('subtitles', [{}])[0].get('name', 'Unknown') if item.get('subtitles') else 'Unknown',
                            'source': item.get('_source', 'unknown')
                        }
                        processed_data.append(processed_item)
                
                progress.advance(task)
        
        self.df = pd.DataFrame(processed_data)
        if len(self.df) > 0:
            self.df['timestamp'] = pd.to_datetime(self.df['timestamp'])
            self.df['date'] = self.df['timestamp'].dt.date
            self.df['hour'] = self.df['timestamp'].dt.hour
            self.df['day_of_week'] = self.df['timestamp'].dt.day_name()
            self.df['month'] = self.df['timestamp'].dt.month
            self.df['year'] = self.df['timestamp'].dt.year
        
        self.console.print(f"[green]✓ Обработано {len(self.df)} записей[/green]")
    
    def get_durations(self, sample_size: int = 100) -> None:
        """Получение длительности видео для выборки"""
        if self.df is None or len(self.df) == 0:
            self.console.print("[red]Нет данных для анализа![/red]")
            return
        
        self.console.print(f"[bold blue]Получаю длительность для {sample_size} видео...[/bold blue]")
        
        # Фильтруем видео с доступными каналами (не Unknown)
        available_videos = self.df[self.df['channel'] != 'Unknown'].copy()
        
        if len(available_videos) == 0:
            self.console.print("[red]Нет доступных видео с известными каналами![/red]")
            return
        
        # Берем случайную выборку из доступных видео
        sample_size = min(sample_size, len(available_videos))
        sample = available_videos.sample(sample_size)
        
        self.console.print(f"[blue]Выбрано {len(sample)} видео с доступными каналами[/blue]")
        self.console.print(f"[blue]Всего доступных видео: {len(available_videos)}[/blue]")
        
        # Получаем длительность через curl
        self.get_durations_api(sample)
    
    def get_durations_ytdlp(self, sample_df) -> None:
        """Получение длительности через yt-dlp"""
        try:
            import yt_dlp
            
            self.console.print("[blue]Используется yt-dlp для получения длительности...[/blue]")
            
            # Настройки yt-dlp для получения метаданных (рабочая версия)
            ydl_opts = {
                'quiet': False,  # Включаем вывод для отладки
                'no_warnings': False,  # Показываем предупреждения
                'skip_download': True,
                'verbose': True,  # Подробный вывод
                'ignoreerrors': True,  # Продолжаем при ошибках
                'listformats': True,  # Получаем список форматов (включает метаданные)
            }
            
            # Добавляем cookies если есть
            cookies_file = Path("youtube_cookies.txt")  # Ваш основной файл cookies
            if cookies_file.exists():
                # Создаем временную копию для yt-dlp
                import shutil
                temp_cookies = Path("temp_cookies.txt")
                shutil.copy2(cookies_file, temp_cookies)
                
                ydl_opts['cookiefile'] = str(temp_cookies)
                self.console.print("[green]✓ Используются cookies для авторизации[/green]")
                self.console.print("[blue]Создана временная копия cookies для yt-dlp[/blue]")
            else:
                self.console.print("[yellow]⚠️ Файл youtube_cookies.txt не найден![/yellow]")
                self.console.print("[yellow]Создайте файл youtube_cookies.txt для обхода блокировок[/yellow]")
                self.show_cookies_instructions()
            
            # Добавляем user-agent и заголовки
            ydl_opts['http_headers'] = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
                'Accept-Encoding': 'gzip, deflate',
                'DNT': '1',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1',
            }
            
            # Добавляем прокси если нужно (раскомментируйте при необходимости)
            # ydl_opts['proxy'] = 'socks5://127.0.0.1:1080'
            
            # Добавляем задержки между запросами
            ydl_opts['sleep_interval'] = 1
            ydl_opts['max_sleep_interval'] = 3
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                processed = 0
                total = len(sample_df)
                
                with Progress(
                    SpinnerColumn(),
                    TextColumn("[progress.description]{task.description}"),
                    console=self.console
                ) as progress:
                    task = progress.add_task("Получение длительности...", total=total)
                    
                    for _, row in sample_df.iterrows():
                        video_id = row['video_id']
                        video_url = row['url']
                        
                        try:
                            # Получаем информацию о видео
                            self.console.print(f"\n[blue]🔍 Получаю информацию для: {row['title'][:50]}...[/blue]")
                            self.console.print(f"[blue]URL: {video_url}[/blue]")
                            
                            # Получаем информацию в extract_flat режиме
                            info = ydl.extract_info(video_url, download=False)
                            
                            if info and 'duration' in info:
                                duration = info['duration']
                                self.video_durations[video_id] = duration
                                
                                # Показываем прогресс
                                minutes = duration // 60
                                seconds = duration % 60
                                progress.update(task, description=f"✓ {row['title'][:30]}... ({minutes}:{seconds:02d})")
                            else:
                                progress.update(task, description=f"❌ {row['title'][:30]}... (длительность не найдена)")
                            
                            processed += 1
                            
                        except Exception as e:
                            progress.update(task, description=f"❌ {row['title'][:30]}... (ошибка: {str(e)[:20]})")
                            self.console.print(f"[red]❌ Ошибка: {str(e)}[/red]")
                            processed += 1
                        
                        progress.advance(task)
                        
                        # Небольшая задержка чтобы не перегружать YouTube
                        import time
                        time.sleep(1)
                
                self.console.print(f"\n[green]✓ Получена длительность для {len(self.video_durations)} из {total} видео[/green]")
                
                # Очищаем временный файл cookies
                temp_cookies = Path("temp_cookies.txt")
                if temp_cookies.exists():
                    temp_cookies.unlink()
                    self.console.print("[blue]✓ Временный файл cookies удален[/blue]")
                
                if self.video_durations:
                    self.show_duration_statistics()
                else:
                    self.console.print("[yellow]⚠️ Не удалось получить длительность ни для одного видео[/yellow]")
                    self.console.print("[yellow]Возможные причины:[/yellow]")
                    self.console.print("[yellow]  - Google блокирует запросы[/yellow]")
                    self.console.print("[yellow]  - Неправильные cookies[/yellow]")
                    self.console.print("[yellow]  - Видео недоступны[/yellow]")
                    self.show_cookies_instructions()
            
        except ImportError:
            self.console.print("[red]yt-dlp не установлен! Установите: pip install yt-dlp[/red]")
        except Exception as e:
            self.console.print(f"[red]Ошибка при использовании yt-dlp: {e}[/red]")
            self.console.print("[yellow]Попробуйте обновить cookies или использовать VPN[/yellow]")
        
    def show_cookies_instructions(self) -> None:
        """Показ инструкций по настройке cookies"""
        self.console.print("\n[bold blue]🍪 Инструкция по настройке cookies:[/bold blue]")
        self.console.print("1. Установите расширение 'Get cookies.txt' в браузере")
        self.console.print("2. Зайдите на YouTube и войдите в аккаунт")
        self.console.print("3. Экспортируйте cookies в файл youtube_cookies.txt")
        self.console.print("4. Поместите файл в папку проекта")
        self.console.print("5. Перезапустите анализатор")
        self.console.print("\n[blue]Подробные инструкции: см. файл COOKIES_INSTRUCTIONS.md[/blue]")
    
    def show_api_instructions(self) -> None:
        """Показывает инструкции по настройке YouTube API"""
        self.console.print("\n🍪 Инструкция по настройке YouTube API:")
        self.console.print("1. Перейдите на https://console.developers.google.com/")
        self.console.print("2. Создайте новый проект или выберите существующий")
        self.console.print("3. Включите YouTube Data API v3")
        self.console.print("4. Создайте учетные данные (API ключ)")
        self.console.print("5. Скопируйте API ключ в файл youtube_api_key.txt")
        self.console.print("6. Поместите файл в папку проекта")
        self.console.print("7. Перезапустите анализатор")
        self.console.print("\n[blue]Подробные инструкции: см. файл API_INSTRUCTIONS.md[/blue]")
    
    def parse_iso_duration(self, duration_str: str) -> int:
        """Парсит длительность в формате ISO 8601 (PT3M7S) в секунды"""
        try:
            import re
            
            # Убираем префикс PT
            if not duration_str.startswith('PT'):
                return 0
            
            duration_str = duration_str[2:]  # Убираем 'PT'
            
            total_seconds = 0
            
            # Ищем часы (H)
            hours_match = re.search(r'(\d+)H', duration_str)
            if hours_match:
                total_seconds += int(hours_match.group(1)) * 3600
                duration_str = duration_str.replace(hours_match.group(0), '')
            
            # Ищем минуты (M)
            minutes_match = re.search(r'(\d+)M', duration_str)
            if minutes_match:
                total_seconds += int(minutes_match.group(1)) * 60
                duration_str = duration_str.replace(minutes_match.group(0), '')
            
            # Ищем секунды (S)
            seconds_match = re.search(r'(\d+)S', duration_str)
            if seconds_match:
                total_seconds += int(seconds_match.group(1))
            
            return total_seconds
            
        except Exception as e:
            self.console.print(f"[red]❌ Ошибка парсинга ISO длительности: {e}[/red]")
            return 0
    
    def get_durations_api(self, sample_df) -> None:
        """Получение длительности через YouTube Data API v3"""
        try:
            import requests
            import json
            import time
            
            # Проверяем наличие API ключа
            api_key_file = Path("youtube_api_key.txt")
            if not api_key_file.exists():
                self.console.print("[red]❌ Файл youtube_api_key.txt не найден![/red]")
                self.console.print("[yellow]Создайте файл с API ключом YouTube Data API v3[/yellow]")
                self.show_api_instructions()
                return
            
            with open(api_key_file, 'r') as f:
                api_key = f.read().strip()
            
            if not api_key:
                self.console.print("[red]❌ API ключ пустой![/red]")
                self.show_api_instructions()
                return
            
            self.console.print("[green]✓ Используется YouTube Data API v3[/green]")
            self.console.print(f"[blue]📋 Всего видео для обработки: {len(sample_df)}[/blue]")
            
            processed = 0
            total = len(sample_df)
            
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=self.console
            ) as progress:
                task = progress.add_task("Получение длительности через API...", total=total)
                
                for _, row in sample_df.iterrows():
                    video_id = row['video_id']
                    
                    try:
                        # Формируем URL для API запроса
                        api_url = f"https://www.googleapis.com/youtube/v3/videos"
                        params = {
                            'id': video_id,
                            'key': api_key,
                            'part': 'contentDetails,statistics'
                        }
                        
                        response = requests.get(api_url, params=params, timeout=10)
                        
                        if response.status_code == 200:
                            data = response.json()
                            
                            if data.get('items') and len(data['items']) > 0:
                                video_info = data['items'][0]
                                content_details = video_info.get('contentDetails', {})
                                
                                # Получаем длительность в формате ISO 8601 (PT3M7S)
                                duration_str = content_details.get('duration', '')
                                
                                if duration_str:
                                    duration_seconds = self.parse_iso_duration(duration_str)
                                    
                                    if duration_seconds > 0:
                                        self.video_durations[video_id] = duration_seconds
                                        minutes = duration_seconds // 60
                                        seconds = duration_seconds % 60
                                        
                                        # Вычисляем текущее среднее значение
                                        current_avg = sum(self.video_durations.values()) / len(self.video_durations)
                                        avg_minutes = int(current_avg // 60)
                                        avg_seconds = int(current_avg % 60)
                                        
                                        progress.update(task, description=f"✓ {row['title'][:30]}... ({minutes}:{seconds:02d}) | Среднее: {avg_minutes}:{avg_seconds:02d}")
                                        
                                        # Показываем изменение среднего значения каждые 5 видео
                                        if len(self.video_durations) % 5 == 0:
                                            self.console.print(f"[blue]📊 Текущее среднее: {avg_minutes}:{avg_seconds:02d} (на основе {len(self.video_durations)} видео)[/blue]")
                                        
                                        # Показываем общее количество каждые 10 видео
                                        if len(self.video_durations) % 10 == 0:
                                            total_processed = len(self.video_durations)
                                            total_remaining = total - total_processed
                                            progress_percent = (total_processed / total) * 100
                                            self.console.print(f"[green]✅ Обработано: {total_processed}/{total} видео ({progress_percent:.1f}%) | Осталось: {total_remaining}[/green]")
                                    else:
                                        progress.update(task, description=f"❌ {row['title'][:30]}... (ошибка парсинга)")
                                else:
                                    progress.update(task, description=f"❌ {row['title'][:30]}... (длительность не найдена)")
                            else:
                                progress.update(task, description=f"❌ {row['title'][:30]}... (видео недоступно)")
                        else:
                            error_msg = f"HTTP {response.status_code}"
                            if response.status_code == 403:
                                error_msg = "API ключ недействителен или превышен лимит"
                            elif response.status_code == 400:
                                error_msg = "Неверный запрос"
                            
                            progress.update(task, description=f"❌ {row['title'][:30]}... ({error_msg})")
                            
                            if response.status_code == 403:
                                self.console.print(f"[red]❌ Ошибка API: {error_msg}[/red]")
                                self.console.print("[yellow]Проверьте API ключ и лимиты[/yellow]")
                                break
                        
                        processed += 1
                        
                    except requests.exceptions.Timeout:
                        progress.update(task, description=f"❌ {row['title'][:30]}... (таймаут)")
                        processed += 1
                    except requests.exceptions.RequestException as e:
                        progress.update(task, description=f"❌ {row['title'][:30]}... (ошибка сети)")
                        processed += 1
                    except Exception as e:
                        progress.update(task, description=f"❌ {row['title'][:30]}... (ошибка: {str(e)[:20]})")
                        processed += 1
                    
                    progress.advance(task)
                    
                    # Небольшая задержка между запросами (API позволяет до 10,000 запросов в день)
                    time.sleep(0.1)
                
                self.console.print(f"\n[green]✓ Получена длительность для {len(self.video_durations)} из {total} видео[/green]")
                
                if self.video_durations:
                    self.show_duration_statistics()
                else:
                    self.console.print("[yellow]⚠️ Не удалось получить длительность ни для одного видео[/yellow]")
                    self.console.print("[yellow]Возможные причины:[/yellow]")
                    self.console.print("[yellow]  - Неверный API ключ[/yellow]")
                    self.console.print("[yellow]  - Превышен лимит API запросов[/yellow]")
                    self.console.print("[yellow]  - Видео недоступны[/yellow]")
                    self.show_api_instructions()
            
        except Exception as e:
            self.console.print(f"[red]Ошибка при использовании API: {e}[/red]")
            self.console.print("[yellow]Убедитесь, что установлен модуль requests[/yellow]")
    
    def extract_duration_from_html(self, html_content: str) -> int:
        """Извлечение длительности из HTML страницы YouTube"""
        try:
            # Ищем различные паттерны длительности
            patterns = [
                r'"lengthSeconds":"(\d+)"',  # JSON в HTML
                r'"lengthSeconds":(\d+)',  # JSON без кавычек
                r'"duration":"PT(\d+)M(\d+)S"',  # ISO 8601 формат
                r'"duration":"PT(\d+)H(\d+)M(\d+)S"',  # ISO 8601 с часами
                r'<meta property="og:video:duration" content="(\d+)"',  # Open Graph
                r'"duration":"(\d+)"',  # Простой формат
                r'data-duration="(\d+)"',  # Data атрибут
                r'"duration":(\d+)',  # Без кавычек
            ]
            
            # Отладка: показываем найденные совпадения
            found_patterns = []
            
            for i, pattern in enumerate(patterns):
                matches = re.findall(pattern, html_content)
                if matches:
                    found_patterns.append(f"Паттерн {i+1}: {pattern} -> {matches[:3]}")  # Показываем первые 3 совпадения
            
            if found_patterns:
                self.console.print(f"[blue]Найдены паттерны: {found_patterns[:2]}[/blue]")  # Показываем первые 2
            
            # Ищем длительность
            for pattern in patterns:
                match = re.search(pattern, html_content)
                if match:
                    try:
                        if 'H' in pattern:  # Формат с часами
                            hours = int(match.group(1))
                            minutes = int(match.group(2))
                            seconds = int(match.group(3))
                            result = hours * 3600 + minutes * 60 + seconds
                            self.console.print(f"[green]✓ Длительность найдена: {hours}ч {minutes}м {seconds}с = {result}с[/green]")
                            return result
                        elif 'M' in pattern and 'S' in pattern:  # Формат с минутами и секундами
                            minutes = int(match.group(1))
                            seconds = int(match.group(2))
                            result = minutes * 60 + seconds
                            self.console.print(f"[green]✓ Длительность найдена: {minutes}м {seconds}с = {result}с[/green]")
                            return result
                        else:  # Простой формат в секундах
                            result = int(match.group(1))
                            self.console.print(f"[green]✓ Длительность найдена: {result}с[/green]")
                            return result
                    except (ValueError, IndexError) as e:
                        self.console.print(f"[yellow]⚠️ Ошибка парсинга паттерна {pattern}: {e}[/yellow]")
                        continue
            
            # Если не нашли, возвращаем 0
            self.console.print("[red]❌ Длительность не найдена ни одним паттерном[/red]")
            return 0
            
        except Exception as e:
            self.console.print(f"[red]❌ Ошибка в extract_duration_from_html: {e}[/red]")
            return 0
    
    def get_durations_selenium(self, sample_df) -> None:
        """Получение длительности через Selenium (с браузером)"""
        try:
            from selenium import webdriver
            from selenium.webdriver.common.by import By
            from selenium.webdriver.support.ui import WebDriverWait
            from selenium.webdriver.support import expected_conditions as EC
            from selenium.webdriver.chrome.service import Service
            from webdriver_manager.chrome import ChromeDriverManager
            from selenium.webdriver.chrome.options import Options
            
            self.console.print("[blue]Используется Selenium для получения длительности...[/blue]")
            self.console.print("[yellow]Этот метод медленнее, но более надежен для обхода блокировок[/yellow]")
            
            # Настройки Chrome
            chrome_options = Options()
            chrome_options.add_argument("--headless")  # Фоновый режим
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--disable-gpu")
            chrome_options.add_argument("--window-size=1920,1080")
            
            # Добавляем user-agent
            chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")
            
            # Проверяем наличие cookies
            cookies_file = Path("cookies.txt")
            if cookies_file.exists():
                self.console.print("[green]✓ Найден файл cookies.txt - будет использован для авторизации[/green]")
            
            try:
                # Автоматическая установка драйвера
                service = Service(ChromeDriverManager().install())
                driver = webdriver.Chrome(service=service, options=chrome_options)
                
                # Загружаем cookies если есть
                if cookies_file.exists():
                    driver.get("https://www.youtube.com")
                    with open(cookies_file, 'r') as f:
                        for line in f:
                            if line.startswith('#') or not line.strip():
                                continue
                            try:
                                parts = line.strip().split('\t')
                                if len(parts) >= 7:
                                    cookie = {
                                        'name': parts[5],
                                        'value': parts[6],
                                        'domain': parts[0],
                                        'path': parts[2]
                                    }
                                    driver.add_cookie(cookie)
                            except:
                                continue
                    self.console.print("[green]✓ Cookies загружены в браузер[/green]")
                
                processed = 0
                total = len(sample_df)
                
                with Progress(
                    SpinnerColumn(),
                    TextColumn("[progress.description]{task.description}"),
                    console=self.console
                ) as progress:
                    task = progress.add_task("Получение длительности через браузер...", total=total)
                    
                    for _, row in sample_df.iterrows():
                        video_url = row['url']
                        video_id = row['video_id']
                        
                        try:
                            # Открываем страницу видео
                            driver.get(video_url)
                            
                            # Ждем загрузки страницы
                            WebDriverWait(driver, 10).until(
                                EC.presence_of_element_located((By.TAG_NAME, "body"))
                            )
                            
                            # Ищем элемент с длительностью
                            try:
                                duration_element = WebDriverWait(driver, 5).until(
                                    EC.presence_of_element_located((By.CSS_SELECTOR, "span.ytp-time-duration"))
                                )
                                duration_text = duration_element.text
                                
                                # Парсим длительность (формат: MM:SS или H:MM:SS)
                                duration = self.parse_duration(duration_text)
                                
                                if duration > 0:
                                    self.video_durations[video_id] = duration
                                    progress.update(task, description=f"✓ {row['title'][:30]}... ({duration_text})")
                                else:
                                    progress.update(task, description=f"❌ {row['title'][:30]}... (длительность не найдена)")
                                
                            except:
                                progress.update(task, description=f"❌ {row['title'][:30]}... (длительность не найдена)")
                            
                            processed += 1
                            
                        except Exception as e:
                            progress.update(task, description=f"❌ {row['title'][:30]}... (ошибка: {str(e)[:20]})")
                            processed += 1
                        
                        progress.advance(task)
                        
                        # Задержка между запросами
                        import time
                        time.sleep(1)
                
                driver.quit()
                
                self.console.print(f"\n[green]✓ Получена длительность для {len(self.video_durations)} из {total} видео[/green]")
                
                if self.video_durations:
                    self.show_duration_statistics()
                
            except Exception as e:
                self.console.print(f"[red]Ошибка при запуске браузера: {e}[/red]")
                self.console.print("[yellow]Попробуйте установить Chrome или использовать другой метод[/yellow]")
                
        except ImportError:
            self.console.print("[red]Selenium не установлен! Установите: pip install selenium webdriver-manager[/red]")
        except Exception as e:
            self.console.print(f"[red]Ошибка при использовании Selenium: {e}[/red]")
    
    def get_durations_manual(self, sample_df) -> None:
        """Ручной ввод длительности для тестирования"""
        self.console.print("[blue]Ручной режим для тестирования...[/blue]")
        self.console.print("[yellow]Введите длительность в формате MM:SS или H:MM:SS[/yellow]")
        
        processed = 0
        total = min(5, len(sample_df))  # Ограничиваем для тестирования
        
        for i, (_, row) in enumerate(sample_df.head(total).iterrows()):
            self.console.print(f"\n[{i+1}/{total}] {row['title'][:50]}...")
            self.console.print(f"URL: {row['url']}")
            
            duration_input = input("Длительность (MM:SS или Enter для пропуска): ").strip()
            
            if duration_input:
                try:
                    duration = self.parse_duration(duration_input)
                    if duration > 0:
                        self.video_durations[row['video_id']] = duration
                        self.console.print(f"[green]✓ Длительность: {duration_input} ({duration} сек)[/green]")
                        processed += 1
                    else:
                        self.console.print("[red]❌ Неверный формат длительности[/red]")
                except:
                    self.console.print("[red]❌ Неверный формат длительности[/red]")
            else:
                self.console.print("[yellow]Пропущено[/yellow]")
        
        self.console.print(f"\n[green]✓ Обработано {processed} видео[/green]")
        
        if self.video_durations:
            self.show_duration_statistics()
    
    def parse_duration(self, duration_text: str) -> int:
        """Парсинг длительности из текста в секунды"""
        try:
            parts = duration_text.split(':')
            if len(parts) == 2:  # MM:SS
                minutes = int(parts[0])
                seconds = int(parts[1])
                return minutes * 60 + seconds
            elif len(parts) == 3:  # H:MM:SS
                hours = int(parts[0])
                minutes = int(parts[1])
                seconds = int(parts[2])
                return hours * 3600 + minutes * 60 + seconds
            else:
                return 0
        except:
            return 0
    
    def show_duration_statistics(self) -> None:
        """Показ статистики по длительности видео"""
        if not self.video_durations:
            return
        
        self.console.print("\n[bold blue]📊 Статистика по длительности видео[/bold blue]")
        
        durations = list(self.video_durations.values())
        total_duration = sum(durations)
        avg_duration = total_duration / len(durations)
        
        # Конвертируем в часы, минуты, секунды
        total_hours = total_duration // 3600
        total_minutes = (total_duration % 3600) // 60
        total_seconds = total_duration % 60
        
        avg_minutes = avg_duration // 60
        avg_seconds = avg_duration % 60
        
        # Создаем таблицу статистики
        table = Table(title="Статистика длительности")
        table.add_column("Параметр", style="cyan")
        table.add_column("Значение", style="green")
        
        table.add_row("Всего видео с длительностью", str(len(durations)))
        table.add_row("Общее время просмотра", f"{total_hours}ч {total_minutes}м {total_seconds}с")
        table.add_row("Средняя длительность", f"{avg_minutes}м {avg_seconds}с")
        table.add_row("Самое короткое видео", f"{min(durations) // 60}м {min(durations) % 60}с")
        table.add_row("Самое длинное видео", f"{max(durations) // 60}м {max(durations) % 60}с")
        
        self.console.print(table)
        
        # Показываем распределение по длительности
        self.console.print("\n[bold blue]📈 Распределение по длительности[/bold blue]")
        
        # Группируем по диапазонам
        ranges = {
            "0-5 мин": 0,
            "5-15 мин": 0,
            "15-30 мин": 0,
            "30-60 мин": 0,
            "60+ мин": 0
        }
        
        for duration in durations:
            minutes = duration // 60
            if minutes < 5:
                ranges["0-5 мин"] += 1
            elif minutes < 15:
                ranges["5-15 мин"] += 1
            elif minutes < 30:
                ranges["15-30 мин"] += 1
            elif minutes < 60:
                ranges["30-60 мин"] += 1
            else:
                ranges["60+ мин"] += 1
        
        for range_name, count in ranges.items():
            percentage = (count / len(durations)) * 100
            self.console.print(f"  {range_name}: {count} видео ({percentage:.1f}%)")
        
        # Сохраняем длительности в CSV для дальнейшего анализа
        if self.df is not None:
            self.save_durations_to_csv()
        
        # Показываем общую статистику времени просмотра
        self.show_total_watch_time_summary()
    
    def show_total_watch_time_summary(self) -> None:
        """Показывает сводку по общему времени просмотра"""
        if not self.video_durations:
            self.console.print("[yellow]Нет данных о длительности для подсчета общего времени[/yellow]")
            return
        
        watch_stats = self.calculate_total_watch_time()
        
        self.console.print("\n[bold blue]⏰ СВОДКА ПО ВРЕМЕНИ ПРОСМОТРА[/bold blue]")
        
        # Создаем таблицу сводки
        summary_table = Table(title="Общее время просмотра")
        summary_table.add_column("Параметр", style="cyan")
        summary_table.add_column("Значение", style="green")
        
        summary_table.add_row("Всего видео в истории", str(watch_stats['total_videos']))
        summary_table.add_row("Видео с известной длительностью", str(len(self.video_durations)))
        summary_table.add_row("Видео без данных о длительности", str(watch_stats['total_videos'] - len(self.video_durations)))
        summary_table.add_row("Общее время (известные видео)", watch_stats['total_duration_formatted'])
        summary_table.add_row("Средняя длительность видео", watch_stats['avg_duration_formatted'])
        summary_table.add_row("Оценка общего времени", watch_stats['estimated_total_time_formatted'])
        
        self.console.print(summary_table)
        
        # Дополнительная информация
        if watch_stats['total_videos'] > len(self.video_durations):
            coverage_percent = (len(self.video_durations) / watch_stats['total_videos']) * 100
            self.console.print(f"\n[blue]📊 Покрытие данных: {coverage_percent:.1f}%[/blue]")
            self.console.print(f"[yellow]⚠️ Для {watch_stats['total_videos'] - len(self.video_durations)} видео длительность неизвестна[/yellow]")
            self.console.print(f"[yellow]   Общее время рассчитано с учетом оценки на основе средней длительности[/yellow]")
    
    def calculate_total_watch_time(self) -> dict:
        """Вычисляет общее время просмотра за исследуемый период"""
        if not self.video_durations or self.df is None:
            return {
                'total_videos': 0,
                'total_duration': 0,
                'total_duration_formatted': '0 часов 0 минут',
                'avg_duration': 0,
                'avg_duration_formatted': '0 минут',
                'estimated_total_time': 0,
                'estimated_total_time_formatted': '0 часов 0 минут'
            }
        
        # Время для видео с известной длительностью
        known_durations = list(self.video_durations.values())
        total_known_duration = sum(known_durations)
        total_known_videos = len(known_durations)
        total_videos = len(self.df)
        
        # Оценка общего времени (предполагаем, что неизвестные видео имеют среднюю длительность)
        if total_known_videos > 0:
            avg_duration = total_known_duration / total_known_videos
            unknown_videos = total_videos - total_known_videos
            estimated_unknown_duration = unknown_videos * avg_duration
            estimated_total_duration = total_known_duration + estimated_unknown_duration
        else:
            estimated_total_duration = 0
            avg_duration = 0
        
        # Вычисляем процент покрытия
        coverage_percent = (total_known_videos / total_videos * 100) if total_videos > 0 else 0
        
        return {
            'total_videos': total_videos,
            'total_duration': total_known_duration,
            'total_duration_formatted': self.format_duration(total_known_duration),
            'avg_duration': avg_duration,
            'avg_duration_formatted': self.format_duration(avg_duration),
            'estimated_total_time': estimated_total_duration,
            'estimated_total_time_formatted': self.format_duration(estimated_total_duration),
            'coverage_percent': coverage_percent
        }
    
    def format_duration(self, seconds: int) -> str:
        """Форматирует длительность в секундах в читаемый вид"""
        if seconds < 60:
            return f"{int(seconds)} секунд"
        elif seconds < 3600:
            minutes = int(seconds // 60)
            remaining_seconds = int(seconds % 60)
            if remaining_seconds == 0:
                return f"{minutes} минут"
            else:
                return f"{minutes} минут {remaining_seconds} секунд"
        else:
            hours = int(seconds // 3600)
            remaining_minutes = int((seconds % 3600) // 60)
            remaining_seconds = int(seconds % 60)
            if remaining_minutes == 0 and remaining_seconds == 0:
                return f"{hours} часов"
            elif remaining_seconds == 0:
                return f"{hours} часов {remaining_minutes} минут"
            else:
                return f"{hours} часов {remaining_minutes} минут {remaining_seconds} секунд"
    
    def save_durations_to_csv(self) -> None:
        """Сохранение длительностей видео в CSV"""
        if not self.video_durations:
            return
        
        # Создаем DataFrame с длительностями
        durations_data = []
        for video_id, duration in self.video_durations.items():
            video_row = self.df[self.df['video_id'] == video_id]
            if not video_row.empty:
                row = video_row.iloc[0]
                durations_data.append({
                    'video_id': video_id,
                    'title': row['title'],
                    'channel': row['channel'],
                    'url': row['url'],
                    'duration_seconds': duration,
                    'duration_formatted': f"{duration // 60}:{duration % 60:02d}",
                    'timestamp': row['timestamp'],
                    'source': row.get('source', 'unknown')
                })
        
        if durations_data:
            durations_df = pd.DataFrame(durations_data)
            csv_path = self.output_dir / "video_durations.csv"
            durations_df.to_csv(csv_path, index=False, encoding='utf-8-sig')
            
            self.console.print(f"\n[green]✓ Длительности сохранены в: {csv_path}[/green]")
            self.console.print(f"[blue]Размер файла: {csv_path.stat().st_size / 1024:.1f} KB[/blue]")
    
    def create_plots(self) -> None:
        """Создание графиков"""
        if self.df is None or len(self.df) == 0:
            self.console.print("[red]Нет данных для создания графиков![/red]")
            return
        
        self.console.print("[bold blue]Создаю графики...[/bold blue]")
        
        # График 1: Активность по месяцам
        monthly_stats = self.df.groupby([self.df['timestamp'].dt.year, self.df['timestamp'].dt.month]).size()
        monthly_stats.index = pd.to_datetime([f"{year}-{month:02d}-01" for year, month in monthly_stats.index])
        
        fig1 = go.Figure(data=[
            go.Scatter(
                x=monthly_stats.index,
                y=monthly_stats.values,
                mode='lines+markers',
                line=dict(color='#FF0000', width=3),
                marker=dict(size=8)
            )
        ])
        fig1.update_layout(
            title='Активность по месяцам',
            xaxis_title='Месяц',
            yaxis_title='Количество видео',
            template='plotly_white'
        )
        
        # График 2: Накопительное время (если есть длительности)
        if self.video_durations:
            cumulative_time = []
            dates = []
            total_time = 0
            
            for _, row in self.df.sort_values('timestamp').iterrows():
                video_id = row['video_id']
                if video_id in self.video_durations:
                    total_time += self.video_durations[video_id]
                    cumulative_time.append(total_time)
                    dates.append(row['timestamp'])
            
            if cumulative_time:
                fig2 = go.Figure(data=[
                    go.Scatter(
                        x=dates,
                        y=cumulative_time,
                        mode='lines',
                        line=dict(color='#00FF00', width=3),
                        fill='tonexty'
                    )
                ])
                fig2.update_layout(
                    title='Накопительное время просмотра',
                    xaxis_title='Дата',
                    yaxis_title='Время (секунды)',
                    template='plotly_white'
                )
            else:
                fig2 = None
        else:
            fig2 = None
        
        # График 3: Активность по дням недели
        day_stats = self.df.groupby('day_of_week').size()
        day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        day_stats = day_stats.reindex(day_order)
        
        fig3 = go.Figure(data=[
            go.Bar(
                x=day_stats.index,
                y=day_stats.values,
                marker_color='#FF6B6B'
            )
        ])
        fig3.update_layout(
            title='Активность по дням недели',
            xaxis_title='День недели',
            yaxis_title='Количество видео',
            template='plotly_white'
        )
        
        # График 4: Распределение по часам
        hour_stats = self.df.groupby('hour').size()
        
        fig4 = go.Figure(data=[
            go.Bar(
                x=hour_stats.index,
                y=hour_stats.values,
                marker_color='#4ECDC4'
            )
        ])
        fig4.update_layout(
            title='Активность по часам суток',
            xaxis_title='Час',
            yaxis_title='Количество видео',
            template='plotly_white'
        )
        
        # Сохраняем графики
        fig1.write_html(self.output_dir / "monthly_activity.html")
        if fig2:
            fig2.write_html(self.output_dir / "cumulative_time.html")
        fig3.write_html(self.output_dir / "day_of_week.html")
        fig4.write_html(self.output_dir / "hourly_activity.html")
        
        self.console.print("[green]✓ Графики сохранены[/green]")
    
    def generate_html_report(self, stats: Dict[str, Any]) -> None:
        """Генерация HTML отчета"""
        self.console.print("[bold blue]Генерирую HTML отчет...[/bold blue]")
        
        # Автоматически создаем графики
        self.console.print("[blue]Создаю графики...[/blue]")
        self.create_plots()
        
        html_content = f"""
<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Анализ истории YouTube</title>
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin: 0;
            padding: 20px;
            background-color: #f5f5f5;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            padding: 30px;
            border-radius: 10px;
            box-shadow: 0 0 20px rgba(0,0,0,0.1);
        }}
        h1 {{
            color: #FF0000;
            text-align: center;
            border-bottom: 3px solid #FF0000;
            padding-bottom: 10px;
        }}
        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin: 30px 0;
        }}
        .stat-card {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 20px;
            border-radius: 10px;
            text-align: center;
        }}
        .stat-number {{
            font-size: 2.5em;
            font-weight: bold;
            margin-bottom: 10px;
        }}
        .stat-label {{
            font-size: 1.1em;
            opacity: 0.9;
        }}
        .chart-container {{
            margin: 30px 0;
            text-align: center;
        }}
        .chart-container iframe {{
            width: 100%;
            height: 500px;
            border: none;
            border-radius: 10px;
            box-shadow: 0 5px 15px rgba(0,0,0,0.1);
        }}
        .section {{
            margin: 40px 0;
            padding: 20px;
            background: #f8f9fa;
            border-radius: 8px;
        }}
        .top-channels {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
            margin: 20px 0;
        }}
        .channel-card {{
            background: white;
            padding: 15px;
            border-radius: 8px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            text-align: center;
        }}
        .channel-name {{
            font-weight: bold;
            color: #333;
            margin-bottom: 5px;
        }}
        .channel-count {{
            color: #FF0000;
            font-size: 1.5em;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>📊 Анализ истории YouTube</h1>
        
        <div class="stats-grid">
            <div class="stat-card">
                <div class="stat-number">{stats['total_videos']:,}</div>
                <div class="stat-label">Всего видео</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{stats['total_days']:,}</div>
                <div class="stat-label">Дней активности</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{stats['avg_videos_per_day']:.1f}</div>
                <div class="stat-label">Среднее видео в день</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{stats['unique_channels']:,}</div>
                <div class="stat-label">Уникальных каналов</div>
            </div>
        </div>
        
        <div class="section">
            <h2>📈 Активность по месяцам</h2>
            <div class="chart-container">
                <iframe src="monthly_activity.html"></iframe>
            </div>
        </div>
        
        <div class="section">
            <h2>📅 Активность по дням недели</h2>
            <div class="chart-container">
                <iframe src="day_of_week.html"></iframe>
            </div>
        </div>
        
        <div class="section">
            <h2>🕐 Активность по часам суток</h2>
            <div class="chart-container">
                <iframe src="hourly_activity.html"></iframe>
            </div>
        </div>
        
        <div class="section">
            <h2>🏆 Топ каналов</h2>
            <div class="top-channels">
"""
        
        # Добавляем топ каналы
        for channel, count in stats['top_channels'][:10]:
            html_content += f"""
                <div class="channel-card">
                    <div class="channel-name">{channel}</div>
                    <div class="channel-count">{count}</div>
                </div>
"""
        
        html_content += """
            </div>
        </div>
        
        <div class="section">
            <h2>⏰ Статистика по длительности видео</h2>
"""
        
        # Добавляем статистику по длительности, если есть данные
        if hasattr(self, 'video_durations') and self.video_durations:
            watch_stats = self.calculate_total_watch_time()
            
            html_content += f"""
            <div class="stats-grid">
                <div class="stat-card">
                    <div class="stat-number">{len(self.video_durations):,}</div>
                    <div class="stat-label">Видео с известной длительностью</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number">{watch_stats['total_videos'] - len(self.video_durations):,}</div>
                    <div class="stat-label">Видео без данных о длительности</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number">{watch_stats['coverage_percent']:.1f}%</div>
                    <div class="stat-label">Покрытие данных</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number">{watch_stats['avg_duration_formatted']}</div>
                    <div class="stat-label">Средняя длительность</div>
                </div>
            </div>
            
            <div class="section">
                <h3>📊 Время просмотра</h3>
                <div class="stats-grid">
                    <div class="stat-card">
                        <div class="stat-number">{watch_stats['total_duration_formatted']}</div>
                        <div class="stat-label">Общее время (известные видео)</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-number">{watch_stats['estimated_total_time_formatted']}</div>
                        <div class="stat-label">Оценка общего времени</div>
                    </div>
                </div>
                
                </div>
            </div>
"""
        else:
            html_content += """
            <p><em>Данные о длительности видео не были получены. Используйте функцию "Получить длительность видео" для анализа времени просмотра.</em></p>
"""
        
        html_content += """
        </div>
        
        <div class="section">
            <h2>📊 Дополнительная статистика</h2>
            <p><strong>Период анализа:</strong> {stats['date_range']}</p>
            <p><strong>Источники данных:</strong></p>
            <ul>
"""
        
        # Добавляем статистику по источникам
        for source, count in stats['source_stats'].items():
            html_content += f"                <li>{source}: {count:,} записей</li>\n"
        
        html_content += """
            </ul>
        </div>
    </div>
</body>
</html>
"""
        
        # Заменяем плейсхолдеры
        html_content = html_content.replace("{stats['date_range']}", f"{stats['start_date']} - {stats['end_date']}")
        
        # Сохраняем отчет
        with open(self.output_dir / "report.html", 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        self.console.print(f"[green]✓ HTML отчет сохранен: {self.output_dir / 'report.html'}[/green]")
    
    def export_to_csv(self) -> None:
        """Экспорт данных в CSV файл"""
        if self.df is None or len(self.df) == 0:
            self.console.print("[red]Нет данных для экспорта![/red]")
            return
        
        self.console.print("[bold blue]Экспортирую данные в CSV...[/bold blue]")
        
        # Создаем копию DataFrame для экспорта
        export_df = self.df.copy()
        
        # Добавляем дополнительные колонки для удобства
        export_df['date_formatted'] = export_df['timestamp'].dt.strftime('%Y-%m-%d')
        export_df['time_formatted'] = export_df['timestamp'].dt.strftime('%H:%M:%S')
        export_df['year_month'] = export_df['timestamp'].dt.strftime('%Y-%m')
        export_df['day_of_week_ru'] = export_df['day_of_week'].map({
            'Monday': 'Понедельник',
            'Tuesday': 'Вторник', 
            'Wednesday': 'Среда',
            'Thursday': 'Четверг',
            'Friday': 'Пятница',
            'Saturday': 'Суббота',
            'Sunday': 'Воскресенье'
        })
        
        # Переименовываем колонки для лучшей читаемости
        export_df = export_df.rename(columns={
            'video_id': 'ID_видео',
            'title': 'Название_видео',
            'url': 'Ссылка_на_видео',
            'channel': 'Канал',
            'source': 'Источник_данных',
            'timestamp': 'Дата_время_UTC',
            'date': 'Дата',
            'hour': 'Час',
            'day_of_week': 'День_недели_EN',
            'month': 'Месяц',
            'year': 'Год',
            'date_formatted': 'Дата_формат',
            'time_formatted': 'Время_формат',
            'year_month': 'Год_месяц',
            'day_of_week_ru': 'День_недели_РУ'
        })
        
        # Добавляем информацию о длительности, если есть
        if hasattr(self, 'video_durations') and self.video_durations:
            export_df['duration_seconds'] = export_df['ID_видео'].map(self.video_durations)
            export_df['duration_formatted'] = export_df['duration_seconds'].apply(
                lambda x: self.format_duration(x) if pd.notna(x) else 'Неизвестно'
            )
            export_df['duration_minutes'] = export_df['duration_seconds'].apply(
                lambda x: round(x / 60, 1) if pd.notna(x) else None
            )
        
        # Выбираем и переупорядочиваем колонки для экспорта
        columns_order = [
            'ID_видео',
            'Название_видео', 
            'Канал',
            'Ссылка_на_видео',
            'Дата_формат',
            'Время_формат',
            'Год_месяц',
            'День_недели_РУ',
            'Час',
            'Источник_данных',
            'Дата_время_UTC'
        ]
        
        # Добавляем колонки длительности, если есть
        if hasattr(self, 'video_durations') and self.video_durations:
            columns_order.extend(['duration_seconds', 'duration_formatted', 'duration_minutes'])
        
        # Добавляем колонки, которые могут отсутствовать
        available_columns = [col for col in columns_order if col in export_df.columns]
        export_df = export_df[available_columns]
        
        # Сохраняем основной CSV
        csv_path = self.output_dir / "youtube_history_export.csv"
        export_df.to_csv(csv_path, index=False, encoding='utf-8-sig')
        
        # Создаем сводную статистику
        summary_stats = {
            'Общая_статистика': {
                'Всего_записей': len(export_df),
                'Период_начала': export_df['Дата_формат'].min(),
                'Период_окончания': export_df['Дата_формат'].max(),
                'Количество_дней': (export_df['Дата_время_UTC'].max() - export_df['Дата_время_UTC'].min()).days if len(export_df) > 0 else 0
            },
            'Статистика_по_источникам': export_df['Источник_данных'].value_counts().to_dict(),
            'Топ_10_каналов': export_df['Канал'].value_counts().head(10).to_dict(),
            'Статистика_по_дням_недели': export_df['День_недели_РУ'].value_counts().to_dict(),
            'Статистика_по_часам': export_df['Час'].value_counts().sort_index().to_dict()
        }
        
        # Сохраняем сводную статистику
        import json
        summary_path = self.output_dir / "youtube_history_summary.json"
        with open(summary_path, 'w', encoding='utf-8') as f:
            json.dump(summary_stats, f, ensure_ascii=False, indent=2, default=str)
        
        # Создаем README для CSV
        readme_content = f"""# Экспорт истории YouTube

## Файлы экспорта:

### 1. youtube_history_export.csv
Основной файл с данными истории просмотров YouTube.

**Колонки:**
- ID_видео - уникальный идентификатор видео
- Название_видео - название просмотренного видео
- Канал - название канала (Unknown = удаленный/приватный канал)
- Ссылка_на_видео - прямая ссылка на видео
- Дата_формат - дата в формате YYYY-MM-DD
- Время_формат - время в формате HH:MM:SS
- Год_месяц - год и месяц в формате YYYY-MM
- День_недели_РУ - день недели на русском языке
- Час - час просмотра (0-23)
- Источник_данных - откуда получены данные (watch_history/my_activity)
- Дата_время_UTC - полная дата и время в UTC

### 2. youtube_history_summary.json
Сводная статистика по всем данным.

### 3. report.html
HTML отчет с графиками и визуализацией.

## Общая информация:
- Всего записей: {len(export_df)}
- Период: {export_df['Дата_формат'].min()} - {export_df['Дата_формат'].max()}
- YouTube Music: полностью исключен
- My Activity: только "Watched" записи (без лайков, дизлайков, поиска)
- Дубли: удалены автоматически

## Примечания:
- Каналы "Unknown" - это удаленные или приватные каналы
- Время указано в UTC
- Данные объединены из двух источников: история просмотров + My Activity
"""
        
        readme_path = self.output_dir / "README_export.md"
        with open(readme_path, 'w', encoding='utf-8') as f:
            f.write(readme_content)
        
        self.console.print(f"[green]✓ CSV экспорт сохранен: {csv_path}[/green]")
        self.console.print(f"[green]✓ Сводная статистика: {summary_path}[/green]")
        self.console.print(f"[green]✓ README файл: {readme_path}[/green]")
        self.console.print(f"[blue]Размер CSV файла: {csv_path.stat().st_size / 1024 / 1024:.1f} MB[/blue]")
        
        # Показываем краткую статистику
        self.console.print(f"\n[bold yellow]Краткая статистика экспорта:[/bold yellow]")
        self.console.print(f"📊 Всего записей: {len(export_df):,}")
        self.console.print(f"📅 Период: {export_df['Дата_формат'].min()} - {export_df['Дата_формат'].max()}")
        self.console.print(f"🎯 Уникальных каналов: {export_df['Канал'].nunique()}")
        self.console.print(f"📁 Файл готов для импорта в Excel/Google Sheets")
    
    def generate_statistics(self) -> Dict[str, Any]:
        """Генерация статистики"""
        if self.df is None or len(self.df) == 0:
            return {}
        
        # Основная статистика
        total_videos = len(self.df)
        date_range = self.df['timestamp'].max() - self.df['timestamp'].min()
        total_days = date_range.days
        avg_videos_per_day = total_videos / total_days if total_days > 0 else 0
        unique_channels = self.df['channel'].nunique()
        
        # Топ каналов
        top_channels = self.df['channel'].value_counts().head(10).items()
        
        # Статистика по источникам
        source_stats = {}
        if 'source' in self.df.columns:
            source_stats = self.df['source'].value_counts().to_dict()
        
        # Временные диапазоны
        start_date = self.df['timestamp'].min().strftime('%Y-%m-%d')
        end_date = self.df['timestamp'].max().strftime('%Y-%m-%d')
        
        return {
            'total_videos': total_videos,
            'total_days': total_days,
            'avg_videos_per_day': avg_videos_per_day,
            'unique_channels': unique_channels,
            'top_channels': list(top_channels),
            'source_stats': source_stats,
            'start_date': start_date,
            'end_date': end_date
        }
    
    def show_tui(self) -> None:
        """Показ TUI интерфейса"""
        while True:
            self.console.clear()
            
            # Заголовок
            self.console.print("╭───────────────────────────────────────╮")
            self.console.print("│ YouTube History Analyzer              │")
            self.console.print("│ Анализатор истории просмотров YouTube │")
            self.console.print("╰───────────────────────────────────────╯")
            
            # Показываем статистику, если есть данные
            if self.df is not None and len(self.df) > 0:
                stats = self.generate_statistics()
                
                # Основная статистика
                self.console.print("\n      📊 Основная статистика       ")
                table = Table(show_header=False, box=None)
                table.add_column("Параметр", style="cyan")
                table.add_column("Значение", style="green")
                
                table.add_row("Всего видео", f"{stats['total_videos']:,}")
                table.add_row("Дней активности", f"{stats['total_days']:,}")
                table.add_row("Среднее видео в день", f"{stats['avg_videos_per_day']:.1f}")
                
                self.console.print(table)
                
                # Топ каналов
                self.console.print("\n      🏆 Топ каналов      ")
                table = Table(show_header=False, box=None)
                table.add_column("Канал", style="cyan")
                table.add_column("Видео", style="green")
                
                for channel, count in stats['top_channels'][:5]:
                    table.add_row(channel, str(count))
                
                self.console.print(table)
            
            # Меню действий
            self.console.print("\n[bold yellow]Доступные действия:[/bold yellow]")
            self.console.print("1. Загрузить данные из Takeout")
            self.console.print("2. Получить длительность видео")
            self.console.print("3. Сгенерировать HTML отчет")
            self.console.print("4. Экспорт данных в CSV")
            self.console.print("5. Открыть отчет в браузере")
            self.console.print("0. Выход")
            
            choice = input("\nВыберите действие (0-5): ").strip()
            
            if choice == "0":
                self.console.print("[yellow]До свидания![/yellow]")
                break
            elif choice == "1":
                self.load_takeout_data_menu()
            elif choice == "2":
                if self.df is not None:
                    sample_size = input("Размер выборки для анализа длительности (по умолчанию 100): ").strip()
                    sample_size = int(sample_size) if sample_size.isdigit() else 100
                    self.get_durations(sample_size)
                else:
                    self.console.print("[red]Сначала загрузите данные![/red]")
            elif choice == "3":
                if self.df is not None:
                    stats = self.generate_statistics()
                    self.generate_html_report(stats)
                else:
                    self.console.print("[red]Сначала загрузите данные![/red]")
            elif choice == "4":
                if self.df is not None:
                    self.export_to_csv()
                else:
                    self.console.print("[red]Сначала загрузите данные![/red]")
            elif choice == "5":
                report_path = self.output_dir / "report.html"
                if report_path.exists():
                    import webbrowser
                    webbrowser.open(f"file://{report_path.absolute()}")
                else:
                    self.console.print("[red]Отчет еще не создан![/red]")
            else:
                self.console.print("[red]Неверный выбор![/red]")
            
            input("\nНажмите Enter для продолжения...")
            self.console.clear()
    
    def load_takeout_data_menu(self) -> None:
        """Меню загрузки данных из Takeout"""
        self.console.print("\n[bold blue]Загрузка данных из Takeout[/bold blue]")
        
        # Автоматический поиск файлов
        history_file = Path("Takeout/YouTube and YouTube Music/history/watch-history.json")
        activity_file = Path("Takeout/My Activity/YouTube/MyActivity.json")
        
        loaded_any = False
        
        if history_file.exists():
            self.console.print(f"[green]Найден файл истории: {history_file}[/green]")
            if Confirm.ask("Загрузить файл истории просмотров?"):
                if self.load_data_source(str(history_file), 'watch_history'):
                    loaded_any = True
        
        if activity_file.exists():
            self.console.print(f"[green]Найден файл My Activity: {activity_file}[/green]")
            if Confirm.ask("Загрузить файл My Activity?"):
                if self.load_data_source(str(activity_file), 'my_activity'):
                    loaded_any = True
        
        if loaded_any:
            self.process_data()
        else:
            self.console.print("[red]Не удалось загрузить ни один файл![/red]")

def main():
    """Главная функция"""
    analyzer = YouTubeAnalyzer()
    
    try:
        analyzer.show_tui()
    except KeyboardInterrupt:
        analyzer.console.print("\n[yellow]Программа прервана пользователем[/yellow]")
    except Exception as e:
        analyzer.console.print(f"\n[red]Ошибка: {e}[/red]")

if __name__ == "__main__":
    main()
