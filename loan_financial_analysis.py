"""
Financial Analysis Utilities for Loan Approval System
Provides utilities for financial analysis, risk assessment, and insights generation
"""

import numpy as np
import pandas as pd
from collections import Counter

class LoanAnalyzer:
    """Analyzes loan applications for financial patterns and risk assessment"""
    
    def __init__(self, df):
        """Initialize with loan application data"""
        self.df = df
        
    def calculate_financial_metrics(self):
        """Calculate comprehensive financial metrics"""
        metrics = {
            'Total_Applications': len(self.df),
            'Approved_Applications': (self.df['Loan_Approved'] == 1).sum(),
            'Rejected_Applications': (self.df['Loan_Approved'] == 0).sum(),
            'Approval_Rate': (self.df['Loan_Approved'] == 1).sum() / len(self.df) * 100,
            'Rejection_Rate': (self.df['Loan_Approved'] == 0).sum() / len(self.df) * 100,
            'Avg_Income': self.df['Income'].mean(),
            'Avg_Loan_Amount': self.df['Loan_Amount'].mean(),
            'Avg_Credit_Score': self.df['Credit_Score'].mean(),
            'Avg_Approval_Score': self.df['Approval_Score'].mean(),
            'Avg_DTI_Ratio': self.df['Debt_to_Income_Ratio'].mean(),
            'Avg_Employment_Years': self.df['Employment_Years'].mean()
        }
        
        return metrics
    
    def analyze_by_income_bracket(self):
        """Analyze approval rates by income bracket"""
        income_bins = [0, 500000, 1000000, 2000000, 5000000]
        income_labels = ['<500K', '500K-1M', '1M-2M', '>2M']
        
        self.df['Income_Bracket'] = pd.cut(self.df['Income'], bins=income_bins, labels=income_labels)
        
        analysis = []
        for bracket in income_labels:
            bracket_data = self.df[self.df['Income_Bracket'] == bracket]
            if len(bracket_data) > 0:
                approval_rate = (bracket_data['Loan_Approved'] == 1).sum() / len(bracket_data) * 100
                avg_credit = bracket_data['Credit_Score'].mean()
                avg_dti = bracket_data['Debt_to_Income_Ratio'].mean()
                
                analysis.append({
                    'Income_Bracket': bracket,
                    'Count': len(bracket_data),
                    'Approval_Rate': approval_rate,
                    'Avg_Credit_Score': avg_credit,
                    'Avg_DTI': avg_dti
                })
        
        return pd.DataFrame(analysis)
    
    def analyze_by_credit_score(self):
        """Analyze approval rates by credit score category"""
        credit_bins = [0, 600, 650, 700, 750, 850]
        credit_labels = ['Poor', 'Fair', 'Good', 'Very Good', 'Excellent']
        
        self.df['Credit_Category'] = pd.cut(self.df['Credit_Score'], bins=credit_bins, labels=credit_labels)
        
        analysis = []
        for category in credit_labels:
            category_data = self.df[self.df['Credit_Category'] == category]
            if len(category_data) > 0:
                approval_rate = (category_data['Loan_Approved'] == 1).sum() / len(category_data) * 100
                avg_income = category_data['Income'].mean()
                avg_dti = category_data['Debt_to_Income_Ratio'].mean()
                
                analysis.append({
                    'Credit_Category': category,
                    'Count': len(category_data),
                    'Approval_Rate': approval_rate,
                    'Avg_Income': avg_income,
                    'Avg_DTI': avg_dti
                })
        
        return pd.DataFrame(analysis)
    
    def analyze_by_employment_status(self):
        """Analyze approval rates by employment type"""
        analysis = []
        
        for emp_type in self.df['Employment_Type'].unique():
            emp_data = self.df[self.df['Employment_Type'] == emp_type]
            approval_rate = (emp_data['Loan_Approved'] == 1).sum() / len(emp_data) * 100
            avg_income = emp_data['Income'].mean()
            avg_years = emp_data['Employment_Years'].mean()
            avg_credit = emp_data['Credit_Score'].mean()
            
            analysis.append({
                'Employment_Type': emp_type,
                'Count': len(emp_data),
                'Approval_Rate': approval_rate,
                'Avg_Income': avg_income,
                'Avg_Employment_Years': avg_years,
                'Avg_Credit_Score': avg_credit
            })
        
        return pd.DataFrame(analysis)
    
    def identify_risk_segments(self):
        """Identify high-risk and low-risk applicant segments"""
        # Calculate risk score
        self.df['Risk_Score'] = 100 - self.df['Approval_Score']
        
        # Categorize risk
        self.df['Risk_Category'] = pd.cut(self.df['Risk_Score'], 
                                          bins=[0, 15, 25, 35, 45, 100],
                                          labels=['Very Low', 'Low', 'Medium', 'High', 'Very High'])
        
        risk_analysis = []
        for category in ['Very Low', 'Low', 'Medium', 'High', 'Very High']:
            risk_data = self.df[self.df['Risk_Category'] == category]
            if len(risk_data) > 0:
                approval_rate = (risk_data['Loan_Approved'] == 1).sum() / len(risk_data) * 100
                
                risk_analysis.append({
                    'Risk_Category': category,
                    'Count': len(risk_data),
                    'Approval_Rate': approval_rate,
                    'Avg_Credit_Score': risk_data['Credit_Score'].mean(),
                    'Avg_DTI': risk_data['Debt_to_Income_Ratio'].mean()
                })
        
        return pd.DataFrame(risk_analysis)
    
    def calculate_approval_drivers(self):
        """Identify key factors driving loan approvals"""
        approved = self.df[self.df['Loan_Approved'] == 1]
        rejected = self.df[self.df['Loan_Approved'] == 0]
        
        drivers = {
            'Avg_Credit_Score_Approved': approved['Credit_Score'].mean(),
            'Avg_Credit_Score_Rejected': rejected['Credit_Score'].mean(),
            'Avg_Income_Approved': approved['Income'].mean(),
            'Avg_Income_Rejected': rejected['Income'].mean(),
            'Avg_DTI_Approved': approved['Debt_to_Income_Ratio'].mean(),
            'Avg_DTI_Rejected': rejected['Debt_to_Income_Ratio'].mean(),
            'Avg_Employment_Approved': approved['Employment_Years'].mean(),
            'Avg_Employment_Rejected': rejected['Employment_Years'].mean()
        }
        
        return drivers
    
    def identify_high_risk_applicants(self, threshold=35):
        """Identify applicants with high risk scores"""
        high_risk = self.df[self.df['Risk_Score'] > threshold]
        
        return {
            'High_Risk_Count': len(high_risk),
            'High_Risk_Percentage': len(high_risk) / len(self.df) * 100,
            'High_Risk_Approval_Rate': (high_risk['Loan_Approved'] == 1).sum() / len(high_risk) * 100 if len(high_risk) > 0 else 0,
            'Avg_Credit_Score': high_risk['Credit_Score'].mean() if len(high_risk) > 0 else 0,
            'Avg_DTI': high_risk['Debt_to_Income_Ratio'].mean() if len(high_risk) > 0 else 0
        }


