#!/usr/bin/env python3
import os
import sys
import glob
import json
import html
import subprocess
from urllib.parse import urlparse, parse_qs
from http.server import HTTPServer, SimpleHTTPRequestHandler

PORT = 8080
CAPTIONS_FILE = "captions.json"

class AdminHTTPRequestHandler(SimpleHTTPRequestHandler):
    def end_headers(self):
        # Prevent caching for API calls to ensure updates are visible
        if self.path.startswith('/api/'):
            self.send_header('Cache-Control', 'no-store, no-cache, must-revalidate')
        super().end_headers()

    def do_GET(self):
        url = urlparse(self.path)
        
        # Route to admin interface
        if url.path in ('/', '/admin', '/admin.html'):
            self.send_response(200)
            self.send_header('Content-Type', 'text/html; charset=utf-8')
            self.end_headers()
            self.wfile.write(self.get_admin_html().encode('utf-8'))
            return
            
        # API: Get list of images and their captions
        elif url.path == '/api/images':
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            
            # Load captions
            captions = {}
            if os.path.exists(CAPTIONS_FILE):
                try:
                    with open(CAPTIONS_FILE, 'r', encoding='utf-8') as f:
                        captions = json.load(f)
                except Exception as e:
                    print(f"Error loading captions: {e}")

            # Scan RAW_IMAGES (primary source)
            raw_dir = "RAW_IMAGES"
            if not os.path.exists(raw_dir):
                for name in ["raw_images", "RAW_images", "Raw_Images"]:
                    if os.path.exists(name):
                        raw_dir = name
                        break
            
            extensions = ("*.jpg", "*.jpeg", "*.png", "*.webp")
            filepaths = []
            if os.path.exists(raw_dir):
                for ext in extensions:
                    filepaths.extend(glob.glob(os.path.join(raw_dir, ext)))
                    filepaths.extend(glob.glob(os.path.join(raw_dir, ext.upper())))
            
            # De-duplicate and sort filenames
            filenames = sorted(list(set(os.path.basename(fp) for fp in filepaths)))
            
            images_data = []
            for name in filenames:
                entry = captions.get(name, {})
                # Backwards compatibility
                if isinstance(entry, str):
                    entry = {
                        "caption": entry,
                        "details": "",
                        "tags": [],
                        "pinned": False
                    }
                else:
                    entry = {
                        "caption": entry.get("caption", ""),
                        "details": entry.get("details", ""),
                        "tags": entry.get("tags", []),
                        "pinned": entry.get("pinned", False)
                    }
                
                images_data.append({
                    "filename": name,
                    "caption": entry["caption"],
                    "details": entry["details"],
                    "tags": entry["tags"],
                    "pinned": entry["pinned"],
                    "thumbnail": f"/images/thumbnails/{name}" if os.path.exists(f"images/thumbnails/{name}") else f"/images/{name}" if os.path.exists(f"images/{name}") else f"/RAW_IMAGES/{name}"
                })
                
            self.wfile.write(json.dumps(images_data).encode('utf-8'))
            return

        # Fallback to SimpleHTTPRequestHandler to serve static files (thumbnails, CSS, JS)
        super().do_GET()

    def do_POST(self):
        url = urlparse(self.path)
        
        # API: Save captions
        if url.path == '/api/save':
            try:
                content_length = int(self.headers['Content-Length'])
                post_data = self.rfile.read(content_length).decode('utf-8')
                data = json.loads(post_data)
                
                # Load existing captions
                captions = {}
                if os.path.exists(CAPTIONS_FILE):
                    try:
                        with open(CAPTIONS_FILE, 'r', encoding='utf-8') as f:
                            captions = json.load(f)
                    except Exception:
                        pass
                
                # Update with incoming captions (accepts dictionary of filename -> object/string)
                for filename, entry in data.items():
                    if isinstance(entry, str):
                        captions[filename] = {
                            "caption": entry.strip(),
                            "details": "",
                            "tags": [],
                            "pinned": False
                        }
                    else:
                        captions[filename] = {
                            "caption": entry.get("caption", "").strip(),
                            "details": entry.get("details", "").strip(),
                            "tags": [t.strip().lower() for t in entry.get("tags", []) if t.strip()],
                            "pinned": bool(entry.get("pinned", False))
                        }
                
                # Write back to file
                with open(CAPTIONS_FILE, 'w', encoding='utf-8') as f:
                    json.dump(captions, f, indent=2, ensure_ascii=False)
                    
                # Run the static generator script to rebuild index.html
                print("Rebuilding static photobook...")
                result = subprocess.run([sys.executable, "generate.py"], capture_output=True, text=True)
                
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({
                    "success": True, 
                    "message": "Captions saved and photobook rebuilt successfully!",
                    "build_output": result.stdout
                }).encode('utf-8'))
                
            except Exception as e:
                self.send_response(500)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({"success": False, "error": str(e)}).encode('utf-8'))
            return

        self.send_response(404)
        self.end_headers()

    def get_admin_html(self):
        return """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>PHOTOBOOK - Captions Admin</title>
  <!-- Google Fonts -->
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700&display=swap" rel="stylesheet">
  <style>
    :root {
      --bg-color: #0b0c10;
      --card-bg: rgba(20, 22, 26, 0.7);
      --text-primary: #f5f7fa;
      --text-secondary: #9aa0a6;
      --accent-color: #c5a880;
      --border-color: rgba(255, 255, 255, 0.07);
      --font-family: 'Outfit', sans-serif;
      --transition-smooth: all 0.3s cubic-bezier(0.16, 1, 0.3, 1);
    }
    
    * {
      box-sizing: border-box;
      margin: 0;
      padding: 0;
    }
    
    body {
      font-family: var(--font-family);
      background-color: var(--bg-color);
      color: var(--text-primary);
      line-height: 1.6;
      padding-top: 100px;
    }
    
    header {
      position: fixed;
      top: 0;
      left: 0;
      width: 100%;
      background: rgba(11, 12, 16, 0.85);
      backdrop-filter: blur(16px);
      -webkit-backdrop-filter: blur(16px);
      border-bottom: 1px solid var(--border-color);
      z-index: 100;
    }
    
    .header-container {
      max-width: 1120px;
      margin: 0 auto;
      padding: 20px 40px;
      display: flex;
      justify-content: space-between;
      align-items: center;
    }
    
    .logo {
      font-size: 1.25rem;
      font-weight: 700;
      letter-spacing: 0.15em;
      text-decoration: none;
      color: var(--text-primary);
      display: flex;
      align-items: center;
      gap: 8px;
    }
    
    .logo-dot {
      width: 6px;
      height: 6px;
      background-color: var(--accent-color);
      border-radius: 50%;
      box-shadow: 0 0 8px var(--accent-color);
    }
    
    .header-actions {
      display: flex;
      gap: 16px;
      align-items: center;
    }
    
    .btn {
      font-family: var(--font-family);
      font-size: 0.85rem;
      font-weight: 500;
      padding: 10px 20px;
      border-radius: 20px;
      cursor: pointer;
      text-decoration: none;
      transition: var(--transition-smooth);
      border: 1px solid transparent;
    }
    
    .btn-primary {
      background-color: var(--accent-color);
      color: #0b0c10;
    }
    
    .btn-primary:hover {
      background-color: #d6b88f;
      transform: translateY(-2px);
    }
    
    .btn-secondary {
      background-color: transparent;
      border-color: var(--border-color);
      color: var(--text-primary);
    }
    
    .btn-secondary:hover {
      background-color: rgba(255, 255, 255, 0.05);
      border-color: var(--accent-color);
    }
    
    .container {
      max-width: 1120px;
      margin: 0 auto;
      padding: 40px;
    }
    
    .page-title {
      font-size: 2rem;
      font-weight: 300;
      margin-bottom: 12px;
      letter-spacing: -0.02em;
    }
    
    .page-subtitle {
      font-size: 0.95rem;
      color: var(--text-secondary);
      margin-bottom: 40px;
    }
    
    .admin-grid {
      display: grid;
      grid-template-columns: repeat(auto-fill, minmax(340px, 1fr));
      gap: 32px;
    }
    
    .image-card {
      background-color: var(--card-bg);
      border: 1px solid var(--border-color);
      border-radius: 12px;
      overflow: hidden;
      display: flex;
      flex-direction: column;
      transition: var(--transition-smooth);
    }
    
    .image-card:hover {
      transform: translateY(-4px);
      box-shadow: 0 12px 30px rgba(0, 0, 0, 0.4);
      border-color: rgba(197, 168, 128, 0.3);
    }
    
    .thumbnail-wrapper {
      width: 100%;
      height: 220px;
      overflow: hidden;
      background-color: #121316;
      display: flex;
      align-items: center;
      justify-content: center;
      position: relative;
    }
    
    .thumbnail-wrapper img {
      width: 100%;
      height: 100%;
      object-fit: cover;
      transition: var(--transition-smooth);
    }
    
    .image-card:hover .thumbnail-wrapper img {
      transform: scale(1.05);
    }

    .card-pinned-badge {
      position: absolute;
      top: 12px;
      right: 12px;
      background: var(--accent-color);
      color: #0b0c10;
      padding: 4px 8px;
      font-size: 0.65rem;
      font-weight: 700;
      border-radius: 4px;
      letter-spacing: 0.05em;
      text-transform: uppercase;
      display: none;
    }

    .card-pinned-badge.visible {
      display: block;
    }
    
    .card-content {
      padding: 24px;
      display: flex;
      flex-direction: column;
      gap: 18px;
      flex-grow: 1;
    }
    
    .filename {
      font-size: 0.85rem;
      font-weight: 600;
      color: var(--text-primary);
      white-space: nowrap;
      overflow: hidden;
      text-overflow: ellipsis;
      border-bottom: 1px solid var(--border-color);
      padding-bottom: 8px;
    }
    
    .input-wrapper {
      display: flex;
      flex-direction: column;
      gap: 6px;
    }
    
    .field-label {
      font-size: 0.65rem;
      font-weight: 700;
      letter-spacing: 0.1em;
      color: var(--text-secondary);
      text-transform: uppercase;
    }
    
    .caption-input-text, .details-input {
      font-family: var(--font-family);
      font-size: 0.9rem;
      background-color: rgba(0, 0, 0, 0.3);
      border: 1px solid var(--border-color);
      color: var(--text-primary);
      padding: 10px 12px;
      border-radius: 6px;
      transition: var(--transition-smooth);
    }

    .details-input {
      resize: vertical;
      min-height: 80px;
    }
    
    .caption-input-text:focus, .details-input:focus {
      outline: none;
      border-color: var(--accent-color);
      background-color: rgba(0, 0, 0, 0.5);
    }

    .tags-checkbox-grid {
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 8px;
      background-color: rgba(0, 0, 0, 0.2);
      padding: 10px;
      border-radius: 6px;
      border: 1px solid var(--border-color);
    }

    .checkbox-label {
      font-size: 0.8rem;
      color: var(--text-primary);
      display: flex;
      align-items: center;
      gap: 8px;
      cursor: pointer;
      user-select: none;
    }

    .checkbox-label input[type="checkbox"] {
      cursor: pointer;
      accent-color: var(--accent-color);
    }
    
    .card-footer {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-top: 8px;
      border-top: 1px solid var(--border-color);
      padding-top: 14px;
    }
    
    .status-badge {
      font-size: 0.7rem;
      font-weight: 600;
      letter-spacing: 0.05em;
      padding: 4px 10px;
      border-radius: 4px;
      background-color: rgba(255, 255, 255, 0.05);
      color: var(--text-secondary);
    }
    
    .status-badge.dirty {
      background-color: rgba(197, 168, 128, 0.15);
      color: var(--accent-color);
    }
    
    .status-badge.saved {
      background-color: rgba(46, 204, 113, 0.15);
      color: #2ecc71;
    }
    
    /* Loading screen */
    #loading {
      display: flex;
      justify-content: center;
      align-items: center;
      height: 50vh;
      font-size: 1.2rem;
      font-weight: 300;
      color: var(--text-secondary);
    }
    
    /* Toast Notification */
    .toast {
      position: fixed;
      bottom: 30px;
      right: 30px;
      background: rgba(11, 12, 16, 0.95);
      border: 1px solid var(--accent-color);
      border-radius: 8px;
      padding: 16px 24px;
      color: var(--text-primary);
      z-index: 1000;
      transform: translateY(100px);
      opacity: 0;
      transition: var(--transition-smooth);
      box-shadow: 0 10px 30px rgba(0, 0, 0, 0.5);
    }
    
    .toast.show {
      transform: translateY(0);
      opacity: 1;
    }
  </style>
</head>
<body>
  <header>
    <div class="header-container">
      <a href="#" class="logo">
        <span class="logo-dot"></span>
        PHOTOBOOK ADMIN
      </a>
      <div class="header-actions">
        <a href="/index.html" class="btn btn-secondary" target="_blank">View Live Site</a>
        <button id="save-all-btn" class="btn btn-primary">Save All Captions</button>
      </div>
    </div>
  </header>

  <main class="container">
    <h1 class="page-title">Manage Image Captions</h1>
    <p class="page-subtitle">Add captions, details, tags, and pinning status to your photographs. Clicking "Save All" will rebuild the photobook immediately.</p>
    
    <div id="loading">Scanning portfolio and loading captions...</div>
    <div id="admin-grid" class="admin-grid" style="display: none;"></div>
  </main>

  <div id="toast" class="toast">Captions saved and photobook rebuilt!</div>

  <script>
    document.addEventListener('DOMContentLoaded', () => {
      const adminGrid = document.getElementById('admin-grid');
      const loading = document.getElementById('loading');
      const saveAllBtn = document.getElementById('save-all-btn');
      const toast = document.getElementById('toast');
      
      let initialData = {};
      let currentData = {};

      // Load images data from server API
      const loadImages = async () => {
        try {
          const response = await fetch('/api/images');
          const data = await response.json();
          
          loading.style.display = 'none';
          adminGrid.style.display = 'grid';
          adminGrid.innerHTML = '';
          
          data.forEach(img => {
            // Store deep copies of original fields
            initialData[img.filename] = {
              caption: img.caption || '',
              details: img.details || '',
              tags: Array.isArray(img.tags) ? [...img.tags] : [],
              pinned: !!img.pinned
            };
            
            currentData[img.filename] = {
              caption: img.caption || '',
              details: img.details || '',
              tags: Array.isArray(img.tags) ? [...img.tags] : [],
              pinned: !!img.pinned
            };
            
            const card = document.createElement('div');
            card.className = 'image-card';
            card.id = `card-${img.filename.replace(/[^a-zA-Z0-9]/g, '_')}`;
            
            // Thumbnail image wrapper
            const thumbWrapper = document.createElement('div');
            thumbWrapper.className = 'thumbnail-wrapper';
            const imgTag = document.createElement('img');
            imgTag.src = img.thumbnail;
            imgTag.alt = img.filename;
            thumbWrapper.appendChild(imgTag);

            // Card Pinned Badge
            const pinBadge = document.createElement('span');
            pinBadge.className = 'card-pinned-badge';
            pinBadge.textContent = 'Pinned';
            if (img.pinned) {
              pinBadge.classList.add('visible');
            }
            thumbWrapper.appendChild(pinBadge);
            card.appendChild(thumbWrapper);
            
            // Card body content
            const content = document.createElement('div');
            content.className = 'card-content';
            
            // Filename header
            const nameEl = document.createElement('div');
            nameEl.className = 'filename';
            nameEl.textContent = img.filename;
            content.appendChild(nameEl);
            
            // CAPTION (Short text input)
            const capWrapper = document.createElement('div');
            capWrapper.className = 'input-wrapper';
            const capLabel = document.createElement('label');
            capLabel.className = 'field-label';
            capLabel.textContent = 'Caption (Grid Title)';
            const capInput = document.createElement('input');
            capInput.type = 'text';
            capInput.className = 'caption-input-text';
            capInput.value = img.caption || '';
            capInput.placeholder = 'Enter photo caption title...';
            capWrapper.appendChild(capLabel);
            capWrapper.appendChild(capInput);
            content.appendChild(capWrapper);
            
            // DETAILS (Textarea)
            const detWrapper = document.createElement('div');
            detWrapper.className = 'input-wrapper';
            const detLabel = document.createElement('label');
            detLabel.className = 'field-label';
            detLabel.textContent = 'Details / Story';
            const detInput = document.createElement('textarea');
            detInput.className = 'details-input';
            detInput.value = img.details || '';
            detInput.placeholder = 'Enter a detailed story or context...';
            detWrapper.appendChild(detLabel);
            detWrapper.appendChild(detInput);
            content.appendChild(detWrapper);
            
            // TAGS (Checkboxes)
            const tagsWrapper = document.createElement('div');
            tagsWrapper.className = 'input-wrapper';
            const tagsLabel = document.createElement('label');
            tagsLabel.className = 'field-label';
            tagsLabel.textContent = 'Categories';
            
            const tagsGrid = document.createElement('div');
            tagsGrid.className = 'tags-checkbox-grid';
            
            const availableTags = ['nature', 'urban', 'minimalist', 'portrait'];
            const checkboxElements = [];
            
            availableTags.forEach(tag => {
              const label = document.createElement('label');
              label.className = 'checkbox-label';
              
              const chk = document.createElement('input');
              chk.type = 'checkbox';
              chk.value = tag;
              chk.checked = currentData[img.filename].tags.includes(tag);
              checkboxElements.push(chk);
              
              label.appendChild(chk);
              label.appendChild(document.createTextNode(' ' + tag.charAt(0).toUpperCase() + tag.slice(1)));
              tagsGrid.appendChild(label);
            });
            
            tagsWrapper.appendChild(tagsLabel);
            tagsWrapper.appendChild(tagsGrid);
            content.appendChild(tagsWrapper);
            
            // PINNED (Checkbox)
            const pinWrapper = document.createElement('div');
            pinWrapper.className = 'input-wrapper';
            const pinLabel = document.createElement('label');
            pinLabel.className = 'checkbox-label';
            const pinChk = document.createElement('input');
            pinChk.type = 'checkbox';
            pinChk.checked = currentData[img.filename].pinned;
            pinLabel.appendChild(pinChk);
            pinLabel.appendChild(document.createTextNode(' Pin to top of gallery'));
            pinWrapper.appendChild(pinLabel);
            content.appendChild(pinWrapper);

            // Save status badge
            const badge = document.createElement('span');
            badge.className = 'status-badge';
            badge.textContent = 'Saved';
            
            // Dirty checking logic
            const checkDiff = () => {
              const init = initialData[img.filename];
              const cur = currentData[img.filename];
              
              const tagsEqual = init.tags.length === cur.tags.length && 
                                init.tags.every(t => cur.tags.includes(t)) &&
                                cur.tags.every(t => init.tags.includes(t));
                                
              const modified = init.caption !== cur.caption ||
                               init.details !== cur.details ||
                               init.pinned !== cur.pinned ||
                               !tagsEqual;
              
              if (modified) {
                badge.textContent = 'Draft';
                badge.className = 'status-badge dirty';
              } else {
                badge.textContent = 'Saved';
                badge.className = 'status-badge';
              }

              // Toggle thumbnail pinned visual badge
              if (cur.pinned) {
                pinBadge.classList.add('visible');
              } else {
                pinBadge.classList.remove('visible');
              }
            };
            
            // Bind input changes
            capInput.addEventListener('input', (e) => {
              currentData[img.filename].caption = e.target.value;
              checkDiff();
            });
            
            detInput.addEventListener('input', (e) => {
              currentData[img.filename].details = e.target.value;
              checkDiff();
            });

            checkboxElements.forEach(chk => {
              chk.addEventListener('change', () => {
                const selectedTags = checkboxElements.filter(c => c.checked).map(c => c.value);
                currentData[img.filename].tags = selectedTags;
                checkDiff();
              });
            });

            pinChk.addEventListener('change', (e) => {
              currentData[img.filename].pinned = e.target.checked;
              checkDiff();
            });
            
            // Card footer
            const footer = document.createElement('div');
            footer.className = 'card-footer';
            footer.appendChild(badge);
            content.appendChild(footer);
            
            card.appendChild(content);
            adminGrid.appendChild(card);
          });
        } catch (e) {
          loading.textContent = 'Failed to load portfolio images. Check server connection.';
          console.error(e);
        }
      };

      // Save all captions/metadata to server
      const saveAll = async () => {
        saveAllBtn.disabled = true;
        saveAllBtn.textContent = 'Saving...';
        
        // Find changes
        const payload = {};
        let changeCount = 0;
        
        for (const filename in currentData) {
          const init = initialData[filename];
          const cur = currentData[filename];
          
          const tagsEqual = init.tags.length === cur.tags.length && 
                            init.tags.every(t => cur.tags.includes(t)) &&
                            cur.tags.every(t => init.tags.includes(t));
                            
          const modified = init.caption !== cur.caption ||
                           init.details !== cur.details ||
                           init.pinned !== cur.pinned ||
                           !tagsEqual;
                           
          if (modified) {
            payload[filename] = cur;
            changeCount++;
          }
        }
        
        if (changeCount === 0) {
          showToast('No modifications to save.');
          saveAllBtn.disabled = false;
          saveAllBtn.textContent = 'Save All Captions';
          return;
        }
        
        try {
          const response = await fetch('/api/save', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
          });
          
          const result = await response.json();
          if (result.success) {
            showToast('Portfolio metadata saved and site successfully rebuilt!');
            
            // Commit current state to initial state
            for (const filename in payload) {
              initialData[filename] = {
                caption: payload[filename].caption,
                details: payload[filename].details,
                tags: [...payload[filename].tags],
                pinned: payload[filename].pinned
              };
              
              // Reset status badges to "Saved"
              const cardId = `card-${filename.replace(/[^a-zA-Z0-9]/g, '_')}`;
              const card = document.getElementById(cardId);
              if (card) {
                const badge = card.querySelector('.status-badge');
                if (badge) {
                  badge.textContent = 'Saved';
                  badge.className = 'status-badge';
                }
              }
            }
          } else {
            showToast('Error saving: ' + (result.error || 'Unknown error'));
          }
        } catch (e) {
          showToast('Network error saving captions.');
          console.error(e);
        } finally {
          saveAllBtn.disabled = false;
          saveAllBtn.textContent = 'Save All Captions';
        }
      };

      const showToast = (message) => {
        toast.textContent = message;
        toast.classList.add('show');
        setTimeout(() => {
          toast.classList.remove('show');
        }, 3000);
      };

      saveAllBtn.addEventListener('click', saveAll);
      loadImages();
    });
  </script>
</body>
</html>
"""

def main():
    server_address = ('', PORT)
    httpd = HTTPServer(server_address, AdminHTTPRequestHandler)
    print(f"==================================================")
    print(f"PHOTOBOOK CAPTION ADMIN SERVER STARTED")
    print(f"Access it here: http://localhost:{PORT}/admin")
    print(f"Press Ctrl+C to stop the server.")
    print(f"==================================================")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nStopping admin server...")
        httpd.server_close()
        print("Server stopped.")

if __name__ == '__main__':
    main()
