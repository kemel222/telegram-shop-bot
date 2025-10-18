import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { productsApi } from '../api/api';

function Favorites() {
  const [products, setProducts] = useState([]);
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();

  useEffect(() => {
    loadFavorites();
  }, []);

  const loadFavorites = async () => {
    try {
      const response = await productsApi.getFavorites();
      setProducts(response.data);
      setLoading(false);
    } catch (error) {
      console.error('Error loading favorites:', error);
      setLoading(false);
    }
  };

  if (loading) {
    return <div className="page"><div className="loading">Загрузка...</div></div>;
  }

  return (
    <div className="page">
      <div className="page-title">❤️ Избранное</div>

      {products.length === 0 ? (
        <div>
          <p>У вас пока нет избранных товаров</p>
          <button className="button" onClick={() => navigate('/')}>
            Перейти к покупкам
          </button>
        </div>
      ) : (
        products.map(product => (
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
            <span style={{ fontSize: '24px' }}>❤️</span>
          </div>
        ))
      )}
    </div>
  );
}

export default Favorites;

