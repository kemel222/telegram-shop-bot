import React, { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { productsApi } from '../api/api';

function Catalog() {
  const { categoryId } = useParams();
  const [products, setProducts] = useState([]);
  const [category, setCategory] = useState(null);
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();

  useEffect(() => {
    if (categoryId) {
      loadProducts();
    }
  }, [categoryId]);

  const loadProducts = async () => {
    try {
      const [categoryRes, productsRes] = await Promise.all([
        productsApi.getCategory(categoryId),
        productsApi.getCategoryProducts(categoryId)
      ]);
      
      setCategory(categoryRes.data);
      setProducts(productsRes.data);
      setLoading(false);
    } catch (error) {
      console.error('Error loading products:', error);
      setLoading(false);
    }
  };

  if (loading) {
    return <div className="page"><div className="loading">Загрузка...</div></div>;
  }

  return (
    <div className="page">
      <button 
        onClick={() => navigate('/')} 
        style={{ marginBottom: '16px', background: 'transparent', border: 'none', fontSize: '16px', cursor: 'pointer' }}
      >
        ← Назад
      </button>
      
      <div className="page-title">{category?.name || 'Каталог'}</div>
      
      {category?.description && (
        <div style={{ marginBottom: '20px', color: '#666' }}>
          {category.description}
        </div>
      )}

      {products.length === 0 ? (
        <div>В этой категории пока нет товаров</div>
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
            {product.is_favorite && <span style={{ fontSize: '24px' }}>❤️</span>}
          </div>
        ))
      )}
    </div>
  );
}

export default Catalog;

