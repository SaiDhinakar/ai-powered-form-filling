import { useState } from 'react';
import api from '../services/api';

export default function Login({ onLogin }) {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  // Add a new state for mode
  const [isLogin, setIsLogin] = useState(true);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setIsLoading(true);
    try {
      const endpoint = isLogin ? '/auth/login' : '/auth/signup';
      const payload = {
        email: email,
        password: password
      };

      if (!isLogin) {
        // Signup flow
        await api.post(endpoint, payload);
        // On success, switch to login or auto-login
        // Let's auto-login or just reuse the login logic
        // For simplicity: after signup, call login immediately 
        const loginRes = await api.post('/auth/login', payload);
        const { access_token } = loginRes.data;
        localStorage.setItem('token', access_token);
        onLogin();
      } else {
        // Login flow
        const response = await api.post(endpoint, payload);
        const { access_token } = response.data;
        localStorage.setItem('token', access_token);
        onLogin();
      }
    } catch (error) {
      console.error(isLogin ? 'Login failed:' : 'Signup failed:', error);
      const msg = error.response?.data?.detail || 'Authentication failed. Please check credentials.';
      alert(msg);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex bg-[#ECEFF3]">

      {/* LEFT PANEL */}
      <div
        className="hidden lg:flex lg:w-1/2 items-center px-16"
        style={{
          background:
            'radial-gradient(circle at top left, #F8FAFC 0%, #E5EAF0 40%, #DCE2EA 100%)',
        }}
      >
        <div className="max-w-xl space-y-12">

          {/* Headline */}
          <div>
            <h1 className="text-5xl font-semibold leading-tight text-[#0F172A]">
              Forms,
              <br />
              filled with intent.
            </h1>
            <p className="mt-6 text-lg text-[#475569] max-w-lg leading-relaxed">
              A document system that understands structure, applies intelligence,
              and still leaves the final decision to humans.
            </p>
          </div>

          {/* Visual Block */}
          <div className="bg-[#FDFEFF] border border-[#E6E8EB] rounded-2xl p-8">
            <AnimatedFormSVG />
          </div>

          {/* Statement */}
          <p className="text-sm text-[#475569] max-w-md">
            Designed for real workflows. Built to scale without visual noise.
          </p>

        </div>
      </div>

      {/* RIGHT PANEL */}
      <div className="flex-1 flex items-center justify-center px-8">
        <div className="w-full max-w-lg">

          {/* Mobile headline */}
          <div className="lg:hidden mb-12 text-center">
            <h1 className="text-4xl font-semibold text-[#0F172A]">
              Forms, filled with intent.
            </h1>
            <p className="mt-4 text-base text-[#475569]">
              Sign in to your workspace
            </p>
          </div>

          {/* Login Card */}
          <div className="bg-[#FDFEFF] border border-[#E6E8EB] rounded-2xl p-10">
            <div className="mb-10">
              <h2 className="text-2xl font-semibold text-[#0F172A]">
                {isLogin ? 'Sign in' : 'Create an account'}
              </h2>
              <p className="mt-2 text-base text-[#64748B]">
                {isLogin ? 'Use your organization email' : 'Get started with your free account'}
              </p>
            </div>

            <form onSubmit={handleSubmit} className="space-y-7">
              <input
                type="email"
                placeholder="name@company.com"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                disabled={isLoading}
                required
                className="
                  w-full h-14 px-4 rounded-xl
                  border border-[#E6E8EB]
                  text-base
                  placeholder:text-[#94A3B8]
                  focus:outline-none focus:border-[#2563EB]
                "
              />

              <input
                type="password"
                placeholder="••••••••"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                disabled={isLoading}
                required
                className="
                  w-full h-14 px-4 rounded-xl
                  border border-[#E6E8EB]
                  text-base
                  placeholder:text-[#94A3B8]
                  focus:outline-none focus:border-[#2563EB]
                "
              />

              <button
                type="submit"
                disabled={isLoading}
                className="
                  w-full h-14 rounded-xl
                  bg-[#2563EB] text-white text-base font-medium
                  hover:bg-[#1D4ED8]
                  transition
                  disabled:opacity-60
                "
              >
                {isLoading ? (isLogin ? 'Signing in…' : 'Creating account…') : (isLogin ? 'Continue' : 'Sign up')}
              </button>

              <div className="text-center">
                <button
                  type="button"
                  onClick={() => setIsLogin(!isLogin)}
                  className="text-sm text-[#2563EB] hover:underline"
                >
                  {isLogin ? "Don't have an account? Sign up" : "Already have an account? Sign in"}
                </button>
              </div>
            </form>
          </div>
        </div>
      </div>
    </div>
  );
}

/* ---------- SVG ---------- */

function AnimatedFormSVG() {
  return (
    <svg viewBox="0 0 400 200" className="w-full">
      <rect
        x="20"
        y="20"
        width="360"
        height="160"
        rx="14"
        fill="none"
        stroke="#CBD5E1"
        strokeWidth="1.5"
      />
      {[70, 100, 130].map((y, i) => (
        <line
          key={i}
          x1="60"
          y1={y}
          x2="300"
          y2={y}
          stroke="#64748B"
          strokeWidth="2"
          strokeDasharray="240"
          strokeDashoffset="240"
        >
          <animate
            attributeName="stroke-dashoffset"
            from="240"
            to="0"
            dur="0.9s"
            begin={`${i * 0.5}s`}
            fill="freeze"
          />
        </line>
      ))}
    </svg>
  );
}
