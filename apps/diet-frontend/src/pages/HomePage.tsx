import { } from 'react';
import { Link } from 'react-router-dom';
import { motion } from 'framer-motion';
import {
  ArrowRight,
  Calculator,
  UtensilsCrossed,
  Target,
  Sparkles,
  CheckCircle,
  Users,
  TrendingUp
} from 'lucide-react';
import type { AppState } from '@/types/api';

interface HomePageProps {
  context: AppState;
}

export default function HomePage({ context }: HomePageProps) {
  const features = [
    {
      icon: Calculator,
      title: 'Precision Metadata Analysis',
      description: 'Accurate TDEE calculations utilizing advanced bio-metric algorithms and system metadata.',
      color: 'from-blue-600 to-cyan-600'
    },
    {
      icon: UtensilsCrossed,
      title: 'Algorithmic Meal Planning',
      description: 'System-generated nutrition protocols tailored to hyper-specific dietary constraints and goals.',
      color: 'from-emerald-600 to-teal-600'
    },
    {
      icon: Target,
      title: 'Macro-Nutrient Optimization',
      description: 'Data-driven targets for protein, lipid, and carbohydrate intake for peak metabolic performance.',
      color: 'from-purple-600 to-pink-600'
    },
    {
      icon: Sparkles,
      title: 'AI Coaching Interface',
      description: '24/7 intelligent coaching integrated with OpenAI, Gemini, and Local LLM systems for real-time advice.',
      color: 'from-orange-600 to-amber-600'
    }
  ];

  const benefits = [
    'Science-based nutrition calculations',
    'Customizable dietary preferences',
    'Real-time macro tracking',
    'Professional-grade recommendations',
    'Easy-to-follow meal plans',
    'Progress monitoring tools'
  ];

  const stats = [
    { label: 'Accurate TDEE', value: '±5%', icon: Target },
    { label: 'AI Responses', value: '< 2s', icon: Sparkles },
    { label: 'Meals Analysis', value: 'Instant', icon: UtensilsCrossed },
  ];

  return (
    <div className="max-w-7xl mx-auto">
      {/* Hero Section */}
      <motion.section
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6 }}
        className="text-center py-16 lg:py-24"
      >
        <motion.div
          initial={{ scale: 0.9 }}
          animate={{ scale: 1 }}
          transition={{ duration: 0.6, delay: 0.2 }}
          className="mb-8"
        >
          <h1 className="text-4xl lg:text-6xl font-bold font-display mb-6">
            <span className="bg-gradient-to-r from-primary-600 via-secondary-500 to-primary-600 bg-clip-text text-transparent">
              AI-Powered
            </span>
            <br />
            <span className="text-gray-900 dark:text-gray-100">
              Nutrition Coach
            </span>
          </h1>
          <p className="text-xl lg:text-2xl text-gray-600 dark:text-gray-300 max-w-3xl mx-auto leading-relaxed">
            Get personalized nutrition plans, accurate TDEE calculations, and AI-driven meal recommendations
            tailored to your unique goals and preferences.
          </p>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.4 }}
          className="flex flex-col sm:flex-row gap-4 justify-center items-center"
        >
          <Link
            to={context.user ? '/results' : '/profile'}
            className="btn-primary text-lg px-8 py-4 group"
          >
            {context.user ? 'View Your Plan' : 'Get Started'}
            <ArrowRight className="ml-2 w-5 h-5 group-hover:translate-x-1 transition-transform" />
          </Link>

          {context.user && (
            <Link
              to="/profile"
              className="btn-outline text-lg px-8 py-4"
            >
              Update Profile
            </Link>
          )}
        </motion.div>

        {/* Quick Stats */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.6 }}
          className="mt-16 grid grid-cols-1 md:grid-cols-3 gap-8 max-w-4xl mx-auto"
        >
          {stats.map((stat, index) => {
            const Icon = stat.icon;
            return (
              <motion.div
                key={stat.label}
                initial={{ opacity: 0, scale: 0.8 }}
                animate={{ opacity: 1, scale: 1 }}
                transition={{ duration: 0.5, delay: 0.8 + index * 0.1 }}
                className="text-center"
              >
                <div className="inline-flex items-center justify-center w-12 h-12 bg-primary-100 dark:bg-primary-900 rounded-full mb-4">
                  <Icon className="w-6 h-6 text-primary-600 dark:text-primary-400" />
                </div>
                <div className="text-2xl font-bold text-gray-900 dark:text-gray-100">
                  {stat.value}
                </div>
                <div className="text-sm text-gray-600 dark:text-gray-400">
                  {stat.label}
                </div>
              </motion.div>
            );
          })}
        </motion.div>
      </motion.section>

      {/* Features Section */}
      <motion.section
        initial={{ opacity: 0 }}
        whileInView={{ opacity: 1 }}
        viewport={{ once: true }}
        transition={{ duration: 0.8 }}
        className="py-16 lg:py-24"
      >
        <div className="text-center mb-16">
          <h2 className="text-3xl lg:text-4xl font-bold font-display text-gray-900 dark:text-gray-100 mb-4">
            Powerful Features for Your Success
          </h2>
          <p className="text-lg text-gray-600 dark:text-gray-300 max-w-2xl mx-auto">
            Everything you need to achieve your nutrition and fitness goals, powered by cutting-edge AI.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8">
          {features.map((feature, index) => {
            const Icon = feature.icon;
            return (
              <motion.div
                key={feature.title}
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ duration: 0.6, delay: index * 0.1 }}
                whileHover={{ y: -5 }}
                className="card-hover text-center group"
              >
                <div className={`inline-flex items-center justify-center w-16 h-16 bg-gradient-to-br ${feature.color} rounded-2xl mb-6 group-hover:scale-110 transition-transform duration-300`}>
                  <Icon className="w-8 h-8 text-white" />
                </div>
                <h3 className="text-xl font-semibold text-gray-900 dark:text-gray-100 mb-3">
                  {feature.title}
                </h3>
                <p className="text-gray-600 dark:text-gray-300 leading-relaxed">
                  {feature.description}
                </p>
              </motion.div>
            );
          })}
        </div>
      </motion.section>

      {/* Benefits Section */}
      <motion.section
        initial={{ opacity: 0 }}
        whileInView={{ opacity: 1 }}
        viewport={{ once: true }}
        transition={{ duration: 0.8 }}
        className="py-16 lg:py-24 bg-gradient-to-br from-primary-50 to-secondary-50 dark:from-gray-800 dark:to-gray-700 rounded-3xl"
      >
        <div className="max-w-6xl mx-auto px-6">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-12 items-center">
            <div>
              <h2 className="text-3xl lg:text-4xl font-bold font-display text-gray-900 dark:text-gray-100 mb-6">
                Why Choose Diet Coach?
              </h2>
              <p className="text-lg text-gray-600 dark:text-gray-300 mb-8">
                Join thousands of users who have transformed their nutrition journey with our
                evidence-based approach and personalized recommendations.
              </p>

              <div className="space-y-4">
                {benefits.map((benefit, index) => (
                  <motion.div
                    key={benefit}
                    initial={{ opacity: 0, x: -20 }}
                    whileInView={{ opacity: 1, x: 0 }}
                    viewport={{ once: true }}
                    transition={{ duration: 0.5, delay: index * 0.1 }}
                    className="flex items-center space-x-3"
                  >
                    <CheckCircle className="w-5 h-5 text-primary-500 flex-shrink-0" />
                    <span className="text-gray-700 dark:text-gray-200">
                      {benefit}
                    </span>
                  </motion.div>
                ))}
              </div>
            </div>

            <motion.div
              initial={{ opacity: 0, scale: 0.8 }}
              whileInView={{ opacity: 1, scale: 1 }}
              viewport={{ once: true }}
              transition={{ duration: 0.8 }}
              className="relative"
            >
              <div className="bg-white dark:bg-gray-800 rounded-2xl shadow-2xl p-8 relative z-10">
                <div className="flex items-center space-x-4 mb-6">
                  <div className="w-12 h-12 bg-gradient-to-br from-primary-500 to-secondary-500 rounded-full flex items-center justify-center">
                    <TrendingUp className="w-6 h-6 text-white" />
                  </div>
                  <div>
                    <h3 className="text-lg font-semibold text-gray-900 dark:text-gray-100">
                      Success Rate
                    </h3>
                    <p className="text-sm text-gray-500 dark:text-gray-400">
                      Users reaching their goals
                    </p>
                  </div>
                </div>

                <div className="text-4xl font-bold text-primary-600 dark:text-primary-400 mb-2">
                  94%
                </div>

                <p className="text-gray-600 dark:text-gray-300">
                  of our users successfully achieve their nutrition targets within 30 days
                </p>
              </div>

              {/* Decorative elements */}
              <div className="absolute -top-4 -right-4 w-24 h-24 bg-gradient-to-br from-secondary-400 to-primary-400 rounded-full opacity-20 blur-xl"></div>
              <div className="absolute -bottom-4 -left-4 w-32 h-32 bg-gradient-to-br from-primary-400 to-secondary-400 rounded-full opacity-20 blur-xl"></div>
            </motion.div>
          </div>
        </div>
      </motion.section>

      {/* CTA Section */}
      <motion.section
        initial={{ opacity: 0, y: 20 }}
        whileInView={{ opacity: 1, y: 0 }}
        viewport={{ once: true }}
        transition={{ duration: 0.8 }}
        className="py-16 lg:py-24 text-center"
      >
        <div className="max-w-4xl mx-auto">
          <h2 className="text-3xl lg:text-4xl font-bold font-display text-gray-900 dark:text-gray-100 mb-6">
            Ready to Transform Your Nutrition?
          </h2>
          <p className="text-lg text-gray-600 dark:text-gray-300 mb-8">
            Start your personalized nutrition journey today. It takes just 2 minutes to set up.
          </p>

          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Link
              to="/profile"
              className="btn-primary text-lg px-8 py-4 group"
            >
              Create Your Profile
              <Users className="ml-2 w-5 h-5 group-hover:scale-110 transition-transform" />
            </Link>
            <Link
              to="/about"
              className="btn-secondary text-lg px-8 py-4"
            >
              Learn More
            </Link>
          </div>
        </div>
      </motion.section>
    </div>
  );
}
