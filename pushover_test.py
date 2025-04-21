import http.client
import urllib
import json
import time
import markdown
import sys
import random
import datetime  # Add this for timestamping logs

# Setup logging
def log_message(message):
    """Log a message with timestamp to both stdout and the log file"""
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_msg = f"[{timestamp}] {message}"
    print(log_msg)
    with open("pushover.log", "a") as log_file:
        log_file.write(log_msg + "\n")

# Parse command line arguments
log_message(f"Command line arguments: {sys.argv}")
page = False
custom_sound = None

# Process arguments
args = sys.argv.copy()
for i, arg in enumerate(args):
    if arg == "--page" and i < len(args):
        page = True
        sys.argv.remove("--page")
        log_message("Page mode enabled")
    elif arg.startswith("--sound=") and i < len(args):
        custom_sound = arg.split("=")[1]
        sys.argv.remove(arg)
        log_message(f"Custom sound specified: {custom_sound}")

# Set sound based on parameters
if custom_sound:
    sound = custom_sound
    log_message(f"Using custom sound: {sound}")
else:
    sound = "plan" + str(random.randint(1, 9))
    if page:
        sound = "question" + str(random.randint(1, 9))
    log_message(f"Using sound: {sound}")

# Credentials
APP_TOKEN = "azottw766yxy7oz3vsu2oz432brx8f"
USER_KEY = "uqek4s2jo8pmrkskp96ravqb85yr15"

def send_basic_message(message, title=None):
    """Send a basic message to Pushover"""
    log_message(f"Sending basic message: {title if title else 'No title'}")
    conn = http.client.HTTPSConnection("api.pushover.net:443")
    
    params = {
        "token": APP_TOKEN,
        "user": USER_KEY,
        "message": message,
    }
    
    if title:
        params["title"] = title
        
    # Always add sound parameter - plan sounds by default, question sounds if --page is given
    params["sound"] = sound
    log_message(f"Adding sound: {sound}")
        
    try:
        conn.request("POST", "/1/messages.json",
                    urllib.parse.urlencode(params),
                    {"Content-type": "application/x-www-form-urlencoded"})
        
        response = conn.getresponse()
        result = json.loads(response.read().decode())
        log_message(f"Response: {result}")
        return result
    except Exception as e:
        log_message(f"Error sending message: {str(e)}")
        return {"status": 0, "error": str(e)}

def send_emergency_message(message, title=None):
    """Send an emergency priority message that requires acknowledgment"""
    conn = http.client.HTTPSConnection("api.pushover.net:443")
    
    params = {
        "token": APP_TOKEN,
        "user": USER_KEY,
        "message": message,
        "priority": 2,  # Emergency priority
        "retry": 30,    # Retry every 30 seconds
        "expire": 3600, # Expire after 1 hour
    }
    
    if title:
        params["title"] = title
        
    conn.request("POST", "/1/messages.json",
                urllib.parse.urlencode(params),
                {"Content-type": "application/x-www-form-urlencoded"})
    
    response = conn.getresponse()
    return json.loads(response.read().decode())

def send_html_message(message, title=None):
    """Send a message with HTML formatting"""
    conn = http.client.HTTPSConnection("api.pushover.net:443")
    
    params = {
        "token": APP_TOKEN,
        "user": USER_KEY,
        "message": message,
        "html": 1,
    }
    
    if title:
        params["title"] = title
        
    conn.request("POST", "/1/messages.json",
                urllib.parse.urlencode(params),
                {"Content-type": "application/x-www-form-urlencoded"})
    
    response = conn.getresponse()
    return json.loads(response.read().decode())

def send_url_message(message, url, url_title=None, title=None):
    """Send a message with a supplementary URL"""
    conn = http.client.HTTPSConnection("api.pushover.net:443")
    
    params = {
        "token": APP_TOKEN,
        "user": USER_KEY,
        "message": message,
        "url": url,
    }
    
    if url_title:
        params["url_title"] = url_title
    
    if title:
        params["title"] = title
        
    conn.request("POST", "/1/messages.json",
                urllib.parse.urlencode(params),
                {"Content-type": "application/x-www-form-urlencoded"})
    
    response = conn.getresponse()
    return json.loads(response.read().decode())

def send_markdown_message(markdown_text, title=None):
    """Convert markdown to HTML and send as a Pushover message"""
    log_message(f"Sending markdown message: {title if title else 'No title'}")
    
    # Convert markdown to HTML
    try:
        html = markdown.markdown(markdown_text)
        log_message("Markdown converted to HTML successfully")
    except Exception as e:
        log_message(f"Error converting markdown to HTML: {str(e)}")
        return {"status": 0, "error": f"Markdown conversion failed: {str(e)}"}
    
    # Clean up the HTML for Pushover compatibility
    # Pushover only supports: <b>, <i>, <u>, <font>, <a>
    html = (html
           .replace('<h1>', '<b>')
           .replace('</h1>', '</b>\n\n')
           .replace('<h2>', '<b>')
           .replace('</h2>', '</b>\n\n')
           .replace('<strong>', '<b>')
           .replace('</strong>', '</b>')
           .replace('<em>', '<i>')
           .replace('</em>', '</i>')
           .replace('<code>', '<i>')
           .replace('</code>', '</i>')
           .replace('<li>', '• ')
           .replace('</li>', '\n')
           .replace('<ul>', '\n')
           .replace('</ul>', '\n')
           .replace('<pre>', '')
           .replace('</pre>', '')
           )
    
    # Send the converted HTML message
    conn = http.client.HTTPSConnection("api.pushover.net:443")
    
    params = {
        "token": APP_TOKEN,
        "user": USER_KEY,
        "message": html,
        "html": 1,
    }
    
    if title:
        params["title"] = title
    
    # Always add sound parameter - plan sounds by default, question sounds if --page is given
    params["sound"] = sound
    log_message(f"Adding sound: {sound}")
    
    try:
        conn.request("POST", "/1/messages.json",
                    urllib.parse.urlencode(params),
                    {"Content-type": "application/x-www-form-urlencoded"})
        
        response = conn.getresponse()
        result = json.loads(response.read().decode())
        log_message(f"Response: {result}")
        return result
    except Exception as e:
        log_message(f"Error sending message: {str(e)}")
        return {"status": 0, "error": str(e)}

def send_markdown_file(file_path, title=None):
    """Read a markdown file and send it as a Pushover message"""
    log_message(f"Reading markdown file: {file_path}")
    try:
        with open(file_path, 'r') as f:
            markdown_text = f.read()
        log_message(f"File read successfully ({len(markdown_text)} characters)")
        return send_markdown_message(markdown_text, title)
    except Exception as e:
        log_message(f"Error reading file {file_path}: {str(e)}")
        return {"status": 0, "error": f"File read failed: {str(e)}"}

if __name__ == "__main__":
    if len(sys.argv) < 3:
        log_message("Error: Insufficient arguments")
        print("This script is meant to be called from ninja-mail")
        print("Usage: python3 pushover_test.py <markdown_file> <subject> [--page] [--sound=<sound_name>]")
        print("  --page: Use question sounds instead of plan sounds")
        print("  --sound=<sound_name>: Use a specific sound (e.g., idle1, idle2, etc.)")
        sys.exit(1)
        
    markdown_file = sys.argv[1]
    subject = sys.argv[2]
    
    log_message(f"Sending markdown file '{markdown_file}' with subject '{subject}'...")
    result = send_markdown_file(markdown_file, subject)
    log_message(f"Result: {result}")
    
    # Exit with appropriate code
    if result.get("status") == 1:
        sys.exit(0)
    else:
        sys.exit(1)