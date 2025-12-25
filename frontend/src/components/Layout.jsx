import { Link, useLocation } from 'react-router-dom';
import { motion } from 'framer-motion';
import {
  SquaresFour,
  FileText,
  FilePlus,
  FolderOpen,
  ClockCounterClockwise,
  SignOut,
} from 'phosphor-react';

export default function Layout({ children, onLogout }) {
  const location = useLocation();

  const navItems = [
    { path: '/dashboard', label: 'Dashboard', icon: SquaresFour },
    { path: '/entities', label: 'Entities', icon: FolderOpen },
    { path: '/form-filling', label: 'Form Filling', icon: FilePlus },
    { path: '/templates', label: 'Templates', icon: FileText },
    { path: '/recent-forms', label: 'Recent Forms', icon: ClockCounterClockwise },
  ];

  const containerVariants = {
    hidden: { opacity: 0 },
    visible: {
      opacity: 1,
      transition: {
        staggerChildren: 0.05,
        delayChildren: 0.1,
      },
    },
  };

  const itemVariants = {
    hidden: { opacity: 0, x: -10 },
    visible: {
      opacity: 1,
      x: 0,
      transition: { duration: 0.3, ease: 'easeOut' },
    },
  };

  return (
    <div className="flex h-screen bg-[#F7F8FA]">
      {/* Sidebar */}
      <motion.aside
        className="w-64 bg-white border-r border-[#E6E8EB] flex flex-col shadow-sm"
        initial={{ x: -280 }}
        animate={{ x: 0 }}
        transition={{ type: 'spring', stiffness: 100, damping: 20 }}
      >
        {/* Logo/Header */}
        <motion.div
          className="px-6 py-5 border-b border-[#E6E8EB]"
          whileHover={{ backgroundColor: '#F7F8FA' }}
          transition={{ duration: 0.2 }}
        >
          <motion.h1
            className="text-lg font-semibold bg-gradient-to-r from-blue-600 to-indigo-600 bg-clip-text text-transparent"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.3 }}
          >
            AI Form Filling
          </motion.h1>
          <motion.p
            className="text-sm text-muted mt-0.5"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.4 }}
          >
            Document automation
          </motion.p>
        </motion.div>

        {/* Navigation */}
        <motion.nav
          className="flex-1 px-3 py-4 overflow-y-auto"
          variants={containerVariants}
          initial="hidden"
          animate="visible"
        >
          {navItems.map((item, index) => {
            const Icon = item.icon;
            const isActive = location.pathname === item.path;
            return (
              <motion.div key={item.path} variants={itemVariants}>
                <Link
                  to={item.path}
                  aria-current={isActive ? 'page' : undefined}
                  className={`flex items-center gap-3 px-3 py-2 rounded-lg mb-1 transition-all duration-200 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[#2563EB] focus-visible:ring-offset-2 group ${
                    isActive
                      ? 'bg-gradient-to-r from-blue-50 to-indigo-50 text-[#2563EB]'
                      : 'text-secondary hover:bg-[#F7F8FA]'
                  }`}
                >
                  <motion.div
                    whileHover={{ scale: 1.1 }}
                    whileTap={{ scale: 0.95 }}
                  >
                    <Icon
                      size={20}
                      weight={isActive ? 'fill' : 'regular'}
                      className={isActive ? '' : 'text-muted group-hover:text-secondary'}
                    />
                  </motion.div>
                  <span className="text-sm font-medium">{item.label}</span>
                </Link>
              </motion.div>
            );
          })}
        </motion.nav>

        {/* Logout */}
        <motion.div
          className="px-3 py-4 border-t border-[#E6E8EB]"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.5 }}
        >
          <motion.button
            onClick={onLogout}
            className="flex items-center gap-3 px-3 py-2 rounded-lg text-secondary hover:bg-red-50 hover:text-red-600 transition-all duration-200 w-full focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[#2563EB] focus-visible:ring-offset-2"
            whileHover={{ x: 4 }}
            whileTap={{ scale: 0.98 }}
          >
            <SignOut size={20} className="text-muted" />
            <span className="text-sm font-medium">Logout</span>
          </motion.button>
        </motion.div>
      </motion.aside>

      {/* Main Content */}
      <motion.main
        className="flex-1 overflow-auto bg-[#F7F8FA]"
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 0.2, duration: 0.3 }}
      >
        {children}
      </motion.main>
    </div>
  );
}