class LoanInsights:
    """Generates actionable insights from loan analysis"""
    
    def __init__(self, df):
        """Initialize with loan data"""
        self.df = df
        self.analyzer = LoanAnalyzer(df)
    
    def get_key_findings(self):
        """Extract key findings from the data"""
        metrics = self.analyzer.calculate_financial_metrics()
        
        findings = []
        
        # Finding 1: Overall approval rate
        approval_rate = metrics['Approval_Rate']
        if approval_rate >= 70:
            findings.append(f"High approval rate of {approval_rate:.1f}% indicates lenient lending policy")
        elif approval_rate >= 50:
            findings.append(f"Moderate approval rate of {approval_rate:.1f}% suggests balanced risk management")
        else:
            findings.append(f"Low approval rate of {approval_rate:.1f}% indicates strict lending standards")
        
        # Finding 2: Credit score impact
        credit_analysis = self.analyzer.analyze_by_credit_score()
        if len(credit_analysis) > 0:
            excellent_rate = credit_analysis[credit_analysis['Credit_Category'] == 'Excellent']['Approval_Rate'].values
            poor_rate = credit_analysis[credit_analysis['Credit_Category'] == 'Poor']['Approval_Rate'].values
            
            if len(excellent_rate) > 0 and len(poor_rate) > 0:
                diff = excellent_rate[0] - poor_rate[0]
                findings.append(f"Credit score significantly impacts approval: {diff:.1f}% difference between excellent and poor credit")
        
        # Finding 3: Income level impact
        income_analysis = self.analyzer.analyze_by_income_bracket()
        if len(income_analysis) > 0:
            high_income = income_analysis[income_analysis['Income_Bracket'] == '>2M']['Approval_Rate'].values
            low_income = income_analysis[income_analysis['Income_Bracket'] == '<500K']['Approval_Rate'].values
            
            if len(high_income) > 0 and len(low_income) > 0:
                diff = high_income[0] - low_income[0]
                findings.append(f"Income level influences approval: {diff:.1f}% difference between high and low income groups")
        
        return findings
    
    def get_risk_recommendations(self):
        """Generate risk management recommendations"""
        high_risk = self.analyzer.identify_high_risk_applicants()
        
        recommendations = []
        
        if high_risk['High_Risk_Percentage'] > 30:
            recommendations.append("High proportion of high-risk applicants detected. Consider stricter approval criteria.")
        
        if high_risk['High_Risk_Approval_Rate'] > 50:
            recommendations.append("High-risk applicants have significant approval rate. Implement additional verification steps.")
        
        return recommendations
    
    def get_business_insights(self):
        """Generate business-level insights"""
        metrics = self.analyzer.calculate_financial_metrics()
        
        insights = []
        
        avg_loan = metrics['Avg_Loan_Amount']
        total_apps = metrics['Total_Applications']
        approved = metrics['Approved_Applications']
        
        total_approved_amount = (self.df[self.df['Loan_Approved'] == 1]['Loan_Amount'].sum())
        
        insights.append(f"Total loan portfolio: ₹{total_approved_amount:,.0f} across {approved} approved applications")
        insights.append(f"Average loan size: ₹{avg_loan:,.0f}")
        insights.append(f"Processing {total_apps} applications with {metrics['Approval_Rate']:.1f}% approval rate")
        
        return insights


