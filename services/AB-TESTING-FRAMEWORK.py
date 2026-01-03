"""A/B Testing Framework for Payment Retry Strategies

Implements statistical testing, MDE calculation, power analysis,
and stratified sampling for payment processing experiments.
"""

import time
import hashlib
import json
import numpy as np
from dataclasses import dataclass
from enum import Enum
from typing import Dict, List, Tuple, Optional
from scipy import stats
from datetime import datetime, timedelta


class RetryStrategy(Enum):
    """Retry interval strategies for A/B testing"""
    CONTROL = "exponential_1s_5s_30s_300s"      # Baseline: 1, 5, 30, 300s
    TEST_A = "exponential_500ms_2s_10s_60s"     # Aggressive: 0.5, 2, 10, 60s  
    TEST_B = "exponential_2s_10s_60s_600s"      # Conservative: 2, 10, 60, 600s


@dataclass
class ABTestConfig:
    """Configuration for A/B test"""
    control_success_rate: float = 0.95
    expected_test_a_lift: float = 0.02  # 2% improvement
    expected_test_b_lift: float = -0.01  # 1% degradation
    significance_level: float = 0.05
    power: float = 0.80
    sample_size: Optional[int] = None
    mde: Optional[float] = None  # Minimum Detectable Effect


class StatisticalCalculator:
    """Calculate statistical metrics for experiment design"""
    
    @staticmethod
    def calculate_mde(p1: float, sample_size: int, alpha: float = 0.05, beta: float = 0.20) -> float:
        """Calculate Minimum Detectable Effect
        
        Args:
            p1: Baseline conversion rate
            sample_size: Samples per arm
            alpha: Significance level
            beta: Type II error rate
            
        Returns:
            Minimum detectable effect size (absolute difference)
        """
        z_alpha = stats.norm.ppf(1 - alpha/2)
        z_beta = stats.norm.ppf(1 - beta)
        
        # For two-proportion test
        pooled_p = p1
        numerator = (z_alpha + z_beta) ** 2 * pooled_p * (1 - pooled_p)
        denominator = sample_size
        
        mde = np.sqrt(2 * numerator / denominator)
        return mde
    
    @staticmethod
    def calculate_sample_size(p1: float, p2: float, alpha: float = 0.05, beta: float = 0.20) -> int:
        """Calculate required sample size per arm
        
        Args:
            p1: Control conversion rate
            p2: Test conversion rate
            alpha: Significance level
            beta: Type II error rate
            
        Returns:
            Required sample size per arm
        """
        z_alpha = stats.norm.ppf(1 - alpha/2)
        z_beta = stats.norm.ppf(1 - beta)
        
        p_bar = (p1 + p2) / 2
        numerator = ((z_alpha + z_beta) ** 2) * (p1 * (1 - p1) + p2 * (1 - p2))
        denominator = (p1 - p2) ** 2
        
        n = numerator / denominator
        return int(np.ceil(n))
    
    @staticmethod
    def calculate_power(n: int, p1: float, p2: float, alpha: float = 0.05) -> float:
        """Calculate statistical power
        
        Args:
            n: Sample size per arm
            p1: Control rate
            p2: Test rate
            alpha: Significance level
            
        Returns:
            Statistical power (0-1)
        """
        z_alpha = stats.norm.ppf(1 - alpha/2)
        p_bar = (p1 + p2) / 2
        
        se = np.sqrt(2 * p_bar * (1 - p_bar) / n)
        z_beta = (abs(p1 - p2) / se) - z_alpha
        
        power = stats.norm.cdf(z_beta)
        return min(power, 1.0)


class StratifiedSampler:
    """Stratified sampling for balanced experiment design"""
    
    def __init__(self, risk_scores: List[float], n_strata: int = 3):
        """Initialize sampler with risk score distribution
        
        Args:
            risk_scores: List of payment risk scores (0-1)
            n_strata: Number of strata to create
        """
        self.risk_scores = risk_scores
        self.n_strata = n_strata
        self.strata_boundaries = self._calculate_strata_boundaries()
        
    def _calculate_strata_boundaries(self) -> List[float]:
        """Calculate quantile boundaries for strata"""
        boundaries = []
        for i in range(1, self.n_strata):
            quantile = i / self.n_strata
            boundary = np.quantile(self.risk_scores, quantile)
            boundaries.append(boundary)
        return boundaries
    
    def stratify_samples(self, samples: List[Dict]) -> Dict[int, List[Dict]]:
        """Assign samples to strata
        
        Args:
            samples: List of payment samples with risk scores
            
        Returns:
            Dict mapping stratum index to samples
        """
        strata = {i: [] for i in range(self.n_strata)}
        
        for sample in samples:
            risk_score = sample.get('risk_score', 0.5)
            stratum_idx = 0
            
            for i, boundary in enumerate(self.strata_boundaries):
                if risk_score >= boundary:
                    stratum_idx = i + 1
            
            strata[stratum_idx].append(sample)
        
        return strata


