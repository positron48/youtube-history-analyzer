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
        
        # Берем случайную выборку
        sample = self.df.sample(min(sample_size, len(self.df)))
        
        # Здесь можно добавить логику получения длительности через yt-dlp
        # Пока просто показываем статистику
        self.console.print(f"[green]✓ Выборка из {len(sample)} видео готова для анализа длительности[/green]")
    
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
