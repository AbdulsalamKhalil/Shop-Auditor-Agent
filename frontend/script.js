
function renderDeals(deals) {
  const grid = document.getElementById('resultsGrid');
  const countSpan = document.querySelector('.highlight-count');

  if (!grid) return;

  if (countSpan) countSpan.textContent = deals.length;

  let htmlContent = '';

  deals.forEach(deal => {
    const specsHTML = deal.specs ? deal.specs.map(spec => `<span class="spec-tag">${spec}</span>`).join('') : '';

    htmlContent += `
      <div class="deal-card">
        <div class="deal-image">
          <img src="${deal.image || 'https://via.placeholder.com/150'}" alt="${deal.title}">
        </div>
        
        <div class="deal-content">
          <div class="deal-header">
            <h3 class="deal-title">${deal.title}</h3>
            <div class="deal-price-wrapper">
              <span class="deal-price">${deal.price}</span><span class="deal-currency">${deal.currency || 'EGP'}</span>
            </div>
          </div>

          <div class="deal-meta">
            <div class="deal-store">
              <svg class="store-icon" viewBox="0 0 24 24" fill="currentColor"><path d="M14.9 17.5c-1.3.8-3.1 1.2-4.9 1.2-4.1 0-7.3-2.6-7.3-6.2 0-3.4 2.8-6.1 6.8-6.1 2.3 0 4.1.8 5.3 2.1l-1.9 1.9c-.8-.9-2.1-1.4-3.4-1.4-2.4 0-4.1 1.7-4.1 3.7 0 2.1 1.7 3.7 4.1 3.7 1 0 1.9-.3 2.6-.7v1.8h2.8z"/></svg>
              ${deal.store}
            </div>
            <div class="deal-rating">
              <svg class="star-icon" viewBox="0 0 24 24" fill="#fbbf24"><path d="M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z"/></svg>
              ${deal.rating || 'N/A'}
            </div>
          </div>

          <div class="deal-bottom">
            <div class="deal-specs">
              ${specsHTML}
            </div>
            <a href="${deal.link || '#'}" class="btn-buy-now" target="_blank">Buy Now</a>
          </div>
        </div>
      </div>
    `;
  });

  grid.innerHTML = htmlContent;
}

// 2. دالة التعامل مع استدعاء البحث والـ Loading State
async function handleSearch() {
  const queryInput = document.querySelector('.search-input');
  const imageInput = document.querySelector('.file-input-hidden');
  const grid = document.getElementById('resultsGrid');
  const loadingContainer = document.getElementById('loadingContainer');

  const query = queryInput.value.trim();
  const imageFile = imageInput ? imageInput.files[0] : null;

  if (!query && !imageFile) return;

  // 1. الانتقال إلى سكشن النتائج تلقائياً
  document.getElementById('results').scrollIntoView({ behavior: 'smooth' });

  // 2. إظهار انيميشن الـ Loading وتفريغ النتائج القديمة
  if (loadingContainer) loadingContainer.classList.remove('hidden');
  if (grid) grid.innerHTML = '';

  try {
    const formData = new FormData();
    if (query) formData.append('query', query);
    if (imageFile) formData.append('image', imageFile);

    const response = await fetch('http://localhost:8000/api/audit', {
      method: 'POST',
      body: formData
    });

    if (!response.ok) {
      throw new Error(`Server Error: ${response.status}`);
    }

    const realBackendData = await response.json();

    // 3. إخفاء الـ Loading ورسم النتائج الحقيقية
    if (loadingContainer) loadingContainer.classList.add('hidden');
    renderDeals(realBackendData);

  } catch (error) {
    console.error("Error fetching deals:", error);
    if (loadingContainer) loadingContainer.classList.add('hidden');
    if (grid) {
      grid.innerHTML = '<div style="grid-column: 1/-1; text-align: center; color: #ef4444; padding: 2rem;">Unable to connect to the backend server. Please make sure FastAPI is running.</div>';
    }
  }
}

// 3. ربط أحداث الضغط على الأزرار
document.querySelector('.btn-submit-search').addEventListener('click', (e) => {
  e.preventDefault();
  handleSearch();
});

document.querySelector('.search-input').addEventListener('keypress', (e) => {
  if (e.key === 'Enter' && !e.shiftKey) {
    e.preventDefault();
    handleSearch();
  }
});
