import React, { useEffect, useState } from 'react';
import { BrowserRouter as Router, Routes, Route, Link } from 'react-router-dom';
import './App.css';
import Home from './pages/Home';
import Catalog from './pages/Catalog';
import ProductDetail from './pages/ProductDetail';
import Cart from './pages/Cart';
import Favorites from './pages/Favorites';
import Profile from './pages/Profile';
import Search from './pages/Search';
import Checkout from './pages/Checkout';
import { api } from './api/api';

function App() {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    // Инициализация Telegram WebApp
    const tg = window.Telegram.WebApp;
    tg.ready();
    tg.expand();

    // Аутентификация пользователя
    const initUser = async () => {
      try {
        const initData = tg.initDataUnsafe;
        
        if (!initData.user) {
          throw new Error('User data not found');
        }

        // Отправляем данные пользователя на бэкенд для аутентификации
        const response = await api.post('/users/auth', {
          telegram_id: initData.user.id,
          username: initData.user.username,
          first_name: initData.user.first_name
        });

        // Сохраняем токен
        localStorage.setItem('token', response.data.access_token);
        setUser(response.data);
        setLoading(false);
      } catch (err) {
        console.error('Auth error:', err);
        setError('Ошибка авторизации');
        setLoading(false);
      }
    };

    initUser();
  }, []);

  if (loading) {
    return <div className="loading">Загрузка...</div>;
  }

  if (error) {
    return <div className="error">{error}</div>;
  }

  return (
    <Router>
      <div className="App">
        <Routes>
          <Route path="/" element={<Home user={user} />} />
          <Route path="/catalog" element={<Catalog />} />
          <Route path="/catalog/:categoryId" element={<Catalog />} />
          <Route path="/product/:productId" element={<ProductDetail />} />
          <Route path="/cart" element={<Cart />} />
          <Route path="/favorites" element={<Favorites />} />
          <Route path="/profile" element={<Profile user={user} setUser={setUser} />} />
          <Route path="/search" element={<Search />} />
          <Route path="/checkout" element={<Checkout />} />
        </Routes>
        
        <BottomNav />
      </div>
    </Router>
  );
}

function BottomNav() {
  return (
    <>
      <nav className="bottom-nav">
        <Link to="/" className="nav-item">
          <span>🏠</span>
          <span>Главная</span>
        </Link>
        <Link to="/search" className="nav-item">
          <span>🔍</span>
          <span>Поиск</span>
        </Link>
        <Link to="/favorites" className="nav-item">
          <span>❤️</span>
          <span>Избранное</span>
        </Link>
        <Link to="/profile" className="nav-item">
          <span>👤</span>
          <span>Профиль</span>
        </Link>
      </nav>
      <div style={{ 
        position: 'fixed', 
        bottom: '60px', 
        right: '10px', 
        background: '#f8f9fa', 
        padding: '5px 10px', 
        borderRadius: '8px',
        fontSize: '11px',
        zIndex: 1000,
        boxShadow: '0 2px 4px rgba(0,0,0,0.1)'
      }}>
        💻 by <a href="https://t.me/x32asm" style={{ color: '#3390ec', textDecoration: 'none' }}>@x32asm</a>
      </div>
    </>
  );
}

export default App;

