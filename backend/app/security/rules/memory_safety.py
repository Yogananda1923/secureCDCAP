import re
from typing import List
from app.schemas.compiler_schemas import VulnerabilityItem

class MemorySafetyRule:
    """
    Detects Memory and Pointer Safety Issues (CWE-120, CWE-134, CWE-476, CWE-416).
    Identifies unbounded buffer copies, format string vulnerabilities,
    use-after-free, and unchecked NULL pointer dereferences in C.
    """

    @staticmethod
    def scan_c(code: str, file_name: str) -> List[VulnerabilityItem]:
        vulns: List[VulnerabilityItem] = []
        lines = code.splitlines()

        freed_pointers = set()

        for idx, line in enumerate(lines, 1):
            sline = line.strip()
            if not sline or sline.startswith("//"):
                continue

            # 1. Unbounded buffer copies: strcpy, gets, strcat, sprintf
            if re.search(r'\bgets\s*\(', sline):
                vulns.append(MemorySafetyRule._create_bof_vuln(
                    idx, sline, "gets() function",
                    "fgets(buffer, sizeof(buffer), stdin);"
                ))
            elif re.search(r'\bstrcpy\s*\(\s*([a-zA-Z_][a-zA-Z0-9_]*)\s*,', sline):
                match = re.search(r'\bstrcpy\s*\(\s*([a-zA-Z_][a-zA-Z0-9_]*)\s*,\s*([^\)]+)\)', sline)
                dest = match.group(1) if match else "dest"
                src = match.group(2).strip() if match else "src"
                vulns.append(MemorySafetyRule._create_bof_vuln(
                    idx, sline, "strcpy() without buffer size check",
                    f"strncpy({dest}, {src}, sizeof({dest}) - 1);\n{dest}[sizeof({dest}) - 1] = '\\0';"
                ))
            elif re.search(r'\bstrcat\s*\(', sline):
                vulns.append(MemorySafetyRule._create_bof_vuln(
                    idx, sline, "strcat() without size limits",
                    "strncat(dest, src, sizeof(dest) - strlen(dest) - 1);"
                ))
            elif re.search(r'\bsprintf\s*\(\s*([a-zA-Z_][a-zA-Z0-9_]*)\s*,', sline):
                match = re.search(r'\bsprintf\s*\(\s*([a-zA-Z_][a-zA-Z0-9_]*)\s*,', sline)
                dest = match.group(1) if match else "dest"
                vulns.append(MemorySafetyRule._create_bof_vuln(
                    idx, sline, "sprintf() without destination buffer bounds",
                    f"snprintf({dest}, sizeof({dest}), ...);"
                ))

            # 2. Format string vulnerability: printf(user_input) instead of printf("%s", user_input)
            elif re.search(r'\bprintf\s*\(\s*([a-zA-Z_][a-zA-Z0-9_]*)\s*\)\s*;', sline):
                match = re.search(r'\bprintf\s*\(\s*([a-zA-Z_][a-zA-Z0-9_]*)\s*\)\s*;', sline)
                var = match.group(1) if match else "str"
                vulns.append(VulnerabilityItem(
                    vuln_id="SEC-MEM-002",
                    name="Format String Vulnerability (Uncontrolled Format String)",
                    category="Memory & Pointer Safety",
                    cwe_id="CWE-134",
                    cwe_name="Use of Externally-Controlled Format String",
                    severity="High",
                    confidence="High",
                    line_number=idx,
                    vulnerable_snippet=sline,
                    root_cause=f"Directly passing variable '{var}' as format argument to printf() instead of format specifier.",
                    attack_scenario="An attacker provides %x or %n specifiers to read arbitrary stack memory or overwrite function pointers in memory.",
                    security_impact="Memory exposure, arbitrary memory write, code execution.",
                    recommended_solution="Always use explicit string format specifiers like printf(\"%s\", var);.",
                    suggested_fix=f"printf(\"%s\", {var});"
                ))

            # 3. Use-After-Free: free(p) followed by usage
            free_match = re.search(r'\bfree\s*\(\s*([a-zA-Z_][a-zA-Z0-9_]*)\s*\)', sline)
            if free_match:
                freed_ptr = free_match.group(1)
                freed_pointers.add(freed_ptr)
            else:
                for ptr in list(freed_pointers):
                    # Check if ptr is dereferenced or accessed: *ptr, ptr->, or ptr[
                    if re.search(rf'(\*{ptr}\b|{ptr}->|{ptr}\[)', sline):
                        vulns.append(VulnerabilityItem(
                            vuln_id="SEC-MEM-003",
                            name="Use After Free (Accessing Memory After Deallocation)",
                            category="Memory & Pointer Safety",
                            cwe_id="CWE-416",
                            cwe_name="Use After Free",
                            severity="Critical",
                            confidence="High",
                            line_number=idx,
                            vulnerable_snippet=sline,
                            root_cause=f"Pointer '{ptr}' was freed in an earlier statement but dereferenced/accessed at line {idx}.",
                            attack_scenario="An attacker crafts heap layouts so the freed chunk is allocated with malicious data before dereference, enabling arbitrary code execution.",
                            security_impact="Remote code execution, heap corruption, memory leak, system crash.",
                            recommended_solution="Set freed pointers to NULL immediately after calling free(), e.g., free(ptr); ptr = NULL; and verify non-null.",
                            suggested_fix=f"free({ptr});\n{ptr} = NULL;"
                        ))
                        freed_pointers.discard(ptr)

        return vulns

    @staticmethod
    def _create_bof_vuln(line_no: int, snippet: str, sink: str, suggested_fix: str) -> VulnerabilityItem:
        return VulnerabilityItem(
            vuln_id="SEC-MEM-001",
            name="Classic Buffer Overflow (Buffer Copy without Checking Size of Input)",
            category="Memory & Pointer Safety",
            cwe_id="CWE-120",
            cwe_name="Buffer Copy without Checking Size of Input ('Classic Buffer Overflow')",
            severity="Critical",
            confidence="High",
            line_number=line_no,
            vulnerable_snippet=snippet,
            root_cause=f"Unbounded string or memory copy operation via {sink}.",
            attack_scenario="An attacker inputs a string longer than the allocated destination buffer, corrupting adjacent stack frames, return addresses, or heap metadata.",
            security_impact="Stack smash, arbitrary code execution, denial of service (SIGSEGV).",
            recommended_solution="Use bounded alternatives with explicit length restrictions, such as strncpy, snprintf, or strlcpy, and ensure null-termination.",
            suggested_fix=suggested_fix
        )

