import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  Calendar,
  ChefHat,
  Download,
  ArrowLeft,
  ArrowRight,
  Coffee,
  Salad,
  Carrot,
  Apple,
  Utensils,
  ShoppingBag,
  Clock,
  ChevronRight
} from 'lucide-react';
import { Link } from 'react-router-dom';
import toast from 'react-hot-toast';

import { formatCalories, formatMacro, downloadJSON } from '@/utils/helpers';
import type { AppState, Meal } from '@/types/api';

const MealIcon = ({ name, className = "w-5 h-5" }: { name: string; className?: string }) => {
  const lowerName = name.toLowerCase();
  if (lowerName.includes('breakfast')) return <Coffee className={className} />;
  if (lowerName.includes('lunch')) return <Salad className={className} />;
  if (lowerName.includes('dinner')) return <Utensils className={className} />;
  if (lowerName.includes('snack')) return <Carrot className={className} />;
  return <Apple className={className} />;
};

const getDifficultyColor = (foodCount: number) => {
  if (foodCount <= 3) return 'bg-emerald-100 text-emerald-800 dark:bg-emerald-900/30 dark:text-emerald-400';
  if (foodCount <= 5) return 'bg-amber-100 text-amber-800 dark:bg-amber-900/30 dark:text-amber-400';
  return 'bg-rose-100 text-rose-800 dark:bg-rose-900/30 dark:text-rose-400';
};

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
      <div className="max-w-4xl mx-auto text-center py-24">
        <div className="mb-10">
          <div className="w-20 h-20 bg-gray-100 dark:bg-gray-800 rounded-3xl flex items-center justify-center mx-auto mb-6">
            <ChefHat className="w-10 h-10 text-gray-400" />
          </div>
          <h1 className="text-3xl font-bold text-gray-900 dark:text-gray-100 mb-4">
            No Meal Plan Generated
          </h1>
          <p className="text-lg text-gray-600 dark:text-gray-300 max-w-md mx-auto">
            Your personalized nutrition architecture is waiting. Start by generating a plan from your results.
          </p>
        </div>
        <Link to="/results" className="btn-primary px-8 py-3">
          Return to Results
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

  return (
    <div className="max-w-7xl mx-auto pb-12">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6 }}
      >
        {/* Header Section */}
        <div className="flex flex-col lg:flex-row lg:items-end justify-between gap-8 mb-12">
          <div className="max-w-2xl">
            <h1 className="text-4xl lg:text-5xl font-extrabold font-display text-gray-900 dark:text-gray-100 mb-6 tracking-tight">
              {mealPlan.days.length}-Day Performance Plan
            </h1>
            <div className="flex flex-wrap gap-4">
              <div className="flex items-center gap-2 px-4 py-2 bg-emerald-50 dark:bg-emerald-900/20 text-emerald-700 dark:text-emerald-400 rounded-xl text-sm font-bold border border-emerald-100 dark:border-emerald-800">
                <div className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse" />
                {mealPlan.adherence_score}% Adherence Score
              </div>
              <div className="flex items-center gap-2 px-4 py-2 bg-blue-50 dark:bg-blue-900/20 text-blue-700 dark:text-blue-400 rounded-xl text-sm font-bold border border-blue-100 dark:border-blue-800">
                <Calendar className="w-4 h-4" />
                Current Cycle: Day {currentDay.day}
              </div>
            </div>
          </div>

          <div className="flex items-center gap-3">
            <button
              onClick={context.openGroceryList}
              className="flex items-center gap-2 px-6 py-3 bg-gradient-to-r from-orange-500 to-orange-600 hover:from-orange-600 hover:to-orange-700 text-white 
                       rounded-2xl transition-all shadow-xl shadow-orange-500/20 font-bold"
            >
              <ShoppingBag className="w-5 h-5" />
              Smart Grocery List
            </button>
            <button
              onClick={exportMealPlan}
              className="p-3 bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-2xl text-gray-600 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-750 transition-colors shadow-sm"
              title="Export Plan"
            >
              <Download className="w-5 h-5" />
            </button>
          </div>
        </div>

        {/* Nutrition Overview Stats */}
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-6 mb-12">
          <div className="bg-white dark:bg-gray-800/50 backdrop-blur-sm rounded-3xl p-6 border border-gray-100 dark:border-gray-700 shadow-xl shadow-gray-200/50 dark:shadow-none">
            <div className="text-sm font-bold text-gray-500 dark:text-gray-400 mb-2 uppercase tracking-widest">Average Daily Energy</div>
            <div className="text-3xl font-black text-gray-900 dark:text-white font-display">
              {formatCalories(mealPlan.plan_totals.avg_daily_calories)}
            </div>
            <div className="mt-2 h-1.5 w-full bg-gray-100 dark:bg-gray-700 rounded-full overflow-hidden">
              <div className="h-full bg-primary-500 w-full" />
            </div>
          </div>
          <div className="bg-white dark:bg-gray-800/50 backdrop-blur-sm rounded-3xl p-6 border border-gray-100 dark:border-gray-700 shadow-xl shadow-gray-200/50 dark:shadow-none">
            <div className="text-sm font-bold text-rose-500 dark:text-rose-400 mb-2 uppercase tracking-widest">Daily Protein Target</div>
            <div className="text-3xl font-black text-gray-900 dark:text-white font-display">
              {formatMacro(mealPlan.plan_totals.protein / mealPlan.days.length)}
            </div>
            <div className="mt-2 h-1.5 w-full bg-rose-100 dark:bg-rose-900/30 rounded-full overflow-hidden">
              <div className="h-full bg-rose-500 w-3/4" />
            </div>
          </div>
          <div className="bg-white dark:bg-gray-800/50 backdrop-blur-sm rounded-3xl p-6 border border-gray-100 dark:border-gray-700 shadow-xl shadow-gray-200/50 dark:shadow-none">
            <div className="text-sm font-bold text-amber-500 dark:text-amber-400 mb-2 uppercase tracking-widest">Daily Fat Target</div>
            <div className="text-3xl font-black text-gray-900 dark:text-white font-display">
              {formatMacro(mealPlan.plan_totals.fat / mealPlan.days.length)}
            </div>
            <div className="mt-2 h-1.5 w-full bg-amber-100 dark:bg-amber-900/30 rounded-full overflow-hidden">
              <div className="h-full bg-amber-500 w-1/2" />
            </div>
          </div>
          <div className="bg-white dark:bg-gray-800/50 backdrop-blur-sm rounded-3xl p-6 border border-gray-100 dark:border-gray-700 shadow-xl shadow-gray-200/50 dark:shadow-none">
            <div className="text-sm font-bold text-emerald-500 dark:text-emerald-400 mb-2 uppercase tracking-widest">Daily Carb Target</div>
            <div className="text-3xl font-black text-gray-900 dark:text-white font-display">
              {formatMacro(mealPlan.plan_totals.carbs / mealPlan.days.length)}
            </div>
            <div className="mt-2 h-1.5 w-full bg-emerald-100 dark:bg-emerald-900/30 rounded-full overflow-hidden">
              <div className="h-full bg-emerald-500 w-2/3" />
            </div>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-4 gap-8">
          {/* Daily Sidebar Navigation */}
          <div className="space-y-4">
            <div className="bg-white dark:bg-gray-800 rounded-3xl p-6 border border-gray-100 dark:border-gray-700">
              <h2 className="text-sm font-black text-gray-400 uppercase tracking-widest mb-6 px-2">Timeline</h2>
              <div className="space-y-3">
                {mealPlan.days.map((day, index) => (
                  <button
                    key={day.day}
                    onClick={() => setSelectedDay(index)}
                    className={`w-full group relative flex items-center justify-between p-4 rounded-2xl transition-all duration-300
                              ${selectedDay === index
                        ? 'bg-primary-500 text-white shadow-lg shadow-primary-500/25'
                        : 'bg-gray-50 dark:bg-gray-900/50 text-gray-600 dark:text-gray-400 hover:bg-gray-100 dark:hover:bg-gray-700 border border-transparent'
                      }`}
                  >
                    <div className="flex items-center gap-3">
                      <div className={`w-8 h-8 rounded-lg flex items-center justify-center font-bold text-xs
                                    ${selectedDay === index ? 'bg-white/20' : 'bg-gray-200 dark:bg-gray-800'}`}>
                        {day.day}
                      </div>
                      <div className="text-left font-bold tracking-tight">Day {day.day}</div>
                    </div>
                    {selectedDay === index ? (
                      <ChevronRight className="w-4 h-4" />
                    ) : (
                      <div className="text-xs font-bold opacity-60">
                        {Math.round(day.daily_totals.calories)} kcal
                      </div>
                    )}
                  </button>
                ))}
              </div>
            </div>

            <div className="bg-gradient-to-br from-gray-900 to-black rounded-3xl p-6 text-white overflow-hidden relative">
              <div className="relative z-10">
                <h3 className="text-xl font-bold mb-2 italic">Pro Tip</h3>
                <p className="text-gray-400 text-sm leading-relaxed">
                  Consistency is the primary driver of nutritional success. Stick to this plan for 14 days to see metabolic adaptation.
                </p>
              </div>
              <Utensils className="absolute -bottom-4 -right-4 w-24 h-24 text-white/5 rotate-12" />
            </div>
          </div>

          {/* Detailed Day Content */}
          <div className="lg:col-span-3 space-y-8">
            {/* Day Performance Card */}
            <motion.div
              key={selectedDay}
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ duration: 0.4 }}
              className="bg-white dark:bg-gray-800 rounded-[2.5rem] p-8 border border-gray-100 dark:border-gray-700 shadow-sm"
            >
              <div className="flex items-center justify-between mb-8 pb-8 border-b border-gray-100 dark:border-gray-700">
                <div>
                  <h2 className="text-3xl font-black text-gray-900 dark:text-gray-100 mb-1">
                    System Configuration: Day {currentDay.day}
                  </h2>
                  <p className="text-gray-500 font-medium">Precision-balanced micro & macro nutrients</p>
                </div>
                <div className="flex items-center gap-2">
                  <button
                    onClick={() => setSelectedDay(Math.max(0, selectedDay - 1))}
                    disabled={selectedDay === 0}
                    className="p-3 rounded-2xl bg-gray-50 dark:bg-gray-700 hover:bg-gray-100 dark:hover:bg-gray-600 disabled:opacity-30 transition-all border border-gray-100 dark:border-gray-600"
                  >
                    <ArrowLeft className="w-5 h-5" />
                  </button>
                  <button
                    onClick={() => setSelectedDay(Math.min(mealPlan.days.length - 1, selectedDay + 1))}
                    disabled={selectedDay === mealPlan.days.length - 1}
                    className="p-3 rounded-2xl bg-gray-50 dark:bg-gray-700 hover:bg-gray-100 dark:hover:bg-gray-600 disabled:opacity-30 transition-all border border-gray-100 dark:border-gray-600"
                  >
                    <ArrowRight className="w-5 h-5" />
                  </button>
                </div>
              </div>

              {/* Day Visual Breakdown */}
              <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
                {[
                  { label: 'Energy', value: formatCalories(currentDay.daily_totals.calories), color: 'bg-primary-500' },
                  { label: 'Protein', value: formatMacro(currentDay.daily_totals.protein), color: 'bg-rose-500' },
                  { label: 'Lipids', value: formatMacro(currentDay.daily_totals.fat), color: 'bg-amber-500' },
                  { label: 'Carbs', value: formatMacro(currentDay.daily_totals.carbs), color: 'bg-emerald-500' },
                ].map((stat) => (
                  <div key={stat.label} className="p-4 rounded-2xl bg-gray-50 dark:bg-gray-900/50 border border-gray-100 dark:border-gray-700">
                    <div className="text-[10px] font-black uppercase tracking-widest text-gray-400 mb-1">{stat.label}</div>
                    <div className="text-xl font-bold text-gray-900 dark:text-white leading-none">{stat.value}</div>
                  </div>
                ))}
              </div>
            </motion.div>

            {/* Meal Matrix */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {currentDay.meals.map((meal, mealIndex) => (
                <motion.div
                  key={`${selectedDay}-${mealIndex}`}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ duration: 0.4, delay: mealIndex * 0.1 }}
                  whileHover={{ y: -4 }}
                  className="bg-white dark:bg-gray-800 rounded-[2rem] p-6 border border-gray-100 dark:border-gray-700 shadow-sm cursor-pointer hover:shadow-xl hover:shadow-gray-200/50 dark:hover:shadow-none transition-all group"
                  onClick={() => setSelectedMeal(meal)}
                >
                  <div className="flex items-center justify-between mb-6">
                    <div className="flex items-center space-x-4">
                      <div className="w-12 h-12 rounded-2xl bg-primary-50 dark:bg-primary-900/50 flex items-center justify-center text-primary-600 dark:text-primary-400 group-hover:scale-110 transition-transform">
                        <MealIcon name={meal.name} className="w-6 h-6" />
                      </div>
                      <div>
                        <h3 className="text-xl font-bold text-gray-900 dark:text-gray-100 group-hover:text-primary-600 transition-colors">
                          {meal.name}
                        </h3>
                        <div className={`mt-1 inline-flex items-center px-2 py-0.5 rounded-full text-[10px] font-black uppercase tracking-wider ${getDifficultyColor(meal.foods.length)}`}>
                          {meal.foods.length} Nodes
                        </div>
                      </div>
                    </div>
                  </div>

                  <div className="mb-6 p-4 bg-gray-50 dark:bg-gray-900/50 rounded-2xl flex items-center justify-between">
                    <div>
                      <div className="text-2xl font-black text-gray-900 dark:text-white">
                        {Math.round(meal.totals.calories)}
                      </div>
                      <div className="text-[10px] font-black uppercase tracking-widest text-gray-400">Kilocalories</div>
                    </div>
                    <div className="h-10 w-px bg-gray-200 dark:bg-gray-700 mx-2" />
                    <div className="flex-1 px-2 flex justify-between text-center overflow-x-auto gap-2">
                      <div>
                        <div className="text-xs font-bold text-rose-500">P</div>
                        <div className="text-[10px] font-bold text-gray-500">{Math.round(meal.totals.protein)}g</div>
                      </div>
                      <div>
                        <div className="text-xs font-bold text-amber-500">F</div>
                        <div className="text-[10px] font-bold text-gray-500">{Math.round(meal.totals.fat)}g</div>
                      </div>
                      <div>
                        <div className="text-xs font-bold text-emerald-500">C</div>
                        <div className="text-[10px] font-bold text-gray-500">{Math.round(meal.totals.carbs)}g</div>
                      </div>
                    </div>
                  </div>

                  <div className="space-y-3">
                    {meal.foods.slice(0, 3).map((food, foodIndex) => (
                      <div key={foodIndex} className="flex justify-between items-center text-sm border-b border-gray-50 dark:border-gray-700 pb-2 last:border-0 last:pb-0">
                        <span className="text-gray-600 dark:text-gray-300 font-medium truncate pr-4">
                          {food.name}
                        </span>
                        <span className="text-xs font-bold text-gray-400 bg-gray-50 dark:bg-gray-900 px-2 py-1 rounded-lg">
                          {food.amount_g}g
                        </span>
                      </div>
                    ))}
                    {meal.foods.length > 3 && (
                      <div className="text-[10px] font-black text-gray-400 uppercase tracking-widest text-center pt-2 group-hover:text-primary-500 transition-colors">
                        +{meal.foods.length - 3} Additional Elements
                      </div>
                    )}
                  </div>
                </motion.div>
              ))}
            </div>
          </div>
        </div>

        {/* Improved Meal Detail Modal */}
        <AnimatePresence>
          {selectedMeal && (
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              className="fixed inset-0 bg-black/60 backdrop-blur-md z-[60] flex items-end md:items-center justify-center p-0 md:p-6"
              onClick={() => setSelectedMeal(null)}
            >
              <motion.div
                initial={{ y: 100, opacity: 0 }}
                animate={{ y: 0, opacity: 1 }}
                exit={{ y: 100, opacity: 0 }}
                className="bg-white dark:bg-gray-900 rounded-t-[2.5rem] md:rounded-[2.5rem] p-8 max-w-2xl w-full max-h-[90vh] overflow-y-auto shadow-2xl relative"
                onClick={(e) => e.stopPropagation()}
              >
                <div className="sticky top-0 bg-white/80 dark:bg-gray-900/80 backdrop-blur-md z-10 -mx-8 -mt-8 px-8 py-6 mb-6 border-b border-gray-100 dark:border-gray-800 flex items-center justify-between">
                  <div className="flex items-center space-x-4">
                    <div className="w-12 h-12 rounded-2xl bg-primary-100 dark:bg-primary-900/30 flex items-center justify-center text-primary-600">
                      <MealIcon name={selectedMeal.name} className="w-6 h-6" />
                    </div>
                    <div>
                      <h3 className="text-2xl font-black text-gray-900 dark:text-gray-100 tracking-tight">
                        {selectedMeal.name}
                      </h3>
                      <p className="text-sm font-bold text-gray-400 uppercase tracking-widest">
                        {selectedMeal.foods.length} Ingredients Found
                      </p>
                    </div>
                  </div>
                  <button
                    onClick={() => setSelectedMeal(null)}
                    className="w-10 h-10 rounded-full bg-gray-50 dark:bg-gray-800 flex items-center justify-center text-gray-400 hover:text-gray-600 transition-colors"
                  >
                    ×
                  </button>
                </div>

                {/* Macro Architecture Visualization */}
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-10">
                  {[
                    { label: 'Calories', value: Math.round(selectedMeal.totals.calories), unit: 'kcal', color: 'text-gray-900' },
                    { label: 'Protein', value: Math.round(selectedMeal.totals.protein), unit: 'grams', color: 'text-rose-500' },
                    { label: 'Fat', value: Math.round(selectedMeal.totals.fat), unit: 'grams', color: 'text-amber-500' },
                    { label: 'Carbs', value: Math.round(selectedMeal.totals.carbs), unit: 'grams', color: 'text-emerald-500' },
                  ].map((macro) => (
                    <div key={macro.label} className="p-4 bg-gray-50 dark:bg-gray-800/50 rounded-2xl border border-gray-100 dark:border-gray-700">
                      <div className="text-[10px] font-black text-gray-400 uppercase tracking-widest mb-1">{macro.label}</div>
                      <div className={`text-2xl font-black ${macro.color} dark:text-white`}>
                        {macro.value}
                        <span className="text-[10px] ml-1 font-bold text-gray-400">{macro.unit}</span>
                      </div>
                    </div>
                  ))}
                </div>

                {/* Component List */}
                <div className="mb-10">
                  <h4 className="text-sm font-black text-gray-400 uppercase tracking-widest mb-6">Ingredient Protocol</h4>
                  <div className="space-y-3">
                    {selectedMeal.foods.map((food, index) => (
                      <div key={index} className="flex items-center justify-between p-4 bg-gray-50 dark:bg-gray-800/50 rounded-3xl border border-gray-100 dark:border-gray-700 group hover:border-primary-200 transition-all">
                        <div className="flex-1 min-w-0 pr-4">
                          <div className="font-bold text-gray-900 dark:text-gray-100 truncate">
                            {food.name}
                          </div>
                          <div className="flex items-center gap-2 mt-1">
                            <Clock className="w-3 h-3 text-gray-400" />
                            <span className="text-xs font-bold text-gray-400 uppercase tracking-tighter">
                              {food.amount_g}g · {Math.round(food.calories)} kcal
                            </span>
                          </div>
                        </div>
                        <div className="text-right whitespace-nowrap">
                          <div className="flex gap-2">
                            <div className="px-2 py-1 bg-white dark:bg-gray-700 rounded-lg text-[10px] font-bold">
                              <span className="text-rose-500 mr-1">P</span>{Math.round(food.protein)}g
                            </div>
                            <div className="px-2 py-1 bg-white dark:bg-gray-700 rounded-lg text-[10px] font-bold">
                              <span className="text-emerald-500 mr-1">C</span>{Math.round(food.carbs)}g
                            </div>
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>

                {/* Dynamic Recipe Generation Trigger */}
                <div className="space-y-4">
                  <button
                    onClick={() => {
                      context.openRecipe(selectedMeal);
                      setSelectedMeal(null);
                    }}
                    className="w-full py-5 bg-gradient-to-r from-gray-900 via-gray-800 to-gray-900 text-white rounded-[2rem] font-bold text-lg shadow-2xl shadow-gray-900/20 hover:scale-[1.02] active:scale-[0.98] transition-all flex items-center justify-center gap-3"
                  >
                    <ChefHat className="w-6 h-6 text-orange-400" />
                    Initialize AI Chef Protocol
                  </button>
                  <p className="text-center text-[10px] font-black text-gray-400 uppercase tracking-widest">
                    Real-time synthesis of cooking instructions and metabolic analysis
                  </p>
                </div>
              </motion.div>
            </motion.div>
          )}
        </AnimatePresence>
      </motion.div>
    </div>
  );
}
