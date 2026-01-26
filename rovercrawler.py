#!/usr/bin/env python3
"""
RoverCrawler v2.1 - Single-file web crawler for site structure mapping
Created by URDev
"""

import sys
import time
import argparse
from urllib.parse import urljoin, urlparse
from collections import deque
import threading
import json
import os

# Third-party imports (must be installed separately)
try:
    import requests
    from bs4 import BeautifulSoup
    from colorama import init, Fore, Style
    COLORAMA_AVAILABLE = True
except ImportError as e:
    print(f"Error: Missing required module: {e}")
    print("Install with: pip install requests beautifulsoup4 colorama")
    sys.exit(1)

# Initialize colorama for cross-platform colors
init(autoreset=True)

# ============================================================================
# 1. GLOBAL CONFIGURATION
# ============================================================================

CONFIG = {
    "max_depth": 3,
    "max_pages": 100,           # Safety limit
    "follow_external": False,
    "timeout": 10,
    "verbose": False,
    "user_agent": "Mozilla/5.0 (compatible; RoverCrawler/2.1; +https://github.com/urdev)",
    "rate_limit": 0.5,          # Seconds between requests
    "colors": {
        "root": Fore.GREEN + Style.BRIGHT,
        "link": Fore.CYAN,
        "external": Fore.YELLOW,
        "error": Fore.RED,
        "warning": Fore.YELLOW,
        "info": Fore.BLUE,
        "dim": Style.DIM,
        "reset": Style.RESET_ALL
    }
}

# ============================================================================
# 2. BANNER DISPLAY
# ============================================================================

def print_banner():
    """Print the cool ASCII banner"""
    # Using raw strings (r"") to handle backslashes properly
    banner = r"""                          ____
                         / __ \____ _   _____  _____
  By URDev | v2.1       / /_/ / __ \ | / / _ \/ ___/
                       / _, _/ /_/ / |/ /  __/ /
               |      /_/ |_|\____/|___/\___/_/
               |      ______                    __
  ____,________|_    / ____/________ __      __/ /__  _____
  c=<L__,o,_ __b.   / /   / ___/ __ `/ | /| / / / _ \/ ___/
  .=:" .-:"=":=.   / /___/ /  / /_/ /| |/ |/ / /  __/ /
  `-'  `-'   `-'   \____/_/   \__,_/ |__/|__/_/\___/_/"""
    
    print(f"{CONFIG['colors']['info']}{banner}{CONFIG['colors']['reset']}")
    print(f"{CONFIG['colors']['dim']}Web crawler for site structure mapping{CONFIG['colors']['reset']}")
    print("-" * 60)

# ============================================================================
# 3. URL NORMALIZATION & FILTERING
# ============================================================================

def normalize_url(base_url, link):
    """
    Normalize a URL relative to base URL
    Returns normalized URL or None if invalid
    """
    if not link or link.startswith(('javascript:', 'mailto:', 'tel:', '#')):
        return None
    
    # Handle relative URLs
    try:
        full_url = urljoin(base_url, link)
        parsed = urlparse(full_url)
        
        # Only accept http/https
        if parsed.scheme not in ('http', 'https'):
            return None
        
        # Remove fragments and query parameters for normalization
        clean_url = f"{parsed.scheme}://{parsed.netloc}{parsed.path}"
        
        # Remove trailing slash for consistency
        if clean_url.endswith('/') and len(clean_url) > 1:
            clean_url = clean_url.rstrip('/')
            
        return clean_url.lower()  # Case-insensitive comparison
    except Exception:
        return None

def is_same_domain(url1, url2):
    """Check if two URLs belong to the same domain"""
    try:
        domain1 = urlparse(url1).netloc
        domain2 = urlparse(url2).netloc
        return domain1 == domain2
    except Exception:
        return False

def should_crawl_url(url, root_domain, visited):
    """
    Determine if a URL should be crawled
    """
    if not url:
        return False
    
    if url in visited:
        return False
    
    parsed = urlparse(url)
    
    # Check scheme
    if parsed.scheme not in ('http', 'https'):
        return False
    
    # Check domain
    if not CONFIG['follow_external']:
        if parsed.netloc != root_domain:
            return False
    
    # Check file extensions to skip
    skip_extensions = {'.pdf', '.jpg', '.jpeg', '.png', '.gif', '.zip', 
                      '.tar', '.gz', '.exe', '.dmg', '.mp3', '.mp4', '.avi'}
    if any(url.lower().endswith(ext) for ext in skip_extensions):
        return False
    
    return True

