#!/usr/bin/env bash
# build.sh - Render build script

echo "Starting build process..."
echo "Python version: $(python --version)"
echo "Current directory: $(pwd)"
echo "Directory contents:"
ls -la

# Create directory structure
echo "Creating directory structure..."
mkdir -p templates static/css static/js static/uploads

# Create basic templates if they don't exist
if [ ! -f "templates/base.html" ]; then
    echo "Creating basic templates..."
    
    # Create base.html
    cat > templates/base.html << 'EOF'
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{% block title %}Flask App{% endblock %}</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: Arial, sans-serif; }
        .container { max-width: 1200px; margin: 0 auto; padding: 20px; }
        .flash { padding: 10px; margin: 10px 0; border-radius: 5px; }
        .success { background: #d4edda; color: #155724; }
        .error { background: #f8d7da; color: #721c24; }
    </style>
</head>
<body>
    <div class="container">
        {% with messages = get_flashed_messages(with_categories=true) %}
            {% if messages %}
                {% for category, message in messages %}
                    <div class="flash {{ category }}">{{ message }}</div>
                {% endfor %}
            {% endif %}
        {% endwith %}
        
        {% block content %}{% endblock %}
    </div>
</body>
</html>
EOF

    # Create login.html
    cat > templates/login.html << 'EOF'
{% extends "base.html" %}

{% block title %}Login{% endblock %}

{% block content %}
<div style="max-width: 400px; margin: 50px auto;">
    <h1 style="text-align: center;">Login</h1>
    
    <form method="POST" style="background: #f9f9f9; padding: 20px; border-radius: 8px;">
        <div style="margin-bottom: 15px;">
            <label style="display: block; margin-bottom: 5px;">Mobile Number</label>
            <input type="tel" name="phone" required style="width: 100%; padding: 8px;">
        </div>
        
        <div style="margin-bottom: 15px;">
            <label style="display: block; margin-bottom: 5px;">Password</label>
            <input type="password" name="password" required style="width: 100%; padding: 8px;">
        </div>
        
        <button type="submit" style="width: 100%; padding: 10px; background: #4CAF50; color: white; border: none; border-radius: 4px;">
            Login
        </button>
    </form>
    
    <p style="text-align: center; margin-top: 15px;">
        Don't have an account? <a href="/register">Register</a>
    </p>
</div>
{% endblock %}
EOF

    # Create register.html
    cat > templates/register.html << 'EOF'
{% extends "base.html" %}

{% block title %}Register{% endblock %}

{% block content %}
<div style="max-width: 500px; margin: 50px auto;">
    <h1 style="text-align: center;">Register</h1>
    
    <form method="POST" enctype="multipart/form-data" style="background: #f9f9f9; padding: 20px; border-radius: 8px;">
        <div style="margin-bottom: 15px;">
            <label style="display: block; margin-bottom: 5px;">Full Name</label>
            <input type="text" name="full_name" required style="width: 100%; padding: 8px;">
        </div>
        
        <div style="margin-bottom: 15px;">
            <label style="display: block; margin-bottom: 5px;">Mobile Number</label>
            <input type="tel" name="phone" required style="width: 100%; padding: 8px;">
        </div>
        
        <div style="margin-bottom: 15px;">
            <label style="display: block; margin-bottom: 5px;">Email</label>
            <input type="email" name="email" required style="width: 100%; padding: 8px;">
        </div>
        
        <div style="margin-bottom: 15px;">
            <label style="display: block; margin-bottom: 5px;">Location</label>
            <input type="text" name="location" required style="width: 100%; padding: 8px;">
        </div>
        
        <div style="margin-bottom: 15px;">
            <label style="display: block; margin-bottom: 5px;">Profile Picture (Optional)</label>
            <input type="file" name="profile_pic" accept="image/*" style="width: 100%; padding: 8px;">
        </div>
        
        <div style="margin-bottom: 15px;">
            <label style="display: block; margin-bottom: 5px;">Password</label>
            <input type="password" name="password" required style="width: 100%; padding: 8px;">
        </div>
        
        <div style="margin-bottom: 15px;">
            <label style="display: block; margin-bottom: 5px;">Confirm Password</label>
            <input type="password" name="confirm_password" required style="width: 100%; padding: 8px;">
        </div>
        
        <button type="submit" style="width: 100%; padding: 10px; background: #2196F3; color: white; border: none; border-radius: 4px;">
            Register
        </button>
    </form>
    
    <p style="text-align: center; margin-top: 15px;">
        Already have an account? <a href="/login">Login</a>
    </p>
</div>
{% endblock %}
EOF

    # Create dashboard.html
    cat > templates/dashboard.html << 'EOF'
{% extends "base.html" %}

{% block title %}Dashboard{% endblock %}

{% block content %}
<div style="text-align: center; padding: 50px 20px;">
    <h1>Welcome, {{ session.full_name }}!</h1>
    <p style="margin: 20px 0;">This is your dashboard.</p>
    
    <div style="display: flex; justify-content: center; gap: 20px; margin-top: 30px;">
        <a href="/services" style="padding: 10px 20px; background: #4CAF50; color: white; text-decoration: none; border-radius: 5px;">
            Services
        </a>
        <a href="/menu" style="padding: 10px 20px; background: #2196F3; color: white; text-decoration: none; border-radius: 5px;">
            Menu
        </a>
        <a href="/cart" style="padding: 10px 20px; background: #FF9800; color: white; text-decoration: none; border-radius: 5px;">
            Cart
        </a>
        <a href="/profile" style="padding: 10px 20px; background: #9C27B0; color: white; text-decoration: none; border-radius: 5px;">
            Profile
        </a>
        <a href="/logout" style="padding: 10px 20px; background: #f44336; color: white; text-decoration: none; border-radius: 5px;">
            Logout
        </a>
    </div>
</div>
{% endblock %}
EOF

    # Create other basic templates
    for template in services.html menu.html cart.html checkout.html orders.html profile.html; do
        cat > templates/$template << EOF
{% extends "base.html" %}

{% block title %}${template%.*|title}{% endblock %}

{% block content %}
<div style="text-align: center; padding: 50px 20px;">
    <h1>${template%.*|title} Page</h1>
    <p style="margin: 20px 0;">This page is under construction.</p>
    <a href="/dashboard" style="padding: 10px 20px; background: #2196F3; color: white; text-decoration: none; border-radius: 5px;">
        Back to Dashboard
    </a>
</div>
{% endblock %}
EOF
    done
fi

# Create basic CSS if it doesn't exist
if [ ! -f "static/css/style.css" ]; then
    echo "Creating basic CSS..."
    cat > static/css/style.css << 'EOF'
/* Basic CSS for the application */
body {
    font-family: Arial, sans-serif;
    line-height: 1.6;
    margin: 0;
    padding: 0;
    background-color: #f4f4f4;
}

.container {
    width: 80%;
    margin: auto;
    overflow: hidden;
}

.btn {
    display: inline-block;
    padding: 10px 20px;
    background: #333;
    color: white;
    text-decoration: none;
    border-radius: 5px;
}

.btn:hover {
    background: #555;
}
EOF
fi

# Upgrade pip
pip install --upgrade pip

# Install Python dependencies
echo "Installing dependencies..."
pip install -r requirements.txt

# ✅ IMPORTANT: Initialize database tables
echo "Initializing database tables..."
python -c "
from app import create_tables_if_not_exists
create_tables_if_not_exists()
print('✅ Database tables initialized successfully')
"

# Set permissions
chmod -R 755 static/uploads

echo "Build completed successfully!"
echo "Final directory structure:"
ls -la
ls -la templates/
ls -la static/