import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { cartApi } from '../api/api';

function Cart() {
  const [cart, setCart] = useState({ items: [], total: 0 });
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();

  useEffect(() => {
    loadCart();
  }, []);

  const loadCart = async () => {
    try {
      const response = await cartApi.getCart();
      setCart(response.data);
      setLoading(false);
    } catch (error) {
      console.error('Error loading cart:', error);
      setLoading(false);
    }
  };

  const handleUpdateQuantity = async (productId, newQuantity) => {
    try {
      if (newQuantity === 0) {
        await cartApi.removeFromCart(productId);
      } else {
        await cartApi.updateCartItem(productId, newQuantity);
      }
      loadCart();
    } catch (error) {
      console.error('Error updating cart:', error);
    }
  };

  const handleClearCart = async () => {
    const confirmed = window.confirm('Вы уверены, что хотите очистить корзину?');
    if (confirmed) {
      try {
        await cartApi.clearCart();
        loadCart();
      } catch (error) {
        console.error('Error clearing cart:', error);
      }
    }
  };

  if (loading) {
    return <div className="page"><div className="loading">Загрузка...</div></div>;
  }

  return (
    <div className="page">
      <div className="page-title">🛒 Корзина</div>

      {cart.items.length === 0 ? (
        <div>
          <p>Ваша корзина пуста</p>
          <button className="button" onClick={() => navigate('/')}>
            Перейти к покупкам
          </button>
        </div>
      ) : (
        <>
          {cart.items.map(item => (
            <div key={item.id} className="card">
              <div style={{ display: 'flex', gap: '12px' }}>
                <img
                  src={item.product_image || 'https://via.placeholder.com/60'}
                  alt={item.product_name}
                  style={{ width: '60px', height: '60px', objectFit: 'cover', borderRadius: '8px' }}
                />
                <div style={{ flex: 1 }}>
                  <div className="product-name">{item.product_name}</div>
                  <div className="product-price">{item.product_price}₽</div>
                  <div style={{ fontSize: '14px', color: '#666' }}>
                    Сумма: {item.subtotal}₽
                  </div>
                </div>
              </div>
              
              <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginTop: '12px' }}>
                <button
                  onClick={() => handleUpdateQuantity(item.product_id, item.quantity - 1)}
                  style={{ padding: '8px 16px', fontSize: '18px' }}
                >
                  -
                </button>
                <span style={{ fontSize: '18px', fontWeight: 'bold' }}>{item.quantity}</span>
                <button
                  onClick={() => handleUpdateQuantity(item.product_id, item.quantity + 1)}
                  style={{ padding: '8px 16px', fontSize: '18px' }}
                >
                  +
                </button>
                <button
                  onClick={() => handleUpdateQuantity(item.product_id, 0)}
                  style={{ marginLeft: 'auto', padding: '8px 16px', background: '#e53e3e', color: 'white', border: 'none', borderRadius: '6px' }}
                >
                  🗑
                </button>
              </div>
            </div>
          ))}

          <div className="card" style={{ background: '#f8f9fa', fontWeight: 'bold', fontSize: '20px' }}>
            Итого: {cart.total}₽
          </div>

          <button className="button" onClick={() => navigate('/checkout')}>
            ✅ Оформить заказ
          </button>

          <button
            className="button"
            onClick={handleClearCart}
            style={{ background: '#e53e3e' }}
          >
            🗑 Очистить корзину
          </button>
        </>
      )}
    </div>
  );
}

export default Cart;