# ============================================================================
# 4. HTML PARSING
# ============================================================================

def extract_links(html_content, base_url):
    """
    Extract all unique links from HTML content
    """
    links = set()
    
    try:
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Find all anchor tags
        for a_tag in soup.find_all('a', href=True):
            url = normalize_url(base_url, a_tag['href'])
            if url:
                links.add(url)
        
        # Also check for link tags (less common)
        for link_tag in soup.find_all('link', href=True):
            url = normalize_url(base_url, link_tag['href'])
            if url:
                links.add(url)
                
    except Exception as e:
        if CONFIG['verbose']:
            print(f"{CONFIG['colors']['warning']}[!] Parse error: {e}{CONFIG['colors']['reset']}")
    
    return links

# ============================================================================
# 5. CRAWLER CORE
# ============================================================================

class RoverCrawler:
    """Main crawler class"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': CONFIG['user_agent']
        })
        self.last_request_time = 0
        self.lock = threading.Lock()
        self.stats = {
            'pages_crawled': 0,
            'links_found': 0,
            'errors': 0,
            'start_time': time.time()
        }
    
    def rate_limit(self):
        """Enforce rate limiting between requests"""
        current_time = time.time()
        elapsed = current_time - self.last_request_time
        if elapsed < CONFIG['rate_limit']:
            time.sleep(CONFIG['rate_limit'] - elapsed)
        self.last_request_time = time.time()
    
    def fetch_url(self, url):
        """Fetch a URL with error handling"""
        self.rate_limit()
        
        if CONFIG['verbose']:
            print(f"{CONFIG['colors']['info']}[→] Fetching: {url}{CONFIG['colors']['reset']}")
        
        try:
            response = self.session.get(
                url,
                timeout=CONFIG['timeout'],
                allow_redirects=True,
                verify=True  # SSL verification
            )
            
            # Check if it's HTML
            content_type = response.headers.get('Content-Type', '').lower()
            if 'text/html' not in content_type:
                if CONFIG['verbose']:
                    print(f"{CONFIG['colors']['dim']}[i] Skipping non-HTML: {content_type[:30]}{CONFIG['colors']['reset']}")
                return None
            
            # Check status code
            if response.status_code != 200:
                if CONFIG['verbose']:
                    print(f"{CONFIG['colors']['warning']}[!] Status {response.status_code}: {url}{CONFIG['colors']['reset']}")
                return None
            
            self.stats['pages_crawled'] += 1
            return response.text
            
        except requests.exceptions.RequestException as e:
            if CONFIG['verbose']:
                print(f"{CONFIG['colors']['error']}[!] Request failed: {e}{CONFIG['colors']['reset']}")
            self.stats['errors'] += 1
            return None
        except Exception as e:
            if CONFIG['verbose']:
                print(f"{CONFIG['colors']['error']}[!] Unexpected error: {e}{CONFIG['colors']['reset']}")
            self.stats['errors'] += 1
            return None
    
    def crawl(self, start_url, max_depth=None):
        """
        Main crawl function using BFS for more predictable results
        Returns tree structure
        """
        if max_depth is None:
            max_depth = CONFIG['max_depth']
        
        root_domain = urlparse(start_url).netloc
        visited = set()
        to_visit = deque([(start_url, 0)])  # (url, depth)
        tree = {}
        
        print(f"{CONFIG['colors']['info']}[*] Starting crawl of {start_url}{CONFIG['colors']['reset']}")
        print(f"{CONFIG['colors']['dim']}[*] Max depth: {max_depth}, Max pages: {CONFIG['max_pages']}{CONFIG['colors']['reset']}")
        
        url_parent_map = {start_url: None}
        
        while to_visit and len(visited) < CONFIG['max_pages']:
            current_url, depth = to_visit.popleft()
            
            # Skip if already visited or too deep
            if current_url in visited or depth > max_depth:
                continue
            
            visited.add(current_url)
            
            # Fetch the page
            html = self.fetch_url(current_url)
            if html is None:
                continue
            
            # Extract links
            links = extract_links(html, current_url)
            self.stats['links_found'] += len(links)
            
            if CONFIG['verbose']:
                print(f"{CONFIG['colors']['dim']}[i] Found {len(links)} links at depth {depth}{CONFIG['colors']['reset']}")
            
            # Process each link
            for link in links:
                if link not in visited and should_crawl_url(link, root_domain, visited):
                    to_visit.append((link, depth + 1))
                    url_parent_map[link] = current_url
            
            # Update progress
            if len(visited) % 10 == 0:
                elapsed = time.time() - self.stats['start_time']
                print(f"{CONFIG['colors']['dim']}[i] Progress: {len(visited)} pages, {len(to_visit)} in queue ({elapsed:.1f}s){CONFIG['colors']['reset']}")
        
        # Build tree structure from parent map
        return self._build_tree(start_url, url_parent_map, visited)
    
    def _build_tree(self, root_url, parent_map, visited_urls):
        """Build tree structure from parent-child relationships"""
        # First, find all children for each URL
        children_map = {}
        for url in visited_urls:
            parent = parent_map.get(url)
            if parent:
                if parent not in children_map:
                    children_map[parent] = []
                children_map[parent].append(url)
        
        # Recursively build tree
        def build_subtree(url):
            subtree = {}
            for child in children_map.get(url, []):
                subtree[child] = build_subtree(child)
            return subtree
        
        return {root_url: build_subtree(root_url)}
    
    def print_stats(self):
        """Print crawling statistics"""
        elapsed = time.time() - self.stats['start_time']
        print(f"\n{CONFIG['colors']['info']}{'='*60}{CONFIG['colors']['reset']}")
        print(f"{CONFIG['colors']['root']}CRAWL STATISTICS:{CONFIG['colors']['reset']}")
        print(f"{CONFIG['colors']['dim']}  Pages crawled: {self.stats['pages_crawled']}")
        print(f"  Links found:  {self.stats['links_found']}")
        print(f"  Errors:       {self.stats['errors']}")
        print(f"  Time elapsed: {elapsed:.1f} seconds")
        if elapsed > 0:
            print(f"  Avg speed:    {self.stats['pages_crawled']/elapsed:.1f} pages/sec{CONFIG['colors']['reset']}")
        print(f"{CONFIG['colors']['info']}{'='*60}{CONFIG['colors']['reset']}")

# ============================================================================
# 6. TREE RENDERING
# ============================================================================

def print_tree(tree, prefix="", is_last=True, is_root=True):
    """
    Print tree structure with colors and formatting
    """
    if not tree:
        return
    
    items = list(tree.items())
    for i, (url, children) in enumerate(items):
        is_last_item = (i == len(items) - 1)
        
        # Determine branch characters
        if is_root and i == 0:
            branch = ""
            new_prefix = ""
        else:
            branch = "└── " if is_last_item else "├── "
            new_prefix = prefix + ("    " if is_last_item else "│   ")
        
        # Color coding
        parsed = urlparse(url)
        root_domain = urlparse(list(tree.keys())[0]).netloc
        
        if parsed.netloc != root_domain:
            color = CONFIG['colors']['external']
            suffix = " (external)"
        else:
            color = CONFIG['colors']['link']
            suffix = ""
        
        # Print the line
        print(f"{prefix}{branch}{color}{parsed.path or '/'}{suffix}{CONFIG['colors']['reset']}")
        
        # Recursively print children
        print_tree(children, new_prefix, is_last_item, False)

# ============================================================================
# 7. INTERACTIVE MODE
# ============================================================================

def interactive_setup():
    """Interactive configuration setup"""
    print(f"{CONFIG['colors']['root']}INTERACTIVE MODE{CONFIG['colors']['reset']}")
    print(f"{CONFIG['colors']['dim']}Configure the crawler (press Enter for defaults):{CONFIG['colors']['reset']}")
    print()
    
    # Get target URL
    while True:
        url = input(f"{CONFIG['colors']['info']}Target URL (include http:// or https://): {CONFIG['colors']['reset']}").strip()
        if url:
            if not url.startswith(('http://', 'https://')):
                print(f"{CONFIG['colors']['warning']}[!] Please include http:// or https://{CONFIG['colors']['reset']}")
                continue
            try:
                urlparse(url)
                break
            except:
                print(f"{CONFIG['colors']['error']}[!] Invalid URL format{CONFIG['colors']['reset']}")
        else:
            print(f"{CONFIG['colors']['error']}[!] URL is required{CONFIG['colors']['reset']}")
    
    # Get max depth
    depth_input = input(f"{CONFIG['colors']['info']}Max crawl depth [{CONFIG['max_depth']}]: {CONFIG['colors']['reset']}").strip()
    if depth_input.isdigit():
        depth = int(depth_input)
        if 1 <= depth <= 10:
            CONFIG['max_depth'] = depth
        else:
            print(f"{CONFIG['colors']['warning']}[!] Depth must be between 1-10, using default{CONFIG['colors']['reset']}")
    
    # Get max pages
    pages_input = input(f"{CONFIG['colors']['info']}Max pages to crawl [{CONFIG['max_pages']}]: {CONFIG['colors']['reset']}").strip()
    if pages_input.isdigit():
        pages = int(pages_input)
        if 10 <= pages <= 1000:
            CONFIG['max_pages'] = pages
        else:
            print(f"{CONFIG['colors']['warning']}[!] Pages must be between 10-1000, using default{CONFIG['colors']['reset']}")
    
    # Get verbose mode
    verbose_input = input(f"{CONFIG['colors']['info']}Verbose mode? [y/N]: {CONFIG['colors']['reset']}").strip().lower()
    CONFIG['verbose'] = verbose_input in ('y', 'yes')
    
    # Get external links
    external_input = input(f"{CONFIG['colors']['info']}Follow external links? [y/N]: {CONFIG['colors']['reset']}").strip().lower()
    CONFIG['follow_external'] = external_input in ('y', 'yes')
    
    print()
    return url

# ============================================================================
# 8. CLI PARSER
# ============================================================================

def parse_cli():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(
        description='RoverCrawler v2.1 - Web crawler for site structure mapping',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python rovercrawler.py https://example.com
  python rovercrawler.py https://example.com -d 4 -v --external
  python rovercrawler.py --export-json results.json

Note: External libraries required:
  pip install requests beautifulsoup4 colorama
"""
    )
    
    parser.add_argument(
        'url',
        nargs='?',
        help='Target URL to crawl (e.g., https://example.com)'
    )
    
    parser.add_argument(
        '-d', '--depth',
        type=int,
        help=f'Maximum crawl depth (default: {CONFIG["max_depth"]})'
    )
    
    parser.add_argument(
        '-p', '--pages',
        type=int,
        help=f'Maximum pages to crawl (default: {CONFIG["max_pages"]})'
    )
    
    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='Enable verbose output'
    )
    
    parser.add_argument(
        '-e', '--external',
        action='store_true',
        help='Follow external links (outside domain)'
    )
    
    parser.add_argument(
        '-t', '--timeout',
        type=int,
        help=f'Request timeout in seconds (default: {CONFIG["timeout"]})'
    )
    
    parser.add_argument(
        '--export-json',
        metavar='FILE',
        help='Export results as JSON file'
    )
    
    parser.add_argument(
        '--export-txt',
        metavar='FILE',
        help='Export results as plain text'
    )
    
    parser.add_argument(
        '--no-banner',
        action='store_true',
        help='Skip banner display'
    )
    
    parser.add_argument(
        '--no-colors',
        action='store_true',
        help='Disable colored output'
    )
    
    return parser.parse_args()

