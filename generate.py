#!/usr/bin/env python3
import os
import glob
import html
import sys
import re
from PIL import Image, ImageOps
from PIL.ExifTags import TAGS

# Mock metadata dictionary to preserve beautiful EXIF values for demo assets
MOCK_METADATA = {
    "forest": {
        "title": "Morning Sanctuary",
        "location": "Kyoto, Japan",
        "camera": "Fujifilm X-T5",
        "lens": "XF 18-55mm f/2.8-4 R",
        "exif": "f/4.0 • 1/125s • ISO 160",
        "category": "nature"
    },
    "street": {
        "title": "Neon Whispers",
        "location": "Shinjuku, Tokyo",
        "camera": "Sony A7R V",
        "lens": "FE 35mm f/1.4 GM",
        "exif": "f/1.4 • 1/160s • ISO 800",
        "category": "urban"
    },
    "neon": {
        "title": "Neon Whispers",
        "location": "Shinjuku, Tokyo",
        "camera": "Sony A7R V",
        "lens": "FE 35mm f/1.4 GM",
        "exif": "f/1.4 • 1/160s • ISO 800",
        "category": "urban"
    },
    "arch": {
        "title": "Geometric Symphony",
        "location": "Berlin, Germany",
        "camera": "Leica Q3",
        "lens": "Summilux 28mm f/1.7",
        "exif": "f/8.0 • 1/500s • ISO 100",
        "category": "minimalist"
    },
    "raindrops": {
        "title": "Liquid Crystals",
        "location": "Oregon, USA",
        "camera": "Canon EOS R5",
        "lens": "RF 100mm f/2.8L Macro",
        "exif": "f/5.6 • 1/200s • ISO 320",
        "category": "nature"
    },
    "dunes": {
        "title": "Sands of Time",
        "location": "Sahara, Morocco",
        "camera": "Sony A7R V",
        "lens": "FE 70-200mm f/2.8 GM II",
        "exif": "f/8.0 • 1/320s • ISO 100",
        "category": "minimalist"
    },
    "portrait": {
        "title": "The Sea Captain",
        "location": "Reykjavik, Iceland",
        "camera": "Nikon Z9",
        "lens": "NIKKOR Z 85mm f/1.2 S",
        "exif": "f/1.2 • 1/250s • ISO 64",
        "category": "portrait"
    },
    "captain": {
        "title": "The Sea Captain",
        "location": "Reykjavik, Iceland",
        "camera": "Nikon Z9",
        "lens": "NIKKOR Z 85mm f/1.2 S",
        "exif": "f/1.2 • 1/250s • ISO 64",
        "category": "portrait"
    }
}

KEYWORD_CATEGORIES = {
    "nature": ["nature", "forest", "leaf", "droplet", "lake", "mountain", "landscape", "tree", "plant", "garden", "flower", "sky", "cloud", "green"],
    "urban": ["urban", "street", "city", "neon", "road", "night", "traffic", "car", "subway", "metro", "tokyo", "shinjuku", "signboard"],
    "minimalist": ["minimalist", "minimal", "architecture", "arch", "abstract", "shadow", "dune", "line", "geometry", "concrete", "sand"],
    "portrait": ["portrait", "people", "man", "woman", "captain", "face", "self", "child", "elderly"]
}

def determine_category(filename):
    fn_lower = filename.lower()
    for cat, keywords in KEYWORD_CATEGORIES.items():
        for kw in keywords:
            if kw in fn_lower:
                return cat
    return "nature" # Default fallback

def get_clean_title(filename):
    # Strip extension
    base = os.path.splitext(filename)[0]
    # Strip the keyword "pinned" case-insensitively, along with any adjoining dashes or underscores
    base_clean = re.sub(r'(?i)[-_]?pinned[-_]?', '', base).strip()
    # Replace dashes/underscores with space
    title = base_clean.replace("_", " ").replace("-", " ")
    title = " ".join(title.split()) # normalize double spaces
    title = title.title()
    
    # Truncate title if it is too long (limit to 24 characters)
    if len(title) > 24:
        title = title[:21] + "..."
    return title

