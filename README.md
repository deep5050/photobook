# 🖼️ Photobook: Premium Minimalist Photography Portfolio Generator

Photobook is a premium, minimalist photography portfolio builder designed to showcase fine art photography in its native aspect ratios. It features a local CMS admin dashboard, automated image optimization, EXIF metadata extraction, and dynamic client-side color histograms.

Since it generates a completely static site (`index.html`), anyone can fork this repository, drop in their photos, and instantly deploy a gorgeous portfolio site to GitHub Pages, Netlify, or Vercel.

---

## ✨ Core Features

* 🖼️ **Native Proportions & Aspect Ratios**: No square-cropping or forced dimensions. Landscape and portrait photos are displayed as originally shot.
* 🌓 **Aesthetic Theme Switcher**: Fluid transitions between light and dark mode with persistent user choice saving via `localStorage`.
* 🏷️ **Categorized Navigation**: Beautiful filter controls for Nature, Urban, Minimalist, and Portrait categories.
* 🔍 **Interactive Lightbox Modal**: Implements navigation transitions, touch-friendly navigation, background dimming, and deep scrollable details.
* 📊 **Real-time Color Histograms**: Dynamically computes and draws RGB color profile distributions directly onto HTML5 canvases in the lightbox.
* ⚡ **Lazy Loading**: Pre-loads images dynamically using the high-performance `IntersectionObserver` API to optimize bandwidth and page speed.
* ⚙️ **Automated Asset Compiler**: Rotates (correcting portrait orientations via EXIF), compresses, and structures high-resolution photos into optimized web formats and thumbnails.
* 💻 **Admin Dashboard CMS**: Local web-based administration panel to edit captions, write stories, manage tags, and pin favorite photos to the top. Saving automatically rebuilds the site.

---

## 📋 Prerequisites

To run the builder and local dashboard, you only need **Python 3.x** and the **Pillow** image processing library:

```bash
pip install Pillow
```

---

## 🚀 Step-by-Step Setup Guide

Follow these steps to build your own personalized photobook:

### Step 1: Fork & Clone the Repository
Fork this repository to your GitHub account and clone it locally:
```bash
git clone https://github.com/YOUR_USERNAME/photobook.git
cd photobook
```

### Step 2: Add Your Raw Photos
Create a directory named `RAW_IMAGES` at the root of the project:
```bash
mkdir RAW_IMAGES
```
Place your original, high-resolution photo files (supports `.jpg`, `.jpeg`, `.png`, `.webp` format) inside this new directory. 

> [!IMPORTANT]  
> The `RAW_IMAGES` directory is automatically excluded from Git commits via `.gitignore`. This keeps your repository size small and clean, preventing slow push/pull times. Only the web-optimized images in `images/` will be pushed.

### Step 3: Run the Admin Server Dashboard
To manage details, write captions, select tags, or pin images, run the local backend server:
```bash
make backend
```
*(If `make` is not installed on your system, run: `python3 admin_server.py`)*

Open your browser and navigate to:  
👉 **[http://localhost:8080/admin](http://localhost:8080/admin)**

### Step 4: Write Stories & Save Captions
In the Admin Dashboard, you can edit metadata for all scanned images:
* **Caption**: The title that appears over the photo grid.
* **Details / Story**: A markdown-compatible description, memory, or backstory associated with the photo.
* **Categories**: Checkbox tags (Nature, Urban, Minimalist, Portrait) to organize filtering.
* **Pin to top**: Check this to highlight and pin particular images to the beginning of the gallery.

Click **Save All Captions** in the upper right. This saves your choices to `captions.json` and automatically compiles `index.html`.

### Step 5: Build the Static Website Manually
If you ever want to recompile the site directly from the terminal without using the admin UI, simply run:
```bash
make build
```
*(Alternative: `python3 generate.py`)*

This script will:
1. Scan your `RAW_IMAGES` directory.
2. Auto-rotate, scale down, and compress images into `images/` (optimized original quality) and `images/thumbnails/` (max 800x800).
3. Extract EXIF details (shutter speed, ISO, aperture, camera, lens) to show in the lightbox.
4. Update `index.html` with your captions, categories, and sorted layout.

### Step 6: Deploy Your Portfolio
Because the generated website is entirely static, it can be hosted for free on a wide variety of services.

#### Deploying on GitHub Pages:
1. Push your updated files (including `index.html`, `styles.css`, `app.js`, `captions.json`, and the optimized `images/` directory) to your GitHub repository:
   ```bash
   git add index.html captions.json images/ styles.css app.js
   git commit -m "Configure and compile photobook portfolio"
   git push origin main
   ```
2. Go to your repository settings on GitHub.
3. Click on **Pages** in the left sidebar.
4. Select **Deploy from a branch** under Source, pick the `main` branch and `/ (root)` folder, then hit Save.
5. Within a minute, your photobook will be live at `https://YOUR_USERNAME.github.io/photobook/`!

#### Alternative Hosting:
Drag and drop your project folder containing `index.html`, `styles.css`, `app.js`, `captions.json`, and `images/` directly into **Netlify** or **Vercel**.

---

## 🛠️ Makefile Commands

For easy command execution, a `Makefile` is included:

| Command | Description |
| :--- | :--- |
| `make backend` | Starts the local HTTP admin dashboard server on port `8080` |
| `make build` | Compresses raw images, parses EXIF/captions, and compiles the static site |
| `make clean` | Removes all generated web images, thumbnails, and the built index.html |
| `make help` | Displays the available make commands |

---

## 🎨 Fine-Tuning Categories (Optional)
If you do not specify custom tags in the admin panel, the compiler (`generate.py`) determines categories automatically based on filename keywords:
* **Nature**: `nature`, `forest`, `leaf`, `droplet`, `lake`, `mountain`, `landscape`, `tree`, `plant`, `garden`, `flower`, `sky`, `cloud`, `green`
* **Urban**: `urban`, `street`, `city`, `neon`, `road`, `night`, `traffic`, `car`, `subway`, `metro`, `tokyo`, `shinjuku`, `signboard`
* **Minimalist**: `minimalist`, `minimal`, `architecture`, `arch`, `abstract`, `shadow`, `dune`, `line`, `geometry`, `concrete`, `sand`
* **Portrait**: `portrait`, `people`, `man`, `woman`, `captain`, `face`, `self`, `child`, `elderly`

You can edit the `KEYWORD_CATEGORIES` dictionary inside `generate.py` to customize these rules.
