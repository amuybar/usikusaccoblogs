import os
import markdown
from datetime import datetime
import xml.etree.ElementTree as ET
from pathlib import Path
import yaml

class BlogGenerator:
    def __init__(self, posts_dir='posts', output_dir='public'):
        self.posts_dir = posts_dir
        self.output_dir = output_dir
        self.posts = []
        
    def parse_post(self, filename):
        """Parse a blog post file with YAML frontmatter and markdown content."""
        with open(filename, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # Split YAML frontmatter from markdown content
        parts = content.split('---\n')
        if len(parts) >= 3:
            frontmatter = yaml.safe_load(parts[1])
            markdown_content = parts[2]
        else:
            raise ValueError(f"Invalid post format in {filename}")
            
        return {
            'title': frontmatter['title'],
            'date': frontmatter['date'],
            'description': frontmatter.get('description', ''),
            'content': markdown.markdown(markdown_content),
            'slug': Path(filename).stem
        }
        
    def generate_rss(self):
        """Generate RSS feed from blog posts."""
        rss = ET.Element('rss', version='2.0')
        channel = ET.SubElement(rss, 'channel')
        
        # Add channel metadata
        ET.SubElement(channel, 'title').text = 'My Blog'
        ET.SubElement(channel, 'link').text = 'https://yourblog.com'
        ET.SubElement(channel, 'description').text = 'My Personal Blog'
        
        # Add items for each post
        for post in sorted(self.posts, key=lambda x: x['date'], reverse=True):
            item = ET.SubElement(channel, 'item')
            ET.SubElement(item, 'title').text = post['title']
            ET.SubElement(item, 'link').text = f"https://yourblog.com/posts/{post['slug']}.html"
            ET.SubElement(item, 'description').text = post['description']
            ET.SubElement(item, 'pubDate').text = post['date'].strftime('%a, %d %b %Y %H:%M:%S %z')
            
        # Write RSS feed to file
        tree = ET.ElementTree(rss)
        os.makedirs(self.output_dir, exist_ok=True)
        tree.write(f'{self.output_dir}/feed.xml', encoding='utf-8', xml_declaration=True)
        
    def generate_html(self):
        """Generate HTML files for each post and index page."""
        os.makedirs(f'{self.output_dir}/posts', exist_ok=True)
        
        # Generate individual post pages
        for post in self.posts:
            self._generate_post_page(post)
            
        # Generate index page
        self._generate_index_page()
        
    def _generate_post_page(self, post):
        """Generate HTML page for a single post."""
        with open('templates/post.html', 'r') as f:
            template = f.read()
            
        html = template.format(
            title=post['title'],
            date=post['date'].strftime('%B %d, %Y'),
            content=post['content']
        )
        
        with open(f"{self.output_dir}/posts/{post['slug']}.html", 'w') as f:
            f.write(html)
            
    def _generate_index_page(self):
        """Generate main index page with list of posts."""
        with open('templates/index.html', 'r') as f:
            template = f.read()
            
        posts_html = ''
        for post in sorted(self.posts, key=lambda x: x['date'], reverse=True):
            posts_html += f"""
            <article class="post-preview">
                <h2><a href="/posts/{post['slug']}.html">{post['title']}</a></h2>
                <div class="post-meta">{post['date'].strftime('%B %d, %Y')}</div>
                <p>{post['description']}</p>
            </article>
            """
            
        html = template.format(posts=posts_html)
        
        with open(f'{self.output_dir}/index.html', 'w') as f:
            f.write(html)
            
    def build(self):
        """Build the entire blog."""
        # Load all posts
        for filename in Path(self.posts_dir).glob('*.md'):
            self.posts.append(self.parse_post(filename))
            
        # Generate RSS and HTML
        self.generate_rss()
        self.generate_html()

if __name__ == '__main__':
    generator = BlogGenerator()
    generator.build()