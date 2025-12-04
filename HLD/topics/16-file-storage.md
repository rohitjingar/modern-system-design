# 16. File Storage (S3, Blob Storage)

File storage is where you put stuff and hope you never have to retrieve it. But when you do, you find out you forgot the file path, the region, and the access key. Welcome to cloud purgatory. ☁️😭

[← Back to Main](../README.md) | [Previous: Data Modeling](15-data-modeling.md) | [Next: Load Balancers →](17-load-balancers.md)

---

## 🎯 Quick Summary

**File Storage** (Object Storage) is how large files (images, videos, documents) are stored in the cloud. AWS S3, Azure Blob Storage, Google Cloud Storage are popular options. They're cheaper than databases for files, massively scalable, and handle millions of requests. Trade-off: higher latency than local disk, but unlimited scale and reliability.

Think of it as: **File Storage = Infinitely Large Hard Drive**

---

## 🌟 Beginner Explanation

### The Post Office Analogy

**LOCAL STORAGE (Hard Drive):**

```
Store files on your computer:

✅ Fast (local disk)
✅ No internet needed
✅ No monthly cost
❌ Limited space (1TB max usually)
❌ If computer dies, files gone
❌ Can't access from other places
❌ Expensive to add more storage

Example: Your laptop hard drive
```

**FILE STORAGE (S3/Cloud):**

```
Store files in the cloud:

✅ Unlimited space (literally infinite)
✅ Access from anywhere
✅ Automatic backups & redundancy
✅ Cheap per GB ($0.023/GB for S3)
✅ Handles millions of simultaneous requests
✅ No server maintenance
❌ Slightly higher latency (milliseconds)
❌ Ongoing monthly cost
❌ Network dependent

Example: S3, Google Cloud Storage, Azure Blob
```

### How File Storage Works

```
TRADITIONAL APPROACH (Bad):

Database stores file data:
│
├─ User uploads 10MB image
├─ Database processes upload
├─ Database stores as BLOB
├─ Database gets HUGE (10MB × 1M users = 10TB!)
├─ Database becomes slow
├─ Backups huge (10TB daily?)
├─ Expensive!

Problem:
❌ Database bloated
❌ Backups slow
❌ Performance hit
```

**FILE STORAGE APPROACH (Good):**

```
Database stores metadata, S3 stores file:

User uploads 10MB image:
│
├─ Database stores: filename, size, upload_date
├─ S3 stores: actual file data
├─ Database stays small
├─ Backups fast (metadata only)
├─ Both scale independently

Benefits:
✅ Database small & fast
✅ File storage unlimited
✅ Separate scaling
✅ Cheap!
```

### S3 Concepts

```
S3 STORAGE:

BUCKET:
├─ Like a folder/directory
├─ example.com-bucket-1
├─ Contains objects
└─ Region-specific (us-east-1, eu-west-1, etc)

OBJECT:
├─ Actual file
├─ Key: /images/profile-123.jpg
├─ Value: file data (bytes)
├─ Metadata: size, created date, etc
└─ Can be 0 bytes to 5TB!

STORAGE CLASS:
├─ STANDARD: Frequent access (default)
├─ INTELLIGENT_TIERING: Auto optimize
├─ GLACIER: Archive (cheap, slow access)
├─ DEEP_ARCHIVE: Very old files
└─ ONEZONE_IA: Single region, low access

PRICING:
├─ Storage: $0.023/GB/month (STANDARD)
├─ Transfer out: $0.09/GB (data leaving AWS)
├─ Requests: $0.0004 per 1000 PUT/GET
├─ Data transfer in: FREE!
└─ Example: 1TB = $23/month
```

---

## 🔬 Advanced Explanation

### Storage Architecture

**SINGLE FILE STORAGE (Simple):**

```
┌─────────────────────────┐
│  S3 Bucket (us-east-1)  │
│                         │
│  ├─ image-1.jpg         │
│  ├─ image-2.jpg         │
│  ├─ video-1.mp4         │
│  └─ document-1.pdf      │
└─────────────────────────┘

Access:
User → S3 direct
Response: 100-500ms (network dependent)

Problems:
❌ Geographic latency (Australia user waits 500ms)
❌ Single region (disaster in us-east-1 = all down)
```

**MULTI-REGION WITH CDN (Scalable):**

