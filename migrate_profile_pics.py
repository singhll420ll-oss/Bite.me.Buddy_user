# migrate_profile_pics.py - COMPLETELY FIXED VERSION (NO SIGNATURE ERRORS)
import os
import sys
import psycopg
from psycopg.rows import dict_row
import cloudinary
import cloudinary.uploader
from datetime import datetime
import time

# Cloudinary Configuration
cloudinary.config(
    cloud_name=os.environ.get("CLOUDINARY_CLOUD_NAME"),
    api_key=os.environ.get("CLOUDINARY_API_KEY"),
    api_secret=os.environ.get("CLOUDINARY_API_SECRET"),
    secure=True
)

def get_db_connection():
    """Establish database connection"""
    database_url = os.environ.get('DATABASE_URL')
    if not database_url:
        raise ValueError("DATABASE_URL environment variable is not set")
    
    if database_url.startswith('postgres://'):
        database_url = database_url.replace('postgres://', 'postgresql://', 1)
    
    return psycopg.connect(database_url, row_factory=dict_row)

def check_cloudinary_credentials():
    """Verify Cloudinary credentials are working"""
    print("🔐 Checking Cloudinary credentials...")
    try:
        # Simple test to verify credentials
        test_result = cloudinary.uploader.upload(
            "https://res.cloudinary.com/demo/image/upload/sample.jpg",
            folder="test_folder",
            public_id="test_connection",
            overwrite=True,
            transformation="w_100,h_100,c_fill"
        )
        print("✅ Cloudinary credentials are valid!")
        return True
    except Exception as e:
        print(f"❌ Cloudinary credentials error: {str(e)}")
        return False