# ============================================================================
# 9. EXPORT FUNCTIONS
# ============================================================================

def export_json(tree, filename):
    """Export tree structure to JSON file"""
    try:
        with open(filename, 'w') as f:
            json.dump(tree, f, indent=2)
        print(f"{CONFIG['colors']['info']}[✓] Results exported to {filename}{CONFIG['colors']['reset']}")
    except Exception as e:
        print(f"{CONFIG['colors']['error']}[!] Failed to export JSON: {e}{CONFIG['colors']['reset']}")

def export_txt(tree, filename):
    """Export tree structure to plain text file"""
    try:
        original_colors = CONFIG['colors'].copy()
        
        # Temporarily disable colors for export
        for key in CONFIG['colors']:
            CONFIG['colors'][key] = ""
        
        with open(filename, 'w') as f:
            # Redirect print to file
            import io
            from contextlib import redirect_stdout
            
            output = io.StringIO()
            with redirect_stdout(output):
                print("=" * 60)
                print("ROVERCRAWLER EXPORT")
                print(f"Generated: {time.strftime('%Y-%m-%d %H:%M:%S')}")
                print("=" * 60)
                print()
                root_url = list(tree.keys())[0]
                print(f"Root URL: {root_url}")
                print(f"Crawl depth: {CONFIG['max_depth']}")
                print(f"Pages crawled: {len(get_all_urls(tree))}")
                print()
                print("SITE STRUCTURE:")
                print()
                print_tree(tree)
            
            f.write(output.getvalue())
        
        # Restore colors
        CONFIG['colors'] = original_colors
        
        print(f"{CONFIG['colors']['info']}[✓] Results exported to {filename}{CONFIG['colors']['reset']}")
    except Exception as e:
        print(f"{CONFIG['colors']['error']}[!] Failed to export text: {e}{CONFIG['colors']['reset']}")

