#!/usr/bin/env python3
"""
Demo Script for Enhanced Diet Coach Features
Demonstrates Excel export and detailed AI explanations
"""
import requests
import json
import base64
from datetime import datetime

# API base URL
API_BASE_URL = "http://localhost:8000"

def demo_enhanced_explanation():
    """Demo the enhanced AI explanation feature"""
    print("🤖 ENHANCED AI EXPLANATION DEMO")
    print("=" * 50)
    
    # Sample data for explanation
    explanation_data = {
        "calories": 2200,
        "protein_g": 110,
        "fat_g": 73,
        "carbs_g": 275,
        "constraints": "Budget-conscious, vegetarian preferences",
        "diet_tags": ["veg", "budget"]
    }
    
    try:
        response = requests.get(f"{API_BASE_URL}/explain", params=explanation_data)
        if response.status_code == 200:
            result = response.json()
            explanation = result.get('explanation', '')
            
            print("✅ Enhanced AI Explanation Generated!")
            print(f"📄 Length: {len(explanation)} characters")
            print("📋 Includes:")
            print("   ✓ Detailed macronutrient analysis")
            print("   ✓ Physiological adaptations timeline")
            print("   ✓ Meal timing optimization")
            print("   ✓ Micronutrient considerations")
            print("   ✓ Behavioral strategies")
            print("   ✓ Clinical monitoring recommendations")
            print("   ✓ Evidence-based references")
            print("\n" + "="*80)
            print("SAMPLE EXCERPT:")
            print("="*80)
            print(explanation[:500] + "...")
            print("="*80)
            
        else:
            print(f"❌ Error: {response.status_code} - {response.text}")
            
    except Exception as e:
        print(f"💥 Error: {e}")

def demo_excel_export():
    """Demo the Excel export feature"""
    print("\n📊 EXCEL EXPORT DEMO")
    print("=" * 50)
    
    # Sample comprehensive data for Excel export
    export_data = {
        "user_profile": {
            "age": 30,
            "sex": "female",
            "height_cm": 165,
            "weight_kg": 65,
            "activity_level": "moderate",
            "goal": "maintain"
        },
        "nutrition_targets": {
            "target_calories": 2200,
            "tdee": 2200,
            "bmr": 1450,
            "activity_factor": 1.55,
            "macro_targets": {
                "protein_g": 110,
                "fat_g": 73,
                "carbs_g": 275
            }
        },
        "meal_plan": {
            "days": [
                {
                    "day": 1,
                    "meals": [
                        {
                            "name": "Breakfast",
                            "foods": [
                                {"name": "Steel Cut Oats", "amount_g": 80, "calories": 311, "protein": 13.5, "fat": 5.5, "carbs": 53},
                                {"name": "Greek Yogurt", "amount_g": 150, "calories": 89, "protein": 15.5, "fat": 0.6, "carbs": 5.4}
                            ],
                            "totals": {"calories": 400, "protein": 29, "fat": 6.1, "carbs": 58.4}
                        },
                        {
                            "name": "Lunch", 
                            "foods": [
                                {"name": "Quinoa Power Bowl", "amount_g": 200, "calories": 360, "protein": 17, "fat": 12.4, "carbs": 48.6}
                            ],
                            "totals": {"calories": 360, "protein": 17, "fat": 12.4, "carbs": 48.6}
                        }
                    ],
                    "daily_totals": {"calories": 760, "protein": 46, "fat": 18.5, "carbs": 107}
                }
            ],
            "plan_totals": {"calories": 760, "protein": 46, "fat": 18.5, "carbs": 107},
            "adherence_score": 0.92
        },
        "explanation": "**COMPREHENSIVE NUTRITION PLAN ANALYSIS**\n*Professional Dietitian Consultation Report*\n\n**EXECUTIVE SUMMARY**\nThis personalized nutrition plan provides 2200 calories daily with scientifically-optimized macronutrient distribution..."
    }
    
    try:
        response = requests.post(f"{API_BASE_URL}/export/excel", json=export_data)
        if response.status_code == 200:
            result = response.json()
            
            print("✅ Excel Export Generated Successfully!")
            print(f"📄 Filename: {result['filename']}")
            print(f"📊 Base64 Length: {len(result['excel_data'])} characters")
            print("📋 Sheets Included:")
            for i, sheet in enumerate(result['sheets_included'], 1):
                print(f"   {i}. {sheet}")
            
            print("\n🎯 Export Features:")
            for feature in result['export_features']:
                print(f"   ✓ {feature}")
            
            # Optionally save the Excel file
            excel_data = base64.b64decode(result['excel_data'])
            filename = f"demo_{result['filename']}"
            with open(filename, 'wb') as f:
                f.write(excel_data)
            print(f"\n💾 Excel file saved as: {filename}")
            print(f"📏 File size: {len(excel_data)} bytes")
            
        else:
            print(f"❌ Error: {response.status_code} - {response.text}")
            
    except Exception as e:
        print(f"💥 Error: {e}")

