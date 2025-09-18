import { useState, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import { Chart as ChartJS, ArcElement, Tooltip, Legend, CategoryScale, LinearScale, BarElement } from 'chart.js';
import { Doughnut, Bar } from 'react-chartjs-2';
import toast from 'react-hot-toast';
import { 
  ArrowRight, 
  Target, 
  Flame, 
  TrendingUp, 
  Info,
  RefreshCw,
  Download
} from 'lucide-react';

import { dietAPI, transformTDEEToMealPlan } from '@/services/api';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import { MACRO_COLORS, GOALS, ACTIVITY_LEVELS, DIET_TAGS } from '@/utils/constants';
import { formatCalories, formatMacro, calculateMacroPercentages, downloadJSON } from '@/utils/helpers';
import type { AppState } from '@/types/api';

// Register Chart.js components
ChartJS.register(ArcElement, Tooltip, Legend, CategoryScale, LinearScale, BarElement);

interface ResultsPageProps {
  context: AppState & {
    updateNutritionResults: (nutrition: any) => void;
    setLoading: (loading: boolean) => void;
    setError: (error: string | null) => void;
  };
}

export default function ResultsPage({ context }: ResultsPageProps) {
  const navigate = useNavigate();
  const [explanation, setExplanation] = useState<string>('');
  const [loadingExplanation, setLoadingExplanation] = useState(false);

  const { user, nutrition } = context;
  const tdee = nutrition?.tdee;

  // Redirect if no data
  useEffect(() => {
    if (!user || !tdee) {
      navigate('/profile');
    }
  }, [user, tdee, navigate]);

  // Load explanation
  useEffect(() => {
    if (tdee && !explanation) {
      loadExplanation();
    }
  }, [tdee]);

  const loadExplanation = async () => {
    if (!tdee) return;
    
    try {
      setLoadingExplanation(true);
      const response = await dietAPI.explainNutrition({
        calories: tdee.target_calories,
        protein_g: tdee.macro_targets.protein_g,
        fat_g: tdee.macro_targets.fat_g,
        carbs_g: tdee.macro_targets.carbs_g,
        constraints: `${user?.goal} goal, ${user?.activity_level} activity level`,
        diet_tags: user?.diet_preferences || []
      });
      setExplanation(response.explanation);
    } catch (error) {
      console.error('Failed to load explanation:', error);
      setExplanation('Our nutrition recommendations are based on established scientific formulas and your personal profile.');
    } finally {
      setLoadingExplanation(false);
    }
  };

  const generateMealPlan = async () => {
    if (!tdee || !user) return;

    try {
      context.setLoading(true);
      
      const mealPlanRequest = transformTDEEToMealPlan(tdee, {
        days: 7,
        diet_tags: user.diet_preferences || []
      });

      const mealPlan = await dietAPI.generateMealPlan(mealPlanRequest);
      
      context.updateNutritionResults({
        ...nutrition,
        mealPlan
      });

      toast.success('Meal plan generated successfully!');
      navigate('/meal-plan');
      
    } catch (error) {
      console.error('Failed to generate meal plan:', error);
      context.setError(error instanceof Error ? error.message : 'Failed to generate meal plan');
    } finally {
      context.setLoading(false);
    }
  };

  const exportData = () => {
    if (!user || !tdee) return;
    
    const exportData = {
      profile: user,
      nutrition: tdee,
      explanation,
      timestamp: new Date().toISOString()
    };
    
    downloadJSON(exportData, `diet-coach-results-${new Date().toISOString().split('T')[0]}`);
    toast.success('Results exported successfully!');
  };

  if (!user || !tdee) {
    return null;
  }

  // Calculate macro percentages
  const macroPercentages = calculateMacroPercentages(
    tdee.macro_targets.protein_g,
    tdee.macro_targets.fat_g,
    tdee.macro_targets.carbs_g,
    tdee.target_calories
  );

  // Chart data
  const macroChartData = {
    labels: ['Protein', 'Fat', 'Carbohydrates'],
    datasets: [
      {
        data: [
          tdee.macro_targets.protein_g,
          tdee.macro_targets.fat_g,
          tdee.macro_targets.carbs_g
        ],
        backgroundColor: [
          MACRO_COLORS.protein.primary,
          MACRO_COLORS.fat.primary,
          MACRO_COLORS.carbs.primary
        ],
        borderColor: [
          MACRO_COLORS.protein.dark,
          MACRO_COLORS.fat.dark,
          MACRO_COLORS.carbs.dark
        ],
        borderWidth: 2,
        hoverOffset: 4
      }
    ]
  };

  const calorieBreakdownData = {
    labels: ['Protein (4 kcal/g)', 'Fat (9 kcal/g)', 'Carbs (4 kcal/g)'],
    datasets: [
      {
        label: 'Calories',
        data: [
          tdee.macro_targets.protein_g * 4,
          tdee.macro_targets.fat_g * 9,
          tdee.macro_targets.carbs_g * 4
        ],
        backgroundColor: [
          MACRO_COLORS.protein.light,
          MACRO_COLORS.fat.light,
          MACRO_COLORS.carbs.light
        ],
        borderColor: [
          MACRO_COLORS.protein.primary,
          MACRO_COLORS.fat.primary,
          MACRO_COLORS.carbs.primary
        ],
        borderWidth: 1
      }
    ]
  };

  const chartOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        position: 'bottom' as const,
        labels: {
          padding: 20,
          usePointStyle: true
        }
      },
      tooltip: {
        callbacks: {
          label: (context: any) => {
            const label = context.label || '';
            const value = context.parsed;
            const percentage = macroPercentages[label.toLowerCase().split(' ')[0] as keyof typeof macroPercentages];
            return `${label}: ${value}g (${percentage}%)`;
          }
        }
      }
    }
  };

  const currentGoal = GOALS.find(g => g.value === user.goal);
  const currentActivity = ACTIVITY_LEVELS.find(a => a.value === user.activity_level);

  // Render AI explanation as Markdown (GFM)
  const renderExplanation = (text: string) => (
    <div className="prose prose-sm md:prose-base dark:prose-invert max-w-none">
      <ReactMarkdown remarkPlugins={[remarkGfm]}>
        {text}
      </ReactMarkdown>
    </div>
  );

  return (
    <div className="max-w-7xl mx-auto">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6 }}
      >
        {/* Header */}
        <div className="text-center mb-12">
          <h1 className="text-3xl lg:text-4xl font-bold font-display text-gray-900 dark:text-gray-100 mb-4">
            Your Personalized Nutrition Plan
          </h1>
          <p className="text-lg text-gray-600 dark:text-gray-300 max-w-2xl mx-auto">
            Based on your profile, here are your daily nutrition targets and recommendations.
          </p>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Main Results */}
          <div className="lg:col-span-2 space-y-8">
            {/* Key Metrics */}
            <motion.section
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ duration: 0.6, delay: 0.2 }}
              className="card"
            >
              <h2 className="text-xl font-semibold text-gray-900 dark:text-gray-100 mb-6 flex items-center">
                <Target className="w-5 h-5 mr-2 text-primary-500" />
                Daily Targets
              </h2>

              <div className="grid grid-cols-2 md:grid-cols-4 gap-6">
                <div className="text-center">
                  <div className="w-16 h-16 bg-gradient-to-br from-primary-500 to-primary-600 rounded-2xl flex items-center justify-center mx-auto mb-3">
                    <Flame className="w-8 h-8 text-white" />
                  </div>
                  <div className="text-2xl font-bold text-gray-900 dark:text-gray-100">
                    {formatCalories(tdee.target_calories)}
                  </div>
                  <div className="text-sm text-gray-500 dark:text-gray-400">
                    Target Calories
                  </div>
                </div>

                <div className="text-center">
                  <div className="w-16 h-16 bg-gradient-to-br from-red-500 to-red-600 rounded-2xl flex items-center justify-center mx-auto mb-3">
                    <span className="text-white font-bold text-lg">P</span>
                  </div>
                  <div className="text-2xl font-bold text-gray-900 dark:text-gray-100">
                    {formatMacro(tdee.macro_targets.protein_g)}
                  </div>
                  <div className="text-sm text-gray-500 dark:text-gray-400">
                    Protein ({macroPercentages.protein}%)
                  </div>
                </div>

                <div className="text-center">
                  <div className="w-16 h-16 bg-gradient-to-br from-orange-500 to-orange-600 rounded-2xl flex items-center justify-center mx-auto mb-3">
                    <span className="text-white font-bold text-lg">F</span>
                  </div>
                  <div className="text-2xl font-bold text-gray-900 dark:text-gray-100">
                    {formatMacro(tdee.macro_targets.fat_g)}
                  </div>
                  <div className="text-sm text-gray-500 dark:text-gray-400">
                    Fat ({macroPercentages.fat}%)
                  </div>
                </div>

                <div className="text-center">
                  <div className="w-16 h-16 bg-gradient-to-br from-green-500 to-green-600 rounded-2xl flex items-center justify-center mx-auto mb-3">
                    <span className="text-white font-bold text-lg">C</span>
                  </div>
                  <div className="text-2xl font-bold text-gray-900 dark:text-gray-100">
                    {formatMacro(tdee.macro_targets.carbs_g)}
                  </div>
                  <div className="text-sm text-gray-500 dark:text-gray-400">
                    Carbs ({macroPercentages.carbs}%)
                  </div>
                </div>
              </div>
            </motion.section>

            {/* Charts */}
            <motion.section
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ duration: 0.6, delay: 0.4 }}
              className="card"
            >
              <h2 className="text-xl font-semibold text-gray-900 dark:text-gray-100 mb-6 flex items-center">
                <TrendingUp className="w-5 h-5 mr-2 text-blue-500" />
                Macro Distribution
              </h2>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
                <div>
                  <h3 className="text-lg font-medium text-gray-900 dark:text-gray-100 mb-4 text-center">
                    Macronutrient Ratio (grams)
                  </h3>
                  <div className="h-64">
                    <Doughnut data={macroChartData} options={chartOptions} />
                  </div>
                </div>

                <div>
                  <h3 className="text-lg font-medium text-gray-900 dark:text-gray-100 mb-4 text-center">
                    Calorie Breakdown
                  </h3>
                  <div className="h-64">
                    <Bar data={calorieBreakdownData} options={{
                      ...chartOptions,
                      plugins: {
                        ...chartOptions.plugins,
                        tooltip: {
                          callbacks: {
                            label: (context: any) => {
                              return `${context.label}: ${context.parsed.y} kcal`;
                            }
                          }
                        }
                      },
                      scales: {
                        y: {
                          beginAtZero: true,
                          title: {
                            display: true,
                            text: 'Calories'
                          }
                        }
                      }
                    }} />
                  </div>
                </div>
              </div>
            </motion.section>

            {/* Explanation */}
            <motion.section
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ duration: 0.6, delay: 0.6 }}
              className="card"
            >
              <div className="flex items-center justify-between mb-6">
                <h2 className="text-xl font-semibold text-gray-900 dark:text-gray-100 flex items-center">
                  <Info className="w-5 h-5 mr-2 text-purple-500" />
                  AI Explanation
                </h2>
                <button
                  onClick={loadExplanation}
                  disabled={loadingExplanation}
                  className="btn-secondary text-sm"
                >
                  {loadingExplanation ? (
                    <div className="w-4 h-4 border-2 border-gray-500 border-t-transparent rounded-full animate-spin" />
                  ) : (
                    <RefreshCw className="w-4 h-4" />
                  )}
                </button>
              </div>

              <div className="bg-gray-50 dark:bg-gray-800 rounded-xl p-6">
                {loadingExplanation ? (
                  <div className="animate-pulse space-y-3">
                    <div className="h-4 bg-gray-300 dark:bg-gray-600 rounded w-3/4"></div>
                    <div className="h-4 bg-gray-300 dark:bg-gray-600 rounded w-full"></div>
                    <div className="h-4 bg-gray-300 dark:bg-gray-600 rounded w-5/6"></div>
                  </div>
                ) : (
                  renderExplanation(explanation || 'Loading explanation...')
                )}
              </div>
            </motion.section>
          </div>

          {/* Sidebar */}
          <div className="space-y-6">
            {/* Profile Summary */}
            <motion.div
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ duration: 0.6, delay: 0.3 }}
              className="card"
            >
              <h3 className="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-4">
                Profile Summary
              </h3>
              
              <div className="space-y-3">
                <div className="flex justify-between">
                  <span className="text-gray-600 dark:text-gray-400">Sex:</span>
                  <span className="font-medium text-gray-900 dark:text-gray-100">
                    {user.sex === 'male' ? '👨 Male' : '👩 Female'}
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600 dark:text-gray-400">Age:</span>
                  <span className="font-medium text-gray-900 dark:text-gray-100">
                    {user.age} years
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600 dark:text-gray-400">Height:</span>
                  <span className="font-medium text-gray-900 dark:text-gray-100">
                    {user.height_cm} cm
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600 dark:text-gray-400">Weight:</span>
                  <span className="font-medium text-gray-900 dark:text-gray-100">
                    {user.weight_kg} kg
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600 dark:text-gray-400">Activity:</span>
                  <span className="font-medium text-gray-900 dark:text-gray-100">
                    {currentActivity?.icon} {currentActivity?.label}
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600 dark:text-gray-400">Goal:</span>
                  <span className="font-medium text-gray-900 dark:text-gray-100">
                    {currentGoal?.icon} {currentGoal?.label}
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600 dark:text-gray-400">Diet:</span>
                  <span className="font-medium text-gray-900 dark:text-gray-100">
                    {user.diet_preferences && user.diet_preferences.length > 0 ? (
                      <div className="flex flex-wrap gap-1">
                        {user.diet_preferences.map((pref) => {
                          const tag = DIET_TAGS.find(t => t.value === pref);
                          return tag ? (
                            <span key={pref} className="text-xs">
                              {tag.icon}
                            </span>
                          ) : null;
                        })}
                      </div>
                    ) : (
                      'No preferences set'
                    )}
                  </span>
                </div>
              </div>

              <div className="mt-4 pt-4 border-t border-gray-200 dark:border-gray-700">
                <div className="flex justify-between">
                  <span className="text-gray-600 dark:text-gray-400">BMR:</span>
                  <span className="font-medium text-gray-900 dark:text-gray-100">
                    {formatCalories(tdee.bmr)}
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600 dark:text-gray-400">TDEE:</span>
                  <span className="font-medium text-gray-900 dark:text-gray-100">
                    {formatCalories(tdee.tdee)}
                  </span>
                </div>
              </div>
            </motion.div>

            {/* Actions */}
            <motion.div
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ duration: 0.6, delay: 0.5 }}
              className="card space-y-4"
            >
              <h3 className="text-lg font-semibold text-gray-900 dark:text-gray-100">
                Next Steps
              </h3>
              
              <button
                onClick={generateMealPlan}
                disabled={context.loading}
                className="btn-primary w-full group"
              >
                {context.loading ? (
                  <>
                    <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin mr-2" />
                    Generating...
                  </>
                ) : (
                  <>
                    Generate Meal Plan
                    <ArrowRight className="ml-2 w-4 h-4 group-hover:translate-x-1 transition-transform" />
                  </>
                )}
              </button>

              <div className="grid grid-cols-2 gap-2">
                <Link to="/profile" className="btn-secondary text-sm text-center">
                  Edit Profile
                </Link>
                <button onClick={exportData} className="btn-secondary text-sm">
                  <Download className="w-4 h-4 mr-1" />
                  Export
                </button>
              </div>
            </motion.div>
          </div>
        </div>
      </motion.div>
    </div>
  );
}
