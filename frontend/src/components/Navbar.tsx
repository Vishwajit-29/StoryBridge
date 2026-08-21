import React, { useState, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { Sparkles, BookOpen, Clock, ShieldCheck, User as UserIcon, LogOut, Search, Compass } from 'lucide-react';
import { authApi } from '../services/api';
import { UserProfile } from '../types';

interface NavbarProps {
  onSearch?: (q: string) => void;
}

export const Navbar: React.FC<NavbarProps> = ({ onSearch }) => {
  const navigate = useNavigate();
  const [user, setUser] = useState<UserProfile | null>(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [showAuthModal, setShowAuthModal] = useState(false);
  const [isLogin, setIsLogin] = useState(true);
  const [authForm, setAuthForm] = useState({ username: '', email: '', password: '' });
  const [authError, setAuthError] = useState('');

  useEffect(() => {
    const token = localStorage.getItem('storybridge_token');
    if (token) {
      authApi.getProfile()
        .then((res) => setUser(res.data))
        .catch(() => {
          localStorage.removeItem('storybridge_token');
          setUser(null);
        });
    }
  }, []);

  const handleSearchSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (onSearch) {
      onSearch(searchQuery);
    } else {
      navigate(`/?q=${encodeURIComponent(searchQuery)}`);
    }
  };

  const handleAuthSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setAuthError('');
    try {
      if (isLogin) {
        const res = await authApi.login({ username: authForm.username, password: authForm.password });
        localStorage.setItem('storybridge_token', res.data.token);
        setUser({ id: '', username: res.data.username, email: res.data.email, role: res.data.role as any });
      } else {
        const res = await authApi.register(authForm);
        localStorage.setItem('storybridge_token', res.data.token);
        setUser({ id: '', username: res.data.username, email: res.data.email, role: res.data.role as any });
      }
      setShowAuthModal(false);
      setAuthForm({ username: '', email: '', password: '' });
    } catch (err: any) {
      setAuthError(err.response?.data?.message || err.response?.data?.error || 'Authentication failed');
    }
  };

  const handleLogout = () => {
    localStorage.removeItem('storybridge_token');
    setUser(null);
    navigate('/');
  };

  return (
    <>
      <header className="sticky top-0 z-40 w-full border-b border-slate-800/80 bg-slate-950/85 backdrop-blur-md">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between gap-4">
          
          {/* Logo */}
          <Link to="/" className="flex items-center gap-2.5 group">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-brand-600 via-brand-500 to-indigo-400 flex items-center justify-center shadow-lg shadow-brand-500/20 group-hover:scale-105 transition-transform">
              <Sparkles className="w-5 h-5 text-white" />
            </div>
            <div className="flex flex-col">
              <span className="font-bold text-xl tracking-tight bg-clip-text text-transparent bg-gradient-to-r from-white via-slate-200 to-brand-300">
                StoryBridge
              </span>
              <span className="text-[10px] uppercase tracking-widest text-brand-400 font-semibold -mt-1">
                AI Narrative Engine
              </span>
            </div>
          </Link>

          {/* Search bar */}
          <form onSubmit={handleSearchSubmit} className="hidden md:flex flex-1 max-w-md relative">
            <Search className="absolute left-3.5 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400" />
            <input
              type="text"
              placeholder="Search stories, characters, mythologies..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full pl-10 pr-4 py-2 bg-slate-900/90 border border-slate-800 rounded-full text-sm text-slate-100 placeholder-slate-400 focus:outline-none focus:border-brand-500 focus:ring-1 focus:ring-brand-500 transition-all"
            />
          </form>

          {/* Navigation Items */}
          <div className="flex items-center gap-3">
            <Link
              to="/"
              className="flex items-center gap-1.5 px-3 py-1.5 text-sm font-medium text-slate-300 hover:text-white rounded-lg hover:bg-slate-900 transition-colors"
            >
              <Compass className="w-4 h-4 text-brand-400" />
              <span>Explore</span>
            </Link>

            <Link
              to="/library"
              className="hidden sm:flex items-center gap-1.5 px-3 py-1.5 text-sm font-medium text-slate-300 hover:text-white rounded-lg hover:bg-slate-900 transition-colors"
            >
              <BookOpen className="w-4 h-4 text-brand-400" />
              <span>My Library</span>
            </Link>

            {user?.role === 'ADMIN' || user?.role === 'REVIEWER' ? (
              <Link
                to="/admin"
                className="flex items-center gap-1.5 px-3 py-1.5 text-xs font-semibold text-amber-300 bg-amber-500/10 border border-amber-500/30 rounded-lg hover:bg-amber-500/20 transition-colors"
              >
                <ShieldCheck className="w-4 h-4" />
                <span>Admin CMS</span>
              </Link>
            ) : null}

            {user ? (
              <div className="flex items-center gap-2 pl-2 border-l border-slate-800">
                <div className="flex items-center gap-2 px-2.5 py-1 bg-slate-900 border border-slate-800 rounded-full">
                  <div className="w-6 h-6 rounded-full bg-brand-600 flex items-center justify-center text-xs font-bold text-white uppercase">
                    {user.username.charAt(0)}
                  </div>
                  <span className="text-xs font-medium text-slate-200">{user.username}</span>
                </div>
                <button
                  onClick={handleLogout}
                  title="Log out"
                  className="p-1.5 text-slate-400 hover:text-rose-400 rounded-lg hover:bg-slate-900 transition-colors"
                >
                  <LogOut className="w-4 h-4" />
                </button>
              </div>
            ) : (
              <button
                onClick={() => setShowAuthModal(true)}
                className="flex items-center gap-1.5 px-4 py-2 text-sm font-medium text-white bg-gradient-to-r from-brand-600 to-brand-700 hover:from-brand-500 hover:to-brand-600 rounded-full shadow-md shadow-brand-600/20 transition-all hover:scale-[1.02]"
              >
                <UserIcon className="w-4 h-4" />
                <span>Sign In</span>
              </button>
            )}
          </div>
        </div>
      </header>

      {/* Auth Modal */}
      {showAuthModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/70 backdrop-blur-sm p-4 animate-in fade-in duration-200">
          <div className="bg-slate-900 border border-slate-800 rounded-2xl w-full max-w-md p-6 shadow-2xl relative">
            <button
              onClick={() => setShowAuthModal(false)}
              className="absolute top-4 right-4 text-slate-400 hover:text-white"
            >
              ✕
            </button>

            <h3 className="text-xl font-bold text-white mb-1">
              {isLogin ? 'Welcome back to StoryBridge' : 'Create your account'}
            </h3>
            <p className="text-xs text-slate-400 mb-6">
              {isLogin ? 'Sign in to save bookmarks, sync history, and customize narrations.' : 'Join free to explore multilingual AI storytelling.'}
            </p>

            {authError && (
              <div className="mb-4 p-3 bg-rose-500/10 border border-rose-500/30 rounded-xl text-xs text-rose-300">
                {authError}
              </div>
            )}

            <form onSubmit={handleAuthSubmit} className="space-y-4">
              <div>
                <label className="block text-xs font-medium text-slate-300 mb-1">Username</label>
                <input
                  type="text"
                  required
                  value={authForm.username}
                  onChange={(e) => setAuthForm({ ...authForm, username: e.target.value })}
                  placeholder="e.g. storylover"
                  className="w-full px-3.5 py-2.5 bg-slate-950 border border-slate-800 rounded-xl text-sm text-white focus:outline-none focus:border-brand-500"
                />
              </div>

              {!isLogin && (
                <div>
                  <label className="block text-xs font-medium text-slate-300 mb-1">Email</label>
                  <input
                    type="email"
                    required
                    value={authForm.email}
                    onChange={(e) => setAuthForm({ ...authForm, email: e.target.value })}
                    placeholder="you@domain.com"
                    className="w-full px-3.5 py-2.5 bg-slate-950 border border-slate-800 rounded-xl text-sm text-white focus:outline-none focus:border-brand-500"
                  />
                </div>
              )}

              <div>
                <label className="block text-xs font-medium text-slate-300 mb-1">Password</label>
                <input
                  type="password"
                  required
                  value={authForm.password}
                  onChange={(e) => setAuthForm({ ...authForm, password: e.target.value })}
                  placeholder="••••••••"
                  className="w-full px-3.5 py-2.5 bg-slate-950 border border-slate-800 rounded-xl text-sm text-white focus:outline-none focus:border-brand-500"
                />
              </div>

              <button
                type="submit"
                className="w-full py-2.5 bg-brand-600 hover:bg-brand-500 text-white font-medium text-sm rounded-xl shadow-lg shadow-brand-600/30 transition-all"
              >
                {isLogin ? 'Sign In' : 'Create Account'}
              </button>
            </form>

            <div className="mt-4 pt-4 border-t border-slate-800 text-center">
              <button
                onClick={() => {
                  setIsLogin(!isLogin);
                  setAuthError('');
                }}
                className="text-xs text-brand-400 hover:underline"
              >
                {isLogin ? "Don't have an account? Sign up" : 'Already have an account? Sign in'}
              </button>
            </div>
          </div>
        </div>
      )}
    </>
  );
};