def migrate_existing_users():
    """Migrate existing users' profile pics to Cloudinary - FIXED SIGNATURE ERROR"""
    print("🚀 Starting migration of existing profile pictures to Cloudinary...")
    print("=" * 60)
    
    total_start_time = time.time()
    
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        
        # Get all users with local profile pics or default avatars
        cur.execute("""
            SELECT id, profile_pic, full_name, email
            FROM users 
            WHERE (
                profile_pic NOT LIKE 'http%' 
                OR profile_pic LIKE '%default-avatar%'
                OR profile_pic IS NULL
                OR profile_pic = ''
            )
            ORDER BY id
        """)
        
        users = cur.fetchall()
        print(f"📊 Found {len(users)} users to process")
        
        if len(users) == 0:
            print("✅ All users already have Cloudinary URLs!")
            conn.close()
            return True
        
        migrated_count = 0
        failed_count = 0
        skipped_count = 0
        default_set_count = 0
        
        # Default Cloudinary avatar URL
        DEFAULT_AVATAR_URL = "https://res.cloudinary.com/demo/image/upload/v1234567890/profile_pics/default-avatar.png"
        
        print("\n📦 Starting migration process...")
        print("-" * 60)
        
        for index, user in enumerate(users, 1):
            user_id = user['id']
            old_pic = user['profile_pic'] or 'None'
            user_name = user['full_name']
            
            print(f"\n[{index}/{len(users)}] Processing User #{user_id}: {user_name}")
            print(f"   Current profile pic: {old_pic}")
            
            # Case 1: Local file exists
            if old_pic and old_pic != 'None' and not old_pic.startswith('http'):
                filepath = os.path.join('static', 'uploads', old_pic)
                
                if os.path.exists(filepath):
                    try:
                        print(f"   📤 Uploading to Cloudinary...")
                        
                        # ✅ FIXED: Use transformation string to avoid signature error
                        upload_start = time.time()
                        
                        result = cloudinary.uploader.upload(
                            filepath,
                            folder="profile_pics",
                            public_id=f"migrated_user_{user_id}_{int(time.time())}",
                            overwrite=True,
                            transformation="w_500,h_500,c_fill,q_auto,f_auto"
                        )
                        
                        upload_time = time.time() - upload_start
                        
                        cloudinary_url = result["secure_url"]
                        
                        # Update database
                        cur.execute(
                            "UPDATE users SET profile_pic = %s WHERE id = %s",
                            (cloudinary_url, user_id)
                        )
                        
                        # Optional: Delete local file after successful upload
                        # os.remove(filepath)
                        
                        print(f"   ✅ Uploaded in {upload_time:.2f}s")
                        print(f"   🔗 New URL: {cloudinary_url[:50]}...")
                        migrated_count += 1
                        
                    except Exception as e:
                        print(f"   ❌ Upload failed: {str(e)[:100]}")
                        failed_count += 1
                else:
                    print(f"   ⚠️  Local file not found: {filepath}")
                    skipped_count += 1
            
            # Case 2: Null, empty, or default avatar
            elif not old_pic or old_pic == '' or old_pic == 'None' or 'default-avatar' in str(old_pic):
                try:
                    cur.execute(
                        "UPDATE users SET profile_pic = %s WHERE id = %s",
                        (DEFAULT_AVATAR_URL, user_id)
                    )
                    print(f"   🔄 Set to Cloudinary default avatar")
                    default_set_count += 1
                except Exception as e:
                    print(f"   ❌ Failed to set default: {str(e)}")
                    failed_count += 1
            
            # Case 3: Already has Cloudinary URL but needs transformation fix
            elif 'cloudinary' in old_pic and 'w_500' not in old_pic:
                try:
                    # Extract public_id from existing URL
                    parts = old_pic.split('/')
                    if 'upload' in parts:
                        upload_index = parts.index('upload')
                        if upload_index + 1 < len(parts):
                            # Re-upload with transformation
                            print(f"   🔧 Fixing existing Cloudinary image...")
                            
                            result = cloudinary.uploader.upload(
                                old_pic,
                                folder="profile_pics",
                                public_id=f"fixed_user_{user_id}_{int(time.time())}",
                                overwrite=True,
                                transformation="w_500,h_500,c_fill,q_auto,f_auto"
                            )
                            
                            cur.execute(
                                "UPDATE users SET profile_pic = %s WHERE id = %s",
                                (result["secure_url"], user_id)
                            )
                            
                            print(f"   ✅ Fixed transformation")
                            migrated_count += 1
                except Exception as e:
                    print(f"   ⚠️  Could not fix existing URL: {str(e)[:80]}")
                    skipped_count += 1
        
        # Commit all changes
        conn.commit()
        
        total_time = time.time() - total_start_time
        
        print("\n" + "=" * 60)
        print("📈 MIGRATION COMPLETE - SUMMARY")
        print("=" * 60)
        print(f"🕐 Total time: {total_time:.2f} seconds")
        print(f"👥 Total users processed: {len(users)}")
        print(f"✅ Successfully migrated: {migrated_count}")
        print(f"🔄 Set to default: {default_set_count}")
        print(f"⚠️  Skipped: {skipped_count}")
        print(f"❌ Failed: {failed_count}")
        print("=" * 60)
        
        # Verify results
        verify_migration(cur)
        
        conn.close()
        
        return True
        
    except Exception as e:
        print(f"💥 Migration error: {str(e)}")
        return False

def verify_migration(cur):
    """Verify migration results"""
    print("\n🔍 Verifying migration results...")
    
    cur.execute("SELECT COUNT(*) as total FROM users")
    total_users = cur.fetchone()['total']
    
    cur.execute("""
        SELECT COUNT(*) as cloudinary_count 
        FROM users 
        WHERE profile_pic LIKE '%cloudinary%'
    """)
    cloudinary_users = cur.fetchone()['cloudinary_count']
    
    cur.execute("""
        SELECT COUNT(*) as local_count 
        FROM users 
        WHERE profile_pic NOT LIKE 'http%' 
        AND profile_pic IS NOT NULL 
        AND profile_pic != ''
    """)
    local_users = cur.fetchone()['local_count']
    
    cur.execute("""
        SELECT COUNT(*) as null_count 
        FROM users 
        WHERE profile_pic IS NULL OR profile_pic = ''
    """)
    null_users = cur.fetchone()['null_count']
    
    print(f"   📊 Total users: {total_users}")
    print(f"   ☁️  Users with Cloudinary URLs: {cloudinary_users}")
    print(f"   💾 Users with local files: {local_users}")
    print(f"   ❓ Users with null/empty: {null_users}")
    
    if local_users == 0 and null_users == 0:
        print("\n🎉 SUCCESS: All users migrated to Cloudinary!")
    else:
        print(f"\n⚠️  ATTENTION: {local_users + null_users} users still need migration")