```
┌──────────────┐
│ S3 Bucket    │
│ (us-east-1)  │ ← Origin
└──────────────┘
       ↑
    replicate
       ↓
┌─────────────────────────────────────┐
│         CloudFront CDN              │
├─────────────────────────────────────┤
│ ├─ Edge in NY (10ms)                │
│ ├─ Edge in LA (50ms)                │
│ ├─ Edge in London (80ms)            │
│ └─ Edge in Sydney (30ms to AU users)│
└─────────────────────────────────────┘

Access:
User → Nearest CDN edge
Response: 50-100ms (global!)

Benefits:
✅ Fast everywhere
✅ CDN caches popular files
✅ If origin down, CDN still serves
✅ Reduced S3 load
```

### Upload Strategies

**DIRECT UPLOAD (Simple):**

```
Browser → S3 directly

Steps:
1. User selects file
2. Browser sends to S3
3. S3 stores file

Pros:
✅ Simple
✅ Server doesn't see file

Cons:
❌ Browser must authenticate with S3
❌ Exposes S3 credentials
❌ No server-side processing
```

**SERVER UPLOAD (Secure):**

```
Browser → Server → S3

Steps:
1. User selects file
2. Browser uploads to YOUR server
3. Server validates, processes, stores in S3
4. Server returns confirmation

Pros:
✅ Server validates file
✅ S3 credentials hidden
✅ Can process before storing
✅ Rate limiting possible

Cons:
❌ Server uses bandwidth twice
❌ Server disk space needed
❌ More complex
```

**PRESIGNED URL (Best of Both):**

```
Browser → Get presigned URL from server → S3 directly

Steps:
1. Browser: "I want to upload image.jpg"
2. Server: "OK, use this presigned URL (valid 15 min)"
3. Browser: Uploads directly to S3 with URL
4. S3: Validates signature, accepts upload
5. Server gets webhook notification

Pros:
✅ Direct upload (fast, no server bandwidth)
✅ Secure (signature-based)
✅ Server controls who can upload
✅ Server can validate metadata

Used by: Most apps (Dropbox, Google Photos, etc)
```

### Data Organization

**FLAT STRUCTURE (Simple):**

```
Bucket:
├─ image-1.jpg
├─ image-2.jpg
├─ image-3.jpg
├─ video-1.mp4
├─ document-1.pdf

Problem:
❌ Hard to organize
❌ No logical grouping
❌ Can't apply policies easily
```

**HIERARCHICAL STRUCTURE (Organized):**

```
Bucket:
├─ users/
│  ├─ alice/
│  │  ├─ profile.jpg
│  │  ├─ header.png
│  │  └─ settings.json
│  └─ bob/
│     ├─ profile.jpg
│     └─ avatar.png
├─ uploads/
│  ├─ 2024/01/
│  │  ├─ file1.pdf
│  │  └─ file2.docx
│  └─ 2024/02/
│     └─ file3.xlsx
└─ archives/
   ├─ 2023-backup.tar.gz
   └─ 2022-backup.tar.gz

Benefits:
✅ Organized
✅ Easy to apply policies
✅ Can expire old files
✅ Natural grouping
```

### Lifecycle Policies

```
Automatically move/delete files based on age

POLICY EXAMPLE:

├─ STANDARD: Days 0-30 (hot data)
│  Access frequently, keep fast
│
├─ INTELLIGENT_TIERING: Days 31-90 (warming)
│  Accessed occasionally
│  Auto-optimize cost
│
├─ GLACIER: Days 91-365 (cold data)
│  Rarely accessed
│  Cheap, slow retrieval (hours)
│
└─ DELETE: After 365 days (archive/delete)
   Old backup files gone

Cost reduction:
100GB on STANDARD: $2.30/month
100GB moved to GLACIER: $0.40/month
Savings: 83%! 💰
```

### Permissions & Security

```
BUCKET POLICIES:

1. Public Read (anyone can GET):
   ✅ Images for website
   ✅ Public documents
   ✅ Downloadable assets

2. Private (only authenticated):
   ✅ User files
   ✅ Private documents
   ✅ Sensitive data

3. Restricted (specific users):
   ✅ Team files
   ✅ Internal documents
   ✅ Shared projects

ENCRYPTION:

1. In Transit (HTTPS):
   ✅ File encrypted while uploading

2. At Rest (Server-side):
   ✅ File encrypted while stored
   ✅ S3 manages keys (default)
   ✅ Or you manage keys (KMS)

3. Client-side:
   ✅ You encrypt before upload
   ✅ Only you can decrypt
```

---

## 🐍 Python Code Example

### ❌ Without File Storage (Database Bloat)

