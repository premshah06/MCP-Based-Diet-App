import { } from 'react';
import { motion } from 'framer-motion';
import {
  Brain,
  Calculator,
  Shield,
  Zap,
  Target,
  Users,
  Award,
  Lightbulb,
  Heart,
  Sparkles,
  ArrowRight,
  ExternalLink
} from 'lucide-react';
import { Link } from 'react-router-dom';
import type { AppState } from '@/types/api';

interface AboutPageProps {
  context: AppState;
}

export default function AboutPage({ context }: AboutPageProps) {
  const features = [
    {
      icon: Calculator,
      title: 'Precision TDEE Calculations',
      description: 'Our advanced algorithms use the Mifflin-St Jeor equation combined with activity factor analysis to provide accurate Total Daily Energy Expenditure calculations within ±5% accuracy.',
      color: 'from-blue-500 to-cyan-500'
    },
    {
      icon: Brain,
      title: 'AI-Powered Insights',
      description: 'Leveraging machine learning and nutritional science, our AI provides personalized recommendations and explanations tailored to your unique profile and goals.',
      color: 'from-purple-500 to-pink-500'
    },
    {
      icon: Target,
      title: 'Macro Optimization',
      description: 'Evidence-based macronutrient distribution optimized for your specific goals - whether cutting, maintaining, or bulking - following ISSN and ACSM guidelines.',
      color: 'from-green-500 to-emerald-500'
    },
    {
      icon: Shield,
      title: 'Science-Backed Approach',
      description: 'Every recommendation is based on peer-reviewed research from sports nutrition, exercise science, and metabolism studies. No fad diets, just proven science.',
      color: 'from-orange-500 to-red-500'
    }
  ];

  const methodologies = [
    {
      title: 'Basal Metabolic Rate (BMR)',
      description: 'Calculated using the Mifflin-St Jeor equation, the gold standard for BMR estimation.',
      formula: 'Men: (10 × weight) + (6.25 × height) - (5 × age) + 5',
      accuracy: '±5%'
    },
    {
      title: 'Activity Factor',
      description: 'Research-validated multipliers based on exercise frequency and intensity.',
      formula: 'TDEE = BMR × Activity Factor (1.2 - 1.9)',
      accuracy: '±10%'
    },
    {
      title: 'Caloric Adjustment',
      description: 'Goal-specific caloric modifications based on sustainable weight change rates.',
      formula: 'Cut: -20% | Maintain: 0% | Bulk: +15%',
      accuracy: '±15%'
    }
  ];

  const benefits = [
    { icon: Zap, title: 'Instant Results', description: 'Get your personalized nutrition plan in under 2 minutes' },
    { icon: Heart, title: 'Health-Focused', description: 'Sustainable approaches that prioritize long-term health' },
    { icon: Users, title: 'Personalized', description: 'Tailored to your unique body composition and lifestyle' },
    { icon: Award, title: 'Evidence-Based', description: 'Backed by the latest sports nutrition research' },
    { icon: Lightbulb, title: 'Educational', description: 'Learn the science behind your nutrition plan' },
    { icon: Sparkles, title: 'AI-Enhanced', description: 'Continuously improving through machine learning' }
  ];

  return (
    <div className="max-w-7xl mx-auto">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6 }}
      >
        {/* Hero Section */}
        <div className="text-center py-16">
          <motion.h1
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.2 }}
            className="text-4xl lg:text-5xl font-bold font-display text-gray-900 dark:text-gray-100 mb-6"
          >
            The Science Behind{' '}
            <span className="bg-gradient-to-r from-primary-600 to-secondary-500 bg-clip-text text-transparent">
              Diet Coach
            </span>
          </motion.h1>
          <motion.p
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.4 }}
            className="text-xl text-gray-600 dark:text-gray-300 max-w-3xl mx-auto"
          >
            Discover how we combine cutting-edge AI with evidence-based nutrition science
            to deliver personalized meal plans and accurate TDEE calculations.
          </motion.p>
        </div>

        {/* Features Section */}
        <motion.section
          initial={{ opacity: 0 }}
          whileInView={{ opacity: 1 }}
          viewport={{ once: true }}
          transition={{ duration: 0.8 }}
          className="py-16"
        >
          <h2 className="text-3xl font-bold font-display text-center text-gray-900 dark:text-gray-100 mb-12">
            Core Features & Technologies
          </h2>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
            {features.map((feature, index) => {
              const Icon = feature.icon;
              return (
                <motion.div
                  key={feature.title}
                  initial={{ opacity: 0, y: 20 }}
                  whileInView={{ opacity: 1, y: 0 }}
                  viewport={{ once: true }}
                  transition={{ duration: 0.6, delay: index * 0.1 }}
                  className="card"
                >
                  <div className={`inline-flex items-center justify-center w-12 h-12 bg-gradient-to-br ${feature.color} rounded-xl mb-4`}>
                    <Icon className="w-6 h-6 text-white" />
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

        {/* Methodology Section */}
        <motion.section
          initial={{ opacity: 0 }}
          whileInView={{ opacity: 1 }}
          viewport={{ once: true }}
          transition={{ duration: 0.8 }}
          className="py-16 bg-gradient-to-br from-gray-50 to-white dark:from-gray-800 dark:to-gray-700 rounded-3xl"
        >
          <div className="max-w-6xl mx-auto px-6">
            <h2 className="text-3xl font-bold font-display text-center text-gray-900 dark:text-gray-100 mb-12">
              Our Scientific Methodology
            </h2>

            <div className="space-y-8">
              {methodologies.map((method, index) => (
                <motion.div
                  key={method.title}
                  initial={{ opacity: 0, x: index % 2 === 0 ? -20 : 20 }}
                  whileInView={{ opacity: 1, x: 0 }}
                  viewport={{ once: true }}
                  transition={{ duration: 0.6, delay: index * 0.2 }}
                  className="bg-white dark:bg-gray-800 rounded-2xl p-6 shadow-lg"
                >
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-6 items-center">
                    <div>
                      <h3 className="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-2">
                        {method.title}
                      </h3>
                      <p className="text-gray-600 dark:text-gray-300">
                        {method.description}
                      </p>
                    </div>
                    <div className="md:col-span-2">
                      <div className="bg-gray-50 dark:bg-gray-700 rounded-lg p-4">
                        <div className="font-mono text-sm text-gray-800 dark:text-gray-200 mb-2">
                          {method.formula}
                        </div>
                        <div className="flex items-center justify-between">
                          <span className="text-xs text-gray-500 dark:text-gray-400">
                            Accuracy: {method.accuracy}
                          </span>
                          <div className="w-16 h-2 bg-green-200 dark:bg-green-800 rounded-full">
                            <div
                              className="h-full bg-green-500 rounded-full"
                              style={{ width: `${100 - parseInt(method.accuracy.replace(/[^0-9]/g, ''))}%` }}
                            ></div>
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>
                </motion.div>
              ))}
            </div>
          </div>
        </motion.section>

        {/* Benefits Grid */}
        <motion.section
          initial={{ opacity: 0 }}
          whileInView={{ opacity: 1 }}
          viewport={{ once: true }}
          transition={{ duration: 0.8 }}
          className="py-16"
        >
          <h2 className="text-3xl font-bold font-display text-center text-gray-900 dark:text-gray-100 mb-12">
            Why Choose Diet Coach?
          </h2>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {benefits.map((benefit, index) => {
              const Icon = benefit.icon;
              return (
                <motion.div
                  key={benefit.title}
                  initial={{ opacity: 0, scale: 0.9 }}
                  whileInView={{ opacity: 1, scale: 1 }}
                  viewport={{ once: true }}
                  transition={{ duration: 0.5, delay: index * 0.1 }}
                  className="card text-center group hover:shadow-xl transition-all duration-300"
                >
                  <div className="w-12 h-12 bg-primary-100 dark:bg-primary-900 rounded-xl flex items-center justify-center mx-auto mb-4 group-hover:scale-110 transition-transform">
                    <Icon className="w-6 h-6 text-primary-600 dark:text-primary-400" />
                  </div>
                  <h3 className="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-2">
                    {benefit.title}
                  </h3>
                  <p className="text-gray-600 dark:text-gray-300">
                    {benefit.description}
                  </p>
                </motion.div>
              );
            })}
          </div>
        </motion.section>

        {/* Technical Details */}
        <motion.section
          initial={{ opacity: 0 }}
          whileInView={{ opacity: 1 }}
          viewport={{ once: true }}
          transition={{ duration: 0.8 }}
          className="py-16"
        >
          <div className="max-w-4xl mx-auto">
            <h2 className="text-3xl font-bold font-display text-center text-gray-900 dark:text-gray-100 mb-12">
              Technical Architecture
            </h2>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
              <div className="card">
                <h3 className="text-xl font-semibold text-gray-900 dark:text-gray-100 mb-4">
                  Frontend Technologies
                </h3>
                <ul className="space-y-2 text-gray-600 dark:text-gray-300">
                  <li>• React 18 with TypeScript for type safety</li>
                  <li>• Tailwind CSS for responsive design</li>
                  <li>• Framer Motion for smooth animations</li>
                  <li>• Chart.js for data visualizations</li>
                  <li>• Progressive Web App capabilities</li>
                </ul>
              </div>

              <div className="card">
                <h3 className="text-xl font-semibold text-gray-900 dark:text-gray-100 mb-4">
                  Backend Technologies
                </h3>
                <ul className="space-y-2 text-gray-600 dark:text-gray-300">
                  <li>• FastAPI for high-performance APIs</li>
                  <li>• Python with Pydantic for data validation</li>
                  <li>• Multi-Model AI Orchestration (OpenAI, Gemini, HF)</li>
                  <li>• Docker containerization</li>
                  <li>• MCP (Model Context Protocol) support</li>
                </ul>
              </div>
            </div>
          </div>
        </motion.section>

        {/* CTA Section */}
        <motion.section
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.8 }}
          className="py-16 text-center"
        >
          <div className="max-w-4xl mx-auto">
            <h2 className="text-3xl font-bold font-display text-gray-900 dark:text-gray-100 mb-6">
              Ready to Experience the Science?
            </h2>
            <p className="text-lg text-gray-600 dark:text-gray-300 mb-8">
              Join thousands of users who trust our evidence-based approach to nutrition planning.
            </p>

            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <Link
                to={context.user ? '/results' : '/profile'}
                className="btn-primary text-lg px-8 py-4 group"
              >
                {context.user ? 'View Your Plan' : 'Start Your Journey'}
                <ArrowRight className="ml-2 w-5 h-5 group-hover:translate-x-1 transition-transform" />
              </Link>
              <a
                href="https://github.com/diet-coach"
                target="_blank"
                rel="noopener noreferrer"
                className="btn-outline text-lg px-8 py-4 group"
              >
                View Source Code
                <ExternalLink className="ml-2 w-5 h-5 group-hover:scale-110 transition-transform" />
              </a>
            </div>
          </div>
        </motion.section>
      </motion.div>
    </div>
  );
}
