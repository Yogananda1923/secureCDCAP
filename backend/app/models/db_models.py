from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Float, Boolean, JSON
from sqlalchemy.orm import relationship
from app.database import Base

class Project(Base):
    __tablename__ = "projects"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, default="Default Project")
    description = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    source_files = relationship("SourceFile", back_populates="project", cascade="all, delete-orphan")
    history_records = relationship("AnalysisHistory", back_populates="project", cascade="all, delete-orphan")


class SourceFile(Base):
    __tablename__ = "source_files"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=True)
    file_name = Column(String(255), nullable=False)
    language = Column(String(50), nullable=False)  # python, c, java
    content = Column(Text, nullable=False)
    file_size = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)

    project = relationship("Project", back_populates="source_files")
    analyses = relationship("AnalysisHistory", back_populates="source_file", cascade="all, delete-orphan")


class AnalysisHistory(Base):
    __tablename__ = "analysis_history"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=True)
    source_file_id = Column(Integer, ForeignKey("source_files.id"), nullable=True)
    file_name = Column(String(255), nullable=False)
    language = Column(String(50), nullable=False)
    source_code = Column(Text, nullable=False)
    
    # Metrics
    total_lines = Column(Integer, default=0)
    total_tokens = Column(Integer, default=0)
    ast_nodes_count = Column(Integer, default=0)
    functions_count = Column(Integer, default=0)
    variables_count = Column(Integer, default=0)
    syntax_valid = Column(Boolean, default=True)
    security_score = Column(Float, default=100.0)
    parsing_time_ms = Column(Float, default=0.0)
    status = Column(String(50), default="Completed")
    
    # Full analysis dumps as JSON for frontend viewing
    tokens_data = Column(JSON, nullable=True)
    ast_data = Column(JSON, nullable=True)
    semantic_data = Column(JSON, nullable=True)
    ir_data = Column(JSON, nullable=True)
    cfg_data = Column(JSON, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)

    project = relationship("Project", back_populates="history_records")
    source_file = relationship("SourceFile", back_populates="analyses")
    vulnerabilities = relationship("Vulnerability", back_populates="analysis", cascade="all, delete-orphan")
    transformations = relationship("Transformation", back_populates="analysis", cascade="all, delete-orphan")
    reports = relationship("Report", back_populates="analysis", cascade="all, delete-orphan")


class Vulnerability(Base):
    __tablename__ = "vulnerabilities"

    id = Column(Integer, primary_key=True, index=True)
    analysis_id = Column(Integer, ForeignKey("analysis_history.id"), nullable=False)
    vuln_id = Column(String(100), nullable=False)  # e.g., SEC-SQLI-001
    name = Column(String(255), nullable=False)
    category = Column(String(100), nullable=False)  # Injection, Memory, Crypto, etc.
    cwe_id = Column(String(50), nullable=True)  # e.g., CWE-89
    cwe_name = Column(String(255), nullable=True)
    severity = Column(String(50), nullable=False)  # Critical, High, Medium, Low, Informational
    confidence = Column(String(50), default="High")  # High, Medium, Low
    line_number = Column(Integer, nullable=False, default=1)
    end_line_number = Column(Integer, nullable=True)
    vulnerable_snippet = Column(Text, nullable=False)
    root_cause = Column(Text, nullable=True)
    attack_scenario = Column(Text, nullable=True)
    security_impact = Column(Text, nullable=True)
    recommended_solution = Column(Text, nullable=True)
    suggested_fix = Column(Text, nullable=True)
    is_transformed = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    analysis = relationship("AnalysisHistory", back_populates="vulnerabilities")


class Transformation(Base):
    __tablename__ = "transformations"

    id = Column(Integer, primary_key=True, index=True)
    analysis_id = Column(Integer, ForeignKey("analysis_history.id"), nullable=False)
    transformation_type = Column(String(100), nullable=False)  # SecurityFix, ConstantFolding, DCE, etc.
    description = Column(Text, nullable=False)
    original_code = Column(Text, nullable=False)
    transformed_code = Column(Text, nullable=False)
    diff_data = Column(JSON, nullable=True)
    is_verified = Column(Boolean, default=False)
    verification_status = Column(String(50), default="Pending")
    explanation = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    analysis = relationship("AnalysisHistory", back_populates="transformations")
    verification_results = relationship("VerificationResult", back_populates="transformation", cascade="all, delete-orphan")


class VerificationResult(Base):
    __tablename__ = "verification_results"

    id = Column(Integer, primary_key=True, index=True)
    transformation_id = Column(Integer, ForeignKey("transformations.id"), nullable=False)
    syntax_valid = Column(Boolean, default=False)
    semantic_valid = Column(Boolean, default=False)
    regression_passed = Column(Boolean, default=False)
    overall_status = Column(String(50), default="Passed")  # Passed, Failed, Rejected
    details = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    transformation = relationship("Transformation", back_populates="verification_results")


class TestCase(Base):
    __tablename__ = "test_cases"

    id = Column(Integer, primary_key=True, index=True)
    test_id = Column(String(100), unique=True, nullable=False)
    name = Column(String(255), nullable=False)
    language = Column(String(50), nullable=False)
    category = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    source_code = Column(Text, nullable=False)
    expected_detection = Column(String(100), nullable=True)  # Vulnerability name or 'Clean'
    expected_severity = Column(String(50), nullable=True)
    expected_transformation = Column(Text, nullable=True)
    expected_verification = Column(String(50), default="Passed")
    is_predefined = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    executions = relationship("TestExecution", back_populates="test_case", cascade="all, delete-orphan")


class TestExecution(Base):
    __tablename__ = "test_executions"

    id = Column(Integer, primary_key=True, index=True)
    test_case_id = Column(Integer, ForeignKey("test_cases.id"), nullable=False)
    status = Column(String(50), nullable=False)  # Passed, Failed, Skipped
    actual_detection = Column(String(100), nullable=True)
    actual_severity = Column(String(50), nullable=True)
    actual_verification = Column(String(50), nullable=True)
    execution_time_ms = Column(Float, default=0.0)
    details = Column(JSON, nullable=True)
    executed_at = Column(DateTime, default=datetime.utcnow)

    test_case = relationship("TestCase", back_populates="executions")


class Report(Base):
    __tablename__ = "reports"

    id = Column(Integer, primary_key=True, index=True)
    analysis_id = Column(Integer, ForeignKey("analysis_history.id"), nullable=False)
    report_type = Column(String(50), default="JSON")  # PDF, JSON, HTML
    file_path = Column(String(500), nullable=True)
    summary_data = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    analysis = relationship("AnalysisHistory", back_populates="reports")