def get_exif_data(filepath):
    try:
        img = Image.open(filepath)
        exif = img.getexif()
        exif_info = {}
        
        # Load standard EXIF tags
        for tag_id, value in exif.items():
            tag = TAGS.get(tag_id, tag_id)
            exif_info[tag] = value
            
        # Check Sub-IFDs for camera detailed metadata
        for ifd_id in [0x8769, 0xa405]:
            try:
                ifd = exif.get_ifd(ifd_id)
                for tag_id, value in ifd.items():
                    tag = TAGS.get(tag_id, tag_id)
                    exif_info[tag] = value
            except Exception:
                pass
                
        camera = exif_info.get("Model", "Digital Camera").strip()
        lens = exif_info.get("LensModel", "Standard Lens").strip()
        
        # Clean defaults if empty/placeholder
        if not camera or camera == "Unknown Camera":
            camera = "Digital Camera"
        if not lens or lens == "Unknown Lens":
            lens = "Standard Lens"
            
        # Format exposure
        f_number = exif_info.get("FNumber")
        exposure_time = exif_info.get("ExposureTime")
        iso = exif_info.get("ISOSpeedRatings")
        
        exif_parts = []
        if f_number:
            try:
                exif_parts.append(f"f/{float(f_number):.1f}")
            except (ValueError, TypeError):
                pass
        if exposure_time:
            try:
                exposure_time = float(exposure_time)
                if exposure_time < 1.0:
                    den = int(round(1.0 / exposure_time))
                    exif_parts.append(f"1/{den}s")
                else:
                    exif_parts.append(f"{exposure_time}s")
            except (ValueError, TypeError):
                pass
        if iso:
            exif_parts.append(f"ISO {iso}")
            
        exif_str = " • ".join(exif_parts) if exif_parts else "N/A"
            
        return camera, lens, exif_str
    except Exception as e:
        print(f"Error parsing EXIF for {filepath}: {e}", file=sys.stderr)
        return "Digital Camera", "Standard Lens", "N/A"

HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>PHOTOBOOK</title>
  <!-- SEO Meta Tags -->
  <meta name="description" content="A premium and minimalist photography portfolio showcasing fine art photography in its native aspect ratios. Featuring nature, urban, minimalist, and portrait works.">
  <meta name="keywords" content="photography, portfolio, minimalist, fine art, landscape, portrait, urban, light mode">
  <meta name="author" content="Lens & Light">
  <!-- Open Graph / Facebook -->
  <meta property="og:type" content="website">
  <meta property="og:title" content="PHOTOBOOK">
  <meta property="og:description" content="A premium and minimalist photography portfolio showcasing fine art photography in its native aspect ratios.">
  <!-- Google Fonts -->
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700&display=swap" rel="stylesheet">
  <!-- Stylesheet -->
  <link rel="stylesheet" href="styles.css">
  <!-- Content Security Policy -->
  <meta http-equiv="Content-Security-Policy" content="default-src 'self'; img-src 'self' data:; style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; font-src 'self' https://fonts.gstatic.com; script-src 'self';">
</head>
<body class="light-theme">
  <!-- Sticky Header & Navigation -->
  <header id="main-header" class="glass-effect">
    <div class="header-container">
      <a href="#" class="logo" id="logo" aria-label="Photobook Home">
        <span class="logo-dot"></span>
        PHOTOBOOK
      </a>
      
      <nav id="categories-nav" aria-label="Photo Categories">
        <ul class="filter-list">
          <li><button class="filter-btn active" data-filter="all" id="filter-all">All</button></li>
          <li><button class="filter-btn" data-filter="nature" id="filter-nature">Nature</button></li>
          <li><button class="filter-btn" data-filter="urban" id="filter-urban">Urban</button></li>
          <li><button class="filter-btn" data-filter="minimalist" id="filter-minimalist">Minimalist</button></li>
          <li><button class="filter-btn" data-filter="portrait" id="filter-portrait">Portrait</button></li>
        </ul>
      </nav>

      <div class="theme-switch-container">
        <button id="theme-toggle" class="theme-toggle-btn" aria-label="Toggle light and dark theme">
          <svg class="sun-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <circle cx="12" cy="12" r="4"></circle>
            <path d="M12 2v2M12 20v2M4.93 4.93l1.41 1.41M17.66 17.66l1.41 1.41M2 12h2M20 12h2M6.34 17.66l-1.41 1.41M19.07 4.93l-1.41 1.41"></path>
          </svg>
          <svg class="moon-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <path d="M12 3a6 6 0 0 0 9 9 9 9 0 1 1-9-9Z"></path>
          </svg>
        </button>
      </div>
    </div>
  </header>

  <!-- Main Content Area -->
  <main id="main-content">
    <div class="gallery-wrapper">
      <section class="gallery" id="photo-gallery" aria-label="Photography Grid">
{gallery_items}
      </section>
    </div>
  </main>

  <!-- Footer Section -->
  <footer id="main-footer">
    <div class="footer-container">
      <p class="copyright">&copy; 2026 PHOTOBOOK. All rights reserved.</p>
      <p class="footer-tagline">Capturing raw moments in native proportions.</p>
    </div>
  </footer>

  <!-- Lightbox Modal -->
  <div id="lightbox" class="lightbox-modal" role="dialog" aria-hidden="true" aria-label="Image Lightbox Viewer">
    <button id="lightbox-close" class="lightbox-close-btn" aria-label="Close lightbox">
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
        <line x1="18" y1="6" x2="6" y2="18"></line>
        <line x1="6" y1="6" x2="18" y2="18"></line>
      </svg>
    </button>
    
    <button id="lightbox-prev" class="lightbox-nav-btn prev" aria-label="Previous image">
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
        <polyline points="15 18 9 12 15 6"></polyline>
      </svg>
    </button>

    <div class="lightbox-scroll-container">
      <!-- First Fold (Full Viewport Image) -->
      <div class="lightbox-first-fold">
        <div class="lightbox-img-wrapper">
          <img id="lightbox-img" src="" alt="">
        </div>
        
        <!-- Subtle pulsing scroll indicator -->
        <div id="lightbox-scroll-arrow" class="lightbox-scroll-arrow" aria-label="Scroll down for details">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
            <polyline points="6 9 12 15 18 9"></polyline>
          </svg>
        </div>
      </div>
      
      <!-- Second Fold (Caption & Metadata) -->
      <div class="lightbox-second-fold">
        <div class="lightbox-details-container">
          <div class="lightbox-caption-section">
            <span class="details-label">CAPTION</span>
            <p id="lightbox-caption" class="lightbox-caption-text"></p>
          </div>
          
          <!-- Meta Information overlay panel -->
          <div id="lightbox-meta" class="lightbox-meta-panel glass-effect">
            <div class="meta-main-info">
              <span id="meta-category" class="meta-tag"></span>
              <h2 id="meta-title" class="meta-photo-title"></h2>
              <p id="meta-location" class="meta-photo-loc"></p>
            </div>
            <hr class="meta-separator">
            <div class="meta-tech-details">
              <div class="tech-item">
                <span class="tech-label">CAMERA</span>
                <span id="meta-camera" class="tech-val"></span>
              </div>
              <div class="tech-item">
                <span class="tech-label">LENS</span>
                <span id="meta-lens" class="tech-val"></span>
              </div>
              <div class="tech-item">
                <span class="tech-label">EXIF</span>
                <span id="meta-exif" class="tech-val"></span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <button id="lightbox-next" class="lightbox-nav-btn next" aria-label="Next image">
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
        <polyline points="9 18 15 12 9 6"></polyline>
      </svg>
    </button>
  </div>

  <!-- Javascript Bundle -->
  <script src="app.js"></script>