class ABTestingManager:
    """Manage A/B test execution and analysis"""
    
    def __init__(self, config: ABTestConfig):
        self.config = config
        self.test_results = {}
        self.allocation = {
            RetryStrategy.CONTROL: 0.5,
            RetryStrategy.TEST_A: 0.25,
            RetryStrategy.TEST_B: 0.25
        }
        
        # Calculate sample sizes if not provided
        if config.sample_size is None:
            self._calculate_required_sample_size()
    
    def _calculate_required_sample_size(self):
        """Calculate required sample size for experiment"""
        calculator = StatisticalCalculator()
        
        # For TEST_A
        p2_a = self.config.control_success_rate + self.config.expected_test_a_lift
        n_a = calculator.calculate_sample_size(
            self.config.control_success_rate,
            p2_a,
            self.config.significance_level,
            1 - self.config.power
        )
        
        # For TEST_B
        p2_b = self.config.control_success_rate + self.config.expected_test_b_lift
        n_b = calculator.calculate_sample_size(
            self.config.control_success_rate,
            p2_b,
            self.config.significance_level,
            1 - self.config.power
        )
        
        self.config.sample_size = max(n_a, n_b)
        
        # Calculate MDE
        self.config.mde = calculator.calculate_mde(
            self.config.control_success_rate,
            self.config.sample_size,
            self.config.significance_level,
            1 - self.config.power
        )
    
    def assign_strategy(self, user_id: str) -> RetryStrategy:
        """Assign user to test variant using consistent hashing
        
        Args:
            user_id: Unique user identifier
            
        Returns:
            Assigned retry strategy
        """
        hash_value = int(hashlib.md5(user_id.encode()).hexdigest(), 16)
        random_seed = hash_value % 1000000 / 1000000
        
        cumulative = 0.0
        for strategy, proportion in self.allocation.items():
            cumulative += proportion
            if random_seed <= cumulative:
                return strategy
        
        return RetryStrategy.CONTROL
    
    def analyze_results(self, results: Dict[RetryStrategy, Dict]) -> Dict:
        """Perform statistical analysis of test results
        
        Args:
            results: Dict with test results {strategy: {success_count, total_count}}
            
        Returns:
            Analysis results with p-values and confidence intervals
        """
        analysis = {}
        control_data = results[RetryStrategy.CONTROL]
        control_rate = control_data['success_count'] / control_data['total_count']
        
        for strategy in [RetryStrategy.TEST_A, RetryStrategy.TEST_B]:
            test_data = results[strategy]
            test_rate = test_data['success_count'] / test_data['total_count']
            
            # Chi-square test
            contingency_table = [
                [control_data['success_count'], control_data['total_count'] - control_data['success_count']],
                [test_data['success_count'], test_data['total_count'] - test_data['success_count']]
            ]
            
            chi2, p_value = stats.chi2_contingency(contingency_table)[:2]
            
            # Confidence interval for difference
            se = np.sqrt(control_rate * (1 - control_rate) / control_data['total_count'] +
                        test_rate * (1 - test_rate) / test_data['total_count'])
            
            diff = test_rate - control_rate
            ci_lower = diff - 1.96 * se
            ci_upper = diff + 1.96 * se
            
            analysis[strategy] = {
                'test_rate': test_rate,
                'control_rate': control_rate,
                'difference': diff,
                'p_value': p_value,
                'significant': p_value < self.config.significance_level,
                'ci_lower': ci_lower,
                'ci_upper': ci_upper,
                'lift_pct': (diff / control_rate) * 100
            }
        
        return analysis


if __name__ == '__main__':
    # Example usage
    config = ABTestConfig(
        control_success_rate=0.95,
        expected_test_a_lift=0.02,
        expected_test_b_lift=-0.01
    )
    
    manager = ABTestingManager(config)
    
    print(f"Required sample size: {config.sample_size}")
    print(f"Minimum Detectable Effect: {config.mde:.4f}")
    print(f"\nStrategy Allocation:")
    for strategy, allocation in manager.allocation.items():
        print(f"  {strategy.name}: {allocation*100:.0f}%")
