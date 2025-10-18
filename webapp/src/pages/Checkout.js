import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { ordersApi, cartApi, promoApi } from '../api/api';

function Checkout() {
  const [cart, setCart] = useState({ items: [], total: 0 });
  const [deliveryType, setDeliveryType] = useState('');
  const [customerName, setCustomerName] = useState('');
  const [customerPhone, setCustomerPhone] = useState('');
  const [deliveryAddress, setDeliveryAddress] = useState('');
  const [deliveryTimeSlot, setDeliveryTimeSlot] = useState('');
  const [paymentMethod, setPaymentMethod] = useState('');
  const [promoCode, setPromoCode] = useState('');
  const [discount, setDiscount] = useState(0);
  const [useBalance, setUseBalance] = useState(false);
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  useEffect(() => {
    loadCart();
  }, []);

  const loadCart = async () => {
    try {
      const response = await cartApi.getCart();
      setCart(response.data);
    } catch (error) {
      console.error('Error loading cart:', error);
    }
  };

  const handleValidatePromo = async () => {
    if (!promoCode.trim()) return;

    try {
      const response = await promoApi.validatePromo(promoCode, cart.total);
      setDiscount(response.data.discount || 0);
      window.Telegram.WebApp.showAlert(response.data.message);
    } catch (error) {
      window.Telegram.WebApp.showAlert(
        error.response?.data?.detail || 'Промокод недействителен'
      );
      setDiscount(0);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    if (!deliveryType || !customerName || !customerPhone || !paymentMethod) {
      window.Telegram.WebApp.showAlert('Заполните все обязательные поля');
      return;
    }

    if (deliveryType === 'delivery' && !deliveryAddress) {
      window.Telegram.WebApp.showAlert('Укажите адрес доставки');
      return;
    }

    if ((deliveryType === 'pickup_center' || deliveryType === 'pickup_tc') && !deliveryTimeSlot) {
      window.Telegram.WebApp.showAlert('Укажите время самовывоза');
      return;
    }

    setLoading(true);

    try {
      const orderData = {
        delivery_type: deliveryType,
        customer_name: customerName,
        customer_phone: customerPhone,
        payment_method: paymentMethod,
        delivery_address: deliveryType === 'delivery' ? deliveryAddress : null,
        delivery_time_slot: deliveryType !== 'delivery' ? deliveryTimeSlot : null,
        promo_code: promoCode || null,
        use_balance: useBalance
      };

      const response = await ordersApi.createOrder(orderData);
      
      window.Telegram.WebApp.showAlert(
        '✅ Заказ успешно создан!\n\nНомер заказа: #' + response.data.id,
        () => {
          navigate('/');
        }
      );
    } catch (error) {
      console.error('Error creating order:', error);
      window.Telegram.WebApp.showAlert(
        error.response?.data?.detail || 'Ошибка при создании заказа'
      );
    }

    setLoading(false);
  };

  const deliveryCost = deliveryType === 'delivery' ? 300 : 0;
  const finalTotal = cart.total + deliveryCost - discount;

  return (
    <div className="page">
      <div className="page-title">✅ Оформление заказа</div>

      <form onSubmit={handleSubmit}>
        <div className="card">
          <h3>Способ получения</h3>
          <select
            className="input"
            value={deliveryType}
            onChange={(e) => setDeliveryType(e.target.value)}
            required
          >
            <option value="">Выберите способ получения</option>
            <option value="pickup_center">🏢 Самовывоз из Центра (12:00-17:00)</option>
            <option value="pickup_tc">🏬 Самовывоз из ТЦ (16:30-21:00)</option>
            <option value="delivery">🚚 Доставка (300₽)</option>
          </select>

          {deliveryType === 'delivery' && (
            <input
              type="text"
              className="input"
              placeholder="Адрес доставки"
              value={deliveryAddress}
              onChange={(e) => setDeliveryAddress(e.target.value)}
              required
            />
          )}

          {(deliveryType === 'pickup_center' || deliveryType === 'pickup_tc') && (
            <input
              type="text"
              className="input"
              placeholder={
                deliveryType === 'pickup_center'
                  ? 'Время (12:00-17:00)'
                  : 'Время (16:30-21:00)'
              }
              value={deliveryTimeSlot}
              onChange={(e) => setDeliveryTimeSlot(e.target.value)}
              required
            />
          )}
        </div>

        <div className="card">
          <h3>Контактные данные</h3>
          <input
            type="text"
            className="input"
            placeholder="Ваше имя"
            value={customerName}
            onChange={(e) => setCustomerName(e.target.value)}
            required
          />
          <input
            type="tel"
            className="input"
            placeholder="Номер телефона"
            value={customerPhone}
            onChange={(e) => setCustomerPhone(e.target.value)}
            required
          />
        </div>

        <div className="card">
          <h3>Промокод</h3>
          <div style={{ display: 'flex', gap: '8px' }}>
            <input
              type="text"
              className="input"
              style={{ marginBottom: 0 }}
              placeholder="Введите промокод"
              value={promoCode}
              onChange={(e) => setPromoCode(e.target.value.toUpperCase())}
            />
            <button
              type="button"
              onClick={handleValidatePromo}
              style={{ padding: '12px 24px', background: '#48bb78', color: 'white', border: 'none', borderRadius: '8px' }}
            >
              ✓
            </button>
          </div>
          {discount > 0 && (
            <div style={{ marginTop: '8px', color: '#48bb78' }}>
              Скидка: {discount}₽
            </div>
          )}
        </div>

        <div className="card">
          <h3>Способ оплаты</h3>
          <select
            className="input"
            value={paymentMethod}
            onChange={(e) => setPaymentMethod(e.target.value)}
            required
          >
            <option value="">Выберите способ оплаты</option>
            <option value="sbp_online">💳 СБП онлайн</option>
            <option value="sbp_on_receipt">💳 СБП при получении</option>
            <option value="cash">💵 Наличными при получении</option>
            <option value="balance">💰 Баланс сайта</option>
          </select>

          <div style={{ marginTop: '12px' }}>
            <label style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
              <input
                type="checkbox"
                checked={useBalance}
                onChange={(e) => setUseBalance(e.target.checked)}
              />
              <span>Использовать баланс для частичной оплаты</span>
            </label>
          </div>
        </div>

        <div className="card" style={{ background: '#f8f9fa' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '8px' }}>
            <span>Товары:</span>
            <span>{cart.total}₽</span>
          </div>
          {deliveryCost > 0 && (
            <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '8px' }}>
              <span>Доставка:</span>
              <span>{deliveryCost}₽</span>
            </div>
          )}
          {discount > 0 && (
            <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '8px', color: '#48bb78' }}>
              <span>Скидка:</span>
              <span>-{discount}₽</span>
            </div>
          )}
          <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '20px', fontWeight: 'bold', marginTop: '12px', paddingTop: '12px', borderTop: '1px solid #ddd' }}>
            <span>Итого:</span>
            <span>{finalTotal}₽</span>
          </div>
        </div>

        <button type="submit" className="button" disabled={loading}>
          {loading ? 'Создание заказа...' : '✅ Подтвердить заказ'}
        </button>

        <button
          type="button"
          className="button"
          onClick={() => navigate('/cart')}
          style={{ background: '#6c757d' }}
        >
          ← Вернуться в корзину
        </button>
      </form>
    </div>
  );
}

export default Checkout;