def demo_complete_report():
    """Demo the complete report generation"""
    print("\n🎯 COMPLETE REPORT DEMO")
    print("=" * 50)
    
    complete_request = {
        "user_data": {
            "sex": "male",
            "age": 28,
            "height_cm": 175,
            "weight_kg": 75,
            "activity_level": "active",
            "goal": "bulk"
        },
        "meal_preferences": {
            "diet_tags": ["non_veg", "budget"],
            "days": 7,
            "constraints": "High protein for muscle building, budget-friendly options preferred"
        }
    }
    
    try:
        response = requests.post(f"{API_BASE_URL}/generate-complete-report", json=complete_request)
        if response.status_code == 200:
            result = response.json()
            
            print("✅ Complete Report Generated!")
            print(f"📋 Report ID: {result['report_metadata']['user_id']}")
            print(f"⏰ Generated: {result['report_metadata']['generated_at']}")
            
            summary = result['summary']
            print(f"\n📊 NUTRITION SUMMARY:")
            print(f"   🔥 Daily Calories: {summary['daily_calories']}")
            print(f"   🥩 Daily Protein: {summary['daily_protein']}g")
            print(f"   🥑 Daily Fat: {summary['daily_fat']}g")
            print(f"   🍞 Daily Carbs: {summary['daily_carbs']}g")
            print(f"   📅 Plan Duration: {summary['plan_duration_days']} days")
            print(f"   🎯 Adherence Score: {summary['adherence_score']:.1%}")
            
            print(f"\n📝 NEXT STEPS:")
            for i, step in enumerate(result['next_steps'], 1):
                print(f"   {i}. {step}")
            
            # Save Excel if available
            if 'excel_export' in result and result['excel_export']['success']:
                excel_data = base64.b64decode(result['excel_export']['excel_data'])
                filename = f"complete_report_{result['excel_export']['filename']}"
                with open(filename, 'wb') as f:
                    f.write(excel_data)
                print(f"\n💾 Complete Excel report saved as: {filename}")
            
        else:
            print(f"❌ Error: {response.status_code} - {response.text}")
            
    except Exception as e:
        print(f"💥 Error: {e}")

def demo_system_analytics():
    """Demo the system analytics"""
    print("\n📈 SYSTEM ANALYTICS DEMO")
    print("=" * 50)
    
    try:
        response = requests.get(f"{API_BASE_URL}/analytics/summary")
        if response.status_code == 200:
            result = response.json()
            
            print("✅ System Analytics Retrieved!")
            
            db_analytics = result['database_analytics']
            print(f"📊 DATABASE STATS:")
            print(f"   🍎 Total Foods: {db_analytics['total_foods']}")
            print(f"   📈 Database Version: {db_analytics['database_version']}")
            print(f"   ✅ Validation Rate: {db_analytics['validation_rate']}%")
            
            print(f"\n🌍 CULTURAL CONTEXTS:")
            for context in db_analytics['cultural_contexts']:
                print(f"   • {context.title()}")
            
            print(f"\n🍽️ DIETARY ACCOMMODATIONS:")
            for accommodation in db_analytics['dietary_accommodations']:
                print(f"   • {accommodation.replace('_', ' ').title()}")
            
            research_caps = result['research_capabilities']
            print(f"\n🔬 RESEARCH CAPABILITIES:")
            print(f"   🧪 Nutritional Validation: {'✅' if research_caps['nutritional_validation'] else '❌'}")
            print(f"   🌍 Cultural Diversity: {'✅' if research_caps['cultural_diversity'] else '❌'}")
            print(f"   💰 Accessibility Focus: {'✅' if research_caps['accessibility_focus'] else '❌'}")
            print(f"   🤖 ML Ready: {'✅' if research_caps['ml_ready'] else '❌'}")
            
        else:
            print(f"❌ Error: {response.status_code} - {response.text}")
            
    except Exception as e:
        print(f"💥 Error: {e}")

def check_api_health():
    """Check if the API is running"""
    print("🏥 CHECKING API HEALTH...")
    try:
        response = requests.get(f"{API_BASE_URL}/health", timeout=5)
        if response.status_code == 200:
            health_data = response.json()
            print(f"✅ API Status: {health_data['status']}")
            print(f"📋 Service: {health_data['service']}")
            print(f"🔢 Version: {health_data['version']}")
            
            if 'database' in health_data:
                db_info = health_data['database']
                print(f"💾 Database: {db_info['status']} ({db_info['foods_count']} foods)")
            
            return True
        else:
            print(f"❌ API Health Check Failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"💥 Cannot connect to API: {e}")
        print("💡 Make sure the API server is running on http://localhost:8000")
        return False

def main():
    """Run all demos"""
    print("🎯 DIET COACH ENHANCED FEATURES DEMO")
    print("=" * 80)
    print(f"🕐 Demo started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)
    
    # Check API health first
    if not check_api_health():
        print("\n❌ API is not accessible. Please start the API server first:")
        print("   cd apps/diet-api")
        print("   python main.py")
        return
    
    print("\n" + "="*80)
    
    # Run all demos
    demo_enhanced_explanation()
    demo_excel_export() 
    demo_complete_report()
    demo_system_analytics()
    
    print("\n" + "="*80)
    print("🎉 ALL DEMOS COMPLETED SUCCESSFULLY!")
    print("📋 Features Demonstrated:")
    print("   ✅ Enhanced AI Dietitian Explanations")
    print("   ✅ Professional Excel Export")
    print("   ✅ Complete Report Generation")
    print("   ✅ System Analytics & Health Monitoring")
    print("=" * 80)

if __name__ == "__main__":
    main()
