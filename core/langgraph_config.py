#!/usr/bin/env python3
"""
Configuration management for LangGraph Multi-Agent SKOS Classifier
"""

from dataclasses import dataclass, field
from typing import Dict, Optional
import os
import yaml
from pathlib import Path


@dataclass
class QdrantConfig:
    """Qdrant vector database configuration"""
    url: str = "http://localhost:6333"
    collection_name: str = "concepts"
    
    # HNSW index parameters
    m: int = 32  # Number of edges per node
    ef_construct: int = 128  # Construction time parameter
    ef_search: int = 96  # Search time parameter
    
    # Quantization settings
    use_quantization: bool = False
    quantization_vectors: list = field(default_factory=lambda: ["desc_vec", "path_vec"])
    
    # Storage settings
    on_disk_payload: bool = True
    
    # Vector names
    vector_names: list = field(default_factory=lambda: [
        "lexical_vec",
        "desc_vec", 
        "path_vec",
        "comp_vec"
    ])


@dataclass
class EmbeddingConfig:
    """Embedding model configuration"""
    model_name: str = "sentence-transformers/all-MiniLM-L6-v2"
    embedding_dim: int = 768
    device: str = "cpu"  # "cuda" for GPU
    batch_size: int = 32
    
    # Cache settings
    use_cache: bool = True
    cache_size: int = 10000  # LRU cache size
    cache_ttl: int = 3600  # Cache TTL in seconds


@dataclass
class RetrievalConfig:
    """Retrieval and ranking configuration"""
    retrieval_limit: int = 50
    top_k_output: int = 5
    top_m_rerank: int = 20
    
    # Fusion weights
    weight_comp: float = 1.0
    weight_lex: float = 0.3
    weight_path: float = 0.2
    weight_graph: float = 0.02


@dataclass
class ThresholdConfig:
    """Decision thresholds and calibration"""
    tau_low: float = 0.55  # Minimum confidence to accept
    epsilon_tie: float = 0.03  # Score difference threshold for tie detection
    
    # Abstain conditions
    abstain_on_low_confidence: bool = True
    abstain_on_language_mismatch: bool = False
    
    # Tie-breaking
    prefer_broader_on_tie: bool = True


@dataclass
class FeatureFlags:
    """Feature flags for optional components"""
    cross_encoder_enabled: bool = False
    lexical_boost_enabled: bool = True
    graph_reasoning_enabled: bool = True
    calibration_enabled: bool = False
    
    # A/B testing
    experiment_id: Optional[str] = None


@dataclass
class ObservabilityConfig:
    """Observability and monitoring configuration"""
    enable_metrics: bool = True
    enable_tracing: bool = True
    
    # Logging
    log_level: str = "INFO"
    log_format: str = "json"
    
    # Metrics backend
    metrics_backend: Optional[str] = None  # "prometheus", "datadog", etc.
    
    # Trace sampling
    trace_sample_rate: float = 1.0


@dataclass
class PerformanceConfig:
    """Performance and resource limits"""
    max_concurrent_requests: int = 100
    request_timeout_ms: int = 30000
    
    # Per-node timeouts
    node_timeout_ms: Dict[str, int] = field(default_factory=lambda: {
        "n0_ingest": 1000,
        "n1_queryvecs": 2000,
        "n2_retrieval": 3000,
        "n3_lexboost": 2000,
        "n4_merge": 1000,
        "n5_graph": 2000,
        "n6_rerank": 5000,  # Cross-encoder can be slow
        "n7_decide": 1000,
        "n8_validate": 500,
        "n9_persist": 1000,
    })


@dataclass
class TaxonomyConfig:
    """Taxonomy-specific configuration"""
    default_scheme_uri: str = "https://treew.io/taxonomy/"
    supported_languages: list = field(default_factory=lambda: ["es", "en", "pt", "fr"])
    default_language: str = "es"
    
    # Versioning
    enable_versioning: bool = True
    version_field: str = "scheme_version"


