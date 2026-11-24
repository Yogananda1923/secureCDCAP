from typing import List, Dict, Any

SAMPLE_PROGRAMS: List[Dict[str, Any]] = [
    {
        "id": "sample-py-vuln-login",
        "title": "Vulnerable Python Login Application",
        "language": "python",
        "category": "Injection & Hardcoded Secrets",
        "is_vulnerable": True,
        "description": "Educational sample demonstrating SQL injection via f-strings and hardcoded database credentials.",
        "expected_vulns": ["SQL Injection", "Hardcoded Credentials"],
        "expected_fix": "Parameterized queries and os.getenv() configuration.",
        "code": '''import sqlite3

# EDUCATIONAL DEMONSTRATION SAMPLE: VULNERABLE
DATABASE_PASSWORD = "HardcodedAdminPass2026!"

def login_user(username, user_password):
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()
    # Vulnerable f-string query construction: SQL Injection
    query = f"SELECT id, role FROM accounts WHERE user = '{username}' AND pass = '{user_password}'"
    cursor.execute(query)
    record = cursor.fetchone()
    conn.close()
    return record
'''
    },
    {
        "id": "sample-py-secure-login",
        "title": "Secure Python Login Application",
        "language": "python",
        "category": "Authentication",
        "is_vulnerable": False,
        "description": "Hardened Python login service using environment variables, parameterized SQL, and safe authentication practices.",
        "expected_vulns": [],
        "expected_fix": "Already secured against OWASP Top 10 injection vectors.",
        "code": '''import sqlite3
import os

DATABASE_PASSWORD = os.getenv("DATABASE_PASSWORD", "")

def login_user(username, user_password):
    """Hardened user login with parameterized prepared statement."""
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()
    # Parameterized query protects against SQL Injection
    cursor.execute("SELECT id, role, password_hash FROM accounts WHERE user = ?", (username,))
    record = cursor.fetchone()
    conn.close()
    return record
'''
    },
    {
        "id": "sample-py-cmd-inj",
        "title": "Python OS Command Injection Example",
        "language": "python",
        "category": "Injection",
        "is_vulnerable": True,
        "description": "Server diagnostic function invoking os.system with unvalidated user input.",
        "expected_vulns": ["Command Injection"],
        "expected_fix": "subprocess.run() with shell=False and argument vector.",
        "code": '''import os

# EDUCATIONAL DEMONSTRATION SAMPLE: VULNERABLE
def run_network_diagnostic(target_host):
    # Untrusted concatenation into system command shell
    command = "traceroute -m 5 " + target_host
    os.system(command)
'''
    },
    {
        "id": "sample-py-weak-crypto",
        "title": "Python Weak Cryptography & Secret Example",
        "language": "python",
        "category": "Authentication & Cryptography",
        "is_vulnerable": True,
        "description": "Cryptographic utility using deprecated MD5 hashing and hardcoded HMAC secret.",
        "expected_vulns": ["Weak Hash", "Hardcoded Credentials"],
        "expected_fix": "Migrate to SHA-256 / Argon2id and use environment variable for secret key.",
        "code": '''import hashlib

# EDUCATIONAL DEMONSTRATION SAMPLE: VULNERABLE
API_SECRET_KEY = "sk_live_prod_9988112233"

def hash_user_token(token_str):
    # Broken MD5 cryptographic hash
    return hashlib.md5(token_str.encode()).hexdigest()
'''
    },
    {
        "id": "sample-c-bof",
        "title": "C Stack Buffer Overflow Demonstration",
        "language": "c",
        "category": "Memory & Pointer Safety",
        "is_vulnerable": True,
        "description": "Classic stack smashing vulnerability caused by gets() and unbounded strcpy().",
        "expected_vulns": ["Classic Buffer Overflow"],
        "expected_fix": "Bounded fgets() and strncpy() with null-byte termination.",
        "code": '''#include <stdio.h>
#include <string.h>

// EDUCATIONAL DEMONSTRATION SAMPLE: VULNERABLE
void authenticate_client() {
    char username[32];
    char password[32];
    
    // Dangerous unbounded reading
    gets(username);
    
    // Unchecked memory copy
    strcpy(password, username);
}
'''
    },
    {
        "id": "sample-c-safe-string",
        "title": "Safe C String Handling Example",
        "language": "c",
        "category": "Memory & Pointer Safety",
        "is_vulnerable": False,
        "description": "Robust C programming using bounded buffers, snprintf(), and size checks.",
        "expected_vulns": [],
        "expected_fix": "Complies with CERT C coding standards.",
        "code": '''#include <stdio.h>
#include <string.h>

void safe_client_handler(const char *input_str) {
    char buffer[64];
    if (input_str != NULL) {
        snprintf(buffer, sizeof(buffer), "%s", input_str);
        printf("%s\\n", buffer);
    }
}
'''
    },
    {
        "id": "sample-java-path-traversal",
        "title": "Java Insecure File Handling Example",
        "language": "java",
        "category": "General Security",
        "is_vulnerable": True,
        "description": "File download endpoint prone to directory traversal via unvalidated user path.",
        "expected_vulns": ["Path Traversal"],
        "expected_fix": "Canonical path verification preventing directory escape.",
        "code": '''import java.io.File;
import java.io.FileInputStream;

// EDUCATIONAL DEMONSTRATION SAMPLE: VULNERABLE
public class FileService {
    public FileInputStream downloadReport(String baseDir, String userFilename) throws Exception {
        // Path Traversal: userFilename may contain "../"
        File target = new File(baseDir, userFilename);
        return new FileInputStream(target);
    }
}
'''
    },
    {
        "id": "sample-java-secure-input",
        "title": "Java Secure Input Validation Example",
        "language": "java",
        "category": "Input Validation & Injection",
        "is_vulnerable": False,
        "description": "Secured Java service enforcing strict regular expression validation and PreparedStatement.",
        "expected_vulns": [],
        "expected_fix": "Standard compliant enterprise Java code.",
        "code": '''import java.sql.Connection;
import java.sql.PreparedStatement;
import java.sql.ResultSet;

public class SecureUserService {
    public void queryUser(Connection conn, String username) throws Exception {
        // Whitelist validation
        if (username == null || !username.matches("^[a-zA-Z0-9_]{3,30}$")) {
            throw new IllegalArgumentException("Invalid username format");
        }
        String sql = "SELECT id, email FROM users WHERE username = ?";
        try (PreparedStatement stmt = conn.prepareStatement(sql)) {
            stmt.setString(1, username);
            ResultSet rs = stmt.executeQuery();
        }
    }
}
'''
    }
]

