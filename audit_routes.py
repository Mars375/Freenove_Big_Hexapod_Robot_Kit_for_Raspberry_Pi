#!/usr/bin/env python3
"""Audit des routes API"""
import sys
import importlib.util

def load_app():
    spec = importlib.util.spec_from_file_location("server", "core/web/server.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.app

try:
    app = load_app()
    print("🌐 ROUTES DISPONIBLES:")
    print("=" * 50)
    
    for route in app.routes:
        if hasattr(route, 'path') and hasattr(route, 'methods'):
            methods = getattr(route, 'methods', [''])
            print(f"{', '.join(methods):10} {route.path}")
    
except Exception as e:
    print(f"❌ Erreur: {e}")
