import markdown
from bs4 import BeautifulSoup
from pathlib import Path

def get_article_title(md_file_path):
    """Extract the title from the top header (H1) in the markdown file."""
    with open(md_file_path, 'r', encoding='utf-8') as file:
        content = file.read()
        html = markdown.markdown(content)
        soup = BeautifulSoup(html, 'html.parser')
        title = soup.find('h1')  # Get the first H1 header
        return title.text if title else "Untitled"

def generate_readme(base_dir):
    """Generate README.md based on the file structure."""
    base_path = Path(base_dir)
    readme_content = "# Today I Learned\n\n记录日常遇到的不足以形成一篇完整博文的小问题、小技术点，inspired by [simonw/til](https://github.com/simonw/til)。\n\n"
    
    topics = {}

    # Directly get all folders under base_dir
    for topic_folder in base_path.iterdir():
        if topic_folder.is_dir():  # Make sure it's a directory
            # Get all markdown files under this folder
            for md_file in topic_folder.glob("*.md"):
                article_title = get_article_title(md_file)
                article_path = md_file.relative_to(base_path)
                
                if topic_folder.name not in topics:
                    topics[topic_folder.name] = []
                topics[topic_folder.name].append((article_title, article_path))
    
    # Sort topics alphabetically
    for topic, articles in sorted(topics.items()):
        readme_content += f"## {topic.capitalize()}\n\n"
        for article_title, article_path in sorted(articles):
            readme_content += f"- [{article_title}]({article_path})\n"
        readme_content += "\n"
    
    # Write to README.md
    with open(base_path / "README.md", 'w', encoding='utf-8') as readme_file:
        readme_file.write(readme_content)

# Change the base directory to your root folder where 'docker' and 'milvus' folders are located
base_directory = "./"
generate_readme(base_directory)
