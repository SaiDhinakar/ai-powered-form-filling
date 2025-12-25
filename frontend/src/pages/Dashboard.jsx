import { Link } from 'react-router-dom';
import { motion } from 'framer-motion';
import useLocalStorage from '../hooks/useLocalStorage';

export default function Dashboard() {
  const [entities] = useLocalStorage('entities', []);
  const [templates] = useLocalStorage('templates', []);
  const [recentForms] = useLocalStorage('recentForms', []);

  const stats = [
    { label: 'Entities', value: entities.length, link: '/entities' },
    { label: 'Templates', value: templates.length, link: '/templates' },
    { label: 'Recent forms', value: recentForms.length, link: '/recent-forms' },
  ];

  return (
    <motion.div
      className="min-h-screen bg-[#ECEFF3] px-10 py-10"
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      transition={{ duration: 0.4 }}
    >
      {/* HEADER */}
      <header className="mb-14">
        <h1 className="text-4xl font-semibold text-[#0F172A]">
          Dashboard
        </h1>
        <p className="mt-3 text-lg text-[#475569] max-w-2xl">
          A high-level view of your document system and recent activity.
        </p>
      </header>

      {/* STATS */}
      <section className="grid grid-cols-1 md:grid-cols-3 gap-8 mb-16">
        {stats.map((stat) => (
          <Link key={stat.label} to={stat.link}>
            <motion.div
              className="
                bg-[#FDFEFF]
                border border-[#E6E8EB]
                rounded-2xl
                p-8
                h-full
                cursor-pointer
              "
              whileHover={{ y: -4 }}
              transition={{ duration: 0.2 }}
            >
              <p className="text-sm uppercase tracking-wide text-[#94A3B8]">
                {stat.label}
              </p>

              <p className="mt-6 text-5xl font-semibold text-[#0F172A]">
                {stat.value}
              </p>
            </motion.div>
          </Link>
        ))}
      </section>

      {/* MAIN ACTIONS */}
      <section className="grid grid-cols-1 lg:grid-cols-2 gap-10">
        {/* LEFT: Primary Action */}
        <motion.div
          className="
            bg-[#FDFEFF]
            border border-[#E6E8EB]
            rounded-3xl
            p-10
          "
          initial={{ opacity: 0, y: 12 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
        >
          <h2 className="text-2xl font-semibold text-[#0F172A]">
            Start a new form
          </h2>
          <p className="mt-4 text-base text-[#475569] max-w-md">
            Upload a document, extract fields, review AI suggestions,
            and finalize with confidence.
          </p>

          <Link
            to="/form-filling"
            className="
              inline-block
              mt-8
              px-6
              py-3
              rounded-xl
              bg-[#2563EB]
              text-white
              text-base
              font-medium
              hover:bg-[#1D4ED8]
              transition
            "
          >
            Fill a form
          </Link>
        </motion.div>

        {/* RIGHT: Secondary Action */}
        <motion.div
          className="
            bg-[#F4F6F8]
            border border-[#E6E8EB]
            rounded-3xl
            p-10
          "
          initial={{ opacity: 0, y: 12 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.3 }}
        >
          <h2 className="text-2xl font-semibold text-[#0F172A]">
            Manage entities
          </h2>
          <p className="mt-4 text-base text-[#475569] max-w-md">
            Maintain structured entities and templates
            that power accurate form filling.
          </p>

          <Link
            to="/entities"
            className="
              inline-block
              mt-8
              px-6
              py-3
              rounded-xl
              border border-[#E6E8EB]
              text-[#0F172A]
              text-base
              font-medium
              hover:bg-[#F7F8FA]
              transition
            "
          >
            View entities
          </Link>
        </motion.div>
      </section>
    </motion.div>
  );
}
