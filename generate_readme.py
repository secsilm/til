import os
from datetime import datetime
from pathlib import Path
import subprocess
import pytz

def get_commit_date(file_path):
    """Get the commit date for a file using git log and convert to Beijing time (GMT+8)."""
    try:
        result = subprocess.run(
            ['git', 'log', '-1', '--format=%cd', '--date=iso', '--', file_path],  # Add '--' to specify the file
            capture_output=True, text=True, check=True
        )
        # Parse the commit date (ISO 8601 format, e.g. 2024-12-17T10:30:00+08:00)
        commit_date_str = result.stdout.strip()
        print(f"{commit_date_str=}")
        commit_date = datetime.strptime(commit_date_str, '%Y-%m-%d %H:%M:%S %z')
        
        # Convert the date to Beijing time (GMT+8)
        beijing_tz = pytz.timezone('Asia/Shanghai')
        commit_date = commit_date.astimezone(beijing_tz).date()
        
        return commit_date
    except subprocess.CalledProcessError:
        return None

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
    
    readme_content = "# Today I Learned\n\n记录日常遇到的不足以形成一篇完整博文的小问题、小技术点，inspired by [simonw/til](https://github.com/simonw/til) 。\n\n"
    
    for topic in topics:
        readme_content += f"## {topic.name}\n"
        
        # List all markdown files in the topic directory
        markdown_files = [f for f in topic.glob('*.md')]
        
        # Get commit date for each markdown file
        markdown_with_dates = []
        for md_file in markdown_files:
            title = extract_title(md_file)
            article_date = get_commit_date(md_file)
            print(md_file, title, article_date)
            markdown_with_dates.append((md_file, title, article_date))
        
        # Sort files by commit date (most recent first)
        markdown_with_dates.sort(key=lambda x: x[2], reverse=True)
        
        for md_file, title, article_date in markdown_with_dates:
            # Format the article entry with title and date
            if article_date:
                formatted_date = article_date.strftime('%Y-%m-%d')
                readme_content += f"- [{title}]({md_file.relative_to(base_dir)}) - {formatted_date}\n"
            else:
                readme_content += f"- [{title}]({md_file.relative_to(base_dir)})\n"
    
    # Write the content to the README.md
    with open(output_file, 'w', encoding='utf-8') as readme_file:
        readme_file.write(readme_content)

if __name__ == '__main__':
    generate_readme()
