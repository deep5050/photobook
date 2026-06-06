/**
 * Lens & Light / Aperture - Photography Portfolio Logic
 * Fully compliant with Vanilla JS DOM Manipulation security rules.
 */

document.addEventListener('DOMContentLoaded', () => {
  // --- DOM Elements Cache ---
  const body = document.body;
  const themeToggle = document.getElementById('theme-toggle');
  const filterButtons = document.querySelectorAll('.filter-btn');
  const galleryItems = document.querySelectorAll('.gallery-item');
  
  // Lightbox elements
  const lightbox = document.getElementById('lightbox');
  const lightboxImg = document.getElementById('lightbox-img');
  const lightboxClose = document.getElementById('lightbox-close');
  const lightboxPrev = document.getElementById('lightbox-prev');
  const lightboxNext = document.getElementById('lightbox-next');
  
  // Lightbox scroll container and caption elements
  const lightboxScrollContainer = lightbox ? lightbox.querySelector('.lightbox-scroll-container') : null;
  const lightboxScrollArrow = document.getElementById('lightbox-scroll-arrow');
  const lightboxCaption = document.getElementById('lightbox-caption');
  const lightboxDetails = document.getElementById('lightbox-details');
  const lightboxHistogramCanvas = document.getElementById('lightbox-histogram-canvas');
  
  // Lightbox EXIF elements
  const metaCategory = document.getElementById('meta-category');
  const metaTitle = document.getElementById('meta-title');
  const metaLocation = document.getElementById('meta-location');
  const metaCamera = document.getElementById('meta-camera');
  const metaLens = document.getElementById('meta-lens');
  const metaExif = document.getElementById('meta-exif');

  // --- State Variables ---
  let activeFilter = 'all';
  let filteredItems = Array.from(galleryItems); // Holds visible items under the current filter
  let currentImgIndex = 0; // Index of the currently opened item in the filtered list

  // ==========================================================================
  // Theme Toggle (Dark / Light Mode)
  // ==========================================================================
  const initTheme = () => {
    const savedTheme = localStorage.getItem('theme');
    if (savedTheme) {
      body.className = savedTheme;
    } else {
      // Default to light theme
      body.classList.add('light-theme');
    }
  };

  const toggleTheme = () => {
    if (body.classList.contains('dark-theme')) {
      body.classList.remove('dark-theme');
      body.classList.add('light-theme');
      localStorage.setItem('theme', 'light-theme');
    } else {
      body.classList.remove('light-theme');
      body.classList.add('dark-theme');
      localStorage.setItem('theme', 'dark-theme');
    }
  };

  if (themeToggle) {
    themeToggle.addEventListener('click', toggleTheme);
  }

  // ==========================================================================
  // Photo Category Filtering
  // ==========================================================================
  const filterGallery = (category) => {
    activeFilter = category;
    
    // Clear and build the list of visible items
    filteredItems = [];
    
    galleryItems.forEach(item => {
      const itemCategoryAttr = item.getAttribute('data-category') || '';
      const categories = itemCategoryAttr.split(',').map(c => c.trim().toLowerCase());
      
      // Reset animation classes
      item.classList.remove('fade-in-item');
      
      if (category === 'all' || categories.includes(category.toLowerCase())) {
        item.classList.remove('filtered-out');
        // Force reflow to restart CSS keyframe animation
        void item.offsetWidth; 
        item.classList.add('fade-in-item');
        filteredItems.push(item);
      } else {
        item.classList.add('filtered-out');
      }
    });
  };

  filterButtons.forEach(btn => {
    btn.addEventListener('click', (e) => {
      // Manage active visual state on buttons
      filterButtons.forEach(b => b.classList.remove('active'));
      e.currentTarget.classList.add('active');
      
      const filterValue = e.currentTarget.getAttribute('data-filter') || 'all';
      filterGallery(filterValue);
    });
  });

  // ==========================================================================
  // Lightbox Modal Functionality
  // ==========================================================================
  let activeClickedItem = null;

  const setActiveClickBorder = (item) => {
    if (activeClickedItem) {
      activeClickedItem.classList.remove('active-click');
    }
    activeClickedItem = item;
    if (activeClickedItem) {
      activeClickedItem.classList.add('active-click');
    }
  };

  const updateLightboxContent = (index, deferBorderHighlight = false) => {
    if (index < 0 || index >= filteredItems.length) return;
    currentImgIndex = index;
    const currentItem = filteredItems[currentImgIndex];
    
    // Highlight the active item in the grid if not deferred
    if (!deferBorderHighlight) {
      setActiveClickBorder(currentItem);
    }
    
    const imgEl = currentItem.querySelector('img');
    if (!imgEl) return;
    
    // Reset scroll position to top when updating content
    if (lightboxScrollContainer) {
      lightboxScrollContainer.scrollTop = 0;
    }
    
    // Safety check & assign properties (no innerHTML to avoid XSS)
    // Use data-original for high quality image, fall back to thumbnail data-src or imgEl.src
    lightboxImg.src = currentItem.getAttribute('data-original') || imgEl.getAttribute('data-src') || imgEl.src;
    lightboxImg.alt = imgEl.alt || 'Photography showcase';
    
    // Populate text details safely
    if (metaCategory) {
      const catAttr = currentItem.getAttribute('data-category') || '';
      metaCategory.textContent = catAttr.split(',').map(t => t.trim()).filter(t => t).map(t => `#${t}`).join(' ');
    }
    if (metaTitle) {
      metaTitle.textContent = currentItem.getAttribute('data-title') || 'Untitled';
    }
    if (metaLocation) {
      metaLocation.textContent = currentItem.getAttribute('data-location') || '';
    }
    if (metaCamera) {
      metaCamera.textContent = currentItem.getAttribute('data-camera') || 'N/A';
    }
    if (metaLens) {
      metaLens.textContent = currentItem.getAttribute('data-lens') || 'N/A';
    }
    if (metaExif) {
      metaExif.textContent = currentItem.getAttribute('data-exif') || 'N/A';
    }
    if (lightboxDetails) {
      lightboxDetails.textContent = currentItem.getAttribute('data-details') || '';
    }
    
    // Populate caption and handle scroll arrow visibility
    const caption = currentItem.getAttribute('data-caption') || '';
    const title = currentItem.getAttribute('data-title') || 'Untitled';
    if (lightboxCaption) {
      lightboxCaption.textContent = caption || title;
    }
    
    if (lightboxScrollArrow) {
      lightboxScrollArrow.classList.add('visible');
    }
  };

  const openLightbox = (index) => {
    updateLightboxContent(index);
    lightbox.classList.add('active');
    lightbox.setAttribute('aria-hidden', 'false');
    body.style.overflow = 'hidden'; // Lock background scroll
  };

  const closeLightbox = () => {
    lightbox.classList.remove('active');
    lightbox.setAttribute('aria-hidden', 'true');
    body.style.overflow = ''; // Unlock background scroll
    
    // Clear out image src after animation finishes to prevent flash next time
    setTimeout(() => {
      lightboxImg.src = '';
      lightboxImg.alt = '';
      if (lightboxHistogramCanvas) {
        const ctx = lightboxHistogramCanvas.getContext('2d');
        ctx.clearRect(0, 0, lightboxHistogramCanvas.width, lightboxHistogramCanvas.height);
      }
    }, 400);
  };

  const navigateLightbox = (direction) => {
    if (filteredItems.length <= 1) return;
    
    let newIndex = currentImgIndex;
    if (direction === 'next') {
      newIndex = (currentImgIndex + 1) % filteredItems.length;
    } else if (direction === 'prev') {
      newIndex = (currentImgIndex - 1 + filteredItems.length) % filteredItems.length;
    }
    
    // Remove active selection outline from grid item during transition
    if (activeClickedItem) {
      activeClickedItem.classList.remove('active-click');
    }
    
    // Calculate slide direction translation offsets
    const slideOutX = direction === 'next' ? '-40px' : '40px';
    const slideInX = direction === 'next' ? '40px' : '-40px';
    
    // Slide current image out
    lightboxImg.style.transition = 'opacity 0.22s ease-in, transform 0.22s ease-in';
    lightboxImg.style.opacity = '0';
    lightboxImg.style.transform = `translateX(${slideOutX}) scale(0.97)`;
    
    setTimeout(() => {
      // Load content but defer border highlight until transition ends
      updateLightboxContent(newIndex, true);
      
      // Instantly position new image on opposite side
      lightboxImg.style.transition = 'none';
      lightboxImg.style.transform = `translateX(${slideInX}) scale(0.97)`;
      
      // Force reflow
      void lightboxImg.offsetWidth;
      
      // Slide in smoothly to center
      lightboxImg.style.transition = 'opacity 0.3s cubic-bezier(0.16, 1, 0.3, 1), transform 0.3s cubic-bezier(0.16, 1, 0.3, 1)';
      lightboxImg.style.opacity = '1';
      lightboxImg.style.transform = 'translateX(0) scale(1)';
      
      // Re-apply active clicked border selection on background grid once image enters
      setTimeout(() => {
        setActiveClickBorder(filteredItems[newIndex]);
      }, 250);
    }, 220);
  };

  // Wire up item clicks in the gallery
  galleryItems.forEach(item => {
    item.addEventListener('click', (e) => {
      // Find the index of the clicked item inside the filtered array
      const idx = filteredItems.indexOf(item);
      if (idx !== -1) {
        openLightbox(idx);
      }
    });
  });

  // Event Listeners for Lightbox Controls
  if (lightboxClose) {
    lightboxClose.addEventListener('click', closeLightbox);
  }
  
  if (lightboxNext) {
    lightboxNext.addEventListener('click', () => navigateLightbox('next'));
  }
  
  if (lightboxPrev) {
    lightboxPrev.addEventListener('click', () => navigateLightbox('prev'));
  }

  // Click on background overlay closes lightbox
  lightbox.addEventListener('click', (e) => {
    // If clicked outside the image and navigation buttons, close it
    const isOverlayClick = e.target === lightbox || 
                           e.target.classList.contains('lightbox-scroll-container') || 
                           e.target.classList.contains('lightbox-first-fold') || 
                           e.target.classList.contains('lightbox-second-fold') ||
                           e.target.classList.contains('lightbox-details-container');
    if (isOverlayClick) {
      closeLightbox();
    }
  });

  // Smooth scroll down to details when clicking the scroll arrow
  if (lightboxScrollArrow && lightboxScrollContainer) {
    lightboxScrollArrow.addEventListener('click', () => {
      lightboxScrollContainer.scrollTo({
        top: window.innerHeight,
        behavior: 'smooth'
      });
    });
  }

  // Keyboard navigation
  document.addEventListener('keydown', (e) => {
    if (!lightbox.classList.contains('active')) return;
    
    if (e.key === 'Escape') {
      closeLightbox();
    } else if (e.key === 'ArrowRight') {
      navigateLightbox('next');
    } else if (e.key === 'ArrowLeft') {
      navigateLightbox('prev');
    }
  });

  // ==========================================================================
  // IntersectionObserver Lazy Image Loader
  // ==========================================================================
  const initLazyLoading = () => {
    const lazyImages = document.querySelectorAll('img.lazy-img');
    const imageObserver = new IntersectionObserver((entries, observer) => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          const img = entry.target;
          img.src = img.getAttribute('data-src');
          img.classList.remove('lazy-img');
          img.classList.add('lazy-loaded');
          observer.unobserve(img);
        }
      });
    }, {
      rootMargin: '200px 0px', // Pre-load images 200px before coming into viewport
      threshold: 0.01
    });
    
    lazyImages.forEach(img => imageObserver.observe(img));
  };

  // Compute and draw image color histogram
  const computeHistogram = () => {
    if (!lightboxHistogramCanvas || !lightboxImg || !lightboxImg.complete || lightboxImg.naturalWidth === 0) {
      if (lightboxHistogramCanvas) {
        const ctx = lightboxHistogramCanvas.getContext('2d');
        ctx.clearRect(0, 0, lightboxHistogramCanvas.width, lightboxHistogramCanvas.height);
      }
      return;
    }

    try {
      const tempCanvas = document.createElement('canvas');
      const tempCtx = tempCanvas.getContext('2d');
      const scanSize = 100;
      tempCanvas.width = scanSize;
      tempCanvas.height = scanSize;

      // Draw the image onto our tiny offscreen scanner canvas
      tempCtx.drawImage(lightboxImg, 0, 0, scanSize, scanSize);

      const imgData = tempCtx.getImageData(0, 0, scanSize, scanSize);
      const data = imgData.data;

      const rHist = new Array(256).fill(0);
      const gHist = new Array(256).fill(0);
      const bHist = new Array(256).fill(0);

      for (let i = 0; i < data.length; i += 4) {
        rHist[data[i]]++;
        gHist[data[i+1]]++;
        bHist[data[i+2]]++;
      }

      const maxVal = Math.max(...rHist, ...gHist, ...bHist) || 1;

      const ctx = lightboxHistogramCanvas.getContext('2d');
      const w = lightboxHistogramCanvas.width;
      const h = lightboxHistogramCanvas.height;
      ctx.clearRect(0, 0, w, h);

      // Use standard alpha blending which is robust and works perfectly on transparent canvas backgrounds
      ctx.globalCompositeOperation = 'source-over';

      const drawChannel = (hist, fillColor, strokeColor) => {
        ctx.fillStyle = fillColor;
        ctx.strokeStyle = strokeColor;
        ctx.lineWidth = 1.5;
        ctx.lineJoin = 'round';
        ctx.lineCap = 'round';
        
        // Draw filled region
        ctx.beginPath();
        ctx.moveTo(0, h);
        for (let i = 0; i < 256; i++) {
          const x = (i / 255) * w;
          const y = h - (hist[i] / maxVal) * (h - 6);
          ctx.lineTo(x, y);
        }
        ctx.lineTo(w, h);
        ctx.closePath();
        ctx.fill();
        
        // Draw top stroke outline
        ctx.beginPath();
        for (let i = 0; i < 256; i++) {
          const x = (i / 255) * w;
          const y = h - (hist[i] / maxVal) * (h - 6);
          if (i === 0) ctx.moveTo(x, y);
          else ctx.lineTo(x, y);
        }
        ctx.stroke();
      };

      const isDarkMode = body.classList.contains('dark-theme');
      if (isDarkMode) {
        // Vibrant overlapping translucent fills and bright strokes for dark mode
        drawChannel(rHist, 'rgba(235, 77, 75, 0.22)', 'rgba(235, 77, 75, 0.8)');   // Red
        drawChannel(gHist, 'rgba(46, 204, 113, 0.22)', 'rgba(46, 204, 113, 0.8)');   // Green
        drawChannel(bHist, 'rgba(52, 152, 219, 0.22)', 'rgba(52, 152, 219, 0.8)');   // Blue
      } else {
        // Slightly softer fills and strokes for light mode
        drawChannel(rHist, 'rgba(235, 77, 75, 0.18)', 'rgba(235, 77, 75, 0.7)');
        drawChannel(gHist, 'rgba(46, 204, 113, 0.18)', 'rgba(46, 204, 113, 0.7)');
        drawChannel(bHist, 'rgba(52, 152, 219, 0.18)', 'rgba(52, 152, 219, 0.7)');
      }
    } catch (err) {
      console.warn("Histogram computation skipped (likely local file CORS restriction or image not loaded):", err);
    }
  };

  if (lightboxImg) {
    lightboxImg.addEventListener('load', computeHistogram);
  }

  // --- Initialize App ---
  initTheme();
  initLazyLoading();
});
