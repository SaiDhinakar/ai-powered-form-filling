import { motion } from 'framer-motion';

export default function Loader({ size = 'md', fullScreen = false }) {
  const sizes = {
    sm: 24,
    md: 40,
    lg: 60,
  };

  const containerVariants = {
    animate: {
      transition: {
        staggerChildren: 0.1,
      },
    },
  };

  const dotVariants = {
    animate: {
      y: [0, -10, 0],
      transition: {
        duration: 0.6,
        repeat: Infinity,
        ease: 'easeInOut',
      },
    },
  };

  const loaderContent = (
    <div className="flex items-center justify-center flex-col gap-4">
      <motion.div
        className="flex gap-2"
        variants={containerVariants}
        animate="animate"
      >
        {[0, 1, 2].map((i) => (
          <motion.div
            key={i}
            className="bg-gradient-to-r from-blue-500 to-blue-600 rounded-full"
            style={{
              width: sizes[size],
              height: sizes[size],
            }}
            variants={dotVariants}
          />
        ))}
      </motion.div>
      <motion.p
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 0.3 }}
        className="text-sm text-gray-500 font-medium"
      >
        Loading...
      </motion.p>
    </div>
  );

  if (fullScreen) {
    return (
      <div className="fixed inset-0 bg-white bg-opacity-90 backdrop-blur-sm flex items-center justify-center z-50">
        {loaderContent}
      </div>
    );
  }

  return (
    <div className="flex items-center justify-center py-12">
      {loaderContent}
    </div>
  );
}
