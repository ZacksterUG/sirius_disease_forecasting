import { useState } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { loginUser } from './authSlice';
import { useNavigate } from 'react-router-dom';
import "./LoginForm.css"

export default function LoginForm() {
  const dispatch = useDispatch();
  const navigate = useNavigate();
  const [login, setLogin] = useState(localStorage.getItem('savedLogin') || '');
  const [password, setPassword] = useState('');
  const status = useSelector((state) => state.auth.status);
  const error = useSelector((state) => state.auth.error);

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      const result = await dispatch(loginUser({ login, password })).unwrap();
      if (result.access_token) {
        navigate('/data');
      }
    } catch (err) {
      console.error('Login failed', err);
    }
  };

  return (
    <div className="login-container">
      <form onSubmit={handleSubmit}>
        <div className='login-components'>
          <h2>Авторизация</h2>
          <input
            type="text"
            placeholder="Логин"
            value={login}
            onChange={(e) => setLogin(e.target.value)}
            required
          />
          <input
            type="password"
            placeholder="Пароль"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
          />
          <button
            type="submit">
            {status === 'loading' ? 'Вход...' : 'Войти'}
          </button>
          {error && <p>Ошибка входа</p>}
        </div>
      </form>
    </div>
  );
}