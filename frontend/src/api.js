import axios from 'axios';

const API_URL = 'http://127.0.0.1:8000';

export const api = axios.create({
  baseURL: API_URL,
});

export const loginUsuario = async (email, password) => {
  const formData = new FormData();
  formData.append('email', email);
  formData.append('password', password);
  const { data } = await api.post('/api/login', formData);
  return data;
};

export const registrarUsuario = async (email, password) => {
  const formData = new FormData();
  formData.append('email', email);
  formData.append('password', password);
  const { data } = await api.post('/api/registro', formData);
  return data;
};

export const limpiarArchivos = async (email, archivos, columnaDuplicados, textoBasura) => {
  const formData = new FormData();
  formData.append('email', email);
  if (columnaDuplicados) formData.append('columna_duplicados', columnaDuplicados);
  if (textoBasura) formData.append('texto_basura', textoBasura);
  
  for (let i = 0; i < archivos.length; i++) {
    formData.append('archivos', archivos[i]);
  }

  const response = await api.post('/api/limpiar', formData, {
    responseType: 'blob', // Importante para recibir el archivo .ZIP binario
  });
  return response.data;
};

export const obtenerHistorial = async (email) => {
  const { data } = await api.get(`/api/historial/${email}`);
  return data.historial;
};

export const crearCheckout = async (email) => {
  const formData = new FormData();
  formData.append('email', email);
  formData.append('url_retorno', window.location.origin);
  const { data } = await api.post('/api/checkout', formData);
  return data.checkout_url;
};