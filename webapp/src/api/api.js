import axios from 'axios';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api';

// Создаём экземпляр axios с настройками
export const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Добавляем токен к каждому запросу
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// API методы
export const productsApi = {
  getCategories: () => api.get('/products/categories'),
  getCategory: (id) => api.get(`/products/categories/${id}`),
  getCategoryProducts: (id) => api.get(`/products/categories/${id}/products`),
  getProduct: (id) => api.get(`/products/${id}`),
  searchProducts: (query) => api.get(`/products/search/${query}`),
  addToFavorites: (id) => api.post(`/products/${id}/favorite`),
  removeFromFavorites: (id) => api.delete(`/products/${id}/favorite`),
  getFavorites: () => api.get('/products/favorites/list'),
};

export const cartApi = {
  getCart: () => api.get('/cart'),
  addToCart: (productId, quantity = 1) => api.post('/cart/add', { product_id: productId, quantity }),
  updateCartItem: (productId, quantity) => api.put(`/cart/${productId}`, { quantity }),
  removeFromCart: (productId) => api.delete(`/cart/${productId}`),
  clearCart: () => api.delete('/cart/clear'),
};

export const ordersApi = {
  createOrder: (orderData) => api.post('/orders', orderData),
  getOrders: () => api.get('/orders'),
  getOrder: (id) => api.get(`/orders/${id}`),
  cancelOrder: (id) => api.post(`/orders/${id}/cancel`),
};

export const promoApi = {
  validatePromo: (code, orderTotal) => api.post('/promo/validate', { code, order_total: orderTotal }),
  applyBalancePromo: (code) => api.post('/promo/apply-balance-promo', { code }),
};

export const usersApi = {
  auth: (data) => api.post('/users/auth', data),
  getProfile: () => api.get('/users/profile'),
  updatePhone: (phone) => api.put('/users/profile/phone', { phone }),
  getBalance: () => api.get('/users/balance'),
  getCashbackInfo: () => api.get('/users/cashback'),
};

