"""Payment Risk Scorer - ML Model for Transaction Risk Assessment

Implements gradient boosting model to predict payment failure risk
and stratify transactions for A/B test allocation.
"""

import numpy as np
import pandas as pd
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import roc_auc_score, precision_score, recall_score
from typing import Dict, List, Tuple
import joblib
from datetime import datetime, timedelta


class PaymentRiskScorer:
    """ML-based payment risk assessment model"""
    
    def __init__(self, model_version: str = "v1.0"):
        """Initialize scorer with model version"""
        self.model_version = model_version
        self.model = GradientBoostingClassifier(
            n_estimators=100,
            learning_rate=0.1,
            max_depth=5,
            min_samples_split=10,
            min_samples_leaf=5,
            subsample=0.8,
            random_state=42
        )
        self.scaler = StandardScaler()
        self.feature_names = [
            'amount',
            'card_age_days',
            'merchant_category_code',
            'previous_success_rate',
            'time_since_last_transaction_hours',
            'geo_velocity_score',
            'device_risk_score',
            'card_not_present',
            'international_transaction',
            'retry_count'
        ]
        self.feature_importance = {}
        self.is_trained = False
        self.training_date = None
        
    def train(self, X: pd.DataFrame, y: pd.Series, test_size: float = 0.2):
        """Train the risk scoring model
        
        Args:
            X: Feature dataframe
            y: Target labels (0=success, 1=failure)
            test_size: Test set proportion
        """
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=test_size, random_state=42, stratify=y
        )
        
        # Scale features
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_test_scaled = self.scaler.transform(X_test)
        
        # Train model
        self.model.fit(X_train_scaled, y_train)
        self.is_trained = True
        self.training_date = datetime.now()
        
        # Store feature importance
        for feature, importance in zip(self.feature_names, self.model.feature_importances_):
            self.feature_importance[feature] = float(importance)
        
        # Evaluate
        train_auc = roc_auc_score(y_train, self.model.predict_proba(X_train_scaled)[:, 1])
        test_auc = roc_auc_score(y_test, self.model.predict_proba(X_test_scaled)[:, 1])
        
        print(f"Model {self.model_version} Trained:")
        print(f"  Train AUC: {train_auc:.4f}")
        print(f"  Test AUC: {test_auc:.4f}")
        print(f"  Top Features: {sorted(self.feature_importance.items(), key=lambda x: x[1], reverse=True)[:3]}")
        
        return {
            'train_auc': train_auc,
            'test_auc': test_auc,
            'feature_importance': self.feature_importance
        }
    
    def predict_risk(self, transaction: Dict) -> float:
        """Predict risk score for a transaction
        
        Args:
            transaction: Transaction features dict
            
        Returns:
            Risk score (0-1, higher = riskier)
        """
        if not self.is_trained:
            raise ValueError("Model must be trained before prediction")
        
        # Extract features in order
        features = np.array([[transaction.get(feat, 0) for feat in self.feature_names]])
        
        # Scale and predict
        features_scaled = self.scaler.transform(features)
        risk_score = self.model.predict_proba(features_scaled)[0][1]
        
        return float(risk_score)
    
    def stratify_transactions(self, transactions: List[Dict], n_strata: int = 3) -> Dict[str, List[Dict]]:
        """Stratify transactions by risk level
        
        Args:
            transactions: List of transaction dicts
            n_strata: Number of risk strata
            
        Returns:
            Dict mapping risk_level -> [transactions]
        """
        # Calculate risk scores
        risks = []
        for txn in transactions:
            risk = self.predict_risk(txn)
            risks.append((txn, risk))
        
        # Calculate quantile boundaries
        risk_scores = np.array([r[1] for r in risks])
        boundaries = []
        for i in range(1, n_strata):
            quantile = i / n_strata
            boundary = np.quantile(risk_scores, quantile)
            boundaries.append(boundary)
        
        # Assign to strata
        strata_labels = ['low_risk', 'medium_risk', 'high_risk']
        strata = {label: [] for label in strata_labels[:n_strata]}
        
        for txn, risk in risks:
            stratum_idx = 0
            for i, boundary in enumerate(boundaries):
                if risk >= boundary:
                    stratum_idx = i + 1
            
            strata[strata_labels[stratum_idx]].append({
                'transaction': txn,
                'risk_score': risk,
                'stratum': strata_labels[stratum_idx]
            })
        
        return strata
    
    def get_model_metadata(self) -> Dict:
        """Get model metadata for monitoring"""
        return {
            'version': self.model_version,
            'training_date': self.training_date.isoformat() if self.training_date else None,
            'is_trained': self.is_trained,
            'n_estimators': self.model.n_estimators,
            'feature_importance': self.feature_importance,
            'features': self.feature_names
        }
    
    def save_model(self, filepath: str):
        """Save trained model to disk"""
        joblib.dump({
            'model': self.model,
            'scaler': self.scaler,
            'feature_names': self.feature_names,
            'feature_importance': self.feature_importance,
            'model_version': self.model_version,
            'training_date': self.training_date
        }, filepath)
        print(f"Model saved to {filepath}")
    
    def load_model(self, filepath: str):
        """Load trained model from disk"""
        data = joblib.load(filepath)
        self.model = data['model']
        self.scaler = data['scaler']
        self.feature_names = data['feature_names']
        self.feature_importance = data['feature_importance']
        self.model_version = data['model_version']
        self.training_date = data['training_date']
        self.is_trained = True
        print(f"Model {self.model_version} loaded from {filepath}")


class RiskScoreMonitor:
    """Monitor model performance and data drift"""
    
    def __init__(self, scorer: PaymentRiskScorer):
        self.scorer = scorer
        self.score_history = []
        self.baseline_distribution = None
        
    def log_prediction(self, transaction: Dict, risk_score: float, actual_outcome: bool):
        """Log a prediction for monitoring"""
        self.score_history.append({
            'timestamp': datetime.now(),
            'risk_score': risk_score,
            'actual_outcome': actual_outcome,
            'correct': (risk_score > 0.5) == actual_outcome
        })
    
    def calculate_calibration_error(self, window_hours: int = 24) -> float:
        """Calculate model calibration error in recent window
        
        Args:
            window_hours: Time window in hours
            
        Returns:
            Calibration error metric
        """
        cutoff = datetime.now() - timedelta(hours=window_hours)
        recent = [h for h in self.score_history if h['timestamp'] > cutoff]
        
        if not recent:
            return 0.0
        
        accuracy = sum(1 for h in recent if h['correct']) / len(recent)
        return abs(accuracy - 0.5)  # Simplified calibration metric
    
    def detect_data_drift(self, recent_scores: List[float]) -> Dict:
        """Detect changes in score distribution
        
        Args:
            recent_scores: Recent risk scores
            
        Returns:
            Drift metrics and alerts
        """
        if self.baseline_distribution is None:
            self.baseline_distribution = np.array(recent_scores)
            return {'status': 'baseline_set'}
        
        recent_mean = np.mean(recent_scores)
        baseline_mean = np.mean(self.baseline_distribution)
        
        mean_shift = abs(recent_mean - baseline_mean) / baseline_mean
        
        return {
            'mean_shift': mean_shift,
            'alert': mean_shift > 0.1,  # Alert if >10% shift
            'baseline_mean': baseline_mean,
            'recent_mean': recent_mean
        }


if __name__ == '__main__':
    # Example usage
    print("Payment Risk Scorer initialized")
    scorer = PaymentRiskScorer("v1.0")
    print(f"Model metadata: {scorer.get_model_metadata()}")
