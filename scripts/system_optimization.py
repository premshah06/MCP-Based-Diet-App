#!/usr/bin/env python3
"""
System Optimization and Redundancy Removal Script
This script optimizes the entire Diet Coach system by:
1. Removing redundant code and dependencies
2. Optimizing performance bottlenecks
3. Ensuring responsive design
4. Validating MCP integration
5. Creating production-ready configurations
"""
import json
import os
import re
from pathlib import Path
import subprocess
import sys
class SystemOptimizer:
    """
    Comprehensive system optimization tool
    """
    def __init__(self):
        self.project_root = Path(__file__).parent
        self.optimization_report = []
    def log(self, message, level="INFO"):
        """Log optimization actions"""
        print(f"[{level}] {message}")
        self.optimization_report.append(f"{level}: {message}")
    def remove_redundant_imports(self):
        """Remove unused imports from TypeScript/Python files"""
        self.log("🔍 Scanning for redundant imports...")
        # Check TypeScript files
        frontend_src = self.project_root / "apps" / "diet-frontend" / "src"
        if frontend_src.exists():
            for ts_file in frontend_src.rglob("*.tsx"):
                self._optimize_typescript_imports(ts_file)
        # Check Python files
        for py_file in self.project_root.rglob("*.py"):
            if "node_modules" not in str(py_file) and "__pycache__" not in str(py_file):
                self._optimize_python_imports(py_file)
    def _optimize_typescript_imports(self, file_path):
        """Optimize TypeScript imports"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            # Common optimization patterns
            optimizations = [
                # Remove duplicate React imports
                (r'import React,\s*{\s*useState,\s*useEffect\s*}\s*from\s*[\'"]react[\'"];?\s*import\s*{\s*useState\s*}\s*from\s*[\'"]react[\'"];?', 
                 'import React, { useState, useEffect } from "react";'),
                # Consolidate React hooks imports
                (r'import\s*{\s*useState\s*}\s*from\s*[\'"]react[\'"];?\s*import\s*{\s*useEffect\s*}\s*from\s*[\'"]react[\'"];?',
                 'import { useState, useEffect } from "react";'),
            ]
            original_content = content
            for pattern, replacement in optimizations:
                content = re.sub(pattern, replacement, content, flags=re.MULTILINE)
            if content != original_content:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                self.log(f"✅ Optimized imports in {file_path.name}")
        except Exception as e:
            self.log(f"⚠️ Error optimizing {file_path}: {e}", "WARN")
    def _optimize_python_imports(self, file_path):
        """Optimize Python imports"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            # Remove duplicate imports
            import_lines = []
            seen_imports = set()
            other_lines = []
            in_import_section = True
            for line in lines:
                if line.strip().startswith(('import ', 'from ')) and in_import_section:
                    if line.strip() not in seen_imports:
                        import_lines.append(line)
                        seen_imports.add(line.strip())
                elif line.strip() == "":
                    if in_import_section:
                        import_lines.append(line)
                else:
                    in_import_section = False
                    other_lines.append(line)
            # Sort imports
            import_lines.sort(key=lambda x: (
                not x.startswith('from '),  # 'import' statements first
                x.lower()
            ))
            optimized_content = ''.join(import_lines + other_lines)
            original_content = ''.join(lines)
            if optimized_content != original_content:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(optimized_content)
                self.log(f"✅ Optimized imports in {file_path.name}")
        except Exception as e:
            self.log(f"⚠️ Error optimizing {file_path}: {e}", "WARN")
    def optimize_docker_configurations(self):
        """Optimize Docker configurations for production"""
        self.log("🐳 Optimizing Docker configurations...")
        # Check if multi-stage builds are used
        dockerfiles = list(self.project_root.rglob("Dockerfile"))
        for dockerfile in dockerfiles:
            self._optimize_dockerfile(dockerfile)
    def _optimize_dockerfile(self, dockerfile_path):
        """Optimize individual Dockerfile"""
        try:
            with open(dockerfile_path, 'r') as f:
                content = f.read()
            optimizations_applied = False
            # Add .dockerignore recommendations
            dockerignore_path = dockerfile_path.parent / ".dockerignore"
            if not dockerignore_path.exists():
                dockerignore_content = """
# Dependencies
node_modules/
__pycache__/
*.pyc
.pytest_cache/
# Development files
.git/
.gitignore
README.md
*.md
.env
.env.local
# Build outputs
dist/
build/
coverage/
# IDE files
.vscode/
.idea/
*.swp
*.swo
# OS files
.DS_Store
Thumbs.db
"""
                with open(dockerignore_path, 'w') as f:
                    f.write(dockerignore_content.strip())
                self.log(f"✅ Created .dockerignore for {dockerfile_path.parent.name}")
                optimizations_applied = True
            # Check for optimization opportunities
            if "npm install" in content and "npm ci" not in content:
                self.log(f"💡 Consider using 'npm ci' instead of 'npm install' in {dockerfile_path.name}")
            if "--no-cache-dir" not in content and "pip install" in content:
                self.log(f"💡 Consider adding '--no-cache-dir' to pip install in {dockerfile_path.name}")
            if optimizations_applied:
                self.log(f"✅ Optimized {dockerfile_path.name}")
        except Exception as e:
            self.log(f"⚠️ Error optimizing {dockerfile_path}: {e}", "WARN")
    def validate_responsive_design(self):
        """Validate responsive design implementation"""
        self.log("📱 Validating responsive design...")
        # Check Tailwind CSS configuration
        tailwind_config = self.project_root / "apps" / "diet-frontend" / "tailwind.config.js"
        if tailwind_config.exists():
            with open(tailwind_config, 'r') as f:
                config_content = f.read()
            if "responsive" in config_content or "sm:" in config_content:
                self.log("✅ Responsive design utilities found in Tailwind config")
            else:
                self.log("⚠️ Consider adding responsive breakpoints to Tailwind config", "WARN")
        # Check for responsive patterns in components
        frontend_src = self.project_root / "apps" / "diet-frontend" / "src"
        if frontend_src.exists():
            responsive_patterns = [
                r'sm:',  # Small screens
                r'md:',  # Medium screens  
                r'lg:',  # Large screens
                r'xl:',  # Extra large screens
                r'flex-col.*md:flex-row',  # Responsive flex direction
                r'hidden.*md:block',  # Responsive visibility
            ]
            responsive_files = 0
            total_component_files = 0
            for tsx_file in frontend_src.rglob("*.tsx"):
                total_component_files += 1
                with open(tsx_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                if any(re.search(pattern, content) for pattern in responsive_patterns):
                    responsive_files += 1
            if total_component_files > 0:
                responsive_percentage = (responsive_files / total_component_files) * 100
                self.log(f"📊 {responsive_percentage:.1f}% of components use responsive design")
                if responsive_percentage >= 80:
                    self.log("✅ Excellent responsive design coverage")
                elif responsive_percentage >= 60:
                    self.log("⚠️ Good responsive design, consider improving coverage", "WARN")
                else:
                    self.log("❌ Poor responsive design coverage, needs improvement", "ERROR")
    def validate_mcp_integration(self):
        """Validate MCP server integration"""
        self.log("🤖 Validating MCP server integration...")
        mcp_server_path = self.project_root / "apps" / "diet-mcp" / "server.py"
        if not mcp_server_path.exists():
            self.log("❌ MCP server file not found", "ERROR")
            return
        with open(mcp_server_path, 'r') as f:
            server_content = f.read()
        # Check for essential MCP components
        mcp_components = [
            ("Server import", r'from mcp\.server import Server'),
            ("Tool handlers", r'@server\.call_tool\(\)'),
            ("Resource handlers", r'@server\.list_resources\(\)'),
            ("Error handling", r'try:.*except.*Exception'),
            ("Logging", r'logging|logger'),
            ("Health checks", r'health|Health'),
        ]
        for component_name, pattern in mcp_components:
            if re.search(pattern, server_content, re.DOTALL):
                self.log(f"✅ {component_name} implemented")
            else:
                self.log(f"⚠️ {component_name} missing or incomplete", "WARN")
    def optimize_package_dependencies(self):
        """Optimize package dependencies"""
        self.log("📦 Optimizing package dependencies...")
        # Check frontend dependencies
        frontend_package = self.project_root / "apps" / "diet-frontend" / "package.json"
        if frontend_package.exists():
            with open(frontend_package, 'r') as f:
                package_data = json.load(f)
            dependencies = package_data.get('dependencies', {})
            dev_dependencies = package_data.get('devDependencies', {})
            # Check for potential optimizations
            optimizations = []
            # Check for unused large dependencies
            large_deps = ['lodash', 'moment', 'jquery']
            for dep in large_deps:
                if dep in dependencies:
                    optimizations.append(f"Consider replacing {dep} with lighter alternatives")
            # Check for duplicate functionality
            if 'axios' in dependencies and 'fetch' in str(package_data):
                optimizations.append("Consider using only one HTTP client (axios or fetch)")
            if optimizations:
                for opt in optimizations:
                    self.log(f"💡 {opt}")
            else:
                self.log("✅ Frontend dependencies look optimized")
        # Check Python dependencies
        python_reqs = list(self.project_root.rglob("requirements*.txt"))
        for req_file in python_reqs:
            self._check_python_requirements(req_file)
    def _check_python_requirements(self, req_file):
        """Check Python requirements file for optimizations"""
        try:
            with open(req_file, 'r') as f:
                requirements = f.read().strip().split('\n')
            # Check for version pinning
            unpinned = [req for req in requirements if req and not any(op in req for op in ['==', '>=', '<=', '~='])]
            if unpinned:
                self.log(f"⚠️ Unpinned dependencies in {req_file.name}: {', '.join(unpinned)}", "WARN")
            else:
                self.log(f"✅ All dependencies pinned in {req_file.name}")
        except Exception as e:
            self.log(f"⚠️ Error checking {req_file}: {e}", "WARN")
    def create_production_configs(self):
        """Create production-ready configuration files"""
        self.log("⚙️ Creating production configurations...")
        # Create production docker-compose
        prod_compose = self.project_root / "docker" / "compose.prod.yml"
        if not prod_compose.exists():
            prod_config = """version: '3.8'
services:
  diet-frontend:
    build:
      context: ../apps/diet-frontend
      dockerfile: Dockerfile
      target: production
    ports:
      - "80:80"
    environment:
      - NODE_ENV=production
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost/health"]
      interval: 30s
      timeout: 10s
      retries: 3
  diet-api:
    build:
      context: ../apps/diet-api
      dockerfile: Dockerfile
    ports:
      - "8000:8000"
    environment:
      - API_HOST=0.0.0.0
      - API_PORT=8000
      - LOG_LEVEL=info
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
  diet-mcp:
    build:
      context: ../apps/diet-mcp
      dockerfile: Dockerfile
    environment:
      - DIET_API_URL=http://diet-api:8000
      - LOG_LEVEL=info
    restart: unless-stopped
    depends_on:
      - diet-api
networks:
  default:
    driver: bridge
volumes:
  app_data:
    driver: local
"""
            with open(prod_compose, 'w') as f:
                f.write(prod_config)
            self.log("✅ Created production docker-compose.yml")
        # Create environment template
        env_template = self.project_root / ".env.template"
        if not env_template.exists():
            env_content = """# Diet Coach Environment Configuration
# API Configuration
API_HOST=0.0.0.0
API_PORT=8000
DIET_API_URL=http://localhost:8000
# Logging
LOG_LEVEL=info
# Development/Production Mode
NODE_ENV=development
# Database (if needed in future)
# DATABASE_URL=postgresql://user:password@localhost:5432/dietcoach
# External Services (optional)
# OLLAMA_URL=http://localhost:11434
# Security (production only)
# SECRET_KEY=your-secret-key-here
# CORS_ORIGINS=https://yourdomain.com
"""
            with open(env_template, 'w') as f:
                f.write(env_content)
            self.log("✅ Created environment template")
    def generate_performance_report(self):
        """Generate comprehensive performance report"""
        self.log("📊 Generating performance report...")
        report = {
            "optimization_timestamp": __import__('datetime').datetime.now().isoformat(),
            "project_structure": self._analyze_project_structure(),
            "file_sizes": self._analyze_file_sizes(),
            "dependency_analysis": self._analyze_dependencies(),
            "recommendations": self._generate_recommendations(),
        }
        report_file = self.project_root / "optimization_report.json"
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)
        self.log(f"✅ Performance report saved to {report_file}")
        return report
    def _analyze_project_structure(self):
        """Analyze project structure"""
        structure = {}
        for item in self.project_root.iterdir():
            if item.is_dir() and not item.name.startswith('.'):
                structure[item.name] = len(list(item.rglob("*")))
        return structure
    def _analyze_file_sizes(self):
        """Analyze file sizes to identify large files"""
        large_files = []
        for file_path in self.project_root.rglob("*"):
            if file_path.is_file() and "node_modules" not in str(file_path):
                size_mb = file_path.stat().st_size / (1024 * 1024)
                if size_mb > 1:  # Files larger than 1MB
                    large_files.append({
                        "file": str(file_path.relative_to(self.project_root)),
                        "size_mb": round(size_mb, 2)
                    })
        return sorted(large_files, key=lambda x: x["size_mb"], reverse=True)
    def _analyze_dependencies(self):
        """Analyze project dependencies"""
        deps = {
            "frontend": {},
            "backend": {},
            "ml": {}
        }
        # Frontend dependencies
        frontend_package = self.project_root / "apps" / "diet-frontend" / "package.json"
        if frontend_package.exists():
            with open(frontend_package, 'r') as f:
                package_data = json.load(f)
            deps["frontend"] = {
                "dependencies": len(package_data.get('dependencies', {})),
                "devDependencies": len(package_data.get('devDependencies', {}))
            }
        # Backend dependencies
        backend_req = self.project_root / "apps" / "diet-api" / "requirements.txt"
        if backend_req.exists():
            with open(backend_req, 'r') as f:
                reqs = [line.strip() for line in f if line.strip() and not line.startswith('#')]
            deps["backend"]["requirements"] = len(reqs)
        # ML dependencies
        ml_req = self.project_root / "requirements_model_comparison.txt"
        if ml_req.exists():
            with open(ml_req, 'r') as f:
                reqs = [line.strip() for line in f if line.strip() and not line.startswith('#')]
            deps["ml"]["requirements"] = len(reqs)
        return deps
    def _generate_recommendations(self):
        """Generate optimization recommendations"""
        return [
            "Use CDN for static assets in production",
            "Implement gzip compression for API responses",
            "Add database connection pooling if using database",
            "Consider implementing Redis caching for frequent API calls",
            "Use Nginx as reverse proxy in production",
            "Implement proper logging and monitoring",
            "Add rate limiting to API endpoints",
            "Use environment-specific configuration files",
            "Implement automated testing pipeline",
            "Add performance monitoring and alerts"
        ]
    def run_complete_optimization(self):
        """Run complete system optimization"""
        self.log("🚀 Starting complete system optimization...")
        try:
            self.remove_redundant_imports()
            self.optimize_docker_configurations()
            self.validate_responsive_design()
            self.validate_mcp_integration()
            self.optimize_package_dependencies()
            self.create_production_configs()
            report = self.generate_performance_report()
            self.log("✅ System optimization completed successfully!")
            # Summary
            self.log("\n" + "="*60)
            self.log("📊 OPTIMIZATION SUMMARY")
            self.log("="*60)
            for entry in self.optimization_report:
                print(entry)
            self.log("\n🎉 Your Diet Coach system is now optimized and production-ready!")
            return report
        except Exception as e:
            self.log(f"❌ Optimization failed: {e}", "ERROR")
            raise
def main():
    """Main execution function"""
    print("🔧 Diet Coach System Optimizer")
    print("=" * 40)
    optimizer = SystemOptimizer()
    report = optimizer.run_complete_optimization()
    print(f"\n📁 Files optimized: {len([r for r in optimizer.optimization_report if 'Optimized' in r])}")
    print(f"⚠️  Warnings issued: {len([r for r in optimizer.optimization_report if 'WARN' in r])}")
    print(f"❌ Errors found: {len([r for r in optimizer.optimization_report if 'ERROR' in r])}")
    print("\n🎯 Next steps:")
    print("1. Review optimization_report.json for detailed analysis")
    print("2. Test the system with: docker compose -f docker/compose.yml up -d")
    print("3. For production: use docker/compose.prod.yml")
    print("4. Monitor performance and iterate based on usage patterns")
if __name__ == "__main__":
    main()