def generate_and_save_loan_datasets(output_dir='/home/ubuntu'):
    """Generate and save all sample loan datasets"""
    print("Generating loan application datasets...")
    
    # Generate loan dataset
    from loan_approval_prediction import generate_loan_applications
    
    df = generate_loan_applications(n_applications=1000)
    
    # Save raw dataset
    print("  Saving raw loan application dataset...")
    df.to_csv(f'{output_dir}/loan_applications.csv', index=False)
    print(f"  ✓ Raw dataset saved")
    
    # Perform financial analysis
    print("  Performing financial analysis...")
    analyzer = LoanAnalyzer(df)
    
    # Calculate financial metrics
    print("  Calculating financial metrics...")
    metrics = analyzer.calculate_financial_metrics()
    
    metrics_df = pd.DataFrame({
        'Metric': list(metrics.keys()),
        'Value': list(metrics.values())
    })
    
    metrics_df.to_csv(f'{output_dir}/loan_financial_metrics.csv', index=False)
    print(f"  ✓ Financial metrics saved")
    
    # Analyze by income bracket
    print("  Analyzing by income bracket...")
    income_analysis = analyzer.analyze_by_income_bracket()
    income_analysis.to_csv(f'{output_dir}/loan_income_analysis.csv', index=False)
    print(f"  ✓ Income analysis saved")
    
    # Analyze by credit score
    print("  Analyzing by credit score...")
    credit_analysis = analyzer.analyze_by_credit_score()
    credit_analysis.to_csv(f'{output_dir}/loan_credit_analysis.csv', index=False)
    print(f"  ✓ Credit analysis saved")
    
    # Analyze by employment status
    print("  Analyzing by employment status...")
    employment_analysis = analyzer.analyze_by_employment_status()
    employment_analysis.to_csv(f'{output_dir}/loan_employment_analysis.csv', index=False)
    print(f"  ✓ Employment analysis saved")
    
    # Risk segmentation
    print("  Performing risk segmentation...")
    risk_analysis = analyzer.identify_risk_segments()
    risk_analysis.to_csv(f'{output_dir}/loan_risk_analysis.csv', index=False)
    print(f"  ✓ Risk analysis saved")
    
    # Generate insights
    print("  Generating insights...")
    insights = LoanInsights(df)
    
    findings = insights.get_key_findings()
    recommendations = insights.get_risk_recommendations()
    business = insights.get_business_insights()
    
    insights_df = pd.DataFrame({
        'Type': ['Finding'] * len(findings) + ['Recommendation'] * len(recommendations) + ['Business'] * len(business),
        'Insight': findings + recommendations + business
    })
    
    insights_df.to_csv(f'{output_dir}/loan_insights.csv', index=False)
    print(f"  ✓ Insights saved")
    
    return df, analyzer, metrics


if __name__ == '__main__':
    df, analyzer, metrics = generate_and_save_loan_datasets()
    
    print("\nDataset Summary:")
    print(f"Total Applications: {len(df)}")
    print(f"Approved: {(df['Loan_Approved'] == 1).sum()}")
    print(f"Rejected: {(df['Loan_Approved'] == 0).sum()}")
    
    print("\nFinancial Metrics:")
    for metric, value in list(metrics.items())[:5]:
        print(f"  {metric}: {value:.2f}")
    
    print("\nRisk Analysis:")
    risk_high = analyzer.identify_high_risk_applicants()
    print(f"  High-Risk Applicants: {risk_high['High_Risk_Count']}")
    print(f"  High-Risk Percentage: {risk_high['High_Risk_Percentage']:.2f}%")