```python
# ===== WITHOUT FILE STORAGE (BAD) =====

import sqlite3

class BadFileDB:
    """Stores files directly in database (bad idea!)"""
    
    def __init__(self):
        self.conn = sqlite3.connect(':memory:')
        self.cursor = self.conn.cursor()
        
        # Create table with BLOB column (🚩 red flag!)
        self.cursor.execute('''
            CREATE TABLE user_files (
                id INTEGER PRIMARY KEY,
                user_id INTEGER,
                filename TEXT,
                file_data BLOB
            )
        ''')
        self.conn.commit()
    
    def upload_file(self, user_id, filename, file_data):
        """Upload file to database (bloats database!)"""
        self.cursor.execute(
            '''INSERT INTO user_files (user_id, filename, file_data)
               VALUES (?, ?, ?)''',
            (user_id, filename, file_data)
        )
        self.conn.commit()
    
    def get_file(self, file_id):
        """Retrieve file from database"""
        self.cursor.execute(
            'SELECT filename, file_data FROM user_files WHERE id = ?',
            (file_id,)
        )
        return self.cursor.fetchone()

# Problems:
# ❌ Database grows HUGE (10GB file = 10GB database!)
# ❌ Backups massive
# ❌ Queries slow (file data mixed with metadata)
# ❌ Can't expire old files efficiently
# ❌ No built-in redundancy
# ❌ Expensive!

# Example:
db = BadFileDB()
large_file = b"x" * (100 * 1024 * 1024)  # 100MB file
db.upload_file(1, "large.bin", large_file)
print("Stored 100MB in database... 💀")
```

### ✅ With File Storage (S3)

```python
# ===== WITH FILE STORAGE (S3) =====

import boto3
from datetime import datetime

class S3FileStorage:
    """Store files in S3, metadata in database"""
    
    def __init__(self, bucket_name):
        self.s3 = boto3.client('s3')
        self.bucket = bucket_name
        self.metadata = {}  # Simulate database
        self.file_id = 1
    
    def upload_file(self, user_id, filename, file_data):
        """Upload file to S3, store metadata"""
        
        # Generate unique key
        key = f"users/{user_id}/{filename}"
        
        # Upload to S3
        self.s3.put_object(
            Bucket=self.bucket,
            Key=key,
            Body=file_data,
            Metadata={
                'user_id': str(user_id),
                'uploaded_at': datetime.now().isoformat()
            }
        )
        
        # Store METADATA in database (tiny!)
        self.metadata[self.file_id] = {
            'user_id': user_id,
            'filename': filename,
            's3_key': key,
            'size_bytes': len(file_data),
            'uploaded_at': datetime.now().isoformat()
        }
        
        file_id = self.file_id
        self.file_id += 1
        
        return file_id
    
    def get_file_url(self, file_id, expiration_seconds=3600):
        """Get pre-signed URL for file access"""
        
        if file_id not in self.metadata:
            return None
        
        key = self.metadata[file_id]['s3_key']
        
        # Generate presigned URL (valid for 1 hour)
        url = self.s3.generate_presigned_url(
            'get_object',
            Params={'Bucket': self.bucket, 'Key': key},
            ExpiresIn=expiration_seconds
        )
        
        return url
    
    def delete_file(self, file_id):
        """Delete file from S3"""
        
        if file_id not in self.metadata:
            return False
        
        key = self.metadata[file_id]['s3_key']
        
        self.s3.delete_object(Bucket=self.bucket, Key=key)
        del self.metadata[file_id]
        
        return True
    
    def get_storage_stats(self):
        """Get storage statistics"""
        total_size = sum(f['size_bytes'] for f in self.metadata.values())
        return {
            'files': len(self.metadata),
            'total_size_gb': total_size / (1024 ** 3),
            'cost_per_month': (total_size / (1024 ** 3)) * 0.023
        }

# Benefits:
# ✅ Database stays small (only metadata)
# ✅ Files stored in unlimited S3
# ✅ Automatic backups
# ✅ Cheap!
# ✅ Global access
# ✅ No server storage needed

# Example usage (requires AWS credentials):
# storage = S3FileStorage('my-bucket')
# large_file = b"x" * (100 * 1024 * 1024)  # 100MB
# file_id = storage.upload_file(1, "large.bin", large_file)
# url = storage.get_file_url(file_id)
# print(f"Download at: {url}")
```

### ✅ Production File Storage (Advanced)

