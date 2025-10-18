import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { productsApi } from '../api/api';

function PromoBanner() {
  const [currentBanner, setCurrentBanner] = useState(0);
  
  const banners = [
    { emoji: '🎁', text: 'Кешбек до 3.5% на все товары!' },
    { emoji: '🔥', text: 'Новинки в каталоге каждую неделю!' },
    { emoji: '💰', text: 'Скидки до 20% на избранные товары!' },
    { emoji: '🚀', text: 'Быстрая доставка по городу!' },
    { emoji: '⚡', text: 'Оплата онлайн или при получении!' }
  ];
  
  useEffect(() => {
    const interval = setInterval(() => {
      setCurrentBanner((prev) => (prev + 1) % banners.length);
    }, 15000); // Каждые 15 секунд
    
    return () => clearInterval(interval);
  }, []);
  
  return (
    <div style={{
      background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
      color: 'white',
      padding: '16px',
      borderRadius: '12px',
      textAlign: 'center',
      marginBottom: '16px',
      boxShadow: '0 4px 6px rgba(0,0,0,0.1)',
      transition: 'all 0.5s ease',
      fontWeight: 'bold'
    }}>
      <div style={{ fontSize: '24px', marginBottom: '4px' }}>
        {banners[currentBanner].emoji}
      </div>
      <div style={{ fontSize: '15px' }}>
        {banners[currentBanner].text}
      </div>
    </div>
  );
}

function Home({ user }) {
  const [categories, setCategories] = useState([]);
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();

  useEffect(() => {
    loadCategories();
  }, []);

  const loadCategories = async () => {
    try {
      const response = await productsApi.getCategories();
      setCategories(response.data);
      setLoading(false);
    } catch (error) {
      console.error('Error loading categories:', error);
      setLoading(false);
    }
  };

  if (loading) {
    return <div className="page"><div className="loading">Загрузка...</div></div>;
  }

  return (
    <div className="page">
      <div className="page-title">🛍 Hotspot</div>
      
      <PromoBanner />
      
      {user && (
        <div className="card">
          <div>Привет, {user.first_name || 'пользователь'}!</div>
          <div>💰 Баланс: {user.balance}₽</div>
          <div>💳 Кешбек: {user.cashback_balance || 0}₽</div>
        </div>
      )}

      <h2 style={{ marginTop: '20px', marginBottom: '12px' }}>Категории</h2>
      
      {categories.length === 0 ? (
        <div>Категории пока отсутствуют</div>
      ) : (
        categories.map(category => (
          <div
            key={category.id}
            className="category-card"
            onClick={() => navigate(`/catalog/${category.id}`)}
          >
            {category.image_url && (
              <img
                src={category.image_url}
                alt={category.name}
                style={{ width: '100%', height: '150px', objectFit: 'cover', borderRadius: '8px', marginBottom: '12px' }}
              />
            )}
            <div className="category-name">{category.name}</div>
            {category.description && (
              <div style={{ fontSize: '14px', color: '#666', marginTop: '4px' }}>
                {category.description}
              </div>
            )}
          </div>
        ))
      )}
    </div>
  );
}

export default Home;

