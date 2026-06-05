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
      const itemCategory = item.getAttribute('data-category');
      
      // Reset animation classes
      item.classList.remove('fade-in-item');
      
      if (category === 'all' || itemCategory === category) {
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
    
    // Safety check & assign properties (no innerHTML to avoid XSS)
    // Use data-original for high quality image, fall back to thumbnail data-src or imgEl.src
    lightboxImg.src = currentItem.getAttribute('data-original') || imgEl.getAttribute('data-src') || imgEl.src;
    lightboxImg.alt = imgEl.alt || 'Photography showcase';
    
    // Populate text details safely
    metaCategory.textContent = currentItem.getAttribute('data-category') || '';
    metaTitle.textContent = currentItem.getAttribute('data-title') || 'Untitled';
    metaLocation.textContent = currentItem.getAttribute('data-location') || '';
    metaCamera.textContent = currentItem.getAttribute('data-camera') || 'N/A';
    metaLens.textContent = currentItem.getAttribute('data-lens') || 'N/A';
    metaExif.textContent = currentItem.getAttribute('data-exif') || 'N/A';
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
    if (e.target === lightbox || e.target.classList.contains('lightbox-content')) {
      closeLightbox();
    }
  });

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

  // --- Initialize App ---
  initTheme();
  initLazyLoading();
});