def get_all_urls(tree):
    """Extract all URLs from tree structure"""
    urls = []
    for url, children in tree.items():
        urls.append(url)
        urls.extend(get_all_urls(children))
    return urls

# ============================================================================
# 10. MAIN ENTRY POINT
# ============================================================================

def main():
    """Main entry point"""
    args = parse_cli()
    
    # Handle color disabling
    if args.no_colors:
        for key in CONFIG['colors']:
            CONFIG['colors'][key] = ""
    
    # Show banner unless disabled
    if not args.no_banner:
        print_banner()
    
    # Determine mode: if no URL provided, use interactive mode
    if not args.url:
        # No URL provided, run interactive mode
        url = interactive_setup()
    else:
        url = args.url
        if not url.startswith(('http://', 'https://')):
            print(f"{CONFIG['colors']['error']}[!] URL must start with http:// or https://{CONFIG['colors']['reset']}")
            sys.exit(1)
    
    # Update config from CLI arguments
    if args.depth:
        CONFIG['max_depth'] = args.depth
    if args.pages:
        CONFIG['max_pages'] = args.pages
    if args.verbose:
        CONFIG['verbose'] = True
    if args.external:
        CONFIG['follow_external'] = True
    if args.timeout:
        CONFIG['timeout'] = args.timeout
    
    # Create and run crawler
    crawler = RoverCrawler()
    
    try:
        # Perform crawl
        tree = crawler.crawl(url)
        
        # Print results
        if tree:
            root_url = list(tree.keys())[0]
            print(f"\n{CONFIG['colors']['root']}SITE STRUCTURE:{CONFIG['colors']['reset']}")
            print(f"{CONFIG['colors']['dim']}Root: {root_url}{CONFIG['colors']['reset']}")
            print()
            print_tree(tree)
        else:
            print(f"{CONFIG['colors']['warning']}[!] No pages were crawled. Check URL and network connection.{CONFIG['colors']['reset']}")
        
        # Print statistics
        crawler.print_stats()
        
        # Export if requested
        if args.export_json:
            export_json(tree, args.export_json)
        
        if args.export_txt:
            export_txt(tree, args.export_txt)
        
        # Show summary
        all_urls = get_all_urls(tree)
        print(f"\n{CONFIG['colors']['info']}[✓] Crawl complete! Found {len(all_urls)} unique URLs.{CONFIG['colors']['reset']}")
        
    except KeyboardInterrupt:
        print(f"\n{CONFIG['colors']['warning']}[!] Crawl interrupted by user{CONFIG['colors']['reset']}")
        crawler.print_stats()
        sys.exit(0)
    except Exception as e:
        print(f"\n{CONFIG['colors']['error']}[!] Fatal error: {e}{CONFIG['colors']['reset']}")
        import traceback
        if CONFIG['verbose']:
            traceback.print_exc()
        sys.exit(1)

# ============================================================================
# ENTRY POINT
# ============================================================================

if __name__ == "__main__":
    main()
