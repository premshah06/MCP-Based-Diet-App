import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  Calendar, 
  ChefHat, 
  Download,
  ArrowLeft,
  ArrowRight
} from 'lucide-react';
import { Link } from 'react-router-dom';
import toast from 'react-hot-toast';

import { formatCalories, formatMacro, downloadJSON } from '@/utils/helpers';
import type { AppState, Meal } from '@/types/api';

interface MealPlanPageProps {
  context: AppState;
}

export default function MealPlanPage({ context }: MealPlanPageProps) {
  const { nutrition } = context;
  const mealPlan = nutrition?.mealPlan;
  
  const [selectedDay, setSelectedDay] = useState(0);
  const [selectedMeal, setSelectedMeal] = useState<Meal | null>(null);

  if (!mealPlan) {
    return (
      <div className="max-w-4xl mx-auto text-center py-16">
        <div className="mb-8">
          <ChefHat className="w-16 h-16 text-gray-400 mx-auto mb-4" />
          <h1 className="text-2xl font-bold text-gray-900 dark:text-gray-100 mb-2">
            No Meal Plan Generated
          </h1>
          <p className="text-gray-600 dark:text-gray-300">
            Please generate your meal plan from the results page first.
          </p>
        </div>
        <Link to="/results" className="btn-primary">
          Go to Results
        </Link>
      </div>
    );
  }

  const currentDay = mealPlan.days[selectedDay];

  const exportMealPlan = () => {
    const exportData = {
      mealPlan,
      generatedAt: new Date().toISOString(),
      adherenceScore: mealPlan.adherence_score
    };
    
    downloadJSON(exportData, `meal-plan-${new Date().toISOString().split('T')[0]}`);
    toast.success('Meal plan exported successfully!');
  };

  const getMealIcon = (mealName: string) => {
    const name = mealName.toLowerCase();
    if (name.includes('breakfast')) return '🍳';
    if (name.includes('lunch')) return '🥗';
    if (name.includes('dinner')) return '🍽️';
    if (name.includes('snack')) return '🥜';
    return '🍎';
  };

  const getDifficultyColor = (foodCount: number) => {
    if (foodCount <= 3) return 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200';
    if (foodCount <= 5) return 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200';
    return 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200';
  };

  return (
    <div className="max-w-7xl mx-auto">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6 }}
      >
        {/* Header */}
        <div className="text-center mb-8">
          <h1 className="text-3xl lg:text-4xl font-bold font-display text-gray-900 dark:text-gray-100 mb-4">
            Your {mealPlan.days.length}-Day Meal Plan
          </h1>
          <p className="text-lg text-gray-600 dark:text-gray-300 max-w-2xl mx-auto mb-6">
            Personalized meals designed to meet your nutrition goals with a {mealPlan.adherence_score}% adherence score.
          </p>

          {/* Plan Overview */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 max-w-4xl mx-auto">
            <div className="bg-white dark:bg-gray-800 rounded-xl p-4 border border-gray-200 dark:border-gray-700">
              <div className="text-2xl font-bold text-primary-600 dark:text-primary-400">
                {formatCalories(mealPlan.plan_totals.avg_daily_calories)}
              </div>
              <div className="text-sm text-gray-500 dark:text-gray-400">Avg Daily Calories</div>
            </div>
            <div className="bg-white dark:bg-gray-800 rounded-xl p-4 border border-gray-200 dark:border-gray-700">
              <div className="text-2xl font-bold text-red-600 dark:text-red-400">
                {formatMacro(mealPlan.plan_totals.protein / mealPlan.days.length)}
              </div>
              <div className="text-sm text-gray-500 dark:text-gray-400">Avg Protein/Day</div>
            </div>
            <div className="bg-white dark:bg-gray-800 rounded-xl p-4 border border-gray-200 dark:border-gray-700">
              <div className="text-2xl font-bold text-orange-600 dark:text-orange-400">
                {formatMacro(mealPlan.plan_totals.fat / mealPlan.days.length)}
              </div>
              <div className="text-sm text-gray-500 dark:text-gray-400">Avg Fat/Day</div>
            </div>
            <div className="bg-white dark:bg-gray-800 rounded-xl p-4 border border-gray-200 dark:border-gray-700">
              <div className="text-2xl font-bold text-green-600 dark:text-green-400">
                {formatMacro(mealPlan.plan_totals.carbs / mealPlan.days.length)}
              </div>
              <div className="text-sm text-gray-500 dark:text-gray-400">Avg Carbs/Day</div>
            </div>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-4 gap-8">
          {/* Day Navigation */}
          <motion.div
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.6, delay: 0.2 }}
            className="card"
          >
            <div className="flex items-center space-x-2 mb-6">
              <Calendar className="w-5 h-5 text-primary-500" />
              <h2 className="text-lg font-semibold text-gray-900 dark:text-gray-100">
                Days
              </h2>
            </div>

            <div className="space-y-2">
              {mealPlan.days.map((day, index) => (
                <button
                  key={day.day}
                  onClick={() => setSelectedDay(index)}
                  className={`w-full text-left p-4 rounded-xl transition-all ${
                    selectedDay === index
                      ? 'bg-primary-100 dark:bg-primary-900 text-primary-700 dark:text-primary-300 border-2 border-primary-500'
                      : 'bg-gray-50 dark:bg-gray-700 hover:bg-gray-100 dark:hover:bg-gray-600 border-2 border-transparent'
                  }`}
                >
                  <div className="font-medium">Day {day.day}</div>
                  <div className="text-sm text-gray-500 dark:text-gray-400">
                    {formatCalories(day.daily_totals.calories)}
                  </div>
                  <div className="text-xs text-gray-400 dark:text-gray-500">
                    {day.meals.length} meals
                  </div>
                </button>
              ))}
            </div>

            {/* Export Button */}
            <button
              onClick={exportMealPlan}
              className="btn-secondary w-full mt-6"
            >
              <Download className="w-4 h-4 mr-2" />
              Export Plan
            </button>
          </motion.div>

          {/* Day Content */}
          <div className="lg:col-span-3 space-y-6">
            {/* Day Header */}
            <motion.div
              key={selectedDay}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.4 }}
              className="card"
            >
              <div className="flex items-center justify-between mb-4">
                <h2 className="text-2xl font-bold text-gray-900 dark:text-gray-100">
                  Day {currentDay.day}
                </h2>
                <div className="flex items-center space-x-2">
                  <button
                    onClick={() => setSelectedDay(Math.max(0, selectedDay - 1))}
                    disabled={selectedDay === 0}
                    className="btn-secondary p-2 disabled:opacity-50"
                  >
                    <ArrowLeft className="w-4 h-4" />
                  </button>
                  <button
                    onClick={() => setSelectedDay(Math.min(mealPlan.days.length - 1, selectedDay + 1))}
                    disabled={selectedDay === mealPlan.days.length - 1}
                    className="btn-secondary p-2 disabled:opacity-50"
                  >
                    <ArrowRight className="w-4 h-4" />
                  </button>
                </div>
              </div>

              {/* Daily Totals */}
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4 p-4 bg-gray-50 dark:bg-gray-800 rounded-xl">
                <div className="text-center">
                  <div className="text-lg font-bold text-gray-900 dark:text-gray-100">
                    {formatCalories(currentDay.daily_totals.calories)}
                  </div>
                  <div className="text-sm text-gray-500 dark:text-gray-400">Total Calories</div>
                </div>
                <div className="text-center">
                  <div className="text-lg font-bold text-red-600 dark:text-red-400">
                    {formatMacro(currentDay.daily_totals.protein)}
                  </div>
                  <div className="text-sm text-gray-500 dark:text-gray-400">Protein</div>
                </div>
                <div className="text-center">
                  <div className="text-lg font-bold text-orange-600 dark:text-orange-400">
                    {formatMacro(currentDay.daily_totals.fat)}
                  </div>
                  <div className="text-sm text-gray-500 dark:text-gray-400">Fat</div>
                </div>
                <div className="text-center">
                  <div className="text-lg font-bold text-green-600 dark:text-green-400">
                    {formatMacro(currentDay.daily_totals.carbs)}
                  </div>
                  <div className="text-sm text-gray-500 dark:text-gray-400">Carbs</div>
                </div>
              </div>
            </motion.div>

            {/* Meals */}
            <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-6">
              {currentDay.meals.map((meal, mealIndex) => (
                <motion.div
                  key={`${selectedDay}-${mealIndex}`}
                  initial={{ opacity: 0, scale: 0.9 }}
                  animate={{ opacity: 1, scale: 1 }}
                  transition={{ duration: 0.4, delay: mealIndex * 0.1 }}
                  className="card-hover"
                  onClick={() => setSelectedMeal(meal)}
                >
                  <div className="flex items-center space-x-3 mb-4">
                    <span className="text-2xl">{getMealIcon(meal.name)}</span>
                    <div>
                      <h3 className="text-lg font-semibold text-gray-900 dark:text-gray-100">
                        {meal.name}
                      </h3>
                      <div className={`inline-flex items-center px-2 py-1 rounded-full text-xs font-medium ${getDifficultyColor(meal.foods.length)}`}>
                        {meal.foods.length} ingredients
                      </div>
                    </div>
                  </div>

                  {/* Meal Totals */}
                  <div className="grid grid-cols-2 gap-4 mb-4 p-3 bg-gray-50 dark:bg-gray-800 rounded-lg">
                    <div>
                      <div className="text-lg font-bold text-gray-900 dark:text-gray-100">
                        {formatCalories(meal.totals.calories)}
                      </div>
                      <div className="text-xs text-gray-500 dark:text-gray-400">Calories</div>
                    </div>
                    <div className="text-right">
                      <div className="text-sm text-gray-600 dark:text-gray-300">
                        P: {formatMacro(meal.totals.protein)} |{' '}
                        F: {formatMacro(meal.totals.fat)} |{' '}
                        C: {formatMacro(meal.totals.carbs)}
                      </div>
                    </div>
                  </div>

                  {/* Food Preview */}
                  <div className="space-y-2">
                    {meal.foods.slice(0, 3).map((food, foodIndex) => (
                      <div key={foodIndex} className="flex justify-between text-sm">
                        <span className="text-gray-700 dark:text-gray-300 truncate">
                          {food.name}
                        </span>
                        <span className="text-gray-500 dark:text-gray-400 ml-2 flex-shrink-0">
                          {food.amount_g}g
                        </span>
                      </div>
                    ))}
                    {meal.foods.length > 3 && (
                      <div className="text-xs text-gray-500 dark:text-gray-400 text-center pt-2">
                        +{meal.foods.length - 3} more items
                      </div>
                    )}
                  </div>
                </motion.div>
              ))}
            </div>
          </div>
        </div>

        {/* Meal Detail Modal */}
        <AnimatePresence>
          {selectedMeal && (
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              className="fixed inset-0 bg-black bg-opacity-50 backdrop-blur-sm z-50 flex items-center justify-center p-4"
              onClick={() => setSelectedMeal(null)}
            >
              <motion.div
                initial={{ scale: 0.9, opacity: 0 }}
                animate={{ scale: 1, opacity: 1 }}
                exit={{ scale: 0.9, opacity: 0 }}
                className="bg-white dark:bg-gray-800 rounded-2xl p-6 max-w-2xl w-full max-h-[80vh] overflow-y-auto"
                onClick={(e) => e.stopPropagation()}
              >
                <div className="flex items-center justify-between mb-6">
                  <div className="flex items-center space-x-3">
                    <span className="text-3xl">{getMealIcon(selectedMeal.name)}</span>
                    <div>
                      <h3 className="text-2xl font-bold text-gray-900 dark:text-gray-100">
                        {selectedMeal.name}
                      </h3>
                      <p className="text-gray-500 dark:text-gray-400">
                        {selectedMeal.foods.length} ingredients
                      </p>
                    </div>
                  </div>
                  <button
                    onClick={() => setSelectedMeal(null)}
                    className="btn-secondary p-2"
                  >
                    ×
                  </button>
                </div>

                {/* Meal Nutrition */}
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6 p-4 bg-gray-50 dark:bg-gray-800 rounded-xl">
                  <div className="text-center">
                    <div className="text-xl font-bold text-gray-900 dark:text-gray-100">
                      {formatCalories(selectedMeal.totals.calories)}
                    </div>
                    <div className="text-sm text-gray-500 dark:text-gray-400">Calories</div>
                  </div>
                  <div className="text-center">
                    <div className="text-xl font-bold text-red-600 dark:text-red-400">
                      {formatMacro(selectedMeal.totals.protein)}
                    </div>
                    <div className="text-sm text-gray-500 dark:text-gray-400">Protein</div>
                  </div>
                  <div className="text-center">
                    <div className="text-xl font-bold text-orange-600 dark:text-orange-400">
                      {formatMacro(selectedMeal.totals.fat)}
                    </div>
                    <div className="text-sm text-gray-500 dark:text-gray-400">Fat</div>
                  </div>
                  <div className="text-center">
                    <div className="text-xl font-bold text-green-600 dark:text-green-400">
                      {formatMacro(selectedMeal.totals.carbs)}
                    </div>
                    <div className="text-sm text-gray-500 dark:text-gray-400">Carbs</div>
                  </div>
                </div>

                {/* Food List */}
                <div>
                  <h4 className="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-4">
                    Ingredients & Portions
                  </h4>
                  <div className="space-y-3">
                    {selectedMeal.foods.map((food, index) => (
                      <div key={index} className="flex items-center justify-between p-3 bg-gray-50 dark:bg-gray-700 rounded-lg">
                        <div>
                          <div className="font-medium text-gray-900 dark:text-gray-100">
                            {food.name}
                          </div>
                          <div className="text-sm text-gray-500 dark:text-gray-400">
                            {food.amount_g}g · {formatCalories(food.calories)}
                          </div>
                        </div>
                        <div className="text-right text-sm">
                          <div className="text-gray-600 dark:text-gray-300">
                            P: {formatMacro(food.protein)}
                          </div>
                          <div className="text-gray-600 dark:text-gray-300">
                            F: {formatMacro(food.fat)} · C: {formatMacro(food.carbs)}
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              </motion.div>
            </motion.div>
          )}
        </AnimatePresence>
      </motion.div>
    </div>
  );
}