</body>
</html>
"""

def generate_html_items(image_list):
    blocks = []
    for i, item in enumerate(image_list):
        safe_title = html.escape(item["title"])
        safe_location = html.escape(item["location"])
        safe_camera = html.escape(item["camera"])
        safe_lens = html.escape(item["lens"])
        safe_exif = html.escape(item["exif"])
        safe_category = html.escape(item["category"])
        safe_original = html.escape(item["original_path"])
        safe_thumb = html.escape(item["thumb_path"])
        safe_caption = html.escape(item.get("caption", ""))
        
        cat_display = safe_category.capitalize()
        
        # Render dynamic pinned badge if the photo is pinned
        pinned_badge = ""
        if item["is_pinned"]:
            pinned_badge = """            <div class="pinned-badge" aria-label="Pinned Photo">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
                <line x1="12" y1="2" x2="12" y2="13"></line>
                <path d="M12 13H5l2-3V5a2 2 0 0 1 2-2h6a2 2 0 0 1 2 2v5l2 3h-7z"></path>
                <line x1="12" y1="13" x2="12" y2="22"></line>
              </svg>
            </div>"""
        
        block = f"""        <!-- Photo Item: {safe_title} -->
        <article class="gallery-item" data-category="{safe_category}" id="item-{i}"
                 data-title="{safe_title}"
                 data-location="{safe_location}"
                 data-camera="{safe_camera}"
                 data-lens="{safe_lens}"
                 data-exif="{safe_exif}"
                 data-original="{safe_original}"
                 data-caption="{safe_caption}">
          <div class="image-container">
            {pinned_badge}
            <img src="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 1 1'%3E%3C/svg%3E" data-src="{safe_thumb}" class="lazy-img" alt="{safe_title} photography by PHOTOBOOK">
            <div class="hover-overlay">
              <div class="photo-info">
                <span class="photo-cat">{cat_display}</span>
                <h2 class="photo-title">{safe_title}</h2>
                <span class="photo-loc">{safe_location}</span>
              </div>
              <div class="zoom-indicator">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                  <path d="M15 3h6v6M9 21H3v-6M21 3l-7 7M3 21l7-7"></path>
                </svg>
              </div>
            </div>
          </div>
        </article>"""
        blocks.append(block)
    return "\n\n".join(blocks)

def main():
    import json
    captions = {}
    if os.path.exists("captions.json"):
        try:
            with open("captions.json", "r", encoding="utf-8") as f:
                captions = json.load(f)
        except Exception as e:
            print(f"⚠ Failed to load captions.json: {e}", file=sys.stderr)

    raw_dir = "RAW_IMAGES"
    if not os.path.exists(raw_dir):
        # Fallback in case of case variation
        for name in ["raw_images", "RAW_images", "Raw_Images"]:
            if os.path.exists(name):
                raw_dir = name
                break
    if not os.path.exists(raw_dir):
        print(f"Error: RAW_IMAGES directory not found.")
        sys.exit(1)
        
    image_dir = "images"
    os.makedirs(image_dir, exist_ok=True)
    
    thumb_dir = os.path.join(image_dir, "thumbnails")
    os.makedirs(thumb_dir, exist_ok=True)
    
    print(f"Scanning original images from: {raw_dir}...")
    
    # Supported image extensions
    extensions = ("*.jpg", "*.jpeg", "*.png", "*.webp")
    filepaths = []
    for ext in extensions:
        filepaths.extend(glob.glob(os.path.join(raw_dir, ext)))
        filepaths.extend(glob.glob(os.path.join(raw_dir, ext.upper())))
        
    filepaths = list(set(filepaths))
    
    image_list = []
    for fp in filepaths:
        filename = os.path.basename(fp)
        
        # Path to compressed original image
        compressed_path = os.path.join(image_dir, filename)
        
        # Compress original image if needed
        try:
            if not os.path.exists(compressed_path) or os.path.getmtime(fp) > os.path.getmtime(compressed_path):
                img = Image.open(fp)
                # Apply EXIF rotation to correctly orient portrait images
                img = ImageOps.exif_transpose(img)
                # For JPG optimization, convert RGBA/P formats to standard RGB
                if img.mode in ("RGBA", "P") and filename.lower().endswith((".jpg", ".jpeg")):
                    img = img.convert("RGB")
                # Save compressed original image at 70% quality
                img.save(compressed_path, quality=70, optimize=True)
                print(f"✓ Generated compressed original image for: {filename}")
        except Exception as e:
            print(f"⚠ Failed to compress original image {filename}: {e}", file=sys.stderr)
            
        # Build thumbnail
        thumb_path = os.path.join(thumb_dir, filename)
        try:
            # Use the compressed image to generate thumbnail if it exists, otherwise fallback to raw
            source_for_thumb = compressed_path if os.path.exists(compressed_path) else fp
            if not os.path.exists(thumb_path) or os.path.getmtime(source_for_thumb) > os.path.getmtime(thumb_path):
                img = Image.open(source_for_thumb)
                # Apply EXIF rotation (already done for compressed, but safe to repeat or do if fallback)
                img = ImageOps.exif_transpose(img)
                img.thumbnail((800, 800))
                # For JPG optimization, convert RGBA/P formats to standard RGB
                if img.mode in ("RGBA", "P") and filename.lower().endswith((".jpg", ".jpeg")):
                    img = img.convert("RGB")
                img.save(thumb_path, quality=70, optimize=True)
                print(f"✓ Generated compressed thumbnail for: {filename}")
        except Exception as e:
            print(f"⚠ Failed to generate thumbnail for {filename}: {e}", file=sys.stderr)
            
        mtime = os.path.getmtime(fp)
        is_pinned = "pinned" in filename.lower()
        
        # Match mock profile if available to keep demo look professional
        matched_mock = None
        for key, mock_data in MOCK_METADATA.items():
            if key in filename.lower():
                matched_mock = mock_data
                break
                
        if matched_mock:
            title = matched_mock["title"]
            location = matched_mock["location"]
            camera = matched_mock["camera"]
            lens = matched_mock["lens"]
            exif_str = matched_mock["exif"]
            category = matched_mock["category"]
        else:
            title = get_clean_title(filename)
            location = "Local Capture"
            camera, lens, exif_str = get_exif_data(fp)
            category = determine_category(filename)
            
        image_list.append({
            "filename": filename,
            "original_path": f"images/{filename}",
            "thumb_path": f"images/thumbnails/{filename}",
            "title": title,
            "location": location,
            "camera": camera,
            "lens": lens,
            "exif": exif_str,
            "category": category,
            "mtime": mtime,
            "is_pinned": is_pinned,
            "caption": captions.get(filename, "")
        })
        
    # Sort files: pinned files go to the top, then sorted by mtime descending
    image_list.sort(key=lambda x: (not x["is_pinned"], -x["mtime"]))
    
    print(f"Total processed images: {len(image_list)}")
    
    # Generate HTML items blocks
    gallery_items_str = generate_html_items(image_list)
    
    # Fill the template
    full_html = HTML_TEMPLATE.format(gallery_items=gallery_items_str)
    
    # Overwrite index.html safely
    try:
        with open("index.html", "w", encoding="utf-8") as f:
            f.write(full_html)
        print("✓ Successfully updated index.html with latest images sorted newest-first!")
    except Exception as e:
        print(f"Error writing index.html: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