def create_migration_report():
    """Create a detailed migration report"""
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        
        cur.execute("""
            SELECT 
                COUNT(*) as total_users,
                SUM(CASE WHEN profile_pic LIKE '%cloudinary%' THEN 1 ELSE 0 END) as cloudinary_users,
                SUM(CASE WHEN profile_pic NOT LIKE 'http%' AND profile_pic IS NOT NULL AND profile_pic != '' THEN 1 ELSE 0 END) as local_users,
                SUM(CASE WHEN profile_pic IS NULL OR profile_pic = '' THEN 1 ELSE 0 END) as null_users
            FROM users
        """)
        
        stats = cur.fetchone()
        
        report = f"""
        ============================================
        PROFILE PICTURE MIGRATION REPORT
        Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
        ============================================
        
        📊 STATISTICS:
        Total Users: {stats['total_users']}
        Cloudinary Users: {stats['cloudinary_users']}
        Local File Users: {stats['local_users']}
        Null/Empty Users: {stats['null_users']}
        
        📈 MIGRATION STATUS:
        Migration Percentage: {(stats['cloudinary_users']/stats['total_users']*100):.1f}%
        
        {'✅ COMPLETE' if stats['local_users'] == 0 and stats['null_users'] == 0 else '⚠️  INCOMPLETE'}
        
        ============================================
        """
        
        print(report)
        
        # Save report to file
        with open('migration_report.txt', 'w') as f:
            f.write(report)
        
        print("📄 Report saved to 'migration_report.txt'")
        
        conn.close()
        
    except Exception as e:
        print(f"Error creating report: {str(e)}")

if __name__ == '__main__':
    print("=" * 60)
    print("PROFILE PICTURE MIGRATION TOOL")
    print("CLOUDINARY SIGNATURE ERROR FIXED VERSION")
    print("=" * 60)
    
    # Check environment variables
    required_vars = ['DATABASE_URL', 'CLOUDINARY_CLOUD_NAME', 'CLOUDINARY_API_KEY', 'CLOUDINARY_API_SECRET']
    missing_vars = [var for var in required_vars if not os.environ.get(var)]
    
    if missing_vars:
        print("❌ Missing environment variables:")
        for var in missing_vars:
            print(f"   - {var}")
        print("\nPlease set them before running:")
        print("export DATABASE_URL='postgresql://user:pass@localhost/dbname'")
        print("export CLOUDINARY_CLOUD_NAME='your_cloud_name'")
        print("export CLOUDINARY_API_KEY='your_api_key'")
        print("export CLOUDINARY_API_SECRET='your_api_secret'")
        sys.exit(1)
    
    # Check Cloudinary credentials
    if not check_cloudinary_credentials():
        print("\n❌ Cannot proceed with invalid Cloudinary credentials")
        sys.exit(1)
    
    print("\n" + "=" * 60)
    print("MIGRATION OPTIONS:")
    print("1. Run full migration")
    print("2. Check migration status only")
    print("3. Generate migration report")
    print("=" * 60)
    
    try:
        choice = input("Select option (1/2/3): ").strip()
        
        if choice == '1':
            print("\n🚀 Starting full migration...")
            confirmation = input("Are you sure? This will update all user profile pictures (y/n): ")
            if confirmation.lower() == 'y':
                success = migrate_existing_users()
                if success:
                    create_migration_report()
            else:
                print("Migration cancelled.")
        
        elif choice == '2':
            print("\n🔍 Checking migration status...")
            try:
                conn = get_db_connection()
                cur = conn.cursor()
                verify_migration(cur)
                conn.close()
            except Exception as e:
                print(f"Error checking status: {str(e)}")
        
        elif choice == '3':
            print("\n📄 Generating migration report...")
            create_migration_report()
        
        else:
            print("Invalid choice. Exiting.")
    
    except KeyboardInterrupt:
        print("\n\n⚠️  Migration interrupted by user.")
    
    except Exception as e:
        print(f"\n💥 Unexpected error: {str(e)}")
    
    finally:
        print("\n" + "=" * 60)
        print("Migration tool completed.")
        print("=" * 60)