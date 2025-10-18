import React, { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { productsApi, cartApi } from '../api/api';

function ProductDetail() {
  const { productId } = useParams();
  const [product, setProduct] = useState(null);
  const [loading, setLoading] = useState(true);
  const [addingToCart, setAddingToCart] = useState(false);
  const navigate = useNavigate();

  useEffect(() => {
    loadProduct();
  }, [productId]);

  const loadProduct = async () => {
    try {
      const response = await productsApi.getProduct(productId);
      setProduct(response.data);
      setLoading(false);
    } catch (error) {
      console.error('Error loading product:', error);
      setLoading(false);
    }
  };

  const handleAddToCart = async () => {
    setAddingToCart(true);
    try {
      await cartApi.addToCart(productId, 1);
      window.Telegram.WebApp.showAlert('Товар добавлен в корзину!');
    } catch (error) {
      console.error('Error adding to cart:', error);
      window.Telegram.WebApp.showAlert('Ошибка при добавлении в корзину');
    }
    setAddingToCart(false);
  };

  const handleToggleFavorite = async () => {
    try {
      if (product.is_favorite) {
        await productsApi.removeFromFavorites(productId);
        setProduct({ ...product, is_favorite: false });
        window.Telegram.WebApp.showAlert('Удалено из избранного');
      } else {
        await productsApi.addToFavorites(productId);
        setProduct({ ...product, is_favorite: true });
        window.Telegram.WebApp.showAlert('Добавлено в избранное');
      }
    } catch (error) {
      console.error('Error toggling favorite:', error);
    }
  };

  if (loading) {
    return <div className="page"><div className="loading">Загрузка...</div></div>;
  }

  if (!product) {
    return <div className="page"><div className="error">Товар не найден</div></div>;
  }

  return (
    <div className="page">
      <button 
        onClick={() => navigate(-1)} 
        style={{ marginBottom: '16px', background: 'transparent', border: 'none', fontSize: '16px', cursor: 'pointer' }}
      >
        ← Назад
      </button>

      {product.image_url && (
        <img
          src={product.image_url}
          alt={product.name}
          style={{ width: '100%', height: '300px', objectFit: 'cover', borderRadius: '12px', marginBottom: '16px' }}
        />
      )}

      <div className="page-title">{product.name}</div>

      <div className="product-price" style={{ fontSize: '24px', marginBottom: '16px' }}>
        {product.price}₽
      </div>

      <div style={{ marginBottom: '16px', color: '#666' }}>
        {product.quantity > 0 ? (
          `✅ В наличии: ${product.quantity} шт.`
        ) : (
          '❌ Нет в наличии'
        )}
      </div>

      {product.description && (
        <div style={{ marginBottom: '20px', lineHeight: '1.5' }}>
          {product.description}
        </div>
      )}

      <button
        className="button"
        onClick={handleAddToCart}
        disabled={!product.is_available || product.quantity === 0 || addingToCart}
      >
        {addingToCart ? 'Добавление...' : '🛒 Добавить в корзину'}
      </button>

      <button
        className="button"
        onClick={handleToggleFavorite}
        style={{ background: product.is_favorite ? '#e53e3e' : '#48bb78' }}
      >
        {product.is_favorite ? '💔 Убрать из избранного' : '❤️ Добавить в избранное'}
      </button>

      <button
        className="button"
        onClick={() => navigate('/cart')}
        style={{ background: '#805ad5' }}
      >
        Перейти в корзину
      </button>
    </div>
  );
}

export default ProductDetail;

