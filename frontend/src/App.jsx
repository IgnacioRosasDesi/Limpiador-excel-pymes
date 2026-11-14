import { useState, useEffect } from 'react';
import { Zap, Upload, FileSpreadsheet, ShieldCheck, Crown, LogOut, History, Sparkles, CheckCircle2, AlertCircle } from 'lucide-react';
import { loginUsuario, registrarUsuario, limpiarArchivos, obtenerHistorial, crearCheckout } from './api';

export default function App() {
  const [usuario, setUsuario] = useState(() => {
    const guardado = localStorage.getItem('rowrescue_user');
    return guardado ? JSON.parse(guardado) : null;
  });

  // Estados de Auth
  const [vistaAuth, setVistaAuth] = useState('landing'); // 'landing' | 'login' | 'registro'
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [errorAuth, setErrorAuth] = useState('');
  const [cargandoAuth, setCargandoAuth] = useState(false);

  // Estados de Limpieza
  const [archivos, setArchivos] = useState([]);
  const [columnaDup, setColumnaDup] = useState('');
  const [textoBasura, setTextoBasura] = useState('');
  const [procesando, setProcesando] = useState(false);
  const [mensajeExito, setMensajeExito] = useState('');
  const [errorProceso, setErrorProceso] = useState('');
  const [historial, setHistorial] = useState([]);

  useEffect(() => {
    if (usuario?.email) {
      cargarHistorial(usuario.email);
    }
  }, [usuario]);

  const cargarHistorial = async (correo) => {
    try {
      const lista = await obtenerHistorial(correo);
      setHistorial(lista);
    } catch (e) {
      console.error('Error cargando historial', e);
    }
  };

  const manejarAuth = async (e) => {
    e.preventDefault();
    setErrorAuth('');
    setCargandoAuth(true);
    try {
      if (vistaAuth === 'registro') {
        await registrarUsuario(email, password);
      }
      const res = await loginUsuario(email, password);
      setUsuario(res.usuario);
      localStorage.setItem('rowrescue_user', JSON.stringify(res.usuario));
    } catch (err) {
      setErrorAuth(err.response?.data?.detail || 'Error de autenticación. Verifica tus datos.');
    } finally {
      setCargandoAuth(false);
    }
  };

  const cerrarSesion = () => {
    setUsuario(null);
    localStorage.removeItem('rowrescue_user');
    setVistaAuth('landing');
  };

  const manejarLimpieza = async (e) => {
    e.preventDefault();
    if (archivos.length === 0) return;
    setProcesando(true);
    setErrorProceso('');
    setMensajeExito('');

    try {
      const zipBlob = await limpiarArchivos(usuario.email, archivos, columnaDup, textoBasura);
      
      // Descarga automática del ZIP en el navegador
      const url = window.URL.createObjectURL(new Blob([zipBlob]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', 'RowRescue_Limpios.zip');
      document.body.appendChild(link);
      link.click();
      link.remove();

      setMensajeExito('¡Archivos estandarizados y Reporte PDF descargados con éxito!');
      setArchivos([]);
      cargarHistorial(usuario.email);
    } catch (err) {
      if (err.response?.data instanceof Blob) {
        const text = await err.response.data.text();
        const json = JSON.parse(text);
        setErrorProceso(json.detail || 'Error al procesar archivos');
      } else {
        setErrorProceso('Error conectando con el servidor de limpieza.');
      }
    } finally {
      setProcesando(false);
    }
  };

  const irAPagar = async () => {
    try {
      const url = await crearCheckout(usuario.email);
      window.location.href = url;
    } catch {
      alert('No se pudo generar el enlace de Mercado Pago');
    }
  };

  // --- VISTA 1: LANDING & LOGIN ---
  if (!usuario) {
    return (
      <div className="min-h-screen bg-slate-950 text-slate-100 flex flex-col">
        <nav className="border-b border-slate-800 px-6 py-4 flex justify-between items-center max-w-6xl mx-auto w-full">
          <div className="flex items-center gap-2 font-bold text-xl cursor-pointer" onClick={() => setVistaAuth('landing')}>
            <Zap className="text-blue-500 fill-blue-500" />
            <span>Row<span className="text-blue-500">Rescue</span></span>
          </div>
          <div className="flex gap-3">
            <button onClick={() => setVistaAuth('login')} className="px-4 py-2 text-sm text-slate-300 hover:text-white">
              Iniciar Sesión
            </button>
            <button onClick={() => setVistaAuth('registro')} className="px-4 py-2 text-sm bg-blue-600 hover:bg-blue-500 rounded-lg font-medium transition">
              Crear Cuenta Gratis
            </button>
          </div>
        </nav>

        {vistaAuth === 'landing' ? (
          <main className="flex-1 flex flex-col items-center justify-center text-center px-6 max-w-4xl mx-auto py-16">
            <span className="px-3 py-1 rounded-full bg-blue-500/10 text-blue-400 text-xs font-semibold border border-blue-500/20 mb-6">
              Plataforma SaaS para PyMEs y Analistas
            </span>
            <h1 className="text-4xl md:text-6xl font-extrabold tracking-tight mb-6">
              Limpia y estandariza tus planillas Excel en <span className="text-blue-500">segundos</span>
            </h1>
            <p className="text-slate-400 text-lg md:text-xl mb-10 max-w-2xl">
              Elimina duplicados masivos, normaliza RUTs automáticamente, filtra registros basura y descarga tu reporte ejecutivo en PDF con un solo clic.
            </p>
            <button
              onClick={() => setVistaAuth('registro')}
              className="px-8 py-4 bg-blue-600 hover:bg-blue-500 rounded-xl font-bold text-lg shadow-lg shadow-blue-600/25 transition flex items-center gap-2"
            >
              <Sparkles className="w-5 h-5" /> Comenzar Gratis Ahora
            </button>
          </main>
        ) : (
          <main className="flex-1 flex items-center justify-center px-4">
            <form onSubmit={manejarAuth} className="bg-slate-900 border border-slate-800 p-8 rounded-2xl w-full max-w-md shadow-xl">
              <h2 className="text-2xl font-bold mb-2">
                {vistaAuth === 'login' ? 'Bienvenido de vuelta' : 'Crea tu cuenta en RowRescue'}
              </h2>
              <p className="text-slate-400 text-sm mb-6">
                {vistaAuth === 'login' ? 'Ingresa tus credenciales para acceder a tu espacio.' : 'Empieza gratis hoy mismo sin tarjeta de crédito.'}
              </p>

              {errorAuth && (
                <div className="mb-4 p-3 rounded-lg bg-red-500/10 border border-red-500/30 text-red-400 text-sm flex items-center gap-2">
                  <AlertCircle className="w-4 h-4 shrink-0" /> {errorAuth}
                </div>
              )}

              <div className="space-y-4">
                <div>
                  <label className="block text-xs font-medium text-slate-400 mb-1">Correo electrónico</label>
                  <input
                    type="email"
                    required
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    className="w-full px-4 py-2.5 rounded-lg bg-slate-950 border border-slate-800 focus:border-blue-500 focus:outline-none"
                    placeholder="tu@empresa.cl"
                  />
                </div>
                <div>
                  <label className="block text-xs font-medium text-slate-400 mb-1">Contraseña</label>
                  <input
                    type="password"
                    required
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    className="w-full px-4 py-2.5 rounded-lg bg-slate-950 border border-slate-800 focus:border-blue-500 focus:outline-none"
                    placeholder="••••••••"
                  />
                </div>
                <button
                  type="submit"
                  disabled={cargandoAuth}
                  className="w-full py-3 bg-blue-600 hover:bg-blue-500 rounded-lg font-semibold transition disabled:opacity-50"
                >
                  {cargandoAuth ? 'Conectando...' : vistaAuth === 'login' ? 'Entrar a la Plataforma' : 'Registrarme'}
                </button>
              </div>
            </form>
          </main>
        )}
      </div>
    );
  }

  // --- VISTA 2: DASHBOARD PRINCIPAL ---
  return (
    <div className="min-h-screen bg-slate-950 text-slate-100">
      <header className="border-b border-slate-800 bg-slate-900/50 px-6 py-4">
        <div className="max-w-6xl mx-auto flex flex-wrap justify-between items-center gap-4">
          <div className="flex items-center gap-2 font-bold text-xl">
            <Zap className="text-blue-500 fill-blue-500" />
            <span>Row<span className="text-blue-500">Rescue</span></span>
            <span className={`ml-2 text-xs px-2.5 py-0.5 rounded-full font-semibold uppercase ${
              usuario.plan === 'premium' ? 'bg-amber-500/20 text-amber-400 border border-amber-500/30' : 'bg-slate-800 text-slate-400'
            }`}>
              Plan {usuario.plan}
            </span>
          </div>

          <div className="flex items-center gap-4">
            {usuario.plan !== 'premium' && (
              <button
                onClick={irAPagar}
                className="px-3.5 py-1.5 rounded-lg bg-gradient-to-r from-amber-500 to-orange-500 text-slate-950 font-bold text-xs flex items-center gap-1.5 hover:opacity-90 transition"
              >
                <Crown className="w-4 h-4" /> Pasar a Premium ($5.000)
              </button>
            )}
            <span className="text-sm text-slate-400 hidden sm:inline">{usuario.email}</span>
            <button onClick={cerrarSesion} className="p-2 text-slate-400 hover:text-white rounded-lg hover:bg-slate-800" title="Cerrar sesión">
              <LogOut className="w-5 h-5" />
            </button>
          </div>
        </div>
      </header>

      <main className="max-w-6xl mx-auto px-6 py-10 grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Columna Izquierda: Motor de Limpieza */}
        <div className="lg:col-span-2 space-y-6">
          <form onSubmit={manejarLimpieza} className="bg-slate-900 border border-slate-800 rounded-2xl p-6 space-y-6">
            <div>
              <h2 className="text-xl font-bold flex items-center gap-2">
                <FileSpreadsheet className="text-blue-500" /> Nuevo Proceso de Limpieza
              </h2>
              <p className="text-slate-400 text-sm mt-1">
                Sube tus archivos Excel (.xlsx) o CSV. Detectamos y estandarizamos columnas RUT automáticamente.
              </p>
            </div>

            {/* Zona de Archivos */}
            <label className="border-2 border-dashed border-slate-700 hover:border-blue-500 rounded-xl p-8 flex flex-col items-center justify-center cursor-pointer transition bg-slate-950/50">
              <Upload className="w-10 h-10 text-blue-500 mb-3" />
              <span className="font-medium text-slate-200">
                {archivos.length > 0 ? `${archivos.length} archivo(s) seleccionado(s)` : 'Haz clic para seleccionar tus archivos'}
              </span>
              <span className="text-xs text-slate-500 mt-1">
                {usuario.plan === 'premium' ? 'Lotes ilimitados habilitados' : 'Plan Gratuito: 1 archivo por proceso'}
              </span>
              <input
                type="file"
                multiple={usuario.plan === 'premium'}
                accept=".xlsx,.xls,.csv"
                onChange={(e) => setArchivos(Array.from(e.target.files))}
                className="hidden"
              />
            </label>

            {/* Reglas Opcionales */}
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div>
                <label className="block text-xs font-medium text-slate-400 mb-1">
                  Columna clave para duplicados (Opcional)
                </label>
                <input
                  type="text"
                  value={columnaDup}
                  onChange={(e) => setColumnaDup(e.target.value)}
                  placeholder="Ej: RUT o Email"
                  className="w-full px-3.5 py-2 rounded-lg bg-slate-950 border border-slate-800 text-sm focus:border-blue-500 focus:outline-none"
                />
              </div>
              <div>
                <label className="block text-xs font-medium text-slate-400 mb-1">
                  Filtrar palabra clave basura (Opcional)
                </label>
                <input
                  type="text"
                  value={textoBasura}
                  onChange={(e) => setTextoBasura(e.target.value)}
                  placeholder="Ej: PRUEBA o NULO"
                  className="w-full px-3.5 py-2 rounded-lg bg-slate-950 border border-slate-800 text-sm focus:border-blue-500 focus:outline-none"
                />
              </div>
            </div>

            {errorProceso && (
              <div className="p-3.5 rounded-lg bg-red-500/10 border border-red-500/30 text-red-400 text-sm flex items-center gap-2">
                <AlertCircle className="w-4 h-4 shrink-0" /> {errorProceso}
              </div>
            )}

            {mensajeExito && (
              <div className="p-3.5 rounded-lg bg-emerald-500/10 border border-emerald-500/30 text-emerald-400 text-sm flex items-center gap-2">
                <CheckCircle2 className="w-4 h-4 shrink-0" /> {mensajeExito}
              </div>
            )}

            <button
              type="submit"
              disabled={procesando || archivos.length === 0}
              className="w-full py-3.5 bg-blue-600 hover:bg-blue-500 rounded-xl font-bold transition disabled:opacity-40 flex items-center justify-center gap-2"
            >
              <ShieldCheck className="w-5 h-5" />
              {procesando ? 'Procesando y generando PDF...' : 'Limpiar Datos y Descargar ZIP'}
            </button>
          </form>
        </div>

        {/* Columna Derecha: Historial Reciente */}
        <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6 h-fit">
          <h3 className="font-bold text-lg flex items-center gap-2 mb-4">
            <History className="text-blue-500 w-5 h-5" /> Últimas Limpiezas
          </h3>
          {historial.length === 0 ? (
            <p className="text-sm text-slate-500">Aún no tienes procesos registrados.</p>
          ) : (
            <div className="space-y-3">
              {historial.map((item, idx) => (
                <div key={idx} className="p-3 rounded-xl bg-slate-950 border border-slate-800/80 text-xs space-y-1">
                  <div className="flex justify-between text-slate-400">
                    <span>{new Date(item.fecha).toLocaleDateString()}</span>
                    <span className="text-blue-400 font-semibold">{item.num_archivos} arch.</span>
                  </div>
                  <div className="text-slate-200 font-medium">
                    Originales: {item.filas_originales} | Duplicados: -{item.duplicados_eliminados}
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </main>
    </div>
  );
}