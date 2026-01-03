/**
 * Grocery List Component
 * AI-powered shopping list generator from meal plans
 */

import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { dietAPI } from '@/services/api';
import type { MealPlanResponse, GroceryList as GroceryListType, GroceryCategory } from '@/types/api';
import toast from 'react-hot-toast';
import { Printer, CheckCircle2, ShoppingBag, Info, ClipboardList } from 'lucide-react';
import { LucideIcon } from '@/components/LucideIcon';

interface GroceryListProps {
  isOpen: boolean;
  onClose: () => void;
  mealPlan: MealPlanResponse | null;
}

export function GroceryList({ isOpen, onClose, mealPlan }: GroceryListProps) {
  const [groceryList, setGroceryList] = useState<GroceryListType | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [checkedItems, setCheckedItems] = useState<Set<string>>(new Set());
  const [budget, setBudget] = useState<string>('');

  const getCategoryIcon = (input: string): string => {
    const lowerInput = input.toLowerCase();
    if (lowerInput.includes('meat') || lowerInput.includes('protein') || lowerInput.includes('🥩') || lowerInput.includes('🍖')) return 'Utensils';
    if (lowerInput.includes('veg') || lowerInput.includes('produce') || lowerInput.includes('🥦') || lowerInput.includes('🥗')) return 'Carrot';
    if (lowerInput.includes('dairy') || lowerInput.includes('milk') || lowerInput.includes('🥛') || lowerInput.includes('🧀')) return 'Milk';
    if (lowerInput.includes('fruit') || lowerInput.includes('🍎') || lowerInput.includes('🍓')) return 'Apple';
    if (lowerInput.includes('grain') || lowerInput.includes('bread') || lowerInput.includes('🌾')) return 'Wheat';
    if (lowerInput.includes('pantry') || lowerInput.includes('spice') || lowerInput.includes('🥫')) return 'Archive';
    if (lowerInput.includes('budget') || lowerInput.includes('💰')) return 'Coins';
    return 'Package';
  };
  const generateList = async () => {
    if (!mealPlan) {
      toast.error('No meal plan available. Generate a meal plan first.');
      return;
    }

    setIsLoading(true);
    try {
      const response = await dietAPI.generateGroceryList({
        meal_plan: mealPlan,
        preferences: budget ? { budget } : undefined,
      });

      setGroceryList(response.grocery_list);
      setCheckedItems(new Set());
      toast.success('Grocery list generated!');
    } catch (error: any) {
      toast.error(error.message || 'Failed to generate grocery list');
    } finally {
      setIsLoading(false);
    }
  };

  const toggleItem = (categoryName: string, itemName: string) => {
    const key = `${categoryName}-${itemName}`;
    setCheckedItems((prev) => {
      const newSet = new Set(prev);
      if (newSet.has(key)) {
        newSet.delete(key);
      } else {
        newSet.add(key);
      }
      return newSet;
    });
  };

  const copyToClipboard = () => {
    if (!groceryList) return;

    const text = groceryList.categories
      .map((cat) => {
        const items = cat.items.map((item) => `  • ${item.name} - ${item.quantity}`).join('\n');
        return `${cat.name}\n${items}`;
      })
      .join('\n\n');

    navigator.clipboard.writeText(text);
    toast.success('Copied to clipboard!');
  };

  const getProgress = () => {
    if (!groceryList) return 0;
    const totalItems = groceryList.categories.reduce((sum, cat) => sum + cat.items.length, 0);
    return totalItems > 0 ? (checkedItems.size / totalItems) * 100 : 0;
  };

  const handleExportPDF = () => {
    if (!groceryList) return;
    window.print();
    toast.success('Preparing PDF for download...');
  };

  if (!isOpen) return null;

  return (
    <AnimatePresence>
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        exit={{ opacity: 0 }}
        className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm p-4"
        onClick={onClose}
      >
        <motion.div
          initial={{ scale: 0.9, opacity: 0, y: 20 }}
          animate={{ scale: 1, opacity: 1, y: 0 }}
          exit={{ scale: 0.9, opacity: 0, y: 20 }}
          className="bg-white dark:bg-gray-800 sm:rounded-2xl shadow-2xl w-full sm:max-w-2xl h-full sm:max-h-[85vh] flex flex-col overflow-hidden"
          onClick={(e) => e.stopPropagation()}
        >
          {/* Header */}
          <div className="bg-gradient-to-r from-orange-500 to-amber-500 p-4 text-white">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-4">
                <div className="w-12 h-12 bg-white/10 backdrop-blur-md rounded-2xl flex items-center justify-center border border-white/20">
                  <ShoppingBag className="w-6 h-6 text-white" />
                </div>
                <div>
                  <h2 className="text-xl font-black tracking-tight">Grocery Intelligence</h2>
                  <p className="text-orange-100 text-xs font-bold uppercase tracking-widest">AI-Optimized Inventory</p>
                </div>
              </div>
              <button
                onClick={onClose}
                className="p-2 hover:bg-white/20 rounded-lg transition-colors"
              >
                <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>

            {/* Progress bar */}
            {groceryList && (
              <div className="mt-4">
                <div className="flex justify-between text-sm mb-1">
                  <span>Shopping Progress</span>
                  <span>{Math.round(getProgress())}%</span>
                </div>
                <div className="h-2 bg-white/20 rounded-full overflow-hidden">
                  <motion.div
                    initial={{ width: 0 }}
                    animate={{ width: `${getProgress()}%` }}
                    className="h-full bg-white rounded-full"
                  />
                </div>
              </div>
            )}
          </div>

          {/* Content */}
          <div className="flex-1 overflow-y-auto p-4">
            {!groceryList ? (
              <div className="text-center py-12">
                <div className="w-24 h-24 bg-orange-100 dark:bg-orange-900/30 rounded-3xl flex items-center justify-center mx-auto mb-6">
                  <ShoppingBag className="w-10 h-10 text-orange-600" />
                </div>
                <h3 className="text-lg font-semibold text-gray-800 dark:text-gray-200 mb-2">
                  Generate Your Shopping List
                </h3>
                <p className="text-gray-600 dark:text-gray-400 mb-6 max-w-sm mx-auto">
                  {mealPlan
                    ? 'Click below to create an organized grocery list from your meal plan.'
                    : 'You need to generate a meal plan first before creating a grocery list.'}
                </p>

                {mealPlan && (
                  <div className="mb-4">
                    <label className="block text-sm text-gray-600 dark:text-gray-400 mb-2">
                      Budget preference (optional)
                    </label>
                    <select
                      value={budget}
                      onChange={(e) => setBudget(e.target.value)}
                      className="px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg
                               bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                    >
                      <option value="">Any budget</option>
                      <option value="low">Budget-friendly</option>
                      <option value="medium">Moderate</option>
                      <option value="high">Premium</option>
                    </select>
                  </div>
                )}

                <button
                  onClick={generateList}
                  disabled={!mealPlan || isLoading}
                  className="px-6 py-3 bg-orange-500 hover:bg-orange-600 text-white font-semibold 
                           rounded-xl disabled:opacity-50 disabled:cursor-not-allowed transition-colors
                           flex items-center gap-2 mx-auto"
                >
                  {isLoading ? (
                    <>
                      <div className="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                      Generating...
                    </>
                  ) : (
                    <>
                      <ShoppingBag className="w-5 h-5" />
                      Generate Inventory List
                    </>
                  )}
                </button>
              </div>
            ) : (
              <div className="space-y-6">
                {/* Categories */}
                {groceryList.categories.map((category: GroceryCategory) => (
                  <div key={category.name} className="bg-gray-50 dark:bg-gray-700/50 rounded-2xl p-5 border border-gray-100 dark:border-gray-600 shadow-sm">
                    <div className="flex items-center justify-between mb-4">
                      <h3 className="font-bold text-gray-900 dark:text-gray-100 flex items-center gap-3 text-lg">
                        <div className="p-2.5 bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-100 dark:border-gray-600">
                          <LucideIcon name={getCategoryIcon(category.icon || category.name)} className="w-5 h-5 text-orange-500" />
                        </div>
                        {category.name}
                      </h3>
                      <span className="text-xs font-semibold px-2 py-1 bg-gray-200 dark:bg-gray-600 text-gray-600 dark:text-gray-300 rounded-full">
                        {category.items.length} {category.items.length === 1 ? 'Item' : 'Items'}
                      </span>
                    </div>

                    <div className="space-y-3">
                      {category.items.map((item) => {
                        const key = `${category.name}-${item.name}`;
                        const isChecked = checkedItems.has(key);
                        return (
                          <motion.label
                            key={item.name}
                            whileHover={{ x: 4 }}
                            className={`flex items-start gap-4 p-3 rounded-xl cursor-pointer transition-all border
                                      ${isChecked
                                ? 'bg-emerald-50/50 dark:bg-emerald-900/10 border-emerald-200 dark:border-emerald-800/50 opacity-60'
                                : 'bg-white dark:bg-gray-800 border-transparent hover:border-orange-200 dark:hover:border-orange-900/50 shadow-sm'}`}
                          >
                            <div className="mt-1">
                              <div className={`w-6 h-6 rounded-lg border-2 flex items-center justify-center transition-colors
                                            ${isChecked
                                  ? 'bg-emerald-500 border-emerald-500 text-white'
                                  : 'border-gray-300 dark:border-gray-600'}`}>
                                <input
                                  type="checkbox"
                                  checked={isChecked}
                                  onChange={() => toggleItem(category.name, item.name)}
                                  className="sr-only"
                                />
                                {isChecked && <CheckCircle2 className="w-4 h-4" />}
                              </div>
                            </div>

                            <div className="flex-1">
                              <div className="flex items-center justify-between gap-2">
                                <span className={`font-semibold text-gray-900 dark:text-gray-100 ${isChecked ? 'line-through text-gray-400' : ''}`}>
                                  {item.name}
                                </span>
                                <span className="text-sm font-bold text-orange-600 dark:text-orange-400 bg-orange-50 dark:bg-orange-900/20 px-2 py-0.5 rounded-md whitespace-nowrap">
                                  {item.quantity}
                                </span>
                              </div>

                              {item.notes && (
                                <div className="flex items-start gap-1 mt-1 text-xs text-gray-500 dark:text-gray-400 italic">
                                  <Info className="w-3 h-3 mt-0.5" />
                                  <span>{item.notes}</span>
                                </div>
                              )}
                            </div>
                          </motion.label>
                        );
                      })}
                    </div>
                  </div>
                ))}

                {/* Shopping Tips */}
                {groceryList.shopping_tips && groceryList.shopping_tips.length > 0 && (
                  <div className="bg-gradient-to-br from-blue-50 to-indigo-50 dark:from-blue-900/20 dark:to-indigo-900/20 rounded-2xl p-6 border border-blue-100 dark:border-blue-800/50">
                    <h3 className="font-bold text-blue-900 dark:text-blue-200 mb-3 flex items-center gap-2">
                      <ShoppingBag className="w-5 h-5" />
                      Pro Shopping Tips
                    </h3>
                    <ul className="grid grid-cols-1 md:grid-cols-2 gap-3">
                      {groceryList.shopping_tips.map((tip, index) => (
                        <li key={index} className="flex items-start gap-2 text-blue-800/80 dark:text-blue-300/80 text-sm">
                          <span className="text-blue-400 mt-1">•</span>
                          {tip}
                        </li>
                      ))}
                    </ul>
                  </div>
                )}
              </div>
            )}
          </div>

          {/* PDF EXPORT CONTENT (Visible only when printing) */}
          <div className="hidden print:block fixed inset-0 bg-white p-10 z-[1000] text-gray-900 overflow-visible">
            <div className="flex items-center justify-between border-b-2 border-orange-500 pb-6 mb-8">
              <div>
                <h1 className="text-3xl font-bold text-gray-900 mb-1">Smart Grocery List</h1>
                <p className="text-gray-600">Generated by Diet Coach AI • {new Date().toLocaleDateString()}</p>
              </div>
              <div className="text-right">
                <p className="text-orange-600 font-bold text-xl">{groceryList?.total_items} Items Total</p>
                <p className="text-gray-500 text-sm">Ref: {Math.random().toString(36).substring(7).toUpperCase()}</p>
              </div>
            </div>

            <div className="grid grid-cols-2 gap-x-10 gap-y-8">
              {groceryList?.categories.map((category) => (
                <div key={category.name} className="break-inside-avoid mb-6">
                  <h2 className="text-xl font-bold flex items-center gap-3 mb-4 border-b border-gray-200 pb-2">
                    <LucideIcon name={getCategoryIcon(category.icon || category.name)} className="w-5 h-5 text-orange-500" />
                    {category.name}
                  </h2>
                  <div className="space-y-2">
                    {category.items.map((item) => (
                      <div key={item.name} className="flex items-center gap-3 py-1">
                        <div className="w-5 h-5 border-2 border-gray-300 rounded flex-shrink-0"></div>
                        <span className="flex-1 font-medium">{item.name}</span>
                        <span className="font-bold text-gray-600">{item.quantity}</span>
                      </div>
                    ))}
                  </div>
                </div>
              ))}
            </div>

            {groceryList?.shopping_tips && (
              <div className="mt-12 p-6 bg-gray-50 rounded-2xl border border-gray-200">
                <h2 className="text-lg font-bold mb-3 flex items-center gap-2">
                  <Info className="w-5 h-5 text-blue-500" />
                  Shopping Intelligence
                </h2>
                <div className="grid grid-cols-2 gap-4">
                  {groceryList.shopping_tips.map((tip, i) => (
                    <p key={i} className="text-sm text-gray-600">• {tip}</p>
                  ))}
                </div>
              </div>
            )}

            <div className="mt-12 pt-8 border-t border-gray-200 text-center text-gray-400 text-xs">
              This list was automatically generated based on your personalized nutritional targets and meal plan.
            </div>
          </div>

          {/* Footer */}
          {groceryList && (
            <div className="p-4 border-t border-gray-200 dark:border-gray-700 flex items-center justify-between">
              <div className="text-sm text-gray-600 dark:text-gray-400">
                {groceryList.total_items} items total
                {groceryList.estimated_total && ` • Est. ${groceryList.estimated_total}`}
              </div>
              <div className="flex gap-2">
                <button
                  onClick={() => {
                    setGroceryList(null);
                    setCheckedItems(new Set());
                  }}
                  className="px-4 py-2 text-gray-600 dark:text-gray-400 hover:bg-gray-100 
                           dark:hover:bg-gray-700 rounded-xl transition-colors font-medium"
                >
                  Regenerate
                </button>
                <button
                  onClick={copyToClipboard}
                  className="px-4 py-2 bg-gray-100 dark:bg-gray-700 hover:bg-gray-200 dark:hover:bg-gray-600 text-gray-700 dark:text-gray-200 
                           rounded-xl transition-all flex items-center gap-2 font-bold"
                >
                  <ClipboardList className="w-4 h-4" />
                  Copy
                </button>
                <button
                  onClick={handleExportPDF}
                  className="px-4 py-2 bg-gradient-to-r from-orange-500 to-orange-600 hover:from-orange-600 hover:to-orange-700 text-white 
                           rounded-xl transition-all flex items-center gap-2 shadow-lg shadow-orange-500/20 font-bold"
                >
                  <Printer className="w-4 h-4" />
                  Print PDF
                </button>
              </div>
            </div>
          )}
        </motion.div>
      </motion.div>
    </AnimatePresence>
  );
}

export default GroceryList;
