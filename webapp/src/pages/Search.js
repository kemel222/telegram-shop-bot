import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { productsApi } from '../api/api';

function Search() {
  const [query, setQuery] = useState('');
  const [products, setProducts] = useState([]);
  const [loading, setLoading] = useState(false);
  const [searched, setSearched] = useState(false);
  const navigate = useNavigate();

  const handleSearch = async (e) => {
    e.preventDefault();
    
    if (!query.trim()) {
      window.Telegram.WebApp.showAlert('Введите поисковый запрос');
      return;
    }

    setLoading(true);
    setSearched(true);

    try {
      const response = await productsApi.searchProducts(query);
      setProducts(response.data);
      setLoading(false);
    } catch (error) {
      console.error('Error searching products:', error);
      setLoading(false);
    }
  };

  return (
    <div className="page">
      <div className="page-title">🔍 Поиск</div>

      <form onSubmit={handleSearch}>
        <input
          type="text"
          className="input"
          placeholder="Введите название товара..."
          value={query}
          onChange={(e) => setQuery(e.target.value)}
        />
        <button type="submit" className="button" disabled={loading}>
          {loading ? 'Поиск...' : '🔍 Найти'}
        </button>
      </form>

      {searched && (
        <div style={{ marginTop: '20px' }}>
          {loading ? (
            <div className="loading">Поиск...</div>
          ) : products.length === 0 ? (
            <div style={{ textAlign: 'center', color: '#666' }}>
              Ничего не найдено по запросу "{query}"
            </div>
          ) : (
            <>
              <div style={{ marginBottom: '12px', color: '#666' }}>
                Найдено: {products.length} товаров
              </div>
              {products.map(product => (
                <div
                  key={product.id}
                  className="product-card"
                  onClick={() => navigate(`/product/${product.id}`)}
                >
                  <img
                    src={product.image_url || 'https://via.placeholder.com/80'}
                    alt={product.name}
                    className="product-image"
                  />
                  <div className="product-info">
                    <div className="product-name">{product.name}</div>
                    <div className="product-price">{product.price}₽</div>
                    <div style={{ fontSize: '12px', color: '#666', marginTop: '4px' }}>
                      {product.quantity > 0 ? `В наличии: ${product.quantity} шт.` : 'Нет в наличии'}
                    </div>
                  </div>
                  {product.is_favorite && <span style={{ fontSize: '24px' }}>❤️</span>}
                </div>
              ))}
            </>
          )}
        </div>
      )}
    </div>
  );
}

export default Search;

