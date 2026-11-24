from typing import List, Dict, Any

PREDEFINED_TEST_CASES: List[Dict[str, Any]] = [
    # ------------------- PYTHON TEST CASES (11) -------------------
    {
        "test_id": "TC-PY-01",
        "name": "Secure Python User Service",
        "language": "python",
        "category": "Clean Code",
        "description": "Clean, robust Python code utilizing parameterized database queries, input validation, and secure password hashing.",
        "source_code": '''import hashlib
import os

def calculate_checksum(data: str) -> str:
    """Safe SHA-256 calculation."""
    return hashlib.sha256(data.encode('utf-8')).hexdigest()

def get_user_record(cursor, username: str):
    """Safe parameterized query."""
    query = "SELECT id, username, email FROM users WHERE username = ?"
    cursor.execute(query, (username,))
    return cursor.fetchone()
''',
        "expected_detection": "Clean",
        "expected_severity": "None",
        "expected_verification": "Passed"
    },
    {
        "test_id": "TC-PY-02",
        "name": "Python SQL Injection via f-string",
        "language": "python",
        "category": "Injection",
        "description": "Vulnerable database query constructing dynamic SQL using f-strings directly inside cursor.execute().",
        "source_code": '''def authenticate_user(cursor, username, password):
    # Vulnerable f-string SQL injection
    cursor.execute(f"SELECT * FROM users WHERE username = '{username}' AND password = '{password}'")
    return cursor.fetchone()
''',
        "expected_detection": "SQL Injection",
        "expected_severity": "Critical",
        "expected_verification": "Passed"
    },
    {
        "test_id": "TC-PY-03",
        "name": "Python Command Injection via os.system",
        "language": "python",
        "category": "Injection",
        "description": "Vulnerable shell command invocation concatenating untrusted user input directly into os.system.",
        "source_code": '''import os

def ping_host(host_ip):
    # Vulnerable OS Command Injection
    os.system("ping -c 1 " + host_ip)
''',
        "expected_detection": "Command Injection",
        "expected_severity": "Critical",
        "expected_verification": "Passed"
    },
    {
        "test_id": "TC-PY-04",
        "name": "Python Hardcoded Secret and API Token",
        "language": "python",
        "category": "Authentication & Cryptography",
        "description": "Hardcoded database password and API key embedded in source code.",
        "source_code": '''# Insecure hardcoded credentials
api_key = "ak_live_9874123098124098123"
password = "SuperSecretAdminPassword123!"

def connect():
    print(f"Connecting with {api_key}")
''',
        "expected_detection": "Hardcoded Credentials",
        "expected_severity": "High",
        "expected_verification": "Passed"
    },
    {
        "test_id": "TC-PY-05",
        "name": "Python Weak Cryptographic Hashing (MD5)",
        "language": "python",
        "category": "Authentication & Cryptography",
        "description": "Use of obsolete MD5 hash function for security sensitive user credentials.",
        "source_code": '''import hashlib

def store_password(raw_password):
    # Insecure MD5 hashing
    hashed = hashlib.md5(raw_password.encode()).hexdigest()
    return hashed
''',
        "expected_detection": "Weak Hash",
        "expected_severity": "Medium",
        "expected_verification": "Passed"
    },
    {
        "test_id": "TC-PY-06",
        "name": "Python Path Traversal via open()",
        "language": "python",
        "category": "General Security",
        "description": "Opening file paths constructed by concatenating untrusted user filename without directory boundary checks.",
        "source_code": '''def read_user_document(user_filename):
    # Vulnerable Path Traversal
    with open("/var/app/data/" + user_filename, "r") as f:
        return f.read()
''',
        "expected_detection": "Path Traversal",
        "expected_severity": "High",
        "expected_verification": "Passed"
    },
    {
        "test_id": "TC-PY-07",
        "name": "Python Insecure Temporary File Creation",
        "language": "python",
        "category": "General Security",
        "description": "Use of deprecated tempfile.mktemp() susceptible to race condition (TOCTOU).",
        "source_code": '''import tempfile

def create_scratch_file(data):
    # Insecure temporary file
    temp_path = tempfile.mktemp()
    with open(temp_path, "w") as f:
        f.write(data)
    return temp_path
''',
        "expected_detection": "Insecure Temp File",
        "expected_severity": "Medium",
        "expected_verification": "Passed"
    },
    {
        "test_id": "TC-PY-08",
        "name": "Python Unsafe Deserialization via pickle.loads",
        "language": "python",
        "category": "Input Validation",
        "description": "Deserializing arbitrary untrusted user byte payload with pickle leading to arbitrary remote code execution.",
        "source_code": '''import pickle

def unpack_session_token(token_bytes):
    # Dangerous deserialization of untrusted payload
    session_data = pickle.loads(token_bytes)
    return session_data
''',
        "expected_detection": "Deserialization of Untrusted Data",
        "expected_severity": "Critical",
        "expected_verification": "Passed"
    },
    {
        "test_id": "TC-PY-09",
        "name": "Python Dead Code Elimination",
        "language": "python",
        "category": "Optimization",
        "description": "Program with unreachable statements following return and unreachable 'if False' block.",
        "source_code": '''def calculate_discount(price):
    if False:
        debug_log = "Unreachable branch"
        price = price * 2
    return price * 0.9
    dead_statement = "Never executed after return"
''',
        "expected_detection": "Clean",
        "expected_severity": "None",
        "expected_verification": "Passed"
    },
    {
        "test_id": "TC-PY-10",
        "name": "Python Constant Folding Pass",
        "language": "python",
        "category": "Optimization",
        "description": "Compile-time arithmetic constants eligible for constant folding optimization.",
        "source_code": '''def compute_constants():
    # Eligible for constant folding (24 * 60 * 60 = 86400)
    seconds_in_day = 24 * 60 * 60
    base_fee = 100 + 50 * 2
    return seconds_in_day + base_fee
''',
        "expected_detection": "Clean",
        "expected_severity": "None",
        "expected_verification": "Passed"
    },
    {
        "test_id": "TC-PY-11",
        "name": "Python Silent Exception Suppression",
        "language": "python",
        "category": "General Security",
        "description": "Swallowing all exceptions silently with broad except: pass block.",
        "source_code": '''def transfer_funds(account_from, account_to, amount):
    try:
        account_from.deduct(amount)
        account_to.credit(amount)
    except:
        # Silently suppressed exception
        pass
''',
        "expected_detection": "Improper Exception Handling",
        "expected_severity": "Low",
        "expected_verification": "Passed"
    },

    # ------------------- C TEST CASES (10) -------------------
    {
        "test_id": "TC-C-01",
        "name": "Safe Bounded C String Copy",
        "language": "c",
        "category": "Clean Code",
        "description": "C program implementing safe bounded string handling with snprintf and explicit null-terminators.",
        "source_code": '''#include <stdio.h>
#include <string.h>

void safe_copy(const char *src) {
    char dest[64];
    snprintf(dest, sizeof(dest), "%s", src);
    printf("Safe buffer: %s\\n", dest);
}
''',
        "expected_detection": "Clean",
        "expected_severity": "None",
        "expected_verification": "Passed"
    },
    {
        "test_id": "TC-C-02",
        "name": "C Buffer Overflow via gets()",
        "language": "c",
        "category": "Memory & Pointer Safety",
        "description": "Classic buffer overflow using gets() into a fixed 64-byte stack buffer.",
        "source_code": '''#include <stdio.h>

void read_input() {
    char buffer[64];
    // Dangerous gets() without bounds
    gets(buffer);
}
''',
        "expected_detection": "Classic Buffer Overflow",
        "expected_severity": "Critical",
        "expected_verification": "Passed"
    },
    {
        "test_id": "TC-C-03",
        "name": "C Unbounded strcpy() Buffer Overflow",
        "language": "c",
        "category": "Memory & Pointer Safety",
        "description": "Unbounded string copy into destination array without verifying source length.",
        "source_code": '''#include <string.h>

void copy_user_name(char *src) {
    char dest[32];
    // Dangerous strcpy
    strcpy(dest, src);
}
''',
        "expected_detection": "Classic Buffer Overflow",
        "expected_severity": "Critical",
        "expected_verification": "Passed"
    },
    {
        "test_id": "TC-C-04",
        "name": "C Format String Vulnerability in printf",
        "language": "c",
        "category": "Memory & Pointer Safety",
        "description": "Passing user-controlled string directly into printf() without format specifier.",
        "source_code": '''#include <stdio.h>

void log_message(char *user_msg) {
    // Format string vulnerability
    printf(user_msg);
}
''',
        "expected_detection": "Format String Vulnerability",
        "expected_severity": "High",
        "expected_verification": "Passed"
    },
    {
        "test_id": "TC-C-05",
        "name": "C Use-After-Free Vulnerability",
        "language": "c",
        "category": "Memory & Pointer Safety",
        "description": "Accessing pointer memory after deallocating with free().",
        "source_code": '''#include <stdlib.h>

void process_data() {
    int *ptr = (int *)malloc(sizeof(int) * 10);
    free(ptr);
    // Use-after-free
    *ptr = 42;
}
''',
        "expected_detection": "Use After Free",
        "expected_severity": "Critical",
        "expected_verification": "Passed"
    },
    {
        "test_id": "TC-C-06",
        "name": "C SQL Injection via sprintf()",
        "language": "c",
        "category": "Injection",
        "description": "Dynamic SQL construction using sprintf() formatting untrusted user string into query buffer.",
        "source_code": '''#include <stdio.h>

void query_user(char *user_input) {
    char query[256];
    // SQL injection via sprintf
    sprintf(query, "SELECT * FROM users WHERE id = '%s'", user_input);
    sqlite3_exec(db, query, NULL, NULL, NULL);
}
''',
        "expected_detection": "SQL Injection",
        "expected_severity": "Critical",
        "expected_verification": "Passed"
    },
    {
        "test_id": "TC-C-07",
        "name": "C Command Injection via system()",
        "language": "c",
        "category": "Injection",
        "description": "Passing unvalidated command line directly to system() shell interpreter.",
        "source_code": '''#include <stdlib.h>

void execute_backup(char *backup_dir) {
    char cmd[128];
    sprintf(cmd, "tar -czf backup.tar.gz %s", backup_dir);
    // Dangerous command execution
    system(cmd);
}
''',
        "expected_detection": "Command Injection",
        "expected_severity": "Critical",
        "expected_verification": "Passed"
    },
    {
        "test_id": "TC-C-08",
        "name": "C Hardcoded Master Key",
        "language": "c",
        "category": "Authentication & Cryptography",
        "description": "Hardcoded encryption secret stored directly in C constant buffer.",
        "source_code": '''void init_crypto() {
    char secret_key[] = "MasterKey_Secured999!";
    printf("Key initialized\\n");
}
''',
        "expected_detection": "Hardcoded Credentials",
        "expected_severity": "High",
        "expected_verification": "Passed"
    },
    {
        "test_id": "TC-C-09",
        "name": "C Insecure Temporary File via mktemp()",
        "language": "c",
        "category": "General Security",
        "description": "Creation of temporary file name using unsafe mktemp() API.",
        "source_code": '''#include <unistd.h>

void create_temp() {
    char template_str[] = "/tmp/app_XXXXXX";
    mktemp(template_str);
}
''',
        "expected_detection": "Insecure Temporary File",
        "expected_severity": "Medium",
        "expected_verification": "Passed"
    },
    {
        "test_id": "TC-C-10",
        "name": "C Constant Arithmetic Optimization",
        "language": "c",
        "category": "Optimization",
        "description": "Constant arithmetic calculation eligible for compile-time simplification.",
        "source_code": '''int compute_limits() {
    int total = 100 + 200;
    return total;
}
''',
        "expected_detection": "Clean",
        "expected_severity": "None",
        "expected_verification": "Passed"
    },

    # ------------------- JAVA TEST CASES (10) -------------------
    {
        "test_id": "TC-JAVA-01",
        "name": "Safe Java Repository with PreparedStatement",
        "language": "java",
        "category": "Clean Code",
        "description": "Secure Java data access object utilizing parameterized PreparedStatement and proper resource cleanup.",
        "source_code": '''import java.sql.Connection;
import java.sql.PreparedStatement;
import java.sql.ResultSet;
import java.sql.SQLException;

public class UserRepository {
    public void findUser(Connection conn, String username) throws SQLException {
        String sql = "SELECT id, email FROM users WHERE username = ?";
        try (PreparedStatement pstmt = conn.prepareStatement(sql)) {
            pstmt.setString(1, username);
            ResultSet rs = pstmt.executeQuery();
        }
    }
}
''',
        "expected_detection": "Clean",
        "expected_severity": "None",
        "expected_verification": "Passed"
    },
    {
        "test_id": "TC-JAVA-02",
        "name": "Java SQL Injection via Statement Concatenation",
        "language": "java",
        "category": "Injection",
        "description": "Vulnerable query constructed by concatenating untrusted user input directly in Statement.executeQuery().",
        "source_code": '''import java.sql.Statement;
import java.sql.ResultSet;

public class AuthService {
    public void login(Statement stmt, String username) throws Exception {
        // Vulnerable SQL Injection
        String query = "SELECT * FROM users WHERE username = '" + username + "'";
        ResultSet rs = stmt.executeQuery(query);
    }
}
''',
        "expected_detection": "SQL Injection",
        "expected_severity": "Critical",
        "expected_verification": "Passed"
    },
    {
        "test_id": "TC-JAVA-03",
        "name": "Java Command Injection via Runtime.exec()",
        "language": "java",
        "category": "Injection",
        "description": "Executing system commands directly with untrusted input using Runtime.getRuntime().exec().",
        "source_code": '''public class NetworkTool {
    public void pingHost(String ipAddress) throws Exception {
        // Dangerous Command Injection
        Runtime.getRuntime().exec("ping -c 1 " + ipAddress);
    }
}
''',
        "expected_detection": "Command Injection",
        "expected_severity": "Critical",
        "expected_verification": "Passed"
    },
    {
        "test_id": "TC-JAVA-04",
        "name": "Java Hardcoded Database Password",
        "language": "java",
        "category": "Authentication & Cryptography",
        "description": "Hardcoded database password constant stored in Java source code.",
        "source_code": '''public class DbConfig {
    private static final String password = "ProdDatabasePassword2026!";
    
    public String getPassword() {
        return password;
    }
}
''',
        "expected_detection": "Hardcoded Credentials",
        "expected_severity": "High",
        "expected_verification": "Passed"
    },
    {
        "test_id": "TC-JAVA-05",
        "name": "Java Weak Hash Algorithm (MD5)",
        "language": "java",
        "category": "Authentication & Cryptography",
        "description": "Use of deprecated MD5 message digest algorithm.",
        "source_code": '''import java.security.MessageDigest;

public class HashUtil {
    public byte[] hashData(byte[] input) throws Exception {
        // Insecure MD5 instance
        MessageDigest md = MessageDigest.getInstance("MD5");
        return md.digest(input);
    }
}
''',
        "expected_detection": "Weak Hash",
        "expected_severity": "Medium",
        "expected_verification": "Passed"
    },
    {
        "test_id": "TC-JAVA-06",
        "name": "Java Insecure Deserialization via readObject()",
        "language": "java",
        "category": "Input Validation",
        "description": "Deserializing arbitrary untrusted ObjectInputStream payload without class filters.",
        "source_code": '''import java.io.InputStream;
import java.io.ObjectInputStream;

public class SessionDeserializer {
    public Object deserialize(InputStream stream) throws Exception {
        ObjectInputStream ois = new ObjectInputStream(stream);
        // Vulnerable untrusted deserialization
        return ois.readObject();
    }
}
''',
        "expected_detection": "Deserialization of Untrusted Data",
        "expected_severity": "Critical",
        "expected_verification": "Passed"
    },
    {
        "test_id": "TC-JAVA-07",
        "name": "Java Path Traversal via new File()",
        "language": "java",
        "category": "General Security",
        "description": "Constructing File objects from untrusted user input without canonical path verification.",
        "source_code": '''import java.io.File;

public class FileManager {
    public File getFile(String baseDir, String filename) {
        // Path Traversal
        return new File(baseDir, filename);
    }
}
''',
        "expected_detection": "Path Traversal",
        "expected_severity": "High",
        "expected_verification": "Passed"
    },
    {
        "test_id": "TC-JAVA-08",
        "name": "Java Insecure Random for Security Token",
        "language": "java",
        "category": "Authentication & Cryptography",
        "description": "Using java.util.Random instead of SecureRandom for security sensitive token generation.",
        "source_code": '''import java.util.Random;

public class TokenGenerator {
    public int generateToken() {
        Random rand = new Random();
        // Predictable pseudo-random generator
        return rand.nextInt(1000000);
    }
}
''',
        "expected_detection": "Insufficiently Random Values",
        "expected_severity": "Medium",
        "expected_verification": "Passed"
    },
    {
        "test_id": "TC-JAVA-09",
        "name": "Java Empty Catch Block / Silent Suppression",
        "language": "java",
        "category": "General Security",
        "description": "Empty catch block swallowing critical exceptions without logging or rethrowing.",
        "source_code": '''public class SecurityCheck {
    public void verifyToken(String token) {
        try {
            validate(token);
        } catch (Exception e) {
            // Silently caught exception
        }
    }
    private void validate(String t) {}
}
''',
        "expected_detection": "Empty Catch Block",
        "expected_severity": "Low",
        "expected_verification": "Passed"
    },
    {
        "test_id": "TC-JAVA-10",
        "name": "Java Unreachable Code After Return",
        "language": "java",
        "category": "Optimization",
        "description": "Statement placed after unconditional return statement.",
        "source_code": '''public class MathUtils {
    public int compute(int a, int b) {
        return a + b;
    }
}
''',
        "expected_detection": "Clean",
        "expected_severity": "None",
        "expected_verification": "Passed"
    }
]

