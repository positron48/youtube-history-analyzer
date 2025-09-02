#!/usr/bin/env python3
"""
YouTube History Analyzer
YouTube History Analyzer with TUI interface
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
import requests
import time
import random
from locales import get_text, get_csv_columns, get_day_of_week, get_month_name
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
        self.language = 'ru'  # По умолчанию русский
        
        # Новые переменные для отслеживания среднего значения
        self.average_progression = []  # Список кортежей (количество_видео, среднее_значение)
        self.average_data = []  # Список словарей с детальной информацией о каждом видео
    
    def select_language(self) -> None:
        """Выбор языка интерфейса"""
        self.console.print(f"\n[bold blue]{get_text('en', 'welcome')}[/bold blue]")
        self.console.print(f"\n[bold]{get_text('en', 'select_language')}[/bold]")
        self.console.print(f"1. {get_text('en', 'language_ru')}")
        self.console.print(f"2. {get_text('en', 'language_en')}")
        
        while True:
            choice = input("\nВыберите язык / Select language (1-2): ").strip()
            if choice == '1':
                self.language = 'ru'
                self.console.print(f"\n[green]{get_text(self.language, 'language_selected_ru')}[/green]")
                break
            elif choice == '2':
                self.language = 'en'
                self.console.print(f"\n[green]✓ English language selected[/green]")
                break
            else:
                self.console.print(f"[red]{get_text('en', 'invalid_choice')}[/red]")
        
        # Показываем приветствие на выбранном языке
        self.console.print(f"\n[bold blue]{get_text(self.language, 'welcome')}[/bold blue]\n")

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
                self.console.print(f"✓ {get_text(self.language, 'loaded_records', count=len(data), source=source_type)}")
                return True
            else:
                self.console.print(f"[red]{get_text(self.language, 'error_file_not_list', source=source_type)}[/red]")
                return False
                
        except json.JSONDecodeError as e:
            self.console.print(f"[red]{get_text(self.language, 'error_loading_file', error=e)}[/red]")
            return False
        except Exception as e:
            self.console.print(f"[red]{get_text(self.language, 'error_loading_source', source=source_type, error=e)}[/red]")
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
        self.console.print(f"[bold blue]{get_text(self.language, 'merging_sources')}[/bold blue]")
        
        unique_records = {}
        duplicates_count = 0
        total_items = sum(len(data) for data in self.data_sources.values() if data)
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=self.console
        ) as progress:
            task = progress.add_task(get_text(self.language, 'deduplication'), total=total_items)
            
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
            self.console.print(f"[green]✓ {get_text(self.language, 'merged_unique', count=len(self.data))}[/green]")
            self.console.print(f"[yellow]{get_text(self.language, 'found_duplicates', count=duplicates_count)}[/yellow]")
    
    def process_data(self) -> None:
        """Обработка данных истории"""
        self.console.print(f"[bold blue]{get_text(self.language, 'processing_data')}[/bold blue]")
        
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
            task = progress.add_task(get_text(self.language, 'processing_records'), total=len(self.data))
            
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
        
        self.console.print(f"[green]✓ {get_text(self.language, 'processed_records', count=len(self.df))}[/green]")
    
    def get_durations(self, sample_size: int = 100) -> None:
        """Получение длительности видео для выборки"""
        if self.df is None or len(self.df) == 0:
            self.console.print(f"[red]{get_text(self.language, 'no_data_loaded')}[/red]")
            return
        
        self.console.print(f"[bold blue]{get_text(self.language, 'getting_durations', count=sample_size)}[/bold blue]")
        
        # Фильтруем видео с доступными каналами (не Unknown)
        available_videos = self.df[self.df['channel'] != 'Unknown'].copy()
        
        if len(available_videos) == 0:
            self.console.print(f"[red]{get_text(self.language, 'no_available_videos')}[/red]")
            return
        
        # Берем случайную выборку из доступных видео
        sample_size = min(sample_size, len(available_videos))
        sample = available_videos.sample(sample_size)
        
        self.console.print(f"[blue]{get_text(self.language, 'selected_videos', count=len(sample))}[/blue]")
        self.console.print(f"[blue]{get_text(self.language, 'total_available', count=len(available_videos))}[/blue]")
        
        # Получаем длительность через API
        self.get_durations_api(sample)
    
    def get_durations_ytdlp(self, sample_df) -> None:
        """Получение длительности через yt-dlp"""
        try:
            import yt_dlp
            
            self.console.print(f"[blue]{get_text(self.language, 'yt_dlp_usage')}[/blue]")
            
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
                self.console.print(f"[green]{get_text(self.language, 'cookies_used')}[/green]")
                self.console.print(f"[blue]{get_text(self.language, 'temp_cookies_created')}[/blue]")
            else:
                self.console.print(f"[yellow]{get_text(self.language, 'cookies_file_not_found')}[/yellow]")
                self.console.print(f"[yellow]{get_text(self.language, 'cookies_instructions')}[/yellow]")
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
                    task = progress.add_task(get_text(self.language, 'getting_duration'), total=total)
                    
                    for _, row in sample_df.iterrows():
                        video_id = row['video_id']
                        video_url = row['url']
                        
                        try:
                            # Получаем информацию о видео
                            self.console.print(f"\n[blue]{get_text(self.language, 'getting_info_for', title=row['title'][:50])}[/blue]")
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
                                progress.update(task, description=get_text(self.language, 'duration_not_found', title=row['title'][:30]))
                            
                            processed += 1
                            
                        except Exception as e:
                            progress.update(task, description=get_text(self.language, 'duration_error', title=row['title'][:30], error=str(e)[:20]))
                            self.console.print(f"[red]❌ {get_text(self.language, 'error')}: {str(e)}[/red]")
                            processed += 1
                        
                        progress.advance(task)
                        
                        # Небольшая задержка чтобы не перегружать YouTube
                        import time
                        time.sleep(1)
                
                self.console.print(f"\n[green]{get_text(self.language, 'duration_obtained', obtained=len(self.video_durations), total=total)}[/green]")
                
                # Очищаем временный файл cookies
                temp_cookies = Path("temp_cookies.txt")
                if temp_cookies.exists():
                    temp_cookies.unlink()
                    self.console.print(f"[blue]{get_text(self.language, 'temp_cookies_removed')}[/blue]")
                
                if self.video_durations:
                    self.show_duration_statistics()
                else:
                                    self.console.print(f"[yellow]{get_text(self.language, 'no_duration_videos')}[/yellow]")
                self.console.print(f"[yellow]{get_text(self.language, 'no_duration_reasons')}[/yellow]")
                self.console.print(f"[yellow]{get_text(self.language, 'google_blocking')}[/yellow]")
                self.console.print(f"[yellow]{get_text(self.language, 'wrong_cookies')}[/yellow]")
                self.console.print(f"[yellow]{get_text(self.language, 'videos_unavailable')}[/yellow]")
                self.show_cookies_instructions()
            
        except ImportError:
            self.console.print(f"[red]{get_text(self.language, 'yt_dlp_not_installed')}[/red]")
        except Exception as e:
            self.console.print(f"[red]{get_text(self.language, 'yt_dlp_error', error=e)}[/red]")
            self.console.print(f"[yellow]{get_text(self.language, 'yt_dlp_try_vpn')}[/yellow]")
        
    def show_cookies_instructions(self) -> None:
        """Показ инструкций по настройке cookies"""
        self.console.print(f"\n[bold blue]{get_text(self.language, 'cookies_setup_title')}[/bold blue]")
        self.console.print(f"{get_text(self.language, 'cookies_step1')}")
        self.console.print(f"{get_text(self.language, 'cookies_step2')}")
        self.console.print(f"{get_text(self.language, 'cookies_step3')}")
        self.console.print(f"{get_text(self.language, 'cookies_step4')}")
        self.console.print(f"{get_text(self.language, 'cookies_step5')}")
        self.console.print(f"\n[blue]{get_text(self.language, 'cookies_instructions_file')}[/blue]")
    
    def show_api_instructions(self) -> None:
        """Показывает инструкции по настройке YouTube API"""
        self.console.print(f"\n{get_text(self.language, 'api_instructions_title')}:")
        self.console.print(get_text(self.language, 'api_step_1'))
        self.console.print(get_text(self.language, 'api_step_2'))
        self.console.print(get_text(self.language, 'api_step_3'))
        self.console.print(get_text(self.language, 'api_step_4'))
        self.console.print(get_text(self.language, 'api_step_5'))
        self.console.print(f"\n[blue]{get_text(self.language, 'api_quota_info')}[/blue]")
        self.console.print(f"[yellow]{get_text(self.language, 'api_recommendation')}[/yellow]")
    
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
            self.console.print(f"[red]{get_text(self.language, 'iso_parse_error', error=e)}[/red]")
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
                self.console.print(f"[red]{get_text(self.language, 'api_key_not_found')}[/red]")
                self.console.print(f"[yellow]{get_text(self.language, 'api_key_instructions')}[/yellow]")
                self.show_api_instructions()
                return
            
            with open(api_key_file, 'r') as f:
                api_key = f.read().strip()
            
            if not api_key:
                self.console.print(f"[red]{get_text(self.language, 'api_key_empty')}[/red]")
                self.show_api_instructions()
                return
            
            self.console.print(f"[green]✓ {get_text(self.language, 'using_api')}[/green]")
            self.console.print(f"[blue]📋 {get_text(self.language, 'total_videos', count=len(sample_df))}[/blue]")
            
            processed = 0
            total = len(sample_df)
            
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=self.console
            ) as progress:
                task = progress.add_task(get_text(self.language, 'getting_durations', count=total), total=total)
                
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
                                        
                                        progress.update(task, description=get_text(self.language, 'duration_progress', 
                                                                               title=row['title'][:30], 
                                                                               duration=f"{minutes}:{seconds:02d}", 
                                                                               avg_duration=f"{avg_minutes}:{avg_seconds:02d}"))
                                        
                                        # Сохраняем данные о среднем для графика сходимости (для каждого видео)
                                        self.average_progression.append((len(self.video_durations), current_avg))
                                        self.average_data.append({
                                            'video_count': len(self.video_durations),
                                            'average_duration_seconds': current_avg,
                                            'average_duration_minutes': round(current_avg / 60, 1),
                                            'average_duration_formatted': f"{avg_minutes}:{avg_seconds:02d}",
                                            'total_duration_seconds': sum(self.video_durations.values()),
                                            'current_video_duration': duration_seconds,
                                            'current_video_title': row['title'][:50]
                                        })
                                        
                                        # Показываем изменение среднего значения каждые 5 видео
                                        if len(self.video_durations) % 5 == 0:
                                            self.console.print(f"[blue]📊 {get_text(self.language, 'current_average', avg_duration=f'{avg_minutes}:{avg_seconds:02d}', count=len(self.video_durations))}[/blue]")
                                        
                                        # Показываем общее количество каждые 10 видео
                                        if len(self.video_durations) % 10 == 0:
                                            total_processed = len(self.video_durations)
                                            total_remaining = total - total_processed
                                            progress_percent = (total_processed / total) * 100
                                            self.console.print(f"[green]✅ {get_text(self.language, 'processed_count', processed=total_processed, total=total, percent=progress_percent, remaining=total_remaining)}[/green]")
                                    else:
                                        progress.update(task, description=get_text(self.language, 'parsing_error', title=row['title'][:30]))
                                else:
                                    progress.update(task, description=get_text(self.language, 'duration_not_found', title=row['title'][:30]))
                            else:
                                progress.update(task, description=get_text(self.language, 'video_unavailable', title=row['title'][:30]))
                        else:
                            error_msg = f"HTTP {response.status_code}"
                            if response.status_code == 403:
                                error_msg = get_text(self.language, 'api_key_invalid')
                            elif response.status_code == 400:
                                error_msg = get_text(self.language, 'api_request_invalid')
                            
                            progress.update(task, description=f"❌ {row['title'][:30]}... ({error_msg})")
                            
                            if response.status_code == 403:
                                self.console.print(f"[red]❌ {get_text(self.language, 'api_error')}: {error_msg}[/red]")
                                self.console.print(f"[yellow]{get_text(self.language, 'api_check_key')}[/yellow]")
                                break
                        
                        processed += 1
                        
                    except requests.exceptions.Timeout:
                        progress.update(task, description=f"❌ {row['title'][:30]}... ({get_text(self.language, 'timeout')})")
                        processed += 1
                    except requests.exceptions.RequestException as e:
                        progress.update(task, description=f"❌ {row['title'][:30]}... ({get_text(self.language, 'network_error')})")
                        processed += 1
                    except Exception as e:
                        progress.update(task, description=f"❌ {row['title'][:30]}... ({get_text(self.language, 'error')}: {str(e)[:20]})")
                        processed += 1
                    
                    progress.advance(task)
                    
                    # Небольшая задержка между запросами (API позволяет до 10,000 запросов в день)
                    time.sleep(0.1)
                
                self.console.print(f"\n[green]✓ {get_text(self.language, 'duration_complete', processed=len(self.video_durations), total=total)}[/green]")
                
                if self.video_durations:
                    self.show_duration_statistics()
                else:
                    self.console.print(f"[yellow]{get_text(self.language, 'no_duration_videos')}[/yellow]")
                self.console.print(f"[yellow]{get_text(self.language, 'no_duration_reasons')}[/yellow]")
                self.console.print(f"[yellow]{get_text(self.language, 'wrong_cookies')}[/yellow]")
                self.console.print(f"[yellow]{get_text(self.language, 'wrong_cookies')}[/yellow]")
                self.console.print(f"[yellow]{get_text(self.language, 'videos_unavailable')}[/yellow]")
                self.show_api_instructions()
            
        except Exception as e:
            self.console.print(f"[red]{get_text(self.language, 'api_module_error', error=e)}[/red]")
            self.console.print(f"[yellow]{get_text(self.language, 'api_install_requests')}[/yellow]")
    
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
                    found_patterns.append(f"{get_text(self.language, 'pattern_found', num=i+1, pattern=pattern, matches=matches[:3])}")  # Показываем первые 3 совпадения
            
            if found_patterns:
                self.console.print(f"[blue]{get_text(self.language, 'patterns_found', patterns=found_patterns[:2])}[/blue]")  # Показываем первые 2
            
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
                            self.console.print(f"[green]{get_text(self.language, 'duration_hours_minutes', hours=hours, minutes=minutes, seconds=seconds, result=result)}[/green]")
                            return result
                        elif 'M' in pattern and 'S' in pattern:  # Формат с минутами и секундами
                            minutes = int(match.group(1))
                            seconds = int(match.group(2))
                            result = minutes * 60 + seconds
                            self.console.print(f"[green]{get_text(self.language, 'duration_minutes_seconds', minutes=minutes, seconds=seconds, result=result)}[/green]")
                            return result
                        else:  # Простой формат в секундах
                            result = int(match.group(1))
                            self.console.print(f"[green]{get_text(self.language, 'duration_seconds', result=result)}[/green]")
                            return result
                    except (ValueError, IndexError) as e:
                        self.console.print(f"[yellow]{get_text(self.language, 'pattern_parse_error', pattern=pattern, error=e)}[/yellow]")
                        continue
            
            # Если не нашли, возвращаем 0
            self.console.print(f"[red]{get_text(self.language, 'duration_no_patterns')}[/red]")
            return 0
            
        except Exception as e:
            self.console.print(f"[red]{get_text(self.language, 'extract_html_error', error=e)}[/red]")
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
            
            self.console.print(f"[blue]{get_text(self.language, 'selenium_usage')}[/blue]")
            self.console.print(f"[yellow]{get_text(self.language, 'selenium_slower')}[/yellow]")
            
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
                self.console.print(f"[green]{get_text(self.language, 'cookies_found')}[/green]")
            
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
                    self.console.print(f"[green]{get_text(self.language, 'cookies_loaded')}[/green]")
                
                processed = 0
                total = len(sample_df)
                
                with Progress(
                    SpinnerColumn(),
                    TextColumn("[progress.description]{task.description}"),
                    console=self.console
                ) as progress:
                    task = progress.add_task(get_text(self.language, 'getting_duration_browser'), total=total)
                    
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
                                    progress.update(task, description=get_text(self.language, 'duration_not_found', title=row['title'][:30]))
                                
                            except:
                                progress.update(task, description=get_text(self.language, 'duration_not_found', title=row['title'][:30]))
                            
                            processed += 1
                            
                        except Exception as e:
                            progress.update(task, description=get_text(self.language, 'duration_error', title=row['title'][:30], error=str(e)[:20]))
                            processed += 1
                        
                        progress.advance(task)
                        
                        # Задержка между запросами
                        import time
                        time.sleep(1)
                
                driver.quit()
                
                self.console.print(f"\n[green]{get_text(self.language, 'duration_obtained', obtained=len(self.video_durations), total=total)}[/green]")
                
                if self.video_durations:
                    self.show_duration_statistics()
                
            except Exception as e:
                            self.console.print(f"[red]{get_text(self.language, 'browser_error', error=e)}[/red]")
            self.console.print(f"[yellow]{get_text(self.language, 'browser_install_chrome')}[/yellow]")
                
        except ImportError:
            self.console.print(f"[red]{get_text(self.language, 'selenium_not_installed')}[/red]")
        except Exception as e:
            self.console.print(f"[red]{get_text(self.language, 'selenium_error', error=e)}[/red]")
    
    def get_durations_manual(self, sample_df) -> None:
        """Ручной ввод длительности для тестирования"""
        self.console.print(f"[blue]{get_text(self.language, 'manual_mode')}[/blue]")
        self.console.print(f"[yellow]{get_text(self.language, 'manual_duration_format')}[/yellow]")
        
        processed = 0
        total = min(5, len(sample_df))  # Ограничиваем для тестирования
        
        for i, (_, row) in enumerate(sample_df.head(total).iterrows()):
            self.console.print(f"\n[{i+1}/{total}] {row['title'][:50]}...")
            self.console.print(f"URL: {row['url']}")
            
            duration_input = input(get_text(self.language, 'manual_duration_input')).strip()
            
            if duration_input:
                try:
                    duration = self.parse_duration(duration_input)
                    if duration > 0:
                        self.video_durations[row['video_id']] = duration
                        self.console.print(f"[green]{get_text(self.language, 'manual_duration_success', input=duration_input, duration=duration)}[/green]")
                        processed += 1
                    else:
                        self.console.print(f"[red]{get_text(self.language, 'manual_duration_invalid')}[/red]")
                except:
                    self.console.print(f"[red]{get_text(self.language, 'manual_duration_invalid')}[/red]")
            else:
                self.console.print(f"[yellow]{get_text(self.language, 'manual_duration_skipped')}[/yellow]")
        
        self.console.print(f"\n[green]{get_text(self.language, 'manual_processed', processed=processed)}[/green]")
        
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
        
        self.console.print(f"\n[bold blue]{get_text(self.language, 'duration_stats_title')}[/bold blue]")
        
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
        table = Table(title=get_text(self.language, 'duration_stats_title'))
        table.add_column(get_text(self.language, 'parameter'), style="cyan")
        table.add_column(get_text(self.language, 'value'), style="green")
        
        table.add_row(get_text(self.language, 'total_videos_with_duration'), str(len(durations)))
        table.add_row(get_text(self.language, 'total_watch_time'), get_text(self.language, 'time_format_hours', hours=total_hours, minutes=total_minutes, seconds=total_seconds))
        table.add_row(get_text(self.language, 'average_duration'), get_text(self.language, 'time_format_minutes', minutes=avg_minutes, seconds=avg_seconds))
        table.add_row(get_text(self.language, 'shortest_video'), get_text(self.language, 'time_format_minutes', minutes=min(durations) // 60, seconds=min(durations) % 60))
        table.add_row(get_text(self.language, 'longest_video'), get_text(self.language, 'time_format_minutes', minutes=max(durations) // 60, seconds=max(durations) % 60))
        
        self.console.print(table)
        
        # Показываем распределение по длительности
        self.console.print(f"\n[bold blue]{get_text(self.language, 'duration_distribution')}[/bold blue]")
        
        # Группируем по диапазонам
        ranges = {
            get_text(self.language, 'duration_range_0_5', count=0, percent=0.0): 0,
            get_text(self.language, 'duration_range_5_15', count=0, percent=0.0): 0,
            get_text(self.language, 'duration_range_15_30', count=0, percent=0.0): 0,
            get_text(self.language, 'duration_range_30_60', count=0, percent=0.0): 0,
            get_text(self.language, 'duration_range_60_plus', count=0, percent=0.0): 0
        }
        
        for duration in durations:
            minutes = duration // 60
            if minutes < 5:
                ranges[get_text(self.language, 'duration_range_0_5', count=0, percent=0.0)] += 1
            elif minutes < 15:
                ranges[get_text(self.language, 'duration_range_5_15', count=0, percent=0.0)] += 1
            elif minutes < 30:
                ranges[get_text(self.language, 'duration_range_15_30', count=0, percent=0.0)] += 1
            elif minutes < 60:
                ranges[get_text(self.language, 'duration_range_30_60', count=0, percent=0.0)] += 1
            else:
                ranges[get_text(self.language, 'duration_range_60_plus', count=0, percent=0.0)] += 1
        
        for range_name, count in ranges.items():
            percentage = (count / len(durations)) * 100
            if "0-5" in range_name:
                self.console.print(f"  {get_text(self.language, 'duration_range_0_5', count=count, percent=percentage)}")
            elif "5-15" in range_name:
                self.console.print(f"  {get_text(self.language, 'duration_range_5_15', count=count, percent=percentage)}")
            elif "15-30" in range_name:
                self.console.print(f"  {get_text(self.language, 'duration_range_15_30', count=count, percent=percentage)}")
            elif "30-60" in range_name:
                self.console.print(f"  {get_text(self.language, 'duration_range_30_60', count=count, percent=percentage)}")
            else:
                self.console.print(f"  {get_text(self.language, 'duration_range_60_plus', count=count, percent=percentage)}")
        
        # Сохраняем длительности в CSV для дальнейшего анализа
        if self.df is not None:
            self.save_durations_to_csv()
        
        # Сохраняем данные о среднем для графика сходимости
        if self.average_data:
            self.save_average_progression_data()
            self.console.print(f"\n[blue]{get_text(self.language, 'average_convergence_chart', path='average_convergence.html')}[/blue]")
            self.console.print(f"[blue]{get_text(self.language, 'average_progression_data', csv='average_progression.csv', json='.json')}[/blue]")
        
        # Показываем общую статистику времени просмотра
        self.show_total_watch_time_summary()
    
    def show_total_watch_time_summary(self) -> None:
        """Показывает сводку по общему времени просмотра"""
        if not self.video_durations:
            self.console.print(f"[yellow]{get_text(self.language, 'no_data_for_watch_time')}[/yellow]")
            return
        
        watch_stats = self.calculate_total_watch_time()
        
        self.console.print(f"\n[bold blue]{get_text(self.language, 'watch_time_summary')}[/bold blue]")
        
        # Создаем таблицу сводки
        summary_table = Table(title=get_text(self.language, 'watch_time_summary'))
        summary_table.add_column(get_text(self.language, 'parameter'), style="cyan")
        summary_table.add_column(get_text(self.language, 'value'), style="green")
        
        summary_table.add_row(get_text(self.language, 'total_videos_in_history'), str(watch_stats['total_videos']))
        summary_table.add_row(get_text(self.language, 'total_videos_in_history'), str(len(self.video_durations)))
        summary_table.add_row(get_text(self.language, 'videos_without_duration'), str(watch_stats['total_videos'] - len(self.video_durations)))
        summary_table.add_row(get_text(self.language, 'total_time_known'), watch_stats['total_duration_formatted'])
        summary_table.add_row(get_text(self.language, 'average_duration_videos'), watch_stats['avg_duration_formatted'])
        summary_table.add_row(get_text(self.language, 'estimated_total_time'), watch_stats['estimated_total_time_formatted'])
        
        self.console.print(summary_table)
        
        # Дополнительная информация
        if watch_stats['total_videos'] > len(self.video_durations):
            coverage_percent = (len(self.video_durations) / watch_stats['total_videos']) * 100
            self.console.print(f"\n[blue]📊 {get_text(self.language, 'data_coverage', percent=coverage_percent)}[/blue]")
            self.console.print(f"[yellow]⚠️ {get_text(self.language, 'duration_unknown_warning', count=watch_stats['total_videos'] - len(self.video_durations))}[/yellow]")
            self.console.print(f"[yellow]   {get_text(self.language, 'estimated_time_note')}[/yellow]")
    
    def calculate_total_watch_time(self) -> dict:
        """Вычисляет общее время просмотра за исследуемый период"""
        if not self.video_durations or self.df is None:
            return {
                'total_videos': 0,
                'total_duration': 0,
                'total_duration_formatted': f'0 {get_text(self.language, "hours_minutes")}',
                'avg_duration': 0,
                'avg_duration_formatted': f'0 {get_text(self.language, "minutes")}',
                'estimated_total_time': 0,
                'estimated_total_time_formatted': f'0 {get_text(self.language, "hours_minutes")}'
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
            return f"{int(seconds)} {get_text(self.language, 'seconds')}"
        elif seconds < 3600:
            minutes = int(seconds // 60)
            remaining_seconds = int(seconds % 60)
            if remaining_seconds == 0:
                return f"{minutes} {get_text(self.language, 'minutes')}"
            else:
                return f"{minutes} {get_text(self.language, 'minutes')} {remaining_seconds} {get_text(self.language, 'seconds')}"
        else:
            hours = int(seconds // 3600)
            remaining_minutes = int((seconds % 3600) // 60)
            remaining_seconds = int(seconds % 60)
            if remaining_minutes == 0 and remaining_seconds == 0:
                return f"{hours} {get_text(self.language, 'hours')}"
            elif remaining_seconds == 0:
                return f"{hours} {get_text(self.language, 'hours')} {remaining_minutes} {get_text(self.language, 'minutes')}"
            else:
                return f"{hours} {get_text(self.language, 'hours')} {remaining_minutes} {get_text(self.language, 'minutes')} {remaining_seconds} {get_text(self.language, 'seconds')}"
    
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
            
            self.console.print(f"\n[green]✓ {get_text(self.language, 'duration_saved', path=csv_path)}[/green]")
            self.console.print(f"[blue]{get_text(self.language, 'file_size', size=f'{csv_path.stat().st_size / 1024:.1f} KB')}[/blue]")
    
    def save_average_progression_data(self) -> None:
        """Сохранение данных о прогрессии среднего значения длительности видео (для каждого видео)"""
        if not self.average_data:
            return
        
        # Сохраняем в JSON для удобства анализа
        json_path = self.output_dir / "average_progression.json"
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(self.average_data, f, ensure_ascii=False, indent=2)
        
        # Сохраняем в CSV для удобства работы с данными
        csv_path = self.output_dir / "average_progression.csv"
        df = pd.DataFrame(self.average_data)
        df.to_csv(csv_path, index=False, encoding='utf-8-sig')
        
        self.console.print(f"\n[green]{get_text(self.language, 'average_progression_saved')}[/green]")
        self.console.print(f"[blue]{get_text(self.language, 'average_progression_json', path=json_path)}[/blue]")
        self.console.print(f"[blue]{get_text(self.language, 'average_progression_csv', path=csv_path)}[/blue]")
        self.console.print(f"[blue]{get_text(self.language, 'average_progression_size', size=f'{csv_path.stat().st_size / 1024:.1f} KB')}[/blue]")
    
    def create_plots(self) -> None:
        """Создание графиков"""
        if self.df is None or len(self.df) == 0:
            self.console.print(f"[red]{get_text(self.language, 'no_data_for_plots')}[/red]")
            return
        
        self.console.print(f"[bold blue]{get_text(self.language, 'creating_plots')}[/bold blue]")
        
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
            title=get_text(self.language, 'monthly_activity'),
            xaxis_title=get_text(self.language, 'month'),
            yaxis_title=get_text(self.language, 'video_count'),
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
                    title=get_text(self.language, 'cumulative_time'),
                    xaxis_title=get_text(self.language, 'date'),
                    yaxis_title=get_text(self.language, 'time_seconds'),
                    template='plotly_white'
                )
            else:
                fig2 = None
        else:
            fig2 = None
        
        # График 3: Активность по дням недели
        # Создаем маппинг английских названий на локализованные
        day_mapping = {
            'Monday': get_text(self.language, 'monday'),
            'Tuesday': get_text(self.language, 'tuesday'),
            'Wednesday': get_text(self.language, 'wednesday'),
            'Thursday': get_text(self.language, 'thursday'),
            'Friday': get_text(self.language, 'friday'),
            'Saturday': get_text(self.language, 'saturday'),
            'Sunday': get_text(self.language, 'sunday')
        }
        
        # Создаем временную колонку с локализованными названиями для группировки
        temp_df = self.df.copy()
        temp_df['day_of_week_local'] = temp_df['day_of_week'].map(day_mapping)
        
        day_stats = temp_df.groupby('day_of_week_local').size()
        
        # Создаем локализованный порядок дней недели
        day_order = [
            get_text(self.language, 'monday'),
            get_text(self.language, 'tuesday'),
            get_text(self.language, 'wednesday'),
            get_text(self.language, 'thursday'),
            get_text(self.language, 'friday'),
            get_text(self.language, 'saturday'),
            get_text(self.language, 'sunday')
        ]
        day_stats = day_stats.reindex(day_order)
        
        fig3 = go.Figure(data=[
            go.Bar(
                x=day_stats.index,
                y=day_stats.values,
                marker_color='#FF6B6B'
            )
        ])
        fig3.update_layout(
            title=get_text(self.language, 'day_of_week_activity'),
            xaxis_title=get_text(self.language, 'day_of_week'),
            yaxis_title=get_text(self.language, 'video_count'),
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
            title=get_text(self.language, 'hourly_activity'),
            xaxis_title=get_text(self.language, 'hour'),
            yaxis_title=get_text(self.language, 'video_count'),
            template='plotly_white'
        )
        
        # График 5: Сходимость среднего значения длительности (для каждого видео)
        if self.average_progression:
            # Конвертируем секунды в минуты с округлением до десятых
            video_counts = [point[0] for point in self.average_progression]
            avg_minutes = [round(point[1] / 60, 1) for point in self.average_progression]
            
            fig5 = go.Figure(data=[
                go.Scatter(
                    x=video_counts,
                    y=avg_minutes,
                    mode='lines+markers',
                    line=dict(color='#FF8C00', width=3),
                    marker=dict(size=6, color='#FF8C00'),
                    name=get_text(self.language, 'average_value')
                )
            ])
            
            # Вычисляем скользящий тренд (окно = 10% от общего количества видео, минимум 5)
            window_size = max(5, len(video_counts) // 10)
            if window_size > 1 and len(video_counts) > window_size:
                # Вычисляем скользящее среднее
                moving_averages = []
                for i in range(len(video_counts)):
                    start_idx = max(0, i - window_size + 1)
                    end_idx = i + 1
                    window_avg = sum(avg_minutes[start_idx:end_idx]) / len(avg_minutes[start_idx:end_idx])
                    moving_averages.append(round(window_avg, 1))
                
                # Добавляем линию скользящего тренда
                fig5.add_trace(
                    go.Scatter(
                        x=video_counts,
                        y=moving_averages,
                        mode='lines',
                        line=dict(color='red', width=2, dash='dash'),
                        name=get_text(self.language, 'average_convergence_trend', window=window_size)
                    )
                )
            
            # Добавляем горизонтальную линию финального среднего для сравнения
            final_avg_minutes = round(self.average_progression[-1][1] / 60, 1) if self.average_progression else 0
            if final_avg_minutes > 0:
                fig5.add_hline(
                    y=final_avg_minutes,
                    line_dash="dot",
                    line_color="gray",
                    line_width=1,
                    annotation_text=get_text(self.language, 'average_convergence_final', value=final_avg_minutes),
                    annotation_position="bottom right"
                )
            
            fig5.update_layout(
                title=get_text(self.language, 'average_convergence_title'),
                xaxis_title=get_text(self.language, 'average_convergence_xaxis'),
                yaxis_title=get_text(self.language, 'average_convergence_yaxis'),
                template='plotly_white',
                showlegend=True
            )
        else:
            fig5 = None
        
        # Сохраняем графики
        fig1.write_html(self.output_dir / "monthly_activity.html")
        if fig2:
            fig2.write_html(self.output_dir / "cumulative_time.html")
        fig3.write_html(self.output_dir / "day_of_week.html")
        fig4.write_html(self.output_dir / "hourly_activity.html")
        if fig5:
            fig5.write_html(self.output_dir / "average_convergence.html")
        
        self.console.print(f"[green]✓ {get_text(self.language, 'plots_saved')}[/green]")
    
    def generate_html_report(self, stats: Dict[str, Any]) -> None:
        """Генерация HTML отчета"""
        self.console.print(f"[bold blue]{get_text(self.language, 'generating_html')}[/bold blue]")
        
        # Автоматически создаем графики
        self.console.print(f"[blue]{get_text(self.language, 'creating_plots')}[/blue]")
        self.create_plots()
        
        html_content = f"""
