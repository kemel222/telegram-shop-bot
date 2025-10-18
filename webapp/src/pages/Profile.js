import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { usersApi, promoApi } from '../api/api';

function Profile({ user, setUser }) {
  const [cashbackInfo, setCashbackInfo] = useState(null);
  const [promoCode, setPromoCode] = useState('');
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();

  useEffect(() => {
    loadCashbackInfo();
  }, []);

  const loadCashbackInfo = async () => {
    try {
      const response = await usersApi.getCashbackInfo();
      setCashbackInfo(response.data);
      setLoading(false);
    } catch (error) {
      console.error('Error loading cashback info:', error);
      setLoading(false);
    }
  };

  const handleApplyPromo = async () => {
    if (!promoCode.trim()) {
      window.Telegram.WebApp.showAlert('Введите промокод');
      return;
    }

    try {
      const response = await promoApi.applyBalancePromo(promoCode);
      window.Telegram.WebApp.showAlert(response.data.message);
      
      // Обновляем баланс
      const profileRes = await usersApi.getProfile();
      setUser(profileRes.data);
      setPromoCode('');
    } catch (error) {
      window.Telegram.WebApp.showAlert(
        error.response?.data?.detail || 'Ошибка применения промокода'
      );
    }
  };

  if (loading) {
    return <div className="page"><div className="loading">Загрузка...</div></div>;
  }

  return (
    <div className="page">
      <div className="page-title">👤 Профиль</div>

      <div className="card">
        <div style={{ fontSize: '18px', fontWeight: 'bold', marginBottom: '8px' }}>
          {user?.first_name || 'Пользователь'}
        </div>
        {user?.username && (
          <div style={{ color: '#666', marginBottom: '8px' }}>
            @{user.username}
          </div>
        )}
        <div style={{ fontSize: '20px', fontWeight: 'bold', color: '#3390ec', marginBottom: '8px' }}>
          💰 Баланс: {user?.balance || 0}₽
        </div>
        <div style={{ fontSize: '18px', fontWeight: 'bold', color: '#805ad5' }}>
          💳 Кешбек: {user?.cashback_balance || 0}₽
        </div>
      </div>

      <div className="card">
        <div style={{ fontSize: '16px', fontWeight: 'bold', marginBottom: '12px' }}>
          🎟 Промокод
        </div>
        <input
          type="text"
          className="input"
          placeholder="Введите промокод"
          value={promoCode}
          onChange={(e) => setPromoCode(e.target.value.toUpperCase())}
        />
        <button className="button" onClick={handleApplyPromo}>
          Применить промокод
        </button>
      </div>

      {cashbackInfo && (
        <div className="card">
          <div style={{ fontSize: '16px', fontWeight: 'bold', marginBottom: '12px' }}>
            💰 Кешбек программа
          </div>

          <div style={{ background: '#e6f3ff', padding: '12px', borderRadius: '8px', marginBottom: '12px' }}>
            <div style={{ fontSize: '14px', marginBottom: '8px' }}>
              📊 Статистика:
            </div>
            <div style={{ fontSize: '14px' }}>
              • Всего кешбека: {cashbackInfo.stats.total_cashback}₽
            </div>
            <div style={{ fontSize: '14px' }}>
              • Начислений: {cashbackInfo.stats.transactions_count}
            </div>
            <div style={{ fontSize: '14px' }}>
              • Средний кешбек: {cashbackInfo.stats.average_cashback}₽
            </div>
          </div>

          <div style={{ background: '#f0f9ff', padding: '12px', borderRadius: '8px', marginBottom: '12px' }}>
            <div style={{ fontSize: '14px', marginBottom: '8px', fontWeight: 'bold' }}>
              🎁 Условия начисления:
            </div>
            <div style={{ fontSize: '14px' }}>
              • На POD-системы: 2.5%
            </div>
            <div style={{ fontSize: '14px' }}>
              • На все остальное: 3.5%
            </div>
          </div>

          <div style={{ fontSize: '13px', color: '#666' }}>
            💡 Кешбек начисляется автоматически после выполнения заказа!
            Используйте кешбек для оплаты следующих покупок.
          </div>
        </div>
      )}

      <div className="card" style={{ textAlign: 'center', background: '#f8f9fa' }}>
        <div style={{ fontSize: '13px', color: '#666' }}>
          💻 Разработано <a href="https://t.me/x32asm" style={{ color: '#3390ec', textDecoration: 'none' }}>@x32asm</a>
        </div>
      </div>

      <button className="button" onClick={() => navigate('/cart')} style={{ background: '#805ad5' }}>
        🛒 Перейти в корзину
      </button>
    </div>
  );
}

export default Profile;

