import os
from datetime import datetime
from pathlib import Path
import subprocess
import pytz

def get_commit_date(file_path):
    """Get the commit date for a file using git log and convert to Beijing time (GMT+8)."""
    try:
        # the most recent commit date
        result = subprocess.run(
            ['git', 'log', '-1', '--format=%cd', '--date=iso', '--', file_path],  # Add '--' to specify the file
            capture_output=True, text=True, check=True
        )

        # Parse the commit date (ISO 8601 format, e.g. 2024-12-17T10:30:00+08:00)
        commit_date_str = result.stdout.strip()
        commit_date = datetime.strptime(commit_date_str, '%Y-%m-%d %H:%M:%S %z')
        
        # Convert the date to Beijing time (GMT+8)
        beijing_tz = pytz.timezone('Asia/Shanghai')
        most_recent_commit_date = commit_date.astimezone(beijing_tz).date()

        # the first commit date
        result = subprocess.run(
            ['git', 'log', '--diff-filter=A', '--format=%cd', '--date=iso', '--', file_path],  # Add '--' to specify the file
            capture_output=True, text=True, check=True
        )

        # Parse the commit date (ISO 8601 format, e.g. 2024-12-17T10:30:00+08:00)
        commit_date_str = result.stdout.strip()
        commit_date = datetime.strptime(commit_date_str, '%Y-%m-%d %H:%M:%S %z')
        
        # Convert the date to Beijing time (GMT+8)
        beijing_tz = pytz.timezone('Asia/Shanghai')
        first_commit_date = commit_date.astimezone(beijing_tz).date()
        
        return first_commit_date, most_recent_commit_date
    except subprocess.CalledProcessError:
        return None, None

def extract_title(markdown_file_path):
    """Extract the title (from the first header) of the markdown file."""
    with open(markdown_file_path, 'r', encoding='utf-8') as file:
        content = file.read()
        
        # Extract the title (assuming it's the first header in the markdown)
        title_line = content.splitlines()[0]  # Assuming first line is the title
        title = title_line.strip('#').strip()  # Remove '#' and whitespace
        
        return title

def generate_readme(base_dir='.', output_file='README.md'):
    """Generate the README.md file with a list of articles, including their dates."""
    # Create a list of topics (directories)
    topics = sorted([d for d in Path(base_dir).iterdir() if d.is_dir() and not d.name.startswith('.')])
    n_topics = len(topics)
    n_tils = 0
    
    readme_content = "# Today I Learned\n\n记录日常遇到的不足以形成一篇完整博文的小问题、小技术点，inspired by [simonw/til](https://github.com/simonw/til) 。\n\n目前有 {n_tils} 篇 TIL，涵盖 {n_topics} 个 topic。\n\n"
    
    for topic in topics:
        readme_content += f"## {topic.name}\n"
        
        # List all markdown files in the topic directory
        markdown_files = [f for f in topic.glob('*.md')]
        n_tils += len(markdown_files)
        
        # Get commit date for each markdown file
        markdown_with_dates = []
        for md_file in markdown_files:
            title = extract_title(md_file)
            first_commit_date, most_recent_commit_date = get_commit_date(md_file)
            markdown_with_dates.append((md_file, title, first_commit_date, most_recent_commit_date))
        
        # Sort files by commit date (most recent first)
        markdown_with_dates.sort(key=lambda x: x[3], reverse=True)
        
        for md_file, title, create_time, update_time in markdown_with_dates:
            # Format the article entry with title and date
            if create_time:
                formatted_date = article_date.strftime('%Y-%m-%d')
                readme_content += f"- [{title}]({md_file.relative_to(base_dir)}) - 更新于 {update_time}，创建于 {create_time}\n"
            else:
                readme_content += f"- [{title}]({md_file.relative_to(base_dir)})\n"

    readme_content = readme_content.format(n_tils=n_tils, n_topics=n_topics)
    
    # Write the content to the README.md
    with open(output_file, 'w', encoding='utf-8') as readme_file:
        readme_file.write(readme_content)

if __name__ == '__main__':
    generate_readme()