<!DOCTYPE html>
<html lang="{self.language}">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>YouTube History Analysis</title>
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
        <h1>📊 {get_text(self.language, 'youtube_analysis')}</h1>
        
        <div class="stats-grid">
            <div class="stat-card">
                <div class="stat-number">{stats['total_videos']:,}</div>
                <div class="stat-label">{get_text(self.language, 'total_videos_label')}</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{stats['total_days']:,}</div>
                <div class="stat-label">{get_text(self.language, 'active_days_label')}</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{stats['avg_videos_per_day']:.1f}</div>
                <div class="stat-label">{get_text(self.language, 'avg_videos_per_day_label')}</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{stats['unique_channels']:,}</div>
                <div class="stat-label">{get_text(self.language, 'unique_channels')}</div>
            </div>
        </div>
        
        <div class="section">
            <h2>📈 {get_text(self.language, 'monthly_activity')}</h2>
            <div class="chart-container">
                <iframe src="monthly_activity.html"></iframe>
            </div>
        </div>
        
        <div class="section">
            <h2>📅 {get_text(self.language, 'day_of_week_activity')}</h2>
            <div class="chart-container">
                <iframe src="day_of_week.html"></iframe>
            </div>
        </div>
        
        <div class="section">
            <h2>🕐 {get_text(self.language, 'hourly_activity')}</h2>
            <div class="chart-container">
                <iframe src="hourly_activity.html"></iframe>
            </div>
        </div>
        
        <div class="section">
            <h2>{get_text(self.language, 'average_convergence_section')}</h2>
            <div class="chart-container">
                <iframe src="average_convergence.html"></iframe>
            </div>
        </div>
        
        <div class="section">
            <h2>🏆 {get_text(self.language, 'top_channels')}</h2>
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
        
        html_content += f"""
            </div>
        </div>
        
        <div class="section">
            <h2>⏰ {get_text(self.language, 'video_duration_statistics')}</h2>
"""
        
        # Добавляем статистику по длительности, если есть данные
        if hasattr(self, 'video_durations') and self.video_durations:
            watch_stats = self.calculate_total_watch_time()
            
            html_content += f"""
            <div class="stats-grid">
                <div class="stat-card">
                    <div class="stat-number">{len(self.video_durations):,}</div>
                    <div class="stat-label">{get_text(self.language, 'videos_with_duration')}</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number">{watch_stats['total_videos'] - len(self.video_durations):,}</div>
                    <div class="stat-label">{get_text(self.language, 'videos_without_duration')}</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number">{watch_stats['coverage_percent']:.1f}%</div>
                    <div class="stat-label">{get_text(self.language, 'data_coverage')}</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number">{watch_stats['avg_duration_formatted']}</div>
                    <div class="stat-label">{get_text(self.language, 'average_duration')}</div>
                </div>
            </div>
            
            <h3>📊 {get_text(self.language, 'watch_time')}</h3>
            <div class="stats-grid">
                <div class="stat-card">
                    <div class="stat-number">{watch_stats['total_duration_formatted']}</div>
                    <div class="stat-label">{get_text(self.language, 'total_time_known_videos')}</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number">{watch_stats['estimated_total_time_formatted']}</div>
                    <div class="stat-label">{get_text(self.language, 'estimated_total_time')}</div>
                </div>
            </div>
"""
        else:
            html_content += f"""
            <p><em>{get_text(self.language, 'duration_data_not_available')}</em></p>
"""
        
        html_content += f"""
        </div>
        
        <div class="section">
            <h2>📊 {get_text(self.language, 'additional_statistics')}</h2>
            <p><strong>{get_text(self.language, 'analysis_period')}:</strong> {stats['date_range']}</p>
            <p><strong>{get_text(self.language, 'data_sources')}:</strong></p>
            <ul>
"""
        
        # Добавляем статистику по источникам
        for source, count in stats['source_stats'].items():
            html_content += f"                <li>{source}: {count:,} {get_text(self.language, 'records')}</li>\n"
        
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
        
        self.console.print(f"[green]✓ {get_text(self.language, 'html_saved', path=self.output_dir / 'report.html')}[/green]")
    
    def export_to_csv(self) -> None:
        """Экспорт данных в CSV файл"""
        if self.df is None or len(self.df) == 0:
            self.console.print(f"[red]{get_text(self.language, 'no_data_for_export')}[/red]")
            return
        
        self.console.print(f"[bold blue]{get_text(self.language, 'exporting_csv')}[/bold blue]")
        
        # Создаем копию DataFrame для экспорта
        export_df = self.df.copy()
        
        # Получаем названия колонок для текущего языка
        csv_columns = get_csv_columns(self.language)
        
        # Добавляем дополнительные колонки для удобства
        export_df['date_formatted'] = export_df['timestamp'].dt.strftime('%Y-%m-%d')
        export_df['time_formatted'] = export_df['timestamp'].dt.strftime('%H:%M:%S')
        export_df['year_month'] = export_df['timestamp'].dt.strftime('%Y-%m')
        export_df['day_of_week_local'] = export_df['day_of_week'].map({
            'Monday': get_day_of_week(self.language, 0),
            'Tuesday': get_day_of_week(self.language, 1), 
            'Wednesday': get_day_of_week(self.language, 2),
            'Thursday': get_day_of_week(self.language, 3),
            'Friday': get_day_of_week(self.language, 4),
            'Saturday': get_day_of_week(self.language, 5),
            'Sunday': get_day_of_week(self.language, 6)
        })
        
        # Переименовываем колонки для лучшей читаемости
        export_df = export_df.rename(columns={
            'video_id': csv_columns['video_id'],
            'title': csv_columns['title'],
            'url': csv_columns['url'],
            'channel': csv_columns['channel'],
            'source': csv_columns['source'],
            'timestamp': get_text(self.language, 'datetime_utc'),
            'date': get_text(self.language, 'date'),
            'hour': get_text(self.language, 'hour'),
            'day_of_week': get_text(self.language, 'day_of_week_en'),
            'month': get_text(self.language, 'month'),
            'year': get_text(self.language, 'year'),
            'date_formatted': csv_columns['date'],
            'time_formatted': csv_columns['time'],
            'year_month': get_text(self.language, 'year_month')
        })
        
        # Сохраняем имя колонки дня недели для статистики
        day_of_week_column = get_text(self.language, 'day_of_week_en')
        
        # Добавляем информацию о длительности, если есть
        if hasattr(self, 'video_durations') and self.video_durations:
            export_df[csv_columns['duration_seconds']] = export_df[csv_columns['video_id']].map(self.video_durations)
            export_df[csv_columns['duration_formatted']] = export_df[csv_columns['duration_seconds']].apply(
                lambda x: self.format_duration(x) if pd.notna(x) else get_text(self.language, 'unknown')
            )
            export_df[csv_columns['duration_minutes']] = export_df[csv_columns['duration_seconds']].apply(
                lambda x: round(x / 60, 1) if pd.notna(x) else None
            )
        
        # Выбираем и переупорядочиваем колонки для экспорта
        columns_order = [
            csv_columns['video_id'],
            csv_columns['title'], 
            csv_columns['channel'],
            csv_columns['url'],
            csv_columns['date'],
            csv_columns['time'],
            get_text(self.language, 'year_month'),
            day_of_week_column,
            get_text(self.language, 'hour'),
            csv_columns['source'],
            get_text(self.language, 'datetime_utc')
        ]
        
        # Добавляем колонки длительности, если есть
        if hasattr(self, 'video_durations') and self.video_durations:
            columns_order.extend([csv_columns['duration_seconds'], csv_columns['duration_formatted'], csv_columns['duration_minutes']])
        
        # Добавляем колонки, которые могут отсутствовать
        available_columns = [col for col in columns_order if col in export_df.columns]
        export_df = export_df[available_columns]
        
        # Сохраняем основной CSV
        csv_path = self.output_dir / "youtube_history_export.csv"
        export_df.to_csv(csv_path, index=False, encoding='utf-8-sig')
        

        
        # Создаем сводную статистику
        summary_stats = {
            get_text(self.language, 'general_statistics'): {
                get_text(self.language, 'total_records_key'): len(export_df),
                get_text(self.language, 'period_start'): export_df[csv_columns['date']].min(),
                get_text(self.language, 'period_end'): export_df[csv_columns['date']].max(),
                get_text(self.language, 'days_count'): (export_df[get_text(self.language, 'datetime_utc')].max() - export_df[get_text(self.language, 'datetime_utc')].min()).days if len(export_df) > 0 else 0
            },
            get_text(self.language, 'statistics_by_sources'): export_df[csv_columns['source']].value_counts().to_dict(),
            get_text(self.language, 'top_10_channels'): export_df[csv_columns['channel']].value_counts().head(10).to_dict(),
            get_text(self.language, 'statistics_by_days'): export_df[day_of_week_column].value_counts().to_dict(),
            get_text(self.language, 'statistics_by_hours'): export_df[get_text(self.language, 'hour')].value_counts().sort_index().to_dict()
        }
        
        # Сохраняем сводную статистику
        import json
        summary_path = self.output_dir / "youtube_history_summary.json"
        with open(summary_path, 'w', encoding='utf-8') as f:
            json.dump(summary_stats, f, ensure_ascii=False, indent=2, default=str)
        
        # Создаем README для CSV
        readme_content = f"""# {get_text(self.language, 'youtube_history_export')}

## {get_text(self.language, 'export_files')}:

### 1. youtube_history_export.csv
{get_text(self.language, 'csv_main_file_description')}

{get_text(self.language, 'csv_columns_header')}
- {csv_columns['video_id']}{get_text(self.language, 'csv_video_id_desc')}
- {csv_columns['title']}{get_text(self.language, 'csv_title_desc')}
- {csv_columns['channel']}{get_text(self.language, 'csv_channel_desc')}
- {csv_columns['url']}{get_text(self.language, 'csv_url_desc')}
- {csv_columns['date']}{get_text(self.language, 'csv_date_desc')}
- {csv_columns['time']}{get_text(self.language, 'csv_time_desc')}
- {get_text(self.language, 'year_month')}{get_text(self.language, 'year_month_format')}
- {csv_columns['day_of_week']}{get_text(self.language, 'day_of_week_format')} {get_text(self.language, 'language_ru' if self.language == 'ru' else 'language_en')}
- {get_text(self.language, 'hour')}{get_text(self.language, 'hour_format')}
- {csv_columns['source']}{get_text(self.language, 'csv_source_desc')}
- {get_text(self.language, 'datetime_utc')}{get_text(self.language, 'csv_datetime_utc_desc')}

### 2. youtube_history_summary.json
{get_text(self.language, 'csv_summary_description')}

### 3. report.html
{get_text(self.language, 'csv_html_description')}

## {get_text(self.language, 'general_information')}:
- {get_text(self.language, 'total_records')}: {len(export_df)}
- {get_text(self.language, 'period')}: {export_df[csv_columns['date']].min()} - {export_df[csv_columns['date']].max()}
{get_text(self.language, 'csv_youtube_music_excluded')}
{get_text(self.language, 'csv_my_activity_desc')}
{get_text(self.language, 'csv_duplicates_desc')}

## {get_text(self.language, 'notes')}:
{get_text(self.language, 'csv_unknown_channels_desc')}
{get_text(self.language, 'csv_time_utc_desc')}
{get_text(self.language, 'csv_merged_sources_desc')}
"""
        
        readme_path = self.output_dir / "README_export.md"
        with open(readme_path, 'w', encoding='utf-8') as f:
            f.write(readme_content)
        
        self.console.print(f"[green]✓ {get_text(self.language, 'csv_saved', path=csv_path)}[/green]")
        self.console.print(f"[green]✓ {get_text(self.language, 'summary_statistics')}: {summary_path}[/green]")
        self.console.print(f"[green]✓ {get_text(self.language, 'readme_file')}: {readme_path}[/green]")
        self.console.print(f"[blue]{get_text(self.language, 'csv_file_size')}: {csv_path.stat().st_size / 1024 / 1024:.1f} MB[/blue]")
        
        # Показываем краткую статистику
        self.console.print(f"\n[bold yellow]{get_text(self.language, 'export_summary')}:[/bold yellow]")
        self.console.print(f"📊 {get_text(self.language, 'total_records')}: {len(export_df):,}")
        self.console.print(f"📅 {get_text(self.language, 'period')}: {export_df[csv_columns['date']].min()} - {export_df[csv_columns['date']].max()}")
        self.console.print(f"🎯 {get_text(self.language, 'unique_channels')}: {export_df[csv_columns['channel']].nunique()}")
        self.console.print(f"📁 {get_text(self.language, 'file_ready_for_import')}")
    
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
            'end_date': end_date,
            'date_range': f"{start_date} - {end_date}"
        }
    
    def show_tui(self) -> None:
        """Показ TUI интерфейса"""
        while True:
            self.console.clear()
            
            # Заголовок
            self.console.print("╭───────────────────────────────────────╮")
            self.console.print(f"│ {get_text(self.language, 'app_title')}              │")
            self.console.print(f"│ {get_text(self.language, 'app_subtitle')} │")
            self.console.print("╰───────────────────────────────────────╯")
            
            # Показываем статистику, если есть данные
            if self.df is not None and len(self.df) > 0:
                stats = self.generate_statistics()
                
                # Основная статистика
                self.console.print(f"\n      📊 {get_text(self.language, 'main_statistics')}       ")
                table = Table(show_header=False, box=None)
                table.add_column(get_text(self.language, 'parameter'), style="cyan")
                table.add_column(get_text(self.language, 'value'), style="green")
                
                table.add_row(get_text(self.language, 'total_videos_label'), f"{stats['total_videos']:,}")
                table.add_row(get_text(self.language, 'active_days_label'), f"{stats['total_videos']:,}")
                table.add_row(get_text(self.language, 'avg_videos_per_day_label'), f"{stats['avg_videos_per_day']:.1f}")
                
                self.console.print(table)
                
                # Топ каналов
                self.console.print(f"\n      🏆 {get_text(self.language, 'top_channels')}      ")
                table = Table(show_header=False, box=None)
                table.add_column(get_text(self.language, 'channel'), style="cyan")
                table.add_column(get_text(self.language, 'video'), style="green")
                
                for channel, count in stats['top_channels'][:5]:
                    table.add_row(channel, str(count))
                
                self.console.print(table)
            
            # Меню действий
            self.console.print(f"\n[bold yellow]{get_text(self.language, 'main_menu_title')}[/bold yellow]")
            self.console.print(get_text(self.language, 'menu_option_1'))
            self.console.print(get_text(self.language, 'menu_option_2'))
            self.console.print(get_text(self.language, 'menu_option_3'))
            self.console.print(get_text(self.language, 'menu_option_4'))
            self.console.print(get_text(self.language, 'menu_option_5'))
            self.console.print(get_text(self.language, 'menu_option_0'))
            
            choice = input(f"\n{get_text(self.language, 'enter_choice')}").strip()
            
            if choice == "0":
                self.console.print(f"[yellow]{get_text(self.language, 'goodbye')}[/yellow]")
                break
            elif choice == "1":
                self.load_takeout_data_menu()
            elif choice == "2":
                if self.df is not None:
                    sample_size = input(get_text(self.language, 'sample_size_prompt')).strip()
                    sample_size = int(sample_size) if sample_size.isdigit() else 100
                    self.get_durations(sample_size)
                else:
                    self.console.print(f"[red]{get_text(self.language, 'no_data_loaded')}[/red]")
            elif choice == "3":
                if self.df is not None:
                    stats = self.generate_statistics()
                    self.generate_html_report(stats)
                else:
                    self.console.print(f"[red]{get_text(self.language, 'no_data_loaded')}[/red]")
            elif choice == "4":
                if self.df is not None:
                    self.export_to_csv()
                else:
                    self.console.print(f"[red]{get_text(self.language, 'no_data_loaded')}[/red]")
            elif choice == "5":
                report_path = self.output_dir / "report.html"
                if report_path.exists():
                    import webbrowser
                    webbrowser.open(f"file://{report_path.absolute()}")
                else:
                    self.console.print(f"[red]{get_text(self.language, 'report_not_created')}[/red]")
            else:
                self.console.print(f"[red]{get_text(self.language, 'invalid_choice')}[/red]")
            
            input(f"\n{get_text(self.language, 'press_enter')}")
            self.console.clear()
    
    def load_takeout_data_menu(self) -> None:
        """Меню загрузки данных из Takeout"""
        self.console.print(f"\n[bold blue]{get_text(self.language, 'loading_data')}[/bold blue]")
        
        # Автоматический поиск файлов
        history_file = Path("Takeout/YouTube and YouTube Music/history/watch-history.json")
        activity_file = Path("Takeout/My Activity/YouTube/MyActivity.json")
        
        loaded_any = False
        
        if history_file.exists():
            self.console.print(f"[green]{get_text(self.language, 'found_history_file', path=history_file)}[/green]")
            if Confirm.ask(get_text(self.language, 'load_watch_history')):
                if self.load_data_source(str(history_file), 'watch_history'):
                    loaded_any = True
        
        if activity_file.exists():
            self.console.print(f"[green]{get_text(self.language, 'found_my_activity', path=activity_file)}[/green]")
            if Confirm.ask(get_text(self.language, 'load_watch_history')):
                if self.load_data_source(str(activity_file), 'my_activity'):
                    loaded_any = True
        
        if loaded_any:
            self.process_data()
        else:
            self.console.print(f"[red]{get_text(self.language, 'no_files_loaded')}[/red]")

def main():
    """Главная функция"""
    analyzer = YouTubeAnalyzer()
    
    try:
        # Сначала выбираем язык
        analyzer.select_language()
        # Затем показываем TUI
        analyzer.show_tui()
    except KeyboardInterrupt:
        analyzer.console.print(f"\n[yellow]{get_text(analyzer.language, 'program_interrupted')}[/yellow]")
    except Exception as e:
        analyzer.console.print(f"\n[red]{get_text(analyzer.language, 'error')}: {e}[/red]")

if __name__ == "__main__":
    main()