@dataclass
class LangGraphClassifierConfig:
    """Complete configuration for LangGraph Multi-Agent Classifier"""
    qdrant: QdrantConfig = field(default_factory=QdrantConfig)
    embedding: EmbeddingConfig = field(default_factory=EmbeddingConfig)
    retrieval: RetrievalConfig = field(default_factory=RetrievalConfig)
    thresholds: ThresholdConfig = field(default_factory=ThresholdConfig)
    features: FeatureFlags = field(default_factory=FeatureFlags)
    observability: ObservabilityConfig = field(default_factory=ObservabilityConfig)
    performance: PerformanceConfig = field(default_factory=PerformanceConfig)
    taxonomy: TaxonomyConfig = field(default_factory=TaxonomyConfig)
    
    @classmethod
    def from_yaml(cls, path: str) -> 'LangGraphClassifierConfig':
        """Load configuration from YAML file"""
        with open(path, 'r') as f:
            data = yaml.safe_load(f)
        
        return cls(
            qdrant=QdrantConfig(**data.get('qdrant', {})),
            embedding=EmbeddingConfig(**data.get('embedding', {})),
            retrieval=RetrievalConfig(**data.get('retrieval', {})),
            thresholds=ThresholdConfig(**data.get('thresholds', {})),
            features=FeatureFlags(**data.get('features', {})),
            observability=ObservabilityConfig(**data.get('observability', {})),
            performance=PerformanceConfig(**data.get('performance', {})),
            taxonomy=TaxonomyConfig(**data.get('taxonomy', {})),
        )
    
    @classmethod
    def from_env(cls) -> 'LangGraphClassifierConfig':
        """Load configuration from environment variables"""
        return cls(
            qdrant=QdrantConfig(
                url=os.getenv('QDRANT_URL', 'http://localhost:6333'),
                collection_name=os.getenv('QDRANT_COLLECTION', 'concepts'),
            ),
            embedding=EmbeddingConfig(
                model_name=os.getenv('EMBEDDING_MODEL', 'sentence-transformers/all-MiniLM-L6-v2'),
                device=os.getenv('EMBEDDING_DEVICE', 'cpu'),
            ),
            features=FeatureFlags(
                cross_encoder_enabled=os.getenv('CROSS_ENCODER_ENABLED', 'false').lower() == 'true',
            ),
            observability=ObservabilityConfig(
                log_level=os.getenv('LOG_LEVEL', 'INFO'),
                metrics_backend=os.getenv('METRICS_BACKEND'),
            ),
        )
    
    def to_yaml(self, path: str) -> None:
        """Save configuration to YAML file"""
        data = {
            'qdrant': self.qdrant.__dict__,
            'embedding': self.embedding.__dict__,
            'retrieval': self.retrieval.__dict__,
            'thresholds': self.thresholds.__dict__,
            'features': self.features.__dict__,
            'observability': self.observability.__dict__,
            'performance': self.performance.__dict__,
            'taxonomy': self.taxonomy.__dict__,
        }
        
        with open(path, 'w') as f:
            yaml.dump(data, f, default_flow_style=False)


def load_config(
    config_path: Optional[str] = None,
    use_env: bool = True
) -> LangGraphClassifierConfig:
    """
    Load configuration from file or environment
    
    Args:
        config_path: Path to YAML config file (optional)
        use_env: Whether to load from environment variables as fallback
    
    Returns:
        LangGraphClassifierConfig instance
    """
    if config_path and Path(config_path).exists():
        return LangGraphClassifierConfig.from_yaml(config_path)
    elif use_env:
        return LangGraphClassifierConfig.from_env()
    else:
        return LangGraphClassifierConfig()


# Example configuration template
DEFAULT_CONFIG_TEMPLATE = """
# LangGraph Multi-Agent SKOS Classifier Configuration

qdrant:
  url: "http://localhost:6333"
  collection_name: "concepts"
  m: 32
  ef_construct: 128
  ef_search: 96
  use_quantization: false
  on_disk_payload: true

embedding:
  model_name: "sentence-transformers/all-MiniLM-L6-v2"
  embedding_dim: 768
  device: "cpu"
  batch_size: 32
  use_cache: true
  cache_size: 10000

retrieval:
  retrieval_limit: 50
  top_k_output: 5
  top_m_rerank: 20
  weight_comp: 1.0
  weight_lex: 0.3
  weight_path: 0.2
  weight_graph: 0.02

thresholds:
  tau_low: 0.55
  epsilon_tie: 0.03
  abstain_on_low_confidence: true
  prefer_broader_on_tie: true

features:
  cross_encoder_enabled: false
  lexical_boost_enabled: true
  graph_reasoning_enabled: true
  calibration_enabled: false

observability:
  enable_metrics: true
  enable_tracing: true
  log_level: "INFO"
  log_format: "json"
  trace_sample_rate: 1.0

performance:
  max_concurrent_requests: 100
  request_timeout_ms: 30000

taxonomy:
  default_scheme_uri: "https://treew.io/taxonomy/"
  supported_languages: ["es", "en", "pt", "fr"]
  default_language: "es"
  enable_versioning: true
"""
