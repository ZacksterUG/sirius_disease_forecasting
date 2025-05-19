import { createSlice, createAsyncThunk } from '@reduxjs/toolkit';
import api from '../../api/axios';

const initialState = {
  user: null,
  token: sessionStorage.getItem('accessToken') || null,
  status: 'idle',
  error: null,
};

export const loginUser = createAsyncThunk(
  'auth/loginUser',
  async ({ login, password }, { rejectWithValue }) => {
    try {
      const response = await api.post('/login', { login, password });
      return response.data;
    } catch (err) {
      return rejectWithValue(err.response?.data?.message || 'Ошибка входа');
    }
  }
);

export const logoutUser = createAsyncThunk('auth/logoutUser', async () => {
  await api.delete('/logout');
});

const authSlice = createSlice({
  name: 'auth',
  initialState,
  reducers: {
    logout(state) {
      state.user = null;
      state.token = null;
      state.status = 'idle';
      state.error = null;
      sessionStorage.removeItem('accessToken');
    },
  },
  extraReducers: (builder) => {
    builder
      .addCase(loginUser.pending, (state) => {
        state.status = 'loading';
        state.error = null;
      })
      .addCase(loginUser.fulfilled, (state, action) => {
        state.status = 'succeeded';
        state.token = action.payload.access_token;
        state.error = null;
        sessionStorage.setItem('accessToken', action.payload.access_token);
      })
      .addCase(loginUser.rejected, (state, action) => {
        state.status = 'failed';
        state.error = action.payload || 'Ошибка входа';
      })
      .addCase(logoutUser.fulfilled, (state) => {
        state.status = 'idle';
        state.token = null;
        state.error = null;
        sessionStorage.removeItem('accessToken');
      });
  },
});

export const { logout } = authSlice.actions;
export default authSlice.reducer;