```python
# ===== PRODUCTION FILE STORAGE =====

import boto3
from botocore.exceptions import ClientError
import hashlib
from datetime import datetime, timedelta

class ProductionFileStorage:
    """Production-grade file storage with best practices"""
    
    def __init__(self, bucket_name, region='us-east-1'):
        self.s3 = boto3.client('s3', region_name=region)
        self.bucket = bucket_name
        self.region = region
    
    def upload_file_with_validation(self, user_id, filename, file_data, 
                                    max_size_mb=100, allowed_types=None):
        """Upload with validation"""
        
        # Validate file size
        file_size_mb = len(file_data) / (1024 ** 2)
        if file_size_mb > max_size_mb:
            raise ValueError(f"File too large: {file_size_mb}MB > {max_size_mb}MB")
        
        # Validate file type (by extension)
        if allowed_types:
            ext = filename.split('.')[-1].lower()
            if ext not in allowed_types:
                raise ValueError(f"File type {ext} not allowed")
        
        # Generate unique key
        file_hash = hashlib.md5(file_data).hexdigest()
        date_path = datetime.now().strftime('%Y/%m/%d')
        key = f"users/{user_id}/{date_path}/{file_hash}-{filename}"
        
        try:
            # Upload with encryption & metadata
            self.s3.put_object(
                Bucket=self.bucket,
                Key=key,
                Body=file_data,
                ServerSideEncryption='AES256',
                Metadata={
                    'user_id': str(user_id),
                    'original_filename': filename,
                    'uploaded_at': datetime.now().isoformat()
                },
                ContentType=self._get_content_type(filename),
                StorageClass='INTELLIGENT_TIERING'  # Auto-optimize costs
            )
            
            return {
                'success': True,
                's3_key': key,
                'size_bytes': len(file_data),
                'uploaded_at': datetime.now().isoformat()
            }
        
        except ClientError as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def get_presigned_url(self, s3_key, expiration_hours=1):
        """Get presigned URL for secure download"""
        
        try:
            url = self.s3.generate_presigned_url(
                'get_object',
                Params={'Bucket': self.bucket, 'Key': s3_key},
                ExpiresIn=expiration_hours * 3600
            )
            return url
        except ClientError as e:
            return None
    
    def get_presigned_post_url(self, user_id, filename, max_size_mb=100):
        """Get presigned POST URL for browser upload"""
        
        key = f"users/{user_id}/{filename}"
        
        try:
            response = self.s3.generate_presigned_post(
                Bucket=self.bucket,
                Key=key,
                ExpiresIn=3600,
                Conditions=[
                    ['content-length-range', 0, max_size_mb * 1024 * 1024]
                ]
            )
            return response
        except ClientError as e:
            return None
    
    def setup_lifecycle_policy(self):
        """Set up automatic archival for old files"""
        
        lifecycle_config = {
            'Rules': [
                {
                    'Id': 'Archive old files',
                    'Status': 'Enabled',
                    'Prefix': 'users/',
                    'Transitions': [
                        {
                            'Days': 30,
                            'StorageClass': 'GLACIER'  # Move to cold storage
                        },
                        {
                            'Days': 365,
                            'StorageClass': 'DEEP_ARCHIVE'  # Move to archive
                        }
                    ],
                    'Expiration': {
                        'Days': 2555  # Delete after 7 years
                    }
                }
            ]
        }
        
        try:
            self.s3.put_bucket_lifecycle_configuration(
                Bucket=self.bucket,
                LifecycleConfiguration=lifecycle_config
            )
            return True
        except ClientError:
            return False
    
    def _get_content_type(self, filename):
        """Determine content type from filename"""
        ext_to_type = {
            'jpg': 'image/jpeg',
            'jpeg': 'image/jpeg',
            'png': 'image/png',
            'gif': 'image/gif',
            'pdf': 'application/pdf',
            'mp4': 'video/mp4',
            'txt': 'text/plain'
        }
        ext = filename.split('.')[-1].lower()
        return ext_to_type.get(ext, 'application/octet-stream')

# Usage
# storage = ProductionFileStorage('my-bucket')
# 
# # Upload with validation
# result = storage.upload_file_with_validation(
#     user_id=1,
#     filename='profile.jpg',
#     file_data=open('profile.jpg', 'rb').read(),
#     max_size_mb=10,
#     allowed_types=['jpg', 'jpeg', 'png']
# )
# 
# # Get download URL
# url = storage.get_presigned_url(result['s3_key'])
# 
# # Get browser upload URL
# post_data = storage.get_presigned_post_url(1, 'avatar.jpg')
# 
# # Set up auto-archival
# storage.setup_lifecycle_policy()
```

