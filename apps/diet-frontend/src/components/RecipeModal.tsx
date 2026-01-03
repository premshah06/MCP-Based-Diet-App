import React from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { X, Clock, ChefHat, Utensils, Info, CheckCircle2, List } from 'lucide-react';

interface RecipeModalProps {
    isOpen: boolean;
    onClose: () => void;
    recipe: {
        title: string;
        prep_time: string;
        cook_time: string;
        difficulty: string;
        equipment: string[];
        ingredients: { name: string; amount: string }[];
        instructions: string[];
        tips: string[];
        nutritional_highlights: string[];
    } | null;
    isLoading: boolean;
}

const RecipeModal: React.FC<RecipeModalProps> = ({ isOpen, onClose, recipe, isLoading }) => {
    if (!isOpen) return null;

    return (
        <AnimatePresence>
            <div className="fixed inset-0 z-[60] flex items-center justify-center p-0 sm:p-4">
                <motion.div
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    exit={{ opacity: 0 }}
                    className="absolute inset-0 bg-black/60 backdrop-blur-sm sm:backdrop-blur-md"
                    onClick={onClose}
                />

                <motion.div
                    initial={{ scale: 0.9, opacity: 0, y: 20 }}
                    animate={{ scale: 1, opacity: 1, y: 0 }}
                    exit={{ scale: 0.9, opacity: 0, y: 20 }}
                    className="bg-white dark:bg-gray-800 sm:rounded-2xl shadow-2xl w-full sm:max-w-3xl h-full sm:max-h-[90vh] flex flex-col overflow-hidden relative"
                    onClick={(e) => e.stopPropagation()}
                >
                    {/* Header */}
                    <div className="p-4 sm:p-6 border-b border-gray-100 dark:border-gray-700 flex items-center justify-between bg-gradient-to-r from-orange-50 to-amber-50 dark:from-gray-800 dark:to-gray-750">
                        <div className="flex items-center space-x-3">
                            <div className="w-10 h-10 rounded-full bg-orange-500 flex items-center justify-center text-white">
                                <ChefHat className="w-6 h-6" />
                            </div>
                            <div>
                                <h2 className="text-xl font-bold text-gray-900 dark:text-white leading-tight">
                                    {isLoading ? 'Preparing Recipe...' : recipe?.title || 'Smart Recipe'}
                                </h2>
                                {!isLoading && recipe && (
                                    <div className="flex items-center space-x-3 mt-1 text-xs text-gray-500 dark:text-gray-400">
                                        <span className="flex items-center"><Clock className="w-3 h-3 mr-1" /> {recipe.prep_time} prep</span>
                                        <span className="flex items-center"><Utensils className="w-3 h-3 mr-1" /> {recipe.cook_time} cook</span>
                                        <span className="px-2 py-0.5 rounded-full bg-orange-100 dark:bg-orange-900/30 text-orange-600 dark:text-orange-400 font-medium">{recipe.difficulty}</span>
                                    </div>
                                )}
                            </div>
                        </div>
                        <button
                            onClick={onClose}
                            className="p-2 hover:bg-gray-200 dark:hover:bg-gray-700 rounded-full transition-colors"
                        >
                            <X className="w-6 h-6" />
                        </button>
                    </div>

                    <div className="flex-1 overflow-y-auto p-4 sm:p-8">
                        {isLoading ? (
                            <div className="flex flex-col items-center justify-center h-full space-y-4">
                                <div className="w-16 h-16 border-4 border-orange-200 border-t-orange-500 rounded-full animate-spin"></div>
                                <p className="text-gray-500 dark:text-gray-400 font-medium">AI Chef is writing down the steps...</p>
                            </div>
                        ) : recipe ? (
                            <div className="space-y-8">
                                {/* Ingredients & Equipment */}
                                <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
                                    <section>
                                        <h3 className="text-lg font-bold mb-4 flex items-center">
                                            <List className="w-5 h-5 mr-2 text-orange-500" />
                                            Ingredients
                                        </h3>
                                        <ul className="space-y-2">
                                            {recipe.ingredients.map((ing, idx) => (
                                                <li key={idx} className="flex justify-between items-center py-2 border-b border-gray-50 dark:border-gray-700/50">
                                                    <span className="text-gray-700 dark:text-gray-300">{ing.name}</span>
                                                    <span className="font-semibold text-orange-600 dark:text-orange-400 bg-orange-50 dark:bg-orange-900/20 px-2 py-0.5 rounded text-sm">
                                                        {ing.amount}
                                                    </span>
                                                </li>
                                            ))}
                                        </ul>
                                    </section>

                                    <section>
                                        <h3 className="text-lg font-bold mb-4 flex items-center">
                                            <Utensils className="w-5 h-5 mr-2 text-orange-500" />
                                            What You'll Need
                                        </h3>
                                        <div className="flex flex-wrap gap-2">
                                            {recipe.equipment.map((eq, idx) => (
                                                <span key={idx} className="bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 px-3 py-1.5 rounded-lg text-sm flex items-center">
                                                    <CheckCircle2 className="w-3.5 h-3.5 mr-1.5 text-gray-400" />
                                                    {eq}
                                                </span>
                                            ))}
                                        </div>

                                        <div className="mt-6 p-4 rounded-xl bg-orange-50 dark:bg-orange-900/10 border border-orange-100 dark:border-orange-900/20">
                                            <h4 className="text-sm font-bold text-orange-800 dark:text-orange-300 mb-2 flex items-center">
                                                <Info className="w-4 h-4 mr-1.5" />
                                                Nutritional Highlights
                                            </h4>
                                            <div className="flex flex-wrap gap-2">
                                                {recipe.nutritional_highlights.map((h, idx) => (
                                                    <span key={idx} className="text-xs font-semibold text-orange-700 dark:text-orange-400 uppercase tracking-wider">
                                                        • {h}
                                                    </span>
                                                ))}
                                            </div>
                                        </div>
                                    </section>
                                </div>

                                {/* Instructions */}
                                <section>
                                    <h3 className="text-lg font-bold mb-4 flex items-center">
                                        <ChefHat className="w-5 h-5 mr-2 text-orange-500" />
                                        Instructions
                                    </h3>
                                    <div className="space-y-6">
                                        {recipe.instructions.map((step, idx) => (
                                            <div key={idx} className="flex gap-4 group">
                                                <div className="flex-shrink-0 w-8 h-8 rounded-full bg-orange-100 dark:bg-orange-900/30 text-orange-600 dark:text-orange-400 flex items-center justify-center font-bold text-sm transition-transform group-hover:scale-110">
                                                    {idx + 1}
                                                </div>
                                                <p className="text-gray-700 dark:text-gray-300 leading-relaxed pt-1">
                                                    {step}
                                                </p>
                                            </div>
                                        ))}
                                    </div>
                                </section>

                                {/* Tips */}
                                {recipe.tips.length > 0 && (
                                    <section className="bg-blue-50 dark:bg-blue-900/10 border border-blue-100 dark:border-blue-900/20 p-6 rounded-2xl">
                                        <h3 className="text-lg font-bold mb-3 text-blue-900 dark:text-blue-300 flex items-center">
                                            <Info className="w-5 h-5 mr-2 text-blue-500" />
                                            Chef's Tips
                                        </h3>
                                        <ul className="space-y-2">
                                            {recipe.tips.map((tip, idx) => (
                                                <li key={idx} className="text-blue-800 dark:text-blue-300 text-sm flex items-start italic">
                                                    <span className="mr-2 text-blue-400">•</span>
                                                    {tip}
                                                </li>
                                            ))}
                                        </ul>
                                    </section>
                                )}
                            </div>
                        ) : (
                            <div className="text-center py-12">
                                <Info className="w-12 h-12 text-gray-300 mx-auto mb-4" />
                                <p className="text-gray-500">No recipe data available.</p>
                            </div>
                        )}
                    </div>

                    {/* Footer */}
                    <div className="p-4 sm:p-6 border-t border-gray-100 dark:border-gray-700 bg-gray-50 dark:bg-gray-800/50">
                        <button
                            onClick={onClose}
                            className="w-full btn-primary py-3 rounded-xl font-bold shadow-lg shadow-orange-500/20"
                        >
                            Close Recipe
                        </button>
                    </div>
                </motion.div>
            </div>
        </AnimatePresence>
    );
};

export default RecipeModal;
