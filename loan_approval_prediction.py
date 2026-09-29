"""
Machine Learning-Based Loan Approval Prediction System
Predicts loan approval decisions using applicant financial and personal information
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime, timedelta
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
from sklearn.metrics import confusion_matrix, classification_report, roc_auc_score, roc_curve
import warnings
warnings.filterwarnings('ignore')

# Set style for visualizations
sns.set_style("whitegrid")
plt.rcParams['figure.figsize'] = (14, 8)
plt.rcParams['font.size'] = 10

# ============================================================================
# 1. GENERATE SYNTHETIC LOAN APPLICATION DATASET
# ============================================================================

def generate_loan_applications(n_applications=1000, random_state=42):
    """Generate synthetic loan application dataset"""
    np.random.seed(random_state)
    
    data = {
        'Application_ID': np.arange(1, n_applications + 1),
        'Age': np.random.randint(22, 65, n_applications),
        'Income': np.random.randint(200000, 5000000, n_applications),
        'Loan_Amount': np.random.randint(100000, 2000000, n_applications),
        'Loan_Term': np.random.choice([12, 24, 36, 48, 60], n_applications),
        'Employment_Years': np.random.randint(0, 30, n_applications),
        'Credit_Score': np.random.randint(300, 850, n_applications),
        'Existing_Debt': np.random.randint(0, 1000000, n_applications),
        'Education': np.random.choice(['High School', 'Bachelor', 'Master', 'PhD'], n_applications),
        'Marital_Status': np.random.choice(['Single', 'Married', 'Divorced'], n_applications),
        'Employment_Type': np.random.choice(['Salaried', 'Self-Employed', 'Unemployed'], n_applications),
        'Property_Area': np.random.choice(['Urban', 'Rural', 'Semi-Urban'], n_applications)
    }
    
    df = pd.DataFrame(data)
    
    # Calculate loan approval based on financial metrics
    df['Debt_to_Income_Ratio'] = (df['Existing_Debt'] + df['Loan_Amount']) / df['Income']
    df['Monthly_Income'] = df['Income'] / 12
    df['Monthly_Loan_Payment'] = df['Loan_Amount'] / (df['Loan_Term'])
    df['Payment_to_Income_Ratio'] = df['Monthly_Loan_Payment'] / df['Monthly_Income']
    
    # Approval logic
    approval_probability = []
    for idx, row in df.iterrows():
        score = 0
        
        # Credit score (0-30 points)
        if row['Credit_Score'] >= 750:
            score += 30
        elif row['Credit_Score'] >= 700:
            score += 25
        elif row['Credit_Score'] >= 650:
            score += 20
        elif row['Credit_Score'] >= 600:
            score += 15
        else:
            score += 5
            
        # Employment years (0-20 points)
        if row['Employment_Years'] >= 10:
            score += 20
        elif row['Employment_Years'] >= 5:
            score += 15
        elif row['Employment_Years'] >= 2:
            score += 10
        else:
            score += 5
            
        # Debt to income ratio (0-25 points)
        if row['Debt_to_Income_Ratio'] <= 0.3:
            score += 25
        elif row['Debt_to_Income_Ratio'] <= 0.5:
            score += 20
        elif row['Debt_to_Income_Ratio'] <= 0.7:
            score += 15
        else:
            score += 5
            
        # Income level (0-15 points)
        if row['Income'] >= 2000000:
            score += 15
        elif row['Income'] >= 1000000:
            score += 12
        elif row['Income'] >= 500000:
            score += 10
        else:
            score += 5
            
        # Age (0-10 points)
        if 25 <= row['Age'] <= 55:
            score += 10
        elif 22 <= row['Age'] < 25 or 55 < row['Age'] <= 65:
            score += 5
        else:
            score += 0
            
        approval_probability.append(score)
    
    df['Approval_Score'] = approval_probability
    df['Loan_Approved'] = (df['Approval_Score'] >= 60).astype(int)
    
    print("=" * 90)
    print("LOAN APPROVAL PREDICTION SYSTEM - DATASET OVERVIEW")
    print("=" * 90)
    print(f"\nTotal Applications: {len(df)}")
    print(f"\nApproval Distribution:")
    print(f"  Approved: {(df['Loan_Approved'] == 1).sum()} ({(df['Loan_Approved'] == 1).sum()/len(df)*100:.1f}%)")
    print(f"  Rejected: {(df['Loan_Approved'] == 0).sum()} ({(df['Loan_Approved'] == 0).sum()/len(df)*100:.1f}%)")
    print(f"\nFinancial Metrics:")
    print(f"  Average Income: ₹{df['Income'].mean():,.0f}")
    print(f"  Average Loan Amount: ₹{df['Loan_Amount'].mean():,.0f}")
    print(f"  Average Credit Score: {df['Credit_Score'].mean():.0f}")
    print(f"  Average Approval Score: {df['Approval_Score'].mean():.2f}")
    
    return df

# ============================================================================
# 2. DATA PREPROCESSING AND FEATURE ENGINEERING
# ============================================================================

def preprocess_and_engineer_features(df):
    """Preprocess data and engineer features"""
    print("\n" + "=" * 90)
    print("DATA PREPROCESSING AND FEATURE ENGINEERING")
    print("=" * 90)
    
    df_processed = df.copy()
    
    # Encode categorical variables
    print("\nEncoding categorical variables...")
    le_dict = {}
    categorical_cols = ['Education', 'Marital_Status', 'Employment_Type', 'Property_Area']
    
    for col in categorical_cols:
        le = LabelEncoder()
        df_processed[col + '_Encoded'] = le.fit_transform(df_processed[col])
        le_dict[col] = le
    
    # Select features for modeling
    feature_cols = [
        'Age', 'Income', 'Loan_Amount', 'Loan_Term', 'Employment_Years',
        'Credit_Score', 'Existing_Debt', 'Debt_to_Income_Ratio',
        'Payment_to_Income_Ratio', 'Education_Encoded', 'Marital_Status_Encoded',
        'Employment_Type_Encoded', 'Property_Area_Encoded'
    ]
    
    X = df_processed[feature_cols]
    y = df_processed['Loan_Approved']
    
    print(f"Features selected: {len(feature_cols)}")
    print(f"Feature list: {', '.join(feature_cols)}")
    
    # Split data
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    
    # Scale features
    print("\nScaling features...")
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)
    
    print(f"Training set size: {len(X_train)} applications")
    print(f"Test set size: {len(X_test)} applications")
    print(f"Feature scaling: StandardScaler (mean=0, std=1)")
    
    return X_train_scaled, X_test_scaled, y_train, y_test, scaler, feature_cols, df_processed

# ============================================================================
# 3. VISUALIZATION FUNCTIONS
# ============================================================================

def visualize_approval_distribution(df):
    """Visualize loan approval distribution"""
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    
    # Approval distribution
    approval_counts = df['Loan_Approved'].value_counts()
    colors = ['#D62828', '#2E86AB']
    axes[0, 0].bar(['Rejected', 'Approved'], [approval_counts[0], approval_counts[1]], 
                   color=colors, edgecolor='black', alpha=0.8)
    axes[0, 0].set_title('Loan Approval Distribution', fontweight='bold', fontsize=12)
    axes[0, 0].set_ylabel('Number of Applications')
    axes[0, 0].grid(axis='y', alpha=0.3)
    
    # Approval by income level
    income_bins = [0, 500000, 1000000, 2000000, 5000000]
    df['Income_Level'] = pd.cut(df['Income'], bins=income_bins, 
                                 labels=['<500K', '500K-1M', '1M-2M', '>2M'])
    income_approval = df.groupby('Income_Level')['Loan_Approved'].mean() * 100
    axes[0, 1].bar(income_approval.index, income_approval.values, 
                   color='#2E86AB', edgecolor='black', alpha=0.8)
    axes[0, 1].set_title('Approval Rate by Income Level', fontweight='bold', fontsize=12)
    axes[0, 1].set_ylabel('Approval Rate (%)')
    axes[0, 1].grid(axis='y', alpha=0.3)
    
    # Credit score distribution
    axes[1, 0].hist(df['Credit_Score'], bins=30, color='#A23B72', alpha=0.7, edgecolor='black')
    axes[1, 0].axvline(df['Credit_Score'].mean(), color='red', linestyle='--', linewidth=2)
    axes[1, 0].set_title('Distribution of Credit Scores', fontweight='bold')
    axes[1, 0].set_xlabel('Credit Score')
    axes[1, 0].set_ylabel('Frequency')
    axes[1, 0].grid(alpha=0.3)
    
    # Approval by credit score
    credit_bins = [0, 600, 650, 700, 750, 850]
    df['Credit_Category'] = pd.cut(df['Credit_Score'], bins=credit_bins,
                                    labels=['Poor', 'Fair', 'Good', 'Very Good', 'Excellent'])
    credit_approval = df.groupby('Credit_Category')['Loan_Approved'].mean() * 100
    axes[1, 1].bar(credit_approval.index, credit_approval.values,
                   color='#F18F01', edgecolor='black', alpha=0.8)
    axes[1, 1].set_title('Approval Rate by Credit Score', fontweight='bold', fontsize=12)
    axes[1, 1].set_ylabel('Approval Rate (%)')
    axes[1, 1].grid(axis='y', alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('/home/ubuntu/approval_distribution.png', dpi=300, bbox_inches='tight')
    print("✓ Approval distribution visualization saved")
    plt.close()

def visualize_financial_metrics(df):
    """Visualize financial metrics by approval status"""
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    
    # Income by approval status
    approved_income = df[df['Loan_Approved'] == 1]['Income']
    rejected_income = df[df['Loan_Approved'] == 0]['Income']
    axes[0, 0].boxplot([rejected_income, approved_income], 
                       labels=['Rejected', 'Approved'])
    axes[0, 0].set_title('Income Distribution by Approval Status', fontweight='bold')
    axes[0, 0].set_ylabel('Income (₹)')
    axes[0, 0].grid(alpha=0.3)
    
    # Debt to income ratio
    approved_dti = df[df['Loan_Approved'] == 1]['Debt_to_Income_Ratio']
    rejected_dti = df[df['Loan_Approved'] == 0]['Debt_to_Income_Ratio']
    axes[0, 1].boxplot([rejected_dti, approved_dti],
                       labels=['Rejected', 'Approved'])
    axes[0, 1].set_title('Debt-to-Income Ratio by Approval', fontweight='bold')
    axes[0, 1].set_ylabel('DTI Ratio')
    axes[0, 1].grid(alpha=0.3)
    
    # Employment years
    approved_emp = df[df['Loan_Approved'] == 1]['Employment_Years']
    rejected_emp = df[df['Loan_Approved'] == 0]['Employment_Years']
    axes[1, 0].boxplot([rejected_emp, approved_emp],
                       labels=['Rejected', 'Approved'])
    axes[1, 0].set_title('Employment Years by Approval', fontweight='bold')
    axes[1, 0].set_ylabel('Years')
    axes[1, 0].grid(alpha=0.3)
    
    # Loan amount
    approved_loan = df[df['Loan_Approved'] == 1]['Loan_Amount']
    rejected_loan = df[df['Loan_Approved'] == 0]['Loan_Amount']
    axes[1, 1].boxplot([rejected_loan, approved_loan],
                       labels=['Rejected', 'Approved'])
    axes[1, 1].set_title('Loan Amount by Approval', fontweight='bold')
    axes[1, 1].set_ylabel('Loan Amount (₹)')
    axes[1, 1].grid(alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('/home/ubuntu/financial_metrics.png', dpi=300, bbox_inches='tight')
    print("✓ Financial metrics visualization saved")
    plt.close()

def visualize_model_comparison(results):
    """Visualize model performance comparison"""
    models = list(results.keys())
    accuracy = [results[m]['Accuracy'] for m in models]
    precision = [results[m]['Precision'] for m in models]
    recall = [results[m]['Recall'] for m in models]
    f1 = [results[m]['F1'] for m in models]
    
    x = np.arange(len(models))
    width = 0.2
    
    fig, ax = plt.subplots(figsize=(12, 6))
    
    ax.bar(x - 1.5*width, accuracy, width, label='Accuracy', alpha=0.8, edgecolor='black')
    ax.bar(x - 0.5*width, precision, width, label='Precision', alpha=0.8, edgecolor='black')
    ax.bar(x + 0.5*width, recall, width, label='Recall', alpha=0.8, edgecolor='black')
    ax.bar(x + 1.5*width, f1, width, label='F1-Score', alpha=0.8, edgecolor='black')
    
    ax.set_title('Model Performance Comparison', fontweight='bold', fontsize=12)
    ax.set_ylabel('Score')
    ax.set_xticks(x)
    ax.set_xticklabels(models)
    ax.legend()
    ax.set_ylim([0, 1])
    ax.grid(axis='y', alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('/home/ubuntu/model_comparison.png', dpi=300, bbox_inches='tight')
    print("✓ Model comparison visualization saved")
    plt.close()

def visualize_confusion_matrices(y_test, y_pred_lr, y_pred_rf, y_pred_gb):
    """Visualize confusion matrices"""
    fig, axes = plt.subplots(1, 3, figsize=(15, 4))
    
    models_data = [
        ('Logistic Regression', y_pred_lr),
        ('Random Forest', y_pred_rf),
        ('Gradient Boosting', y_pred_gb)
    ]
    
    for idx, (name, y_pred) in enumerate(models_data):
        cm = confusion_matrix(y_test, y_pred)
        sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', ax=axes[idx],
                   xticklabels=['Rejected', 'Approved'],
                   yticklabels=['Rejected', 'Approved'])
        axes[idx].set_title(f'Confusion Matrix - {name}', fontweight='bold')
        axes[idx].set_ylabel('True Label')
        axes[idx].set_xlabel('Predicted Label')
    
    plt.tight_layout()
    plt.savefig('/home/ubuntu/confusion_matrices.png', dpi=300, bbox_inches='tight')
    print("✓ Confusion matrices visualization saved")
    plt.close()

def visualize_roc_curves(y_test, y_pred_proba_lr, y_pred_proba_rf, y_pred_proba_gb):
    """Visualize ROC curves"""
    fig, ax = plt.subplots(figsize=(12, 8))
    
    models_data = [
        ('Logistic Regression', y_pred_proba_lr),
        ('Random Forest', y_pred_proba_rf),
        ('Gradient Boosting', y_pred_proba_gb)
    ]
    
    for name, y_proba in models_data:
        fpr, tpr, _ = roc_curve(y_test, y_proba)
        auc = roc_auc_score(y_test, y_proba)
        ax.plot(fpr, tpr, linewidth=2, label=f'{name} (AUC = {auc:.4f})')
    
    ax.plot([0, 1], [0, 1], 'k--', linewidth=1, label='Random Classifier')
    ax.set_title('ROC Curves - Model Comparison', fontweight='bold', fontsize=12)
    ax.set_xlabel('False Positive Rate')
    ax.set_ylabel('True Positive Rate')
    ax.legend()
    ax.grid(alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('/home/ubuntu/roc_curves.png', dpi=300, bbox_inches='tight')
    print("✓ ROC curves visualization saved")
    plt.close()

def visualize_feature_importance(feature_cols, rf_model):
    """Visualize feature importance from Random Forest"""
    importances = rf_model.feature_importances_
    indices = np.argsort(importances)[::-1][:10]
    
    fig, ax = plt.subplots(figsize=(12, 6))
    
    ax.bar(range(len(indices)), importances[indices], 
           color='#2E86AB', edgecolor='black', alpha=0.8)
    ax.set_xticks(range(len(indices)))
    ax.set_xticklabels([feature_cols[i] for i in indices], rotation=45, ha='right')
    ax.set_title('Top 10 Feature Importance (Random Forest)', fontweight='bold', fontsize=12)
    ax.set_ylabel('Importance Score')
    ax.grid(axis='y', alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('/home/ubuntu/feature_importance.png', dpi=300, bbox_inches='tight')
    print("✓ Feature importance visualization saved")
    plt.close()

# ============================================================================
# 4. MODEL BUILDING AND TRAINING
# ============================================================================

def train_models(X_train, X_test, y_train, y_test):
    """Train multiple classification models"""
    print("\n" + "=" * 90)
    print("MODEL TRAINING")
    print("=" * 90)
    
    results = {}
    models = {}
    predictions = {}
    probabilities = {}
    
    # Logistic Regression
    print("\nTraining Logistic Regression...")
    lr_model = LogisticRegression(max_iter=1000, random_state=42)
    lr_model.fit(X_train, y_train)
    y_pred_lr = lr_model.predict(X_test)
    y_proba_lr = lr_model.predict_proba(X_test)[:, 1]
    
    results['Logistic Regression'] = {
        'Accuracy': accuracy_score(y_test, y_pred_lr),
        'Precision': precision_score(y_test, y_pred_lr),
        'Recall': recall_score(y_test, y_pred_lr),
        'F1': f1_score(y_test, y_pred_lr),
        'ROC-AUC': roc_auc_score(y_test, y_proba_lr)
    }
    models['Logistic Regression'] = lr_model
    predictions['Logistic Regression'] = y_pred_lr
    probabilities['Logistic Regression'] = y_proba_lr
    
    # Random Forest
    print("Training Random Forest Classifier...")
    rf_model = RandomForestClassifier(n_estimators=100, random_state=42, n_jobs=-1)
    rf_model.fit(X_train, y_train)
    y_pred_rf = rf_model.predict(X_test)
    y_proba_rf = rf_model.predict_proba(X_test)[:, 1]
    
    results['Random Forest'] = {
        'Accuracy': accuracy_score(y_test, y_pred_rf),
        'Precision': precision_score(y_test, y_pred_rf),
        'Recall': recall_score(y_test, y_pred_rf),
        'F1': f1_score(y_test, y_pred_rf),
        'ROC-AUC': roc_auc_score(y_test, y_proba_rf)
    }
    models['Random Forest'] = rf_model
    predictions['Random Forest'] = y_pred_rf
    probabilities['Random Forest'] = y_proba_rf
    
    # Gradient Boosting
    print("Training Gradient Boosting Classifier...")
    gb_model = GradientBoostingClassifier(n_estimators=100, random_state=42)
    gb_model.fit(X_train, y_train)
    y_pred_gb = gb_model.predict(X_test)
    y_proba_gb = gb_model.predict_proba(X_test)[:, 1]
    
    results['Gradient Boosting'] = {
        'Accuracy': accuracy_score(y_test, y_pred_gb),
        'Precision': precision_score(y_test, y_pred_gb),
        'Recall': recall_score(y_test, y_pred_gb),
        'F1': f1_score(y_test, y_pred_gb),
        'ROC-AUC': roc_auc_score(y_test, y_proba_gb)
    }
    models['Gradient Boosting'] = gb_model
    predictions['Gradient Boosting'] = y_pred_gb
    probabilities['Gradient Boosting'] = y_proba_gb
    
    return results, models, predictions, probabilities, y_pred_lr, y_pred_rf, y_pred_gb, y_proba_lr, y_proba_rf, y_proba_gb

# ============================================================================
# 5. MAIN EXECUTION
# ============================================================================

def main():
    """Main execution function"""
    print("\n" + "=" * 90)
    print("MACHINE LEARNING-BASED LOAN APPROVAL PREDICTION SYSTEM")
    print("Using Applicant Financial and Personal Information")
    print("=" * 90)
    
    # Generate dataset
    print("\n[Step 1] Generating Loan Application Dataset...")
    df = generate_loan_applications(n_applications=1000)
    
    # Preprocess and engineer features
    print("\n[Step 2] Preprocessing and Engineering Features...")
    X_train, X_test, y_train, y_test, scaler, feature_cols, df_processed = preprocess_and_engineer_features(df)
    
    # Generate visualizations
    print("\n[Step 3] Generating Visualizations...")
    print("Creating approval distribution visualization...")
    visualize_approval_distribution(df)
    
    print("Creating financial metrics visualization...")
    visualize_financial_metrics(df)
    
    # Train models
    print("\n[Step 4] Training Classification Models...")
    results, models, predictions, probabilities, y_pred_lr, y_pred_rf, y_pred_gb, y_proba_lr, y_proba_rf, y_proba_gb = train_models(
        X_train, X_test, y_train, y_test
    )
    
    # Print results
    print("\n" + "=" * 90)
    print("MODEL PERFORMANCE RESULTS")
    print("=" * 90)
    for model_name, metrics in results.items():
        print(f"\n{model_name}:")
        for metric, value in metrics.items():
            print(f"  {metric}: {value:.4f}")
    
    # Generate additional visualizations
    print("\n[Step 5] Generating Additional Visualizations...")
    print("Creating model comparison...")
    visualize_model_comparison(results)
    
    print("Creating confusion matrices...")
    visualize_confusion_matrices(y_test, y_pred_lr, y_pred_rf, y_pred_gb)
    
    print("Creating ROC curves...")
    visualize_roc_curves(y_test, y_proba_lr, y_proba_rf, y_proba_gb)
    
    print("Creating feature importance...")
    visualize_feature_importance(feature_cols, models['Random Forest'])
    
    print("\n" + "=" * 90)
    print("EXECUTION COMPLETED SUCCESSFULLY")
    print("=" * 90)
    print("\nGenerated Visualizations:")
    print("  1. approval_distribution.png")
    print("  2. financial_metrics.png")
    print("  3. model_comparison.png")
    print("  4. confusion_matrices.png")
    print("  5. roc_curves.png")
    print("  6. feature_importance.png")
    
    return df, X_train, X_test, y_train, y_test, results, models, feature_cols

if __name__ == "__main__":
    df, X_train, X_test, y_train, y_test, results, models, feature_cols = main()