---

## 💡 Mini Project: "Build a File Management System"

### Phase 1: Simple Upload/Download ⭐

**Requirements:**
- Upload files to S3
- List files
- Download files
- Delete files
- Basic metadata

---

### Phase 2: Advanced (With Validation) ⭐⭐

**Requirements:**
- File type validation
- Size limits
- Pre-signed URLs
- Lifecycle policies
- Cost tracking

---

### Phase 3: Enterprise (Full System) ⭐⭐⭐

**Requirements:**
- Multi-tenant support
- Access control
- Virus scanning
- CDN integration
- Analytics dashboard

---

## ⚖️ Storage Services Comparison

| Feature | AWS S3 | Azure Blob | Google Cloud | MinIO |
|---------|--------|-----------|--------------|-------|
| **Cost** | $0.023/GB | $0.018/GB | $0.020/GB | Self-hosted |
| **Regions** | 30+ | 60+ | 40+ | Any |
| **Durability** | 11 nines | 11 nines | 11 nines | Configurable |
| **Throughput** | Unlimited | High | High | Limited |
| **CDN Integration** | CloudFront | Built-in | Built-in | External |
| **Ease of Use** | Very easy | Easy | Easy | Hard |
| **Enterprise** | ✅ | ✅ | ✅ | ❌ |

---

## 🎯 When to Use File Storage

```
✅ USE FILE STORAGE WHEN:
- Large files (>10MB)
- Images, videos, documents
- Millions of files
- Global distribution needed
- Cost matters
- Unlimited capacity needed

❌ DON'T USE WHEN:
- Small metadata only
- Relational queries needed
- Strong consistency required
- Need random access (HDD better)
```

---

## ❌ Common Mistakes

### Mistake 1: Storing Everything in Database

```python
# ❌ Don't do this
database.store_image_blob(image_file)

# ✅ Do this
s3.upload(image_file)
database.store_metadata(filename, s3_key)
```

### Mistake 2: Not Setting Expiration

```python
# ❌ Old files stay forever
# ✅ Set lifecycle policy
storage.setup_lifecycle_policy()
# Auto-delete after 7 years
```

### Mistake 3: Public Access

```python
# ❌ Anyone can download
bucket.make_public()

# ✅ Use presigned URLs
url = storage.get_presigned_url(key, expiration_hours=1)
# Valid for 1 hour only
```

---

## 📚 Additional Resources

**AWS S3:**
- [S3 Documentation](https://docs.aws.amazon.com/s3/)
- [S3 Pricing](https://aws.amazon.com/s3/pricing/)
- [S3 Best Practices](https://docs.aws.amazon.com/AmazonS3/latest/userguide/BestPractices.html)

**Alternatives:**
- [Azure Blob Storage](https://azure.microsoft.com/en-us/products/storage/blobs/)
- [Google Cloud Storage](https://cloud.google.com/storage)
- [MinIO](https://min.io/) - Open source S3-compatible


---

## 🎯 Before You Leave

**Can you answer these?**

1. **Why not store files in a database?**
   - Answer: Bloats database, slow backups, expensive

2. **What's a presigned URL?**
   - Answer: Time-limited URL for secure access without credentials

3. **What's S3 storage class?**
   - Answer: Different tiers (STANDARD, GLACIER, etc) for different access patterns

4. **How do you organize S3 files?**
   - Answer: Hierarchical paths (users/alice/profile.jpg)

5. **What's lifecycle policy?**
   - Answer: Auto-move/delete files based on age to reduce costs

**If you got these right, you're ready for the next topic!** ✅

---

## 🤣 Closing Thoughts

> **Developer:** "I stored all our files in S3!"
>
> **CEO:** "Great! How much does it cost?"
>
> **Developer:** "Well... we have a 10TB bucket..."
>
> **CEO:** "And?"
>
> **Developer:** "...with no lifecycle policy. It's been 5 years."
>
> **CEO:** *faints* 💀

---

[← Back to Main](../README.md) | [Previous: Data Modeling](15-data-modeling.md) | [Next: Load Balancers →](17-load-balancers.md)

---

**Last Updated:** November 10, 2025  
**Difficulty:** ⭐⭐ Beginner-Intermediate (cloud concepts)  
**Time to Read:** 24 minutes  
**Time to Build System:** 3-5 hours per phase  

---

*File storage: Where your files go to live their best cloud life, forever and ever, costing you $23/month.* 🚀