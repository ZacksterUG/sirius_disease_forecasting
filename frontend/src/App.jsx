import './App.css'

import { useSelector } from 'react-redux';
import { Navigate, Route, Routes } from 'react-router-dom';
import LoginForm from './features/auth/LoginForm';
import DataView from './features/data/DataView';
import Forecast from './features/forecast/Forecast';

export default function App() {
  const token = useSelector((state) => state.auth.token);

  return (
    <Routes>
      <Route path="/login" element={<LoginForm />} />
      <Route path="/data" element={token ? <DataView /> : <Navigate to="/login" />} />
      <Route path="/forecast" element={token ? <Forecast /> : <Navigate to="/login" />} />
      <Route
        path="*"
        element={token ? <Navigate to="/data" /> : <Navigate to="/login" />}
      />
    </Routes>
  );
}
