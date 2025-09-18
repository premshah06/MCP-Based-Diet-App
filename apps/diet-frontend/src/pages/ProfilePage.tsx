import { } from 'react';
import { useNavigate } from 'react-router-dom';
import { useForm } from 'react-hook-form';
import { motion } from 'framer-motion';
import toast from 'react-hot-toast';
import { 
  User, 
  Activity, 
  Target, 
  Save, 
  ArrowRight, 
  AlertCircle,
  Info
} from 'lucide-react';

import { dietAPI, transformUserProfileToTDEE } from '@/services/api';
import { ACTIVITY_LEVELS, GOALS, VALIDATION, DIET_TAGS } from '@/utils/constants';
import { cn, calculateBMI, getBMICategory } from '@/utils/helpers';
import type { AppState, UserProfile, ProfileFormData } from '@/types/api';

interface ProfilePageProps {
  context: AppState & {
    updateUserProfile: (profile: UserProfile) => void;
    updateNutritionResults: (nutrition: any) => void;
    setLoading: (loading: boolean) => void;
    setError: (error: string | null) => void;
  };
}

export default function ProfilePage({ context }: ProfilePageProps) {
  const navigate = useNavigate();
  
  const {
    register,
    handleSubmit,
    watch,
    formState: { errors, isValid },
  } = useForm<ProfileFormData>({
    mode: 'onChange',
    defaultValues: context.user || {
      sex: 'male',
      age: 30,
      height_cm: 175,
      weight_kg: 70,
      activity_level: 'moderate',
      goal: 'maintain',
      diet_preferences: [],
    },
    resolver: (values) => {
      const errors: any = {};
      
      // Validate diet preferences
      if (!values.diet_preferences || values.diet_preferences.length === 0) {
        errors.diet_preferences = {
          type: 'required',
          message: 'Please select at least one diet preference'
        };
      }
      
      return {
        values,
        errors: Object.keys(errors).length > 0 ? errors : {}
      };
    }
  });

  const watchedValues = watch();
  const bmi = calculateBMI(watchedValues.weight_kg, watchedValues.height_cm);
  const bmiCategory = getBMICategory(bmi);

  const onSubmit = async (data: ProfileFormData) => {
    try {
      context.setLoading(true);
      context.setError(null);

      // Update user profile
      const userProfile: UserProfile = {
        ...data,
        diet_preferences: data.diet_preferences || [],
      };
      
      context.updateUserProfile(userProfile);

      // Calculate TDEE automatically
      const tdeeRequest = transformUserProfileToTDEE(userProfile);
      const tdeeResponse = await dietAPI.calculateTDEE(tdeeRequest);

      // Update nutrition results
      context.updateNutritionResults({ tdee: tdeeResponse });

      toast.success('Profile saved and nutrition calculated!');
      navigate('/results');
      
    } catch (error) {
      console.error('Profile submission error:', error);
      context.setError(error instanceof Error ? error.message : 'Failed to save profile');
    } finally {
      context.setLoading(false);
    }
  };

  // Form sections for potential future use
  // const formSections = [
  //   {
  //     title: 'Personal Information',
  //     icon: User,
  //     fields: ['sex', 'age', 'height_cm', 'weight_kg'],
  //   },
  //   {
  //     title: 'Activity & Goals',
  //     icon: Activity,
  //     fields: ['activity_level', 'goal'],
  //   },
  // ];

  return (
    <div className="max-w-4xl mx-auto">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6 }}
      >
        {/* Header */}
        <div className="text-center mb-12">
          <h1 className="text-3xl lg:text-4xl font-bold font-display text-gray-900 dark:text-gray-100 mb-4">
            Create Your Nutrition Profile
          </h1>
          <p className="text-lg text-gray-600 dark:text-gray-300 max-w-2xl mx-auto">
            Tell us about yourself so we can create a personalized nutrition plan tailored to your goals.
          </p>
        </div>

        <form onSubmit={handleSubmit(onSubmit)} className="space-y-8">
          {/* Personal Information Section */}
          <motion.section
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.6, delay: 0.2 }}
            className="card"
          >
            <div className="flex items-center space-x-3 mb-6">
              <div className="w-10 h-10 bg-primary-100 dark:bg-primary-900 rounded-lg flex items-center justify-center">
                <User className="w-5 h-5 text-primary-600 dark:text-primary-400" />
              </div>
              <h2 className="text-xl font-semibold text-gray-900 dark:text-gray-100">
                Personal Information
              </h2>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {/* Sex */}
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  Sex
                </label>
                <div className="grid grid-cols-2 gap-3">
                  {[
                    { value: 'male', label: 'Male', emoji: '👨' },
                    { value: 'female', label: 'Female', emoji: '👩' },
                  ].map((option) => (
                    <label
                      key={option.value}
                      className={cn(
                        'flex items-center space-x-3 p-4 border-2 rounded-xl cursor-pointer transition-all',
                        watchedValues.sex === option.value
                          ? 'border-primary-500 bg-primary-50 dark:bg-primary-900/20'
                          : 'border-gray-300 dark:border-gray-600 hover:border-gray-400 dark:hover:border-gray-500'
                      )}
                    >
                      <input
                        type="radio"
                        value={option.value}
                        {...register('sex', { required: 'Please select your sex' })}
                        className="sr-only"
                      />
                      <span className="text-2xl">{option.emoji}</span>
                      <span className="font-medium text-gray-900 dark:text-gray-100">
                        {option.label}
                      </span>
                    </label>
                  ))}
                </div>
                {errors.sex && (
                  <p className="error-message flex items-center space-x-1">
                    <AlertCircle className="w-4 h-4" />
                    <span>{errors.sex.message}</span>
                  </p>
                )}
              </div>

              {/* Age */}
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  Age (years)
                </label>
                <input
                  type="number"
                  {...register('age', {
                    required: 'Age is required',
                    min: { value: VALIDATION.age.min, message: `Age must be at least ${VALIDATION.age.min}` },
                    max: { value: VALIDATION.age.max, message: `Age must be at most ${VALIDATION.age.max}` },
                  })}
                  className={cn('input', errors.age && 'input-error')}
                  placeholder="Enter your age"
                />
                {errors.age && (
                  <p className="error-message flex items-center space-x-1">
                    <AlertCircle className="w-4 h-4" />
                    <span>{errors.age.message}</span>
                  </p>
                )}
              </div>

              {/* Height */}
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  Height (cm)
                </label>
                <input
                  type="number"
                  {...register('height_cm', {
                    required: 'Height is required',
                    min: { value: VALIDATION.height.min, message: `Height must be at least ${VALIDATION.height.min} cm` },
                    max: { value: VALIDATION.height.max, message: `Height must be at most ${VALIDATION.height.max} cm` },
                  })}
                  className={cn('input', errors.height_cm && 'input-error')}
                  placeholder="Enter your height"
                />
                {errors.height_cm && (
                  <p className="error-message flex items-center space-x-1">
                    <AlertCircle className="w-4 h-4" />
                    <span>{errors.height_cm.message}</span>
                  </p>
                )}
              </div>

              {/* Weight */}
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  Weight (kg)
                </label>
                <input
                  type="number"
                  step="0.1"
                  {...register('weight_kg', {
                    required: 'Weight is required',
                    min: { value: VALIDATION.weight.min, message: `Weight must be at least ${VALIDATION.weight.min} kg` },
                    max: { value: VALIDATION.weight.max, message: `Weight must be at most ${VALIDATION.weight.max} kg` },
                  })}
                  className={cn('input', errors.weight_kg && 'input-error')}
                  placeholder="Enter your weight"
                />
                {errors.weight_kg && (
                  <p className="error-message flex items-center space-x-1">
                    <AlertCircle className="w-4 h-4" />
                    <span>{errors.weight_kg.message}</span>
                  </p>
                )}
              </div>
            </div>

            {/* BMI Display */}
            {watchedValues.height_cm && watchedValues.weight_kg && (
              <motion.div
                initial={{ opacity: 0, scale: 0.95 }}
                animate={{ opacity: 1, scale: 1 }}
                className="mt-6 p-4 bg-gray-50 dark:bg-gray-800 rounded-xl"
              >
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-2">
                    <Info className="w-5 h-5 text-gray-500" />
                    <span className="text-sm font-medium text-gray-700 dark:text-gray-300">
                      Your BMI
                    </span>
                  </div>
                  <div className="text-right">
                    <div className="text-lg font-semibold text-gray-900 dark:text-gray-100">
                      {bmi.toFixed(1)}
                    </div>
                    <div className={cn('text-sm font-medium', bmiCategory.color)}>
                      {bmiCategory.category}
                    </div>
                  </div>
                </div>
              </motion.div>
            )}
          </motion.section>

          {/* Activity Level Section */}
          <motion.section
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.6, delay: 0.4 }}
            className="card"
          >
            <div className="flex items-center space-x-3 mb-6">
              <div className="w-10 h-10 bg-blue-100 dark:bg-blue-900 rounded-lg flex items-center justify-center">
                <Activity className="w-5 h-5 text-blue-600 dark:text-blue-400" />
              </div>
              <h2 className="text-xl font-semibold text-gray-900 dark:text-gray-100">
                Activity Level
              </h2>
            </div>

            <div className="space-y-3">
              {ACTIVITY_LEVELS.map((level) => (
                <label
                  key={level.value}
                  className={cn(
                    'flex items-center space-x-4 p-4 border-2 rounded-xl cursor-pointer transition-all',
                    watchedValues.activity_level === level.value
                      ? 'border-blue-500 bg-blue-50 dark:bg-blue-900/20'
                      : 'border-gray-300 dark:border-gray-600 hover:border-gray-400 dark:hover:border-gray-500'
                  )}
                >
                  <input
                    type="radio"
                    value={level.value}
                    {...register('activity_level', { required: 'Please select your activity level' })}
                    className="sr-only"
                  />
                  <span className="text-2xl">{level.icon}</span>
                  <div className="flex-1">
                    <div className="font-medium text-gray-900 dark:text-gray-100">
                      {level.label}
                    </div>
                    <div className="text-sm text-gray-500 dark:text-gray-400">
                      {level.description}
                    </div>
                  </div>
                  <div className="text-sm text-gray-500 dark:text-gray-400">
                    ×{level.factor}
                  </div>
                </label>
              ))}
            </div>
            {errors.activity_level && (
              <p className="error-message flex items-center space-x-1 mt-2">
                <AlertCircle className="w-4 h-4" />
                <span>{errors.activity_level.message}</span>
              </p>
            )}
          </motion.section>

          {/* Goal Section */}
          <motion.section
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.6, delay: 0.6 }}
            className="card"
          >
            <div className="flex items-center space-x-3 mb-6">
              <div className="w-10 h-10 bg-purple-100 dark:bg-purple-900 rounded-lg flex items-center justify-center">
                <Target className="w-5 h-5 text-purple-600 dark:text-purple-400" />
              </div>
              <h2 className="text-xl font-semibold text-gray-900 dark:text-gray-100">
                Fitness Goal
              </h2>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              {GOALS.map((goal) => (
                <label
                  key={goal.value}
                  className={cn(
                    'flex flex-col items-center p-6 border-2 rounded-xl cursor-pointer transition-all text-center',
                    watchedValues.goal === goal.value
                      ? 'border-purple-500 bg-purple-50 dark:bg-purple-900/20'
                      : 'border-gray-300 dark:border-gray-600 hover:border-gray-400 dark:hover:border-gray-500'
                  )}
                >
                  <input
                    type="radio"
                    value={goal.value}
                    {...register('goal', { required: 'Please select your goal' })}
                    className="sr-only"
                  />
                  <span className="text-3xl mb-3">{goal.icon}</span>
                  <div className="font-medium text-gray-900 dark:text-gray-100 mb-2">
                    {goal.label}
                  </div>
                  <div className="text-sm text-gray-500 dark:text-gray-400">
                    {goal.description}
                  </div>
                  <div className="text-xs text-gray-400 dark:text-gray-500 mt-2">
                    {goal.adjustment > 0 ? '+' : ''}{(goal.adjustment * 100).toFixed(0)}% calories
                  </div>
                </label>
              ))}
            </div>
            {errors.goal && (
              <p className="error-message flex items-center space-x-1 mt-2">
                <AlertCircle className="w-4 h-4" />
                <span>{errors.goal.message}</span>
              </p>
            )}
          </motion.section>

          {/* Diet Preferences Section */}
          <motion.section
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.6, delay: 0.7 }}
            className="card"
          >
            <div className="flex items-center space-x-3 mb-6">
              <div className="w-10 h-10 bg-green-100 dark:bg-green-900 rounded-lg flex items-center justify-center">
                <span className="text-2xl">🥗</span>
              </div>
              <h2 className="text-xl font-semibold text-gray-900 dark:text-gray-100">
                Diet Preferences
              </h2>
            </div>

            <div className="space-y-4">
              <p className="text-sm text-gray-600 dark:text-gray-400">
                Select your dietary preferences to get personalized meal recommendations.
              </p>
              
                                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
                {DIET_TAGS.map((tag) => (
                  <label
                    key={tag.value}
                    className={cn(
                      'flex items-center space-x-3 p-4 border-2 rounded-xl cursor-pointer transition-all',
                      watchedValues.diet_preferences?.includes(tag.value)
                        ? 'border-green-500 bg-green-50 dark:bg-green-900/20'
                        : 'border-gray-300 dark:border-gray-600 hover:border-gray-400 dark:hover:border-gray-500'
                    )}
                  >
                    <input
                      type="checkbox"
                      value={tag.value}
                      {...register('diet_preferences')}
                      className="sr-only"
                    />
                    <span className="text-2xl">{tag.icon}</span>
                    <div className="flex-1">
                      <div className="font-medium text-gray-900 dark:text-gray-100">
                        {tag.label}
                      </div>
                      <div className="text-sm text-gray-500 dark:text-gray-400">
                        {tag.description}
                      </div>
                    </div>
                  </label>
                ))}
              </div>
              
              {/* Selected Preferences Display */}
              {watchedValues.diet_preferences && watchedValues.diet_preferences.length > 0 && (
                <div className="mt-4 p-4 bg-green-50 dark:bg-green-900/20 rounded-xl border border-green-200 dark:border-green-800">
                  <div className="flex items-center space-x-2 mb-2">
                    <span className="text-green-600 dark:text-green-400">✓</span>
                    <span className="font-medium text-green-800 dark:text-green-200">Selected Preferences:</span>
                  </div>
                  <div className="flex flex-wrap gap-2">
                    {watchedValues.diet_preferences.map((pref) => {
                      const tag = DIET_TAGS.find(t => t.value === pref);
                      return tag ? (
                        <span
                          key={pref}
                          className="inline-flex items-center space-x-1 px-3 py-1 bg-green-100 dark:bg-green-800 text-green-800 dark:text-green-200 rounded-full text-sm font-medium"
                        >
                          <span>{tag.icon}</span>
                          <span>{tag.label}</span>
                        </span>
                      ) : null;
                    })}
                  </div>
                </div>
              )}
              
              {/* Error Display */}
              {errors.diet_preferences && (
                <p className="error-message flex items-center space-x-1">
                  <AlertCircle className="w-4 h-4" />
                  <span>{errors.diet_preferences.message}</span>
                </p>
              )}
              
              <div className="mt-4 p-4 bg-blue-50 dark:bg-blue-900/20 rounded-xl border border-blue-200 dark:border-blue-800">
                <div className="flex items-start space-x-3">
                  <Info className="w-5 h-5 text-blue-600 dark:text-blue-400 mt-0.5 flex-shrink-0" />
                  <div className="text-sm text-blue-800 dark:text-blue-200">
                    <p className="font-medium mb-1">💡 Pro Tip:</p>
                    <p>Choose "Vegetarian" for plant-based meals, "Non-Vegetarian" to include meat and fish, or both for maximum variety. You can also combine with other preferences like "Budget Friendly" for cost-effective options.</p>
                  </div>
                </div>
              </div>
            </div>
          </motion.section>

          {/* Submit Button */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.8 }}
            className="flex flex-col sm:flex-row gap-4 justify-center"
          >
            <button
              type="submit"
              disabled={!isValid || context.loading}
              className={cn(
                'btn-primary text-lg px-8 py-4 group min-w-[200px]',
                (!isValid || context.loading) && 'opacity-50 cursor-not-allowed'
              )}
            >
              {context.loading ? (
                <>
                  <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin mr-2" />
                  Calculating...
                </>
              ) : (
                <>
                  <Save className="mr-2 w-5 h-5 group-hover:scale-110 transition-transform" />
                  Calculate Nutrition
                  <ArrowRight className="ml-2 w-5 h-5 group-hover:translate-x-1 transition-transform" />
                </>
              )}
            </button>
          </motion.div>
        </form>
      </motion.div>
    </div>
  );
}
